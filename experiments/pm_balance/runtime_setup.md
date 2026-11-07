# 2026-11-07 运行环境恢复

GPU 已恢复访问：NVIDIA H20，97871 MiB 显存，UUID
`GPU-bb163038-9f05-12e3-dc3c-ead2ac87a033`。设备节点为 `/dev/nvidia2`，但当前
进程内逻辑设备是 `cuda:0`；不要从设备节点编号推导 `CUDA_VISIBLE_DEVICES=2`。
此前设备不可见发生在受限执行环境；权限更新后可用，无需重装驱动。

## 独立环境

未修改系统 Python 和 SimpleStream baseline。运行环境为 `.venv-qwen3`：
Python 3.11.18、torch 2.5.1+cu124、torchvision 0.20.1+cu124、transformers
4.57.6、accelerate 1.12.0、qwen-vl-utils 0.0.14、FlashAttention 2.7.4.post1。
完整版本见 `requirements-runtime-20261107.txt`，环境元数据见
`environment_20261107.json`。驱动 535.247.01，使用 CUDA 12.4 wheel（已实测当前驱动下运行）。

重建时先建 Python 3.11 venv，然后安装：

```bash
uv pip install --python .venv-qwen3/bin/python torch==2.5.1 torchvision==0.20.1 \
  --index-url https://download.pytorch.org/whl/cu124
uv pip install --python .venv-qwen3/bin/python \
  -r SimpleStream/requirements-qwen3.txt packaging ninja einops psutil setuptools wheel
uv pip install --python .venv-qwen3/bin/python \
  'https://github.com/Dao-AILab/flash-attention/releases/download/v2.7.4.post1/flash_attn-2.7.4.post1+cu12torch2.5cxx11abiFALSE-cp311-cp311-linux_x86_64.whl'
```

本地模型：`/taijifs_hzlf/share_1227201/weipuzhang/Qwen3-VL-8B-Instruct`。
四个 safetensors shard 齐全；config 为 `qwen3_vl`。本地目录未发现 revision
信息，尚不能声明与某个 HF revision 字节一致；未修改共享权重。

## 单题真实数据验证

OVO 代码/标注来自 `JoeLeelyf/OVO-Bench` commit
`c34093f9a072d93f9e1c6b923446dfba71f4528e`，当前标注共有 1640 条。
首次只验证 id=35 的 EPM 题，query timestamp=82 秒。视频取自官方 HF
`chunked_videos.tar.partaa` 的首个文件 `chunked_videos/35.mp4`，通过 HTTP Range
读取 bytes=1024-57465413，共 57464390 字节。脚本校验标注和视频 SHA256，
避免下载完整的 10 GiB 分卷。

```bash
python3 experiments/pm_balance/scripts/prepare_smoke.py
MODEL_PATH=/taijifs_hzlf/share_1227201/weipuzhang/Qwen3-VL-8B-Instruct \
RESULT_DIR=experiments/pm_balance/results/recent4_smoke_NEW \
  bash experiments/pm_balance/scripts/run_recent4_smoke.sh
```

脚本要求新输出目录，默认按 GPU UUID 选择设备并禁用 HF 在线访问；其余
recent-4 参数保持官方默认。不要将单题结果混入 `window_sweep.csv` 或报告为
完整 baseline 成绩。完整视频集尚未准备，尚不能计算论文 Avg、P、M 或 oracle。

PyAV 可成功解码，视频 1920×1080、30fps；容器时长 82.025011 秒（包含音频），
已逐帧解码 2460 帧，末帧时间为 81.966667 秒，早于 82 秒 query。官方切片代码使用 ceil(realtime)，且当前版本
存在仅处理前向任务的 continue 语句；不能直接用该脚本生成所有回溯/实时切片。
完整复现须另行检查 pre-chunked clips 的覆盖、帧时间及标注对应关系。

## 兼容性修复与验证

- cu121 的 torch 2.5.1 可执行小型张量、FlashAttention 和视觉编码，但 BF16
  `Linear(4096, 151936)` 在单 token 生成时 SIGFPE；独立最小复现与模型 traceback
  一致。`DISABLE_ADDMM_CUDA_LT=1` 未解决。
- 改为 torch 2.5.1+cu124 / torchvision 0.20.1+cu124 后，同一 BF16 vocabulary
  projection 与 FlashAttention 测试通过。`scripts/check_gpu_runtime.py` 可复验。
- FFmpeg 在 384 个可见 CPU 上默认线程分配失败；启动脚本限制前 8 个可用 CPU、
  OpenMP/MKL/OpenBLAS 线程数为 4，torchvision 解码已通过。
- PyAV 18.1.0 的异常处理与旧 torchvision 的 `av.AVError` 引用不兼容；限制线程
  消除了本次触发路径。尝试 av 14.4.0 因缺 FFmpeg 开发库构建失败，未安装。
- 曾尝试 decord 0.6.0，已卸载；最终固定使用 torchvision，`uv pip check` 全部通过。
- 初次失败输出保留在独立目录 _01/_02/_03；cu124 重试使用 _04，不复用断点。

## 成功结果（仅运行验证）

2026-11-07：cu124 环境下 _04 运行退出码 0；原始结果归档为
`recent4_smoke_20261107.json`。id=35 的预测为 C，GT 为 C；实际 4 帧，
final_chunk_ids=[78,79,80,81]，2304 个视觉 tokens，torchvision 解码。
官方 generate_time=0.49064 秒，仅为生成阶段；tqdm 单题约 20.30 秒也不能替代
有 CUDA 同步、明确计时边界的端到端 latency。原始 ttft 字段未独立校准。

此单题成功证明官方代码可在当前 GPU/环境完成一次真实推理。不能据此报告
EPM benchmark accuracy=100%，也不能计算 P/M/论文 Avg。完整视频集、
模型权重 revision/哈希与完整 recent-4 复现仍待完成。SimpleStream checkout 保持未修改。
