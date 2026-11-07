# Task 261010_01 — Validate PM-Balance Idea

**目标**：在不改 backbone、不引入复杂 memory 的前提下，验证学习型窗口选择能否在独立测试数据上超过 SimpleStream 的**最佳固定窗口**。

**当前下一步**：GPU、指定模型、依赖和官方 recent-4 单题验证已通过；准备完整 OVO query-prefix 视频集，审计覆盖和因果性后运行完整 recent-4，再扫描其他窗口，暂不训练选择器。见 `experiments/pm_balance/runtime_setup.md`。

## 1. 冻结 baseline

- 检查当前仓库结构，定位已下载的 SimpleStream；记录 upstream Git commit、依赖、评测命令、采样率和 prompt。
- 保留**原样、可复现**的官方代码版本（独立目录/分支/worktree 均可）；新实验不得覆盖 baseline 输出。
- 使用 `Qwen/Qwen3-VL-8B-Instruct` + `OVO-Bench` 跑通官方 **recent-4**；核对原始评分脚本与论文协议，记录复现偏差。

## 2. 固定窗口扫描与逐题记录

- 在完全相同设置下运行 `N ∈ {2, 4, 8, 16}`（1 fps，视频仅截至 query timestamp）。
- 存储逐题：`video_id, question_id, timestamp, N, prediction, GT(仅离线), correct(仅离线), latency`；如可获得，另记模型 confidence/logprob。
- 复现主指标采用论文口径：`P = macro_avg(OCR, ACR, ATR, STU, FPD, OJR)`，`B = (EPM + ASI + HLD)/3`，`Avg_paper = (P + B)/2`；不直接使用包含前向任务的脚本 `Total Avg.` 对比论文。
- 权衡分析单独报告 `M = (EPM + ASI)/2` 和 HLD；`PM = sqrt(P*M)` 仅为本研究的辅助指标。同时报告整体 Acc（注明任务范围）、实际输入帧数和端到端延迟。
- 按 **video_id** 分离 train/dev/test，禁止同一视频跨 split。若只用 OVO 官方测试标注做探索，结果标为 *internal study*，不当作独立 benchmark 测试结论。

## 3. 先判断是否有可学习空间

- 仅按 dev 的论文 Avg 选择 `Best Fixed-N`（平分优先短窗口），测试前固定。比较其与 `Fixed-4` 的论文 Avg、P、M、HLD 和辅助 PM。
- 在离线、仅诊断条件下，用 GT 计算 **per-question oracle window**（答对的候选中优先选最短窗口），估计固定窗口之外的 headroom；绝不能将 oracle 选择用于测试推理。
- 分析不同窗口的互补性：哪些题在小窗口正确而大窗口错误，反之亦然。
- 绘制 P–M 曲线：P、M 同时提高是直接改善；一升一降则明确报告取舍，不能仅凭论文 Avg 上升声称记忆改善。

## 4. 最小学习验证（仅 headroom 足够时）

- 冻结 VLM。先用轻量分类器/规则校准器预测 `N ∈ {2,4,8,16}`；输入限于**当前 query 和模型实际可观察的 recent-4 信号**（如置信度），不输入 benchmark 类别或 GT。
- 仅使用 train/dev 调整策略；在 held-out test 固定所有超参数，不进行根据答错次数的在线更新。
- 公平比较 `Fixed-4 / Best Fixed-N(dev) / Learned / Oracle(离线诊断)`；报告论文 Avg、P、M、HLD、辅助 PM、平均输入帧数及额外推理成本。若先跑 recent-4 再切换窗口，两次推理均计入成本。

## Go / No-Go

**Go**：oracle 相比 Best Fixed-N 有可观 headroom，且 Learned 在独立测试上稳定提高论文 Avg，并在控制成本下改善 P–M 组合；若 P、M 一升一降，按测试前约定的可接受损失判断，不仅凭总分下结论。

**No-Go**：oracle headroom 很小，或 Learned 仅在开发集有效；整理 failure cases，暂不引入 RL/复杂路由器。

## 交付

- `baseline_repro.md`：commit、环境、命令、复现结果与偏差。
- `window_sweep.csv`：逐题数据（GT/正确性仅用于离线分析）。
- `pm_validation.md`：四窗口曲线、oracle gap、learning 结果、成本、Go/No-Go 结论。

> 原则：**先证明“能选得更好”，再讨论“怎么学得更聪明”。**
