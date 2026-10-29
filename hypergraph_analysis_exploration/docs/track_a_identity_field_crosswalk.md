# Track A 跨层身份字段对照（Phase234）

**状态：静态接口审计；不构成 Track A 设计批准，不冻结或迁移 schema，也没有生成 pair、label、split 或模型输出。** 本文用于精确定位资源关系身份从 OEWN inventory 到 claim-review/proof/NLI 路由的传递断点。逐文件 SHA-256 见[机器审计记录](../sources/track_a_identity_field_crosswalk_2026-10-08_phase234.json)。

## 现有字段如何流动

| 层 | 当前身份字段与行为 | 能支持的结论 | 到下一层的缺口 |
|---|---|---|---|
| OEWN edge inventory | `build_oewn_hypernym_candidate_inventory.py` 为每条直接 edge 生成 `relation_edge_id`。ID 输入含 pinned archive SHA-256、relation、child synset ID、parent synset ID；记录另含 child/parent sense、POS 和 lemma surface 列表。surface 是 edge 下的属性列表，没有各自独立 surface ID。 | 给定固定 release 的 edge 身份可稳定复算；候选 surface 的清单可枚举。inventory 明确不是标注输入，不含 gloss、hypothesis、抽样或 split。 | `relation_edge_id` 和 parent lemma surfaces 没进入 claim-review candidate 或 export contract。 |
| OEWN 路径 verifier | 接收 child/ancestor synset pair；验证 pinned release 的方向可达性，正结果附路径和 resource proof。 | 证明该 release 中 synset pair 的直接/传递关系与可回放路径。 | 未接收 gloss hash、hypothesis surface、`relation_edge_id` 或 condition identity；它的结果不能自动附到 NLI/annotation row。 |
| Claim-review record `/0.1` | 记录 `candidate_id`、`group_id`、source resource/release/sense/POS、premise 与 hypothesis 及其 hash。validator 强制 `premise_sha256` 与 `source.gloss_sha256` 都匹配同一 premise 字节；evidence span 也按该 premise 的 Unicode code point 计。 | 单一 sense、单一 premise/hypothesis 下的人工 semantic-support/NLI 标签结构与字符跨度检查。 | 不能表达 raw gloss 与 rendered premise 的两个 hash、renderer/condition，也没有 parent synset、edge 或 lemma-surface identity。 |
| Text-free candidate manifest `/0.2` | 每行冻结 candidate/group/split/source/direction、premise/hypothesis hash，可选 relation/formula/composition。 | 将具体文本输入的 hash 和 split/group 绑定到 candidate ID，检查 sidecar 与 manifest 一一对应。 | 不携带 `relation_edge_id`、parent synset/surface、target lemma-set identity 或 renderer/condition。`source` 仅含 resource/release/sense/POS。 |
| NLI export `/0.2` | 把 `candidate_id` 同时用作 `example_id` 和 `claim_id`，带 sense/group、premise/hypothesis hash、预测分数、model ID/revision；文件和 manifest 有 hash。 | 复算固定 candidate set 上的 NLI 预测导出身份及线上 strict route 的单 claim 绑定。 | `claim_id=candidate_id` 不是 formal annotation claim ID；导出没有资源 edge/surface/condition 外键。模型 revision 是调用方声明并被文件绑定，不是推理环境独立证明。 |
| Strict proof/NLI route | 按单条 `sense_id`、source gloss/premise hash、hypothesis hash、annotation `claim_id` 和模型导出身份复核证书与 NLI 路由。 | 在现有单 sense、同一 raw-gloss/premise 条件合同下，重放给定规则与 proof，并检查输入 hash/裁决记录绑定。 | 不能把 OEWN edge verifier 的结果关联到具体 parent surface/hypothesis，也不能区分配对 premise conditions。 |

## 对 Phase226 结论的精化

Phase226 所说的“资源关系与形式/NLI 两条路由没有共享 `relation_edge_id`”仍然成立，但应理解为**跨层没有传递/联合使用**，而非整个项目都没有 edge ID。现在的准确断点是：上游设计 inventory 已有 release-bound edge identity；进入 claim-review candidate、manifest、NLI export 和 strict proof route 时，合同退化为单 sense/candidate identity，无法确认末端候选究竟对应哪个 parent edge/surface/条件。

这属于接口能力缺口，不是两条局部 verifier 已发现的正确性缺陷。旧契约对其当前输入范围仍然有效；不能将 source gloss relation、OEWN resource relation、NLI label、形式证明合并成一个 `verified` 标签。

## 版本化实施前必须先冻结的决策

这些字段缺失的填补方式取决于仍未确认的研究对象，不能由 schema 维护者单方面决定：

1. 一条 parent synset 的全部 lemma surfaces 是否逐一成为 hypothesis，及 surface-level 与 edge-level outcome 的汇总目标；
2. primary estimand/statistical unit、split leakage component 与每组行数；
3. `lemma_pos_gloss` 与 `raw_gloss` 是否作为配对条件，以及 source-span 坐标始终锚定 raw gloss 的规则；
4. 哪些 POS/模板进入首轮、NLI 两条件标签是否各自独立裁决；
5. 授权 frame、标注责任、协议签署与来源许可范围。

在这些决策确定前，可复核旧接口和上游资源 inventory，但不得通过重命名 `candidate_id`/`group_id` 假装它们已经是 edge/statistical unit，也不应迁移现有 `/0.1`、manifest `/0.2` 或 export `/0.2`。

## 核验来源

实现与字段位置：[`build_oewn_hypernym_candidate_inventory.py`](../src/analysis/build_oewn_hypernym_candidate_inventory.py)、[`oewn_hypernym_verifier.py`](../src/analysis/oewn_hypernym_verifier.py)、[`claim_review_validator.py`](../src/logic/claim_review_validator.py)、[`freeze_claim_review_candidate_manifest.py`](../src/analysis/freeze_claim_review_candidate_manifest.py)、[`export_claim_review_nli_predictions.py`](../src/analysis/export_claim_review_nli_predictions.py)、[`verified_reasoning_pipeline.py`](../src/logic/verified_reasoning_pipeline.py)。研究选择仍由[Track A pair contract 草案](track_a_pair_contract_design_options.md)及[设计裁决备忘录](track_a_design_decision_memo.md)保留为未决项。
