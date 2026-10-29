# Evaluation readiness and matched-baseline matrix

**Audit date:** 2026-10-08  
**Status:** Implementation/readiness crosswalk; not a preregistration or empirical result.  
**Scope:** Current code and durable artifacts in this worktree for the WordNet/OEWN gloss-to-formal-reasoning goal.

## What can currently be claimed

| Evidence layer | Current implementation / artifact | What has been observed | Maximum defensible statement now | Missing for a paper-level claim |
|---|---|---|---|---|
| Frozen hypergraph structure and selected witness provenance | Frozen bundle audit, AND/OR analysis, witness DAG/source-lineage artifacts; see phase reports linked from project docs | Phase213 current replay matches Phase206 byte-for-byte; the full structural audits and Phase117 source-lineage replay bind structure to the frozen bundle | The declared frozen graph structures/witness payloads can be structurally checked and reproduced under the pinned bundle | Human gloss semantics; validation of whether source clauses encode the gloss; release rights for redistribution; independent clean-environment reproduction where not already recorded |
| Resource-relative hypernym closure | `src/analysis/oewn_hypernym_verifier.py`, independent replay v3; `outputs/phase118/oewn_hypernym_stress_v1_replay_v3.json` | 360 fixed stress claims were replayed; artifact says `valid=true` | The pinned OEWN release supports the reported synset paths for this stress frame and the path certificates replay | It does not validate genus-span→synset mapping, gloss support, or predictive accuracy; a human-mapped shared candidate set is still absent |
| Bridge wiring | `src/analysis/verify_gloss_oewn_relation_links.py`; synthetic example under `examples/synthetic_gloss_oewn_bridge/`; Phase271 outputs under `outputs/phase271/` | Validator 0.3 producer→independent replay v3→bridge succeeds; repeated outputs byte-match; bad external manifest pin, missing unresolved row, and mismatched query triple with internally matching report pins fail closed | The manifest/hash/denominator/query-row contracts work for this marked synthetic fixture | Real gloss candidates, human-adjudicated genus mapping, release/rights review, and semantic-support labels |
| Track A: pair verification (direct NLI and semantic support) | Candidate-manifest freezer, claim-review validator, NLI exporter, `src/logic/nli_gate.py`; schemas in `config/` | Interfaces are present; Phase205/214 confirm the strict route is still single-sense and cannot bind relation-edge/parent-surface identities or distinct raw-gloss/rendered-premise hashes; no project candidate pair manifest, adjudicated pair labels, model-score file, dev/test predictions, or result artifact is present in `outputs/` | The intended data and routing contracts are documented/implemented; no model-quality statement is available | Researcher-approved edge/surface/condition contract; authorized frozen candidate pairs; independent NLI and semantic-support double labels/adjudication; locked model/prompt and independently auditable inference provenance; valid cluster-aware uncertainty/calibration or descriptive-only reporting; lemma-group and exact-premise-hash splits; near-duplicate review; common predictions and metrics |
| Track B: oracle-formalized prover | Annotation compiler, typed Datalog checker, source-only pipeline, certificate/countermodel replay | Code supports reviewed records and declared facts; no project gold-backed Track B run artifact is present | Formal consequences of a supplied program can be checked within the supported finite positive Datalog fragment; this is conditional on supplied premises | Real adjudicated formalizations and facts; locked queries; source-only/resource-augmented conditions on the same items; per-item proof/rejection/runtime record |
| Track C: end-to-end gloss→rules→proof | `verified_reasoning_pipeline.py`, source-record/strict routing components, and multi-reference sidecar/scorer (`gloss-analysis-reference-scorer/0.5`) | No real end-to-end gloss-generation result exists; Phase 119 exercised the separate taxonomy bridge with synthetic sentinel input; Phase 131 added exact resource/version/record/license/input-hash and synset/lemma/POS/gloss identity binding across linked references and predictions | The implementation can enforce parts of the composition and scoring contracts; current execution evidence does not show gloss-to-rule fidelity, reference-set completeness, or end-to-end success | Authorized real gloss inputs, blinded gold, frozen primary estimand and prediction-blind adjudication, frozen generation budget/model and candidate pool, matched baselines, source-span evaluation, independent proof replay and complete failure/abstention accounting |
| Human evidence / gold | OEWN 2025 Plus 400-item blind annotation package and `config/annotation_preregistration_v3_lock.json`; fresh preflight in `outputs/phase121/annotation_preregistration_v3_input_preflight.json` | 21 input checks pass; 400 raw glosses crosscheck exactly to pinned release; manifest carries attribution/license links and modification/use-limit notices; 400 tasks, 400 key rows, 24 strata; 0 return files; `protocol_signed=false`; no external registration ID; `distribution_authorized=false`; Phase 131 scorer-side identity validation does not validate adjudication completeness or label quality | The local candidate package is byte/schema/release-crosscheck ready for further review; no empirical gold is available | Project-owner review of intended external-use scope and underlying Princeton WordNet terms; signed protocol/estimand; responsible personnel; out-of-frame usability/time pilot; registration and explicit authorization; independent human returns/adjudication/IAA |

## Phase265 prior-art implication: downstream validity does not establish gloss fidelity

ACL 2026 CoPE (Huang et al.) evaluates whether plans execute and satisfy a ground-truth PDDL task. Its authors explicitly acknowledge a valid plan can coexist with formal code that failed to faithfully encode the natural-language constraint; their 20-item false-positive audit is a bounded sample, not a universal fidelity guarantee. For this project, keep raw-gloss span support, typed rule/formula correctness, proof/countermodel replay, and downstream query utility as separate outcomes. The new review does not change the matrix above: there are still no authorized gold-backed Track A/B/C runs. See Phase265 report and [full-text log](../sources/literature_screening_log_2026-10-08_acllong2026_cope_fulltext_phase265.json).

## 2026-10-08 current-state addendum (Phases 155–160)

The matrix above remains the evidence-layer baseline; the following changes refine implementation status without upgrading any empirical claim:

- **Typed compiler:** experimental `0.7-draft` and compiler v6 support a restricted multivariate positive-Horn fragment with an explicit target variable and direction-specific safety checks. This path has only static syntax evidence; no boundary-case runtime replay, authoritative WordNet type inventory, blind 0.7 task/return materials, or real annotation exists.
- **Source-only route:** Phase157 added multivariate source-fact grounding checks and Phase160 makes optional typed validation diagnostics visible at the strict-route boundary. Pipeline is now `/13`; invalid typed program is an `unknown` reason, and an untyped run reports `not_requested`. No end-to-end 0.7 proof/source-bundle/NLI route has been run in these phases.
- **Related work:** Phase159 screened T² (ACL Industry Track), FoVer (Findings ACL), and SemEval Task 11. These add formal-behavior, verifier-supervision, and content-effect evaluation precedents, not a matched WordNet gloss-to-Horn baseline. Screening remains selective rather than a systematic review.
- **Annotation readiness:** current v3 blind batch still emits canonical schema 0.4. Phase158 only made the importer schema-selectable; it did not create version-specific 0.7 task/UI/return materials or authorize a new batch.

- **Related work (Phase182):** COLM 2026 Goedel-Code-Prover makes hierarchical proof search and kernel-checked final proofs established method neighbors. It begins from formal Lean specifications, so it is neither a gloss-semantic result nor a matched lexical baseline.

Primary records: Phase155, Phase156, Phase157, Phase158, Phase159, Phase160.

## 2026-10-08 current-state addendum (Phases 205, 213–214)

- **Frozen structure (Phase213):** current frozen hypergraph and minimum-witness audit outputs match Phase206 byte-for-byte; all bundle/closure/witness structural checks pass. The selected-witness descendants still overestimate exact non-seed AND/OR closure loss in 66/85 basis deletions. This validates a fixed structural snapshot, not gloss semantics or research efficacy.
- **Track A contract (Phase205/214):** current strict proof/NLI route binds a test prediction to a single sense/claim and treats source gloss and premise hashes as the same identity. It cannot represent relation-edge/parent-surface identity or the proposed rendered-premise conditions. The design memo remains unconfirmed; no schema migration or pair generation is authorized by the proposal itself.
- **NLI assurance boundary (Phase214):** fixed-grid exact-binomial/Bonferroni calibration is conditional on IID calibration units, a frozen model/grid, and a stable target distribution. Unique group IDs detect duplicate keys but do not establish IID. Export artifacts bind a caller-declared model revision; independent inference-execution attestation is absent.
- **Research claims:** H1–H3 remain unmeasured hypotheses. No gold labels, matched baseline runs, or project effect estimates were added in these phases.

Primary records: Phase205, Phase213, and Phase214.

## 2026-10-08 current-state addendum (Phases 218, 228–232)

- **Launch gate (Phase218):** the locked 400-item v3 package is internally byte/schema/release-crosscheck reproducible, but `protocol_signed=false`, `distribution_authorized=false`, registration is absent, and no returns exist. It is not Track A gold. Track A still has no approved estimand/frame/label contract and must not produce candidate pairs, labels, splits, or a schema migration until the documented design and authorization gates are resolved.
- **Basis/source lineage (Phase229):** all 85 basis identities match nodes and sense index; all 166 associated source-record payloads pass sidecar size, SHA-256, and sense-identity checks. All 154,206 graph clauses have one active source-index row (154,356 clause-document links). This is identity/byte lineage, not source semantic support or clearance.
- **Deletion sensitivity (Phases230–231):** deleting complete sense payload bundles in 3,570 basis-pair scenarios, and deleting one payload in 166 scenarios under explicit permissive/strict clause-retention policies, yielded loss sets equal to the corresponding seed-only deletions. Phase230 direct checks: 4; Phase231: 24; both independent-path replays were byte-identical. These results apply only to the fixed graph and stated bookkeeping interventions; the producer's multi-source semantics and upstream-document effects remain unvalidated.
- **Novelty boundary (Phase228):** reliability engineering/fault-tree importance and minimal cut-set work predate pairwise interaction analysis; the project's Phase227 pair/head statistics therefore do not support a novel interaction-method claim or a source-redundancy interpretation. The 2026 ACL/ICLR/LREC/CL search refresh found the immediately relevant records already represented in the current local screening/comparison files; it did not add a new confirmed nearest-neighbor paper in this pass.
- **New structured-evidence neighbor (Phase232):** NeurIPS 2026's accepted LogicTree-RAG grounds a hierarchical logic tree in retrieved source spans and evaluates node-level evidence support with an LLM judge plus a 20-case human audit, alongside a separate patent-expert study. General logic-tree + evidence grounding + human faithfulness review are prior art; the paper does not evaluate WordNet sense-level gloss→typed Horn support or proof replay. This further narrows broad novelty claims but is not a matched baseline.

Primary records: Phase218, Phase228, Phase229, Phase230, Phase231, and Phase232.

## 2026-10-08 runtime verification addendum (Phase233)

- **Core proof/NLI and resource verifiers:** 72 targeted tests passed across seven existing modules covering the Datalog checker, annotation compiler, strict proof/NLI pipeline, NLI gate, and OEWN hypernym path/certificate verifiers. Two stale compiler-version expectations (`/5`) were corrected to the current backward-compatible compiler v6 contract; compiler behavior was not changed.
- **Evidence ceiling:** these tests cover synthetic/unit scenarios only. They do not establish real gloss→rule fidelity, annotation quality, NLI efficacy/calibration on a target population, rights clearance, or paper-level novelty. Track A remains without authorized pairs, labels, predictions, or empirical effect estimates.
- **Next gate:** resolve the research contract for relation-edge, parent-surface, rendered-premise and statistical-unit identity before generating or migrating any Track A schema. The current certified NLI selector's one-row-per-`group_id` condition is a guardrail, not evidence that distinct groups are IID.

Primary record: Phase233 deep review.

## 2026-10-08 identity-interface addendum (Phase234)

- **Resource identity exists upstream:** the OEWN candidate inventory generates a deterministic release-bound `relation_edge_id` and enumerates child/parent lemma surfaces.
- **Cross-layer join remains absent:** claim-review `/0.1`, candidate manifest `/0.2`, NLI export `/0.2`, and the strict proof/NLI route do not carry that edge ID, parent-surface identity, or condition-renderer identity. Record `/0.1` also requires the raw source gloss hash to equal the premise hash.
- **Implementation gate:** this is a contract gap, not a defect in either local verifier. Track A schema migration remains contingent on a confirmed estimand, surface policy, condition labels, statistical unit, authorization, and rights review.

Primary records: Phase234 deep review, [field crosswalk](track_a_identity_field_crosswalk.md), and [machine audit](../sources/track_a_identity_field_crosswalk_2026-10-08_phase234.json).

## Baseline comparison rules to freeze before predictions

1. **Track A common-pair comparison:** direct gloss-conditioned NLI, a matched gloss-ablated prompt, and any adapted semantic/lexical baseline receive the same sense-linked `(raw gloss, directional hypothesis)` candidate file, split, examples, decoding/prompt budget, and evaluation labels. Resource-relative OEWN relations are reported separately and cannot be converted into NLI or semantic-support gold.
2. **Track B isolation:** all prover conditions receive identical adjudicated AST/rules, query and candidate facts; vary only the predeclared knowledge partition or prover strategy. Compare `source_only` to separately named resource-augmented conditions. A replay-valid certificate is not a source-support judgment.
3. **Track C end-to-end:** compare systems on the same gloss pool and bounded output/search budget. Report candidate/reference-set coverage, direction and formula match, semantic support, span support, proof replay, unknown/abstention and cost as separate outcomes. Pool-only recall is reference-set recall, not recall of every valid gloss formalization.
4. **No label leakage:** establish lemma-group/sense/source splits before training or prompt selection; additionally keep every exact raw-premise UTF-8 SHA-256 in one split across all resources/releases/senses. This exact-duplicate guard does not detect normalized or semantic near-duplicates. Tune only on dev; freeze model/prompt/parser/compiler/prover/retrieval revisions, outputs and hashes before exposing test gold. Human accepted alternatives must be fixed without seeing any system prediction.
5. **Denominators and uncertainty:** report eligible, returned, resolved, unresolved, uncertain/unassessed and abstained counts for every track. Resolved-only score is conditional on adjudication completion. Do not compare per-system macro values as paired outcomes if their empty/empty exclusions produce different denominators; include common-denominator exact match and micro, and define a fixed macro subset before comparison if needed. No population inference from unweighted descriptive scores.

## Freeze order and execution gates

| Order | Required decision/artifact | Must exist before | Current state |
|---:|---|---|---|
| 1 | Per-source rights/attribution determination and allowed distribution scope | Any external annotation or publication of source text | Not complete |
| 2 | Signed protocol: single-reference or multi-reference primary estimand, unresolved-item treatment, outcome hierarchy and uncertainty method | Any formal labels/model prediction | Draft only; choice not frozen |
| 3 | Claim-pair candidate manifest, canonical formula/hash convention, generation/de-duplication and group/sense/source/exact-premise-hash split lock | Label collection | Freezer and validator enforce exact-premise-hash split isolation; no actual project pair frame/hash |
| 4 | Two independent annotators, adjudicator, out-of-frame feasibility/time pilot, privacy and return procedure | Annotation launch | Personnel/authorization not recorded; no returns |
| 5 | Double annotation, blinded adjudication, span/source support and NLI gold, gold audit and IAA summary | Gold-backed metrics | No data |
| 6 | Baseline model/prompt/revision, budget and held-out test predictions locked before unblinding | Confirmatory evaluation | No results |
| 7 | Track-specific runs and independent replay; matched analysis with uncertainty | Any efficacy/novelty conclusion | No real matched evaluation |

The current project is therefore **structurally audited and prototype-capable, but not empirically validated**. The largest remaining gap is not another local bridge wiring check: it is authorized, independently adjudicated source evidence followed by the matched experiments above. This conclusion does not establish novelty or efficacy.

## Phase 140：400 项 blind batch 的轨道适配与启动门审计

只读审计确认：400 行任务输入只含 task_id/POS/lemmas/gloss；返回协议可记录语义节点、span、方向性 rule claim 与 source-support 标签，因此在冻结具体 schema/protocol 并完成裁决后，可作为 Track C 的人工参考资料。它不是 Track A claim-pair NLI frame；Track A 仍需独立的 sense-linked directional pair manifest。Track B 需要从 adjudicated records 构造固定 rules/facts/query 后单独执行。presentation audit 两个 400 行顺序通过 hash/seed 回放，answer key 未纳入，但 plan/manifest 均为 `draft_not_authorized_for_distribution`。当前 lock 没有 pin annotation protocol/schema hash；validator 支持 0.2–0.6 drafts，而协议把 v3 记为 0.4-draft。这是启动前需要作出的版本锁定，不是更改已有 batch 的理由。0 回传、未签协议/未授权状态不变。机器审计见[Phase 140](../sources/annotation_batch_fitness_audit_2026-10-08_phase140.json)，深度分析见报告。

## Phase 141：Track A pair 的目标上下文缺少冻结规则

当前 schema 把 NLI premise hash 与 raw gloss hash 等同，source/manifest 不含 lemma；pair hypothesis 模板尚未冻结，项目也没有实际 pair manifest。因而目标词义虽由 sense ID 绑定，却没有规定模型如何看到目标 lemma/POS，也未保证人审与模型获得完全相同上下文。推荐建立新版本的 lemma+POS+raw-gloss premise renderer，并保留 raw-gloss-only paired ablation；分别哈希原始 gloss 与渲染 premise。在这个输入定义被确认、schema/manifest 版本化之前，不应生成 Track A candidate frame。审计与版本 hash 见Phase 141。

## Phase 144：Track A 候选源的 POS/lemma 一致性 gate

对锁定 v3/400 批次与 OEWN 2025 Plus 固定 release 作逐 sense 对账：400 个 target sense 均在 release 中，raw gloss 仍为 400/400 精确匹配；但发现 1 个 POS 冲突、1 个目标 lemma set 不完整。故 v3 不应直接给未来 pair frame 提供 target POS/lemma context，即便可用它作为候选 sense ID 来源。新 frame 的目标上下文必须以 release sense record 为准，同时将 frame 元数据缺陷保留为历史记录，不能原位修补。

直接 hypernym 候选覆盖 310/400 target senses，共 322 条 edge、311 个 parent synset；172/311 parent synset 有多个 lemma surface。它们可用于 candidate-generation strata；其 label、正确 hypothesis surface 与 gloss 是否支持该关系仍未知。Track A 仍缺已冻结 premise renderer/hypothesis 模板、pair frame、授权标注/裁决标签、模型预测与分数。详情见[Phase 144 机器审计](../outputs/phase144/annotation_frame_release_identity_audit.json)与深度报告。

## Phase 145：hypothesis lexicalization 与分组规模

OEWN pinned release 的 322 条直接 hypernym edge 若按每个父 lemma 生成精确 hypothesis，共 680 行（多 358 行），且本候选池无重复 target-sense/surface-claim 组合。若只选一个 lexicographic surface，虽维持 322 行但不能称作语义 canonical。建议评估逐 surface 候选、edge 层级关联、逐 pair 独立 adjudication；如果按 edge 汇总，需先锁 estimand 和权重。草案泄漏闭包在当前身份键上形成 279 个连通组件、最大 26 行；渲染 premise 冻结后应重算 split feasibility 和层间平衡。现 manifest/0.2 缺 parent synset/resource edge provenance，应建立新版本并另绑 raw gloss、rendered premise、hypothesis 与 parent identity；旧版本不改。统计不产生语义 gold。证据见[Phase 145](../outputs/phase145/track_a_hypothesis_surface_policy_audit.json)和报告。

## Phase 146：上下文 premise 的跨组件迁移门槛

claim-review `/0.1` 强制 premise 与 raw gloss hash 相同，span 按 premise 坐标；strict NLI route 也把 NLI premise hash 绑定 source gloss input hash。新 renderer 必须独立绑定 source-gloss hash、rendered-premise hash 与 renderer version，并继续以 raw gloss 为 source-support span 坐标。现 manifest `/0.2` 无 parent synset/edge provenance。`group_id` 既是跨 split leakage key，也被 dev exporter/calibrator 当作单个独立校准行；多个 lemma surface / paired contexts 不能直接复用该字段。应在新版本中拆分 relation edge、split leakage component 和 statistical unit，并先设计 cluster-aware/edge aggregation calibration。现有三类旧 schema/export 不原地变更。机器证据和需要更新的消费者见[Phase 146](../sources/track_a_context_contract_audit_2026-10-08_phase146.json)与报告。

## Phase 147：Track A pair contract 决策草案

建立设计选项文档，拟以 lemma/POS/raw-gloss 条件为 primary、raw-gloss-only 为 ablation；所有 parent lemma surface 单独成候选；raw-gloss support 与条件内三分类 NLI gold 独立；relation-edge、leakage component、statistical unit 分列。规模上限为 1,360 pair-condition rows，双人标注需最多 2,720 个判断。现有 IID one-row-per-group calibrated gate 不能未经改造套用。所有模板、标签定义、surface scope、estimand 和校准单位仍是草案。见[设计选项](track_a_pair_contract_design_options.md)。


## Phase 161：复算环境状态（2026-10-08）

| 评测准备项 | 当前证据 | 状态边界 |
|---|---|---|
| 维护代码依赖 | 132 个 Python 文件 AST 扫描无解析错误；无非标准库且非本地顶层导入；Python 3.10+ 标准库政策 | 静态扫描，不覆盖动态导入/子进程依赖；本轮未运行测试或 CI |
| CI 版本矩阵 | 配置声明 Ubuntu 3.10–3.13、Windows 3.10/3.13 | 是已有工作流配置，不是本轮执行结果 |
| 冻结 bundle 可用性 | 配置的仓库外路径及 manifest 在当前机器存在 | 未重放 integrity lock；目录存在不等于 payload 匹配；仓库克隆不包含该数据 |

机器快照：[Phase161 环境审计](../sources/reproducibility_environment_audit_2026-10-08_phase161.json)；详细限制：Phase161 报告。

## Phase 181：环境快照入口可复跑（2026-10-08）

| 评测准备项 | 当前证据 | 状态边界 |
|---|---|---|
| 维护代码依赖 | `python -m src.analysis.audit_reproducibility_environment` 扫描 133 个 Python 文件，无 AST 错误或第三方顶层导入 | 静态扫描，不覆盖动态导入/subprocess，也不是 CI/测试结果 |
| CI 版本矩阵 | Ubuntu 3.10–3.13、Windows 3.10/3.13；workflow SHA 与结果一起记录 | 仅静态解析配置 |
| 外部 bundle | 配置的 sibling 路径与 manifest 存在；data-release inventory CLI 当前一致 | 本环境快照未重放 lock 或全量 source payload；release clearance 仍未通过 |

复算命令和限制见[持续开发说明 Phase181](reproducible_development.md#phase-181可复跑的环境数据路径快照)、深度报告与[机器快照](../sources/reproducibility_environment_audit_current.json)。


## Phase 162：冻结输入锁重放（2026-10-08）

| 评测输入 gate | 当前证据 | 未覆盖内容 |
|---|---|---|
| frozen bundle 锁定文件 | manifest fingerprint 与 6 个 required-file SHA-256 全部匹配，integrity verifier errors 为空 | 不遍历所有 source payload；不证明来源许可/真实性或 gloss 语义 |
| 当前执行范围 | 只读 integrity replay；无测试、CI、模型或 proof route | 不构成端到端评测或论文效果证据 |

详见[Phase162机器结果](../outputs/phase162/frozen_bundle_integrity_replay.json)和深度报告。


## Phase 163：来源输入完整性复算（2026-10-08）

| 评测前置项 | 当前结果 | 不能推出的结论 |
|---|---|---|
| 被 sense index 引用的来源 payload | 115,235/115,235 个 payload、18,734,636,389 bytes 均匹配冻结 checksums；重复/畸形记录为 0 | 不证明上游版本/许可/署名或 gloss/图规则语义正确 |
| 审计产物稳定性 | Phase163 聚合 JSON 与 Phase23 留存文件 SHA-256 完全一致 | 不构成模型表现、人工一致性或新颖性结果 |

详见[Phase163机器结果](../outputs/phase163/source_release_metadata_audit_current.json)和报告。


## Phase 164：相关工作对评测分轴的约束（2026-10-08）

| 评价轴 | 近期先例提示 | 项目所需独立证据 |
|---|---|---|
| formal proof validity | APOLLO 使用 Lean 检查/重验形式证明 | 对提供的形式对象有效，不推出 gloss→rule 忠实度 |
| verifier quality | Weaver 聚合弱 verifier；ICML 2026 工作训练 self-verification | 需要在人类裁决 gold 上单独校准，不视为 semantic oracle |
| specification/source fidelity | ICML 2026 formal problem-solving 区分形式构造和已知命题检查 | 本项目仍需 source gloss span 对 directional typed Horn literal 的人工支持 gold |
| rule validity vs. plausibility | MuSLR 控制形式规则；RULEBREAKERS 暴露形式规则与常识反应差异 | 逻辑蕴含、词义 entailment 和典型性分别标注 |

详见Phase164报告及[机器筛读日志](../sources/literature_screening_log_2026-10-08_icml2026_neurips2025_formal_verification.json)。

## Phase 165：ICLR 2026 autoformalization/verifier 证据边界（2026-10-08）

| 评价轴 | ICLR 2026 先例 | 对项目评测的约束 |
|---|---|---|
| natural-language formalization fidelity | Mathesis 用 LeanScorer 分解条件/结论并作 LLM-assisted semantic evaluation，另有 expert-labeled subset | 该类总体方法已有强先例；本项目若继续，需精确区分词典义项、词汇 relation、逐 span support 与 formal replay |
| proof dependency structure | DExploration 从 Lean proof 构建依赖 DAG 并做拓扑遍历 | 通用 DAG/topological traversal 不是足够新颖点；需报告 AND/OR semantics、witness criterion、source lineage 的独立贡献和匹配比较 |
| answer verification | SCI-Verifier 使用 expert-grounded answer equivalence 数据训练/评估 verifier | 专家答案等价 gold 与原始释义 source-support gold 是不同标注对象 |
| verifier generalization | Variation in Verification 发现生成器能力、题目难度与 verifier 能力交互 | 未来应在冻结的共同候选与 gold 上按难度/生成器分层报告；不能从通用 benchmark 外推 gloss semantic accuracy |

详见Phase165报告和[筛读日志](../sources/literature_screening_log_2026-10-08_iclr2026_formalization_verification.json)。

## Phase 166：WordNet/gloss 近邻对评测金标准的约束（2026-10-08）

| 新近任务先例 | 可迁移的设计信息 | 不能替代的项目证据 |
|---|---|---|
| Latin LKG context-based sense prediction with gloss and WordNet hypernyms | 对不同模型/graph context 条件作配对评估；注意上下文、资源链接覆盖与模型规模交互 | 不判断 gloss 是否蕴含关系，也没有逐 literal span 或 source-only proof gold |
| CEFR WordNet gloss alignment by LLM semantic similarity | sense-level gloss alignment 有先例；需把人工 direct alignment audit 和 downstream task metrics 分开 | 论文未人工 spot-check transfer labels；Macro-F1 不是直接 alignment correctness，不是 Horn rule entailment |
| Medical term-definition retrieval and multilingual WordNet resource curation | 定义检索/词网资源工程是邻接任务，可作 background | 不评 relation direction、AND/OR rule semantics、gloss-span support 或 proof certificates |

详情见Phase166报告、[筛读日志](../sources/literature_screening_log_2026-10-08_acl2026_wordnet_slice_phase166.json)和[更新后候选深度 snapshot](../sources/acl_anthology_candidates_2026-10-08_v6_reconciled_phase166.json)。

## Phase 167：AAAI 2026 formalization/logic pipeline 评测先例

| 评价轴 | 已有先例 | 本项目仍需的独立证据 |
|---|---|---|
| ontology vs. formula | 固定 signature/gloss 下 NL→FOL 转换与 SMT equivalence；connective/quantifier/negation perturbation | 分开测 lexical referent/type/ontology 选择、规则方向与 formula；controlled edit adaptation 尚未实现/验证 |
| selective translation / backward search | confidence-aware selective symbolic translation、LLM consistency check、hypothesis-driven backward reasoning | 人工裁决的逐 span source-support、严格 AND/OR Horn 语义及独立 witness replay |
| executable rule application | 法条生成 Prolog 并执行 SWI-Prolog；失败/超时可拒答 | 运行成功或下游答案正确不证明各 rule 忠于 gloss，也不等于 source-only provenance |
| specialized autoformalization | 数学知识+推理训练，BEq 与 prover benchmark | 不能迁移为 WordNet lexical semantic-support 性能 baseline |

证据和筛查边界见Phase167报告及[结构化日志](../sources/literature_screening_log_2026-10-08_aaai2026_formal_logic_neighbors.json)。

## Phase 183：正确性与下游效用分轴

| 评测准备项 | 近期先例约束 | 当前证据/缺口 |
|---|---|---|
| gloss-span semantic support | Quokka 的程序 verifier soundness 不判断自然语言来源是否支持输入断言 | 仍需 sense/release-bound raw-gloss-span→directional typed literal 人工裁决 gold；当前未有结果 |
| formal rule / certificate validity | 候选公式、类型和 replay 有独立的形式检验责任 | 形式验证只给定输入规则的后果，不证明 gloss fidelity；当前 route 结果不能替代人工支持标签 |
| downstream proof utility | 若评估，应固定 facts、queries、base prover，并报告相对 baseline 增量与 end-to-end cost、显式资源预算 | 未有本项目 matched utility experiment；Quokka benchmark/分数不迁移 |
| inconclusive/resource limit | verifier 的 unknown 必须与 proved/refuted 区分 | 现协议保留 `unknown` 与 `resource_limit`，继续按不确定/预算状态报告，不编为否定 gold |

详情见Phase183报告与[筛读日志](../sources/literature_screening_log_2026-10-08_colm2026_verifier_utility_quokka.json)。

## Phase 184：形式图输入现态复算

| 评测准备项 | 当前证据 | 推论边界 |
|---|---|---|
| 冻结 AND/OR 图重放 | integrity lock、manifest、closure、节点/超边对应及 110,425 条 witness 全部通过；与 Phase175 JSON 逐字节一致 | 支持当前固定正 Horn 图结构可复算；不支持 gloss 语义蕴含或 source fidelity |
| 最小深度 witness | 110,425/110,425 selected witness 达最小 grounded depth；depth slack=0 | 不等于最少 DAG edges、证据质量最优或全局最小 basis |
| basis 删除敏感度 | 精确 AND/OR closure 作为影响 oracle；同口径 selected-witness descendants 为 66 高估/19 相等/0 低估 | 只针对当前冻结表示和已验证 witness；不能被解读为语义重要性 |

详见Phase184报告及两个[机器产物](../outputs/phase184/frozen_hypergraph_current.json)、[最小 witness 产物](../outputs/phase184/minimum_witness_current.json)。

## Phase 192：NLI 内容效应关系切片

| 评价准备项 | 当前实现 | 结论边界 |
|---|---|---|
| unsupported NLI relations | 对 not-supported gold 分开切 neutral、contradiction、discordant entailment，并按 plausibility strata 报告计数、混淆矩阵与 FPR | 可避免 neutral/contradiction 的反向变化被合并率遮蔽；没有输入数据，故无实证结果 |
| 内容效应 gap | neutral 与 contradiction 各有 plausible−implausible FPR gap；合并 non-entailment gap 是辅助量，缺比较 cell 返回 null | 描述性指标，不计算区间/显著性，不做阈值选择、模型比较或因果解释 |
| 状态与隔离 | 仅 sidecar JSON API 原型，标注草案未签署/注册 | 无人工 gold、无真实预测、不接入 strict route；不得据原型声称 NLI 内容稳健性 |

详见Phase192报告与[NLI 评测草案](nli_content_effect_evaluation_draft.md)。

## Phase 193：诊断条件与指标分母隔离

| 指标 | 纳入范围 | 隔离约束 |
|---|---|---|
| plausibility strata 与 content-effect gaps | 仅 `diagnostic_condition == "plausibility_stratum"` | 不混入匹配合理性对或无关上下文对，避免不同 estimand 共用分母 |
| matched plausibility diagnostics | 仅 `matched_plausibility_pair` 的完整配对 | 只报告成对分数/决策/准确率差，不进入观察性分层 |
| irrelevant-context diagnostics | 仅 `irrelevant_context_pair` 的完整配对 | 只报告上下文成对变化，不进入 source-only content-effect gap |

Evaluator 版本为 `nli-content-effect-diagnostic/0.2`；split 总行数仍统计所有诊断条件。见Phase193报告。

## Phase 194：跨 split 泄漏检查

除连通分量 `group_id` 外，sidecar validator 现拒绝重复的 `source_sense_id`、`claim_id`、gloss/hypothesis/model-premise/context hash 跨 dev/test。该核验覆盖已编码的身份代理；lemma、改写族和 context-template 家族仍依赖上游正确归并到 `group_id`，不能由当前字段自动证实。见Phase194报告。

## Phase 195：leakage component builder 的能力边界

| 能力 | 当前状态 | 未覆盖内容 |
|---|---|---|
| 多种 opaque leakage key 的连通分量 | 新增确定性并查集 builder；输出每个 example 的 component group ID 和组件大小汇总 | 组件 ID 取决于整个分量成员集合，新增/删除成员会改变该 ID |
| 输入/输出可复算 | 输入文件 SHA、固定 JSON 序列化、排序后的成员与输出 SHA | 本轮未用输入样例做动态行为验证 |
| split 与推断设计 | 显式 `split_assignment_performed=false` | 未分配 split、未定义 split 比例/随机化政策或 statistical unit；不能据此训练、校准或做总体推断 |

实现命令与安全/复算说明见Phase195 深度报告和[开发复算说明](reproducible_development.md)。

## Phase 191：候选 frame/release 一致性敏感性

| 评测准备项 | 当前证据 | 结论边界 |
|---|---|---|
| POS cohort integrity | 1/400 POS mismatch target 未进入任何直接 hypernym edge；noun edge 与 parent-surface 数按 frame/release 分组都为 264/507 | 当前候选边级结果不受影响；不能据此宣称完整 frame 对所有 POS 关系均一致 |
| lemma surface integrity | 1/400 lemma-set mismatch 位于一条 noun edge；frame/release 分别产生 1,105/1,106 全表面组合；来源记录有两个 list variants | 对 all-surface 方案是小的 workload/estimand 敏感性；不判断哪一 variant 符合研究语义，也不改旧 frame |
| protocol consequence | 单 child surface/edge 的行数对列表大小不敏感；all child surfaces 的判断数会变化 | child lemma policy 仍须明确；情景数字不构成 protocol、power 或有效样本量 |

详见Phase191报告与[机器审计](../sources/oewn_candidate_identity_impact_audit_2026-10-08_phase191.json)。
## Phase 196：witness 表示紧凑性不是语义有效性

| 评价对象 | 本轮证据 | 仍缺少的证据 |
|---|---|---|
| witness DAG 结构 | 冻结图 integrity 与 selected/canonical 证书结构均通过；selected witness 均达最小 grounded depth | 外部来源/释义对每条规则的 support；sense/lexical claim 的正确性 |
| 证明表示规模 | DAG edge count 约 66 万；递归 proof-tree unfolding 中 99,144/110,425 根超过 10^12 次节点出现 | 运行时内存/延迟基准、任务效用、source-faithfulness 与人工可读性评估 |
| clause tie-break | 108,224/110,340 selected 最小深度根大于递归目标可达的最小展开树 | 受语义支持约束的紧凑性优化及独立验证；不能将树更小当作更正确 |

结果与统计定义见Phase196深度报告。

## Phase 197：minimum-depth compact witness 的形式成本基线

新增 clause 选择在最小深度约束内最小化递归 proof-tree occurrence 数，并生成结构校验通过的 witness certificate。相较当前 selected witness，根级 median/P90/max bit length 降低 3 bit、超过 10^12 次出现的根少 2,013 个，DAG dependency edges 增加 1,703 条。该结果支持把递归树规模作为可复算的结构成本维度；没有测量运行时/内存，也没有证明 compact witness 有更好的 source support。不要将该策略视为语义 baseline 或默认 witness。详细见Phase197报告。

## Phase 198：compact witness 的 source-index lineage

compact 与原 selected witness 共有完整的 index-level clause→source-document link 覆盖，且链接都具有 head 的 source-record 元数据及 checksums sidecar 条目。Payload bytes 未在此审计中读取或重新 hash；该结果不能证明 5,802 个不同 clause 的 payload 实际字节/身份仍匹配，更不能证明定义语义支持。比较仅支持“索引登记了来源路径”的结构性结论。详见Phase198报告。

## Phase 199：compact witness payload lineage 的当前字节验证

对 selected 与 compact witness source-document/head 关联集合并集重新读取并校验 17,588,076,573 bytes；两侧共 220,764 个关联的 checksum/byte count 和 synset identity 全部匹配，错误均为 0。它增强了 frozen-bundle byte/provenance integrity 证据；source payload 仍未经 gloss-span semantic-support 审定，许可与真实 sense/规则正确性仍是独立缺口。详细见Phase199报告。

## Phase 200：自动 WSD 分支重合仅作结构诊断

对 5,802 个 changed heads 重放 source logic branches 与 WSD synset-ID unions。Exact match 是 129 vs. 137，paired compact-only/selected-only 为 59/51；subset match 是 5,676 vs. 5,679，paired compact-only/selected-only 为 7/4。它们是自动 WSD/part-branch 的集合重合，不是 gloss entailment、human support gold 或 source faithfulness 的代理真值；这些事后小净差不能推出方法优劣。详见Phase200报告。

## Phase 201：自然语言/符号逻辑联合表示不等于来源忠实度

ACL 2026 的跨视图逻辑子空间工作在最终答案层面评测推理准确率；其作者指出中间推理步骤正确性/忠实度还需要细粒度评价。这强化了本项目的分层要求：形式查询正确、答案准确、每条形式规则被原始 gloss 支持、来源证书可独立重放应分别报告。该论文不提供词典释义 span support gold 或 matched lexical baseline。见Phase201报告。

## Phase 202：Track A gold 与 NLI pipeline 的接口缺口

| 层 | 当前组件 | 缺口 |
|---|---|---|
| 候选来源 | 固定 release OEWN direct-hypernym edge/surface inventory | 不含 gloss、模板、pair 条件或 split |
| 文本-free manifest | claim-review `/0.1`/`0.2` freezer/validator | 没有 `relation_edge_id`/parent surface，也没有 raw-gloss 与 rendered-premise 双哈希 |
| 人工返回 | 单义项 blind importer，canonical `/0.4`–`/0.7` draft | 不是 relation-edge×surface×condition task；不能输出独立 source-support/NLI gold |
| NLI export | 单精确 premise×hypothesis 的 claim-review export | 可复用哈希/校验设计，但输入单位和 gold join keys 尚未冻结 |

因此候选→盲标→裁决→NLI 对比没有已验证端到端路径。实现依赖研究者先锁定 edge/surface 单位、exact-condition NLI、POS/template 范围及统计/校准单位；详细接口证据见Phase202报告。

## Phase 203：trace coherence reward 不是 formal/source verifier

KCR (ACL 2026) 使用 embedding distribution 距离和 normalized edit similarity 评估生成 trace 与参考文本/候选的一致性；graph extraction 与 LLM answer judge 也使用 GPT-4o-mini。此类 process reward 不等价于 Horn derivability、source gloss span support 或独立证明回放。未来应分别报告生成轨迹质量、LLM-as-judge、人工 source-support gold 与 checker replay。见Phase203报告。

## Phase 204：假设已可证伪，研究效应仍无可用数据

H1–H3 的支持/反驳/不可判断框架已写入协议；当前限制是候选/统计合同未锁、无裁决 gold 和无共同基线运行。有限冻结包的结构重放、source payload 字节/identity 核验属于已支持的工程事实；它们不支持语义 fidelity、compactness 的语义收益或人审效用。逐项证据等级与下一步反驳读数见[Phase204交叉表](research_claim_evidence_crosswalk_2026-10-08_phase204.md)。


## 2026-10-08 current-state addendum (Phase215)

- **Minimum-depth source provenance:** Phase215 indexed 127,334 minimum-depth clause alternatives over 110,340 nonbasis heads. Every alternative has source-document links and source-record/checksum metadata. With the verified Phase199 selected/compact payload baseline plus 37 incremental payloads, all alternative source associations have checksum and identity verification coverage.
- **Single-witness coverage:** the union over all minimum-depth alternatives adds source-document associations for 49 heads beyond the current selected clause (54 head-document associations total). This is evidence about provenance coverage only; document count does not measure gloss support, rule correctness, license compatibility, or system quality.
- **Research readiness:** no human gloss-span source-support labels, matched baseline, or project effect estimate were added; H1–H3 remain unmeasured.

Primary record: Phase215 report, [machine record](../sources/minimum_depth_alternative_source_audit_2026-10-08_phase215.json), and [aggregate output](../outputs/phase215/minimum_depth_alternative_source_audit.json).


## 2026-10-08 current-state addendum (Phase216)

- **Replayable provenance artifact:** a deterministic 127,380-row hashed mapping now records every minimum-depth clause/source-document association alongside source payload digest and byte count. The independent replay CLI reconstructs all rows from the frozen graph, minimum-depth clauses, sense index, and checksum sidecar; exact row comparison passes.
- **Disclosure boundary:** the map omits plaintext IDs, paths, bodies, and glosses, but its deterministic hashes are pseudonyms and can be dictionary-matched when combined with the bundle. Keep it within controlled project data.
- **Evidence scope:** Phase216 replay checks structure and checksum metadata only; Phase215+199 provide payload byte/identity checks. Neither establishes gloss entailment, source license clearance, nor downstream effect. Gold and matched-baseline gaps remain.

Primary record: Phase216 report, [machine record](../sources/minimum_depth_alternative_source_map_2026-10-08_phase216.json), and [verification result](../outputs/phase216/minimum_depth_alternative_source_map_verification.json).
## Phase219：Track A v1 设计就绪度

| 评价层 | v1 提议 | 当前状态 |
|---|---|---|
| Resource relation | pinned-release direct noun-hypernym edge | 旧 inventory 可供 workload estimate；release-derived 新 frame 未建 |
| Source support | edge-level directional raw-gloss span labels | 设计已具体化；没有人工标签或裁决 gold |
| Exact-pair NLI | 同一 surface pair 的 lemma+POS+gloss 与 raw-gloss 条件 | paired estimand 已提议；renderer、surface scope、gold 与 split 未冻结 |
| Formal proof | 固定签名/类型/规则下独立 replay | 现有 route 不兼容渲染 premise 与 edge/surface 身份，需新版本合同 |
| Calibration/risk | cluster-valid threshold/risk procedure | 没有验证过的方案；先限描述性阈值无关结果 |

Phase219 文档是研究设计草案，不是注册协议或执行许可；不得把工作量、结构 replay 或文献先例表述成效果证据。见[Track A v1](track_a_protocol_v1_draft.md)及深度报告。
## Phase267 相关工作导致的评测边界更新（2026-10-08）

| 命题/终点 | 最新边界 | 当前项目证据 |
|---|---|---|
| 类型检查/形式可证可证明语义忠实 | 不成立为一般保证；BPF/DriftBench 已直接构造并评测 typeable/provable 但语义漂移的数学形式化 | 本项目有 frozen witness/Horn proof replay，但没有 gloss-source support gold |
| 对比性 drift probe 与 controlled NL/formal benchmark 的宽泛新颖性 | 已有 workshop-attributed 方法先例；不能单独主张首创 | 是否可适配 gloss 现象、是否改善识别需独立设计和匹配实验 |
| 释义 span→有类型、带方向 Horn literal 的来源支持 | BPF 不评估此任务；仍是项目可检验的窄差异假设 | 无人工双标/裁决 gold，不能报告精度或新颖性 |
| BPF-style probe score / theorem oracle | 输入 probe label 与 prover completeness 假设必须显式报告；不能当 source semantics oracle | 现有正 Datalog verifier 只验证给定规则系统中的结论，不可替代 source-support 标注 |

细节见Phase267 深度报告及[筛读日志](../sources/literature_screening_log_2026-10-08_faithfulness_gap_driftbench_phase267.json)。

## Phase268 Track A 实现合同复核（2026-10-08）

当前 claim-review `/0.1` 校验器要求 `source.gloss_sha256` 与精确 `premise` 哈希相同，且把 evidence span 按 premise 坐标验证；记录又把 `semantic_support` 和 exact-pair `nli_relation_gold` 放在同一行、单一 `annotation` provenance 下。该合同不能表达 lemma/POS+gloss rendered premise 与 raw-gloss source span 的分离，也没有 Track A 所需的 relation-edge/surface/condition 外键、独立双面板轨迹或分离的 leakage component/PSU/statistical unit。旧哈希/validator 模式与 source-only 证明路由可作为工程先例，但现有 NLI exporter 不是 Track A evaluator。**尚不实施 schema 改造**：先裁决研究总体、surface/POS、estimand、面板和统计单位并完成许可/责任人 gate，再做向后兼容的新版本。见Phase268 报告、[机器审计](../sources/track_a_contract_compatibility_audit_2026-10-08_phase268.json)及[Track A v1 草案](track_a_protocol_v1_draft.md)。

## Phase269 内容效应相关工作全文章节升级（2026-10-08）

| 评测问题 | 当前证据边界 | 对项目的操作含义 |
|---|---|---|
| 逻辑有效性受现实 plausibility 影响 | Findings ACL 2026 全文报告 ten taxonomic triples 上的 syllogism content-effect、validity/plausibility activation alignment 及 steering 干预；不是 WordNet gloss 任务，也未做 lexical-triple holdout | 可作为独立 plausibility/content-effect diagnostic 的方法先例；不能从中推断本项目存在该偏差 |
| Hypernym label 是否等于 gloss-source support | 该论文 hypernymy 是复用十组词汇 triples 的 auxiliary representation control，无 gloss-span semantic annotation | 将 resource relation、exact-pair NLI、plausibility 与 raw-gloss source-support gold 分开保存和报告 |

全文方法、结果和边界见Phase269 报告、[结构化筛读日志](../sources/literature_screening_log_2026-10-08_validity_plausibility_fulltext_phase269.json)与[机器审计](../sources/phase269_validity_plausibility_fulltext_audit_2026-10-08.json)。
