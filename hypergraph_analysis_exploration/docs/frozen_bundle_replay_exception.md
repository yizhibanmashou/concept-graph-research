# 冻结包 canonical replay 单例差异

状态：已定位并与冻结包自带报告、索引、图规则及 witness 交叉核对；差异有明确的上游保留策略，**未修改图数据，也未据此裁决释义语义**。

## 核查结果

冻结包 manifest 与 `reports/source_replay.json` 均报告 110,424/110,425 个 head 可被 canonical replay 精确重建。唯一例外为 `ext_wikt_full_dd659c7fcb3b`（POS `r`）：

- 冻结图为一个 clause：`{oewn-15188844-n, on-2}`；该 head 的选定 witness 正是此 clause，结构深度为 376。
- 来源 canonical replay 与其不同：上游报告 `missing_from_canonical_replay` 为上面的二 literal clause，`extra_in_canonical_replay` 为单 literal clause `{oewn-15188844-n}`。
- 冻结包 `README.md` 说明：对此 head 保留归档的权威图 clause 选择，不把来源 JSON 中额外分支并入本版超图，也不删改来源 JSON。
- 上游 replay 报告把该图 clause 标为有直接 source-DNF evidence。此字段只是上游审计声明；本项目的交叉核查没有重跑上游 normalization/replay，也没有检验 gloss 在语义上是否蕴含该 clause。

因此这不是当前 witness 指向了不存在 clause 的错误：所选 clause 确实存在于冻结图，且本项目的独立 witness verifier 可重放它。它是“来源 canonical replay 与封存图选择不一致”的单例，应保留为版本/策略例外；不能静默把 singleton clause 加入图、替换现有 clause，或将计数差异解释为语义错误。若未来修订，需先得到上游规则版本映射和明确的构图策略，再重算闭包、全部 witness、semantic fingerprint 与论文报告。

## 可复算核对

```powershell
python -m src.analysis.audit_frozen_bundle_replay_exceptions
python -m unittest tests.test_frozen_bundle_replay_exception_audit -v
```

机器结果写入 `outputs/phase8/frozen_bundle_replay_exceptions.json`，复跑覆盖时须显式加 `--force`。当前输入锚点：

| 输入 | SHA-256 |
|---|---|
| bundle semantic fingerprint | `6a26db5de732d90e7eb1ae700eec5c6f34e9c28fa83f35d2eb616c6abb8d4e41` |
| `manifest.json` | `126c8c5390efaff9ca1aaa1e12f7931ca90b802104ffaf57385d4b692c23605f` |
| `reports/source_replay.json` | `781bbd855984bc2b19ecfd1619af477d3fb5c140cdd833021aaad2f579ca85fe` |
| `indexes/senses.jsonl` | `f60679d8cf86e5378411bf0ec7a4759e882fde97e6002945b17e5483558abd30` |
| `graph/hypergraph_rules.jsonl` | `c07dd37342ab399244a091501a21ada9e2f9f706efb1dc34d6b8ebc16a8a0a53` |

该审计只读 manifest、replay report、sense index、rules 和 witness；不打开约 18.9 GB 的 source JSON payload。它验证 bundle 自带例外报告与当前 index/rules/witness 的一致性，不复现上游来源重放，更不验证 source payload 的授权或语义。


## Phase224 现态复核（2026-10-08）

同一例外审计器在当前 frozen bundle 上再次输出 1 个 replay exception，与 phase8 输入指纹/哈希及例外明细完全一致。该结果只确认冻结包内部的 report/index/rule/witness 交叉引用仍可复算；未执行上游 canonical replay 或独立 witness proof replay。现态输出见[Phase224 JSON](../outputs/phase224/frozen_bundle_replay_exceptions_current.json)和深度报告。
