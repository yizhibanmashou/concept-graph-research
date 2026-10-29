# 核心研究主张—证据交叉表（2026-10-08，Phase204）

本表把当前可核查的结构结果、待测研究假设和缺失的实验材料分开。它不是成果总结或预注册。状态依据当前项目中的机器记录、Phase153 设计备忘录与 Phase200–203 报告。

| 核心主张 | 当前状态 | 已有证据 | 仍缺证据 | 可反驳/下一步观测 |
|---|---|---|---|---|
| 冻结 bundle 的 AND/OR Horn 闭包与 witness certificate 可结构性复算 | **有限 snapshot 内已支持** | Phase184 结构 replay；Phase199 payload hash/identity replay | gloss 语义、义项映射、许可及新规则泛化 | 任一新 snapshot 重放失败即不成立；只对指定冻结快照陈述 |
| compact witness 来源 payload 与字节/义项身份一致 | **有限 snapshot 内已支持** | selected/compact source association 的 checksum、byte count、synset identity 核验 | gloss span 支持、规则方向/逻辑完整性、许可 | payload hash/长度/identity mismatch 会反驳结构 lineage |
| compact witness 提升释义来源忠实度 | **未验证假设** | Phase200 自动 WSD ID / DNF branch 重合仅为事后描述指标 | 人工 gloss-support gold、预注册比较与不确定性区间 | 用同一 changed-head 样本做盲化、裁决 span/clause 支持配对比较；不得把 WSD overlap 当语义真值 |
| source-only 规则和 witness replay 能忠实推出 gloss 蕴含的词汇结论（H1） | **未验证假设** | 类型化 Horn/proof 组件与来源字节链路可复用 | 双人裁决 gloss-span gold、matched end-to-end run | 锁定 test 上报告错误接受、方向错误、coverage、source-only replay；未达预注册风险/覆盖判据则削弱或否定 H1 |
| Track A NLI / candidate verification 有效 | **尚未测量** | 通用 claim-review 冻结器、validator、NLI exporter/evaluator 存在 | Track A edge/surface/condition frame、NLI gold、模型分数、外部 candidate-manifest lock | 对裁决过的精确 premise-condition 配对做锁定 split 上的匹配评测 |
| 保留 AND/OR 比压平更保留公式/来源语义（H2） | **未验证假设** | 协议已有方向反转、AND↔OR、删限定挑战 | 共同人工公式/来源支持 gold 与系统对照运行 | 同 claims 上配对比较；若只提高形式 replay 而不提高公式/来源支持，撤回语义收益表述 |
| 证据展示和 proof replay 改善人工错误定位/审计（H3） | **未验证假设** | 协议已规定盲化人审和效率/错误归因结果 | reviewer 分配/界面、耗时和错误标注实测 | 随机化盲审对照；仅 verifier 通过不能支持人审效用主张 |
| 通用图路径/trace reward/text+graph reasoning 是本项目新贡献 | **宽泛表述已被先例排除** | AND/OR evidence trees、proof DAG/graph traces、ACL 2026 KCR 已有相邻方法 | 有匹配实验支持的更窄 lexical source-support 增量 | 不作宽泛主张；窄主张仍需跨 venue 系统检索和共同 gold matched evaluation |

## 协议现有的可证伪性与当前缺口

H1–H3 已分别写有支持结果、削弱/否定结果和不可判断情形。因此当前首要缺口不是“没有任何可证伪标准”，而是它们尚未落成可启动的统计与数据合同：primary estimand、surface/edge 汇总、双条件 NLI gold、统计/校准单位、样本量/精度与锁定效应阈值还未裁决；当前又无授权的双标 gold 或候选预测。

Phase202 的实现互操作审计进一步表明，现有 OEWN inventory、claim-review `/0.1` sidecar/manifest `/0.2` 与单义项 blind importer 不能直接构成 edge×surface×condition Track A 通路。故“工程验证器存在”并不等于“Track A 可直接跑”，也不能由它推导 H1–H3 的效果。协议在统计主比较或新增 schema freeze 前仍须修订并独立锁定；旧 schema 和已锁 batch 不得静默改写。

## 使用边界

本表不修改 H1–H3、不替研究者选 estimand、不启动 pair/gold/split，也不作论文新颖性或效果结论。具体启动条件见[Track A 设计裁决备忘录](track_a_design_decision_memo.md)、Phase202 互操作性审计与Phase203 相关工作筛读。

Phase205 再沿 source-only proof/NLI strict route 追踪发现，现 route 还把测试 premise hash 当作 raw-gloss source hash，并把 proof query 限定为 `wn_sense:<sense_id>`。因此 rendered lemma+POS+gloss 条件及 edge/surface 级 relation identity 无法由现合同完整表达。编译器和证明回放器可以复用，但它们目前服务于经人工裁决的单义项 annotation claims；只有 hash/证书工程能力，不构成 Track A 端到端实现或 source-support gold。详见Phase205源码兼容审计。


## 后续现态补记（Phase205、213–214）

本节保留 Phase204 交叉表的历史定位，并将之后的现态证据并列补充，不回填或重解释原表结论。

- **结构复算**：Phase213 在当前 pinned bundle 重跑 frozen hypergraph 与 minimum witness，两个输出均与 Phase206 字节级一致；85 次 basis deletion 中，selected-witness descendants 对精确非 seed AND/OR closure loss 高估 66 次、相等 19 次、低估 0 次。可支持固定快照上的结构复算，不支持自然语言语义或 compact witness 语义收益。
- **H1 / Track A 可执行性**：Phase205 与 Phase214 的源码哈希对照确认 strict route 仍把 raw gloss 和 premise hash 视作同一身份，并缺 relation-edge、parent sense/surface 及 edge-level gold 键。故 Track A 仍没有可直接执行的端到端 gold 路线；H1 仍未验证。
- **NLI 风险控制**：Phase214 核对了 fixed-grid exact-binomial/Bonferroni 的实现与文档。其名义有限样本保证依赖 IID 校准单位、模型和阈值网格冻结、目标分布稳定。当前 group ID 规则不能证明独立性；因此它不为拟议的 edge/surface 多行 frame 提供现成保证。
- **模型 provenance**：现有导出摘要及外部 manifest pin 可复算分数文件、输入 hash 和调用方声明的 `model_id/revision`，没有独立的推理执行版本 attestation。若将来对外声称冻结模型评测，须补充可审计的服务端/本地运行来源记录或相应限制说明。

机器与源码证据见[Phase213](../sources/frozen_graph_witness_replay_2026-10-08_phase213.json)、[Phase205](../sources/track_a_proof_route_compatibility_audit_2026-10-08_phase205.json)及[Phase214](../sources/nli_proof_route_contract_review_2026-10-08_phase214.json)。H1–H3 均无人工 gold、matched baseline 或项目结果，状态维持未验证/尚未测量。


## 后续现态补记（Phase215）

Phase215 将来源追踪从 selected/compact witness 扩展到所有同深度 clause alternatives。110,340 个非 basis heads 共 127,334 条最小深度替代 clause；全部具有 source-document links，并且 source-record/checksum 元数据覆盖。复用哈希一致的 Phase199 selected/compact payload 审计，再增量检查 37 个未覆盖 payload 后，所有替代来源关联均具 checksum 和 synset identity 核验依据。全部替代来源文档并集在 49 个 head 上超过单条 selected clause，增加 54 个 head-document 关联。这个审计填补 provenance coverage 记录空缺，但不回答来源 gloss 是否支持 clause，也不验证许可或系统效果；交叉表中语义 gold 与 matched evaluation 的缺项不变。详见Phase215报告与[机器记录](../sources/minimum_depth_alternative_source_audit_2026-10-08_phase215.json)。


## 后续现态补记（Phase216）

新增逐条确定性 hash 映射保存全部 127,380 个最小深度 clause/source-document 关联及 checksum sidecar 的 payload digest/byte count。独立 verifier 从冻结 graph、最小深度规则、sense index 和 checksum sidecar 重建并逐行完全匹配。该工件让 provenance 关联可审查、可重放，且不写出明文路径、义项 ID、规则 body 或 gloss；哈希不构成匿名化。映射重放与 Phase215/199 payload bytes/identity 验证共同增强数据链路自洽性，但仍不能回答 gloss 是否支持规则，也不构成许可清权或 matched effect。参见Phase216报告和[机器记录](../sources/minimum_depth_alternative_source_map_2026-10-08_phase216.json)。

## 当前状态增补（Phase266–271，2026-10-08）

本节更新证据状态，不改写 Phase204 的历史主张，也不把相关工作筛读计作本项目实验结果。

| 主张/能力 | 当前判定 | 最新直接证据 | 仍缺/解释边界 |
|---|---|---|---|
| 固定冻结超图上的所选 AND/OR witness 和 ground Datalog proof 可重放 | **有限 snapshot 内已支持** | Phase266：3,596 nodes、14,923 edges、3,512 rules；结构证书与 bridge replay valid、0 errors，与 Phase148 报告逐字节一致；锁定 v3 preflight 21/21 通过 | 不证明所有源释义支持规则，不证明替代 witness 语义等价、WSD 正确、开放世界蕴含、许可或新方法效果；本轮没有重读全部 payload |
| Typed Datalog/strict proof route 已验证为 WordNet 词汇类型与 source semantics | **不成立** | Phase68–72 是调用方声明 type table 下的有限 checker/pipeline 和合成行为验证；Phase268 确认 Track A identity/condition 仍与 legacy sidecar 不兼容 | 无经权威词汇来源裁决的 type inventory、source-support gold 和真实 edge/surface/condition end-to-end route |
| Track A NLI / relation verification 已可端到端执行 | **尚未实现为 Track A 合同** | `/0.1` 把 `source.gloss_sha256`、`premise_sha256` 绑定同一文本，span 使用 premise 坐标；缺 relation-edge/surface/condition 与独立 panel provenance | 不得将 legacy exporter 的候选级 NLI 输出描述为 Track A 结果；需先冻结研究设计与权利/责任 gate，再做新增 versioned schema |
| project gloss-span source-support gold、IAA 或方法实证 | **没有证据** | Phase266 v3 preflight 仍为 400 项/24 strata、0 回传；协议未签署、未授权外部分发 | 没有双标裁决 labels、IAA、NLI gold/predictions 或 matched baseline；H1–H3 继续是未验证假设 |
| 一般“proof validity 不保证 NL/formal fidelity”或 contrastive drift probes 是项目新贡献 | **宽泛 novelty claim 排除** | Phase267 全文审读 BPF/DriftBench（workshop-attributed arXiv v1；实验未复现） | 具体 gloss-span→typed directional Horn support 的任务差异尚未证明新颖或有效 |
| plausibility/content effect 是本项目已证模型缺陷 | **未测量** | Phase269 全文的 syllogism validity/plausibility 分析为独立诊断近邻，使用十组 taxonomy triples；不是 gloss gold，也不是词汇 holdout | 不可外推到本项目；如将来测试须有独立标签、样本、分母和预注册诊断 |
| AAAI 2027 匿名稿件成果归属用户 | **明确否定** | 用户说明该稿非其成果；定位文档只将其作为内部 prior-work comparison | 任何公开写作都须准确处理稿件作者、状态、权限与既有研究边界 |

审计入口：[Phase266 现态记录](../sources/phase266_current_state_audit_2026-10-08.json)、[Phase268 兼容记录](../sources/track_a_contract_compatibility_audit_2026-10-08_phase268.json)、[Phase269 文献记录](../sources/phase269_validity_plausibility_fulltext_audit_2026-10-08.json)、[Phase271 bridge 复算](../sources/phase271_bridge_replay_audit_2026-10-08.json)、[当前就绪度总览](research_readiness_audit.md#当前总览-phase266271)。
### Phase270 增补：proof replay 与 proof quality

| Claim | Evidence now | Supported wording | Still unverified |
|---|---|---|---|
| 结构化 witness 可作为形式推导证据 | 指定 witness/Datalog 路径可重放（历史 Phase266）；ProofRank 将正确性作为其质量比较的前置条件，并另测可用性 proxy。 | “在给定形式前提和当前 checker 下，该 witness 可重放/结构可检查。” | raw gloss 是否支持规则、读者是否理解/采纳证据链、效用是否提升、可读性或数学意义上的 proof quality。 |
| 项目证据链具可用性或高质量 | 无项目人评/下游效用实验；ProofRank 是数学竞赛任务的构念邻居，不是 lexical matched baseline。 | 暂不声称可用性或高质量；把结构量、source support、NLI 与效用作为独立终点。 | 目标读者、任务、评分维度、盲评方案、IAA/裁决及 matched baseline 均未冻结/执行。 |

ProofRank 的 venue 标签存在未解记录差异（NeurIPS 2026 官方目录/海报页列题；arXiv v2 评论标注 ICML AI for Math workshop 接收），因此未把它登记为已确认的 NeurIPS 主会论文。见Phase270 报告和[筛读日志](../sources/literature_screening_log_2026-10-08_proofrank_phase270.json)。

## 后续现态补记（Phase272）

Phase272 在独立输出目录再次运行完整冻结图与最小深度 witness 审计；两份输出各自与 Phase213 字节一致。当前 fixed bundle 的 integrity lock、AND/OR closure、全部 witness 和最小深度证书均通过。可支持的表述仍限定为“固定 positive-Horn bundle 的结构证书在当前维护状态可重复计算”。selected-witness descendants 在 85 个 basis deletion 中有 66 次高估精确非 seed closure loss、19 次相等、0 次低估，精确 deletion 仍应重算完整 AND/OR closure。此次未全量重读 source payload，也没有 gloss-span support gold、NLI、模型效果、许可或新颖性证据。见[Phase272 报告](../../report/research_progress_deep_review_2026-10-12_phase278.md)、[机器记录](../sources/frozen_graph_witness_replay_2026-10-08_phase272.json)和[Phase272 输出](../outputs/phase272/)。

| Claim | Evidence now | Supported wording | Still unverified |
|---|---|---|---|
| 当前维护态可重放冻结 AND/OR 图和 minimum-depth witness 证书 | Phase272 在新目录重跑，两份 JSON 与 Phase213 逐字节一致；lock、closure、witness 和 certificates 均通过。 | “在指定冻结 bundle 与当前脚本/runtime 上，结构审计和证书输出可复算。” | gloss 对 literal 的支持、正确 WSD、外部蕴含、许可、Track A gold、NLI/方法效果。 |
| selected witness descendants 可精确表示删 basis 后损失 | Phase272 对 85 个 basis deletion 完整重算 closure；descendant count 66 次高估、19 次相等。 | 不应以 witness descendants 代替 exact AND/OR deletion closure。 | 对未列出的动态图变化或其他 closure 语义的普遍性；本轮未建立语义层判断。 |

### Phase271 增补：桥接复算不等于词汇语义验证

| Claim | Evidence now | Supported wording | Still unverified |
|---|---|---|---|
| OEWN resource path can be bound to a gloss candidate through the current bridge implementation | Validator 0.3 checks sidecar/manifest/bridge identities, exact query-row binding, producer/replay hashes and pinned-release fingerprints; synthetic end-to-end replay passes twice byte-for-byte; bad pin, missing candidate, and a mismatched query triple with matching report pins fail closed. | “本地 synthetic fixture 的 producer→independent replay→bridge contracts can be reproduced on the pinned release.” | Human genus mapping accuracy, raw-gloss support, actual Track A pair behavior, NLI/source-support labels, model effect or generalization. |
| 当前已有获准的 Track A 语义 gold | v3 preflight passes structural/hash checks but has 0 returns, `protocol_signed=false`, no external registration and `distribution_authorized=false`. | “输入 lock 完整；研究和分发 gate 未通过。” | 人工标注/裁决、IAA、许可证/责任审核、Track A-specific contract and authorized distribution. |

合成复算产物和逐项状态见Phase271 报告、[机器审计](../sources/phase271_bridge_replay_audit_2026-10-08.json)及[Phase271 outputs](../outputs/phase271/)。

## 后续现态补记（Phase273：既有 APF 记录补充）

| Claim | Evidence now | Supported wording | Still unverified |
|---|---|---|---|
| 从自然语言需求形成可执行形式模型、再看下游执行表现，是项目可单独主张的新颖组合 | 既有 2026-10-06 ACL 筛读日志已将 APF 作为邻接先例并定向审读 §3–4；Phase273 仅补充排名人工核对细节并纠正 2026-10-05 快照状态。 | 将“首次 NL→executable formalization / 外部质量评估”排除为宽泛主张；把任务贡献限定于带 release/sense 的释义语义支持与可重放规则证据。Phase273 不新增唯一论文。 | APF 不评估 WordNet sense、raw-gloss spans、typed Horn/AND-OR 或 source-bound witness；窄任务是否新颖仍需跨库系统检索和共同 gold/matched baseline，当前没有其证据。 |
| APF 提供项目的 semantic source-support gold 或同任务 NLI baseline | 其 reference ranking 主要由 LLM 生成，仅有 30×15 的小规模 human ranking judge check；领域为高成本天线优化。 | 可用作 NL→executable engineering formalization 的跨领域 prior art；不移植其分数，不称其人评为逐公式/source-span gold。 | 词汇定义、释义 span、关系方向、自然语言 premise NLI、来源类型和证书 replay 的共同任务评估。 |

证据见[既有 2026-10-06 筛读日志](../sources/literature_screening_log_2026-10-06_acl_formalization_2026.json)、Phase273 深度报告和[补充机器筛读日志](../sources/literature_screening_log_2026-10-08_apf_findings_acl2026_phase273.json)。

## 后续现态补记（Phase275：Phase1 网络指标主张）

| Claim | Evidence now | Supported wording | Still unverified / withdrawn |
|---|---|---|---|
| 85 个 basis 可覆盖锁定包的所有 heads | Phase272 复算 `basis_closure_complete=true`，85 seeds 闭包含 110,425/110,425 heads，所有 witness 结构有效。 | “在指定正 Horn 包和 basis 下，所有 head 都有结构 derivation/witness。” | 自然语言定义语义充分、全局最小 basis、gloss fidelity。 |
| 约 63% 节点深度超过 300 | Phase272 复算 69,052/110,425 selected/minimum witnesses 深度≥301（62.53%），最大396；全部 head 均与 minimum depth 相同。 | “约62.5%的固定图 head 的最小 grounded witness 深度至少为301。” | 语义难度、真实人类推理长度、释义嵌套；旧 max=399 不沿用。 |
| 49,435 个循环表示自然语言相互定义 | 旧 JSON 有计数和10个样例，但检测器/循环单位/去重规则未保存；Phase275 无法复算。 | 不作为论文发现；待恢复算法后再作结构复核。 | 计数可复现性和任何自然语言语义解释。 |
| 图具有幂律或小世界性质 | Phase1 幂律来自分箱频数的 log-log 线性回归；其聚类值来自无向投影且无匹配 null/path-length 对照。外部 Doubao HTML 声称做三种 null model，但代码、所引用 TSV/JSONL 和重复结果在当前工作区缺失，未能独立核验。 | 旧投影统计与 HTML 声称都不能作为本项目已复现的幂律/小世界结果。 | 适当尾部分布比较、超图/投影的可复算 null model、随机种子/重复数、路径判据和语义解释。 |

逐项分析见[Phase275 深度报告](../../report/research_progress_deep_review_2026-10-12_phase278.md)；结构复算的权威现态输出见[Phase272 frozen hypergraph](../outputs/phase272/frozen_hypergraph_current.json)和[minimum witness](../outputs/phase272/minimum_witness_current.json)。
