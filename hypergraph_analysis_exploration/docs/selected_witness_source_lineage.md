# Phase 19：Selected-witness 来源链与 payload 完整性审计

本页中的 Phase 19 数值是 `selected-witness-source-lineage/1` 的历史结果。Phase 117 对复算契约作了加固：运行前验证项目冻结包 integrity lock；显式核验 `selected_basis_atoms.txt` 对 checksums sidecar；新报告记录 manifest、basis、bundle lock、各分析实现文件 SHA-256 与 Python/platform 信息。Phase 19 原报告保留作历史记录，不视作 v2 的复算产物。v2 最新运行记录见Phase 117 报告与 `outputs/phase117/selected_witness_source_lineage.json`。

状态：已对冻结图全部 selected-witness clauses 直接复核来源索引、来源文件 checksums 与 source/synset identity。报告为聚合值，不输出路径、sense ID、lemma 或释义文本。此处“来源链可追溯”不等于来源文字支持规则语义。

## 审计链与复算对象

审计器对每个 witness head 复核：

1. witness DAG 对 frozen OR-of-AND graph 的结构验证通过；
2. 每个非 basis head 的 witness body 能匹配图中所选 clause index；
3. 同一 head 的 `active_clause_sources` 将该 clause index 关联到 source document，且 document 出现在该 head 的 `source_records` 元数据中；
4. source document 能在冻结 `checksums.jsonl` 中定位，实际字节数和 SHA-256 匹配；
5. source JSON 内的 synset identity 与该 witness head 一致。

该检查使用冻结包 manifest、rules、coverage witnesses、sense index 与 checksums 文件，报告分别记录其哈希。源 payload 按最大 16 MiB 文件界限逐个读取，重复文件只校验一次。项目既有 Phase 15 全量 census 也对所有 active source payload 做了相同哈希校验；Phase 19 则沿每个已选 witness clause 的直接索引链接重新构造这条链。

## 全图结果

输入 graph rules SHA-256：`c07dd37342ab399244a091501a21ada9e2f9f706efb1dc34d6b8ebc16a8a0a53`。

- 110,425 个 graph head 中，85 个为 basis seed，110,340 个有 selected rule clause；全部 110,340 个所选子句至少有一个 source-document link。
- 这些所选子句共有 110,382 个 source-document 引用，涉及 110,382 个不同来源文件；没有一个来源文件被多个 selected witness clause 复用。每个所选 clause 的来源数中位数/P90 均为 1，最大为 3。
- 实际重算了 110,382 个文件、共 17,583,887,267 字节；checksum/字节数不匹配为 0，source payload 的 synset identity 与 witness head 不匹配为 0，索引中缺失来源记录元数据的 link 为 0。
- witness DAG 全部通过结构验证；报告未包含 source path、sense identity、lemma 或 raw gloss。

完整 input hashes、各 depth 分层来源链接数与验证布尔值见 `outputs/phase19/selected_witness_source_lineage.json`。

### Phase 117：锁定输入与实现指纹的 v2 复算

Phase 19 的 v1 artifact 未将 basis 文件哈希写入结果，且未在入口调用冻结包 integrity lock。v2 在运行前核对项目 integrity lock，另外将 `graph/selected_basis_atoms.txt` 的 observed SHA-256/字节数与 sidecar 核对，并记录 manifest、basis、checksums、rules、sense index、witness、lock 与五个实现源文件 hashes、Python version 和 platform。

本次 v2 对固定 bundle 完整重算，结果为 110,340/110,340 个 selected clauses 有来源 link；110,382 个来源文件和 17,583,887,267 bytes 完成 checksum/identity 复核，三类错误计数均为 0。冻结锁、basis checksum、witness graph 和其他 lineage validation 均通过。输出不含原文或路径；详见Phase 117 报告与[机器可读 artifact](../outputs/phase117/selected_witness_source_lineage.json)。这些数字证明锁定 bundle 内的结构来源链可重放，不证明 gloss 语义支持。

v2 输出契约由独立的 [JSON Schema](../config/selected_witness_source_lineage.schema.json) 定义。Phase 117 已使用 Draft 2020-12 validator 检查 schema 合法性，并验证当前 artifact 符合该契约；该检查只验证报告结构与字段约束，不替代来源内容复算。

## 证据边界

该审计把“所选图规则→索引 clause index→source document→校验过的 payload bytes→同一 synset identity”闭合为可复算的结构 lineage。它**没有**检查 gloss span 是否支持 graph literal、WSD 是否正确、AND/OR 方向是否忠实、Horn 规则是否为对象层真实定义、文件是否具有可再发布许可。source payload 哈希正确只表示它与冻结包自身的 checksums 一致。不得把 `all_selected_source_payloads_match_checksums=true` 解读为 entailment、定义质量或许可通过。

此外，selected witness 只覆盖每个 head 的一个选定 OR 子句；对备选 clause 的完整 source lineage 可由 Phase 8 索引 census 覆盖，但 Phase 19 的 payload 重哈希范围是 selected witness 实际引用的 source documents，而非所有备选来源。

## 复算

```powershell
python -m src.analysis.selected_witness_source_lineage `
  --bundle "<固定冻结包路径>" `
  --integrity-lock config/frozen_bundle_integrity_lock.json `
  --output outputs/phase117/selected_witness_source_lineage.json
python -m unittest tests.test_selected_witness_source_lineage -v
```

默认报告写入 `outputs/phase19/selected_witness_source_lineage.json`；已有报告需显式传 `--force` 覆盖。Phase 117 命令显式指定新输出文件，避免覆盖历史 v1。此命令需读取 selected witness 实际引用的 source payload，当前冻结图单次运行重算约 17.6 GB 文件内容；最大单文件默认限制 16 MiB，可通过 `--max-source-bytes` 约束而不自动放宽。自动化测试用隔离的合成 bundle 覆盖成功 lineage、缺少来源 link 与 checksum 篡改拒绝，不触碰真实私有 payload；本轮未运行测试。
