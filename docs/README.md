# Perception–Memory Balance in Streaming Video Understanding

基于 [SimpleStream](https://github.com/EvolvingLMMs-Lab/SimpleStream) 开展轻量、可复现的 streaming video understanding 研究。

## Motivation

SimpleStream 表明：少量 recent frames 已是很强的 baseline；延长历史窗口可能改善记忆，却损伤实时感知。我们关心的是：**在不增加复杂 memory/retrieval 架构的前提下，模型能否学会选择合适的历史上下文，并在感知–记忆权衡上超过最佳固定窗口？**

## Research Question

**Can a lightweight learned context policy improve the perception–memory trade-off beyond a fixed recent-window baseline?**

首轮固定 **Qwen3-VL-8B-Instruct + OVO-Bench**，以 SimpleStream 的 recent-only inference 为基础。

## Evaluation

- **Perception (P)**：OVO-Bench Real-Time Visual Perception 六项 accuracy 的宏平均。
- **Memory (M)**：EPM 与 ASI accuracy 的平均；HLD 不计入 M。
- **论文主指标**：`Avg_paper = (P + (EPM + ASI + HLD)/3)/2`，用于复现和比较；与包含前向任务的脚本 Total Avg 区分。
- **权衡分析**：单独报告 P、M、HLD，绘制 P–M 曲线；`PM = sqrt(P * M)` 仅为本研究的辅助指标。同时报告总体 accuracy（注明任务范围）、实际平均帧数及端到端延迟。
- **Comparisons**：Fixed-4、Best Fixed-N（仅用开发集论文 Avg 选 N，平分优先短窗口）、Learned Policy；Oracle 仅作离线上界。总分提高不自动代表记忆改善。

下一步先确认 GPU、依赖与模型/数据可用，跑通官方 recent-4；随后扫描 N=2、8、16 并检查 oracle headroom，足够时再训练轻量选择器。

## Research Rules

1. **保留原始 SimpleStream 不可变 baseline**：记录 upstream commit / 配置 / 环境；新增实验代码独立开发。
2. **严格避免测试泄漏**：GT、正确性、OVO 任务类别及 PM-Score 可用于训练数据监督或离线评测，**不能作为测试时策略输入或在线反馈**。
3. **先验证，再加复杂度**：固定 backbone；先不引入 retrieval、memory graph 或 RL。策略提升必须与最优固定窗口比较，而不只是 Fixed-4。
4. **诚实处理数据划分**：任何使用 OVO 测试标注开发策略的结果仅算内部探索，不声称标准 benchmark 的未见测试成绩。

## Tasks

- [261010_01_validate_idea.md](261010_01_validate_idea.md)：复现 baseline、测量 oracle headroom，并验证最小 learned policy。

参考：[SimpleStream paper](https://arxiv.org/abs/2604.02317) · [Official code](https://github.com/EvolvingLMMs-Lab/SimpleStream)
