# ToLogic：义项逻辑公式枚举

本支线把六例和额外 `want` 案例按用途整理在 `model/`：

| 路径 | 内容 |
| --- | --- |
| `model/engine/` | 公式枚举引擎、规则、配置和规格 |
| `model/cases/` | 六个确认案例，以及 `want_lack` 输入与原始结果 |
| `model/audit/`、`model/tools/` | 独立候选核验及适配器 |
| `model/bundle.py`、`model/enumerate_one.py` | 六例校验/重放入口和单案例枚举入口 |
| `rank_baseline.py` | 六例无训练排序基线 |

原始 ZIP 不进入仓库。模型目录中的历史本机绝对路径已脱敏；受影响的输入摘要和整理后清单已重新计算。因此整理版可以验证自己的 148 个文件，但与原 ZIP 不逐字节相同。原始 ZIP 的 SHA-256 分别为 `cf540eca36aec9ddb598a5c4fe946e8091e5f83d521b228c1b545406e1ca7078`（六例）和 `f07f73cc9cdc8c9bea9a63511bf41e117865e780c83c1268709d8800427e6cd4`（want）。

## 本地运行

需要 Python 3.11 或更高版本，仅使用标准库；无需 GPU、网络、API 密钥或额外模型权重。在仓库根目录的 PowerShell 中：

```powershell
cd hypergraph_analysis_exploration/research/tologic/model
python -B -X utf8 bundle.py verify
python -B -X utf8 bundle.py replay --out ../../../outputs/tologic_replay_new
python -B -X utf8 enumerate_one.py --input cases/want_lack/input.json --out ../../../outputs/tologic_want_new
```

输出目录必须是新目录。六例校验和重放均预期 `PASS`，候选数依次为 130、2、3、20、122、178，共 455；`want` 的 `be without` 输入产生 130 条候选。当前电脑上这些命令已实际跑通。

`without` 在 `want` 中是用户提供的 LHS 接口，不属于 85 个基准词；该案例没有独立 gold，RHS 与语义接受性仍待审核。枚举完成和候选一致不代表自然语言语义已验证。两个额外分支 `lack` 和 `be deficient in` 尚未在此案例中枚举。

## 排序基线

从仓库根目录运行 `python hypergraph_analysis_exploration/research/tologic/rank_baseline.py --out report/tologic_rank_new.json`。基线只按已使用词项 occurrence 的数量评分，参考答案在评分之后读取；并列采用均匀随机打破的期望指标。六例结果仅是同例描述，不证明泛化。

项目实际状态、输入限制和后续计划见[总报告](../../../report/project_review_2026-10-29-current.md)与[研究计划](../../docs/research_tracks_2026-10-28.md)。