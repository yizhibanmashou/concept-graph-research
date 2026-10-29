# 相关工作检索与筛选记录

### Phase 228：coherent system 与 fault-tree 的联合重要度先例

定向查询 joint reliability/failure importance、fault-tree gate events、minimal cut sets、joint structural importance 和 total-order interaction。筛选出 JRI/JFI 的多组件推广、故障树 gate-event JRI、总阶可靠性重要度、经典 fault-tree/minimal-cut importance，以及 2026 joint structural importance。出版商搜索结果提供摘要/元数据；ScienceDirect 直接打开返回 403，因此不声称全文筛读或公式级比较。主要方法结论是 pairwise/multi-component interaction 已有可靠性工程先例；Phase227 确定性 all-head Horn closure loss 与概率敏感度类 JRI/JFI 不可直接等同。完整查询、身份和边界记录见Phase228深度报告与[机器筛读日志](../sources/literature_screening_log_2026-10-08_reliability_interactions_phase228.json)。

### Phase 180：EMNLP 2026 accepted-paper 可用性复核

官方 accepted-main-papers 页面可访问，但本次抓取只显示标题和页脚，没有论文条目；EMNLP 官方主页仍将会议日期列为 2026-10-24 至 10-29。针对 ACL Anthology 2026 EMNLP volume 的 WordNet/gloss/definition/entailment/logic/hypernym 查询也未取得可核对的相关论文记录。**这只能说明本轮未得到可筛的 paper-level records，不能据此断言会场没有相关工作。**将 EMNLP 2026 coverage 继续标为 pending，待正式论文题录或 proceedings 可用后重筛。详见Phase180报告与[结构化状态日志](../sources/literature_screening_log_2026-10-08_emnlp2026_availability_refresh.json)。

### Phase 166：ACL v6 2026 WordNet/gloss 检索族深筛补录

在冻结 v6 reconciled candidate frame 内，过滤 2026 年 `wordnet_gloss_lexical_relations` 家族的九条记录。初始逐篇账本显示五篇已 full-text、四篇仅 metadata/abstract；本轮对剩余四条逐条核对，其中两条（sense-prediction 与 CEFR gloss alignment）查官方 PDF 相关章节，另两条（definition retrieval 与 Konkani WordNet resource）仅核官方 Anthology title/abstract。新增独立结构化日志，随后对同一 v6 frame 执行非覆盖式 exact-URL reconciliation，保持原始 v6 输入不变。该切片的最新深度分布为 5 full-text / 2 targeted-sections / 2 abstract-only，不代表所有 ACL 2026 或全 ACL 已完备。见Phase166报告、[结构化日志](../sources/literature_screening_log_2026-10-08_acl2026_wordnet_slice_phase166.json)和[新 reconciliation](../sources/acl_anthology_candidates_2026-10-08_v6_reconciled_phase166.json)。

### Phase 165：ICLR 2026 autoformalization / proof DAG / verifier 定向补筛

在 ICLR 2026 官方主会论文集按 autoformalization semantic evaluation、proof dependency graph/DAG、expert verifier benchmark、generator/verifier capability 等词组检索。选取 *Mathesis*、*Let's Explore Step by Step*、*SCI-Verifier*、*Variation in Verification* 四篇，均检查官方论文 PDF 中与任务定义、方法/评估及局限相关的章节；不是 proceedings 全量题名/摘要 census。核对重点与逐篇结论、官方链接、检索词和筛读限制见Phase165报告及[结构化筛读日志](../sources/literature_screening_log_2026-10-08_iclr2026_formalization_verification.json)。

### Phase 164：ICML 2026/PMLR 306 与 NeurIPS 2025 补筛

日期：2026-10-08。检索官方来源：NeurIPS 2025 Volume 38 main-conference proceedings 与 PMLR ICML 2026 Volume 306；PMLR ICML 2025 Volume 267 用于规则/常识近邻。使用的标题/摘要查询族为：`formal reasoning logic`、`proof verifier formalization LLM`、`knowledge graph reasoning symbolic`、`logical reasoning LLM benchmark`；NeurIPS 2025 另查 `formal reasoning verifier symbolic logic language model`。

对新命中先与已有 project logs 去重，再按官方元数据/摘要筛题名候选。APOLLO、Weaver 定向核读官方全文相关章节；MuSLR 只读官方摘要（PDF 下载超过当前检索工具可读大小）；ICML 2026 三篇（含 *Editable Proof Sketch*）和 ICML 2025 RULEBREAKERS 均为官方摘要级；合计 7 篇，2 篇定向全文、5 篇摘要级。已有 On Learning Verifiers、Deliberation on Priors 与 KG-RAG dataset audit 不重复计入本轮。APOLLO proceedings 元数据与所连 PDF 标题页第三作者姓名不同，日志保留冲突。

本轮未构成 NeurIPS/ICML proceedings 全量 title/abstract census，不提供稳定候选总数或召回率估计；也不是完整系统综述。逐篇筛读深度和局限见Phase164报告及[结构化日志](../sources/literature_screening_log_2026-10-08_icml2026_neurips2025_formal_verification.json)。

### Phase 159：形式正确性、verifier 监督与 syllogism content effect

对官方 ACL Anthology 进行定向检索，核读 ACL Industry Track 的 T²、Findings ACL 的 FoVer 与 SemEval Task 11 论文中任务、评测和限制部分。精确范围及每篇边界见[结构化日志](../sources/literature_screening_log_2026-10-08_formal_correctness_nli_addendum.json)与Phase 159 报告。这是三篇、单审阅者定向筛查，属于固定 ACL 候选框之外的发现，不改冻结候选数、不估计 recall，不是跨会场系统综述。结论只扩展 formal validity、downstream behavior 与 source semantic fidelity 的分轴设计；不提供 WordNet gloss→typed Horn matched baseline 或项目效果证据。

### Phase 154：分层 conformal risk control 与 NLI 校准假设

针对 Phase153 的 IID/calibration-unit 缺口，定向核读 Salem et al. 的 [HG-CRC](https://arxiv.org/abs/2607.24562) 官方 arXiv v1/PDF，并与 `nli_gate.py`、claim-review exporter 和 strict route 逐项对照。它是新近 LLM selective-risk-control 预印本（arXiv 未列接收会议），提出按 group hierarchy 同时控制 selective risk；严格 split 变体假设 IID calibration rows 与 independent test point。group membership hierarchy 不等于 correlated surface clusters，不能直接移作 Track A calibration 修正。范围、定理假设、结果限制及代码接口发现见Phase154报告和[结构化日志](../sources/literature_screening_log_2026-10-08_hierarchical_group_risk_control.json)。单论文定向全文筛读，不是 conformal literature systematic review；未运行实现或代码。

### Phase 151：COLM 2026 grounded logic 与 judge 可靠性扩展筛读

对 COLM 2026 官方接收目录按 knowledge graph/evidence/logic/verification/claim/grounding/fact-check/RAG 主题做定向标题检索；全文核读 No Free Labels 与 LogicIF，摘要筛读 GraphWalker 与 GDP-RAG。逐项范围和证据见[结构化日志](../sources/literature_screening_log_2026-10-08_colm2026_grounded_logic_addendum.json)及Phase 151 报告。这是两篇全文加两篇摘要的单审阅者选择性筛查，不是 COLM 全目录系统综述或 recall 估计。新增结论：LLM correctness judge 要有独立人工 gold 与正确参考校验；可执行程序 oracle 与人审自然语言 fidelity 已有先例，但不能替代真实 WordNet gloss source-span semantics。GraphWalker/GDP-RAG 为邻接系统论文，不列 matched lexical baselines。未改 ACL 候选框、未跑项目代码或测试。

### Phase 150：COLM 2026 Q-CARE 定向全文筛读

官方 COLM 2026 接收目录发现 Q-CARE，核读其 claim decomposition、claim–chunk alignment、人类标注协议和 repeated-run stability analysis。结构化记录见[机器日志](../sources/literature_screening_log_2026-10-08_colm2026_qcare_fulltext.json)，综合判断见Phase 150 报告。该项为单论文、单审阅者跨会场定向筛读，不是 COLM proceedings 全量筛查或系统综述。它将通用 claim-to-evidence evaluation 从宽泛新意收窄；RAG chunk support 不等价于 WordNet gloss span→typed rule support，LLM judge 也不等价于 proof certificate replay。未修改 ACL v3 候选框、未运行项目代码/测试或 matched baseline。

## 2026-10-07 Phase 91：ACL Anthology 全局日志匹配状态

在 1,747 条固定 v3 候选框上重算所有 90 个结构化筛读日志的精确 URL join：1,286 条至少有一条日志记录，461 条仍无全局匹配。显式深度计数为全文 75、定向章节 134、摘要/元数据 851、匹配但深度未明 226。461 条未匹配项全部属于 2016–2022，当前最大待办切片是 2022 年 130 条。机器输出按年、按重叠 query-family membership 提供聚合统计；family 统计中的深度是**候选全局** URL 匹配深度，不代表该词族专属的筛查覆盖率。[可复算报告](../outputs/phase92/acl_screening_coverage.json)、阶段分析。候选与日志 URL 相同只表示有记录，不能当作相关性纳入、全文审阅、研究质量评估、召回率、新颖性结论或系统综述完成。

## 2026-10-07 COLM 2026 组合证据核验近邻

COLM 2026 官方录用列表已公开，会议日期为 2026-10-06 至 10-09。按组合核验、逻辑保持变体、结构化 reasoning trace 和 symbolic verification 主题进行定向标题检索，并筛读三篇作者公开全文：*When Verification Fails*、LPDS、Neuro-symbolic PRM。录用状态来自官方 COLM 页面，论文方法/实验/限制来自作者全文；该步骤没有穷尽检索 COLM accepted list 或完整 OpenReview 候选。核心综合是：单个显著子句被支持不能替代对所有必需约束的组合检查；形式执行正确不能替代语义 grounding；逻辑保持扰动要先验证语义不变。逐篇筛读证据、深度和差异见[结构化日志](../sources/literature_screening_log_2026-10-07_colm2026_compositional_verification.json)及Phase 55 报告。这三篇不属于冻结 ACL v3 候选框，不改变 ACL reconciliation；本次非系统综述、非 matched baseline、非新颖性审计。

## 2026-10-06 补查：直接使用 WordNet gloss 的 LLM 词汇蕴含判断

通过 ACL Anthology 官方页面/PDF 与限定 venue 的定向网页检索，发现并全文核读 Greco et al. (Findings of EMNLP 2024)：模型输入包含 WordNet 动词 synset 的 gloss，并判断词对的方向性 lexical entailment。该项补足了“释义作为 LLM 蕴含输入”这一近期任务级近邻；同时复核已在项目记录中的 GWC 2025 AI-WordNet 与 LREC 2026 adjective-hypernym 工作，未重复计作新发现。查询词、全文证据、边界和非穷尽性说明见[结构化日志](../sources/literature_screening_log_2026-10-06_definition_entailment_supplement.json)。这是目标明确的定向补查，不是完整跨会场系统综述或新颖性证明。

## 2026-10-06 EMNLP 2024 合成逻辑/NLI 与 Vampire 证明近邻

在固定 v2 中全文核读此前未匹配的 EMNLP 2024 主会论文 Unigram-FOL，检查生成语法、FOL/Vampire 接口、100K 语料切分、逻辑覆盖、消融及限制。该论文对受控形式系统 stress testing 有直接参考价值，但不是 WordNet/gloss source-support 评测。方法和证据边界见[机器日志](../sources/literature_screening_log_2026-10-06_unigram_fol.json)。


对 ACL Anthology 固定 v2 候选框内此前无日志匹配的 LREC-COLING 2024 主会论文 Diff-Comb Explainer 做官方 10 页全文筛读，涵盖 ILP/DBCS 子图选择、WorldTree 切分、ConceptNet 背景事实、指标定义、结果边界与复杂度局限。它属于解释选择/证据图邻居，不是 WordNet gloss 形式化系统；其 answer-explanation faithfulness 不等于 source entailment。逐项依据见[结构化日志](../sources/literature_screening_log_2026-10-06_diff_comb_explainer.json)。


从固定 ACL v2 候选框抽取一条此前无结构化日志 URL 匹配的 ACL 2024 Long Paper，核读 MALLS / LogicLLaMA 全文的生成流程、句法与语义对齐过滤、人工子集、指标、限制及许可声明。该工作提供 translation/equivalence 评测先例，不是 lexical-definition 或 gloss source-support 基线。逐项依据见[结构化日志](../sources/literature_screening_log_2026-10-06_malls_nl_fol.json)。

## 2026-10-06 ACL Anthology 候选框筛查续

在固定 v2 候选框中完成 2016–2019 年 82 条待筛记录的标题/摘要判断（1 direct、43 adjacent、35 background、3 exclude），并对直接先例及两篇邻接论文做定向全文核读；另完成 2023 年 12 条记录的标题/摘要判断（0 direct、7 adjacent、4 background、1 exclude）。逐篇理由与固定候选文件哈希见[2016–2019 日志](../sources/literature_screening_log_2026-10-06_acl_wordnet_direct_2016_2019.json)和[2023 日志](../sources/literature_screening_log_2026-10-06_acl_wordnet_direct_2023.json)。按脚本的精确规范化 URL 匹配复算，截至本日 v1 为 217/1,270、v2 为 303/1,634；v1 深度状态为全文 34、定向章节 17、元数据/摘要 14、深度未明 152，无匹配 1,053；v2 为全文 37、定向章节 21、元数据/摘要 93、深度未明 152，无匹配 1,331。152 条“深度未明”表示虽有 URL 命中，但对应逐篇记录未提供可判定筛读深度的显式字段；不得将其解释为已读全文或摘要。URL 匹配仅表示日志出现过该论文，不等于相关性纳入。所有数字都只描述固定 ACL 候选框与现存项目日志，不估计领域召回率，也不构成系统综述或新颖性证明。

## 2026-10-06 ICLR 形式化验证边界补查

按 ICLR 2026 官方 proceedings 定向核对 ProofBridge 的论文页及 23 页全文，读取任务定义、方法、数据构建、切分、指标、消融、结论和复现附录。重点记录其 Lean kernel 验证范围与参考 Lean formalization 作为 gold 的假设；将它作为形式 verifier 与自然语言来源忠实度分离的邻居，不复述其成绩为本项目基线。逐项事实和限制见[结构化筛读日志](../sources/literature_screening_log_2026-10-06_proofbridge.json)。这是单篇定向筛读，不是 ICLR 全会系统综述或新颖性证明；没有下载/复现代码、模型或数据。

## 2026-10-06 ICLR 2026 定义检索与 autoformalization 补查

在上述 ICLR 定向核查后，用 proceedings 检索词族 `WordNet gloss definition formal logic semantic parsing`、`concept definition retrieval augmented autoformalization`、`formal theorem proving natural language semantic correctness` 补查近期定义检索、自然语言 formalization 与语义验证路线，全文筛读两篇正式 ICLR Conference 论文：[CRAMF](https://proceedings.iclr.cc/paper_files/paper/2026/hash/fd83f4e0dcaf1c64ea15bbb1695bb40f-Abstract-Conference.html) 与 [Mathesis](https://proceedings.iclr.cc/paper_files/paper/2026/hash/93d5797656d3e70dca7535160a1458f3-Abstract-Conference.html)。CRAMF 是 Mathlib 定义检索辅助 Lean autoformalization 先例；Mathesis 是 LeanScorer 分级语义判断和 prover pipeline 先例。两个任务均属数学形式化，不是词典 sense、gloss-span support 或 lexical-hypernym baseline；纳入只限定广义先例，不表示 matched comparison 或研究新颖性已确立。查询字符串、两篇 25 页官方 PDF 核查范围和指标/样本限制见[结构化全文筛读日志](../sources/literature_screening_log_2026-10-06_iclr26_autoformalization_neighbors.json)。本次是两篇目标导向补查，没有记录 proceedings 全集命中总数或去重候选框，因此不能称为 ICLR 系统检索或召回审计。

## 2026-10-06 定义建模近期主会补查

通过 ACL Anthology 官方 EACL/ACL 2026 论文页定向发现 LM-Lexicon，随后核对[正式论文页](https://aclanthology.org/2026.eacl-long.1/)和[22 页官方 PDF](https://aclanthology.org/2026.eacl-long.1.pdf)中的任务、数据切分、主要结果、人评与 limitations。对照 SememeLRM、SenseRel 与 GWC AI-WordNet 时先查现有项目矩阵/日志，已有条目不重复计为新发现。逐篇事实和边界见[结构化筛读日志](../sources/literature_screening_log_2026-10-06_definition_modeling.json)。这是单篇定向全文章节复核，不是数据库穷尽搜索；不估计领域召回率，不支持新颖性结论。

## 2026-10-05 形式证明与分解式 NLI 补筛

从 ACL Anthology v2 固定候选框内抽取两篇仍为待筛状态的主会论文，核对 [GFaiR / resolution refutation](https://aclanthology.org/2024.lrec-main.1436/) 官方页面、PDF 和 arXiv HTML，以及 [RDTE / TREEWISE](https://aclanthology.org/2024.emnlp-main.531/) 的官方页面与全文 PDF。逐项筛读、方法/结果/局限及文内数量冲突见[机器日志](../sources/literature_screening_log_2026-10-05_logic_proof_and_decompositional_nli.json)。两项工作分别强化“逻辑步骤可验证”和“组合论证须有清晰人工准则”的相关工作边界；都不提供 WordNet gloss→typed AND/OR Horn + source-span support 的匹配评测。同步运行 `reconcile_acl_screening_logs` 后，v1 为 59/1,270 匹配，v2 为 144/1,634 匹配；这些数字只是结构化日志 URL 命中/筛读深度计数，不等于相关性纳入或系统综述召回率。

## 2026-10-05 细粒度 source-support 与 NLI 全文补筛

以 ACL Anthology 官方页面及 PDF 定向全文复核 PrefixNLI（ACL 2026 Long Papers）和 QASemConsistency（TACL 2026）。PrefixNLI 处理不完整假设前缀，使用 human-span/synthetic 数据训练 prefix-level NLI，并测试其对受控摘要生成的影响；QASemConsistency 将生成句拆分为 predicate–argument QA，建立三人多数票的局部 source-support 标注。逐篇数据、指标、venue、错误边界与不可移植性见[结构化日志](../sources/literature_screening_log_2026-10-05_fine_grained_support.json)。它们分别启发不完整候选压力测试和 claim-level 支持标注；都不处理 WordNet sense-linked gloss 到方向性 AND/OR Horn 规则，也不提供该项目的 gold 或匹配基线。本轮为单人定向补筛，不能证明检索完备或新颖性。

## 2026-10-05 ACL Anthology 全量元数据候选框

为解决此前 ACL 定向页面搜索无稳定候选全集的问题，新增 `src/analysis/search_related_work_acl.py`，读取 ACL Anthology 官方 [BibTeX+abstract export](https://aclanthology.org/anthology+abstracts.bib.gz)，在 2016–2026 年论文书目记录的 title/abstract 上运行英文词族。查询定义直接见脚本中的 `QUERY_TERMS`；输出记录压缩导出 SHA-256、解压后 BibTeX 内容 SHA-256、各词族去重前命中数及候选记录。复跑：`python -m src.analysis.search_related_work_acl`；若需写新文件，传 `--output`，覆盖既有文件时显式传 `--force`。v1 的压缩导出 SHA-256 为 `7c7503497597f5cab221923e5de454b3cc6cb2e48d9ab28b8c88269189314669`；处理 131,647 条 BibTeX entry（所有 entry 类型），限定年份后按四组命中共汇总为 1,270 个唯一候选；各组命中数为 178、255、296、591，组间重叠。候选中 12 条没有摘要字段。候选集和抽取字段保存在[机器导出](../sources/acl_anthology_candidates_2026-10-05.json)。

原始候选框 v1 生成后，使用 `src/analysis/reconcile_acl_screening_logs.py` 按规范化 ACL Anthology 页面 URL 与 `sources/literature_screening_log*.json` 做精确交叉核对：`python -m src.analysis.reconcile_acl_screening_logs --force`。截至 2026-10-05 最新复算，v1（1,270 条候选）有 59 条精确 URL 匹配，匹配深度为全文 32、定向章节 13、仅元数据/摘要 14、深度未注明 0；其余 1,211 条尚无结构化日志匹配。`prior_screening_log_match` 只表示本项目曾记录该正式论文页面；它不表示相关性已判定或系统综述纳入。逐篇 `screening_depth_status` 仅按匹配记录中的显式字段归一为 `full_text_screened`、`targeted_sections_screened`、`metadata_or_abstract_only` 或 `prior_log_depth_unresolved`；多份日志中取证据最深者。不会用日志总体筛查方法、篇数或标题推断逐篇深度；原始字段保留在 `screening_evidence[].explicit_depth_evidence` 中以便审计。

### 2026-10-05 source-grounded entailment 查询族扩展（v2）

上述定向全文复核发现 ACL 2026 PrefixNLI 和 TACL 2026 QASemConsistency 都不在 v1 的 1,270 条候选框中。为修正“自然语言蕴含 + 形式证明”共现词族漏掉 source-grounded entailment 的问题，在 `src/analysis/search_related_work_acl.py` 新增 `source_grounded_entailment` 词族；不覆盖 v1 文件，另存[扩展候选框 v2](../sources/acl_anthology_candidates_2026-10-05_v2.json)。v2 压缩导出 SHA-256 为 `04352252858ab6e466ec039d1fda3f23395731c2a4d70d7281db5ba8fafea4b4`，解压后内容 SHA-256 为 `045b66593e91fb24d71a14917c41ccecb14278dfcb6c8069b1bea1bfa188df27`；新增族有 404 个去重前命中，总候选由 1,270 增至 1,634（净增 364）。截至 2026-10-05 最新日志对账，v2 有 144/1,634 条 URL 精确匹配，深度计数为全文 34、定向章节 17、摘要/元数据 93；另有 1,490 条候选尚无结构化日志匹配。新增的 2025–2026 两年筛查日志覆盖该切片全部 96 条候选记录。该运行证明新版查询捕获了两个已知漏项，不是 ACL 归档 recall 的估计；日志匹配不代表相关性纳入或系统综述召回率。

### 2026-10-05 图式事实核验与 NLI-guided RAG 定向补筛

从 v2 的 `source_grounded_entailment` 词族抽取 2025–2026 年候选（该两年共有 96 条）后，优先检查把 source evidence/NLI 与图、多跳推理、形式验证或 citation attribution 明确相连的记录。本轮新增结构化逐篇日志六篇，其中 FactCG、FactReasoner、NSF-CoT 核读官方 PDF 的方法、实验和限制章节；CiteEval、Self-Correcting RAG 与 Transform Retrieval 只核对官方页面/摘要。早前记录的 PrefixNLI 和 QASemConsistency 保留在独立全文日志中。结果分别作为图式数据构造、概率证据聚合、形式 QA 验证、来源归因评价及 NLI-guided retrieval 的近邻，不视为 WordNet 定义逻辑化的匹配基线。[逐篇记录及边界](../sources/literature_screening_log_2026-10-05_graph_factuality_nli.json)。

现已对 ACL v2 中 2025–2026 的 96 条候选记录逐条作标题/摘要决定；同题同年的两组导出别名去重后为 94 个论文题名。11 条已有结构化深筛记录，另保留 11 条供全文优先复核、22 条作跨域/背景邻居，50 条按范围排除，2 条标为重复书目别名。逐篇理由写在[标题/摘要筛查账本](../sources/literature_screening_log_2026-10-05_acl_source_grounded_title_abstract.json)，候选 v2 中也存了对应决定。此单人筛查仍受 ACL 单库、宽松检索词族限制；保留项不是最终综述纳入或 top-conference 质量排序，排除数不是 PRISMA 数字，也不能支持新颖性结论。优先候选的首轮 PDF 定向章节复核已完成六篇，其中四篇为 ACL/NAACL Findings、两篇为 NALOMA workshop；其余候选仍需按直接方法相关性与 venue 分层后再决定全文深筛。

### 2026-10-05 ACL Findings source-grounded NLI 定向 PDF 复核

从 11 篇优先全文候选中先核读 ACL/NAACL Findings 四篇官方 PDF 的任务定义、数据构造、人工审查、主要结果与局限章节（不宣称逐页全文/附录穷尽），逐篇边界见[follow-up JSON](../sources/literature_screening_log_2026-10-05_acl_source_grounded_followup.json)。ACL 2025 QC-NLI 把文档 NLI 标签条件化于 query/aspect，21,655 条样例来自 GPT-4o 改写的既有数据；人工抽查每集 33/51 项、共同样例仅 7，作者还明确将长文来源 span attribution 留为后续方向。ACL 2025 HaluMap 以 source/output 文段 NLI 矩阵加 self-NLI 背景校准作生成忠实度判断；NAACL 2025 RefNLI 的 1,143 例说明 premise/hypothesis referent 不一致可改变标签和人类分歧；ACL 2026 Comprehensiveness Metrics 把原子事实间 NLI entailment 组织成评估图，但在 50 样本人审中 NLI 输出完全正确率为 48%（QA 66%、E2E 88%）。这些结果分别强调 aspect、source/sense identity、原子分解和独立人审的重要性；NLI graph 不是逻辑 proof DAG，任务成绩不能外推到 WordNet gloss 规则支持，也不构成本项目匹配基线。

同一优先池再补充两篇 NALOMA workshop 论文的 PDF 定向章节：Saeki & Bekki（2026）记录 wani 形式 NLI prover 的 AND/OR proof-search tree，并在两个 JSeM 案例检查重建不变量；Noble et al.（2025）比较 LLM 生成 FOL、Prover9 与直接标签，指出公式生成即使改善模型分类，也不保证定理证明能从前提/假设公式推出正确关系。前者提供结构保真核查参照，后者说明形式表示语义链接是独立误差源；二者都不是 gloss-to-Horn 实证。筛读细节及明确范围见同一[逐篇 follow-up JSON](../sources/literature_screening_log_2026-10-05_acl_source_grounded_followup.json)。

### 2026-10-05 OpenAlex 候选的标题/摘要筛查

复核既有 `sources/literature_screening_log_2026-10-04_openalex.json` 后，将其 43 条候选的原始单人标题/摘要决定规范化为[逐篇对账表](../sources/openalex_title_abstract_screen_2026-10-05.json)，不重复声称进行了一轮独立筛选。原筛查记录为 4 条新增、9 条已在项目矩阵、30 条排除；候选导出中有 34 条摘要、9 条只有标题。3 条被保留记录在 OpenAlex 导出中缺少摘要，但既有日志记录已核对其出版方元数据/摘要；保留项仍须按原日志记录的证据级别对待。

该数目是 OpenAlex 固定候选框内的标题/摘要初筛数，不是最终纳入数或 PRISMA 总量。与 ACL 1,270 条候选按规范化 DOI 精确匹配 8 条，标题+年份回退匹配 0 条；两个候选框去重后合计 1,305 条候选记录，但这不等于 1,305 条已完成相关性筛查的论文。OpenAlex venue/type 元数据未逐条核验；后续应对主会/Findings/workshop/其他出版形态分别确认，并全文审查保留项。筛查准则将“使用 WordNet/图”与“研究定义来源、义项关系、形式语义或证明证据方法”区分，避免因关键词偶合就当相关论文。

### 2026-10-05 直接定义到规则先例补筛

对固定 ACL 候选中 Moeljadi & Bond 的 Wordnet Bahasa 定义关系抽取论文作官方 PDF 全文复核，并沿其引用明确提及的语法驱动抽取邻域补读 Bond et al. (COLING 2004) 全文；同时复核 Almiman & Ramsay 的 RANLP 2017 全文。后两篇不计入 ACL 候选框数量。三篇发现方法、完整筛查范围、关键指标边界及 RANLP 文献内部召回率差异见[机器日志](../sources/literature_screening_log_2026-10-05_definition_to_rules.json)。结果已纳入[相关工作矩阵](related_work.md)与[最近工作逐项对照](closest_work_comparison.md)。这三篇精选先例不能代表检索完整，也不构成新颖性结论。

### 2026-10-05 近期 WordNet/gloss 候选的题名摘要筛查与定向章节核验

在 ACL 第一组 WordNet/gloss/词汇关系候选中，单独筛查 2024–2026 年 24 条记录：6 条已有日志匹配，本轮新筛 18 条，9 条保留作后续全文核验、9 条在题名摘要阶段排除。逐篇处置与范围限制见[机器日志](../sources/literature_screening_log_2026-10-05_recent_acl_wordnet_slice.json)。对 LREC-COLING 2024 两篇及后续三篇保留候选，只复核与研究定位直接相关的 PDF 章节：*Enriching Word Usage Graphs with Cluster Definitions* 的人工任务测试定义能否辨认 usage cluster，不判定义的事实正确性或 gloss-span 支持；*WordNet under Scrutiny* 评估的是词典用例的自然度、信息量与自包含性，不能充当释义命题 gold。五篇均为定向章节筛读，不标成全文审阅；新增三篇为 LREC-COLING 2024 主会的中文义项标注、OntoLex Workshop 2025 的形容词 hypernym 数据、OSACT @ LREC-COLING 2024 workshop 的 Arabic WordNet 质量修订。它们的官方 PDF 证据、量化结果和 venue 层级已追加到逐篇日志。LREC 2026 跨语 WordNet 层级论文目前仅有官方 ACL Anthology 与 LREC Proceedings 页面/摘要证据；ACL PDF 超出读取大小限制，LREC 官方 PDF 请求返回 502，发布的对齐数据集/框架尚未检查。筛读日志已并入 ACL 候选框的逐篇状态重算。

### 2026-10-05 近期 WordNet-gloss 分类与 theorem-prover 评测

从未筛 ACL 候选中全文复核 ACL 2024 Long Paper *Using Synchronic Definitions and Semantic Relations to Classify Semantic Change Types*，以及 BlackboxNLP 2025 workshop 的 *A Theorem-Proving-Based Evaluation of Neural Semantic Parsing*。二者证据层级、任务和对本项目的比较边界见[结构化全文筛读日志](../sources/literature_screening_log_2026-10-05_recent_acl_methods.json)。第一篇是基于 WordNet relation-derived labels 的 gloss-pair 分类，不是规则抽取；第二篇以 Vampire 对比生成式与参考 logical forms，不是对原始 gloss 的 semantic support 检验。它们已补入相关工作和最近工作矩阵，用于定义分层评测而不跨任务比较分数。

按第一组“WordNet/gloss/词汇关系”词族优先检查 ACL 2024 主会长文 TaxoLLaMA，全文内容、纳入与边界见[专项日志](../sources/literature_screening_log_2026-10-05_aclanthology_taxollama.json)。它以 WordNet 3.0 的既有 hypernym links 微调模型并评测 taxonomy/lexical entailment，是直接 baseline；该审查将“用 WordNet 训练模型预测上下位”从潜在新颖性主张中排除。其余候选仍待人工筛查。

另从 definition-to-formal-logic 族筛读 EMNLP 2025 的 *Autoformalization in the Wild* 与 *Reliable Evaluation and Benchmarks for Statement Autoformalization*；详情见[结构化筛读日志](../sources/literature_screening_log_2026-10-05_autoformalization_evaluation.json)。两者分别排除“自然语言定义形式化+证明器评估”这一宽泛 novelty，并提示必须把 prover/type-check 成功与人工语义等价、源 span 支持拆开评测。两篇仅是精选筛查，ACL 其余候选仍待处理。

补充核对 Findings IJCNLP-AACL 2025 的 NL2FOL，专项日志见[机器记录](../sources/literature_screening_log_2026-10-05_nl2fol.json)。该工作展示 NL→FOL→SMT/CVC4 与反模型，且报告了 pairwise NLI 背景关系遗漏多前提 conjunction 的失败模式；候选框已同步其全文筛读状态。ACL 书目全集仍只筛过少数高优先级项。

另对 ACL 2025 Long Paper *Entailment-Preserving First-order Logic Representations* 全文筛读并更新[专项日志](../sources/literature_screening_log_2026-10-05_epf.json)：EPR/EPR@K 衡量 prover 输出保留多前提自然语言 entailment 标签的比例，不是公式逐条语义等价或 gloss-span 支持。作者的 premise-use/new-predicate filters 与最小语言对缺失都纳入项目评测边界；不能把其 RTE 成绩移作 WordNet 实验结果。

这是 ACL 单一书目档案的词面筛查框，不是 1,270 篇相关论文，也不自动决定纳入/排除；phrase matching、文种字段缺失、venue track 区分、历史引文和语义相关性都需要人工筛查。它只改善 ACL 归档覆盖与可复算性，不能估计其他数据库 recall，也不构成穷尽系统综述或 novelty audit。ACL Anthology 页面注明 2016 年及之后材料采用 CC BY 4.0；具体外部数据集和上游资源许可仍需单独判断。

## 2026-10-04 EMNLP 2026 论文集可用性检查

按 WordNet definition / lexical relation / autoformalization / NLI-verification 主题查询官方 ACL Anthology 后，本轮没有返回 EMNLP 2026 的论文级 proceedings 记录。官方 EMNLP 网站列出主会日期为 2026-10-24 至 2026-10-29，官方 CFP 说明 accepted paper 须在会上报告后才进入 proceedings；因此截至 2026-10-04 应将该届纳入范围标记为**待论文集发布后复查**，不能从当前无命中推断无相关工作。查询、官方时点证据和复查条件记于[机器可读日志](../sources/literature_screening_log_2026-10-04_emnlp2026_status.json)。本项是可用性边界记录，不是完整筛读、PRISMA 流程或 novelty audit。

## 2026-10-04 OpenAlex 可复现候选集补充

新增 `src/analysis/search_related_work_openalex.py`，以 OpenAlex Works API 的 `search.title_and_abstract` 字段按 8 个预先写定的词组查询 2024-01-01 至 2026-10-04、`type:conference-paper` 候选；逐页抓取并按 DOI（缺失时用规范化标题+年份）去重，输出 43 条记录至[原始候选导出](../sources/openalex_related_work_2026-10-04.json)。复算命令为 `python -m src.analysis.search_related_work_openalex --output sources/openalex_related_work_2026-10-04.json`；查询字段按 [OpenAlex 搜索文档](https://help.openalex.org/api/searching/)指定。精确词组、每个 query 的命中数、逐条标题/摘要筛选状态、纳排理由和局限见[结构化筛选日志](../sources/literature_screening_log_2026-10-04_openalex.json)。

这 8 条检索返回 45 个重叠命中，经 DOI/title-year 去重为 43 条；4 篇作为新邻居补入对照矩阵，9 篇映射到既有矩阵，30 篇排除。最初因导出无摘要而暂缓的 FOLDCoVe 已经出版社核验，与另外三篇一起计入这 4 篇。OpenAlex 的 source/type 元数据有缺失，日期存在年初占位，且检索词无法覆盖相关领域全部表达；导出不是 PRISMA 候选总集。该补充将 SymbCoT、乌克兰 WordNet 上下位关系抽取、Prover-Guided Correction 与 FOLDCoVe 作为不同层级邻居；Springer 章节仅依据官方摘要，不推断全文细节。此轮仍是单人定向 scoping review，不是双人筛选、系统综述或 novelty audit；官方出版社/论文集页面支持具体引用事实。

2026-10-05 的 ACL Anthology 直接筛读又发现 CoPE、LogiQAte、Unifying Inference-Time Planning Language Generation、CARL 四篇 ACL/EACL 2026 论文不在上述 43 条 OpenAlex 候选里；标题级漏检清单保存在同一机器日志的 `post_search_completeness_check` 字段。这不是全库 recall 估计，但证明当前 8 个词组未覆盖 ACL 2026 相关候选；后续若要接近系统检索，需扩展检索式并并行筛官方会议论文集，不能以 43 条导出支持“检索完整”。

## 2026-10-03 补充：推理忠实度与形式化不确定性

本轮以官方 ACL Anthology、AAAI OJS、NeurIPS proceedings 为筛查来源，搜索词组合包括 WordNet/gloss/definition/lexical relation、formalization/faithfulness/uncertainty/selective verification、knowledge graph/provenance/hypergraph。新增两篇精选全文：SAVeR (ACL 2026) 与 Grammars of Formal Uncertainty (NeurIPS 2025)；精确查询、筛选说明和纳排记录见[结构化日志](../sources/literature_screening_log_2026-10-03_selective_faithfulness.json)。Direct Dependency Retrieval 与 Structured Sememe Knowledge 虽再次命中，但此前已纳入，不重复计数。搜索系统未给出稳定可导出的去重候选全集，“2 篇”仅为本轮定向全文纳入数，并非总命中数或 PRISMA 流程数。

这项补充不改变总体综述类型：仍为单人定向 scoping review。完整系统检索仍缺 ACL Anthology/OpenReview/综合索引的结构化可导出候选全集、按预先冻结标准的双人筛选及引用链追踪。相关工作矩阵继续优先比较直接 WordNet gloss/关系抽取、GlossTag/semantic parsing、sememe-tree 和 direction/source-support 方法。

### 2026-10-03 补充：AST-guided formalization 与 parser–prover 模块化

再次从 ACL Anthology 与 AAAI OJS 官方来源定向查找近期逻辑化系统，精确查询及范围见[结构化日志](../sources/literature_screening_log_2026-10-03_logic_pipeline.json)。本轮新全文筛读 3 篇：NL2Logic (Findings EACL 2026)、UFAL-CUNI SemEval-2026 Task 11 系统、AAAI 2026 Hybrid Knowledge Base reasoning；FOLX-KG 已在该轮后续单独完成官方全文复核，仍是既有矩阵工作，不重复计数为新增纳入。没有稳定导出、去重的完整搜索候选集，故只记人工全文筛读数，不报告 PRISMA 数量。

这轮核对把“语义正确”进一步拆清：NL2Logic 以 3,000 条 premise–hypothesis 的下游 NLI accuracy 间接代理翻译语义，适合成为结构化解析/确定性生成基线，但不是 gloss-span support gold；其作者也提示前提不一致/不可满足会导致形式结论误导。SemEval 系统展示 FOL parser、transpiler、Prover9、前提筛选的可消融组件边界，适合借鉴 pipeline ablation；其三段论共享任务不能充当 lexical-definition 性能基线。AAAI HKB 工作是符号 ontology 与 classifier 的模型论结合及推理复杂度理论，进一步说明“神经+符号推理”过于宽泛，项目必须靠义项/来源可追溯的定义知识获取和语义支持评测来收窄问题。三者的 venue、任务、证据等级及边界见日志与矩阵。

FOLX-KG 的全文复核补上了此前仅凭摘要的矩阵空缺：其 Appendix D 采用“公式解释器与构造标签对照 + 两批人工 claim–formula 一致性抽样及重叠集 κ”，Appendix G 又把程序错误拆为 syntax、logical、execution 三型。这为项目分层质控和错误分型提供可追溯设计先例，但测试对象仍是 DBpedia claim–formula，不是 source gloss span→方向性规则；且其 100% interpreter agreement 是相对其构造/标注标签的内部核对，不能替代独立 gloss-semantic gold。详见更新后的结构化日志与[最近工作对照](closest_work_comparison.md)。

检索日期：2026-10-02（Asia/Shanghai）。文献范围：词典/WordNet gloss 自动产生义项关系或知识结构；定义到形式逻辑；形式化 NLI、定理证明与可验证推理；Horn/Datalog provenance 与证明证据。目标是研究定位用的**定向 scoping review**，不是 PRISMA 系统综述或穷尽检索。

补充检索更新至 2026-10-03；当日筛读记录单列于 [2026-10-03 筛读日志](../sources/literature_screening_log_2026-10-03.json)。

2026-10-05 对 ACL Anthology 2026 ACL/EACL 长文与 ACL Findings 做了新的定向正式论文集筛读，补入自然语言约束形式化（CoPE）、等价逻辑混淆（LogiQAte）、规划 formalizer 中间表示/复杂度对照，以及 constraint-aware training 四个邻接方向。查询式、筛选计数与论文级范围见[筛读日志](../sources/literature_screening_log_2026-10-05_formalization_robustness.json)。这是四篇精选论文的局部任务/方法核查，没有稳定导出全量命中集或每条 query 的命中数，不报告 PRISMA，不声称穷尽或新颖性审计。

### 2026-10-03 补充：NLI 定理证明与查询时逻辑依赖 DAG

为补齐“逻辑图读出”与“NL→形式逻辑→证明器”两条邻接线索，补查 ACL Anthology 与 AAAI OJS 官方页面。新增候选为 ACL 2025 长文 *Faithful and Robust LLM-Driven Theorem Proving for NLI Explanations*（官方页/摘要核对）与 AAAI 2026 *You Don’t Need Pre-Built Graphs for RAG: Retrieval Augmented Generation with Adaptive Reasoning Structures*（官方页/摘要核对）；检索式、筛查边界见[结构化日志](../sources/literature_screening_log_2026-10-03_logic_dag_supplement.json)。未在本轮重新读取两篇全文或复现实验，引用只限官方摘要支持的事实，不报告不可比的论文性能数字。

ACL 论文进一步说明，LLM 自动形式化接 theorem prover 并以逻辑结构修复/生成 NLI explanation 已是既有研究路线；所以本项目不能把该组合本身作为新意。AAAI LogicRAG 则在 query-time 构造问题依赖 DAG 来指导检索，和本项目对固定释义语料构建可追溯、AND/OR 保真的知识依赖超图不是同一对象。两者共同支持的是“表示—编译/检验—读出”模块需拆开评测，而非项目方案有效性的证据。相关矩阵只将它们作边界/设计参照；项目效果与新颖性仍待 sense-disjoint gold 和匹配基线验证。

## 问题和纳入标准

问题：已有系统分别解决了哪些从定义到词汇关系/形式规则/可验证推理的问题？它们保留了什么义项、方向、变量/作用域、来源链和可重放证明？项目剩余可检验的交叉点是什么？

纳入：优先 2018–2026 年同行评审 ACL/NAACL/EACL/EMNLP/AAAI/ICLR/LREC/Global WordNet 论文；补充最直接的早期方法；论文主题至少覆盖（a）WordNet/词典 gloss 结构抽取或 hypernymy，或（b）自然语言形式化与逻辑校验/proof，或（c）逻辑推理证据/provenance。仅当可核对官方 proceedings、OpenReview 或作者正式论文页面时，纳入具体方法结论。

排除：只讲一般 LLM 幻觉而无知识/逻辑/证据机制；非论文性产品宣传；无法确认出版状态的匿名稿；和词义/形式推理交集太远的通用 hypergraph neural network。同行评审主张与 preprint/workshop 主张分开标识。

## 来源与检索式

使用网页检索并打开原始论文集页面；交叉覆盖 ACL Anthology（含 ACL/EACL/NAACL/EMNLP/LREC/GWC 等论文集）、AAAI OJS、OpenReview；通过 ACL 原文 PDF 补读关键定义抽取方法。推荐的 `parallel-cli` 在本执行环境未安装，未声称它或 Google Scholar/Semantic Scholar 的数据库级检索已执行。

实际执行的查询词/域名限制（逻辑 AND/OR 按搜索引擎自然语言匹配，不等价于数据库语法）：

```text
site:aclanthology.org 2025 2026 dictionary definition WordNet knowledge graph entailment gloss extraction
site:aclanthology.org 2025 2026 natural language to first-order logic theorem prover NLI explanation verification
site:openreview.net/forum 2025 2026 formal verification natural language inference logic reasoning proof
site:aclanthology.org/2026 definition gloss WordNet semantic relation knowledge extraction
site:aclanthology.org/2026 verified first-order logic reasoning traces
site:aclanthology.org/2026 sentence-level fine-grained provenance inference evidence
site:ojs.aaai.org/index.php/AAAI/article/view Datalog provenance explanations logical rules
site:ojs.aaai.org/index.php/AAAI/article/view 2026 query-driven evidence graph incomplete knowledge
site:aclanthology.org/2026 knowledge graph RAG incomplete knowledge benchmark
site:openreview.net/forum 2026 first-order logic NLI verification
"Extracting WordNet links from dictionary glosses" Latvian Wordnet 2025
"FOL-Traces: Verified First-Order Logic Reasoning Traces at Scale"
"FOLX-KG" ACL 2026 first-order logic knowledge graph
site:aclanthology.org/2026 WordNet definition LREC hypernymy
"VeriCoT" ICLR 2026 logic consistency verification
```

### 2026-10-02 补充检索：gloss bases、WordNet expansion 与 autoformalization

为补足“85 basis/semantic primitive”“仅凭释义扩展 WordNet”和“自然语言定义正式化”三个潜在 novelty collision，追加检索 ACL Anthology（ACL/EMNLP/Findings/GWC/OntoLex）、AAAI OJS 与 OpenReview 的官方论文/投稿页；检索发现阶段用 web search，出版状态和定量信息再回到官方 proceedings/PDF 核对。执行的查询主题/字符串包括：

```text
site:aclanthology.org/2025 OR site:aclanthology.org/2026 definition gloss WordNet hypernym lexical semantics
site:aclanthology.org/2025 OR site:aclanthology.org/2026 autoformalization first-order logic theorem proving definitions
site:aclanthology.org/2025 OR site:aclanthology.org/2026 WordNet gloss knowledge graph construction provenance
site:ojs.aaai.org/index.php/AAAI/article/view/ 2026 formal reasoning knowledge bases provenance evidence
site:openreview.net 2025 2026 formal prover verified reasoning knowledge graph
"semantic primitives" WordNet gloss base concepts
"Expanding WordNet Based on Glosses" AI-WordNet
"Autoformalization in the Wild" mathematical definitions Isabelle
"Improving Autoformalization Using Direct Dependency Retrieval"
```

追加核对的官方来源包括 ACL Anthology 的 GWC 2025/EMNLP 2025/ACL 2026 论文页及相应 PDF、AAAI OJS 的 AAAI-26 正式页，以及 OpenReview 状态页。OpenReview 搜到的若干材料明确标注 under review 或 workshop，未混进 peer-reviewed core set；例如未确认正式录用的 ICLR 投稿只作为待核线索。没有取得稳定、可导出的全库检索命中总数/去重列表，因此这里仍不做 PRISMA 数量声明。ACL Anthology、AAAI OJS、OpenReview 是本轮的多个官方 venue/archive 入口，但这种 venue 定向检索不能等价为跨学科数据库的穷尽检索。

### 2026-10-02 补充：规则归纳难度与形式化评测

为把逻辑图实验设计与最新形式化研究对齐，本轮进一步检索 AAAI-25 的 LLM 逻辑理论归纳，以及 EMNLP-25 的 autoformalization 基准/真实定义研究。实际执行的发现查询：

```text
site:ojs.aaai.org/index.php/AAAI/article/view "Inductive Learning of Logical Theories with LLMs"
site:aclanthology.org/2025.emnlp-main autoformalization definitions prover evaluation
"Expanding WordNet Based on Glosses: Methodology and Applications"
"Computing the Why-Provenance for Datalog Queries via SAT Solvers"
```

本次定向复核 3 篇正式论文全文：Sun & Wang (GWC 2025) AI-WordNet；de Souza et al. (AAAI 2025) 逻辑理论归纳；Zhang et al. (EMNLP 2025) 数学定义 autoformalization。其中 AI-WordNet 与数学定义工作已在前轮纳入，本轮是为核对实验细节而复读；AAAI 工作是新补入的邻接先例。另对 Poiroux et al. (EMNLP 2025) 全文核对评测贡献，并重开 Calautti et al. (AAAI 2024) 官方全文核对 why-provenance；二者属既有条目的复核，不重复计数。发现页结果没有可导出候选集，故这些是实际全文复核数，不是检索总命中数或完整筛查数。逐项状态和证据链接见筛读日志 JSON。

这一轮强化了两条方法学结论。第一，AAAI-25 的逻辑归纳实验按规则表达力分层，并报告长谓词关系链对 LLM 更难；本项目已有的 witness depth 与 OR 分支结构可形成可控的压力测试分层，但这只是可迁移的实验设计启发，不是性能预判。第二，Datalog why-provenance 关注导致查询答案的输入事实集合及其替代推导，和当前每个 head 保存一条结构性 witness DAG 不同；若研究问题要求“证据覆盖/全部支持来源”，应把替代 clause/source lineage 明确定义为另一项任务，不能把单 witness 当成完整 provenance。EMNLP-25 的数学形式化评测还强化了独立语义等价标注的必要性：类型检查或 theorem-prover 成功不是源自然语言忠实度的充分指标。

已打开/核对关键全文或 PDF 的新增条目包括：GWC 2025 AI-WordNet；EMNLP 2025 Autoformalization in the Wild 与 Reliable Evaluation and Benchmarks；ACL 2026 Direct Dependency Retrieval；Findings EMNLP 2025 FOL Closeness Metrics；ACL 2025 TROVE；GWC 2025 WordNet–human relation alignment。其他新增条目目前仍以官方元数据/摘要筛选，不把未读全文的细节当作确定事实。

工具没有导出可审计的各数据库总命中数、去重条目表或完整全文筛选数；故不报告 PRISMA 数字，也不声称检索饱和。精确的页面链接和研究摘要在 [相关工作](related_work.md)。可复查入口包括 [ACL Anthology](https://aclanthology.org/)、[AAAI Proceedings](https://ojs.aaai.org/index.php/AAAI/) 和 [OpenReview](https://openreview.net/)。AI 辅助用于扩展检索词、发现候选和整理摘要；纳入的关键出版状态、方法描述与数字已尽可能回到官方论文页面或全文核对，文献解释和新颖性判断仍须由研究者复核。

### 2026-10-02 补充：定义辅助层级推断与词汇关系评分

为审查“定义→关系/层级”与“LLM 参与词汇语义评估”两个相邻方向，继续定向检索 ACL Anthology（含 TACL/Computational Linguistics 正式页面与 PDF）及 AAAI OJS；OpenReview 用于状态核查。发现阶段使用的检索主题/式包括：

```text
site:aclanthology.org/2026 TACL definition augmented relational reasoning hierarchy scientific concepts
site:aclanthology.org/2026 computational linguistics large language model lexical semantic relations strength human ratings
site:ojs.aaai.org/index.php/AAAI 2026 natural language definitions knowledge acquisition symbolic constraints
site:openreview.net 2026 definition reasoning concept hierarchy formal logic
```

本次实际打开全文并筛读方法/结果段 3 篇：Forer & Hope, TACL 2026；dos Santos & Leal, Computational Linguistics 2026；以及 Nirenburg et al., “LLMs as Knowledge Workers”（AAAI Spring Symposium Series 2026）。最后一篇为 symposium proceedings，不纳入 AAAI technical-track 主会论文集，仅作为知识获取流程/约束验证架构近邻。全文显示其实验限于一篇船舶维护文本，报告 9 个词典条目与 2 个本体概念通过自动约束检查；作者明确未做规模化准确率/效率评估，并保留未决案例的人审。它使用 OntoAgent 自有 ontology/lexicon，不是 WordNet gloss-to-Horn 方法。OpenReview 未产生可确认新增正式录用论文。网站搜索的总命中数与去重结果没有被稳定记录，因此只报告“全文实际筛读 3 篇”，不把搜索引擎结果数冒充筛选数。官方全文中的方法、结果和适用边界已写入[相关工作](related_work.md)、[最接近工作的对照矩阵](closest_work_comparison.md)及[结构化筛读日志](../sources/literature_screening_log_2026-10-03_fulltext.json)。

主要结果的使用边界：Forer & Hope 在 SCICO 科学文献概念共指/层级任务中报告定义增强模型的层级指标提升；dos Santos & Leal 预测的是人类给出的词汇关系**强度分数**，以相关系数评价。后者不测定向的义项级蕴含、定义逻辑化忠实度或 proof validity，不能作为本项目端到端有效性的证据。两项均增加了潜在基线/评测设计参考，但不改变本综述为单人定向 scoping review、非穷尽 novelty audit 的性质。

### 2026-10-02 补充：WordNet gloss→形式语义的直接先例

上一版对近年相关工作覆盖较多，但低估了 WordNet gloss 形式化本身的历史脉络。为避免把长期存在的任务误报为新颖，本次对 ACL Anthology/GWC 页面、出版商 DOI 和作者正式论文 PDF 追加精确题名/引用链搜索：

```text
"On the Automatic Generation of Intermediate Logic Forms for WordNet Glosses"
"Semantic Parsing and Sense Tagging the Princeton WordNet Gloss Corpus"
site:aclanthology.org/2025.cl-1.7 WordNet taxonomy semantic parsing challenge set
site:aclanthology.org gloss WordNet "logical form" definition parsing sense tagging
"eXtended WordNet" gloss logical form WordNet 3.0 semantic parsing
```

实际全文筛读 3 项并纳入直接/邻接工作：Agerri & Peñas (CICLing 2010, ILF-WN)；Rademaker et al. (GWC 2023, Princeton GlossTag/ERG)；Zhang et al. (Computational Linguistics 2025, taxonomy-aware neural semantic parsing)。此外 ILF-WN 正文对 eXtended WordNet 与 WN30-lfs 作比较，故将二者作为该历史谱系中的必要对照，但没有把未单独检索/筛读的所有 XWN 版本计入全文筛选数。三项来源均回到正式论文页面/作者或出版商全文核对。结构化候选、DOI、逐项纳排理由与未记录的计数项见 [筛读日志 JSON](../sources/literature_screening_log_2026-10-02.json)。数据库级搜索命中总数和去重列表依旧不可得；这是一组补充的定向引文/题名追溯，不构成 PRISMA 流程或穷尽检索。

这次核查会实质收窄 novelty framing：**WordNet gloss 自动解析/逻辑形式化不是空白**，而项目潜在研究增量必须放在旧资源逐项比较后，尤其验证 sense/version provenance、变量和 scope、显式保留 AND/OR、形式规则与源 span 的语义支持关系、独立 proof/unknown 证书，以及针对定义忠实度的 gold 评测。对照矩阵增加了对应条目；其中发布/资源实际可获取性和许可仍待检查，不能仅据论文正文假定可复现。

## 纳入的核心研究簇

1. 定义/词典到图、基础概念或词汇关系：eXtended WordNet/WN30-lfs/ILF-WN；WordNetGraph (LREC 2018)；Hsu & Hsieh gloss base-concept study (2013)；COLLIE-V (LREC 2020)；Dictionary sememe KB (Findings ACL 2021)；AI-WordNet (GWC 2025)；Latvian WordNet gloss-link extraction、LLM abstraction ladders、WordNet–human relation alignment (GWC 2025)；OEWN adjective hypernym predictor (OntoLex 2025) 与 gold standard (LREC 2026)；HyperDef 作方法背景。
2. 自然语言逻辑化与定义形式化：FOLIO/P-FOLIO (EMNLP/Findings 2024)；Explanation-Refiner (EMNLP 2024)；FoVer (TACL 2025)；Code4Logic (NAACL 2025)；NL2FOL logical fallacy detection (Findings IJCNLP 2025)；数学真实定义 autoformalization 与 proof-assistant feedback (EMNLP 2025)；autoformalization evaluation / FOL closeness metrics (EMNLP 2025)；ACL 2026 Direct Dependency Retrieval；FOL-Traces (Findings EACL 2026)；FOLX-KG (ACL 2026)。
3. 证据与可信推理：Datalog why-provenance (AAAI 2024)；TROVE (ACL 2025) 与 GenProve (ACL 2026) 的细粒度来源关系；AAAI 2025 trustworthy KG reasoning/evidence paths；AAAI 2026 Relink 与 hybrid-KB formal reasoning；EACL 2026 BRINK 等邻近工作。
4. 词汇语义解析与 taxonomy-aware neural semantics：Princeton WordNet GlossTag + ERG (GWC 2023)；Zhang et al., taxonomy-aware semantic parsing (Computational Linguistics 2025)；Forer & Hope definition-augmented scientific-concept hierarchy (TACL 2026)。这些工作不同于 gloss-to-Horn compiler，但限制了对 sense alignment、taxonomy integration 与定义辅助层级推断的宽泛 novelty claim。

## 主题综合与当前定位

“释义自动扩展词汇网络/产生 hypernym 候选”已被直接研究；2025 GWC 工作尤其相关：其从 Tezaurs.lv 释义抽取**义项对**的同义/上下位候选并由三名语言学家评估，且报告自动验证集与较少预处理的人工评审精度有落差，解释包括 sense mismatch、协调结构和派生式定义。2026 LREC 已针对 OEWN 的形容词层级发布 LLM+人工金标准。因此，本项目不能把自动超边、hypernym 候选生成或人工劳动减少本身说成新。

自然语言 FOL 翻译、solver/prover 校验和证明轨迹数据同样是活跃方向。FOL-Traces 说明要测步骤级形式推理而非只看最终标签；FOLX-KG 说明逻辑片段表达力会影响 factual reasoning。项目应从任务本身界定需要的逻辑片段，不能默认现有正 Horn 抽象覆盖量词、否定/情态、定义分支或论元结构。

来源追踪本身也不足以保证可验证性：近期工作区分了 quotation/compression/inference provenance；KG-RAG 在图不完整时可能转而依赖 LLM 记忆。故项目要分别评估 provenance 链是否完整、来源是否在语义上支持规则、以及从缺失规则/知识缺项返回 unknown 的能力。

当前**研究假设**是：一个有价值的贡献可能是把规模化、sense 对齐的释义逻辑化和**带来源的有类型/带方向定义规则**连起来，为蕴含/上下位和失败返回可独立重放证据，并在一致标注协议下定位错误。该假设尚未证明新颖。2025–2026 新增的直接/跨域先例使得贡献空间更窄：AI-WordNet 和 GWC 关系抽取已覆盖 gloss→WordNet 扩展/链接；数学定义 autoformalization 已覆盖 definitions→proof-assistant 表示；ACL/EMNLP 评测研究已覆盖依赖检索、公式质量指标与细粒 provenance。需逐项比对其 scope、逻辑表示、WSD、AND/OR、证据粒度、证明工件、gold 评测及错误分类，不能把不同领域之间“目前没有搜到一个完全相同的组合”写成首创性证据。

## 质量与限制

- 本综述由一位筛选者定向检索；未作双人筛选、引用链穷尽、引用数排序或量化质量评分。
- 会议 proceedings 页面和论文正文是出版信息/方法结论的优先证据；搜索摘要只用于发现，不作最终证据。
- 2026 的已出版 ACL/EACL/LREC 与未核实状态的 OpenReview 匿名稿需分开。VeriCoT 在本轮未能从给定 OpenReview ID 获取可访问的最终 proceedings 记录，所以不把它当已确认的正式会议论文；应后续再核。
- 结论是问题收敛和实验规划，不是 novelty audit，不支持“首次”或比较效果优于现有方法的断言。

## 下一轮检索任务

1. 导出 ACL Anthology、DBLP/OpenAlex、OpenReview 三处结构化检索结果，按 DOI/title 去重并保存候选集与筛选理由。
2. 取得 COLLIE-V、WordNetGraph、GWC 2025、LREC 2026、FoVer、FOL-Traces 的全文/补充材料，逐项填 method-comparison matrix；FOLX-KG 已完成论文 PDF 全文复核，但其代码/数据复现性尚未审计。
3. 顺引用链补检 gloss definition modeling、hypernym extraction、formal semantics for definitions、proof-carrying data / provenance semirings 及 lexical entailment 数据集。

### 2026-10-03 补充：选择性形式化、语义漂移与证明扩展性

为检查 2026 年 ACL/AAAI 主会工作是否改变项目的形式化策略与定位，对 ACL Anthology 和 AAAI OJS 执行以下定向发现查询，并打开官方论文页核对摘要、出版信息和 venue：

```text
site:aclanthology.org/2026.acl-main WordNet gloss definition sense hypernym semantic parsing
site:ojs.aaai.org/index.php/AAAI/article/view 2026 Datalog logic proof provenance language model knowledge acquisition
site:aclanthology.org/2026.acl-long first-order logic entailment autoformalization proof verification natural language
site:aclanthology.org/2026 definition gloss lexical relation WordNet knowledge base
```

官方页面/摘要筛读 3 篇，未在本轮下载或筛读全文；因此以下只记录摘要可支持的结论，不推断未核验的实现细节或完整实验结果：FormalScience (ACL 2026) 提出人机协作科学形式化流程，并报告 FormalPhysics 200 题资源、形式有效性及语义漂移分类；HBLR (AAAI 2026) 摘要描述置信度感知的选择性符号翻译，低置信内容保留自然语言，并用反思机制撤回有损翻译；DeepProofLog (AAAI 2026) 摘要描述神经引导的随机逻辑程序证明搜索及可扩展性研究。它们都是跨领域方法参照，不是 WordNet gloss→Horn 规则的直接先例。

对本项目最实用的设计启发是：把“程序/证明器是否接受”与“规则是否忠实表达原 gloss”分开测；给解析/义项/逻辑化低置信样本保留 `unknown/needs_review` 通道，避免强制编译；按依赖深度、分支数及可搜索证明空间另测证明器成本。上述是对摘要的迁移性解读，不是这些论文已验证本项目可行或优越的证据。三篇的正式出版元数据、摘要筛读范围与纳入边界见 [本轮 JSON 日志](../sources/literature_screening_log_2026-10-03.json)。本轮搜索没有可导出的总命中数/去重候选列表，不报告 PRISMA 计数，也不据未搜到直接结果主张不存在相关工作。

当前已将直接相关的 WordNetGraph、COLLIE-V、GWC 2025、LREC 2026 adjectival hypernymy、FoVer、FOL-Traces、FOLX-KG、GenProve、AAAI 2024 Datalog why-provenance 和 AAAI 2026 hybrid-KB reasoning 放入[逐项对照矩阵](closest_work_comparison.md)。矩阵目前以官方 proceedings 元数据/摘要为主；下一步必须逐篇读全文/附录并记录表示语法、义项层级、规则生成、人审方案、基准划分、证明工件和代码可复现性，之后才能升级 novelty 判断。

### 2026-10-03 后续补充：精选全文核查

这轮不是新的穷尽检索，而是把三篇 2026 ACL/AAAI 方法论文从摘要筛选升级为 PDF 全文核查，并追查 2026 LREC 周边 lexical-alignment 相关工作。查询主题如下；检索入口包括 ACL Anthology、AAAI OJS、Crossref REST 与公开 proceedings 页面：

```text
site:aclanthology.org/2026 WordNet gloss definition hypernym lexical alignment
site:aclanthology.org/2026.acl-long definition autoformalisation semantic drift Lean
site:ojs.aaai.org/index.php/AAAI/article/view/2026 selective symbolic translation confidence logical reasoning
site:ojs.aaai.org/index.php/AAAI/article/view/2026 stochastic logic programs proof scalability
site:aclanthology.org/2026.lrec WordNet synset selection definition hierarchical aggregation
site:aclanthology.org/2026 LDL Open English WordNet hierarchy resource expansion
```

全文筛读 5 篇：FormalScience（ACL 2026）、HBLR（AAAI 2026）、DeepProofLog（AAAI 2026）、Ancient Greek synset-selection（LT4HALA @ LREC 2026 workshop）和 Open English NameNet（LDL @ LREC 2026 workshop）。这是本轮实际读取的精选全文数，不是检索引擎总命中数；前 3 篇为主会，后 2 篇为 workshop，统计时分开标注。详细记录见[全文筛读日志](../sources/literature_screening_log_2026-10-03_fulltext.json)。

方法学结论：

- FormalScience 的 200 项 FormalPhysics 资源由人机协作流程构建，正式代码编译有效率 100%；但对模型自动形式化测试，表现最佳的 agent formal-validity 为 31%。该资源的 LLM-as-judge Logical Preservation / Mathematical Consistency 分别为 72.0% / 72.5%，显著说明 prover 接受不能替代源文本忠实度。对本项目，Horn/Datalog checker 只应验证已输入规则/证明，不可充当 gloss→规则语义 gold。应使用双人 source-span/AST/方向标注；若使用 LLM judge，需盲化、独立评审和人工校准/裁决。
- HBLR 把高置信文本片段转成 FOL、低置信部分留在自然语言，并用 LLM 反思模块回退有损翻译；作者在五个逻辑推理 benchmark 报告选择性方案相对 All-NL/All-FOL 消融的平均改进。部分形式化和 abstention 已是 AAAI 主会先例，不可单独声称新颖。它的 verifier 是 LLM 语义评估而非独立 gold，也不是 WordNet rule provenance 实验；项目应将 `unknown/needs_review` 作为正式输出状态，并在自己的标注集校准。
- DeepProofLog 将 stochastic logic program 的 SLD resolution 映射为 MDP，用动态规划/强化学习来指导证明搜索。它把证明搜索扩展性列为独立问题，但并不替代独立 soundness verifier。若以后扩大本项目 proof search，应把证书重放正确率与搜索成本/成功率分开报告。
- Ancient Greek synset-selection 从 LSJ gloss/同义词组比较 WordNet 局部 hypernym-tree coverage 与 LLM gloss-pair reranking；两位标注者给候选 0–3 分，第三人盲选代表 synset。其 16 个组是小样本，作者明确称结果为趋势；该设置下结构排序整体更稳，LLM reranking 对多义组不稳定。它使 Phase 9/11 的首个词面名词 proxy 需要升级为 sense-disjoint 的结构排序、定义匹配和人工 gold 对照。
- Open English NameNet 通过 Wikidata/Wikipedia 映射和 instance-hypernym 扩充 OEWN named entities，不是 definition parser，但进一步排除了“扩大 OEWN 层级”作为独立贡献的可能。

Crossref 对自然语言 query 返回了极宽泛且不适合当候选全集的 raw totals；OpenAlex 和 Semantic Scholar API 返回 HTTP 429，DBLP 访问被反自动化页面拦截。故没有把这些数作为筛选数，也不报告 PRISMA 数字。本综述仍是单人、定向 scoping review，不是穷尽的 novelty audit。官方出版页/PDF、查询与访问失败均记录在[全文筛读日志](../sources/literature_screening_log_2026-10-03_fulltext.json)。

### 2026-10-03 后续补充：来源契约、round-trip 与 verifier

继续按 provenance-grounded verification、ontology-to-FOL、faithful autoformalization、learned verifiers 和 KG benchmark quality 定向搜索。实际检索式、平台/方法限制、六篇全文筛读记录与纳入边界见[补充 JSON 日志](../sources/literature_screening_log_2026-10-03_late_supplement.json)。此次全文核查 6 篇：5 篇正式 proceedings（Findings ACL 两篇、NeurIPS 三篇）和 1 篇 arXiv 预印本。检索结果没有稳定总命中/去重导出，仍不报告 PRISMA 数字；网页查询未命中某个具体方向不能证明先例不存在。

本轮方法结论是：引用 ID/原文匹配、KG/SPARQL 一致性、NL↔形式表示往返等价、逻辑证明证书重放，分别核验不同属性。尤其 round-trip 可揭示部分漂移，却可能让同一遗漏在两次翻译中一致保留；它不能替代原始 gloss 到规则的语义支持 gold。verifier 的保证也依赖训练/标注假设，例如金标准推理轨迹。后续实验需拆开 sense 对齐、source-span→AST 支持、逻辑化保真、证书重放、NLI 判断和 abstention，而不是汇总成一个“验证成功率”。详细比较见[相关工作](related_work.md)与[最接近工作矩阵](closest_work_comparison.md)。

### 2026-10-03 后续补充：顶会超图读出与逻辑依赖超边的表示差异

围绕依赖图 readout、结构路径证据与高阶图读出，使用官方 ACL Anthology、AAAI OJS、NeurIPS proceedings 做四组定向检索，全文筛读 HyperCoT (ACL 2026)、Cross-Granularity HGRAG (AAAI 2026)、HyperGraphRAG (NeurIPS 2025) 三篇；具体 query 与逐篇边界见[结构化日志](../sources/literature_screening_log_2026-10-03_hypergraph_readout.json)。这些论文分别使用角色化 n-ary 事实超边、实体—段落 incidence 超图、以及 LLM 抽取的 n-ary fact hyperedges；不等同于本项目 head 对多个 AND-body 作 OR 选择的有向 Horn 依赖对象。

可迁移的仅是实验方法：比较 witness/path 深度与数量、路径冗余和删边稳健性、读出时间/内存，并将 hypergraph diffusion/中心性作为非逻辑结构基线。不可迁移的是它们的 QA/link-prediction 分数或路径 trace 的证明语义。项目任何结构读出都要保留原 clause 身份、完整 AND 前提、OR 分支选择并能由 verifier 重放；缺失这些条件的 diffusion/readout 只能用于探索，不能被写成逻辑 entailment 结果。本次是有界定向筛读，无稳定去重候选全集，不是系统综述或 novelty proof。

### 2026-10-03 后续补充：sememe 树、有限语义组件与词汇蕴含

为专门压力测试“释义→85 个原语/语义组件→依赖图→上下位判断”的新颖性边界，对 ACL Anthology 进行 targeted search，并回到 EMNLP 2025 与 ACL 2026 官方 PDF 核对任务、方法、评价及边界。实际查询如下：

```text
site:aclanthology.org/2026 "WordNet" gloss definition hypernym
site:aclanthology.org 2024 2025 2026 dictionary definitions knowledge graph semantic primitives sememe
"sememe" "definition" "knowledge graph" ACL 2025 EMNLP 2026
site:aclanthology.org/2026 "definition" "hierarchy" "knowledge graph"
```

本次从定向候选中选取 2 篇高度相关 ACL proceedings 论文做方法/结果/局限的重点全文核查：Wang et al. (EMNLP 2025) SememeLP 与 Wang et al. (ACL 2026) Structured Sememe Knowledge for Lexical Relation Mining。搜索引擎未提供稳定总命中数或可去重候选导出；不报告 PRISMA 计数。具体筛读字段、DOI、PDF 与纳排边界见[结构化补充日志](../sources/literature_screening_log_2026-10-03_sememe_supplement.json)。

这两篇论文把可能的研究切口明显收紧：EMNLP 2025 从定义预测现成 sememe inventory 的 all/main sememe，并用这些表征做 lexical-KG link prediction；ACL 2026 则通过四阶段流水线预测 sememe 集、主 sememe、树结构及关系类型，论文称自动为 WordNet 构建 sememe trees，并在词汇关系分类及 HyperLex graded lexical entailment 上测试。ACL 2026 报告该自动树平均 gold parent–relation–child 覆盖为 65.9%，表明下游收益不能直接等同逐条结构完全正确。

因此，“从释义提取有限语义原语/组件”“自动构造定义树”或“用定义语义预测 lexical relation/graded entailment”不能单独作为本项目新颖性 claim。较窄的候选差异是把定义解析成可审计的有类型、有方向 Horn 规则，保留 OR 备选与 AND 必要条件、变量/作用域和 sense/version/source-span 来源契约，并区分：机器 checker 相对于输入规则证明什么、输入规则是否忠实于 gloss、以及未知/未覆盖为何发生。后续基线计划新增 SememeLP/SememeLRM；只有在语料、sense 对齐和切分可比时才报告 matched comparison。85 个 frozen basis 是结构标签，不等于论文里的 sememe inventory；如主张两者同义，需提供显式映射和独立语义验证。以上仍是研究假设，不是新颖性结论。

### 2026-10-03 后续补充：WordNet gloss 自举、形容词层级与资源标签有效性

为重新核查本项目最直接的 gloss→WordNet 扩展先例与“WordNet 是否可当语义 gold”，从 ACL Anthology 官方 GWC/LREC 页面与 PDF 做了补充定向检索。代表性查询包括：

```text
site:aclanthology.org/2026 WordNet gloss hypernym definition extraction
site:aclanthology.org/2025 WordNet gloss hypernym definition extraction conference
site:aclanthology.org/2025.gwc WordNet gloss taxonomy expansion human relation intuition
site:ojs.aaai.org/index.php/AAAI 2026 definition ontology logical formalization
site:proceedings.neurips.cc/paper_files/paper/2025 autoformalization formal verification natural language logic
```

本轮对三篇官方全文做方法/结果/限制核查，分别为 GWC 2025 AI-WordNet、LREC 2026 OEWN 形容词 hypernym gold construction，以及 GWC 2025 WordNet—human relation alignment。逐项元数据、PDF 链接、筛读结论见[机器可读日志](../sources/literature_screening_log_2026-10-03_wordnet_source_gold.json)。检索引擎没有稳定候选全集或可靠总命中数；本轮不报告 PRISMA 计数、不称穷尽系统检索，也不作 novelty proof。

AI-WordNet 是必须面对的直接先例：在 PWN 3.0 名词上由 gloss 预测 lexname、synset 与 hypernym，表格报告 hypernym exact hit 64.8% 和平均 taxonomy 距离 1.374；摘要/表与结果段另有 64.5% 的轻微内部差异，引用时应说明所用来源位置。更关键的是，作者评估 8,000 个 Wiktionary 新名词的 cloze distractor 效用而非逐条验证 taxonomy；文中承认一些非 hypernym、甚至方向错误的候选仍能用于 distractor。故“下游好用”“与 WordNet 接近”“原 gloss 支持此关系”是三个不同目标，不能用一个准确率代替。

LREC 2026 的 OEWN 形容词 benchmark 提供 3,836 对关系，并采用多模型分层、人类校准和方向性错误分析；但其多数候选通过小规模双专家校准后的阈值自动接受，并非对最终全集逐条双盲裁决，覆盖也限于 1,148 个高频、已对齐形容词。可以把它作为 adjective-only lexical relation 外部切片，不能外推为全 POS gloss→logic gold。相应地，GWC 2025 的 WordNet—human elicitation 工作发现资源缺失/不匹配关系广泛存在、taxonomy path length 不能稳定代表人类 hypernym 直觉；但它属于 lemma/关系层的直觉实验，也不能据此把 WordNet 全面判错。方法协议因此要求分别报告资源相对的 `OEWN relation agreement`、人类 lexical-relation judgment 与逐条 `gloss-span directional support`，不能相互替代。

这轮证据收窄了后续实验：AI-WordNet 应成为匹配输入范围后可复现的直接 baseline；LREC 形容词数据可用于受限外部校验；人类直觉实验支持给 WordNet 边加独立语义标签，而不应把其当唯一金标准。具体哪些子集/数据在许可与 sense/POS/split 上可复用，尚待逐项核验；所有性能数字仍是来源论文报告，非本项目复现。

### 2026-10-03 后续补充：ACL 2026 KG refinement 的 source-grounding 评测

对 ACL Anthology 中 2026 年 WordNet/definition/lexical semantics 和 source-grounded KG extraction 结果作定向复核，全文阅读 Kim et al., [GraphRefine](https://aclanthology.org/2026.acl-long.1353/)；确切查询、核验项和局限见[JSON 筛读日志](../sources/literature_screening_log_2026-10-03_graphrefine.json)。该论文用三人多数表决检查 80 个生成 KG、共 658 条 triple，报告一致性 κ=0.67，并将错误分成事实正确性与表示质量层面。此项支持我们把 source support、实体/sense 错配、span/表示质量分别计量，并同时报告修正与覆盖；不支持把一般 KG refinement 等同于词义定义逻辑化。GraphRefine 的标签不是必要/充分条件规则 gold，且其 factualness judge 使用 LLM，因此项目仍需盲化的人工 gloss-support 标签作为独立参照。

### 2026-10-03 补充：图上逐步核验与中心性读出线索

针对“图结构是否能帮助读出核验信息”补查 ICLR 2026 官方 proceedings，并交叉查看 ACL Anthology、AAAI OJS、OpenReview 与 arXiv 的定向发现结果。具体查询、筛读与非纳入项见[结构化日志](../sources/literature_screening_log_2026-10-03_graph_verification.json)。对新发现的 VoG 读取 ICLR 正式论文全文与附录：其对象是已有 Freebase/Wikidata factual triples，任务为三类 KGQA；模型以 LLM/冻结 DeBERTa 对比推理步骤和检索事实，按需修订计划。作者把节点中心性/子图连贯性作为 future work，而不是已验证的性能增益。此前已收录的 AAAI 2026 Hybrid KB 与 AAAI Spring Symposium labeled-logic 工作只列为已筛过、不重复计数。

这给当前超图分析提供的是实验假设而非结论：可在 sense-disjoint gold 上测试 AND/OR-aware clause/witness 描述符是否比有损 simple-graph 投影特征更能预测 source-support 错误类别、选择性拒答收益或人工核查/证明成本。VoG 的 KGQA 指标不可移作本项目 baseline 分数；没有人工 gold 时不拟合或宣称这些图特征具备语义预测力。本轮仍是单 reviewer 定向补充，网页发现结果没有可导出的候选全集或一致 hit counts，不报告 PRISMA 数量，也不据此证明研究新颖。


2026-10-05 形式化与证明邻接补充：全文筛读 Zheng et al., *Enhancing Transformers for Generalizable First-Order Logical Entailment*（ACL 2025 Long Papers）。论文以参数化知识图谱查询评估 FOL 式推理，把未见知识与未见组合查询类型作为两个 OOD 轴；此设计可启发 sense/规则知识切分与 AND/OR 组合切分，但不涉及 WordNet gloss、claim-level source support 或 proof replay。未复现代码/数据，不把 KGQA MRR 用作本项目匹配基线。详见[形式化与证明筛选日志](../sources/literature_screening_log_2026-10-04_formal_nli.json)、[相关工作](related_work.md)和[逐项对照](closest_work_comparison.md)。ACL 固定候选框精确 URL 对账现为 47/1,270 有日志匹配，全文 28、定向章节 7、摘要/元数据 12；其余 1,223 无日志匹配。仍属单人定向筛查，不是穷尽综述或新颖性证明。

2026-10-05 NLI 隐含蕴含标注维度补充：全文筛读 Havaldar et al., *Entailed Between the Lines*（ACL 2025 Long Papers）。INLI 将 entailment 分成 explicit/implied；作者对 200 条分层样本做三人标注，报告 κ=.711、相对构造标签多数一致率 .935，但全量数据未全人工审查且主要是对话/社会语境。将其用于提出 `inference_basis` 次级维度和外部知识/语用挑战切片；不把 implied inference 等同于 gloss-span support，也不把 INLI 作 WordNet gold 或匹配 baseline。已更新[标注协议](annotation_protocol.md)、[方法与评测](method_and_evaluation.md)、[相关工作](related_work.md)、[逐项对照](closest_work_comparison.md)及[机器日志](../sources/literature_screening_log_2026-10-04_formal_nli.json)。ACL 固定候选框现为 48/1,270 精确 URL 匹配，全文 29、定向章节 7、元数据/摘要 12、无匹配 1,222。

2026-10-05 TACL FoVer 全文筛读：核读 Pei et al. 的 [FoVer](https://aclanthology.org/2025.tacl-1.61/) 正式 20 页 PDF。系统将 LLM 生成的 Python/Z3 claims、定义、可选 common knowledge 交给 SMT 可满足性验证，区分 executability 和可执行样例准确率/总准确率。实验规模包括 ProofWriter 200、FOLIO validation 203、REVEAL MuSiQue/StrategyQA 各 120 条；加入常识在部分配置提高准确率，但可能冲突、降低执行率。其主要边界是形式校验针对 LLM 生成的逻辑和额外假设，不校验它们是否来自原文。已在 `datalog_checker` 和 `verified_reasoning_pipeline` 中实现事实 partition 标记、source_only 过滤、fact-leaf 证书回放和组合路由限制；分区标签仍是调用方声明，尚无真实 gold 或独立语义审核。ACL 固定候选框仍为 48/1,270 URL 匹配，全文 30、定向章节 7、元数据/摘要 11、无匹配 1,222。机器记录见[形式化与证明筛选日志](../sources/literature_screening_log_2026-10-04_formal_nli.json)。

2026-10-05 proof 输入来源分区实现：FoVer 全文核查指出 LLM 补入 common knowledge 会改变形式证明的前提集合。现为 `datalog_checker` 增加可回放的 `knowledge_partition` fact provenance（`source_assertion` / `resource_fact` / `external_assumption`；缺失视作 `unclassified`）；`verified_reasoning_pipeline` 增加默认兼容的 `knowledge_scope=all_inputs` 和严格 `source_only` 策略。后者只保留有来源文档的显式 source assertions；组合 NLI 路由只在证书实际使用的每个 fact leaf 都仅属 source_assertion 时接受来源支持门。标签属于调用方声明，回放只保证分类未漂移，不证明断言语义为真；未运行测试套件，仍需 synthetic regression 和人工审核 gold 的后续验证。说明见[逻辑验证文档](logic_verification.md)。

### 2026-10-05 ACL Long Papers：SLR 合成 Horn 基准

最新补查 ACL 2026 主会发现并定向核读 [SLR](https://aclanthology.org/2026.acl-long.16/) 正式 PDF 的 rule/background synthesis、symbolic validation、evaluation/error analysis 与 limitations 部分。SLR 把 ground-truth definite clause、可执行 validator、正负样例和模型输出绑定，约 19k prompts / 20 个复杂度等级；作者明确将当前实验限定于干净、合成、单规则 ILP 与 perfect symbolic judge，真实语义噪声/歧义及多规则交互仍待研究。对本项目的落点是合成 checker stress test 和复杂度控制，不是 gloss-to-rule gold，也不是匹配 benchmark。条目和逐项边界见[机器日志](../sources/literature_screening_log_2026-10-05_acl_slr.json)。

### 2026-10-05 跨顶会补查：typed hyperresolution 中的 LLM entailment

由 ACL/ICLR 跨会检索补查到 ICLR 2025 [LLM-TH](https://proceedings.iclr.cc/paper_files/paper/2025/file/67496dfa96afddab795530cc7c69b57a-Paper-Conference.pdf)，并对官方 PDF 的类型化理论归结、LLM entailment 排序、实验数据、typed-search ablation 与评测范围做定向筛读。它用 MNLI 微调模型估计谓词/类型蕴含概率并参与 typed hyperresolution，也允许 commonsense 推断填补 KB 规则；因此“LLM/NLI + hyperresolution/proof search”不能作为新颖性 claim。项目提出的 `source_only` 证书路由须与之明确区分：模型分数只能排序候选而不能授权无来源事实；即使证书可重放，gloss 语义支持仍由 sense-linked span 与人工 gold 单独评测。论文逐项证据和手工 reasoning-score 仅检查 20 个回答的范围边界见[结构化筛读日志](../sources/literature_screening_log_2026-10-05_iclr_llm_th.json)。

2026-10-05 新增近邻：定向筛读 ACL Anthology NALOMA 2026 workshop 论文 [Neural DTS](https://aclanthology.org/2026.naloma-1.2/) 正式 PDF。该系统由 WordNet synset hypernym 边训练 hyperbolic entailment cones，并在 Japanese DTS/NLI prover 搜索时动态加入 lexical IS-A axioms。集成评估只有 20 条 upward-monotonicity proof-of-concept；另有不同任务的 standalone relation F1 与 OOV-filtered MED pair accuracy，不能合并或迁移。它收窄了“WordNet taxonomy + neural lexical entailment + proof search”的可主张空间；这是高度相关 workshop 先例而非主会结果，也不处理逐 gloss span 支持和 AND/OR 规则编译。逐项实验边界见[机器筛读记录](../sources/literature_screening_log_2026-10-05_neural_dts.json)。

### 2026-10-05 ICLR 2026 accepted proceedings：WordNet 层级与逻辑概念组合

针对“WordNet 上的层级与逻辑组合是否已被研究”，查询并核对 ICLR 2026 官方 proceedings 页面和正式 PDF：

```text
ICLR 2026 WordNet hierarchy logical composition lattice representations
site:proceedings.iclr.cc/paper_files/paper/2026 WordNet concept lattice meet join
site:openreview.net ICLR 2026 WordNet logical representation entailment
```

从官方 proceedings 选中 Xiong 的 *The Lattice Representation Hypothesis of Large Language Models*，定向检查 16 页论文中的框架、WordNet 数据构造、属性/偏序与 meet/join 结果及复现声明。该论文建立了 embedding-geometry/FCA lattice 在 WordNet 五个子层级上的概念组合先例，直接压缩“WordNet 上建模层级和逻辑组合”的宽泛 novelty claim。区别是它从对象/属性嵌入推断偏序与 meet/join，而非从原始 gloss 抽出 sense-linked typed Horn rules；其对象属性由 GPT-4o 构造，不能代替独立 source-support gold。逐项来源、结果分母和局限见[机器日志](../sources/literature_screening_log_2026-10-05_iclr_lattice_and_kdd_subspaces.json)。

后续版本/会议信息校正（覆盖本节初筛时的未确认状态）：arXiv v2 将该工作改题为 *Native Hierarchical and Compositional Representations with Subspace Embeddings*，明确列于 KDD ’26 Proceedings Volume 2（2026-08-09 至 13）并提供 ACM DOI 10.1145/3770855.3817808。此前题为 *Native Logical and Hierarchical Representations with Subspace Embeddings* 的 ICLR 投稿是同一 arXiv 记录的早期版本，不应另计为未录用稿。现已按 KDD v2 全文/附录更新方法、WordNet/HyperLex/SNLI/组合基准与限制；具体数值和边界见[机器筛读日志](../sources/literature_screening_log_2026-10-05_iclr_lattice_and_kdd_subspaces.json)。这是单 reviewer 定向筛读，不是跨库穷尽综述或 novelty proof。
## 2026-10-06 ACL 2026 逻辑推理近邻补筛

从固定的 ACL Anthology 2026 v2 候选导出中，按标题/摘要检索 formal reasoning、logical entailment、solver、ontology、lexical relation 与 definition 等主题，再对三篇任务重叠较明显的论文核读官方 PDF 的任务、方法、实验和限制：EACL 2026 Adaptive LLM-Symbolic Reasoning、ACL 2026 OntGQA、Findings of ACL 2026 LoReFact。逐篇范围及不可比项见[结构化筛读日志](../sources/literature_screening_log_2026-10-06_logic_reasoning.json)。候选池不是跨库穷尽检索；未下载或复现实验，不由此推断项目效果、新颖性或筛选召回率。

同一候选池另发现 Findings of ACL 2026 的 FoVer，与形式证明/逐步验证更直接相关。核读官方 PDF 中形式验证定义、Z3/Isabelle 逐步标注、40K 数据构造、评测、讨论和限制；详见[机器日志](../sources/literature_screening_log_2026-10-06_formal_verification_prm.json)。该工作输入已形式化 premises，因此对项目的直接启示是分别审计原文到形式前提的来源忠实度、形式步骤正确性和证明证书回放；不把 PRM 迁移分数当作这些任务的替代指标。

### 2026-10-06 ACL Anthology 2021–2022 WordNet/gloss 词族筛查

在冻结候选文件 `acl_anthology_candidates_2026-10-05_v2.json` 上，对 `wordnet_gloss_lexical_relations` 查询族中 2021–2022 年仍处于 `pending_title_abstract_screen` 的 33 条记录完成题名/摘要筛查。决策为 direct neighbor 4、adjacent 10、background 3、exclude 16；7 条标为优先全文核查。锁定输入文件 SHA-256、逐条原始 ACL Anthology ID、官方页面链接、理由、纳排定义及局限的账本见[结构化日志](../sources/literature_screening_log_2026-10-06_acl_wordnet_direct_2021_2022.json)。

这是固定单库/单词族/两年切片的单 reviewer 筛查。保留仅指全文复核候选，不等于系统综述纳入。7 条优先候选现均已完成官方 PDF 定向核读；逐篇方法、结果、计数差异和任务边界均记录在同一日志。其余 10 条保留项尚未做同等深度复核；本轮没有代码/数据复现，不估计查询召回率，也不能支持新颖性结论。


### 2026-10-06 ACL Anthology 2020 年 WordNet/gloss 词族筛查与近邻复核

对固定候选 v2 中该词族的 25 条待筛记录完成题名/摘要决定：direct neighbor 2、adjacent 12、background 4、exclude 7。逐条决定、理由和输入 SHA-256 见[结构化日志](../sources/literature_screening_log_2026-10-06_acl_wordnet_direct_2020.json)。两篇直接近邻已核读官方 PDF：COLLIE-V（WordNet gloss→义项相关 ontology/AND-OR entailment axioms）和 BMEAUT（Wiktionary→4lang graph→lexical entailment）。前者是重大 novelty collision，后者是必须纳入的 graph baseline 候选。详细结果和范围限制已加入 closest-work、related-work 及评测基线。

这是单 reviewer、ACL 单库词项候选筛查，不是完整系统综述；论文/系统分数不可跨任务直接移作项目结果。候选差异不能据方法描述宣称新颖，须在共同 sense-linked gold 上作 matched comparison。


## 2026-10-06 框外命中与检索覆盖审计

定向全文核读发现 [Logic Haystacks (EACL 2026)](https://aclanthology.org/2026.eacl-short.3/) 与长上下文证据定位/困难干扰项有关，但它不在冻结的 `acl_anthology_candidates_2026-10-05_v2.json` 中。该发现来自筛查 Unigram-FOL 后针对 long-context evidence retrieval、proof-directed evidence attribution 和 distractor robustness 的后续定向跟进，而非原查询框内命中。候选文件 SHA-256 仍为 `609fdbdf439310b8aaa72e5438d88f04924f6df6ca7053dc155a9f9bce5e505d`；不修改原文件、不回填既有 ACL 精确 URL 对账分子或分母。此一漏检说明既有关键词框对该主题覆盖不足，但不能据单例估计总体召回率。后续搜索应把 long-context reasoning、evidence retrieval/attribution、hard distractors、minimal/necessary-sufficient evidence 等查询家族加入增补检索，并与原冻结候选框结果分开报告。筛读细节见[机器日志](../sources/literature_screening_log_2026-10-06_logic_haystacks.json)。


## 2026-10-06 多证据检索与证据评价的补充词族

继 Logic Haystacks 框外发现后，新增定向检索词族：`multi-evidence retrieval/reasoning`、`evidence set selection`、`evidence tree/search`、`evidence evaluation metric`、`source attribution`，并优先查 ACL Anthology 官方 proceedings 和 TACL。该增补发现 ACL 2025 ETS、COLING 2025 Counting-Stars 和 TACL 2026 Ev2R；三项均不在原冻结候选文件，故不加入固定框 reconciliation 计数。前两篇核读官方全文，Ev2R 仅核对官方元数据/摘要，筛读日志明确记录层级。此结果证明现有查询族对组合证据检索/评价的覆盖不足，但不能估计整体召回。后续系统筛查需将扩展词族的检索源、日期、去重规则和候选清单独立冻结，再报告分框计数与筛读深度。详见[机器日志](../sources/literature_screening_log_2026-10-06_evidence_retrieval_supplement.json)。

## 2026-10-06 ACL Anthology 查询词族扩展与 v3 冻结

因 Logic Haystacks、ETS、Counting-Stars 等论文经后续定向检索发现，候选生成器 `src/analysis/search_related_work_acl.py` 新增 `long_context_evidence`、`multi_evidence_selection`、`evidence_evaluation_attribution` 三个 AND/OR 词族，并重新下载官方 ACL Anthology BibTeX+abstract export。导出未压缩 BibTeX SHA-256 与 v2 相同（`045b66593e91fb24d71a14917c41ccecb14278dfcb6c8069b1bea1bfa188df27`），压缩流 SHA-256 为 `d9620aa9651f86bfb5177b3825adda20b18621239a696062d15c8befb1c7573e`；新增三族命中分别为 11、99、24（预去重合计 134），全词族合并去重后候选由 v2 的 1,634 增至 v3 的 1,747。新发现的 Logic Haystacks、ETS、Counting-Stars 与 TACL Ev2R 均进入 v3；前三篇精确匹配全文日志，Ev2R 匹配摘要级日志。它不在 v2，但由新增 evidence evaluation 词族被 v3 召回。

原始候选保存在 [`v3 raw`](../sources/acl_anthology_candidates_2026-10-06_v3.json)，初始逐 URL 对账副本为 [`v3 reconciled`](../sources/acl_anthology_candidates_2026-10-06_v3_reconciled.json)。初始副本的 307/1,747 匹配反映增量筛读前的结构化日志状态（全文 40、定向章节 21、摘要/元数据 94、深度未明 152）。其后对 v3−v2 的 113 条差分候选逐篇筛查并写入[增量筛读日志](../sources/literature_screening_log_2026-10-06_acl_expanded_delta.json)：新增题名/摘要决定 109 条（相邻 68、背景 33、排除 8），4 条复用既有更深筛读。随后对 2026 年 `definition_to_formal_logic` 词族的 24 条待筛记录完成题名/摘要筛查（相邻 13、背景 4、排除 7），并对 10 条优先项作官方 PDF 定向章节复核（方法、评测与局限段落；不称全文/附录穷尽阅读），见[结构化日志](../sources/literature_screening_log_2026-10-06_acl_formalization_2026.json)。后续字段规范化复算版 [`v3 screened normalized`](../sources/acl_anthology_candidates_2026-10-06_v3_screened_normalized.json) 有 1,747 条，其中 443 条匹配日志（全文 56、定向章节 31、摘要/元数据 204、深度未明 152），另 1,304 条待题名/摘要筛查；旧 `v3_screened.json` 保留为修正前历史快照。对账匹配只表示日志存在，不等于相关性纳入；待筛亦非排除。这不是最终纳入数或召回率。v1/v2 候选与历史对账未改。筛读仍属单人、定向 scoping。各文件哈希、词族定义/计数及复算命令见[机器审计](../sources/acl_query_expansion_audit_2026-10-06.json)。

后续对 `definition_to_formal_logic` 中 Liu 的 Code4Logic（NAACL 2025 Long Papers）作了一篇官方 PDF 全文定向筛读，日志见[结构化记录](../sources/literature_screening_log_2026-10-06_code4logic.json)。其 Python 代码渐进生成 NL→FOL 并用于下游 prover/逻辑任务，故宽泛的 code-mediated NL→FOL→prover 不能单列为创新；论文的 Logic Equivalence 和下游结果不等于 gloss-span semantic-support。筛读后当前 [`v3 screened`](../sources/acl_anthology_candidates_2026-10-06_v3_screened.json) 为 441/1,747 条精确 URL 日志匹配（全文 54、定向章节 31、摘要/元数据 204、深度未明 152），1,306 条待题名/摘要筛查。匹配计数仅反映现有日志命中；该单篇筛读不代表全体候选已筛，也不构成纳入数、召回率或新颖性证明。机器审计中的 v3 screened 哈希已随此衍生快照更新，v1/v2、v3 raw 和预增量 reconciled 历史快照保持原样。

另对 Thatikonda et al. 的 FOL closeness metrics（Findings EMNLP 2025）作官方 PDF 全文筛读，记录见[结构化日志](../sources/literature_screening_log_2026-10-06_fol_closeness_metrics.json)。其受控量词、否定、AND/OR、谓词/变量扰动说明公式评价指标对不同错误类型的敏感度不一；主要排名对齐依据 LLM judge，非大样本人类裁决，故只能指导公式层 mutation diagnostics，不能充当 gloss semantic-support gold。当前 [`v3 screened`](../sources/acl_anthology_candidates_2026-10-06_v3_screened.json) 更新为 442/1,747 条精确 URL 日志匹配（全文 55、定向章节 31、摘要/元数据 204、深度未明 152），1,305 条待题名/摘要筛查；机器审计哈希同步更新。该定向单篇筛读不改变有界、单人 scoping 的性质。

对 Saparina & Lapata 的 [Disambiguate First, Parse Later](https://aclanthology.org/2025.findings-acl.863/) 作官方 PDF 全文定向筛读，记录见[结构化日志](../sources/literature_screening_log_2026-10-06_saparina_parse_later.json)。其先生成并补全 text-to-SQL 问句的多种自然语言解释，再逐项执行 SQL semantic parsing；因此“先处理歧义、再形式化”和多解释 coverage 已有 Findings ACL 2025 先例。其任务依赖数据库 schema 和执行结果，不是 WordNet WSD、gloss support 或 Horn proof。筛后当前 [`v3 screened`](../sources/acl_anthology_candidates_2026-10-06_v3_screened_normalized.json) 为 443/1,747 条精确 URL 日志匹配（全文 56、定向章节 31、摘要/元数据 204、深度未明 152），另 1,304 条待题名/摘要筛查；机器审计哈希已同步。这仍是单人定向 scoping，不支持召回率或新颖性结论。

本批 2026 候选突出自然语言要求/论证到优化模型、PDDL/FOL/Lean/Hoare 合约的跨领域形式化，以及 NLI 中的外部 prover；这些方向有助于限定“NL→形式对象”“形式执行/证明核验”已有的广义先例。筛查只依据官方题名/摘要，不足以比较规则方向、义项身份、gloss span 绑定或证明工件，也不构成 WordNet 任务的 matched baseline。全文优先名单应先按与 sense-linked gloss、方向性语义支持及证明 replay 的真实接近度排序。

## 2026-10-06：最近邻研究工件可复现性

针对 Greco et al. (Findings EMNLP 2024)、AI-WordNet (GWC 2025) 与 Augello et al. (LREC 2026) 做官方论文材料和作者链接仓库的定向检查。Greco 的 ACL Anthology 页面只列论文 PDF，未在官方材料中找到代码、数据或预测输出，因此应作为方法参照/基线规格，而非已可原样重跑的结果。AI-WordNet 指向公开的 [wordneter/dataset](https://github.com/wordneter/dataset)，检查到仓库有数据文件但未声明许可证，且未见训练源码。LREC 2026 的[正式 proceedings 页面](https://lrec.elra.info/lrec2026-main-293)标示无补充材料；论文所链接的[作者仓库](https://github.com/lorenzoaugello/hypernymy)含 CSV、RDF 和 prompt，但没有声明许可证或生成源码。公开可访问不等于获准复用；不导入或分发数据，直至完成许可/来源审核。LREC 数据可作 adjective lexical-relation 外部切片候选，但不是 gloss-span source-support gold。逐项证据见[机器可读工件审计](../sources/literature_artifact_availability_2026-10-06.json)。

其官方 PDF 随后完成定向章节核读（引言/相关工作、操作化准则、数据构建、标注评测、错误分析和限制）。该研究经 sense-linked OEWN 形容词定义生成上下位候选，确立了定义条件下预测 lexical relation 和 hybrid human validation 已有先例；其中摘要所述 consensus 87% 指按重复生成规则保留的比例，并非对整个 consensus set 的逐条人审准确率。majority 集阈值 P=.84/R=.72 仅报告于双专家随机 100 对样本；不能外推为整个 1,381 对集合的直接人工 gold 指标。完整方法细节和项目边界见[定向全文筛读日志](../sources/literature_screening_log_2026-10-06_augello_lrec2026_targeted_fulltext.json)。截至当前 ACL v3 规范化固定快照，2026 年 WordNet/gloss 词族 9 条和 `definition_to_formal_logic` 词族 33 条均已有精确 URL 日志匹配，无遗漏的待筛行；这是本次小词族核对结果，并不意味着 1,747 条 ACL 候选都已筛读，也不提供候选召回率或新颖性证明。此前对账脚本未识别三条 per-record `screening_depth` 字段，已纳入 parser 并重新生成派生快照；详细文件 SHA-256 见机器审计。

## 2026-10-06 框外 ACL 2026 Findings 定向补充

在 ACL Anthology 官方站点对 `missing premise`, `grounded reasoning`, `clarify and pause` 作定向检索，发现 Qiu et al. 的 Findings ACL 2026 [Pause or Fabricate?](https://aclanthology.org/2026.findings-acl.1155/)，对官方 22 页全文及附录的数据构造、主要实验和局限作单篇筛读。该文不在冻结 ACL v3 导出中，作为框外补充记录，不能回填候选数或据此声称检索召回完整；筛读边界见[结构化日志](../sources/literature_screening_log_2026-10-06_gril_findings_acl2026.json)与[综合补充](latest_related_work_addendum_2026-10-06.md)。
## 2026-10-06 框外 ACL Findings：SLKD 逻辑结构密度补查

从 ACL Anthology 2026 Findings proceedings 的相关词检索到 Bi et al., [Logical Structure as Knowledge](https://aclanthology.org/2026.findings-acl.436/)，定向核读官方 22 页全文中的逻辑分解、SLKD 公式、基准实验、局限与 artifact 条款。该文不在冻结 ACL v3 导出中；按框外近邻记录，不回填候选数或召回审计。论文将 LLM 抽取的谓词/常量/公式、单条推导链的操作符和嵌套深度组合成训练数据的 reasoning-potential proxy；它没有评测 WordNet sense、gloss span 支持或可重放来源证明。详细边界见[结构化日志](../sources/literature_screening_log_2026-10-06_slkd_findings_acl2026.json)。
# 2026-10-06 固定 ACL v3：2025 formalization/rule 邻居优先全文抽样

在 1,747 条 v3 normalized 候选中，按 `definition_to_formal_logic` query family 与 2025 年筛出高优先自然语言规则/自动形式化项，定向核读四篇：RuleArena、LTRAG、MASA、NL2Lean/ReLean。候选文件 SHA-256 为 `9b5539632bea103ebdbf9acda27c9b23e58d8476e4b0b2a72ae045de5a37321f`；[结构化筛读日志](../sources/literature_screening_log_2026-10-06_acl_2025_formalization_rule_neighbors.json)记录官方页/PDF、review scope、指标与边界。四篇均是 adjacent cross-domain works，没有 gloss-span support 命中；这不构成该年 query family 的完整筛查，也不代表对全集的召回判断。v3 冻结候选及既有计数不变，只有精确 URL 日志 reconciliation 后才更新 screened-depth 对账。

### Phase 30：ACL Anthology v3 的 2025 definition-to-formal-logic 词族

以 `sources/acl_anthology_candidates_2026-10-06_v3_screened_normalized.json` 为冻结候选框（SHA-256 `9b5539632bea103ebdbf9acda27c9b23e58d8476e4b0b2a72ae045de5a37321f`），在 phase29 精确 URL 对账副本中筛出 2025 年 `definition_to_formal_logic` 族尚无日志匹配的 37 条，按官方候选题名/摘要逐篇记录决定与理由。23 条保留为方法邻接、6 条为背景、8 条排除；对 QuaSAR、Tomita et al. 的 CCG/DTS 系统、Skandalis et al. 的 French NLI 和 Zamborlini et al. 的 OntoLex-Lemon 扩展，另查官方 PDF 的方法、数据/评价和限制相关章节。逐条内容在[筛读 JSON](../sources/literature_screening_log_2026-10-06_acl_2025_definition_to_formal_logic_full_screen.json)，全局 URL/深度对账在[phase30 JSON](../sources/acl_screening_reconciliation_2026-10-06_phase30.json)。

本轮结束后，该固定年份/词族的 52 条全部有精确 URL 日志匹配；其中新增项 33 条只有题名/摘要层级，4 条是定向章节，而非穷尽全文。全局 v3 候选框 1,747 条中，484 条有日志匹配、1,263 条仍待题名/摘要筛查；深度为全文 56、定向章节 39、摘要/元数据 237、未明 152。计数只表示日志与候选的精确 URL 对账，不等同相关性纳入数、召回率或系统综述进度。此次筛查没有复现论文结果，也不支持新颖性结论。

### Phase 31：ACL Anthology v3 的 2025 NLI、逻辑与证明词族

基于冻结候选框的 `nli_logic_proof_verification` 族，对 phase30 快照中尚未匹配的 55 条 2025 记录逐篇按官方题名/摘要决定：24 条邻接、12 条背景、19 条排除。对 PGR、Minimal Evidence Groups、SC-Energy、Local Look-Ahead、HalluTree、SemQA 六篇官方 PDF 定向阅读相关方法、评价和限制章节。见[结构化筛读 JSON](../sources/literature_screening_log_2026-10-06_acl_2025_nli_logic_proof_full_screen.json)和[phase31 reconciliation](../sources/acl_screening_reconciliation_2026-10-06_phase31.json)。

该 2025 query family 共 67 条，当前均有日志匹配；本轮新增的 55 条仅六篇做了定向章节阅读。全局 v3 有 539/1,747 条 URL 匹配、1,208 条待筛，深度：全文 56、定向章节 45、摘要/元数据 286、未明 152。日志匹配不是相关性纳入、召回率或系统综述完整度。HalluTree 表明 claim tree + 自然语言推理链已有先例；相关差异只能落在 sense/span-bound source-only proof 和独立语义 gold 上，仍须 matched baseline 实验验证。


## 2026-10-06 Phase 32：ACL v3 的 2024 definition-to-formal-logic 词族

以固定候选输入（SHA-256 `9b5539632bea103ebdbf9acda27c9b23e58d8476e4b0b2a72ae045de5a37321f`）及 phase31 exact-URL 副本为界，对 2024 年该 query family 中剩余 24 条逐篇作官方题名/摘要判断：13 条方法邻接、6 条背景、5 条排除。另对 Consistent Autoformalization、Formal Languages for KBQA、Explanation-Refiner、FOLIO、P-FOLIO、TabVer 六篇官方 PDF 的任务/方法/评价/局限章节定向核读；这些不等同于完整全文或附录穷尽复核。机器日志记录每条官方 URL、原摘要、筛查理由和阅读深度：[Phase 32 JSON](../sources/literature_screening_log_2026-10-06_acl_2024_definition_to_formal_logic_full_screen.json)。

该词族总计 28 条均有精确 URL 日志匹配；固定 v3 全局对账增加至 563/1,747，剩余 1,184 条待题名/摘要筛查，深度为全文 56、定向章节 50、摘要/元数据 305、未明 152。定向 PDF 资料强化了三条边界：形式检查不能独立证明自然语言到公式的忠实度；人工自然语言证明链和逻辑数据集不是 sense-linked gloss-support gold；span 对齐/自然逻辑 proof 的结构化表格工作不能直接当作词典定义上的 Horn 规则 baseline。候选对账只证明日志 URL 存在和显式筛查深度，不是相关性纳入数、系统综述完成度、召回率或新颖性证据。阶段副本见[phase32 reconciliation](../sources/acl_screening_reconciliation_2026-10-06_phase32.json)。


### Phase 33：2026 formal NLI 与 proof-tree 高优先项

从 phase32 对账副本中按任务接近度选取两篇 2026 候选，定向核读其官方 PDF 的方法、评价和限制章节，逐篇记录在[筛读日志](../sources/literature_screening_log_2026-10-06_acl2026_proof_and_formal_nli.json)。这不是 2026 年族内普筛。新增 exact-URL 日志记录后，固定 v3 计数变为 565/1,747，待筛 1,182；深度：全文 56、定向章节 52、摘要/元数据 305、未明 152，见[phase33 对账](../sources/acl_screening_reconciliation_2026-10-06_phase33.json)。新增工作限制通用 proof-tree 生成、交互式 AND/OR 分支探索和 prover 查询导出作为单独新颖性主张；任务差异不能证明剩余 source-span 语义差异新颖。候选 SHA 不变，URL 匹配数不是相关性纳入数、召回率、系统综述完整度或新颖性证据。
### 2026-10-06 跨会场摘要级 ICML 补查

为覆盖 ACL 候选框以外的近期顶会背景，通过官方 PMLR 页面定向查看 ICML 2026 两篇可能相关的工作：图谱式推理验证与形式验证驱动代码生成。只记录元数据和摘要层事实，未访问 PDF 内容、代码或数据；此补查不并入 ACL Anthology v3 候选数或 reconciliation。逐篇任务边界与筛查深度见[结构化日志](../sources/literature_screening_log_2026-10-06_icml2026_verification_supplement.json)。
### 2026-10-06 NeurIPS 2025 reasoning graph / KG constraint 补查

在 ACL Anthology v3 固定候选框外，通过官方 NeurIPS proceedings 页面检索 NeurIPS 2025 main-conference reasoning graphs、graph verification、knowledge-graph constraint/path verification 主题；优先核读 *Topology of Reasoning* 与 *Deliberation on Priors* 的官方 PDF 方法、评测和局限段落。此次为两篇目标性筛读，不是 NeurIPS 全集导出、系统检索或召回率估计；不回填 ACL 计数。结构化筛查记录见[日志](../sources/literature_screening_log_2026-10-06_neurips2025_graph_verification.json)。

## 2026-10-06 IJCAI 2026 逻辑归纳与 textual-entailment 搜索

### 2026-10-07：IJCAI 2026 全目录标题级复查

Phase 40 之后，针对官方 [IJCAI 2026 proceedings](https://www.ijcai.org/proceedings/2026/) 的可见目录文本补查 `WordNet`、`lexical`、`definition`、`synset`、`hypernym`、`hyponym`、`dictionary`、`entailment`、`Horn`、`proof tree`、`rule induction`、`NLI` 和 `gloss`。可见的 textual-entailment 与 rule-induction 标题命中对应已筛 VANESSA/NRI；`Gloss-driven Indian Sign Language Production System` 是语境不同的标题级命中。没有发现额外显眼近邻。Horn 的字符串搜索还命中作者姓氏，作为噪声排除。

这只是全目录标题/元数据层面的补漏，不检查所有摘要和全文；不同术语、未在标题中体现任务的相关工作可能未命中。不得据此声称 IJCAI 全集无相关工作、检索穷尽或项目新颖。逐词记录与边界见[Phase 42 机器日志](../sources/ijcai2026_title_screen_audit_2026-10-07.json)和阶段报告。

- **索引：** IJCAI 2026 官方 proceedings。
- **定向 query：** `logical rule induction`、`textual entailment proof tree`、`proof tree entailment`，在 IJCAI 官方 proceedings 范围内检索。
- **筛读：** 两篇官方 PDF 的任务/方法、规则表示、评估设置和限制章节：NRI（Main Track）与 VANESSA neuro-symbolic QA（Demo Track）。
- **判断：** NRI 是 proposition/tabular DNF induction 邻居；VANESSA 是自然语言文本蕴含桥接符号 prover、生成 proof tree 的直接 pipeline 邻居。二者都不是 WordNet gloss-span source-support gold，也不是当前任务的 matched baseline。
- **证据等级：** 官方 proceedings 页面及官方 PDF；未下载或执行代码/数据，未独立复现论文结果。
- **边界：** 两篇目标性邻近筛查不等于 IJCAI 全 proceedings 系统筛查，不提供召回率或新颖性结论。结构化证据：[screen log](../sources/literature_screening_log_2026-10-06_ijcai2026_logic_neighbors.json)，阶段综合见Phase 40。

### 2026-10-07 ACL 2026：显式规则依赖图补查

在 ACL Anthology 官方 2026 proceedings 定向检索 rule dependency graph、rule state 与 graph-aware reasoning，核读 RGCWM 一篇主会论文的方法、实验、鲁棒性和局限。该补查纳入 pairwise typed rule graph 与连续规则证据状态这一重要邻居，避免将“外显规则依赖/状态跟踪”写成泛化贡献。它并非 ACL 全集系统筛查，不调整冻结候选框计数；官方全文、筛读范围及差异见[结构化日志](../sources/literature_screening_log_2026-10-07_acl_rule_graph_neighbor.json)。其图/状态是模型估计而非 source-supported proof，不能替代对 sense-linked gloss-span→Horn support 的 matched baseline。


## ACL 2026：组合 NLI、来源跨度与规则图候选（Phase 56）

在冻结 ACL v3 候选框的 2026 `nli_logic_proof_verification` 待筛子集中，对 58 条逐篇做题名/摘要初筛，保留 26 条方法邻近、2 条背景，排除 30 条出本轮实质综合；五篇官方全文定向核读。CARENLI 已有临床推理类型路由、专用 schema solver 与 verifier；COMPACT 已用 clause graph 表示多条款义务/例外依赖；FactAppeal 已做 claim/source span annotation；Ghost Context 研究错误上下文跨度造成的误归因；SciClaimEval 将真实科学主张连到跨模态表格/图证据。故 NLI 分解、规则依赖图、来源跨度和证据核验不宜单独作为宽泛 novelty claim。

这些工作尚不提供 sense/release-linked WordNet gloss、逐 span 的 Horn premise support gold、保留替代推导的 AND/OR witness DAG 或 source-only proof replay 的 matched baseline。这个差异仍是研究假设，须由更完整检索及同 gold/预算实验验证。CARENLI 的 typed-template/小样本限制、FactAppeal 的 claim-source 未逐一链接、COMPACT 预设相关条款已找到、Ghost Context 无人工 judge validation 子集，均提示项目需把语义支持、来源链接、证据检索与形式 replay 分开评价。逐条筛读和范围边界见Phase 56 报告与[机器日志](../sources/literature_screening_log_2026-10-07_acl2026_nli_logic.json)。


## ACL 2026：图式证据检索、faithfulness 与超图先例（Phase 57）

在 ACL 固定 v3 框对 `graph_rule_provenance` 2026 年剩余 117 条题名/摘要完成筛读，29 邻近、61 背景、27 排除；定向核读 Faithfulness Beyond Plausibility、FEVER 的 Evidence Grounding vs. Memorization、EHRAG、STEM 四篇官方 PDF。EHRAG 已用结构+语义 hyperedges 做检索，STEM 已用 query schema graph 与 evidence completeness 评价结构化多跳检索；所以“用图/超图表示上下文或检索证据”不应单独主张新颖。另两篇强调更窄的审计问题：引用了 source triple 不等于它蕴含 claim，标注了 evidence span 也不等于裁决真实依赖该 span。

这几篇工作没有共同提供 sense/release-bound lexical gloss span、方向性 AND/OR Horn support gold、alternative witness DAG 和独立 source-only replay 的 matched evaluation。此项仍待全范围检索与实验验证。详情见Phase 57 报告及[结构化筛读日志](../sources/literature_screening_log_2026-10-07_acl2026_graph_rule_provenance.json)。


## ACL Anthology 2025：WordNet taxonomy、Horn/tree rules 与证据核验（Phase 58）

在冻结候选框中筛完 2025 年 `graph_rule_provenance` 的 133 条记录，28 邻近、60 背景、45 排除；十篇做官方全文定向核读。新增最直接近邻是 ACL Findings 2025 LORex：其在 WordNet 等 taxonomy benchmark 上结合节点定义、层级路径与候选父节点推理做 taxonomy expansion。因此“定义辅助的 taxonomy parent/hypernym 选择”不宜单独主张新颖；应作为优先适配 baseline。另有 FOL/Horn tree-like rule refinement、faithful graph query decoding、KG trees 与 graph fact-checking 近邻。它们未提供 sense/release-bound gloss span→Horn literal support gold 和独立 source-only replay。筛查边界和比较细节见Phase 58 报告及[逐条机器日志](../sources/literature_screening_log_2026-10-07_acl2025_graph_rule_provenance.json)。

### Phase 59：ACL 2024 source-grounded entailment 候选

- Frozen input: `acl_anthology_candidates_2026-10-06_v3_reconciled_phase58.json`，SHA-256 `8f3f588722928d6dd28c80588d6d47fabce8ed31deb72180579bb7d572db327e`。
- Slice: `year=2024`、待题名/摘要筛查、query family=`source_grounded_entailment`，共 84 条；30 adjacent、35 background、19 exclude。
- Ten priority records received targeted official PDF section review. All remaining judgments are metadata/abstract-level. Single reviewer; no code/data reproduction, no IAA, no recall claim.
- Reconciliation output: `acl_anthology_candidates_2026-10-06_v3_reconciled_phase59.json`; 957/1,747 exact URL matches, 790 pending. Explicit depth counts: 75 full text, 62 targeted sections, 594 metadata/abstract, 226 unresolved. Exact URL match is not a relevance decision.
- See [screening log](../sources/literature_screening_log_2026-10-07_acl2024_source_grounded_entailment.json) and Phase 59 review.

### Phase 60：ACL 2024 NLI/逻辑/证明候选

- 输入为 Phase 59 对账副本 `acl_anthology_candidates_2026-10-06_v3_reconciled_phase59.json`，SHA-256 `ecd6a2235d9273257039adaac59e33b294a99ffc63c4fcfd7e521b7ae51a58de`。
- 对 2024 年 `nli_logic_proof_verification` 族剩余 36 条待筛记录逐一做标题/摘要判定：16 adjacent、8 background、12 exclude；八篇官方 PDF 定向章节 review。单人筛读；无 IAA 或复现。
- Phase 60 对账为 993/1,747 exact URL match，754 pending；深度：75 full text、70 targeted sections、622 metadata/abstract、226 prior depth unresolved。日志匹配不等于相关性纳入。
- 详见[逐条日志](../sources/literature_screening_log_2026-10-07_acl2024_nli_logic_proof.json)和Phase 60 报告。

### Phase 61：ACL 2024 图/规则/来源候选

- 输入 Phase 60 对账副本，SHA-256 `de2a0c81c75719d1afcc5a9e46cefa2f6e74a450d6ac7d33025c7348bd17b008`。
- 筛查 `graph_rule_provenance` 中剩余 100 条 2024 记录：36 adjacent、33 background、31 exclude；十篇官方 PDF 定向核查。单人，无 IAA，无代码/数据复现。
- 当前对账 1,093/1,747 精确 URL 命中，654 pending；深度全文 75、定向 80、摘要/元数据 712、先前深度未明 226。该数字不是相关性纳入或系统综述覆盖率。
- 见[机器日志](../sources/literature_screening_log_2026-10-07_acl2024_graph_rule_provenance.json)与Phase 61 报告。

### Phase 62：ACL 2023 definition-to-formal-logic 候选

- 输入为 Phase 61 对账副本，SHA-256 `89795ed3e8960f50987ae6d30b1be928877b479cb3107cc06b77a631cf07e068`。
- 对 31 条 pending 2023 `definition_to_formal_logic` 记录完成 title/abstract screen：15 adjacent、13 background、3 exclude；九篇 official PDF 定向核查。单人，无 IAA，无代码/数据复现。
- Phase 62 全框 exact URL match 为 1,124/1,747，623 pending；显式深度：全文 75、定向 89、摘要/元数据 734、深度未明 226。
- 见[结构化筛查日志](../sources/literature_screening_log_2026-10-07_acl2023_definition_to_formal_logic.json)与Phase 62 报告。

### ACL 2023 Phase 63：source-grounded entailment 切片

- **框架：** Phase 62 冻结对账候选副本；筛查 2023 年 `source_grounded_entailment` 中 57 条 pending 记录。
- **筛读：** 全部候选逐条读取官方元数据/摘要；10 篇优先论文定向阅读官方 PDF 的任务、方法、评测或限制章节。
- **主要补充：** WordNet sense gloss 用于 lexical substitution + mutual entailment 的直接先例；ontology subsumption/NLI、WordNet-derived compositional entailment、proposition segmentation、多证据 NLI 与 attribution。
- **证据等级：** 单人筛查；无双人一致性、召回估计、代码/数据复现或系统检索主张。逐篇数据与 depth 字段见[机器日志](../sources/literature_screening_log_2026-10-07_acl2023_source_grounded_entailment.json)。
- **解释边界：** 与目标的 task delta 只能支持形成待检验假设，不能证明新颖性；精确 URL 对账也不等于相关性判定。

### ACL 2023 Phase 64：graph/rule/provenance 与 WiCE 多证据切片

- **框架：** Phase 63 对账快照；筛查 54 条 pending 2023 `graph_rule_provenance` 记录，并额外筛查 pending WiCE 多证据记录，共 55 条。
- **筛读：** 逐条读取官方元数据与摘要；10 篇定向核查官方 PDF 的任务、方法、表示、评估或限制部分，优先覆盖 SPINDLE、KG rule learning/augmentation、FactKG、path reasonableness、WiCE/RoMQA。
- **主要补充：** NL→typed λ/proof checker；KG 结构规则学习与变换；多类型 KG claim verification；路径 spuriousness；claim decomposition/multi-evidence evidence selection。
- **证据边界：** 单人筛读，无代码/数据复现、IAA 或系统综述召回估计；完整候选逐条信息见[Phase 64 结构化日志](../sources/literature_screening_log_2026-10-07_acl2023_graph_rule_provenance.json)。

### ACL 2023 Phase 65：NLI/证明验证切片

- **框架：** Phase 64 对账版中 2023 年 `nli_logic_proof_verification` 16 条 pending 记录。
- **筛读：** 16 条官方 metadata/abstract 全筛；9 篇 PDF 对 task/method/representation/evaluation/limitations 做定向核查；NewsSense 仅核官方摘要且明确不计入全文审阅。
- **近邻重点：** PROVER 的多步 NLI proof generation + human verification；ReCEval 的 chain correctness/informativeness；SICCK 的 hypernym/quantifier/negation slices；RNN-CCG syntax-to-theorem-prover 路线；FEVER 多跳 retrieval + NLI。
- **影响：** NLI proof chains、reasoning-chain metrics、evidence retrieval 均已有先例，项目需以 gloss source-span support 与独立 Horn replay 进行匹配评价。
- **限制：** 单人 scoping，无复现/IAA/召回率，见[机器日志](../sources/literature_screening_log_2026-10-07_acl2023_nli_logic_proof.json)。

### Phase 66：ACL 2022 definition/logic/proof 关键词切片

- **切片定义：** 冻结 Phase 65 ACL 候选副本中 2022 年 pending title/abstract 记录，匹配 `WordNet/gloss/hypernym/definition/semantic parsing/logical form/theorem prover/proof generation/Horn` 词项，共 20 篇。
- **筛读：** 官方元数据/摘要逐篇筛读；10 篇官方 PDF 定向核查 task/formal representation/method/evaluation/limitations。
- **发现：** NLProofS 已具 supplied-fact AND proof tree + trained verifier-guided search；Dual-(m)T5 做 PL/FOL parsing + NLI；CCG+Vampire temporal NLI；ZS4IE verbalization+NLI。另有 definition-trained sentence embeddings、Coq autoformalization、premise retrieval。
- **解释边界：** 目标性关键词 slice，不是 ACL 全量扫描、无召回估计、IAA、代码/数据复现或 novelty 结论。详见[机器日志](../sources/literature_screening_log_2026-10-07_acl2022_definition_logic_proof.json)。

### Phase 67：ACL 2021 lexical/logic/proof 定向切片

- **输入：** Phase 66 对账副本中 2021 年、尚未匹配到筛查日志、标题/摘要命中 WordNet/gloss/hypernym/definition/semantic parsing/logical form/theorem prover/proof/Horn 关键词的 14 条记录。
- **处理：** 对 14 条逐条做 metadata/abstract 判断；对 Sumita/PACLIC、RuleBERT/EMNLP、UniKER/EMNLP、WinoLogic/EMNLP、Enforcing Consistency/ACL、On Robustness/EACL 阅读官方 PDF 任务、表示、方法或评价章节。
- **影响：** 定理证明交互补充词汇知识、soft/definite Horn reasoning、prover-certified commonsense、semantic parser consistency/robustness 都已有先例；新增对照应拆分自然语言来源语义与形式规则推理。
- **边界：** 关键词切片，不是 ACL 全量系统综述；单人筛查，无 IAA、召回估计、许可审计、代码/数据复现或新颖性结论。结构化逐条日志见[Phase 67 log](../sources/literature_screening_log_2026-10-07_acl2021_logic_proof.json)，综合见报告。


### Phase 92：ACL 2022 未匹配候选全切片筛读

- 接续 Phase 91 的冻结 1,747 候选框，逐条筛读当时未命中任何日志的 2022 年 130 条；22 条列为邻近工作，2 条背景，106 条排除出当前核心综合。
- 对 Saji et al.、Feng et al.、Prost、Sprague et al. 四篇官方 PDF 的相关章节做定向核读；另核对 Hypergraph Transformer 官方论文页摘要。单人筛读，未作代码/数据复现或 IAA。
- 复算全框后为 1,416/1,747 URL matches、331 unmatched；2022 unmatched 为 0，331 条未匹配项均在 2016–2021。深度状态：全文 75、定向 138、摘要/元数据 977、此前深度无法确定 226。日志匹配和筛读决定均不是系统综述完成/召回率证据。
- 逐条记录见[Phase 92 screening log](../sources/literature_screening_log_2026-10-07_acl2022_unmatched_title_abstract.json)，全框机器快照见[Phase 92 aggregation](../outputs/phase92/acl_screening_coverage.json)，分析见Phase 92 report。


### Phase 93：ACL 2021 未匹配候选筛读与推理验证近邻

- 筛读 85 条此前无全局 URL 匹配的 2021 年候选：26 adjacent、2 background、54 exclude from current core synthesis、3 deferred because no official abstract was present.
- 四篇官方 PDF 定向核读（LogicNLI、EEV、NeuNLI、ParaPattern）；单人筛读，无 IAA 或代码/数据复现。
- 全框刷新为 1,501/1,747 匹配、246 无匹配；无匹配项落在 2016–2020。2021 候选框总数 128，URL 对账均已匹配，但 3 条无摘要待补证，22 条历史日志深度仍不明。
- 见[逐条日志](../sources/literature_screening_log_2026-10-07_acl2021_unmatched_title_abstract.json)、[全框快照](../outputs/phase93/acl_screening_coverage.json)与Phase 93 深度报告。


### Phase 94：ACL 2020 未匹配候选筛读与关键先例定向核读

- 筛读 Phase 93 后仍无全局 URL 匹配的 2020 年候选 94 条：29 adjacent、3 background、62 exclude from current core synthesis；六篇官方 PDF 做定向章节核读。单人 scoping screen，无 IAA、复现或许可判断。
- 全框更新为 1,595/1,747 URL 匹配、152 无匹配（均为 2016–2019）；深度数为明确全文 75、定向章节 148、摘要/元数据 1,143、旧日志深度未明 229、pending 152。2020 pending 清零。
- 关键先例收窄创新表述：Abzianidze 以 NLI 标签溯因学习词汇关系并接入 natural tableau；Grits 研究形容词到描述逻辑定义；WikiNLI 从百科类别构造词汇蕴含；PRover 约束 proof graph；Goyal & Durrett 做依存弧级源支持；NILE 评估 explanation faithfulness。它们各自不等于 WordNet gloss-span → Horn witness，但排除了“首次词汇关系逻辑学习”“首次定义形式化”“首次 proof graph”之类宽泛主张。
- 机器输出：[Phase 94 snapshot](../outputs/phase94/acl_screening_coverage.json)；逐条筛读：[Phase 94 log](../sources/literature_screening_log_2026-10-07_acl2020_unmatched_title_abstract.json)；综合：Phase 94 深度报告。该切片不证明全领域新颖性或综述完备。


### Phase 95：ACL 2019 未匹配候选筛读与定义到词汇路径先例

- 按全局 reconciliation 状态筛读 2019 年 68 条此前无日志匹配候选：26 adjacent、7 background、35 exclude；4 篇官方 PDF 定向核读。
- 复算后 1,663/1,747 URL 匹配、84 unmatched（均在 2016–2018）；全文 75、定向 152、元数据/摘要 1,207、历史深度不明 229、pending 84。2019 pending 清零。
- Prokhorov et al. (NAACL 2019) 已由 textual definitions 预测 hypernym/hyponym KG paths，并以 attention 显示输入词与路径概念的关系；这直接排除“首次定义到词汇层级路径”宽主张。E3 联合抽取 procedural rules 与判断 conversation entailment；Coq symbolic NLI、ACE→ASP 也分别是证明助手 NLI 与自然语言规则执行先例。项目差异需聚焦逐 literal gloss-span attribution、sense-aware typed Horn compilation、source-only entailment 和独立 witness replay，并以匹配 gold 验证。
- [Phase 95 snapshot](../outputs/phase95/acl_screening_coverage.json)、[screening log](../sources/literature_screening_log_2026-10-07_acl2019_unmatched_title_abstract.json)、深度报告。该候选切片不证明全领域新颖性或系统综述完备。


### Phase 96：ACL 2018 形式词义、推理证明与 WordNet 审计先例

- 筛读 38 条全局未匹配候选：18 adjacent、8 background、12 exclude；对 Yanaka、Gritz、Álvez/Rigau、Kang、Hosseini、WARP-Text 六篇官方 PDF 定向核读。
- 全框为 1,701/1,747 精确 URL 匹配，46 unmatched（均 2016–2017）；筛读深度全文75、定向158、摘要/元数据1,239、旧深度不明229、pending46。
- 发现直接限制宽主张的先例：自然演绎证明学习短语对应（Yanaka）；自然语言定义转 OWL 2 DL（Gritz）；WordNet/SUMO 使用 ATP 检查资源一致性（Álvez/Rigau）；词汇资源与手写规则模板用于NLI训练（AdvEntuRe）；从文本学习typed entailment graphs（Hosseini）；句/短语/token层关系标注（WARP-Text）。当前差异假设应收窄为 sense-linked gloss→typed Horn、逐 literal 版本化 span 归因、source-only entailment 与独立 witness replay 的联合实证，不主张这些组成各自首次。
- [Phase 96 snapshot](../outputs/phase96/acl_screening_coverage.json)、[逐条日志](../sources/literature_screening_log_2026-10-07_acl2018_unmatched_title_abstract.json)、深度分析。此切片不是全领域新颖性证明或系统综述。


### Phase 97：ACL 2017 词汇公理注入与自然语言证明先例

- 筛读 27 条未匹配候选：17 adjacent、7 background、3 exclude；对 Martínez-Gómez、LangPro、Yanaka、Srivastava 四篇官方 PDF 定向核读。
- 全框更新至 1,728/1,747 精确 URL 匹配、19 unmatched（均 2016）；全文75、定向162、元数据/摘要1,262、旧深度不明229。
- Martínez-Gómez et al. 已基于不可证子目标按需构造词汇公理并继续定理证明；LangPro 已做透明 natural-logic tableau 自然语言证明；Yanaka et al. 用自然演绎 proof features 预测语义相似；Srivastava et al. 从自然语言解释联合学习解析和概念。因此创新假设须聚焦 sense-linked gloss 作为规则来源、逐 literal span provenance、source entailment 与独立 witness replay，而不能宽泛主张首次 lexical proof、axiom injection 或 explanation-to-concept learning。
- [Phase 97 snapshot](../outputs/phase97/acl_screening_coverage.json)、[逐条日志](../sources/literature_screening_log_2026-10-07_acl2017_unmatched_title_abstract.json)、深度报告。候选框内 pending 清零也不是检索召回或系统综述完整性的证据。


### Phase 98：ACL 2016 最后候选筛读与固定框覆盖完成

- 筛读最后 19 条 2016 年候选：10 adjacent、6 background、3 exclude；对 Sadoun、ESO、Guo、Santos、TEG-REP 五篇官方 PDF 定向核读。
- 固定 ACL v3 候选框 1,747/1,747 URL 均有日志匹配，pending=0；深度全文75、定向167、摘要/元数据1,276、旧日志深度未明229。候选框匹配不等于相关性纳入、全文阅读、全 ACL 检索召回或系统综述完备。
- 新确认近邻：半自动 ontology/glossary 知识获取、WordNet跨资源事件ontology、KG+逻辑规则联合嵌入、DOLCE关系taxonomy、基于抽取模式的gold textual entailment graphs。进一步限制“首次 ontology/glossary 知识获取”“首次 WordNet形式审计”“首次 KG+规则”“首次文本蕴含图”等主张。
- 后续转为固定框外的引用链与 ACL 外综述，重点比较 sense-linked gloss、逐 literal span、source entailment 与独立 witness replay 的联合假设。见[Phase98快照](../outputs/phase98/acl_screening_coverage.json)、[日志](../sources/literature_screening_log_2026-10-07_acl2016_unmatched_title_abstract.json)和报告。
### Phase 99：ACL 框外 4lang 期刊后续追踪

- 官方全文定向筛读 Kovács et al., *Explainable lexical entailment with semantic graphs*（在线 2022；NLE 2023），核对摘要、方法、评测和错误分析；明确它是 BMEAUT SemEval-2020 同一研究线的期刊扩展，不另计一条独立方法家族。
- 该工作已做词典定义图→方向性 lexical entailment，并提供图路径解释、WordNet 结合和多个 benchmark；因此“首次可解释定义图蕴含”不能成立。图路径也可能因 sense/edge 误差而不忠实，后续比较必须分别测 claim correctness、source-span support 与可重放证书。
- 此为单人、定向、无固定跨库候选总量的筛读；不改变 ACL v3 的 1,747 URL 框，也不估计框外召回或证明新颖性。记录见[结构化日志](../sources/literature_screening_log_2026-10-07_4lang_explainable_lexical_entailment.json)和Phase 99 深度报告。

### Phase 100：4lang 正式规则抽取与人工 gold 邻接先例

- 沿 4lang/BMEAUT 方法线定向核读 Recski et al. 的 BRISE-Plandok（online 2024 / LRE volume 2025）。该研究用 UD→4lang 图、领域手写 pattern 和后续字段抽取构造德语法规正式规则；不属于 WordNet glossary / lexical entailment，不能作为直接基线或横比其论文分数。
- 7,049 个经双标和作者复核句子上的端到端完全正确率：全属性 46%、受手写规则覆盖的 40 个属性 55%、gold attributes 条件下约三分之二。作者说明 pattern 基于完整标注语料经验开发，未能评估跨文档泛化。
- 对本项目的启示是报告各阶段和完整规则正确率，并预防 pattern/test leakage；同时单列 sense、direction、逐 gloss span、source-only entailment 与 proof replay。该轮单人单篇定向复核，不是系统检索或新颖性结论。见[日志](../sources/literature_screening_log_2026-10-07_brise_plandok_rule_extraction.json)及Phase 100 报告。

### Phase 101：BRISE 2021 原型的形式规则与证明器复核

- 核读 CEUR 官方 ASAIL 2021 全文，确认 BRISE 原型已做 UD→4lang→任务特定 grammar/pattern→deontic logic→theorem prover 的端到端架构和逐步解释，排除该架构层面的宽泛“首次”主张。
- Full-pipeline perfect 结果只在 6 条精心挑选的 toy 句上，论文明确说不构成全流程定量评估；10 份文档的 P>93/R>51 是 attribute mentions 指标，不是 formal rule accuracy。Prover 验证生成公式，不验证源文本翻译正确。
- 该论文与 BRISE-Plandok (LRE 2025) 作为同一 BRISE 研究线登记；不重复计数。此轮是单篇引用追踪，无复现或系统综述结论。见[日志](../sources/literature_screening_log_2026-10-07_brise_explainable_rule_extraction_2021.json)和报告。

### Phase 103：2026 lexical explanations × formal NLI

ACL/ICLR/NeurIPS 2025–2026 定向查询后，沿近期词汇蕴含与 prover 关键词核到 de Jong et al. 的 *Explaining Textual Entailment with Lexical Entailments*。确认 arXiv v1 于 2026-09-26 提交并获 AKBC 2026 接收；官方 workshop 日程显示活动安排在 2026-10-28，晚于本次筛读。对 arXiv 全文、摘要、相关工作、lex-NLI 标注集、模型表、LangPro proof coverage、误差分析及限制作定向核读。该文不是顶会主会论文，也不是 WordNet gloss→rule 系统；登记为 2026 强邻接工作，不与 ACL/ICLR 主会结果混计。此次是单篇 citation/search follow-up，不扩充 ACL v3 固定候选框、不估计相关工作检索召回、不形成系统综述结论。结构化记录见[Phase 103 log](../sources/literature_screening_log_2026-10-07_lex_nli_formal_proofs_akbc2026.json)和报告。

### Phase 115：NeurIPS 2025 autoformalization / WordNet targeted screen

- 按官方 NeurIPS proceedings 定向检索并筛读 HAR/CoPA、miniF2F-Lean Revisited、Hierarchical Retrieval 三篇主会论文；本地精确题名去重无既有记录。对数学 formalization 两文核对任务/流程/结果与 fidelity 讨论，对 WordNet 文核对 taxonomy 输入、ancestor retrieval 和指标。
- 纳入相关工作时分别标记为：分阶段数学 autoformalization/proof 方法先例；形式化目标与原自然语言的 benchmark-alignment 方法先例；WordNet 层级检索表示邻居。不得混作 gloss lexical entailment baseline。
- 搜索范围为定向官方来源，不设完整 NeurIPS 2025 candidate denominator，未估计 recall；不声称系统综述或 novelty proof。NeurIPS 2026 的官方虚拟目录未形成可用全量候选框，也不作 absence claim。记录见[筛读日志](../sources/literature_screening_log_2026-10-07_neurips2025_autoformalization_wordnet.json)与报告。
### Phase 116：ICLR 2026 semantic fidelity 与 AND/OR pattern audit

- 在 ICLR 2026 官方 proceedings 按 `autoformalization semantic fidelity consistency benchmark` 与 `AND-OR inference pattern human audit` 检索；筛读 ReForm 和 *Can LLMs Reason Soundly in Law?* 官方全文并逐题名去重。
- ReForm 记为 math NL-to-Lean semantic consistency、expert benchmark 和 adjudication 方法先例；法律论文记为模型 logit/decision score 的 AND/OR phrase-interaction explanation。必须分开 feature interaction、形式陈述语义忠实度、gloss entailment 和 Horn proof replay。
- 此为两篇目标性筛读，无完整 ICLR 候选总量、无召回估计、无 absence/novelty 结论、未复现代码或数据。详见[机器筛读日志](../sources/literature_screening_log_2026-10-07_iclr2026_reflective_fidelity_and_andor_audit.json)和Phase 116 报告。

### Phase 120：Findings of EMNLP 2025 targeted supplement

- 截止日 2026-10-07，定向筛读四篇 Findings of EMNLP 2025 官方记录与 PDF：形式证明评测、adaptive verification agent、principal knowledge grounding、logical reasoning evaluation。此轮 targeted full-text screen 不等同于 proceedings-wide search。
- 精确 Anthology ID/URL 对账至冻结 `acl_v3_screened_normalized.json` 的 1,747 条 candidate array，四条均未命中。作为候选框外 official supplement 登记，不增加 ACL 分母、不改历史 reconciliation、不据此估计 recall。
- ACL Anthology 可用 proceedings listing 最新为 2025；EMNLP 2026 官方 CFP 所列会议日期为 2026-10-24—29，晚于截止日。本轮只界定 publication cutoff，不宣称 EMNLP 2026 全量目录已发布/已筛或不存在相关论文。
- 把形式 proof validity、verifier orchestration、LLM grounding judgments、logical-evaluation metrics 分开列为邻接先例；均不能替代人工审定的 sense/release-linked gloss-span support gold 或独立 source-only Horn replay。逐篇范围和限制见[筛读日志](../sources/literature_screening_log_2026-10-07_emnlp2025_reasoning_verification_grounding.json)与Phase 120 报告。

## Phase 135：扩展 gloss / lexical prediction 词族

ACL v3 候选框与现存结构化日志未包含 Aljaafari et al. (EACL 2026), *Where Do LLMs Compose Meaning?*（Anthology ID 2026.eacl-long.214）。官方全文使用 WordNet 定义做 inverse definition modelling（definition→term），并另做 word→hypernym；该任务名未被当前候选词族捕获。后续检索增加 inverse definition modelling、definition-to-term、WordNet hypernym prediction、gloss-based lexical prediction。见[Phase 135 机器日志](../sources/literature_screening_log_2026-10-07_eacl2026_gloss_composition.json)和报告。

候选框缺项说明关键词召回存在盲区，不说明召回率。新扩展词族应另建版本化候选框、计算 SHA-256 并做 alias/URL 去重；不得改写旧 frozen denominator 或把候选命中等同综述纳入。

## Phase 136：definition-conditioned lexical prediction query-family expansion

Phase 135 的检索词汇盲区已落实到 ACL 搜索器，新增 definition_conditioned_lexical_prediction 词族；条件定义和导出/候选 SHA-256 见[机器审计](../sources/acl_query_expansion_audit_2026-10-07_phase136.json)。基于当期 ACL 官方 BibTeX+abstract 导出生成独立 v4 raw 和 reconciled 文件，没有覆盖冻结 v3。

v3 有 1,747 个 Anthology IDs；v4 有 1,748 个，精确 ID join 为 1,747 shared / 1 added / 0 removed。新增项是 Phase 135 已全文筛读的 EACL 2026 *Where Do LLMs Compose Meaning?*。新词族预去重命中两篇：该 EACL 论文，以及已在 v3/结构化日志中的 Cho et al. 2020 *Leveraging WordNet Paths for Neural Hypernym Prediction*。v4 exact-URL 日志 join 为 1,748/1,748；深度为全文 76、定向章节 167、摘要/元数据 1,276、历史深度未明 229。日志命中不等于综述纳入，229 条未明也不是全文筛读。

v3 与 v4 的官方 BibTeX 导出压缩/解压哈希不同，候选差分仅对照两个已保存集合，不能单独归因于新词族；严格估计词族净效应应在同一导出字节上并行跑旧/新配置。此单库扩展不估计 recall，也不是系统综述。见Phase 136 报告及[审计 JSON](../sources/acl_query_expansion_audit_2026-10-07_phase136.json)。

## Phase 137：固定官方导出上的同源词族消融

为隔离 Phase 136 的跨版本导出变化，候选生成器现在支持离线读取压缩 ACL BibTeX 导出、保存本次下载字节和排除指定 query family。此次固定原始导出 SHA-256 为 537d57a62d42ca43c16d71ccd284d57d53ffe9d4cfa42521acef083508e245d9，BibTeX 内容哈希为 b9c8070c8ded0448e5dc30deaed521ae1bb844933a61f0ee9b62e5cc628fc698。

在同一输入字节上运行全词族与排除 definition_conditioned_lexical_prediction 的基线：1,748 vs 1,747 IDs，shared 1,747，added 1，removed 0；基线 ID 集合和旧词族的全部预去重命中数均与冻结 v3 相同。唯一新增 EACL 2026 Aljaafari et al.；新族另一命中 Cho et al. 2020 已在基线内。v5 reconciled URL 命中 1,748，其中全文 76、定向 167、摘要/元数据 1,276、深度未明 229。该同源差分只对这份 ACL 导出与这一词族成立，不估计召回率。完整哈希、候选差分和命令见Phase 137及[审计 JSON](../sources/acl_query_expansion_audit_2026-10-07_phase137.json)。

原始 bulk export 涵盖该项目年份窗口之前的旧材料，ACL 官方版权说明称 2016 年前材料为 CC BY-NC-SA 3.0，2016 年及以后为 CC BY 4.0。该完整压缩快照只为本地复算保留，不应作为项目数据包公开再分发；过滤后的候选框仍保留文献引文和官方 URL。见[ACL copyright FAQ](https://aclanthology.org/faq/copyright/)与[bulk export FAQ](https://aclanthology.org/faq/)。

## Phase 138：ACL BibTeX 流式解析与同源复算

为降低固定导出复算的内存占用，搜索器改为逐行解压、逐条目解析和处理，不再同时保留全量解压文本与所有 BibTeX 记录。压缩输入仍整体驻留内存。对 Phase 137 的同一导出复算后，解压内容 SHA、131,647 条目数、1,748 条候选 ID 与全部共同记录字段、旧查询族预去重命中数均逐项一致；日志 URL 对账仍为 1,748/1,748，筛读深度仍为 76/167/1,276/229。运行期间一次工作集采样约 69 MiB，历史整文件解析运行曾观察到约 966 MB；两者不是受控峰值基准。此结果只支持该固定输入上的输出等价，不证明一般解析完整性、检索召回或新颖性。见Phase 138 报告和[机器审计](../sources/acl_streaming_parser_audit_2026-10-08_phase138.json)。
# Phase 167：AAAI 2026 正式逻辑与 autoformalization 定向补筛（2026-10-08）

在 AAAI 官方论文集按 autoformalization/NL-FOL、WordNet/gloss、proof/verifier、graph provenance 等主题检索。对 Brunello et al.、Li et al. 的 HBLR、StepFun-Formalizer 及 AAAI 特别轨的 tax reasoning 各作官方 PDF 方法/评估/范围章节定向核读。此为一名审阅者选篇补筛，不是 AAAI 全目录普查或系统综述；主技术轨与 special track 分开标记。结论收录于Phase167报告和[结构化日志](../sources/literature_screening_log_2026-10-08_aaai2026_formal_logic_neighbors.json)。固定 ontology/gloss + SMT formula evaluation、逻辑扰动测试、selective translation/backward reasoning、数学 autoformalization、NL rule→executable Prolog 已有先例；这些均不是 WordNet gloss-span support 或 source-only replay 的匹配 gold。未运行论文代码或项目实验。

## Phase 177：ACL Findings 2026 可执行逻辑形式与 COLM 2026 可验证过程监督

2026-10-08 从 ACL Anthology 官方记录/PDF 与 COLM 官方 accepted-papers 页面定向补查两项先前未出现在项目文献账本的工作。完整筛读 ACL Findings 2026 的 SELF-KBQA 官方 PDF，以及 arXiv v2 作者全文中的 COLM 2026 VPS（venue status 另由 COLM accepted list 核实）。本轮只纳入两篇最接近“结构化知识 + executable logic”及“逐步可验证推理”的新近论文，不是 ACL/COLM proceedings census 或系统综述。逐篇证据、筛查边界与方法映射见Phase177报告和[结构化日志](../sources/literature_screening_log_2026-10-08_structural_kbqa_and_process_verification.json)。

## Phase 182：COLM 2026 层次化 proof search 增量筛查

从 COLM 2026 官方 accepted-paper list 检出 Goedel-Code-Prover，核对作者全文的输入规格边界、辅助引理的 constructive reconstruction、QuickCheck 与 Lean-kernel 分工，以及 benchmark/baseline 口径。筛读将其作为形式证明方法先例，不把 code-verification 结果当 WordNet gloss baseline。单篇单审阅者目标筛读，不估计 COLM 召回率、不构成 systematic review；逐项证据见[结构化日志](../sources/literature_screening_log_2026-10-08_colm2026_hierarchical_code_proof.json)和Phase182报告。


## Phase 183：COLM 2026 verifier utility 定向补筛

从官方 accepted-paper list 识别 Quokka，以作者 arXiv v4 核对 verifier 三态语义、soundness 条件、正确性/下游效用的独立指标和 timeout 变化。按会议正式题名记录 Quokka，并保留早期 InvBench 题名。仅将预算敏感的增量效用、端到端成本和 inconclusive 状态作为评测设计参照，不把程序验证分数移入 WordNet 任务。单篇单审阅者定向筛查，不扩充固定候选分母、不估计召回率或证明新颖性。见Phase183报告与[机器日志](../sources/literature_screening_log_2026-10-08_colm2026_verifier_utility_quokka.json)。

## Phase 189：EMNLP 2026 主会题录与 workshop 状态重查

官方 Accepted Main Conference Papers 页面仍没有可见题名；正式会程只到 oral/poster session 层级。对 ACL Anthology `2026.emnlp-main`、`2026.emnlp-findings` 的 WordNet/gloss/hypernym/entailment/logic 定向检索无可核对单篇记录，event URL 当前不可读取。故 main/findings coverage 保持 pending，不把空页面或未命中当成无相关工作。官方 workshop 列表已显示 AKBC 2026；de Jong et al. 的 lex-NLI 论文此前已做全文筛读，登记为 workshop 邻接，不重复计入主会覆盖。查询边界与正式来源见[Phase189结构化日志](../sources/literature_screening_log_2026-10-08_emnlp2026_availability_refresh_phase189.json)及深度报告。这只是单人可用性刷新，不是会议全集筛查或系统综述。
### Phase225：NeurIPS 2026 定向候选增量（2026-10-08）

**问题族**：source-to-formal faithfulness、theory-scale autoformalization、proof/dependency graph、global premise retrieval、proof quality/cost。**官方候选源**：NeurIPS 2026 Downloads mixed event directory；以 WordNet、gloss、definition、entailment、formalization、proof、logical、hypergraph、dependency graph 逐词查询后，对本地未记录 title 去重。**纳入深筛**：四篇作者版论文的任务、表示、评测/证据与限制章节；记录 arXiv 版本、官方 listing 和 poster URL。**排除/保留**：只按标题命中的候选不写 substantive claim；poster detail cache miss 时 venue track 记为未核；题录事件数不当论文分母。**边界**：这是一个 reviewer 的定向补筛，非 full proceedings census、recall estimate 或 systematic review。机器记录和综合见 [Phase225 log](../sources/literature_screening_log_2026-10-08_neurips2026_autoformalization_and_proof_graph_phase225.json) 与 report。

### Phase237：LREC 2026 WordNet hierarchy supplement

官方 ACL Anthology/LREC proceedings 检索再次命中 Ku et al., *When Structure Matters: Cross-Lingual Hyperbolic Embeddings for Chinese and English Wordnets*（LREC 2026 main）。去重后发现该文已于 2026-10-05 在 `literature_screening_log_2026-10-05_recent_acl_wordnet_slice.json` 做官方 18 页全文筛读；此次仅补齐它在 `closest_work_comparison.md` 中的入口，并确认 ACL/LREC 官方书目信息。当前 PDF/海报抓取失败不覆盖旧全文审阅证据。未增加新文献计数或候选分母；这不是 LREC proceedings census、系统综述、召回率估计或新颖性证明。见Phase237对账报告和[去重记录](../sources/literature_screening_log_2026-10-08_lrec2026_wordnet_hyperbolic_phase237.json)。

### Phase239：ICLR 2026 分层概念与 WordNet taxonomy 定向筛查

在 ICLR 2026 官方 proceedings 中按 WordNet hierarchy、hierarchical concept、reasoning/logic representation 查询并精确去重。本轮对 Hill et al. *Hierarchical Concept-based Interpretable Models* 的官方 29 页 PDF 做全文筛读，判定为 WordNet hierarchy 驱动视觉 concept hierarchy/intervention 的相邻先例，但不是 glossary parsing、lexical relation、Horn proof 或 source-support 方法。Zhou et al. *The Geometry of Reasoning* 只读官方摘要；PDF 获取失败，故只保留为背景候选。两篇定向候选、逐篇筛读深度及排除理由见Phase239报告和[机器日志](../sources/literature_screening_log_2026-10-08_iclr2026_hierarchical_concepts_wordnet_phase239.json)。本轮不是 ICLR 全目录 census、系统综述、recall estimate 或 novelty proof。
### Phase240：NeurIPS 2025 独立证明检查定向筛查

从 NeurIPS 2025 官方 proceedings 围绕独立 checker、proof tree/certificate、proof provenance 和 soundness bug 定向检索，全文核读 Duong et al. *Generating and Checking DNN Verification Proofs*。记录 APTP 的二叉 activation case tree、MILP/LP leaf checking、实验范围和 solver trusted boundary；将其作为 producer/checker separation 与 proof artifact 的方法先例，而非 WordNet gloss 或 Horn 规则基线。精确去重得到 6 个结果、1 篇新全文筛读和 5 个既有重复命中；未改变 proceedings 候选分母。本轮不构成目录 census、系统综述、recall estimate 或 novelty proof。见Phase240报告及[机器日志](../sources/literature_screening_log_2026-10-08_neurips2025_independent_proof_checking_phase240.json)。

