# 最新相关工作补充：gloss 对照、claim-support、校准风险与形式化评测（持续增量至 Phase 270）

审查日期：2026-10-08。本文件汇总 Phase149 以来的跨会场定向增量筛读，来源包括 ACL Anthology、AAAI、ICLR、NeurIPS proceedings、PMLR/ICML 与 COLM 等官方记录。它不是单一冻结候选框的系统综述：框外结果单独记为发现，不回填 ACL 候选计数、不估计检索召回，也不构成新颖性证明。

## Phase270：proof quality 指标要求区分正确性与可用性

Petrov et al. 的 ProofRank 将正确证明中的简洁性、计算便利性、认知简洁性、解法多样性和方法适应性作为可扩展质量 proxy。其人工对照在简洁性上 IAA 为 57.6%，其余四项为 80.1%–89.0%；作者指出标注者彼此熟悉并共同讨论过项目。作者报告 correctness verifier 在人工检查的 17 个分歧中有 10 个 false positive 涉及漏掉关键推理步骤。对本项目的约束是：规则/Witness replay 只验证给定前提下的形式推导，不说明 gloss 的语义支持，更不构成解释清楚或有用的评价。当前将输出定位为可检查的结构化证据链；若将来主张可用性，需另做目标读者和任务明确的人评。该文的终答案数学竞赛场景不是词典释义任务，且结果未复现。官方 NeurIPS Downloads/Poster 页面列题；arXiv v2 评论又记载 ICML AI for Math workshop 接收，当前不能判明具体 NeurIPS track 或两条记录的关系。详见Phase270全文筛读报告和[结构化日志](../sources/literature_screening_log_2026-10-08_proofrank_phase270.json)。

## Phase267：BPF/DriftBench 收窄形式化忠实度主张

定向发现并全文筛读 Mohammad & Sheikh 的 *The Faithfulness Gap*（arXiv:2606.16541v1；作者页将其归为 MusIML @ ICML 2026 workshop）。ICML 官方公告证实该 workshop 存在，但 OpenReview paper-specific forum 当前触发 browser challenge，因此本项目不把它记作已核实的 ICML 主会论文或独立确认的接收论文。BPF 以 Lean provability oracle 比较候选 formalization 与 LLM-generated probes 的双向 entailment fingerprint；CPG 针对 quantifier inversion、hypothesis omission、conclusion weakening、type coercion 构造机械扰动对照。作者报告 DriftBench 2,183 对、六个 mathlib4 子领域，controlled split 上 BPF+CPG 在 3% FPR 的 detection 为 89.6%，384-pair wild split κ=.77（双人 κ=.81），APBA 约 3.2× 成本缩减，FGD 报告 drift 率由 19.4% 降至 10.3%（4 candidates）。这些都是论文报告值，未在本项目复现。

近邻效应：不能再宽泛声称“proof-validity 不足以评价 NL→formal faithfulness”或“contrastive formalization probes/controlled drift evaluation 首创”。项目可保留的研究假设需进一步限定到 sense/release-bound gloss-span 对 typed directional Horn support、AND/OR 结构和 source-linked certificate replay，并以同候选 matched evaluation 验证。BPF 的 probes 不能独自充当 gloss semantics gold。

全文审读另发现形式论证需谨慎：Prop. 4.2 的证明从 probe-set 对理论等价封闭推出含有 N 或其等价 probe，但原条件未保证 probe set 与 N 相交/分离；需要明确的 separating probe 条件。Theorem 8.2 的 Occam proof 也没有说明为何随 k 增长的 `log|H| ≤ 2k` 项可由所示预算控制；可能可用期望误差后接 Markov 不等式另证相似界，但这不是文中当前给出的证明。此为 arXiv v1 文本的可核对证明缺口，不等同于驳倒其报告实验结果。见Phase267报告及[结构化筛读日志](../sources/literature_screening_log_2026-10-08_faithfulness_gap_driftbench_phase267.json)。

## Phase265：ACL 2026 CoPE 与“下游有效≠源文本形式化忠实”

将 Huang et al. 的 CoPE 从摘要/定向章节级升级为 ACL 2026 Long Paper 全文筛读。CoPE 按 initial/goal/action/state 约束分类，在 BlocksWorld 与 CoinCollector 上评测 planner、PDDL/PDDL3/SMT/LTL formalizer、edit/revision 路线；主结果使用每领域 100 个手动配对问题，而完整约束×问题集合有 10,000 项。作者明确指出，有效计划可能掩盖错误的自然语言约束形式化；20 项审计未发现 false positive，但不能推出普遍语义忠实。合取、否定、歧义也被留为未来工作。项目应将 gloss-span→typed rule 支持、形式证明重放、query utility 三个终点分开，并在有授权的 blind gold 上设逻辑组合压力切片。规划专属四类不能直接移植为 gloss taxonomy。详见Phase265报告及[全文补充日志](../sources/literature_screening_log_2026-10-08_acllong2026_cope_fulltext_phase265.json)。这是已知 ACL 论文的深度升级，不增加论文数或候选框分母。

## Phase264：推理轨迹论文中的作者/模型 provenance 与 source/proof provenance

Hammerla & Mehler 的 [*Negation in Reasoning Traces: Interpretable Signals of Correctness and Provenance*](https://aclanthology.org/2026.naloma-1.4/)（NALOMA 2026 workshop）将显式 discourse negation 区分为 corrective 与 refining，并在 GPQA Diamond、AIME 25、Nemotron-Math-HumanReasoning 的人类/六模型轨迹上评估否定统计、结构特征、embedding 和组合特征。两位语言学家复核 36 条轨迹/634 个步骤，human-human κ=.68、LLM-human κ=.37/.38；论文将自动标签视为弱 proxy。正确性分类中 embedding 总体更强于否定特征；最强结果是人类/LLM 作者分类。它的“provenance”是作者/模型识别，不是外部来源 lineage、gloss-span support 或 witness-proof provenance。项目的作者来源、source lineage、语义支持、形式有效性与证明溯源应继续分开，且模型标签不能替代独立 source-support gold。详见Phase264报告及[机器日志](../sources/literature_screening_log_2026-10-08_naloma2026_negation_traces_phase264.json)。本次是单篇官方全文定向筛读，不是会场普查或新颖性证明。

## Phase240：NeurIPS 2025 独立 DNN proof checker

APTP 将神经网络 branch-and-bound 不可满足性证明编码为 activation-pattern 二叉树，由独立 checker 验证每一分支并检查 MILP/LP leaf。该先例收窄独立 proof artifact、producer/checker separation 和小型 checker 的宽泛新颖性；它与 source-only AND/OR Horn witness、WordNet gloss-span support 和 lexical NLI 的任务对象不同，且仍依赖外部 solver。见Phase240报告及[机器日志](../sources/literature_screening_log_2026-10-08_neurips2025_independent_proof_checking_phase240.json)。

## Phase239：ICLR 2026 HiCEM 与 WordNet hierarchy

新增全文筛读 HiCEM：ImageNet concept labels 由 WordNet hypernym ancestry 构造，模型显式表示两层概念并研究 concept intervention。它是 WordNet 驱动 hierarchical concepts 的邻接先例，不处理自然语言 gloss、词汇规则、source spans 或 proof replay。另记录一篇仅摘要可核的 logic-in-representation-space 背景候选，官方 PDF 获取失败。详见Phase239报告及[机器日志](../sources/literature_screening_log_2026-10-08_iclr2026_hierarchical_concepts_wordnet_phase239.json)。

## Phase 182：COLM 2026 层次化机检证明搜索

Goedel-Code-Prover 在已形式化 Lean 规格上搜索辅助引理分解，用 proof reconstruction 检查子目标是否蕴含父目标、用 QuickCheck 随机寻找候选引理反例，再由 Lean kernel 校验最终 proof。它已构成层次化 proof search 与机检证明的近期主会先例；任务未涵盖自然语言 gloss 到逻辑规则的转换。对应项目差异必须落在 sense/release-bound gloss-span support 与 source-bound proof replay 的联合证据上，而非树形分解/机检本身。详见Phase182报告及[机器日志](../sources/literature_screening_log_2026-10-08_colm2026_hierarchical_code_proof.json)。

## Phase 159：形式正确性与内容效应的评测边界

新增三篇官方 ACL Anthology 定向筛读：ACL Industry Track 的 T²、Findings ACL 的 FoVer、SemEval workshop 的 Task 11。T² 用依赖后继定理测试 Lean theorem，仍将结果限定为语义正确性的证据；FoVer 用形式 verifier 给推理步骤打标签并在 NLI benchmark 测 PRM；SemEval Task 11 将 syllogistic validity 与内容 plausibility 拆开，并包括 distractors/multilingual 条件。它们共同支持分开记录 formal replay、行为测试与源语义支持；没有一篇提供 WordNet sense-bound gloss-span→typed Horn gold 或 matched baseline。单审阅者、三论文定向筛读，不改变冻结 ACL 候选框、不估计召回率。证据与限制详见Phase 159 深度报告和[机器日志](../sources/literature_screening_log_2026-10-08_formal_correctness_nli_addendum.json)。

## G-IdiomAlign：gloss/no-gloss 对照已有直接方法先例

Ye et al., [G-IdiomAlign](https://aclanthology.org/2026.acl-long.1794/) 使用英语 Wiktionary gloss 作为跨语言 idiom alignment 的语义 pivot，构造 18,785 个 pair，并在生成任务中直接比较 No-gloss 与 With-gloss 条件。论文报告 gloss 输入在其 embedding-similarity proxy 下提升各模型结果；但 pair 选择本身使用 gloss embedding、MNN 和分语言对分布过滤，人工 alignment evaluation 只覆盖 200 个 Zh–En pairs，其他语言对主要采用三 LLM 多数标签。开放生成上的 86 项人工校准也显示 embedding proxy 在高阈值下覆盖低。因此 gloss-conditioned contrast 已是 ACL 2026 的研究设计先例，而 embedding proxy 不能替代项目的人工语义支持 gold。

Track A 可保留双条件设计，但须把贡献限定在固定 sense 的上下文呈现、exact directional claim、raw-gloss span support 与资源/逻辑验证之间的差异；单独“有/无 gloss”对照不构成新颖性主张。

## ReportLogic：人审逻辑审计与 claim-support 评价已有先例

Zhao et al., [ReportLogic](https://aclanthology.org/2026.acl-long.384/) 以 Macro-Logic、Expositional-Logic、Structural-Logic 评估长篇研究报告；最后一层包括证据充分性、warrant/因果推理、qualifier/counterpoint。其 3,779 queries、1,572 人标 report pairs 使用三名专家对测试 pair 独立判断并多数裁决。rubric 给出报告内检查位置的 span cue。任务单位仍是报告对的整体偏好，不是每条 claim 到外部 source span 的 entailment；没有 lexical sense、typed Horn literal 或独立证明证书。

这使“human-rated logical auditability”“rubric-guided evidence sufficiency”或一般 claim-support 作为宽泛新意不成立。项目仍可测试更细的 release/sense-bound raw-gloss span→directional typed literal support 及 source-only replay；目前只是研究假设，须在同一人工 gold 和 matched baseline 上验证。

逐篇证据、限制和筛查可复算范围见Phase 149 深度报告及[机器日志](../sources/literature_screening_log_2026-10-08_acl2026_gloss_auditability_addendum.json)。


## Phase 150：COLM 2026 Q-CARE claim verifiability 先例

Choi et al., [Q-CARE](https://arxiv.org/abs/2608.11238)（COLM 2026 接收；[官方接收列表](https://colm.eventhosts.cc/Conferences/2026/AcceptedPapers)）将回答拆为原子 claim，并检查 claim 与检索 chunk 的 pairwise support。相关性 benchmark 含 320 个 query、567 个 sub-query 与 7,907 条 claim；三名标注者独立标注、多数裁决，三种关系 κ=.801–.891。论文自动 checker 默认是单一 Qwen3 LLM；同一模型三次运行的 alpha 表示跨运行稳定性，不是 human IAA。

该工作排除一般 claim-to-evidence support 与人类 verifiability 评价作为宽泛新意。其 RAG chunk 判断不等于 WordNet raw-gloss span 对方向性 Horn literal 的支持，也不验证 AND/OR 逻辑忠实度或独立 proof replay；因此是评测设计邻接先例，不是 matched baseline。详见Phase150 深度报告及[结构化日志](../sources/literature_screening_log_2026-10-08_colm2026_qcare_fulltext.json)。


## Phase 151：COLM 2026 judge reliability 与 executable logic benchmark

No Free Labels 指出 LLM judge 的 correctness 评估取决于 judge 自身能力和正确参考，错误参考可能伤害表现；LogicIF 以程序执行产生任务答案，并由两名专家检查自然语言指令是否完整表达代码。二者分别约束 judge gold 的独立性和形式正确性/自然语言语义忠实度的分层。GraphWalker、GDP-RAG 仅记录为题名/摘要级图 traversal 与 gap-aware evidence planning 邻居。它们都不替代 sense-bound gloss span support gold 或 proof replay。证据见Phase 151 深度报告和[机器日志](../sources/literature_screening_log_2026-10-08_colm2026_grounded_logic_addendum.json)。

## Phase 154：group-conditional risk control 与依赖校准边界

Salem et al. 的 HG-CRC 提出 LLM selective prediction 的层级 group-risk 同时控制，属于近期方法邻居（arXiv v1；页面未列已接收会议）。方法对节点作 Bonferroni 风险检验并 leaf-first 路由，但其正式 split 保证假设 calibration rows IID、测试点独立。项目多 surface/condition 观察的 edge/target/gloss 依赖不是该论文的分组假设；不能把泄漏连通组件直接视为 IID calibration examples。论文在 ARC 的经验零 violation 仅为 500 bootstrap 分辨率下限，MMLU-Pro 中有模型近乎全 abstain；分数不移植。本项目 strict NLI gate 目前要求一个 dev row/group_id，并把 split 与 calibration 使用同一个 group_id，故 Track A 多 surface 迁移需先定义独立校准单位和聚合后的路由 estimand。全文范围、假设和代码接口对照见Phase154报告及[筛读日志](../sources/literature_screening_log_2026-10-08_hierarchical_group_risk_control.json)。


## Phase 164：NeurIPS 2025 与 ICML 2025/2026 的 proof/verifier 邻接先例

NeurIPS 2025 的 APOLLO 已把 Lean 编译反馈、失败子目标定位、局部修复与独立 re-verification 组合进 theorem-proving 系统；Weaver 用 weak supervision 汇总多种 verifier/judge 输出；MuSLR 以正式逻辑规则评测多模态组合推理。ICML 2026 PMLR 306 的 *Beyond Theorem Proving* 把“验证已知命题”与 constructive formal problem-solving 区分，并给数学答案定义符号等价指标；*Learning to Self-Verify* 将 self-verification 和生成作为两个训练目标；ICML 2025 RULEBREAKERS 则展示形式规则应用可能与常识/事实预期冲突。

这些先例进一步排除 compiler-guided proof repair、proof sketch refinement、weak verifier fusion、自验证训练或一般 formal-rule benchmark 作为单独的新颖性主张。它们支持分开评估形式规格忠实度、proof-object 有效性、verifier 质量、sense-bound gloss-span 语义支持与常识 plausibility。目标项目的窄差异仍是假设，尚无匹配 gold/baseline。APOLLO 元数据页与 PDF 对第三作者姓名不一致，本轮标注为待核，不在文档中择一。筛读深度、去重、官方来源和检索限制见Phase164报告及[结构化日志](../sources/literature_screening_log_2026-10-08_icml2026_neurips2025_formal_verification.json)。

## Phase 165：ICLR 2026 autoformalization、proof-dependency DAG 与 verifier benchmark

ICLR 2026 *Mathesis* 把 informal mathematics→Lean statement→proof 作为端到端流程，并用 LLM-assisted LeanScorer 做 formalization semantic evaluation；其论文附录给出三位专家对 98 项的独立标注与一致性数据。该结果进一步收窄自然语言形式化与语义评测的宽泛新颖性，但研究对象是数学问题条件/结论，不是 WordNet sense-bound gloss spans。*Let's Explore Step by Step* 从 Lean proof dependencies 构造 DAG 并拓扑遍历，生成 proof-guided exploration；故通用 dependency DAG 与 topological traversal 本身不能作为新颖点，它也不处理词典来源 provenance 或 AND/OR lexical support。*SCI-Verifier* 以专家标注评估答案正确/等价；*Variation in Verification* 表明 verifier 质量随 generator 与 item difficulty 改变。它们不能提供 source-gloss entailment gold，提示未来需同一候选池、分层报告并把人工来源支持与 verifier 分数分开。四篇均为官方 PDF 定向章节筛读；不是 ICLR 主会全量 census。详见Phase165报告及[机器日志](../sources/literature_screening_log_2026-10-08_iclr2026_formalization_verification.json)。

## Phase 166：WordNet gloss 的 LLM sense-alignment 与 contextual WSD 先例

ACL Anthology v6 的 2026 WordNet/gloss lexical-relations 家族共九篇。本轮将此前仍停留在摘要级的四篇全部升级/复核：Ghizzota et al. 的 Latin LKG 用上下文句子和 sense gloss 做 WSD，并从已有图取 WordNet synset/hypernym；Kikuchi et al. 用 GPT-4o 将 WordNet gloss 与 EVP 释义做语义匹配并转移 CEFR sense labels；两者均对官方 PDF 的方法/评估/局限章节作定向核读。Lanz & Pecina 的 UMLS/WordNet term-definition retrieval 与 Redkar et al. 的 Konkani WordNet 资源整理仅摘要级。前两者排除“WordNet + LLM sense prediction”“LLM gloss-to-sense label transfer”作为宽泛新颖性，但不构成 gloss-span→typed AND/OR Horn support 或可重放证明基线。Kikuchi et al. 明言没有人工 spot-check transferred sense labels，故下游分类表现属于间接证据，不能当作对每条 gloss alignment 的直接验证。九条切片最终深度为全文 5、定向章节 2、摘要 2；没有召回率或全 ACL 完备性主张。详见Phase166报告、[机器日志](../sources/literature_screening_log_2026-10-08_acl2026_wordnet_slice_phase166.json)和[逐篇深度对账](../sources/acl_anthology_candidates_2026-10-08_v6_reconciled_phase166.json)。

## Phase 167：AAAI 2026 固定 ontology 的 NL→FOL、选择性形式化与规则执行先例

[Do LLMs Really Struggle at NL-FOL Translation?](https://ojs.aaai.org/index.php/AAAI/article/view/40258) 将 ontology extraction 与在给定 signature/gloss 下做 formula translation 分开，用 SMT equivalence 及 connective/quantifier/negation 扰动评估；作者把 ontology extraction 留作未来工作。[HBLR](https://ojs.aaai.org/index.php/AAAI/article/view/40434) 已有 selective translation 与 backward hypothesis reasoning。[StepFun-Formalizer](https://ojs.aaai.org/index.php/AAAI/article/view/40691) 是数学 autoformalization 的专门模型/数据训练路线。[Tax Reasoning](https://ojs.aaai.org/index.php/AAAI/article/view/41212)（AAAI special track）从 statutes/cases 生成 Prolog 并执行/拒答。这些宽泛方法已是 prior art；它们没有逐条 gold 标注 WordNet gloss span 对 sense-bound typed Horn relation 的支持，也没有 source-payload-bound proof replay。详细边界、逐篇筛读和限制见Phase167报告及[结构化日志](../sources/literature_screening_log_2026-10-08_aaai2026_formal_logic_neighbors.json)。

## Phase 177：结构引导逻辑形式与可验证过程监督

[SELF-KBQA](https://aclanthology.org/2026.findings-acl.177/)（Findings ACL 2026）展示结构化 KB 子图可以同时以拓扑模式与语义相关性约束可执行 logical-form 生成；该先例排除 subgraph-guided executable LF generation 的宽泛新意，但其逻辑形式受 Freebase schema/实体关系和 gold LF 监督，不是从 WordNet gloss 自举 typed Horn rule。Kim et al. 的 [VPS](https://arxiv.org/abs/2605.12519) 已被 COLM 2026 accepted list 收录，通过结构化 trace、确定性 claim extraction、领域 verifier 和 adaptive reward weighting 训练并分别评估答案与过程质量；其任务/ground truth 是 chess engine 与数学步骤信号，不判断 source text 对自然语言规则的语义支持。50 条 trace 的人评相关仅单一 annotator 与 Claude judge 相关，不是多人 IAA。

这两项工作要求将结构感知生成、形式执行、过程步骤校验、来源语义忠实度拆成不同构念。没有共同 WordNet sense/gloss-span gold 和 matched baseline 时，项目仍不能声称窄组合新颖或有效。本次为两篇官方/作者全文定向筛读，不是 ACL/COLM 全集盘点或系统综述；详见Phase177报告及[机器筛读日志](../sources/literature_screening_log_2026-10-08_structural_kbqa_and_process_verification.json)。

## Phase 183：正确的候选不必然有下游效用

COLM 2026 [Quokka](https://arxiv.org/html/2509.21629v4) 分开核验 loop invariant 的正确性与目标 assertion 的可证明性，并同时报告 verifier inconclusive、相对 base solver 的增量解决数和包含 LLM overhead 的端到端时间。GPT-5.2 在 60s 预算下报告 +21 项，在 500s 下 +1 项。其可迁移点是评测维度和预算记录方式；任务是程序 invariant synthesis，不是 gloss source support，绝不移植其分数或 soundness 声明到本项目。须保留人工 source-span support gold，并独立报告公式/类型有效性、certificate replay 和 proof utility。当前 title/版本及筛查限制见Phase183报告与[机器日志](../sources/literature_screening_log_2026-10-08_colm2026_verifier_utility_quokka.json)。

## Phase 201：ACL 2026 自然语言—符号逻辑视图对齐

| 工作 | 方法与评测 | 与本项目的边界 | 比较含义 |
|---|---|---|---|
| [Discovering a Shared Logical Subspace](https://aclanthology.org/2026.acl-long.1806/)（Fang et al., ACL 2026 Long Papers） | 对自然语言与符号证明/形式化的配对表示做 canonical-correlation 对齐，学习跨视图逻辑子空间，并在推理时 steering。评估 FOLIO、PrOntoQA、ProofWriter（OWA/CWA）上的五种开源模型；作者报告相对 greedy CoT 的准确率增益为 1.6–11 个百分点。 | 是 NLP 与符号逻辑联合表示及推理干预的主会先例，排除该宽泛组合本身的新颖性。它的主要终点是最终答案准确率；不做 WordNet sense/gloss 编译、不标注逐 span→Horn literal 的语义支持，也不报告 source-payload-bound proof replay。 | 可作为后续同一冻结 gloss/query 上“自然语言/符号双视图”推理条件的设计参考，但不能移植其准确率，也不是 gloss-support matched baseline。作者也将中间步骤 correctness/faithfulness 的细粒度评测列为未来方向。 |

此项为 ACL 官方记录和 PDF 定向章节筛读；不是 ACL 2026 全会逐篇重审或系统综述。详见Phase201 报告与[机器筛读日志](../sources/literature_screening_log_2026-10-08_acl2026_shared_logical_subspace_phase201.json)。

## Phase 203：ACL 2026 冲突判决中的文本/图推理 trace

| 工作 | 方法与证据 | 与本项目的边界 | 比较含义 |
|---|---|---|---|
| [KCR: Disentangling Reasoning Logic to Resolve Explicit Knowledge Conflicts](https://aclanthology.org/2026.acl-long.1451/)（ACL 2026 Long Papers） | 对 popQA/StrategyQA 的互相冲突上下文抽取文本 trace，并用 GPT-4o-mini 构造局部图与相关路径；用 JS-divergence coherence 和规范化编辑相似 consistency reward 做 GRPO。作者报告冲突判决任务上的模型改进；全文给出 8:1:1 split，LLM-as-judge 使用 GPT-4o-mini。 | 进一步排除“文本+图推理路径”“trace 一致性奖励”作为宽泛新颖点。其 reward 是表征/字符串相似度，不是 Horn soundness、source-span support 或独立 proof replay；不含 WordNet sense/release 或释义 span gold。 | 可借鉴区分 trace generation、LLM judge、人工来源支持与确定性 proof replay；不是词典 formalization matched baseline，分数不可横比。 |

定向官方 PDF 筛读，不是 ACL 2026 全会盘点。详细方法/范围与限制见Phase203报告及[机器日志](../sources/literature_screening_log_2026-10-08_acl2026_kcr_graph_reasoning_phase203.json)。
## Phase 217：来源忠实度、逻辑有效性与 plausibility 分层

定向筛读 FRANQ（Findings ACL 2026）、Min et al.（*SEM 2025）及 Bertolazzi et al.（Findings ACL 2026）。FRANQ 区分 claim 的外部事实正确性与其是否由检索上下文支持；AMR/NLI 全文显示结构化视图可能放大词汇/句法差异并诱发误判；Bertolazzi et al. 的官方摘要报告 validity 与 plausibility 表征对齐（本轮摘要级）。项目应分开记录固定 sense/release 词汇事实、gloss-span 对 typed literal 的支持、Horn 形式证明/重放、模型对 plausibility/表层 cue 的敏感性。此类先例不能替代项目 gold、matched baseline 或效果实验。详见Phase217报告与[机器筛读日志](../sources/literature_screening_log_2026-10-08_faithfulness_validity_plausibility_phase217.json)。
## Phase228：故障树/可靠性中的 pairwise interaction 先例

检索到长期存在的组件联合可靠性/失效重要度（JRI/JFI）、fault-tree gate-event joint importance、minimal cut set 重要度及近期 joint structural importance。故 pairwise interaction 本身不能作为新颖性主张。Phase227 的 all-head deterministic Horn closure-loss 口径与概率/可靠度敏感度不同，但没有公式级匹配比较；当前只可报告冻结图上的结构观察。检索边界和证据见Phase228及[机器日志](../sources/literature_screening_log_2026-10-08_reliability_interactions_phase228.json)。

## Phase232：NeurIPS 2026 LogicTree-RAG

检索并全文定向核读 NeurIPS 2026 接收论文 *LogicTree-RAG*。它已具备技术文档生成中的 hierarchical logic tree、source evidence spans、evidence-guided recursive generation、节点级 fully/partial/unsupported 支持评估（GPT-5 judge + 20-case human audit），及三位专利从业者的独立盲法人审。故“首次 logic tree + 来源证据 + evidence-faithfulness human audit”过宽，必须收窄。任务仍不同于 sense-bound WordNet gloss→typed AND/OR Horn support / proof replay；这种差异只是研究假设，不能当 novelty proof。见Phase232报告、[结构化日志](../sources/literature_screening_log_2026-10-08_logic_tree_rag_neurips2026_phase232.json)及[对照表](closest_work_comparison.md)。

## Phase237：LREC 2026 OEWN 跨语言层级嵌入去重对账

本轮最初把该文误识别为新发现；回查后确认它已在 2026-10-05 完成官方 18 页全文筛读并记录于 [`literature_screening_log_2026-10-05_recent_acl_wordnet_slice.json`](../sources/literature_screening_log_2026-10-05_recent_acl_wordnet_slice.json) 与本文件前述 `related_work.md` 详细段。Phase237 不增加文献数量，只把该既有全文证据补入最近工作矩阵，并从另一个官方入口重核 venue/书目信息。见Phase237对账报告及[去重记录](../sources/literature_screening_log_2026-10-08_lrec2026_wordnet_hyperbolic_phase237.json)。

## Phase249：ACL 2026 SATQuest 与 verifier-backed 逻辑评测

[SATQuest](https://aclanthology.org/2026.acl-long.96/) 用 CNF 生成五类 SAT 任务，PySAT 对结构化二进制输出做确定性核验，并沿 instance、problem type、question format 三轴组织评测。官方全文的主评测含 140 对 CNF，另有 3,000 对 RFT 数据。其受控 Math/DIMACS/合成叙事格式结果提醒：逻辑等价题面也需做配对呈现条件分析。该系统不处理 WordNet sense、gloss-span source support、typed Horn 或 witness provenance；其 80-instance failure audit 用 LLM-as-judge 并人工抽查 10%，不是 lexical semantic gold。因此 verifier-backed logic evaluation 与 multi-axis control 不能单独作为新意；本项目需分开评价形式检查、来源支持、proof replay、NLI 与下游效用。详见Phase249报告及[筛读日志](../sources/literature_screening_log_2026-10-08_satquest_acl2026_phase249.json)。

## Phase273：既有 APF 记录的补充核读与快照对账

[Solver-Independent Automated Problem Formulation](https://aclanthology.org/2026.findings-acl.102/) 已在 2026-10-06 筛读日志中作为邻接先例保留，并定向筛读 §3–4；本阶段纠正 2026-10-05 候选快照的陈旧 pending 状态，补充记录论文对 LLM ranking reference 的小规模人工核对（30 组要求、每组 15 个实例）及其评测边界。该先例排除宽泛“首次把自然语言要求形式化为可执行模型并实验评估”的说法。judge/reference 不是逐句/逐公式人工 gold，也不证明 source text 对公式忠实。它没有 WordNet sense、gloss-span 支持、AND/OR Horn 或 provenance-bound witness。项目窄假设仍待验证，不能由跨任务差异宣称新颖。本阶段没有新增候选或唯一论文。见Phase273报告、[既有筛读日志](../sources/literature_screening_log_2026-10-06_acl_formalization_2026.json)及[补充机器记录](../sources/literature_screening_log_2026-10-08_apf_findings_acl2026_phase273.json)。
