# Stream 研究管理仓库

本仓库管理 perception–memory balance 项目的方案文档和实验记录。研究代码
`SimpleStream/` 保持为独立 Git 仓库，不纳入本仓库的文件历史。

## 目录

- [`docs/`](docs/)：项目概述、研究问题和验证方案。
- [`experiments/pm_balance/`](experiments/pm_balance/)：baseline 归档、环境记录、窗口扫描数据和验证记录。
- `SimpleStream/`：独立的上游代码 checkout；根仓库通过 `.gitignore` 排除它。

## 仓库地址

- 管理仓库：<https://github.com/bluuueheart/Stream>
- `SimpleStream/` 上游：<https://github.com/EvolvingLMMs-Lab/SimpleStream>

当前 `SimpleStream/` 位于 commit `be227ee8ce90a258b286a34161688c2a59eeeadb`。
在新工作区中，可将上游仓库 clone 到 `SimpleStream/`。

## 当前状态

尚未运行推理。Baseline 复现和 PM-balance 评估目前受 CUDA、依赖及本地模型/数据
可用性阻塞，详见 [`baseline_repro.md`](experiments/pm_balance/baseline_repro.md)
和 [`pm_validation.md`](experiments/pm_balance/pm_validation.md)。
