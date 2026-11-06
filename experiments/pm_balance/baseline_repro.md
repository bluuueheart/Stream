# SimpleStream baseline 复现记录

检查日期：2026-11-06 UTC。状态：**尚未运行推理，复现未完成**。

## 冻结版本

- Upstream: https://github.com/EvolvingLMMs-Lab/SimpleStream
- Commit: `be227ee8ce90a258b286a34161688c2a59eeeadb`
- 检查时 `git status --porcelain` 为空；本次未修改 SimpleStream。
- 完整 tracked-source 归档：`baseline/SimpleStream-be227ee.tar`。
- SHA256: `5616037d6555e106f57500d29db9977c2596296f0eb73c8311aa77707ec00f13`。
- 官方依赖：`requirements-qwen3.txt` 指定 transformers 4.57.6、accelerate 1.12.0；公共依赖包含 qwen-vl-utils 0.0.14、av >=14.4.0。PyTorch/torchvision 和 flash-attn 需要单独安装并记录实际版本。
- 当前默认 Python 的实测包版本见 `environment.json`；该环境不满足推理条件。

## 当前阻塞

`nvidia-smi` 无法连接驱动；现有 H-WM 环境的 `torch.cuda.is_available()` 也是 False。默认 Python 缺 transformers、accelerate、av、qwen_vl_utils。检查的项目目录、用户 HF 缓存、local_share 与公共模型目录中未找到指定 8B 模型及 OVO 数据；这不代表全盘不存在。通过 Python 下载官方标注失败，错误为 DNS resolution unavailable。未安装包、未下载大模型或视频、未启动推理。

## 官方 recent-4 命令

在满足依赖和 CUDA 的环境中，从 Stream 根目录执行；只允许使用本机约定的 GPU 2,3,4,5，先检查占用，不结束他人的进程。单 GPU 示例：

```bash
CUDA_VISIBLE_DEVICES=2 python SimpleStream/main_experiments/eval_qwen3vl_ovo.py \
  --model_path Qwen/Qwen3-VL-8B-Instruct \
  --anno_path /absolute/path/ovo_bench_new.json \
  --chunked_dir /absolute/path/chunked_videos \
  --result_dir experiments/pm_balance/results/official_recent4 \
  --recent_frames_only 4 --chunk_duration 1.0 --fps 1.0 --max_qa_tokens 256

python SimpleStream/scoring/score_ovo_bench.py \
  --result_path experiments/pm_balance/results/official_recent4/qwen3vl_results_TIMESTAMP.json
```

首次运行使用新输出目录；官方断点续跑不校验模型和参数，不能跨设置复用目录。四窗口实验分别使用 N=2,4,8,16 和独立目录，不能覆盖官方 recent-4。

## Prompt 与推理行为

选择题 prompt 来自 `ovo_constants.py` 的 `BR_PROMPT_TEMPLATE`，问题之后附 `Options: ...`，末尾为 `Only give the best option's letter directly.`。选项由 `lib/recent_window_eval.py::build_ovo_prompt` 构造。保留原始模板；生成配置为 `do_sample=False`、max_new_tokens=256；Qwen3 默认 bf16、flash_attention_2。MIN_PIXELS、MAX_PIXELS、QWEN_EXACT_RECENT_DECODE 均需记录；本次未启用这些变量。

官方 evaluator 读取 `{id}.mp4`（前向任务使用 `{id}_{index}.mp4`），没有直接用标注的 realtime 截断源视频，因此因果性依赖输入已经是合法的 query-prefix clips。拿到数据后必须核对官方切片方式与时间终点，不能把完整视频当作这些切片。

## 评分口径核对

[论文表 1 与实验设置](https://arxiv.org/html/2604.02317v1)仅报告实时感知与回溯两类，Avg 为两类宏平均的均值；Qwen3 recent-4 报告 67.70。这是外部参考值，不是本次复现成绩。

[OVO 官方 scorer](https://github.com/JoeLeelyf/OVO-Bench/blob/main/utils/OVOBenchScore.py)以及本地 inlined scorer 的 Total Avg 使用回溯、实时、前向三类。应额外按论文口径重算，不能直接用脚本 Total Avg 对比论文。原始选择题计分为大小写敏感的 `gt in response`；本地 evaluator 的即时 summary 使用答案抽取，二者可能不同，正式复现以原始 scorer 为准，并记录歧义响应。

本任务 PM 为 `sqrt(P*M)`，M 只含 EPM 与 ASI；论文 Avg 的回溯项还含 HLD，二者不等价。原始 scorer 的前向类别缺失时还存在局部变量未定义问题；不可直接删去前向结果再运行原始 scorer。

## 待验证事项

依赖实际版本、模型权重 revision、标注与视频哈希、切片时间终点、采样得到的实际帧数、逐题推理结果、原始 scorer 与 evaluator 差异均待 GPU/数据就绪后验证。官方 generate_time 不含解码与视觉编码，不能作为端到端 latency；另记 CUDA 同步后的完整 query 调用时间。当前没有可报告的复现误差或实验成绩。
