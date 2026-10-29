# Gloss 候选关系验证与证明比较协议（草案）

状态：**可执行研究设计草案，尚未预注册、双标审阅或运行。** 当前 v3 blind batch preflight 通过输入 hash/schema 检查，但本机尚无任何 annotation return；协议未签署、任务未获分发授权。该文件规定未来如何公平比较，不是数据集、结果或预注册声明。

## 目的与核心区分

实验对象是固定 release、义项和原始 gloss 上的候选方向关系。至少要分开回答：

1. 给定一条相同候选关系时，模型能否判断它与 gloss 的语义关系？
2. 给定相同的前提表达时，不同逻辑/词汇推理器能否推出目标、拒绝或返回未知？
3. 从原始 gloss 开始，整条系统能否产出方向正确、source-supported、可复放的规则与证明？

这三问有不同输入和分母。直接 NLI 的分类质量不是规则生成 recall；形式 prover 的证书 replay 不是 source support；WordNet relation agreement 不是人类语义 gold。

## 独立标注维度

以精确的 `(sense, release, gloss, directional hypothesis)` 为判定单元，并保留完整 AND/OR 公式及必要/充分方向，不把合取拆成孤立原子后误报整体正确。双人盲审并裁决以下不同标签：

- `nli_relation_gold`：对精确 gloss–hypothesis pair 的三分类 `entailment / neutral / contradiction`。只有完成该三分类且可裁决的行进入 `nli_gate` 分类指标；歧义或未标行单独计数，不映射到 neutral。
- `semantic_support`：方向规则是否由该 gloss/span 直接支持，使用 canonical annotation schema 的 `supported / not_supported / uncertain / unassessed`。特别是 `not_supported` 不能自动变成 contradiction：欠缺支持并不等于原文反驳该命题。
- `inference_basis`：schema 0.4 的人工说明，表示支持判断所需的最小 lexical/compositional/external/pragmatic/figurative 依据；它既不是 NLI 模型输出，也不改变 semantic-support 标签。
- `evidence_spans`：相对于精确 raw gloss 的 Unicode code-point、左闭右开区间；标出支持/反驳判断的文本依据。无可用 span、但并非明确反驳时可标 unresolved/uncertain，不能虚构字符证据。
- `resource_relation`：WordNet/OEWN hypernym 只作资源相对标签，需单独存储 release 与 relation 路径，不能替代前三种人审标签。

若 `nli_relation_gold` 与 `semantic_support` 不一致，保留并分析不一致，不能用一个标签覆盖另一个。两种标签由不同记录层保存：canonical annotation schema `0.4-draft` 保存来源规则的 `semantic_support` 与 `inference_basis`，当前独立的 `claim-review-record/0.1` sidecar 保存候选 pair 的 `nli_relation_status` / `nli_relation_gold`，并要求两者分开裁决、分别评估。NLI gold 不能静默写入 canonical annotation；sidecar、候选 manifest 和导出文件必须继续使用版本化 schema 与外部锁定哈希绑定。

### `resource_relation` 与 gloss/NLI 标签的桥接契约（schema/评测待审，validator 已实现）

当前已有两个独立端点：claim-review sidecar 保存 `candidate_id`、来源 `sense_id`/release/gloss hash、hypothesis/formula hash 与 gloss 证据 span；OEWN hypernym verifier 对显式 synset pair 生成资源内路径，独立 replayer 校验该路径。Phase 110 新增 bridge JSONL validator，按 candidate ID 和 artifact hash 将这些输入对账；它不会产生 genus-to-sense mapping，也不评分 gloss support。

text-free bridge row 至少锁定以下字段；独立结构 schema 见 [`gloss_oewn_relation_link.schema.json`](../config/gloss_oewn_relation_link.schema.json)，validation output schema 见 [`gloss_oewn_relation_link_validation.schema.json`](../config/gloss_oewn_relation_link_validation.schema.json)。JSON Schema 只表达行/报告的结构条件；候选集一一对应、动态 ID/端点相等、字节哈希、span end>start 和 OEWN release 等跨字段不变量仍由 Python validator 校验。

```json
{
  "schema_version": "gloss-oewn-relation-link/0.1",
  "candidate_id": "candidate-17",
  "candidate_record_sha256": "<canonical JSON UTF-8 row SHA-256, sorted keys/no extra whitespace>",
  "source": {
    "resource": "oewn",
    "release": "<pinned release identifier>",
    "sense_id": "oewn-<child synset ID>",
    "gloss_sha256": "<raw gloss SHA-256>"
  },
  "genus_mapping": {
    "status": "adjudicated",
    "span": {"start": 0, "end": 1},
    "ancestor_synset_id": "<mapped genus synset ID, optional oewn- prefix>",
    "adjudicator_id": "<pseudonymous ID>",
    "rationale": "<why this gloss span maps to this synset>"
  },
  "resource_query": {
    "relation": "hypernym",
    "child_synset_id": "<raw taxonomy ID after removing source's oewn- prefix>",
    "ancestor_synset_id": "<raw taxonomy ID after optional oewn- prefix removal>"
  },
  "verifier_report_sha256": "<report SHA-256>",
  "replay_report_sha256": "<independent replay SHA-256>"
}
```

Validator invariants: the set of bridge `candidate_id`s must exactly equal the complete claim-review sidecar candidate set, with one row per candidate; ambiguous/unassessed mapping rows remain in that denominator. Each ID and canonical row hash identify exactly one sidecar row; the complete sidecar must also match the text-free candidate manifest one-to-one, and the manifest bytes must match an externally pinned SHA-256 supplied to the CLI. Source release/sense/gloss hash equal that row. A supplied span must be within the exact raw gloss and select non-whitespace text; the adjudicator records the genus interpretation, while the validator checks only structural bounds/content and does not verify semantic mapping. Child sense IDs are normalized from the project's `oewn-<synset-id>` identity to the raw pinned-taxonomy ID; the mapped ancestor is a separately adjudicated sense link and normalized the same way (ambiguous/unassessed mappings do not become negative relation labels); verifier query and returned result use the exact pair and pinned release; replay report version `/3` binds the exact query JSONL hash and producer report hash. A positive relation status is reportable only if the independent replay is valid and these byte hashes match. `candidate_record_sha256` is SHA-256 over the canonical UTF-8 JSON object (`sort_keys=true`, compact separators, `ensure_ascii=false`, `allow_nan=false`). Start with ordinary `hypernym`; `instance_hypernym` needs its separate predicate/rules and cannot be silently pooled.

`genus_mapping.status="adjudicated"` requires `span`, `ancestor_synset_id`, `adjudicator_id` and non-empty `rationale`; `ambiguous`/`unassessed` requires a non-empty rationale, may retain a bounded span, and cannot select one ancestor or carry a resource query/report hash. Candidate rows with either unresolved mapping state remain in the bridge output denominator as unmapped; they are never counted as resource-negative.

结构核验入口已实现为 `src.analysis.verify_gloss_oewn_relation_links`。对至少一个已裁决 mapping，调用需提供同一批次的 bridge rows、claim-review JSONL、hypernym query JSONL、producer report 和 replay v3 report，以及预先锁定的 release name/archive hash：

```powershell
python -m src.analysis.verify_gloss_oewn_relation_links links.jsonl claim-review.jsonl candidate-manifest.json --candidate-manifest-sha256 <externally-locked-sha256> --expected-release-name "Open English WordNet 2025 Plus" --expected-release-archive-sha256 8832b8fa26a14c0ba8c99bb1ef8db6f9e122a6d9193b65ca9e0ef572580fee7e --queries hypernym-claims.jsonl --verifier-report hypernym-verification.json --replay-report hypernym-replay-v3.json --output relation-links-validated.json
```

若所有 genus mapping 均为 ambiguous/unassessed，则不提供 resource query 与 producer/replay artifacts；输出只报告映射状态，不声称 taxonomy relation 结果。candidate manifest 与其外部固定 SHA-256 对所有 bridge run 均为必填。验证报告格式为 `gloss-oewn-relation-link-validation/0.2`，当前实现标识为 `gloss-oewn-relation-link-validator/0.3`；该实现除既有的 producer-result 对账外，也逐 candidate 直接核对 bridge `resource_query` 与 query JSONL 行中的 claim/child/ancestor 三元组。Phase119 的[合成端到端 fixture](../examples/synthetic_gloss_oewn_bridge/README.md)保留 validator 0.2 的历史产物；Phase271 已在独立输出目录用 validator 0.3 重新运行 producer→independent replay→bridge，并确认有效输入可通过、错误 manifest pin 和缺失 unresolved 候选均 fail closed。三份成功报告重复运行后字节哈希一致。此工程结果不是真实 candidate bridge；真实获授权、经人工裁决的 mapping 仍缺。Validator 核验 sidecar/manifest 一一对应、manifest pin、report/replay 文件摘要和字段绑定，但不会加载 OEWN archive 重跑 replayer；实际资源路径仍由 producer 加独立 replayer 生成。见Phase271 报告与[机器审计](../sources/phase271_bridge_replay_audit_2026-10-08.json)。

The bridge must report three independent outcomes: human `semantic_support`, human `nli_relation_gold`, and resource-relative `resource_relation` (including unmapped/ambiguous/unsupported states). A valid OEWN path establishes only that the pinned release contains the declared path; it neither validates the genus span-to-synset mapping nor proves that the gloss licenses the relation. Only the human review can adjudicate those links. The relation path may be enabled only in a separately named `resource_augmented` condition; its facts must never be inserted into the `source_only` proof program. A synthetic CLI wiring run exists, but the protocol and bridge contract remain unreviewed/unlocked and no empirical result exists. The text-free link rows still bind study labels and sample identities, so the existing privacy and release gates apply; this draft does not authorize sharing them.

当前 sidecar 草案见 [`config/claim_review_record.schema.json`](../config/claim_review_record.schema.json)，版本为 `claim-review-record/0.1`。候选清单另用 [`config/claim_review_candidate_manifest.schema.json`](../config/claim_review_candidate_manifest.schema.json) 的 `0.2`（validator 仍兼容读取 `0.1`）：保存 candidate ID、split/group/sense、direction、premise/hypothesis 与可选 formula hash，不保存文本、模型来源或 gold；组合候选另记录 operator、component candidate IDs 与各 component 是否取反。组合描述要求同一 group/sense/release/premise/split 下的已冻结成员、可解析的 component ID、无循环引用和 formula hash。`src.analysis.freeze_claim_review_candidate_manifest` 从未标注候选对 JSONL 确定性地产生该清单；其输出 hash 必须在标注前由独立 protocol/preregistration lock 固定。现有 v3 annotation sampling lock 只锁 sense sampling frame，不是 claim-pair 清单，不能代替此 gate。`src.logic.claim_review_validator` 可按外部固定的 manifest file hash 核验 sidecar 与候选清单逐行一一对应，重算文本 hash、核对 span 边界及 train/dev/test group/sense/释义泄漏；组合元数据经 manifest hash 和 candidate ID 绑定，不要求重复抄入标注 sidecar。冻结器和 validator 还要求相同的精确 `premise_sha256`（原始 premise UTF-8 字节，不做 Unicode、空白或 HTML 归一化）只出现在一个 train/dev/test split，即使重复文本来自不同资源、release 或 sense。该规则是严格的**精确释义重复隔离**；hash 不同不代表语义不同，因此它不能替代更广泛的近重复/释义相似度审计。`unassigned` 行不参与 split 冲突判断，正式分配 split 前必须重新冻结并验证清单。该 validator 不判断标签语义，也不替代 release 来源审查。候选来源/system provenance 应保存在独立受限 key。

候选池冻结：`python -m src.analysis.freeze_claim_review_candidate_manifest <unlabeled-candidates.jsonl> <candidate-manifest.json> --candidate-set-version <version>`；manifest 输出为 `claim-review-candidate-manifest/0.2`，命令打印输出 hash，需在收集标注前写入经审阅的外部锁。组合输入行可用 `composition: {"operator":"and","components":[{"candidate_id":"atom-a","negated":false},{"candidate_id":"atom-b","negated":true}]}` 表示 AND-NOT。`formula_sha256` 必须由候选构建阶段按冻结 canonical AST 的规范 JSON 字节预先计算；manifest freezer 校验它的格式并锁定该值，但因不把 AST 内容放入隐去文本的 manifest，不能独立重算它。结构审计命令为 `python -m src.logic.claim_review_validator <sidecar.jsonl> --candidate-manifest <candidate-manifest.json> --candidate-manifest-sha256 <externally-locked-sha256>`。外部 NLI 分数 JSONL 每行包含 `candidate_id`、与 sidecar 完全相等的 `premise_sha256`/`hypothesis_sha256` 和 `scores` 三个概率。导出命令 `python -m src.analysis.export_claim_review_nli_predictions <sidecar.jsonl> <model-scores.jsonl> <output-dir> --model-id <id> --model-revision <immutable-revision> --candidate-manifest <candidate-manifest.json> --candidate-manifest-sha256 <externally-locked-sha256>` 生成 `dev_predictions.jsonl`、`test_predictions.jsonl` 和 `claim-review-nli-export/0.2` `export_manifest.json`；manifest 记录 sidecar、候选清单、model-score 输入及两份预测输出文件哈希，CLI 另打印 manifest 自身 SHA-256 供外部运行锁固定。每条导出预测都携带相同 model ID/revision；若有组合元数据会一并随预测输出，支持预先定义的组合切片统计。导出器要求所有 dev/test 候选已有最终裁决与 NLI 三分类标签、评分与候选一一对应、候选集合与外部固定清单完全相同，且 dev 每个 group_id 只有一个候选；它只从 `nli_relation_gold` 取 gold，绝不将 `semantic_support` 映射为 NLI 标签。生成的两份 JSONL 可直接交给 `src.logic.nli_gate` 的 `--dev-predictions` / `--test-predictions` 做离线分析；组合 proof/NLI 研究路由则须使用 `route_pipeline_result_from_export`，并传入外部锁定的 manifest SHA-256。该入口会核验输出文件字节及跨 split 模型身份，并在路由前移除目标 test 行的 gold。哈希绑定不能证明声明的模型 revision 确实执行过，实验还需保存可审计的模型运行/调用证据。

## 三条互补评测轨道

| 轨道 | 每种方法的共同输入 | 主要问题 | 主要报告 |
|---|---|---|---|
| A. Pair verification | 精确 raw gloss + 精确自然语言 hypothesis；直接 NLI 方法使用同一 pair 文件 | 候选关系分类是否正确 | 3-way NLI macro-F1 / per-class P/R、混淆矩阵、Brier/ECE；独立报告 semantic-support precision/recall、uncertain 覆盖和 abstention |
| B. Oracle-formalized prover | 同一份双人裁决的 sense-linked AST/逻辑前提与同一目标 query；在条件间开关指定 taxonomy/外部知识 | 隔离 prover、proof search 和知识策略，不把 parser 差异计入 prover | `entailed / contradicted / unknown / resource_limit` 分别计数；proof replay、使用的 rule/fact leaves、分区、搜索成本；不将形式状态当作 gloss 支持 |
| C. End-to-end generation + proof | 同一 raw gloss、模型/提示预算及冻结的源资源 | 整体生成—规则—证明—来源链是否达到目标 | 候选覆盖/精确率/参考召回、sense/link、方向/公式正确性、span support、proof replay、source-only 叶比例、拒答与成本 |

轨道 B 使用人工 gold formalization 是一种诊断设置，不是现实全自动系统结果；需和 C 分开报告。C 的候选 recall 只相对于本研究经盲审、有限覆盖的 adjudicated reference set，称为 **reference-set recall**，不能声称召回 gloss 中所有可能的有效规则。池外预测必须追加盲审或记为尚未 adjudicated，不可默认正确/错误。

## 可证伪的研究假设与判据（预注册前草案）

以下是待检验假设，不是当前结果或 novelty claim。主假设只在来源许可、盲标/裁决 gold、matched baselines 和预注册均完成后可检验；数值效应门槛、主要比较和区间方法须在 pilot 后、test 标签揭示前确定并锁定，本文不事后挑选有利阈值。

| 假设 | 可观测量与对照 | 什么结果支持 | 什么结果会削弱/否定 | 不足以判断的情形 |
|---|---|---|---|---|
| **H1：来源约束的端到端管线具有增量价值。** 在相同 sense/lemma/source split、候选池和生成预算下，source-only 的 gloss→方向规则→AND/OR Horn→证据/证明路由，相比事先指定的最强可复现基线，能在相同风险下覆盖更多经双人裁决为方向正确且 source-supported 的候选，或在相同覆盖下减少不受支持/方向错误的输出。 | Track C；共同 adjudicated candidate pool；预先指定一个主要 operating point，并以 source-support risk–coverage 为主曲线；报告 reference-set recall、方向/公式错误、证书重放、拒答和成本。直接 NLI 与定义/词面/sememe 方法仅在输入输出可比的指标上比较，不强行合并成一个分数。 | 预注册的配对主比较达到 pilot 后锁定的效应判据，区间与分组结果支持增益；同时 coverage/cost 没有被未预先声明的退化换取，且 proof/source checks 全部可审计。 | 在有足够精度的共同 gold 上，主要比较未达到锁定判据、基线相当或更好；或表面增益来自降低覆盖、候选筛选、跨 split 泄漏、未支持规则/方向错误，或不可复放证书。此时须缩小/放弃“增量价值”主张。 | 无获准 gold、共同候选或合法且可复算的关键基线；区间过宽；关键标签大量 uncertain/unassessed；来源或模型运行不可审计。此类结果是未识别/不确定，不能说支持或否定。 |
| **H2：保留 AND/OR 结构比简单图压平更能保护整体公式与方向判断。** | 对同一冻结 claim 和人工裁决的整体公式，比较保留 AND/OR 的规则/proof 路由与预先定义的存在弧/合取压平对照；使用方向交换、AND↔OR、删限定挑战；报告 exact-formula、方向正确率、unsupported entailment、proof replay 和成本。 | 在独立 gold/挑战项上，保留结构对预注册目标有稳定增益，且提升不只是形式 replay 成功率。 | 两种表征在预定指标上无差异或压平更好，或结构路由只改善形式合法性而不改善整体语义/来源支持。 | 仅在合成规则程序或当前冻结图上显示结构差异；这可以说明计算表示差异，不能识别 gloss 语义收益。 |
| **H3：证据与证明回放有助于定位错误并支持审计。** | 对盲化系统输出比较错误定位的一致性/耗时、source-span 命中和独立 verifier 结果；与无证据展示条件对照，标注人员看不到系统身份。 | 预注册的人审效率/错误归因指标改善，且不增加错误接受；回放结果与人工 source-support 标签分别报告。 | 回放经常通过但 source support 错误、证据 span 不能定位问题，或展示证据导致更多错误接受；则撤回审计辅助价值主张。 | 只证明 verifier 对某个程序的推导可复放，或只对现存图统计 DAG 结构；不能推断人工审阅更快或自然语言判断更准。 |

**解释规则：** 证明 replay 通过仅支持“对给定程序的推导可复算”；WordNet 关系一致仅支持“对给定 release 的资源关系一致”；NLI 三分类仅支持对应 gloss–hypothesis 关系标签。任何一项都不能单独验证 H1。若多个主结果、切片或阈值中仅部分有利，须按预注册层级和多重比较方案报告；探索性发现明确标记为探索性。`unknown`、`resource_limit`、`uncertain`、`unassessed` 及未回收分别统计，不能并入负例或 neutral。

### Greco et al. 直接 LLM 基线适配

Greco et al. (Findings EMNLP 2024) 已在 WordNet 动词词对提示中提供对应 synset gloss，并判断有向 lexical entailment；其八模型、Direct/Indirect/Reverse prompt 和零/少样本设置构成直接方法先例，而不是可直接引用的本项目分数。作者报告 WordNet 扩展后 116,842 个相关动词对（平衡前），但资源关系标签不等于独立的人类 gloss-support gold，也未控制同提示去掉 gloss 的因果效果。[官方论文](https://aclanthology.org/2024.findings-emnlp.881/)；项目全文筛读见[结构化记录](../sources/literature_screening_log_2026-10-06_definition_entailment_supplement.json)。

若实现该基线，预注册两个不可混合的视图：

| 视图 | 输入/标签 | 允许的结论 |
|---|---|---|
| 资源复现诊断 | 仅限可合法取得且可复算的 WordNet 动词子集；明确 synset pair 扩展、负例构造/平衡、提示、模型 revision 与解码设置；标签绑定固定 WordNet release | 与论文设置的复现/偏差诊断。资源关系 accuracy/F1 不能称为人类语义支持或项目 gold 表现 |
| 项目 matched Pair verification | 与所有方法相同的 sense-linked raw gloss、directional hypothesis、冻结 pair 清单、lemma-group split 和人工裁决；模型只接收 gloss 与候选，不接收 taxonomy label、证明或 gold | 在共同样本上比较三分类 NLI 与拒答；独立报告 `semantic_support`、span support 和 resource-relative relation，不能把一种标签映射成另一种 |

项目主比较至少包含 **gloss-conditioned direct prompt**，可另设完全同模板的 **gloss-ablated** 对照来估计增量；只有配对输入/输出预算、system message、解码、示例及抽样完全一致时，消融差才可解释为 gloss 的提示增量。few-shot 示例只能来自训练折，并按 lemma group 排除测试词族；不得从 Greco 论文的 few-shot 示例或测试标签拼入项目提示。若论文复现模型不可用，应报告模型/提示差异，不能把替代模型包装成复现。该路线只评估给定候选的判断能力；候选生成、规则编译、source-span 定位与 proof replay 仍按轨道 C 和独立指标评估。

## 对照条件与知识边界

同一人工 gold 上可以逐步适配以下路由，但不得把原论文跨任务分数直接放进本项目表格：

1. Direct NLI：仅对 raw gloss–hypothesis pair 评分。
2. LLM-TH 风格条件：typed hyperresolution + entailment ranking；resource fact 和 commonsense assumption 分区，逐条登记证明实际用到的外部前提。
3. Neural-DTS 风格条件：由固定 WordNet release 的 hypernym relation/embedding 提供词汇 axiom，再运行 prover；另报 OOV、resource-relative link 与 lemma/sense 对齐失败。
4. 严格 `source_only`：仅允许双人 adjudicated 的 gloss 支持规则和证书实际使用的 source assertions，不得以词汇 taxonomy、NLI 分数或模型常识充当 source 证据。

所有条件的 proof verifier 可确认推导遵守给定程序；它不能确认输入 premise 为真，亦不能确认词典 gloss 支持某方向规则。外部 taxonomy 条件可回答“在给定资源关系下是否可推导”，而非“此 gloss 本身是否支持”。每条运行须锁定模型 revision、提示/解析器、编译器/prover、阈值、候选预算、资源 release/hash 和原始预测文件 hash。

## 候选池、盲审与控制挑战

1. 在任何 test 标签可见前，锁定系统/提示、dev 选定阈值及每系统 top-K / token / wall-clock 预算。生成并封存测试预测与其 hash。
2. 为 Pair verification 固定一组专家/人工 seed claims、冻结系统输出的去重并集、source-independent lexical candidates，以及预先指定的一因素扰动。人审随机 task ID、乱序、隐藏候选来源、模型分数和图结构；标注回传后不再改候选池。
3. 单因素挑战至少覆盖 direction swap（necessary↔sufficient）、AND↔OR、删去限定、sense/source 替换、从 taxonomy/常识注入无 gloss evidence 的关系。扰动目标只是检验盲审/系统对已裁决输入的鲁棒性；每个挑战标签都由人审核验，不由变换代码自动充当语义 gold。
4. 对精确 hypothesis 字符串做精确 hash 和去重；保留 surface paraphrase 作为不同 NLI 输入。结构等价的 FOL/AST 归并只在规则 parser 和 canonicalizer 版本事先冻结时使用；原始文字结果仍保留。
5. 系统输出池中每个 claim 保留不可见的 producer provenance，以便按系统计算输出指标；人审界面不得展示该字段。对共有候选交集与每个系统完整输出分别报告，防止只报容易的共同子集。

## KDD 2026 几何组合基线的 gloss 适配切片

Moreira et al. 的 KDD 2026 版本在约 200 个 Gemini 3.1 Pro 候选经人工筛选、再排除原子 baseline 判断错误后，构造 600 个由原子假设组成的 conjunction/negated-conjunction pair。项目可借鉴其“原子关系 → 组合假设 → 几何评分”的诊断结构，但不得把 WordNet gloss 当作完整场景描述，也不得从原子 NLI 标签自动推定 gloss source-support gold。

建议在未来获批并裁决的 gloss claim pool 上单独建立组合切片：

1. **冻结成分 claim**：同一 sense、release 与 raw gloss 下，先固定至少两个具有独立自然语言表述的原子候选；每个原子候选都保留完整方向、公式 AST、字符 span 和 candidate ID。组件的 NLI relation、`semantic_support` 与 `inference_basis` 分别由盲审裁决，不能用系统分数或 taxonomy edge 代替。
2. **冻结组合形式**：从有资格的组件产生有界的 `AND`、`AND NOT` 组合；组合 JSONL 行记录完整自然语言 hypothesis、formula AST 的规范 hash，以及以 component candidate IDs 表示的 `composition` 树。manifest freezer / validator 必须验证 component 存在、与父项 sense/source/group/split/premise 一致、依赖无环；NLI export 保留组合标签以分层报告。若今后扩展到 `OR`，须作为项目新增切片单报，因为 KDD v2 的组合 entailment 主评测覆盖的是 conjunction 与 negated conjunction，并未给出 OR 的对应 gold AUC。
3. **组合项重新裁决**：组合 pair 本身再由两位标注者独立判定 NLI 三分类与规则级 source support，并裁决 necessary/sufficient direction、完整组合公式及证据 span。不得只依据组件标签用布尔表生成 final gold：语言中的范围、预设、词义与定义覆盖差异可能改变整句关系。`not_supported` 仍不自动等于 NLI contradiction；`uncertain`/`unassessed` 不映射到 neutral。
4. **防止条件化偏差**：主结果包含所有事前合格、已裁决的组合 pair，不因某个 baseline 在其原子组件上出错而排除。另可报告“各模型都判对原子组件”的 conditional subset，清楚标为诊断性条件结果，并报告它与完整资格集的分子/分母差异。这样既可与 KDD v2 的 baseline-filtered 设计讨论可比性，也避免把筛后容易样本的指标冒充无条件组合能力。
5. **同候选比较**：在相同候选文字、同一 group-disjoint split 和冻结预算下比较原始 gloss NLI、KDD subspace inclusion/composition、向量 MLP、可实现的 box baseline、人工 gold AST 上的 Horn/proof 路由。KDD 几何基线分数只作为 NLI/组合行为读出；Horn 路由额外报告来源 proof replay。每种方法都对同一候选池计分，系统独有生成另走端到端 Track C。
6. **分别报告结果**：NLI relation 报 3-way macro-F1、混淆矩阵与校准；source support 报 supported precision/recall、coverage 与 abstention；组合一致性按 AND/AND-NOT（以及将来 OR）分层；Horn 条件报告证书 replay、proof fact partitions、span/annotation binding。严禁把 NLI accuracy/AUC、resource-relative hierarchy、source support 和证书正确性合并为单个准确率。

该切片须先通过标注方案/许可审阅、外部锁定候选 manifest 和双标裁决启动 gate；目前没有符合条件的 component gold 或组合候选，故它是已细化的实验计划，不是已建数据集或有效性结果。KDD 对照的事实、代码和方法边界见[最近工作矩阵](closest_work_comparison.md)及[KDD 筛读记录](../sources/literature_screening_log_2026-10-05_iclr_lattice_and_kdd_subspaces.json)。

## Split、指标与统计

- 用 lemma-group 分组隔离 train/dev/test，sense 也不得跨 split；相同精确 raw-premise UTF-8 SHA-256 也不得跨 split（跨资源、release、sense 一并检查）。候选 freezer、manifest validator 与 standalone NLI dev/test evaluator 均实施这一门槛；NLI evaluator 一旦接收任一 premise hash，要求所有行都带 hash。`group_id` 在校准文件中每组唯一一行。另建立 dictionary/source cold split，独立报告其样本数；精确哈希隔离不代替近重复审计。
- 仅在 dev 调整 NLI 阈值或系统设置；test 预测文件和代码版本先冻结，再揭示裁决 gold。主结果只跑一次锁定 test；事后方案变化标为 exploratory。
- Track A 分别报 NLI 三分类与 binary source-support 层，不将两者混合成单分数；按 `inference_basis`、POS、sense ambiguity、候选类型分层。区间按 lemma-group 聚类/重抽；含随机分层抽样时再使用设计权重，并明确说明指标适用的分母。
- Track B 报证书有效率/拒绝原因、grounded proof 深度/成本、resource/external/source fact leaves；主指标中明确区分 source-only 与条件性知识增强结果。
- Track C 报每系统生成候选数量、候选去重规则、reference-set precision/recall/F1、semantic-support precision、coverage/abstention、proof replay 及单位成本；无 adjudicated gold 的池外 claim 计为待审，不并入真负例。
- 同时报告全部资格样本、uncertain/unassessed、未回收、裁决冲突和许可排除的数量；不得事后删除难例或把未标项计为 neutral。

## 可复算输入与当前启动门

每批候选/标注需保存：release 与原始 gloss hash、hypothesis hash、schema 与候选生成器版本、split/group manifest、模型/prompt/prover revision、预测文件 hash、盲标 task/answer-key 分离 hash、裁决/deviation log 和完整运行命令。含 gloss、义项 ID、answer key 的任务与结果只限本地，直到逐来源许可审查和发布 gate 放行。

2026-10-05 对 `audit_annotation_preregistration_v3_inputs` 的只读 preflight 显示 frame/batch/release hashes 和结构均通过（400/400 tasks，24 strata），但 `annotation_return_files=0`、`protocol_signed=false`、`external_preregistration_id=null`、`distribution_authorized=false`。故当前没有可计算的标注一致性、NLI gold、semantic-support gold、matched baseline 或论文性能；preflight 的 `integrity_pass=true` 只证明输入锁和格式，不是数据授权或注册。

**启动确认性评测前置条件**：审阅并冻结本协议与两个 schema；确定双标/裁决人员、授权与许可；用正式获批的 candidate manifest 核验 sidecar 来源；锁定模型/预算和去重规则；完成盲标回收及裁决；再生成 lemma-group split 与 dev/test 文件。validator/adapter 的工程实现本身不表示这些前置条件已完成。任一 gate 未满足时，只能做结构预演或合成 checker 检查，并清楚标为模拟/工程验证。

### ACL 2023 NLI/推理链 baseline 补充（Phase 65）

近邻审计要求增加两类可适配 baseline：PROVER-style 多步自然语言 inference generation（下一步预测、检索与 composition）及 ReCEval-style chain correctness/informativeness scoring；两者属于文本推理链，不等同于 Horn certificate replay。逻辑挑战集可借鉴 SICCK 的 hypernym、negation、quantifier/modifier compositional slices，但必须在 WordNet sense-disjoint gold 上人工裁决，不能直接把 synthetic NLI 标签当 glossary rule support。证据路径需加 FEVER-style source span retrieval/候选召回，并单独设 gold-source upper bound；在固定 evidence 下评价 NLI、在 source-only Horn 输入下评价形式重放，两者分开报告。此为 baseline 设计建议，不代表上述系统已在本项目运行或结果可横向比较。详见Phase 65 报告。

### ACL 2022 NLProofS / semantic parsing baseline 补充（Phase 66）

纳入 NLProofS-style natural-language proof generation + trained step-validity verifier + proof search 作为强链式基线，但其分类器分数不得冒充形式证明。若适配，固定 source/support facts、候选池和 beam/token budget，分别记录 supporting fact recall、每步 verifier score、人审 validity、AND-premise completeness 与独立 Horn replay。加入 Dual-(m)T5-style PL/FOL parser 并分离 generated-form↔gloss semantic fidelity 与下游 NLI。ZS4IE-style verbalization+NLI 可作 label verbalization baseline；TextGraphs/SBERT 作 premise retrieval baseline；gold-premise/gold-span 设置只能标为 retrieval oracle。所有结论需来自同一经裁决 blind test，当前项目尚无这样的结果。详见Phase 66。

### ACL 2021 theorem-prover / Horn baseline 补充（Phase 67）

增加 Sumita-style interactive theorem-prover NLI 作为词汇子目标交互/证明流程对照；RuleBERT-style soft Horn reasoning 作为给定规则/事实下的神经推理对照；UniKER-style definite Horn forward chaining 作为显式逻辑规则推理对照；WinoLogic-style solver-verified knowledge→answer support 作为形式语义/自动定理验证模式对照。另以 Gupta-style related-input program consistency 和 Huang-style meaning-preserving parser robustness 设计解析器稳定性切片。比较时分别测：规则 AST/类型正确性、gloss span semantic support、AND/OR completeness、source-only proof replay、NL prover/神经 verifier 输出；不可用规则输入成立时的 solver 成功代替“原 gloss 蕴含规则”。截至本阶段，上述系统均未在项目上运行或与项目作 matched evaluation。详见Phase 67 报告。

### Phase 123：执行态 matched-baseline readiness crosswalk

现将三轨协议与当前实现/工件逐项对账：[evaluation readiness matrix](evaluation_readiness_matrix.md)。截至 2026-10-07，冻结超图来源结构和 OEWN taxonomy stress replay 有结构性可复算证据；bridge 成功/失败只在 synthetic fixture 上验证。Pair verification 没有项目候选对、人工 NLI/semantic-support gold、模型分数或 dev/test 预测；oracle-formalized prover 与 source-only/end-to-end 路由没有真实 gold-backed run。Phase 121 的 400 项 annotation package 通过本地输入完整性检查，但 0 回传且未签署/未授权。

因此三个 track 的共同输入、基线类别与分离指标已有协议设计，但尚无真正的 matched baseline result。启动顺序现明确为：逐源 rights/attribution gate → 冻结 primary estimand/不确定项处理 → claim-pair frame/hash 和 group split → 获授权双标/裁决 gold → 冻结模型/预算/held-out 预测 → 分轨运行与独立 replay。任何当前结果只可支持其窄工程/结构结论，不能写成模型有效性或新颖性证据。

### Phase 141：Track A 的 lemma-aware premise 表示尚未定义

当前 `claim-review-record/0.1` 和 candidate manifest/0.2 把模型 premise 与 `source.gloss_sha256` 绑定为同一段 raw-gloss UTF-8 字节；source 只暴露 resource/release/sense ID/POS/hash，不存目标 lemma。hypothesis 模板也未冻结，因此尚不能保证人类 adjudicator 与 NLI 模型看见相同的目标词义上下文。Sense ID 是 provenance key，不是模型可理解的上下文。建议在创建 pair frame 前审阅版本化的确定性 premise renderer：primary pair 同时显示目标 lemma 集、POS、原始 gloss；人审和模型使用相同 premise/hypothesis，另以 raw-gloss-only 作为配对输入上下文消融。raw gloss hash 与 rendered premise hash 必须分开记录，新版 schema/manifest 明确锁定 renderer 与 hypothesis 版本；不得静默改变 `/0.1` 的 hash 契约。现有 sidecar 与 NLI-score 文件为空，因此这是待研究者确认的输入定义，不是观察到的模型影响。见Phase 141 报告和[机器审计](../sources/claim_pair_premise_context_audit_2026-10-08_phase141.json)。

### Phase 142：加入 ACL 2026 staged grounded-claim prompt 作为候选适配基线

Ye et al. (ACL 2026) 已有原子 claim 分解，以及按实体、描述、关系、可推断性逐步检查来源支持的 factuality prompting。若后续纳入 Track A/Track C，只能在同一冻结 premise/hypothesis、sense split、标注标签和推理预算上做项目内适配比较；分别报告方向正确、span/source support、理由定位、abstention 与成本。该方法在长文档 factuality benchmarks 的结果不能作为本项目基线分数，也不能由理由文本推定 proof certificate 有效。候选 Track A frame 仍为空，主上下文及 hypothesis 模板仍须在标注前冻结。全文范围与边界见Phase 142和[机器筛读日志](../sources/literature_screening_log_2026-10-08_grounded_claim_factuality_acl2026.json)。

### Phase 144：候选 sense 的 target metadata 来源规则

Track A 新 frame 若复用 v3/400 的 sense IDs，必须从固定 OEWN release 以 sense ID 重取 POS 和完整 lemma set。v3 frame 目前有 1 个 POS 与 release 冲突、1 个 lemma set 不完整；这两个值也原样进入 blind batch。保留 v3 原字节，不把其 blind/frame 一致当作身份验证。对每个新 premise 分别绑定 raw-gloss hash 与 renderer 后的 premise hash。候选 parent synset 有多词 lemma 的情况须预先冻结 deterministic hypothesis surface/多表面设计；parent ID 留在模型外 provenance。资源 hypernym edge 只定义候选 strata，不赋予 entailment 或 semantic-support 标签。相关输入审计见Phase 144。

## Phase 145：父 synset 多 lemma 的候选规模与 split 闭包审计

新增 `python -m src.analysis.audit_track_a_hypothesis_surface_policy`，先复核 Phase144 锁定输入和 OEWN 归档，再只输出数量统计。对 322 条直接 hypernym edge，逐个父 lemma 建候选会得到 680 个不同的 target-sense × surface hypothesis 组合；每边取一个词面为 322 行但 lexicographic 选择不代表语义 canonical。177/322 边有多 lemma。edge 只覆盖名词/动词关系。把边、目标义项/lemma、父 synset/lemma 和当前 raw-gloss hash 做草案闭包时，680 行形成 279 个组件，最大组件 26 行；真实 premise hash 和最终切分目标尚未锁定，须在 renderer 冻结后重算有效组数和 strata 平衡。

建议评估“每个父 lemma surface 一行、同一 child-parent edge 保持同组”的设计，并对每个精确表层 pair 单独标注；若成本需下采样，预先规定抽样及分层，不把词典序当成语义偏好。primary estimand 应明确按 surface 还是 edge 汇总，避免多 lemma 父项在逐行指标中过度加权。现有 manifest/0.2 没有 parent synset/relation-edge 字段；未来应以新 schema/manifest 版本绑定资源关系身份及表层假设 hash，不改变旧版本契约。此审计没有生成 pair、split、标签或模型结果。详见Phase 145 报告与[机器统计](../outputs/phase145/track_a_hypothesis_surface_policy_audit.json)。

### Phase 146：渲染 premise 的双哈希、分组和路由契约

静态追踪确认 `/0.1` claim sidecar 将 `source.gloss_sha256`、`premise_sha256` 和 premise 文本绑定为同一 raw-gloss 字节，并以 premise 坐标检查证据 span；NLI exporter/strict route 又把 premise hash 当作 raw source hash。父 synset/edge identity 也不在 manifest/0.2。更关键的是 `group_id` 同时用于跨 split 泄漏隔离与 certified dev 校准独立单位（一组恰好一行），因此 680 个 surface/context rows 不能简单共用 edge group 后照旧送入 calibration。建议新 schema 分开 raw gloss/model premise hashes、raw-gloss spans、parent relation provenance、split leakage component 与 statistical/calibration unit；原 `/0.1`、manifest `/0.2`、export `/0.2` 保持不变。具体影响与迁移选项见Phase 146 深度报告及[机器证据](../sources/track_a_context_contract_audit_2026-10-08_phase146.json)。当前尚未选 context-specific NLI gold 定义或 cluster calibration 方案，无实现、pair、labels 或模型运行。

### Phase 147：Track A pair contract 设计选项汇总

综合 Phase144–146，形成[Track A pair contract 设计草案](track_a_pair_contract_design_options.md)：建议模型输入 primary 为 pinned target lemma set + POS family + raw gloss，并设置 raw-gloss-only 配对条件；parent 每个 lemma surface 单独构成 hypothesis，按 relation edge 关联；`semantic_support` 只判断 raw gloss 支持且 spans 锚定 raw gloss，`nli_relation_gold` 则按 exact premise condition 裁决，资源 edge 标签单独保存。所有内容均未冻结：680 个 surface hypotheses × 两种输入条件意味着最多 1,360 pair-condition 行、双标最多 2,720 条独立返回；现 NLI gate 的一组一行 IID 校准规则不适用于未聚合的多 surface rows。正式生成前还须选择 estimand/statistical unit、split-leakage component 和 verb hypothesis grammar。此草案没有生成样本或标签。

### Phase 204：可证伪标准与当前实现边界对账

H1–H3 已给出支持、反驳和不可判断三类结果判据；但尚无锁定的 primary estimand/operating point、候选 manifest、gold 或 matched run。工程可运行的 generic freezer/validator/exporter 不能证明研究轨道已可直接执行。Phase202 静态接口审计确认，pinned OEWN edge/surface inventory、claim-review `/0.1`/manifest `/0.2` 与单义项 annotation importer 属于不同合同；当前字段不能绑定 parent surface / `relation_edge_id`，也不能同时保留 raw-gloss 和 rendered-premise 双哈希。新增 contract 和 Track A gold 的实现须等研究者裁决，并另建版本；此处不改旧协议条款或 schema。详见[主张—证据交叉表](research_claim_evidence_crosswalk_2026-10-08_phase204.md)、Phase202 报告及[机器审计](../sources/track_a_implementation_compatibility_audit_2026-10-08_phase202.json)。

### Phase205：source-only strict route 的双哈希接口限制

源码追踪发现，当前 composed strict route 将测试 `premise_sha256` 与 canonical annotation 的 raw `source.input_sha256` 比较，并要求事实来源 binding 的 `gloss_sha256` 等于同一 premise hash。此契约适用于 raw-gloss premise；对草案中的 lemma+POS+gloss renderer，渲染文本 hash 应与 raw-gloss hash 分开，故当前 source-binding route 不会接受这一输入条件。route 还按 `wn_sense:<sense_id>` 绑定 query，没有 Track A `relation_edge_id`/parent surface 键。复用旧哈希字段会混淆上下文输入身份与证据原文身份。新契约只有在设计冻结后才应另行版本化双哈希、condition/renderer 和 edge/surface 字段。静态审计不构成 Track A 运行结果；详见Phase205 报告与[机器审计](../sources/track_a_proof_route_compatibility_audit_2026-10-08_phase205.json)。
