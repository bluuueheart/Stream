# PM-Balance validation

状态：**完整评估待执行 / 尚不能判断 Go 或 No-Go**。已通过真实单题推理验证，但尚无四窗口实验数据。

2026-11-07 更新：GPU、模型权重和独立环境已准备，已通过单题 recent-4 运行验证（见 `recent4_smoke_20261107.json`），
详见 `runtime_setup.md`。四窗口实验仍无可用结果，以下分析计划保持待执行。
已在获得任何成功预测前冻结 `video_splits_v1.json`：按标注中的 source video 路径
确定划分，train/dev/test 为 405/122/117 个视频、1049/316/275 条标注。
划分算法不读取 GT、task 或预测；完整标注中的 644 个视频无重复 basename，
但不同文件是否内容重复仍待审计。此为官方标注上的 internal study。
dev ACR 仅 3 题，后续宏平均方差可能较大；不根据后续成绩重新划分。

本次已归档未修改的 baseline，记录依赖与命令，核对论文和评分代码的口径。`window_sweep.csv` 仅有表头，**不是完成的实验数据**。

| N | P | M | PM | Acc | 平均实际帧数 | 端到端延迟 |
|---|---|---|---|---|---|---|
| 2 | 待测 | 待测 | 待测 | 待测 | 待测 | 待测 |
| 4 | 待测 | 待测 | 待测 | 待测 | 待测 | 待测 |
| 8 | 待测 | 待测 | 待测 | 待测 | 待测 | 待测 |
| 16 | 待测 | 待测 | 待测 | 待测 | 待测 | 待测 |

P 固定为 OCR/ACR/ATR/STU/FPD/OJR 六项 accuracy 的宏平均；M=(EPM+ASI)/2；PM=sqrt(P*M)。指标统一使用 [0,1] 后再转百分数。缺任一必要子任务时不计算完整 PM，不将缺项记为零。整体 Acc 明确报告覆盖的任务范围，另外保留论文 Avg。

后续按下列顺序执行：

1. 恢复 CUDA、指定 Python 环境及指定模型/OVO 数据路径；核验 query-prefix clips 后运行官方 recent-4。
2. 在相同模型、prompt、分辨率、解码后端、采样率下运行四窗口。保存真实 source video 标识（不能用 question clip id 代替）、question_id、标注 realtime、预测、离线 GT/正确性、实际帧数与端到端延迟。confidence 不可得则留空。
3. 在查看预测效果前，以原始 video_id 固定 train/dev/test 划分并保存清单。检查跨任务是否同源，禁止同视频跨 split。若使用官方测试标注开发，只能称 internal study。
4. 只按 dev 的论文 Avg 选 Best Fixed-N，平分时选择更短窗口。论文 Avg 为 `(P+(EPM+ASI+HLD)/3)/2`；PM 仅作辅助指标。分别报告 train/dev/test 四窗口曲线；不按 test 重选 N。
5. 在每个 split 上离线取最短答对窗口；全错时选择 N=2 并保留错误分数。报告 oracle gap 和两两窗口互补题数。Oracle 不能用于真实推理。
6. 在分析 headroom 前写明实用提升阈值与成本预算；仅当 train/dev headroom 足够时训练轻量策略。仅以 query 和可观察的 recent-4 信号为输入，不输入任务类别或 GT。测试前冻结模型、特征与所有超参数。
7. 同时比较 Fixed-4 / Best Fixed-N(dev) / Learned / Oracle。若先推 recent-4 再重跑其他 N，必须把两次推理帧数、延迟和路由耗时计入 learned 成本；oracle 只报告诊断性选中窗口成本。
8. 用视频为单位的配对 bootstrap 检查测试论文 Avg、P、M 增益的稳定性，保存 failure cases；独立数据条件与成本要求均满足，且 P–M 组合改善（取舍满足测试前约定）后才作 Go 判断。

当前 oracle gap、互补性、learned 效果和成本均未知，尚未训练策略。具体环境阻塞和复现偏差见 `baseline_repro.md` 及 `environment.json`。
