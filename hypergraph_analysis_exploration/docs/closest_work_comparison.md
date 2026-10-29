## 2026-10-12：跨任务结构表示与分析型 NLP（Phase276）

| 工作 | 方法与报告结果 | 对本项目主张的影响与边界 |
|---|---|---|
| [Lingua-Graph: A Unified Representation of Cross-Task Common Substructures for Analytic Language Processing](https://aclanthology.org/2026.acl-long.1129/)（Sun et al., ACL 2026 Long Papers） | 官方全文：提出 representation-then-decision 的 Analytic NLP；单根、token-anchored 的谓词—功能—论元 DAG，以节点自身/后代子图承载实体和事实；报告实体 span hostability 平均 89.82%，并在三个 OIE benchmark 报告 OIE@Lingua 结果。论文自报约 20% 训练样本人工审阅、100 条双评样本保守估计准确率 84%、κ≈0.63。 | 直接收窄“共享显式结构、局部子结构复用、可解释中间表示”的宽泛创新主张；提供表示 hostability/selectivity 与下游效果分层评测范例。它建模句子解析/实体事实片段，不表达 WordNet sense-bound Horn entailment、gloss-span→rule support、AND/OR witness proof replay 或 lexical NLI；hostability 不是语义蕴含正确率。项目的窄差异仍是假设，未由 gold 或 matched experiment 证实。官方论文列出的代码地址本轮返回 404，未复现。见[Phase276 汇报备忘](../../report/project_review_2026-10-29-current.md)。 |

本轮为单篇官方全文定向核读，不是系统综述或 novelty proof。详情见[Phase276 汇报备忘](../../report/project_review_2026-10-29-current.md)。

## 2026-10-08：推理轨迹否定特征与作者/模型 provenance（Phase264）

| 工作 | 方法与报告结果 | 与本项目的关系及边界 |
|---|---|---|
| [Negation in Reasoning Traces: Interpretable Signals of Correctness and Provenance](https://aclanthology.org/2026.naloma-1.4/)（Hammerla & Mehler, NALOMA 2026 workshop） | 将轨迹内显式否定分为 corrective/refining；在 GPQA Diamond、AIME 25、Nemotron-Math-HumanReasoning 与六个 LLM 上用 LightGBM 五折 CV 比较否定、结构和 embedding 特征。36 条轨迹/634 步人工复核的 human-human κ=.68，LLM-human κ=.37/.38；否定特征对正确性高于简单结构基线，但 embeddings 整体更强，最好结果是人类/LLM 作者分类。 | 其 provenance 指作者/模型归属分类；没有 source document lineage、gloss span 对 typed Horn literal 的支持判断或 proof witness replay。是 trace analysis/weak-label reliability 的邻接方法，不是项目的 gloss-to-logic、lexical NLI 或 source-bound proof matched baseline。 |

## 2026-10-08：当前矩阵到筛读日志的可追溯性复核（Phase262）

当前矩阵含 312 次外链、297 个唯一目标。使用 Phase256 冻结去重索引与当前 crosswalk CLI，289 个唯一目标可精确回指结构化筛读日志，302 次链接出现匹配；其余 8 个目标/10 次出现均为非论文资源：5 个代码/项目资源，以及 Princeton 官方 WordNet senseidx 文档、WordNet 3.0 下载和 WN30-lfs 归档。此前分类启发式把后面 3 个官方词典/下载资源误列为学术引用候选；Phase262 对这三个明确的文档/发行 URL 增加了非论文资源判定。该链接对账只说明矩阵链接是否能回指项目日志，不是系统综述检索覆盖率，也不判断学术相关性或发表新颖性。见Phase262 深度报告、[机器结果](../outputs/phase262/closest_work_log_crosswalk.json)和[source record](../sources/closest_work_current_matrix_crosswalk_2026-10-08_phase262.json)。

## 2026-10-08：WN30-lfs 的 WordNet 版本声明与 key 可迁移性（Phase259）

| 证据 | 核对结果 | 对比较的影响 |
|---|---|---|
| [WN30-lfs 原始 lineage 说明](https://ragerri.github.io/files/ilf.pdf)与[Princeton 归档](https://wordnetcode.princeton.edu/standoff-files/wn30-lfs.zip) | CICLing 2010 论文把资源描述为 WordNet 3.0 gloss 的 LF，XML 的 `word` 示例为 `lemma#POS#sense_number`。当前归档 XML 有 104,357 entries、104,321 unique keys、36 次重复；entry 无 release/offset 字段，root `version="1.0"` 是容器属性。 | 资源 lineage 可支持按声明的 WordNet 3.0 构建 release-bound crosswalk；不支持从 XML 自身重建 offset，也不支持把每个缺失 synset 都归因到 parse failure。 |
| [Princeton senseidx(5WN)](https://wordnet.princeton.edu/documentation/senseidx5wn) | 文档指出 `sense_key` 可索引到 sense number/offset，并说明 sense numbers 与 offsets 会跨版本变化。WN30-lfs key 不是该 `sense_key`。 | 阻止把 key 的编号直接当成跨版稳定 identity。Phase257 88.4599% 严格 ID coverage 保留；Phase258 gloss 命中仍为人工审查候选，未自动重映射。 |

结构审计方法、输入哈希与范围限制见Phase259 报告及[机器结果](../outputs/phase259/wn30_lfs_source_schema.json)。这为资源 identity 比较增加 lineage 依据，不评价 LF fidelity、项目效果或许可。

## 2026-10-08：WN30-lfs 未映射 key 的精确 gloss 候选诊断（Phase258）

| 子集 | 精确字符串诊断 | 对照边界 |
|---|---|---|
| Phase257 严格 join 未命中的 174 个 WN30-lfs key | 23 个同 lemma/POS 下有唯一 gloss 候选；1 个同 lemma/POS 候选有歧义；38 个在同 POS 但不同 lemma 下出现唯一 gloss 候选；38 个有同 lemma/POS 但 gloss 不精确匹配；74 个没有精确 lemma/POS 或 gloss 候选。4 条候选只在移除 `SOMETHING_N` 后命中。 | gloss 字符串匹配不构成 sense 金标或 release provenance。异 lemma exact match 可包含拼写/别名差异，也可能和 key 的 named entity 冲突；例如 `Twentieth_Amendment` 命中 `nineteenth_amendment` 的同一 gloss。所有候选只供人工/schema 追查，**不改变** Phase257 的 104,081/117,659（88.4599%）严格 ID coverage。见Phase258报告、[机器候选诊断](../outputs/phase258/wn30_lfs_unmapped_diagnostic.json)、[CLI](../src/analysis/audit_wn30_lfs_unmapped_entries.py)。 |

## 2026-10-08：WN30-lfs 的 WordNet 3.0 synset 身份对账（Phase257）

| 资源 | 本轮 ID 对账 | 含义与限制 |
|---|---|---|
| [WN30-lfs repository archive](https://wordnetcode.princeton.edu/standoff-files/wn30-lfs.zip) × [Princeton WordNet 3.0](https://wordnetcode.princeton.edu/3.0/WordNet-3.0.tar.gz) | 用 `index.sense` 严格连接 `lemma#pos#sense_number` 到 `(POS, offset)`，并与 3.0 四个 `data.*` 文件交叉校验：基准 117,659 synsets；104,081 个唯一 ID 匹配，13,578 个缺失，0 个映射到库外，严格身份覆盖 88.4599%。另有 174 个 XML keys 未严格解析；不使用 lemma/POS-only 猜测。 | 替代 Phase256 的粗略 entry-count ratio 88.69%；本数是 ID 可比性/资源覆盖，绝非 LF 语义准确率。多个 entry 可指同一 synset、状态可冲突；报告单列重复键、多词形与 status。完整 missing ID、未映射 key 和 hashes 在[机器输出](../outputs/phase257/wn30_lfs_synset_crosswalk.json)及[source record](../sources/wn30_lfs_synset_crosswalk_2026-10-08_phase257.json)中；方法及限制见Phase257报告。本轮未评估 WN30-lfs 许可、LF 语义或重放工具链。 |

## 2026-10-08：WordNet gloss→逻辑形式资源与一致性复核（Phase256）

| 工作/资源 | 本轮直接核验 | 对本项目主张的影响与边界 |
|---|---|---|
| [eXtended WordNet: Progress Report](https://digital.library.unt.edu/ark:/67531/metadc83309/)（Mihalcea & Moldovan, NAACL 2001 WordNet workshop） | 六页作者 PDF 可取得；定向核读其阶段、格式、置信度与标注程序部分。报告介绍 preprocessing/parsing、WSD、logical-form transformation、topical relation extraction 四阶段；正文实证重点是前两阶段和 1,000 条 noun.artifact / verb.social gloss pilot。tagger agreement + 人工复核是标注置信流程，不是 LF 语义金标准。 | 更精确地定位 XWN：阶段报告不是完整 LF 转换/端到端忠实度评测。Phase255 的“仅摘要/元数据”判断已由本轮更正；历史快照保留原记录。 |
| [WN30-lfs repository archive](https://wordnetcode.princeton.edu/standoff-files/wn30-lfs.zip)（ISI/Boeing WordNet 3.0 资源） | Princeton 归档 ZIP 可下载并解析：单个 XML，104,357 entries 均有 gloss 与 LF；52,743 `partial`、51,614 `complete`；13,565 entries 含 28,872 个 sub-LF。ILF-WN 引述的 WordNet 总量为 117,659 synsets；104,357/117,659=88.69% 只是数量比，本轮未做 offset join，不能解释为 recall。归档未含 README/license 文件。 | 从“仅由论文提及”升级为已直接取得并做结构盘点的资源；不等于语义质量、完整覆盖、可再分发许可或 LFToolkit 重放已验证。没有把资源冒充独立系统论文。 |
| [Treebanks of Logical Forms: they are Useful Only if Consistent](https://iris.unive.it/handle/10278/35936)（Delmonte & Rotondi, 2012） | 全文报告其 parser 在 132,587 个 XWN LF 中判定 71,658 个含 disconnected variables（54.05%）。该数是 parser 定义的连通性指标，不是人工裁决的 gloss-span 语义支持率。 | 已有 XWN/WN30-lfs/ILF 资源一致性审计先例；需撤回“此前无人量化 LF 资源错误/一致性”的宽泛说法。 |
| [A Logical Form Parser for Correction and Consistency Checking of LF Resources](https://iris.unive.it/handle/10278/3660559)（Delmonte & Rotondi, NLPCS 2015） | 全文报告自动修正后 disconnected XWN LF 降为 31,583/132,587（23.82%），再经人工干预作者报告总错误低于 15%。自动修正效果由同一 parser 统计不一致；低于 15% 是作者报告值。 | LF parser、结构检查和自动修正均有既有工作。其指标/核验非独立语义 gold，不能替代对 gloss 是否支持谓词、论元方向或 Horn clause 的人工裁决。 |

Phase256 对 Phase255 作定向更正：XWN 全文来源可用且已筛读指定章节；WN30-lfs 资源已结构解析；2012/2015 的 LF 连通性审计与自动修正作为直接 prior art 纳入。五类证据须分开：资源记录数量、解析状态、变量连通性、释义语义支持、证明有效性。此处 88.69% 是历史计数比；Phase257 已用 synset ID crosswalk 得到 88.4599% 的严格 ID 覆盖。2015 修正数也不是独立语义准确率。详情见Phase256 报告、[机器日志](../sources/literature_screening_log_2026-10-08_phase256_xwn_wn30_resource_reaudit.json)和[Phase257 crosswalk](../outputs/phase257/wn30_lfs_synset_crosswalk.json)。

## 2026-10-08：WordNet gloss→逻辑形式沿革与逻辑形式评测（Phase255）

| 工作 | 全文/记录核验到的方法与结果 | 对本项目主张的影响 |
|---|---|---|
| [eXtended WordNet: Progress Report](https://digital.library.unt.edu/ark:/67531/metadc83309/)（Mihalcea & Moldovan, NAACL 2001 WordNet workshop） | 当时只核 UNT 馆藏摘要与书目记录；该状态在 Phase256 被更正。 | 仅为历史快照，当前核验见 Phase256。 |
| [ILF-WN](https://doi.org/10.1007/978-3-642-12116-6_3)（Agerri & Peñas, CICLing 2010） | 全文筛读 12 页：WordNet 3.0 gloss 经预处理、POS 与依存分析生成结构化 ILF-WN；表示是扁平 neo-Davidsonian entity/relation 中间形式，非标准 FOL。`conj_or` 是协调关系，不等价于显式 Horn 规则析取。sense offset 仅对单义词加入，本版本未运行 WSD；定量 gold evaluation 被作者推迟。论文直接比较 XWN 2 与 USC/ISI WN30-lfs。 | 属于直接自动 gloss→形式结构先例，排除“首次自动逻辑化/形式化”的宽泛说法。应匹配比较 gloss 覆盖、WSD、AND/OR 语义、scope、span 支持和证明；ILF-WN 不是本项目规则级 source-support gold 或 proof baseline。 |
| [WN30-lfs](https://doi.org/10.1007/978-3-642-12116-6_3)（ISI/Boeing WordNet 3.0 LF resource，作为 ILF-WN 论文讨论的既有资源） | ILF-WN 将其描述为 Charniak parser 与 LFToolkit 生成的平行 WordNet 3.0 逻辑形式资源，并定性讨论若干变量/连通性/协同结构问题。本轮没有找到独立论文全文或数据/代码重放，故只作为该论文引述的资源，不单列独立出版系统。 | 对比矩阵应记录资源和系统论文的关系，避免把被比较资源重复当作新论文证据；具体表示与覆盖需拿到资源后复核。 |
| [A First Evaluation of Logic Form Identification Systems](https://aclanthology.org/W04-0810/)（Rus, SENSEVAL-3 2004） | 全文 4 页：通用英语句子 LF benchmark 有 300 句，4,155 arguments、2,398 predicates；自动初始形式经双标检查并由 moderator 处理分歧。按 argument/predicate 与整句 exact-match 分报；不是 gloss literal support benchmark。 | 一般 LF gold、双人复核/裁决及细粒度/exact 指标均有早期先例；可借鉴指标分层，不得将论文分数当作 WordNet gloss source-support 结果。 |

Phase255 收紧后的剩余假设不是“能否自动生成形式表示”，而是：在固定 sense/release 与同一 gold 上，逐条方向化 typed rule/literal 能否得到人工裁决的 gloss-span 支持，并由独立 checker 重放来源绑定证明。Phase256 又纳入既有 LF 连通性检测/修正研究，因此不能把结构一致性检查本身作为差异。当前原型仍从人审结构化 claim 编译，和原始 gloss parser 的输入边界不同。筛读细节见Phase255 深度报告、Phase256 更正报告与[Phase255 日志](../sources/literature_screening_log_2026-10-08_phase255_wordnet_logic_lineage.json)。

## 2026-10-08：WordNet gloss→逻辑形式的历史直接先例与义项粒度（Phase254）

| 工作 | 全文/记录核验到的方法与结果 | 对本项目主张的影响 |
|---|---|---|
| [Moldovan & Rus, “Transformation of WordNet Glosses into Logic Forms”](https://cdn.aaai.org/FLAIRS/2001/FLAIRS01-088.pdf)（FLAIRS 2001）；同作者 ACL companion：[“Logic Form Transformation of WordNet and its Applicability to Question Answering”](https://aclanthology.org/P01-1052/)（ACL 2001） | FLAIRS 全文：WordNet 谓词编码词元/POS/义项，动词显式保留 event/subject/object 槽位，修饰语共享论元，AND/OR 作为 conjunction predicates；句法解析后生成 LFT，并用于 QA。10,000 条 WordNet 1.6 名词 gloss 用于语法频率；400 条 artifact 层级扩展名词 gloss 有人工 LFT，规则覆盖率从 72.5% 增至 81%。这是 LFT 覆盖率，不是语义精确率或证明正确率。方法明确忽略量词/模态、否定、时态、复数/集合和比较级。ACL companion 本轮只核官方记录/摘要，未把它算作独立系统。 | **重大直接先例。** 必须撤回“首次将 WordNet gloss 编为逻辑形式/义项化谓词/论元结构/AND-OR 组合”以及“首次用于问答/推理”的说法。可检验的剩余差异只能暂列假设：逐个方向化 typed literal 的 gloss-span 支持裁决、与语义范围相关的现代表达、来源绑定 witness 独立重放；仍须重建/适配 2001 LFT 基线并把解析覆盖、语义忠实度、proof validity 分开测。 |
| [Word Sense Linking (Bejgu et al., Findings ACL 2024)](https://aclanthology.org/2024.findings-acl.851/) | 从开放文本联合检测待消歧 span 并链接到参考词义库存；论文将评测覆盖扩展至 11,623 个标注实例。无 concept-detection oracle 设置报告 P/R/F1=75.2/76.7/75.9；小型三专家复标子集 κ=.83。 | span 检测+义项链接是近期上游先例；它的 contextual word spans 不是 gloss 内支持某条形式 literal 的证据 span，也不编译规则或验证证明。分数不可与本项目 source-support/proof 指标比较。 |
| [Analyzing Homonymy Disambiguation Capabilities of Pretrained Language Models (Proietti et al., LREC-COLING 2024)](https://aclanthology.org/2024.lrec-main.83/) | 构造 WordNet 义项的粗粒度 homonymy 分组并测上下文消歧；官方摘要报告 homonymy 粒度最高 95% accuracy。全文筛读显示资源映射先由三位语言学家覆盖抽样子集，之后还有最高一致度标注者及自动/启发式扩展。 | 义项粒度与映射质量必须作为 gold/baseline 的显式变量；95% 是粗粒度 homonymy 任务结果，不能当成 fine-grained sense accuracy，更不能当 gloss-rule support 结果。 |

筛读深度、报告数字、局限及正式来源见[Phase254 结构化筛读日志](../sources/literature_screening_log_2026-10-08_phase254_direct_prior_art.json)与深度审计。其中 FLAIRS 2001 为全文；ACL 2001 companion 仅元数据/摘要；2024 两篇全文定向筛读。此为少量定向筛查，不表示系统检索完成或新颖性成立。

## 2026-10-08：联合重要度与 basis 删除交互（Phase228）

| 工作 | 方法与论文内任务 | 与 Phase227 的边界 |
|---|---|---|
| [Joint reliability/failure importance](https://www.sciencedirect.com/science/article/abs/pii/S0377221706008010)（Gao et al., EJOR 2007） | 对 coherent system 定义两组件 JRI/JFI，并推广到多组件，量化组件可靠度/失效改变对系统结果的联合响应。 | 关闭“组件交互只存在单变量分析”的宽泛说法；其目标是系统可靠性/失效响应，不是遍历所有 Horn heads 的确定性闭包损失。 |
| [Fault-tree gate-event JRI](https://www.sciencedirect.com/science/article/abs/pii/S0951832099000794)（Hong, Koo & Lie, 2000） | 研究两个 gate events 的 joint reliability importance，并讨论其与 minimal cut sets 的关系。 | 故障树中事件组合与最小割集关系已有直接先例；Phase227 未计算顶事件概率或最小割集。 |
| [Joint structural importance](https://www.sciencedirect.com/science/article/abs/pii/S0377042725005710)（2026） | 以 Logic Differential Calculus 研究 coherent system 中两个或更多组件的位置结构重要度。 | 结构性联合指标也有近期先例；目前未做公式级 matched comparison，不能声称 Phase227 与 JSI 等价或优越。 |

Phase227 的 joint-only head loss 在数学上恰是 head-level 二元素最小删除割集实例，故与 minimal-cut-set 思路的关系比一般“交互”类比更直接。它尚未实现全阶割集枚举，也不对组件失效概率、顶事件风险或 source 文档干预作解释。任何词义来源冗余、语义独立性或下游效用都需要 source mapping 和人工 gold 支持。本轮基于摘要/元数据的文献边界与证据限制见Phase228报告及[筛读日志](../sources/literature_screening_log_2026-10-08_reliability_interactions_phase228.json)。

## 2026-10-08：形式验证和逻辑有效性评测近邻（Phase159）

| 工作 | 方法与论文内任务 | 与本项目的边界 |
|---|---|---|
| [T²](https://aclanthology.org/2026.acl-industry.150/)（ACL 2026 Industry Track） | 以 Lean 依赖中的 successor theorem 编译测试评估生成 theorem，关注独立编译指标会漏掉的语义错误；NL description 只做 10 条抽样人工核验。 | 是下游依赖行为测试先例，不判定源 gloss 是否支持某个 sense-specific typed rule；成功 successor 编译也不是对 gloss-to-rule fidelity 的保证。 |
| [FoVer](https://aclanthology.org/2026.findings-acl.403/)（Findings ACL 2026） | Z3/Isabelle 产生形式推理步骤标签并训练分类 PRM；在包括 ANLI、HANS 的 NLI 基准评估 PRM。 | 形式 verifier 监督与跨任务 PRM 评估先例；NLI 是评测域，不是该数据的 gloss-span semantic gold，也非 lexical-rule baseline。 |
| [SemEval-2026 Task 11](https://aclanthology.org/2026.semeval-1.450/)（SemEval workshop） | 受控 syllogism 评估 validity、plausibility、irrelevant-premise filtering 及 multilingual robustness。 | 可启发独立 plausibility/distractor slices；模板真值不能移植为自然 WordNet gloss 支持标签。 |

筛读只覆盖三篇定向选文，不穷尽各会场。完整范围、证据和限制见Phase159与[机器日志](../sources/literature_screening_log_2026-10-08_formal_correctness_nli_addendum.json)。

## 2026-10-08：层次化机检证明搜索近邻（Phase182）

| 工作 | 方法与论文内任务 | 与本项目的边界 |
|---|---|---|
| [Goedel-Code-Prover](https://arxiv.org/html/2603.19329)（COLM 2026） | 从已形式化 Lean 规格开始，递归提出辅助引理，要求 constructive proof reconstruction 证明合取引理蕴含父目标；QuickCheck 随机找反例，最终证明由 Lean kernel 检查。427 项 code-verification benchmark 报告 62.0% overall prove success；与 pass@128 基线非 compute-matched。 | proof decomposition / tree、形式重构和 kernel-checked artifact 均有近期主会先例；其任务明确不含自然语言到形式规格的翻译，不判断 source span 对 lexical rule 的支持，不是 WordNet matched baseline。项目窄差异仍是待证的 sense/release-bound gloss-span→typed Horn support 和来源绑定证书重放。 |

录用状态核对[COLM 2026 官方目录](https://colm.eventhosts.cc/Conferences/2026/AcceptedPapers)，全文核读[作者论文](https://arxiv.org/html/2603.19329)；详见Phase182及[机器日志](../sources/literature_screening_log_2026-10-08_colm2026_hierarchical_code_proof.json)。单篇定向筛查，不是 COLM census 或新颖性证明。

## 2026-10-08：分层 selective risk control 邻接方法（Phase154）

| 工作 | 方法和适用条件 | 与本项目边界 |
|---|---|---|
| [Hierarchical Group-Conditional Conformal Risk Control for Selective Prediction in Language Models](https://arxiv.org/abs/2607.24562)（Salem et al., arXiv 2026 preprint） | 对 user-defined group hierarchy 中各节点做 Bonferroni simultaneous selective-risk certification；leaf-first 阈值回退。形式 split variant 假设 IID calibration examples + independent test point。论文用 Qwen3-4B/Llama-3.1-8B/Gemma-3-4B 在 ARC Challenge、MMLU-Pro 评估；作者明确 ARC 500 bootstrap 的零 violation 是经验上界，不是“零风险”，且 abstention/participation 有成本。 | 限制“首次 hierarchical group-risk abstention”宽泛主张；可在研究者预先指定条件/POS-specific risk 时作 adapted-method 参照。它的分层 membership 不是依赖 observation cluster 校正，不能证明 680 surfaces/两种 context 条件 IID，也不是 WordNet gloss-NLI baseline。代码仅承诺 acceptance 后发布，未独立复现。 |

它是新近 arXiv 预印本，记录为方法邻居而非顶会录用或系统审查。严格保证假设、实验边界与项目代码对照见Phase154和[筛读日志](../sources/literature_screening_log_2026-10-08_hierarchical_group_risk_control.json)。

## 2026-10-08：人类 gold、可执行逻辑 instruction 与图式系统近邻

| 工作 | 已核实的证据 | 对本项目的边界 |
|---|---|---|
| [No Free Labels](https://arxiv.org/abs/2503.05061)（COLM 2026） | 160 个专家写作问题；1,200 个答案各有三份专家正确性标注。LLM judge 与人类的一致度依赖 judge 是否会答题；正确参考改善一致度，错误参考可变差。 | 人工 gold 与参考正确性是 judge 可靠性关键；一般 human-grounded correctness judging 已有先例。不是 lexical span support/NLI gold。 |
| [LogicIF](https://arxiv.org/abs/2508.09125)（COLM 2026） | 426 个代码合成 logic-rich 指令任务、3,050 执行用例；每条指令由两名专家核查，报告 97% fully correct、97.79% agreement。 | 可执行程序 oracle + 自然语言忠实度人审已有先例；真实 WordNet gloss 没有程序 oracle，仍需 sense-linked source-span human gold。非 gloss compiler/proof baseline。 |
| [GraphWalker](https://arxiv.org/abs/2603.28533)（COLM 2026；摘要级） | 随机游走合成轨迹、stage-wise SFT 与 KGQA OOD traversal。 | 图 traversal/agent 先例；不做 gloss→Horn、source-span 或 proof replay。 |
| [GDP-RAG](https://arxiv.org/abs/2606.22681)（COLM 2026；摘要级） | 检索后按已知信息/未解缺口组织多跳 query 与 evidence-bearing trajectory。 | Gap-aware retrieval planning 邻接工作；不做 lexical source-support 或符号规则证明。 |

均为 COLM 2026 定向筛查；前两篇全文，后两篇仅标题/摘要。范围与综合见Phase 151及[结构化日志](../sources/literature_screening_log_2026-10-08_colm2026_grounded_logic_addendum.json)。

## 2026-10-08：Q-CARE 与原子 claim-to-evidence 评测

| 工作 | 任务和证据 | 与本项目的对照结论 |
|---|---|---|
| [Q-CARE](https://arxiv.org/abs/2608.11238)（Choi et al., COLM 2026） | Query/answer decomposition 后检查 sub-query–chunk、sub-query–claim、claim–chunk pairwise alignment；320 个 query、567 个 sub-query、7,907 条 claim 的人标 benchmark，三人独立标注、多数裁决，alignment Fleiss’ κ=.801–.891。自动 checker 默认是单个 Qwen3 模型；同模型三次运行的 alpha 只表示稳定性。 | 关闭一般 atomic claim decomposition、claim-to-evidence 支持和人标 verifiability 评价作为宽泛新意。可作未来 pairwise-support baseline 设计参照，但其 RAG claim↔chunk 不是 WordNet sense-bound gloss-span→directional Horn literal；无 AND/OR fidelity 或独立 proof replay，不能直接比较分数。 |

筛读边界与后续约束见Phase 150和[结构化日志](../sources/literature_screening_log_2026-10-08_colm2026_qcare_fulltext.json)。以下为既有逐项比较矩阵。

## 2026-10-07：lex-NLI 与形式证明的最新强邻接工作

de Jong et al., [*Explaining Textual Entailment with Lexical Entailments*](https://arxiv.org/abs/2609.32491)（AKBC 2026 接收，workshop 尚未举行）为 362 个 SNLI/SICK entailment pair 建立了多参考 lex-set 解释 gold，并将 LLM 提议的词汇关系作为 Lexical KB 输入 LangPro。文中 29% lex sets 为空；经裁决仍有 139/362 个例子保留多个有效关系集合。最佳 LLM intrinsic micro-F1 为 73.1（标注者平均 84.9）；LangPro+WordNet 在 1,000 SNLI entailment pairs 上证明 157 项，LLM+WordNet agentic 设置最高为 212 项。作者又发现，证明覆盖的额外提升中不少来自语义不可靠关系或对 parser/prover 缺陷的补偿。

| 维度 | lex-NLI (AKBC 2026) | 本项目当前路径 |
|---|---|---|
| 输入单位 | SNLI/SICK premise–hypothesis entailment pair | 版本化 WordNet sense/gloss |
| 结构输出 | 解释该句对的有向词汇 entailment 集；允许多个有效 gold | gloss 内 AND/OR 公式、方向与 rule/literal/source-span provenance；当前 compiler 仅一元共享变量受限片段 |
| 证明器角色 | LangPro 对输入句对作 natural-logic proof search | 正 Datalog certificate/countermodel 和 witness replay 针对给定形式程序 |
| gold 证据 | 多 annotator lex sets + adjudication；部分解释存在 legitimate alternatives | 尚无真实 gloss annotation returns、adjudicated gold 或 IAA |
| 独特风险 | proof coverage 可被 unsound lexical relation 或 parser/prover bug 抬高 | replay 能验证输入程序内部形式性，仍须验证 gloss span 是否支持每条方向 literal |

该先例排除“结构化词汇解释 + 人工评测 + prover”作为独立宽泛创新点。当前只能提出待检验问题：是否能在相同义项、定义输入和盲化 gold 上做到对每条有类型规则 literal 的 source-span 支持，并使 proof/witness 可独立重放。论文分数不可直接与本项目横比；一旦有授权的 gold，应适配相同输入和数据切分基线，并将语义正确性与 proof coverage 拆开。详细方法/限制见全文筛读报告。

## 2026-10-06：声明式 FOL/NLI 合成与证明注释近邻

[Unigram-FOL](https://aclanthology.org/2024.emnlp-main.301/) 用声明式、上下文敏感的语法生成简化英语与 TPTP 对照样本，solver 负责 NLI 标签，Vampire 为 entailment 样例提供 proof annotations；全文筛读见[日志](../sources/literature_screening_log_2026-10-06_unigram_fol.json)。它启发项目建立量词/否定/条件句/多前提组合的可控逻辑压力集，并将形式 oracle 与 proof trace 版本化。其输入由模板生成、不包含真实词典释义；正式证明只针对生成的 FOL，不能证明英语表述忠实，也不替代 gloss-span 支持人工 gold。可作为逻辑编译器/推理器测试设计，不是端到端 WordNet baseline。


[LREC-COLING 2024 Diff-Comb Explainer](https://aclanthology.org/2024.lrec-main.40/) 将检索事实和候选答案构成加权图，以 ILP 约束选子图，并分报答案准确率、解释 Precision@K、解释一致性和 answer/explanation faithfulness。完整筛读见[日志](../sources/literature_screening_log_2026-10-06_diff_comb_explainer.json)。它提示本项目不能以 NLI 标签或证明可回放率单独代替端到端解释质量；但其 faithfulness 不是原文蕴含或来源跨度指标，且背景包含 ConceptNet `is-a` facts。它是证据选择与指标分轴的邻接参照，不是 gloss-to-Horn 或 source-only proof baseline。


## 2026-10-06：ACL 2024 NL→FOL 评测近邻

Yang et al. 的 [MALLS / LogicLLaMA](https://aclanthology.org/2024.acl-long.375/) 已提供大规模句子级自然语言到 FOL 翻译数据、CFG 语法过滤、1K 人工评估子集和错误模式驱动过滤；本轮官方全文筛读见[日志](../sources/literature_screening_log_2026-10-06_malls_nl_fol.json)。它覆盖形式化翻译和人工对齐评测，但不处理 WordNet sense/gloss、词汇关系方向、逐规则来源 span 或 proof provenance。因此它排除“NL→FOL + 语法检查 + 人工评估”这一宽泛新颖性说法；若做适配 baseline，需在同一 gloss 候选和双人裁决 gold 上重跑，并独立测源文支持。

Liu 的 [Code4Logic](https://aclanthology.org/2025.naacl-long.547/) 用渐进式 Python 代码生成作 NL→FOL 中间步骤，并将公式用于 Prover9/Pyke 下游任务；官方全文定向筛读见[日志](../sources/literature_screening_log_2026-10-06_code4logic.json)。论文在 FOLIO/MALLS 报告其 Logic Equivalence 指标，并在 LogicNLI、RuleTaker、VitaminC 报告下游结果；这些是论文自身任务与指标，不是 gloss-source support。它进一步排除“NL→FOL 代码桥接并调用 prover”作为单独新颖点。适配时要共享 sense-linked gloss、预算、候选和盲标 gold，并把公式质量、逐 claim 来源支持与证明重放分开报告。

Saparina & Lapata 的 [Disambiguate First, Parse Later](https://aclanthology.org/2025.findings-acl.863/) 先为歧义 text-to-SQL 问句生成多种自然语言读法、补全可能遗漏的解释，再逐一翻译 SQL；全文筛读见[日志](../sources/literature_screening_log_2026-10-06_saparina_parse_later.json)。它提示本项目应把候选 sense/解释覆盖与后续 AST/Horn 解析分开评估，并保留歧义及多解；但数据库 schema 下的问句歧义不等于词汇 sense linking，其 SQL 执行匹配也不是 gloss-span semantic support 或证明证书。该工作排除“歧义先解析、再形式化”和“多解释覆盖评测”作为单独 novelty。



## 2026-10-06：ACL Anthology 2023 固定候选切片

同一固定候选库在 2023 年的 12 条待筛记录完成单人题名/摘要初筛：0 direct neighbor、7 adjacent、4 background、1 exclude。逐条理由见[结构化日志](../sources/literature_screening_log_2026-10-06_acl_wordnet_direct_2023.json)。没有直接近邻命中只表示该检索词族和候选框内的筛选结果，不表示不存在相关工作。

- Wojtasik et al., [Wordnet for Definition Augmentation with Encoder-Decoder Architecture](https://aclanthology.org/2023.gwc-1.6/) 使用 plWordNet 进行释义文本数据增强，并定性评估生成样本；这是 definition augmentation 先例，不是逻辑形式化或 entailment verifier。
- Oliveira, [On the Acquisition of WordNet Relations in Portuguese from Pretrained Masked Language Models](https://aclanthology.org/2023.gwc-1.5/) 以 masked patterns 和预训练 BERT 预测 synset/词语间同义、反义、上下位关系；属于 relation acquisition 近邻，没有以选定 gloss 作为逐规则来源证据。
- Koeva & Hristov, [Resolving Multiple Hyperonymy](https://aclanthology.org/2023.gwc-1.41/) 基于 WordNet 多重 hypernymy 的语义分析重新分类关系，进一步说明词汇层级和继承关系的结构修订已有先例；并非 gloss→Horn 规则编译。

这三类工作可补入广义对照地图，但只能在同一任务 gold 上适配后比较，不能借用其各自资源增强、relation prediction 或结构分析成绩作为本项目结果。


## 2026-10-06：ACL Anthology 2016–2019 固定候选切片

固定候选库的 `wordnet_gloss_lexical_relations` 族中，2016–2019 年尚待筛的 82 条记录已完成单人题名/摘要初筛：1 direct neighbor、43 adjacent、35 background、3 exclude。逐条判定及输入文件 SHA-256 见[结构化日志](../sources/literature_screening_log_2026-10-06_acl_wordnet_direct_2016_2019.json)。这不是跨库系统综述；除已核读的直接先例和两篇高优先相邻工作外，其余保留记录仍是摘要筛查。

- **Almiman & Ramsay (RANLP 2017)** 是此切片唯一直接定义→推理规则近邻：用英语词典（包括 WordNet）将 word:definition 转换为自然语言方向规则，并对 200 条规则做人审。论文细节已记录于[定义到规则全文筛读日志](../sources/literature_screening_log_2026-10-05_definition_to_rules.json)。
- **Silva et al. (CogALex 2016)** 对 100 条 WordNet 名词/动词 gloss 做语义角色分析与人工分段标注，归纳 supertype、essential differentia 与非本质成分，并统计其句法模式；自动分类器是未来工作。它排除“首次分析 WordNet gloss 内部结构”的宽泛主张，但没有实现方向性规则抽取或蕴含评测。[官方全文](https://aclanthology.org/W16-5323.pdf)
- **Nishida et al. (RepL4NLP 2018)** 将上下文注意力下的 WordNet 定义嵌入加入 SNLI/MNLI 句子编码器；多义词用按 WordNet synset 频率排序的最多五条定义。它是定义增强 NLI 的方法先例，但任务是句对分类，不判断单条 gloss 对方向 claim 的支持，也没有显式规则、来源 span 或证明证书。[官方全文](https://aclanthology.org/W18-3007.pdf)
- **Rademaker et al. (GWC 2019)** 的 Princeton Annotated Gloss Corpus 工作连接 gloss 词形与上下文 WordNet 义项；属于 sense/source 对齐资源先例，不是规则蕴含系统。[论文页](https://aclanthology.org/2019.gwc-1.48/)

因此，定义解析、gloss 语义角色、基于定义的 NLI 和 gloss 词义标注都已有先例；需要与这些工作区分的是联合任务和可测结果，而不是分别重新包装已有模块。全文筛读发现、标注差异与未筛候选边界见上述日志。

## 2026-10-06：WordNet gloss、taxonomy 与传递性近邻

定向补查发现 Greco et al., [Talking the Talk Does Not Entail Walking the Walk](https://aclanthology.org/2024.findings-emnlp.881/)（Findings of EMNLP 2024）：八种 LLM 在 WordNet/HyperLex 动词对上做 lexical-entailment 分类；WordNet 提示直接附上对应 synset 的 gloss，并使用三种提示及零/少样本设置。该论文是应纳入的直接 LLM baseline 候选，说明“sense-associated WordNet gloss + 方向性词汇蕴含判断”已有近期先例。它未做同设置有/无 gloss 消融，标签对齐资源关系而非 span-support gold，也无 gloss→显式规则编译、source-span 证据或可独立重放证明。逐项边界与方法数据见[筛读日志](../sources/literature_screening_log_2026-10-06_definition_entailment_supplement.json)。

**ACL 2026 的结构证书近邻**：[From Trajectories to Graphs](https://aclanthology.org/2026.acl-long.2004/) 将候选推理表示为 interface-typed DAG，以紧凑接口证书和确定性 gate 检查合并操作的无环性、命名空间闭合、schema 与终端格式，再调用任务 verifier。作者明确限定该 gate 只证明 structural runnability；语义正确性由外部 verifier 决定。论文报告 MATH L5 下 SemanticGraft 的 verifier-runnable rate 为 92.8%，string-merge 为 41.2%，仅是其任务上的结构运行指标。它不是 WordNet/gloss baseline，但排除了“DAG + 可审计结构证书 + verifier gate”本身作为充分新颖点。项目可能的差异应落在 sense/release 绑定、每条 Horn 规则到 gloss span 的人工支持，以及能否独立回放 source-grounded entailment；这些都仍待 gold 和匹配实验验证。[官方全文筛读日志](../sources/literature_screening_log_2026-10-06_contract_checked_dag.json)。

同日筛读的 SemEval 2026 Task 5 系统论文补充了**分级词义可置信度**方法近邻。GuysLLM 将故事语境与候选 sense definition/example 作为 NLI 输入，微调 DeBERTa-v3-large 做标量回归；SemTechLab/HINTS 使用 NLI-MPNet、目标词 span 特征及对 1–5 人类评分分布的 KL 训练。[两篇官方论文](https://aclanthology.org/2026.semeval-1.314/)与[HINTS 论文](https://aclanthology.org/2026.semeval-1.284/)均属于 SemEval workshop Task 5 系统论文，其任务是上下文中的 graded sense plausibility，不是 gloss 命题对方向关系的 source-support 判断。报告分数不能移作本项目基线；可在同一 gold 上改造为 NLI/打分候选，并保持目标词 span 与 gloss 来源证据 span 的标注分离。筛读边界见[结构化日志](../sources/literature_screening_log_2026-10-06_semeval_word_sense_plausibility.json)。

### SemEval 2026 Task 11：形式有效性与内容合理性的分离

Valentino et al. 的[官方任务论文](https://aclanthology.org/2026.semeval-1.450/)以三段论测 LLM 是否把语义合理性误当作逻辑有效性；四个子任务交叉英语/多语与标准/含无关前提，并在后两类要求识别相关前提。论文报告 accuracy 之外另测 content effect，且指出无关前提过滤与多语稳定性仍有挑战。官方全文核读记录见[结构化日志](../sources/literature_screening_log_2026-10-07_semeval2026_task11_overview.json)。

对本项目的直接启示是：NLI/解析阶段应把世界知识上的合理性与“指定 gloss 是否支持有向 literal”分开，测试可控制 plausible/implausible 表述和无关上下文，并报告干扰下的变化；无关前提选择指标只能作设计参照，不能替代 span-support gold。该任务并非词义绑定、释义到 Horn 编译或 proof-provenance 系统，也不是本项目的匹配基线；是否能改善本项目仍是假设。

ACL Anthology 固定候选框中 2021–2022 年 `wordnet_gloss_lexical_relations` 族的 33 条待筛记录已逐条题名/摘要筛查，详见[结构化日志](../sources/literature_screening_log_2026-10-06_acl_wordnet_direct_2021_2022.json)。该切片计 4 条直接近邻、10 条相邻、3 条背景及 16 条排除；它是单人初筛，不是全文综述。

- Chen et al., [Constructing Taxonomies from Pretrained Language Models](https://aclanthology.org/2021.naacl-main.373/) 将 parenthood prediction 与树协调结合，在 WordNet 子树上训练/测试，并报告 web-retrieved glosses 可提升 taxonomy construction。全文核对显示主设定检索 Wiktionary、Merriam-Webster 和 Wikipedia gloss，WordNet gloss 是 oracle setting；英语子树 F1 从无 gloss 的 63.5 提升到 web gloss 的 66.7，WordNet oracle gloss 为 83.2。它是 gloss-informed hypernym acquisition 的直接邻居，但没有 gloss claim span、规则级人工支持或 proof replay。
- Kober et al., [Data Augmentation for Hypernymy Detection](https://aclanthology.org/2021.eacl-main.89/) 用 hypernym 传递性、修饰语组合和 WordNet 资源增广检测数据。其增广对象是 hypernymy 分类训练样例，使用传递性与交集修饰语组合，另对向量做 GAN 增广，并用 WordNet 扩展数据集；评测覆盖三套数据集和两种向量空间。它关闭了“用词汇传递性/WordNet 辅助上下位预测”这一宽泛空白，但不是由 gloss 抽取逻辑规则。
- Lin & Ng, [Does BERT Know that the IS-A Relation Is Transitive?](https://aclanthology.org/2022.acl-short.11/) 以 WordNet senses 探测模型对 IS-A 传递性的遵循程度；摘要报告预测并不完全符合传递性。论文报告其 WordNet sense-pair probe 中 BERT IS-A accuracy 72.6%，在前两段边均被正确预测的传递三元组上，端点边预测率 82.4%。它是关系一致性基线先例，不提供来源定义支持判定。
- Yao et al., [Connect-the-Dots](https://aclanthology.org/2021.emnlp-main.610/) 将 WordNet 3.0 和五本学习者词典中的 gloss 对齐，报告 704K links；1,000 对抽样人工核验的整体准确率为 .87，阈值筛选后为 .98（双标 200 对，κ=.74）。其 downstream 是 contextual word–gloss semantic equivalence 的 WSD/WiC，不判定 gloss 内部单个命题的支持或方向规则。
- Maudslay & Teufel 的 [Homonymy Information for English WordNet](https://aclanthology.org/2022.gwll-1.13/) 用 Transformer embedding 将 WordNet 定义对齐到 OED 定义，并依据 OED 的 lemma/词源分组区分 homonymy。论文报告 lemma assignment F1=.97、sense assignment F1=.84；双标者原始一致率分别为 97.6% 和 80.4%。摘要写 196 words/554 senses，而详细评估段写 196 wordform–POS combinations/544 senses；该计数差异暂保留。两项工作都是定义/义项对齐，而非定义命题的逻辑支持。
- Almeman & Espinosa-Anke, [Putting WordNet’s Dictionary Examples in the Context of Definition Modelling](https://aclanthology.org/2022.cogalex-1.6/) 将 WordNet 例句与 Oxford-based CHA 资源比较，使用 GDEX 启发式衡量例句，并比较两种语料训练的定义生成模型。作者说明例句质量没有人工标注 gold；生成定义用 BLEU、METEOR 和 ROUGE-L 评估，并作定性错误分析。因此可借鉴资源适配性评测，不能把例句可读性或参考文本重合度当作 gloss-support gold。
- Kratochvil et al., [Abui Wordnet](https://aclanthology.org/2022.fieldmatters-1.7/) 从多语词典 gloss 交集生成 sense 候选并建成人工核查资源，是 gloss-driven sense acquisition 先例；论文人工核查全部 2,368 个三语交集候选，报告其准确率 0.989；双语和单语候选的抽样准确率分别为 0.50 和 0.35。摘要和正文均不涉及 formal entailment 或 Horn rule evaluation。

因此，不能主张 WordNet taxonomy+gloss、hypernym transitivity、定义/sense 对齐或 sense bootstrapping 本身尚未研究。可保留的更窄问题是假设：给定固定 synset/release 后，能否从 gloss 提取逐条有方向、有 source span 的 typed AND/OR Horn 规则，并用独立可回放证书评测来源约束的 entailment。该差异尚无 gold 或匹配实验支持，不能表述为已验证的新颖性或效果。

更新日期：2026-10-06。本文是基于正式论文集页面、部分全文与附录的初步对照，不是全文复现，也不是新颖性结论。除有特别注明外，“未知”表示尚未逐式检查全文、附录、代码或数据，不代表相关工作没有该能力。各轮检索/筛选记录 JSON 可复查新增候选与边界。

## 2026-10-06 ACL Anthology：2020 年定义到形式/图推理直接近邻

对固定 v2 `wordnet_gloss_lexical_relations` 查询族中 2020 年的 25 条待筛记录完成题名/摘要筛查：2 direct neighbor、12 adjacent、4 background、7 exclude；逐条记录见[筛查日志](../sources/literature_screening_log_2026-10-06_acl_wordnet_direct_2020.json)。COLLIE-V 与 BMEAUT 的官方 PDF 已定向核读。

- **COLLIE-V 是重大新颖性碰撞。** 它已从 WordNet gloss 生成义项相关语义结构、AND/OR entailment axioms，并以两名评审对 axiom 正确性/有效性做人审。报告中 20.9% 的错误 axiom 未被系统识别；这是当前方法比较和独立验证设计必须正面回应的证据。其依赖手工 TRIPS 本体、词汇及 WN mappings，并聚焦动词，但这些差异本身不构成项目新颖性。
- **BMEAUT 是图式词汇蕴含的直接基线。** 它将 Wiktionary definition parse 成 4lang graphs，采用 bounded graph expansion、0-edge reachability，并合并 WordNet hypernym 结果；图-only 侧高精确率、低召回，WordNet+graph 混合提高召回。它与本项目的 lemma/sense 粒度不同，但不能被省略出定义图推理对照。

- **Kovács et al. (Natural Language Engineering 2023) 是 BMEAUT 同一研究线的期刊扩展，不应重复计为独立方法家族。** 它改进 UD→4lang 图构造（IRTG 规则）、用有界图扩展上的 0-edge 有向路径判断词汇蕴含，并在 SemEval 2020 与 SherLIiC 上评测，加入 WordNet/同义词节点；作者也分析 sense selection 和图边误差。路径可解释性不保证路径语义有效，论文明确讨论过宽 0-edge 关系可能产生错误蕴含。它排除“首次可解释定义图词汇蕴含”主张；与项目的更窄差别仍是逐 literal gloss-span、typed AND/OR Horn、source-only entailment 与独立 proof replay 的联合 gold 评测，尚待验证。详见[官方全文定向筛读日志](../sources/literature_screening_log_2026-10-07_4lang_explainable_lexical_entailment.json)与[Cambridge Core](https://www.cambridge.org/core/journals/natural-language-engineering/article/explainable-lexical-entailment-with-semantic-graphs/96A9C7F5B30D7DD5A955B54D9AF8ADF4)。

因此，“首次从 WordNet gloss 导出有组合结构的 entailment axioms”“首次把定义建图用于 lexical entailment”等宽泛主张都不成立。更窄的来源跨度标注、release/sense 绑定、可独立重放证据是否与这些先例实质不同，仍须做表示逐项比对并在同一人工 gold 上实测；现阶段只列为研究假设。
### 复现/适配可行性门槛（2026-10-06）

| 系统 | 官方代码/资源状态 | 当前可承诺的复现级别 | 适配到同一 gold 的最小方案与门槛 |
|---|---|---|---|
| COLLIE-V | [项目页](https://tripslab.github.io/)链接 XML/JSON 资源和 `pytrips`；关联 [jsontrips](https://github.com/mrmechko/jsontrips) 与 [pytrips](https://github.com/mrmechko/pytrips) 仓库当前标示 GPL-2.0。作者项目页说明资源可下载，但我们尚未确认一个可固定版本、可在本项目 raw gloss 输入上重跑论文 gloss→axiom induction 的端到端脚本、输入 crosswalk 和原评测数据。 | **先做 resource/output 对照，不宣称复现 induction。** 若后续定位到论文对应代码与可用固定资源，再按其原设置独立复现并记录版本/配置。公开许可只适用于相应仓库材料；数据、ontology、TRIPS 依赖和第三方资源许可须逐项核对。 LREC 2020 官方作者指南说明论文集采用 CC BY-NC 4.0，与 COLLIE-V PDF 页脚一致；ACL Anthology 页脚是针对 ACL materials 的通用声明，单凭该页脚不能认定 ELRA 出版内容存在许可冲突。此范围说明不是法律意见，资源、ontology、软件和第三方依赖仍须分别核验。 | 对齐共同 synset 和 gloss 后，先比较可下载 COLLIE 条目/axiom 对 project blind sense-claim gold 的覆盖与方向关系；只有当公开材料包含逐 gloss 对应的生成候选且可确认来源时，才计为系统预测。报告 claim precision/recall/F1、方向混淆、AND/OR 结构覆盖及 source-span support；不得把 ontology mapping 缺失记成语义错误。 |
| BMEAUT | [论文链接的 `wikt2def` 仓库](https://github.com/adaamko/wikt2def) MIT；SemEval 分支当前固定提交 `bdc67c2a4fdc087ca386bea6d804b9315a23121f`。分支说明依赖 Python 3.7、Flask/NetworkX/StanfordNLP/NLTK/Graphviz/scikit-learn，另需下载预构建 definition/dictionary 与 SemEval 数据，并运行 UD 服务。 | **可尝试固定旧分支复现原 SemEval dev 配置；未运行，当前非复现结果。** 需要先确认外部下载资源仍可得及依赖在隔离环境可安装；原仓库的预计算成绩不得直接作为本项目分数。 | 在相同 blind gold senses 上把锁定 gloss 直接输入其 4lang graph builder；用统一候选方向对运行 graph-only、WordNet-only、graph+WordNet 三种设置，候选/标签和预算与本系统完全一致。分别报告有义项路由的覆盖率、方向关系 P/R/F1、source-span 支持、polysemy 切片、AND/OR 信息丢失和 abstention；WordNet 辅助结果单独成列。原 SemEval binary lexical entailment 分数仅作上游复现核验，不与项目 gold 横比。 |

当前候选框 400 条中有 376 条 effective definition 与锁定义项精确匹配；这只限定未来输入对齐的候选上限，不是 gold 或基线覆盖率。开始 matched comparison 前，还需要先签署标注协议、明确对外使用许可并取得双人裁决 gold；不得将未审候选任务包或答案信息送入外部系统。以上代码/资源调查是静态可行性审查，未运行两项系统、未下载数据，也未执行依赖安装。

## 为什么要做这个对照

项目容易把几个不同对象混成一个：WordNet 定义依赖图、正 Horn/Datalog 闭包、义项级语义关系、自然语言蕴含，以及带可重放证书的证明。它们不能互相替代。特别是从当前 bundle 标记的 basis head 可达某概念，只能说明当前编码下的结构依赖；它本身不证明这些 head 是语言学/认知意义上的 semantic primes、全局最小集，也不证明任意命题之间的语义蕴含。

| 工作 | 输入→输出 | 义项与逻辑结构 | 证明/来源 | 评测与本项目要学的事 |
|---|---|---|---|---|
| [WordNetGraph (Silva et al., LREC 2018)](https://aclanthology.org/L18-1542/) | WordNet 3.0 名词/动词定义→语义角色 span 标注→RDF 定义图→基于分布式语义的图路径与可读 entailment justification；2,000 个 synset 人工标注，最佳序列标注准确率 80.35%，再扩展到 82,112 个名词及 13,761 个动词 synset | **直接先例**：已覆盖“WordNet 定义→语义图→可解释文本蕴含”。其角色图与路径评分不是带显式变量绑定、量词作用域和独立 replay 的 typed Horn 证明；论文未给逐 gloss span→Horn literal gold | 80.35% 是角色序列标注准确率，不是图正确率或 entailment 指标；论文将详细应用结果留给另文 | 必须撤回“首次从 WordNet 定义建图/用于可解释蕴含”类主张。可检验的窄差异是 sense/release-bound gloss span 支持、方向化 AND/OR Horn 结构与 source-only witness replay；需在 matched gold 上验证。全文筛查见[Phase253 日志](../sources/literature_screening_log_2026-10-08_phase253_fulltext_addendum.json)。 |
| [Domain Adaptation for Large-Vocabulary Object Detectors (Jiang et al., NeurIPS 2024)](https://proceedings.neurips.cc/paper_files/paper/2024/hash/89d0d5c2f720921df93bbb8fef514571-Abstract-Conference.html) | WordNet synset definition + hyponym descriptions→CLIP text nodes→weighted undirected language knowledge graph→large-vocabulary object detector adaptation | NeurIPS main-conference precedent for building an explicit downstream graph from WordNet gloss/hierarchy; graph edges are embedding distances, not typed lexical rules | Main paper Table 5: Cityscapes AP50 is 52.0 for definition-only LKG and 52.8 for definition+hyponym hierarchy, against 46.5 source-only. These are detection metrics, not lexical relation/proof evaluation. Targeted method/ablation review only | Further closes broad “WordNet definition/hierarchy to a graph for downstream inference/classification” novelty claims. It is an adjacent vision task, not a matched baseline for gloss-supported entailment or rule/proof generation. See [screening log](../sources/literature_screening_log_2026-10-06_definition_entailment_supplement.json). |
| [ILF-WN (Agerri & Peñas, CICLing 2010)](https://doi.org/10.1007/978-3-642-12116-6_3) | WordNet 3.0 gloss→POS tag/dependency parse→Intermediate Logic Forms；逐 synset 提供结构化 XML；`conj_or` 保留协调标签，但不自动等于显式析取 Horn clause | 全 POS gloss 形式结构先例；采用平坦 entity/relation 中间表示，而非标准 FOL；该版本不对所有词运行 WSD，也无定量 gold fidelity | 论文与 eXtended WordNet、WN30-lfs 作定性比较；没有本项目目标的逐 literal span 支持标签或独立 source-bound proof certificate | **直接 novelty collision**：禁止声称首次从 WordNet gloss 自动产生形式表示。需对齐比较 scope、WSD、source alignment、语义 gold 和证书。 |
| [Definition parsing to ontology acquisition (Bond et al., COLING 2004)](https://aclanthology.org/C04-1193/) | 日语 Lexeed 机器词典定义→HPSG parse→MRS→hypernym 等词汇本体链接；特殊处理 coordinate constructions | 深层语义表示含 predicates、arguments 与 scope constraints；论文说约 20% 定义需额外处理，但该研究最终抽取的是词汇关系，不是完整 Horn 子句编译 | 全文筛读：略多于 80% 定义句可解析；与 Goi-Taikei 类层级比对，15,888/27,146（58.5%）关系确认，包含名称/缩写时报告 60.7% coverage。属本体相对核验，不是逐条 gloss-span 支持标注 | **早期直接结构化先例**：排除“从定义做 compositional semantic parsing 并建词汇本体”的宽泛新颖性说法。论文把 sense-tagging/义项链接列为后续工作；没有报告本项目设想的 typed AND/OR Horn 编译或 proof replay。该边界仅按全文明确描述，不推断其系统的全部能力。 |
| [Wordnet Bahasa definition relation extraction (Moeljadi & Bond, GWC 2016)](https://aclanthology.org/2016.gwc-1.33/) | 清理后的印尼语定义→definition-head regex→与 WordNet synset links 对照，提取 synonym/hyponym/hypernym/instance-hypernym | 直接的 WordNet 定义→词汇关系先例；不是完整 FOL/Horn 编译 | 全文筛读：10,958 条名词/动词定义中 6,257 条（57.10%）提取到四类关系，其中 95.89% 为 hypernym/instance-hypernym；数字是抽取覆盖与关系构成，不是语义 precision | 其首词/定义 head 启发式会漏掉非首词上位项。它限制“首次从 WordNet 定义恢复层级关系”的主张，但未标逐条 source span、完整 AND/OR、或生成证明证书。 |
| [Dictionary-to-inference rules (Almiman & Ramsay, RANLP 2017)](https://acl-bg.org/proceedings/2017/RANLP%202017/pdf/RANLP009.pdf) | Macmillan/WordNet 词条定义→POS-tagged pattern + regex 改写→有方向的自然语言推理模板，如 `X is a human if X is a person`；泛指动词宾语可改变量 | **最接近的直接 prior art**：已经组合“WordNet/词典定义→方向性 inference rules”和规则人工正确性判断；不是顶会结果，按直接相关先例而非顶会 SOTA 记录 | 全文筛读：WordNet 侧改写 3,630 条定义；两来源共约 8,000 条规则，对 200 条抽样规则（各来源 100 条）做人类 meaning/grammar 判断，WordNet 样本 precision 报告 73%。WordNet recall 在摘要 0.09、正文 0.126，存在内部不一致，未择值引用 | 排除“定义转方向规则”“从 WordNet 释义抽推理知识”及“对生成规则做人审”作为单独新颖点。仍需检验的假设只能聚焦 sense/release identity、claim-level gloss span 支持、保真的 typed AND/OR Horn 结构和可独立重放的 proof/unknown；目前无项目 gold 或 matched evidence 证明该组合的有效性或新颖性。 |
| [Princeton WordNet Gloss Corpus semantic parsing (Rademaker et al., GWC 2023)](https://aclanthology.org/2023.gwc-1.30/) | GlossTag 的上下文词义标注→ERG parse / ERG predicates，推进 WordNet gloss 深语义标注及 3.1 映射 | sense tagging + deep semantic parsing 近邻，依赖人工标注/修订的语料工作 | 讨论 GlossTag/WordNet 3.0/3.1 对齐及不一致；不是大规模自动规则生成或可重放推理证书 | 适合作为 sense-WSD、source-span 和版本稳定性基线/标注资源；提示定义与 synset 版本不可混用。 |
| [COLLIE-V (Allen et al., LREC 2020)](https://aclanthology.org/2020.lrec-1.396/) | WordNet gloss→TRIPS parse→verb ontology/semantic roles/entailment axioms; nested AND/OR occur in rule structures, with WN Gloss Corpus, hand-built ontology/lexicon and WN–TRIPS mappings guiding induction | Strongest WordNet-gloss-to-compositional-axiom prior art in the reviewed slice; two judges: 45.1% fully correct + 17.3% valid entailment, 16.7% detected/rejected, 20.9% accepted but erroneous; role F1 .85, template recall .96 | This is a **major novelty collision** for the broad pipeline. Differences must be experimentally established on shared senses and gold; candidate dimensions are source-span audit, source-version binding and independently replayed certificates. Those are hypotheses, not established novelty. Full details in [2020 PDF log](../sources/literature_screening_log_2026-10-06_acl_wordnet_direct_2020.json). |
| [BMEAUT at SemEval-2020 Task 2 (Kovács et al.)](https://aclanthology.org/2020.semeval-1.15/) | Wiktionary definitions→UD/4lang semantic graphs→bounded graph expansion and directed 0-path entailment; combines with WordNet hypernym lookup | Direct definition-graph-to-lexical-entailment baseline; graph-only has high precision/low recall, hybrid improves recall using WordNet. | Major prior-art collision for broad gloss-derived graph reasoning. Matched comparison should test polysemy, sense identity, direction, support spans, AND/OR semantics, and proof object replay; paper task is monolingual binary LE and does not report source-span labels or certificates. See [2020 PDF log](../sources/literature_screening_log_2026-10-06_acl_wordnet_direct_2020.json). |
| [TaxoLLaMA (Moskvoretskii et al., ACL 2024)](https://aclanthology.org/2024.acl-long.127/) | WordNet 3.0 hypernym 关系线性化→LoRA/4-bit LLaMA-2-7B→Hypernym Discovery、Taxonomy Enrichment/Construction、Lexical Entailment | 直接证明 WordNet taxonomy→LLM 词汇关系预测已有 ACL 主会先例；训练/输出是既有链接诱导的 relation predictor | 论文称 16 个任务设置 11 项第一、4 项第二；部分任务缺定义时补入 Wikidata/ChatGPT 定义。没有 arbitrary gloss→AND/OR Horn 编译、span support gold 或可重放证明 | 必须纳入 lexical-hypernym baseline/novelty audit；不得将其任务分数与 source-support/proof fidelity 直接比较。 |
| [LORex (Mishra et al., ACL Findings 2025)](https://aclanthology.org/2025.findings-acl.671/) | WordNet/其他 taxonomy 中的新概念及 description/definition + hierarchy paths + candidate parents → rank/chunk/filter → LLM parent selection and verification | **直接 lexical taxonomy 近邻。** 利用定义与层级路径选择既有 taxonomy 的 parent，但不把 gloss 编译成多前提 Horn clause，不标 span→literal support | 定向核读 19 页官方全文：四个 benchmark（含 WordNet），作者报告相对最佳既有生成基线 accuracy +12%、Wu–Palmer +5%；TEMPORA ranker Hit@k +21.3%。都只是论文任务结果；LLM verifier 不是可独立重放的 source proof | **优先 matched baseline。** 排除“定义辅助的 taxonomy parent/hypernym expansion”作为单独创新点。需要在同 WordNet release、same senses/candidate pool、same split/budget 上适配比较；还须单独测 gloss-span support、AND/OR 规则完整性与 certificate replay。详见Phase 58。 |
| [Multiple Hypernymy Resolution (Hristov, RANLP 2025 Student Research Workshop)](https://aclanthology.org/2025.ranlp-stud.3/) | PWN 3.0 中一个 hyponym 有多个既有 hypernym→四个本地 LLM 在候选 synset 中择一；0/1/5-shot 共 12 个模型设置 | 直接相关于词汇层级清理/关系选择，但它不从任意 gloss 抽取关系，也不构建方向性定义规则 | 全文筛读：1,339 个评测义项；与先前手工整理结果 exact agreement 45.4–55.0%，模型间 agreement 明显更高；论文未报告人工标注者一致率，且提出未来需要进一步人审。公开 GitHub repository 无可见 license 文件，未取用数据 | 提示应将“模型之间的自洽/共识”和“相对独立人工 semantic gold 的正确率”分开报；仅有候选间选择正确率不能证明 gloss→rule support、AND/OR 保真或 proof replay。Student Research Workshop 结果与主会 SOTA 分层陈述。 |
| [AI-WordNet (Sun & Wang, GWC 2025)](https://aclanthology.org/2025.gwc-1.5/) | lemma+gloss→lexname、新/既有 PWN 3.0 名词 synset 决策→hypernym 候选及 WordNet taxonomy 更新 | 是显式“释义自举 WordNet 关系”的直接先例；不同于开放域通用 FOL 或逐 gloss 逻辑编译 | 正文完整方法/结果已筛读。表格报告 lexname F1 .946、hypernym exact hit .648、平均 taxonomy 距离 1.374（正文另有 64.5% 表述）。8,000 条 Wiktionary 条目用于下游 cloze，300 个 cloze 由三位教师评 distractor 效用；并非 8,000 条 hypernym 的人工正确率；示例容许错误方向的候选只要有干扰效用 | **直接先例**：不可声称“仅凭 gloss 自动扩展 WordNet / 预测 hypernym”新颖。matched baseline 要统一资源、sense split 和 relation 指标；任务效用分数不可代替 source-gloss entailment、sense 正确性或 Horn proof。 |
| [Greco et al., Findings of EMNLP 2024](https://aclanthology.org/2024.findings-emnlp.881/) | WordNet verb synset gloss + lemma pairs→LLM 判断方向性 lexical entailment；另测 HyperLex，零样本/少样本及 Direct/Indirect/Reverse 提示 | 与项目的 gloss-conditioned relation decision 最近；没有将 gloss 解析成显式规则或组合证明 | 八个 LLM；WordNet 零样本 Direct 最佳 accuracy/F1 各 0.62，其他提示最佳值及模型不同。没有同设置有/无 gloss 的控制，且评价标签是 WordNet/HyperLex 资源关系而非 gloss-span support gold | 必须纳入相同 sense/pair/gold 的直接 LLM baseline 候选。结果不能作为 source-support 或 proof-validity 分数；更窄差异仍待独立人审和 matched evaluation。详情见[补查日志](../sources/literature_screening_log_2026-10-06_definition_entailment_supplement.json)。 |
| [LM-Lexicon (Liu et al., EACL 2026)](https://aclanthology.org/2026.eacl-long.1/) | 给定 term（及上下文）生成定义；以 WordNet、Oxford、Wikipedia、Urban、3D-EX 五个基准训练/评估语义专家 MoE | EACL 主会定义建模先例，包含 WordNet split；目标是 definition generation，不是从既有 gloss 抽取规则 | 22 页官方全文定向核读：WordNet 13,883/1,752/1,775 train/valid/test；3 个随机种子。300 个 3D-EX 人评样例由三位语言学/词典学研究生按五项质量标准评分，参考定义可见。作者报告平均约 +7% BLEU，并明示仅测英语、训练成本和 verifier 不足 | 限制“WordNet definition modeling 尚未被研究”的说法；不是 gloss→typed Horn、span support 或 proof certificate 的匹配基线。生成质量分数不能代替 sense-linked source-support、关系正确性或证明重放。详见[全文筛读日志](../sources/literature_screening_log_2026-10-06_definition_modeling.json)。 |
| [Adaptive LLM-Symbolic Reasoning (Xu et al., EACL 2026)](https://aclanthology.org/2026.eacl-long.54/) | 对自然语言问题做分解、逻辑范式路由、自动形式化，再调用 LP/FOL/CSP/SMT 求解器 | 近邻覆盖 LLM-to-symbolic 路由与求解；论文在 PrOntoQA、ProofWriter、FOLIO、LogDed7、TRECtrials 等上测端到端答案与路由 | 22 页官方全文定向核读方法、实验/错误分析、讨论与限制；作者指出自动形式化是瓶颈，并报告语法有效但语义错误的形式化 | 不应声称首次结合 LLM 与形式求解器、首次自适应符号推理或首次自动形式化；论文未评测 WordNet gloss、词义链接、gloss span 支持或可重放 provenance。详见[筛读日志](../sources/literature_screening_log_2026-10-06_logic_reasoning.json)。 |
| [OntGQA (Shan et al., ACL 2026)](https://aclanthology.org/2026.acl-long.489/) | 在 Freebase relation-centric ontology graph 上约束头尾实体类型，以 planner-judge 和生成回退回答多跳 KGQA | 类型约束图推理近邻；在 WebQSP/CWQ 评估答案准确率，和词义定义形式化的任务不同 | 14 页官方全文定向核读本体构建、架构/评估与限制；作者将当前实例限制于 Freebase，并指出动态 schema/其他 KG 的迁移仍待评估 | 不应声称首次用类型约束或本体支撑推理链；不是 gloss-derived Horn 规则或可重放证明证书基线。详见[筛读日志](../sources/literature_screening_log_2026-10-06_logic_reasoning.json)。 |
| [LoReFact (Xie et al., Findings of ACL 2026)](https://aclanthology.org/2026.findings-acl.346/) | 长文本事实核查中联合评估内容事实性与逻辑依赖 | 逻辑依赖评估近邻；提出 LOREFACT 数据集、LoRe-Factcheck 与 LoReFactScore | 23 页官方全文定向核读摘要、框架与限制；作者指出受控 LLM 数据可能有分布偏移，且框架不保证多步链全局一致性 | 不应声称首次联合考察内容事实性与逻辑依赖；不属于词义 gloss→逻辑程序、规则蕴含或 provenance 基线。详见[筛读日志](../sources/literature_screening_log_2026-10-06_logic_reasoning.json)。 |
| [FOVER (Kamoi et al., Findings of ACL 2026)](https://aclanthology.org/2026.findings-acl.403/) | Z3/Isabelle 对已形式化逻辑/数学推理轨迹逐步赋予正确/错误标签，再训练分类式 PRM | 对“solver 验规则/推理步骤”及 verifier 监督的最新直接邻居；论文还测 PRM 在 NLI/BBH 等自然语言推理上的迁移 | 20 页官方全文定向核读形式检查、FOVER-40K 构造、实验与限制；作者提醒形式标签训练会使 PRM 过严，例如把可接受的中间近似判错 | 不应声称首次用形式验证器检查推理步骤或构造自动错误标签。其 solver 从形式化 premises 开始，不验证这些 premises 是否忠实来自 gloss；PRM 分数也不是可重放 proof certificate。详见[筛读日志](../sources/literature_screening_log_2026-10-06_formal_verification_prm.json)。 |
| [Pause or Fabricate? (Qiu et al., Findings of ACL 2026)](https://aclanthology.org/2026.findings-acl.1155/) | 对数学习题遮蔽候选数值句构造缺前提输入；GRIL 训练模型判断应先澄清/暂停还是直接求解 | 推理边界感知、信息充分性与拒答/追问的邻接先例；不是 gloss-to-logic 或词汇蕴含系统 | 官方 22 页全文与附录定向核读：论文部分用 LLM solvability 判断给遮蔽句标 essential/redundant；Qwen2.5-1.5B 在 GSM8K-Insufficient 的报告 premise detection 为 4.6%→90.8%、success 为 1.8%→61.6%。这些是作者数学任务结果；论文指出结构化输出依赖、clarification quality/user burden 未直接测量 | 不应声称首次做一般缺前提检测、暂停或主动澄清。项目可借鉴“信息不足”作为单列状态，但 gloss 未支持不等于 NLI contradiction，且还需区分 source-support unknown、逻辑反模型与数据缺失。不是当前 ACL v3 1,747 项候选之一；经框外官方定向发现，不改变候选计数或召回率判断。详见[筛读日志](../sources/literature_screening_log_2026-10-06_gril_findings_acl2026.json)。 |
| [Logical Structure as Knowledge / SLKD (Bi et al., Findings of ACL 2026)](https://aclanthology.org/2026.findings-acl.436/) | LLM 分解上下文为常量、谓词、FOL 表达式；按前提集合、推导步骤、AND/OR/NOT 数及嵌套深度评分，作逻辑推理训练数据选择/重加权 | “逻辑结构密度”“推导拓扑复杂度”指标及其用于训练数据配置的近邻；没有 WordNet sense/gloss 规则抽取任务 | 官方 22 页全文定向核读方法/公式、4 个逻辑基准、SFT/RL 结果、局限和 artifact terms。基准含 36,788 训练与 4,743 测试项；作者称 SLKD 为 reasoning-potential proxy，LLM 逻辑分解可能引噪且领域迁移未证。论文数字不可移植 | 冻结超图的深度/OR/AND画像可作为结构属性，但不能独立代表 gloss 语义密度、正确性或难度；不得仅凭“图复杂度/逻辑密度”主张创新。项目可能的差异仍需通过 source-span support gold 与 matched baseline 实测。该文为 ACL v3 候选框外发现，不改变候选计数或召回结论。详见[筛读日志](../sources/literature_screening_log_2026-10-06_slkd_findings_acl2026.json)。 |
| [Ukrainian WordNet hypernym extraction (Romanyshyn et al., UNLP @ LREC-COLING 2024)](https://aclanthology.org/2024.unlp-1.7/) | PWN/Wikidata/Wikipedia links + machine translation/Hypernym Discovery/instruction-following LLaMA→乌克兰 WordNet 名词层级扩展 | 跨语言词汇资源构建与 hypernym discovery 的直接邻居；官方论文页报告 PWN 映射覆盖 17%、instruction-following LLaMA 的 MOC 41.61% | 全文已查看；这是带专家输入的 workshop 资源建设，不是逐条任意 gloss 的 Horn 支持或证明证书 | 作为跨语词汇关系扩展基线背景，需与 GWC 的直接释义抽边方法区分；MOC 不可解释为 gold gloss entailment。 |
| [SememeLP (Wang et al., EMNLP 2025)](https://aclanthology.org/2025.emnlp-main.740/) | 定义→预定义 sememe inventory 中的 all/main sememe 表征→lexico-semantic KG link prediction；构造 SememeDef（70,645 English、43,163 Chinese definition–sememe examples） | 直接涉及定义诱导固定语义组件并用其完成 WordNet/词汇 KG；评测 missing-triple ranking，不生成声明式规则 | 报告 WN18RR MRR 75.1%；提供代码/数据；其 embedding/LP 分数不是语义证明或源文本忠实度指标 | 禁止把“定义→语义原语/组件→词汇 KG 补全”单独当 novelty。项目需把 basis 与 sememe inventory 区分，并测 source-span support、逻辑方向和 proof replay。 |
| [Enhancing Lexical Relation Mining with Structured Sememe Knowledge (Wang et al., ACL 2026)](https://aclanthology.org/2026.acl-long.224/) | 词义定义→All/Main Sememe Prediction→Structured Sememe Prediction→Sememe Relation Classification，产生 sememe tree；论文称进一步为 WordNet 自动建树，并在词汇关系分类及 HyperLex graded lexical entailment 上评测 | **直接 novelty collision**：覆盖从定义构造结构化义项语义，再用于 hypernym/lexical-entailment 判断；结构树与本项目 Horn 超边仍非同一表示 | 自动 pipeline 在 BabelSememe 上报告 ASP F1 60.3、MSP F1 68.9、SRC F1 98.2；SSP Strict 52.3 来自提供 gold sememe set 的 restricted setting，不是完整 ASP→MSP→SSP 预测链的端到端树准确率。论文在下游 benchmark 实例上报告 main-node / sememe-node / parent–relation–child coverage 平均为 70.7% / 73.9% / 65.9%；自动 STC 下游模型较无 sememe baseline 平均提升 1.3%（论文报告）。这些数字不构成对全部 WordNet senses 的树级人工正确率。论文未提供本项目目标的规则证据/证明证书；公开仓库有代码/benchmark 资源，但本轮未确认完整 WordNet 树文件已发布。 | 宽泛的“从 WordNet 定义自动结构化语义并预测上下位”不再是空白。可检验差异必须收窄为有类型/方向的 Horn 规则、逐条 gloss-span 支持、对 AND/OR 与变量/作用域的形式保证，以及独立证明/unknown 证书；这些还须在 matched benchmark 上实测。 |
| [Native Hierarchical and Compositional Representations with Subspace Embeddings (Moreira et al., KDD 2026)](https://arxiv.org/abs/2508.16687) | WordNet synset hypernym hierarchy→learned subspace/projector embeddings; HyperLex graded lexical entailment; SNLI; LLM-elicited zero-shot premise→AND/negated-AND hypotheses | **直接表示层面近邻**：subspace inclusion 建模 entailment，交/线性和/正交补表示 AND/OR/NOT；SE-128 的 WordNet 稀疏链路预测与合成组合蕴含指标表现强。其软投影逻辑被作者界定为近似逻辑 | KDD 2026 proceedings v2 全文/附录定向筛读：WordNet reconstruction/LP 用既有 taxonomy edge/closure，不解析 gloss；HyperLex 用人类 graded lexical entailment；compositional benchmark 为 Gemini 3.1 Pro elicitation、约 200 候选人工过滤后组成 600 pairs，且先排除 atomic baseline errors。未复现代码 | 已排除“WordNet 逻辑层级/AND-OR-NOT 几何组合、hypernym recovery、NLI/neural composition 尚无顶会先例”等宽泛说法。仍可检验的差别仅为 sense/version-bound gloss→typed directional Horn rules、逐 claim gloss-span 支持与 source-only proof replay；这是待验证假设。其指标不能替代本项目 source-support gold/proof validity。详情见[筛读日志](../sources/literature_screening_log_2026-10-05_iclr_lattice_and_kdd_subspaces.json)、[KDD 论文](https://doi.org/10.1145/3770855.3817808)与[代码](https://github.com/gabmoreira/subembed)。 |
| [The Lattice Representation Hypothesis of LLMs (Xiong, ICLR 2026)](https://proceedings.iclr.cc/paper_files/paper/2026/hash/208853db0e806d03f6be769a3fae1ecd-Abstract-Conference.html) | LLM 属性方向/半空间 + Formal Concept Analysis → WordNet 五个子层级上的概念 lattice、subsumption、meet/join | **重要逻辑组合邻居**：在 WordNet 层级上验证神经表示中可恢复 meet/join 与部分序；否定“WordNet hierarchy 上逻辑合取/析取式组合尚无人研究”的宽泛说法 | 属性 schema/对象标签由 GPT-4o 构造，WordNet is-a 边给层级目标；未从原始 gloss 抽取 typed Horn clauses、未做人审 span support，也未验证可重放逻辑证书 | 论文报告属性恢复 F1 约 70–83%，偏序 F1 最高 77.1；这些是其构造任务的结果，不是本项目可比 gold。项目仅能检验是否提供另一种显式、来源锚定且可 replay 的声明式保障；该差异尚未证明新颖或有效。定向全文边界见[日志](../sources/literature_screening_log_2026-10-05_iclr_lattice_and_kdd_subspaces.json)。 |
| [Hierarchical Concept-based Interpretable Models / HiCEM (Hill et al., ICLR 2026)](https://proceedings.iclr.cc/paper_files/paper/2026/hash/1395b425d06a50e42fafe91cf04f3a98-Abstract-Conference.html) | 从 concept embeddings 以 sparse autoencoders 发现 sub-concepts，训练两层 HiCEM；ImageNet 高层概念标签由 WordNet synset hypernym ancestors 生成，支持不同粒度的 concept intervention | **WordNet 层次概念建模邻居**：压缩“WordNet taxonomy → hierarchical concept representation/intervention 尚无顶会先例”的宽泛主张；输入是视觉类标签/概念 embedding，不是词典 gloss | 全文未发现 sense-linked gloss parsing、lexical relation extraction、source-span claim support、typed AND/OR Horn compiler 或可重放 proof/witness certificate。作者指出 SAE 概念未必有意义且只研究 sub-concept hierarchy | 六个数据集、用户研究及 PseudoKitchens；ImageNet 标签由 WordNet ancestors 构造。其结果不是 lexical entailment 或 gloss-support gold，不能作 matched baseline。局限包括 SAE 语义保证不足、只处理子概念关系、ImageNet validation-as-test。见[Phase239全文筛读日志](../sources/literature_screening_log_2026-10-08_iclr2026_hierarchical_concepts_wordnet_phase239.json)。 |
| [GraphRefine (Kim et al., ACL 2026)](https://aclanthology.org/2026.acl-long.1353/) | 通用文本 KG 的 post-hoc triple refinement：KEEP/DELETE/FIX/REWRITE；区分 source-level unsupported/misidentification 与 ambiguity/verbosity，并以多数据集及人工抽样做评估 | 与项目的源忠实度、结构错误分类、避免单纯删除造成覆盖损失相邻；其多操作改写提示输出修订与覆盖/保留也应分别评测 | 不是 WordNet gloss、sense-level 义项、Horn 规则或逻辑证明任务；人审是 triple consistency/error typing 而非 necessary/sufficient 方向支持。论文 factualness 包含 LLM judge，不能当独立 gold | 可借鉴错误类型/coverage 联合报告；本项目仍需 gloss-span + 方向标签的人审 gold、NLI 与 proof replay 分开评价。只作跨域评测设计参照，不作 matched baseline 或效果预期。 |
| [SenseRel: A Sense-Level Benchmark for Denotational and Connotational Meaning Relations (Cassotti et al., ACL 2026)](https://aclanthology.org/2026.acl-long.20/) | 构建词义级关系基准，覆盖 generalization、metaphor 等指称关系，以及 valence/arousal 两个内涵维度；比较 LLM 与微调 RoBERTa | 提供 sense-level relation evaluation 的邻接基准，但并非从 gloss 生成关系或逻辑规则 | ACL 2026 长文；官方摘要报告 GPT-4o 更贴近人类情感判断，微调 RoBERTa 擅长指称关系分类；细分数据、许可和与 OEWN 的映射仍待全文/数据核验 | 可借鉴把“词义关系”从 lemma 层拆开评估；其关系集合与 WordNet hypernymy、source-span 支持和 proof replay 不同，不能直接充当本项目 gold。 |
| [Gulbe et al. (GWC 2025)](https://aclanthology.org/2025.gwc-1.25/) | Tezaurs.lv 拉脱维亚语词典 gloss→候选 WordNet sense-level synonym/hypernym links；主句主格名词启发式生成 hypernym 候选，再用 Latvian BERT 排序/分类 | **直接 novelty collision**：已从词典释义生成义项级词汇关系，并由 3 位语言学家评估 400 对 sense pairs（synonym 平均认可 72%，hypernym 67.08%；κ 分别为 .76/.59）。但目标是词汇关系链接，不是通用逻辑编译 | 候选义项错配、并列结构与语义粒度会造成错误；400 对人工评估不是完整 span-support gold；没有 Horn rule 或 proof replay | 必须删除“首次从 gloss 建立 WordNet 义项关系/人工评价”宽泛主张。可检验的更窄差异为每个 typed literal 的方向性 span 支持、AND/OR 组合与独立 witness replay；这些仍待实测。全文筛查见[Phase253 日志](../sources/literature_screening_log_2026-10-08_phase253_fulltext_addendum.json)。 |
| [WordNet relation–human intuition alignment (Cao et al., GWC 2025)](https://aclanthology.org/2025.gwc-1.4/) | WordNet 语义关系→模板引导人类判断 | 比较 synset relation 与一般语言使用者直觉；显示 taxonomy path 结构和人类 hypernym 判断不能简单视为同一量 | 人类响应实验；非规则证明 | 对项目评测的直接警示：既要记录 resource-relative label，也要另做 context/human semantic judgement；不能让 WordNet 边充当唯一“ground truth”。 |
| [Wordnet and Word Ladders (Puccetti et al., GWC 2025)](https://aclanthology.org/2025.gwc-1.7/) | Llama 3.1 405B 对 13,518 个名词、45 种 prompt 生成 608,310 条具体/抽象词梯；以 WordNet 3.0 synset depth 与 Spearman 相关度评估排序 | 研究抽象层级和属性 prompt，不解析 gloss、不做 sense-bound source support，也不输出形式证明 | 论文未提供人工词梯基线；层级排序分数不可当作 gloss-rule accuracy 或 proof-validity 指标 | 作为词汇层次/抽象度评估邻居保留，不能替代 gloss-level logicization/evidence benchmark。此前误链 `.18` 实为另一篇 self-motion verbs 论文；已改为正确记录 `.7`。全文筛查见[Phase253 日志](../sources/literature_screening_log_2026-10-08_phase253_fulltext_addendum.json)。 |
| [Augello et al. (LREC 2026)](https://aclanthology.org/2026.lrec-1.293/) | OEWN 形容词定义→三种 LLM 四折候选生成→consensus/majority/singleton 分层；构建 3,836 对层级关系 | 是外部 OEWN adjective hypernym / lexical entailment 邻近 benchmark，可作限制到形容词子集的关系核验切片 | 官方 PDF 定向章节核读：87% 是 consensus 集按重复生成准则保留的比例，不是逐条双盲人审准确率；majority 随机 100 对双专家 κ=.89，据此设 Count≥5、Avg_Rank≤4 阈值，样本 P=.84/R=.72；singleton 反向生成后少量人工核验 κ=.73；仅含 1,148 个高频、经 sense disambiguation 的形容词。细节见[筛读日志](../sources/literature_screening_log_2026-10-06_augello_lrec2026_targeted_fulltext.json)。 | 不可声称首次做 OEWN hypernym 或人审关系资源。可作为外部词汇关系对照，但它不是 arbitrary gloss-rule source-support gold，不覆盖所有 POS/释义结构/证明证书。 |
| [Taxonomical Semantic Parsing (Zhang et al., CL 2025)](https://aclanthology.org/2025.cl-1.7/) | 句子→PMB semantic graphs，概念谓词使用 WordNet taxonomy 编码；另建 500 句 OOD challenge set | taxonomy-structured concept representation 用于 neural semantic parsing，不处理 definition-to-rule compilation | 以 Hard/Soft Smatch、taxonomy similarity 与人工修订 challenge set 评估；论文报告 OOV 概念更能预测语义相近概念 | 最近的神经符号/词汇 taxonomy 邻近工作，可启发 OOD 和层级感知指标；不提供蕴含证明或 gloss 证据忠实度评测。 |
| [Using Synchronic Definitions and Semantic Relations to Classify Semantic Change Types (Cassotti et al., ACL 2024)](https://aclanthology.org/2024.acl-long.249/) | WordNet 直接 taxonomy/antonym links→synset gloss pair + hyperonymy/hyponymy/co-hyponymy/antonymy/unrelated labels→RoBERTa-large pair classifier | 最近 ACL 主会的 sense-gloss + WordNet relation 联合模型；关系标签由资源边派生，不生成形式逻辑规则 | 全文筛读；WordNet in-domain hyperonymy/hyponymy normalized recall .91/.90；作者也迁移到外部 semantic-change任务 | 可作为“给定 sense pairs、用 definitions 分类词义关系”的近期邻接比较，并提示专测方向混淆；其资源派生标签不是独立人审 gloss-support gold，也不是来源证书/ Horn baseline。 |
| [Autoformalization in the Wild (Zhang et al., EMNLP 2025)](https://aclanthology.org/2025.emnlp-main.90/) | Wikipedia/arXiv 数学定义→Isabelle/HOL 形式化；含 56/30 条定义资源并测试 proof-assistant feedback 与 library grounding | Definition-to-formalization 直接近邻，但对象是数学 definitions / HOL，不是 lexical senses 或词汇分类关系 | Isabelle 检查生成形式化并将错误类型化；论文发现真实定义难，简单 binary feedback 改善有限 | 借鉴定义级 gold/resource、错误分型和结构化 feedback；区别须基于任务对象而非泛称“定义→逻辑未做过”。 |
| [Towards a Common Framework for Autoformalization (Mensfelt et al., AAAI 2026)](https://ojs.aaai.org/index.php/AAAI/article/view/42132) | 跨数学定理证明、逻辑/声明式编程、规划、知识表示的 autoformalization 概念框架与综述 | AAAI Proceedings Emerging Trends track；是框架/综述，不是 WordNet 方法或主会技术-track 实证基线 | 明确区分输入—形式输出的语义等价标准 E 与计算验证标准 V；作者称审阅 81 篇且不声称穷尽 | 项目应声明方向敏感、source-to-rule 的 `E_s`，再分层定义 span/ID、schema/compiler、proof replay 和人工 faithfulness 等 `V_s`，避免 checker pass 被误写成语义等价。 |
| [ProofBridge (Jana et al., ICLR 2026)](https://proceedings.iclr.cc/paper_files/paper/2026/hash/16f5b8d916f13534d11c50adf60914e4-Abstract-Conference.html) | 自然语言数学定理+证明→Lean 4 定理+证明；联合 NL/Lean 表示检索 proof DAG 示例，SFT 后迭代修复 | 与“生成形式表示并验证”是重要跨域邻居；不涉及词典 sense、WordNet gloss、定义方向或 lexical relation | Lean type checker 验证形式证明；semantic correctness 只在 type-correct 输出上，通过 LLM 生成受限 tactic 的双向等价 Lean 证明与参考 Lean theorem 对照。参考 theorem 的 NL 忠实度作为前提，不由该 checker 重新验证 | 38,951 训练 theorem-proof 对中约 30% proof 为人工写作、其余由 KiminaProver 生成；NL proof 由 Gemini-2.5-Pro 生成。244 项 MINIF2F-TEST-PF 上，pass@32 相比随机 few-shot Kimina-Prover-RL-1.7B，SC 62.70 vs 31.56、TC 95.49 vs 93.85。适合作为组件级自动形式化/形式等价验证参照；不构成本项目的 gloss-support gold 或直接可比基线。 |
| [ProofFlow (Cabral et al., ICLR 2026)](https://proceedings.iclr.cc/paper_files/paper/2026/hash/5fce5198dbf92d5ff45f74504431e2ff-Abstract-Conference.html) | 数学自然语言证明→lemma/step dependency DAG→Lean 4 statements and proofs；184 项 ProofFlowBench 人工验证步骤图；ProofScore 合并结构、Lean 语法与语义分 | 明确先例：DAG 约束形式化时的依赖可用性，并以 no-DAG 消融及复合结构/语法/语义指标评估。其 DAG 是数学证明步骤依赖，不是带 OR 替代与 AND 前提的 Horn clause/witness DAG | ProofScore 的结构与语义宽松检查使用 Claude Sonnet 4 judge；人工验证 benchmark graphs，但本文未报告已查看段落中的标注者间一致性。lean typecheck 只证形式 proof 可编译，不能证明输入自然语言忠实 | 应排除“DAG constrained formalization”“结构忠实度评测”“形式/语义/结构复合分数”为宽泛创新说法。仍需证明本项目不同对象——sense/release 绑定的 gloss span、规则方向支持、AND/OR Horn 语义和独立 source-only 证书重放——是否有额外价值；现阶段只是可检验假设，不是新颖性结论。[定向全文筛读日志](../sources/literature_screening_log_2026-10-06_proofflow_iclr2026.json) |
| [Generating and Checking DNN Verification Proofs (Duong et al., NeurIPS 2025)](https://proceedings.neurips.cc/paper_files/paper/2025/hash/5f326d2e040a20d52438873f5d727e58-Abstract-Conference.html) | Branch-and-bound DNN verification→activation-pattern binary proof tree；独立 checker 验结构并以 MILP/LP 检查每个 leaf path 的不可满足性 | 直接方法先例：复杂 producer 与小型 proof checker 分离、规范化 machine-readable proof、检查结构缺失/真实 soundness bug；论文报告约 800 SLOC checker、16 个网络/400 个 UNSAT 问题，并检出 NeuralSAT false-UNSAT bug | Checker 的可信度仍依赖外部 MILP/LP solver；作者指出浮点/solver 错误风险。证明对象是 DNN activation case split 与约束不可满足性，不含 WordNet sense、gloss-span 语义支持、typed Horn source rules 或 NLI gold | 收窄“独立证明重放/小 checker/proof mutation”宽泛新颖性。可借鉴 producer/checker separation、缺分支变异与 trusted-computing-base 报告；项目 AND/OR Horn witness DAG 与 APTP binary case tree 不等价。见[Phase240全文筛读日志](../sources/literature_screening_log_2026-10-08_neurips2025_independent_proof_checking_phase240.json)。 |
| [Reliable Evaluation (Poiroux et al., EMNLP 2025)](https://aclanthology.org/2025.emnlp-main.907/) | Lean 4 statement autoformalization→BEq+、ProofNetVerif (3,752 human-labeled pairs)、ProofNet# 与 RLM25 (619 research-level pairs) | 是数学形式化评测而非词义知识库；其 gold 是 NL/formal statement semantic-equivalence labels | BEq+ 在 ProofNetVerif precision/recall/F1 98.0/48.3/64.7；长 statement recall 更低，且依赖正确 formal reference | 项目应以独立 sense-disjoint gold 分开测类型检查/证明器通过、语义等价、gloss-span 支持与 abstention；不能直接套用其数字，也不能把 prover success 当语言忠实度。 |
| [Autoformalization in the Wild (Zhang et al., EMNLP 2025)](https://aclanthology.org/2025.emnlp-main.90/) | Wikipedia/arXiv 数学定义→LLM→Isabelle/HOL；含 proof-assistant feedback 与 formal-definition grounding | 直接排除“自然语言定义自动形式化并由证明助手评估”作为宽泛 novelty；任务不是 WordNet sense/Horn 规则 | Def_Wiki/Def_ArXiv 资源；摘要报告选定策略使 self-correction 提升最多 16%、undefined errors 减少 43% | 不能将数学 benchmark 数字外推至 WordNet。研究差异须明确限于 sense identity、span→Horn semantic support、AND/OR 与 proof provenance，并在本域匹配评测。 |
| [NL2FOL (Lalwani et al., Findings IJCNLP-AACL 2025)](https://aclanthology.org/2025.findings-ijcnlp.8/) | 自然语言论证→LLM 分解/FOL→pairwise NLI 补背景关系→CVC4/SMT 分类与反模型 | 已有自然语言→FOL→solver/countermodel 神经符号 pipeline；输入是 fallacy/NLI 论证，不是词典 sense/gloss | LOGIC/LOGICCLIMATE + SNLI 组合评测；作者报告 GPT-4o 路线 F1 .78/.80。论文指出 NLI 漏掉多前提 conjunction，LLM 误译与背景知识遗漏是错误源 | solver 结果只验证给定 encoding，不能背书 gloss→rule 忠实度。需专测 `(a ∧ b) → c` 等分支保持、source-span 规则支持和 sense identity；该分类 F1 不是可迁移的项目效果对照。 |
| [Inductive Learning of Logical Theories with LLMs (de Souza et al., AAAI 2025)](https://ojs.aaai.org/index.php/AAAI/article/view/34546) | 带形式推理器反馈的 LLM 逻辑理论归纳；按规则依赖表达力分层，并比较 ILP 基线 | 合成关系规则的归纳，不从 WordNet gloss 生成 sense 级定义 | Prolog 执行结果和错误实例用于迭代修正规则；论文报告长谓词关系链是主要困难之一 | 可启发按依赖深度/分支与闭包覆盖做独立 stress test；论文分层与本项目 witness 深度并非同一个量，需重新定义切分和基线，不能直接搬用性能结论。 |
| [Direct Dependency Retrieval (Wang et al., ACL 2026)](https://aclanthology.org/2026.acl-long.821/) | 数学描述→formal library dependencies；Suffix Array Check 查对象存在，500k+ 依赖样例 | 形式库依赖检索，非 lexical-sememe 或 WordNet sense graph | 对 library object 的存在性做确定性字符串索引验证，不保证所检索依赖在源语义上正确 | 对项目原语/谓词 vocabulary 有启发：候选 ID 的“存在性/版本一致性”可机械核验，但还需 sense alignment 和 evidence faithfulness。 |
| [FOL Closeness Metrics (Thatikonda et al., Findings EMNLP 2025)](https://aclanthology.org/2025.findings-emnlp.910/) | 全文核查 FOLIO/MALLS 上 BLEU、ROUGE、METEOR、LE、BERTScore、Smatch++；量词、否定、AND/OR、操作符、谓词和变量受控扰动；另以 GPT-4o 三候选对比 metric ranking 与 o3-mini judge。 | 明确显示指标对表面内容与逻辑操作符变化的敏感性不同；用来设计公式层 mutation diagnostics。 | o3-mini 排名对齐不是全体输出的人类 gold；仅 87 条由三个人类标注者用于挑选 judge，且作者承认数据标签/模型版本限制。不得用自动公式指标代替 gloss-span source-support 标注。筛读记录见[日志](../sources/literature_screening_log_2026-10-06_fol_closeness_metrics.json)。 |
| [A Theorem-Proving-Based Evaluation of Neural Semantic Parsing (Funakura et al., BlackboxNLP 2025)](https://aclanthology.org/2025.blackboxnlp-1.18/) | SICK sentence→ccg2lambda event-semantics FOL；Vampire 对生成式解析公式与参考公式做双向蕴含，并与 Counter/Dmatch 对照 | 近期逻辑形式质量评价方法邻居；输入是 NLI 句子而非 WordNet gloss→定义规则，且在 workshop 发表 | 全文筛读；只留参考解析的 prover label 与原 entailment/contradiction 标签一致的样本并排除 neutral；报告模型/规范化公式分层结果 | 可参考“图匹配与 prover 等价并报”及 coordination/变量绑定压力分层。其 prover accuracy 是相对 CCG 参考公式，且未测端到端 NLI；不能当作公式对原 gloss faithful 的证据。本项目仍须独立测 sense/source-span support。 |
| [TROVE (Zhu et al., ACL 2025)](https://aclanthology.org/2025.acl-long.577/) | 多来源文本→目标句到来源句的追踪和 Quotation/Compression/Inference/Others 分类；英语/中文、11 种场景；人类核验 4,388 英语及 811 中文目标句 | 句级细粒度来源定位和 typed evidence-use 是已确立先例；任务针对生成内容的来源使用，不是 WordNet sense-bound gloss support 或形式证明 | 关系分类仍难，来源检索可能漏证据；不覆盖无来源 hallucination。TROVE F1 不可与本项目 lexical-support/proof 指标横比 | 可借鉴来源定位、关系分类和人工裁决流程；只有 citation/source ID 仍不足以证明 gloss span 蕴含某个 typed rule。全文筛查见[Phase253 日志](../sources/literature_screening_log_2026-10-08_phase253_fulltext_addendum.json)。 |
| [FoVer (Pei et al., TACL 2025)](https://aclanthology.org/2025.tacl-1.61/) | LLM 输出自然语言推理→FOL→Z3 检查 | 面向一般推理解释，不从 WordNet 定义自动生产规则 | theorem-prover 检查是重要先例；原始 NL→FOL 是否忠实仍需独立评估 | “LLM + FOL + prover 验证”不是新贡献。项目需把新意放在定义知识的可追溯生产、义项级规则忠实性和错误归因。 |
| [Entailment-Preserving First-order Logic Representations (Lee et al., ACL 2025)](https://aclanthology.org/2025.acl-long.286/) | 多前提 NL entailment→多候选 FOL；Vampire 检查原始 entailment 标签是否保持；EPR/EPR@K/EPR@K-Oracle 作 reference-free 指标，并以 iterative learning-to-rank 训练 T5-base | **最直接评测近邻之一**：证明“NL entailment→FOL→prover + 标签保持指标”已有 ACL 主会先例；但不处理 WordNet sense/gloss 编译 | 三个数据集 EntailmentBank/eQASC/e-SNLI；摘要报告 EPR +1.8–2.7%、EPR@16 +17.4–20.6%。另过滤新谓词/常量与未使用前提的伪证明；局限包括 FOL 表达范围及缺少语言控制最小对 | EPR 是下游 label preservation，不等价于每个公式对原句语义忠实或有 gloss-span 支持。若迁移，应冻结 K，分报 top-1/top-K/oracle，添加反矛盾与方向对照；此外独立评 source-span gold 与 sense identity。不能将 RTE 的 EPR 数值外推为项目成效。 |
| [Natural Logic at the Core: Dynamic Rewards for Entailment Tree Generation (Shi et al., Findings ACL 2025)](https://aclanthology.org/2025.findings-acl.893/) | 自然逻辑原则用于强化学习的动态奖励，引导 EntailmentBank 上的 entailment tree 生成 | 是证明树生成的近邻，但不是词典 gloss 到有来源 Horn clause 的构建流程 | 官方摘要报告在 EntailmentBank 上优于其 state-of-the-art 对照；树上自然语言推理与机器可重放 Horn proof DAG 的结论范围不同 | 若比较解释质量，应统一 claim 与标注 gold，并分别测 premise coverage、方向正确性及逐步验证；不能仅凭输出树形结构推断逻辑证书有效。 |
| [Faithful and Robust LLM-Driven Theorem Proving for NLI Explanations (Quan et al., ACL 2025)](https://aclanthology.org/2025.acl-long.867/) | e-SNLI/QASC/WorldTree 的自然语言解释→形式逻辑→theorem prover，并用逻辑式指导 proof sketch/refinement | 明确处理 autoformalisation 信息损失、逻辑结构精度、句法修复与 prover feedback；不是词典义项或 gloss→Horn 知识获取 | 官方摘要报告三数据集上的 autoformalisation 与 explanation refinement 改进；本次只核对官方元数据和摘要，未重新审读全文/附录，不外推其证书格式或指标细节 | 进一步排除“LLM 形式化 + theorem prover 检验 NLI”作为独立新颖点。可借鉴分层处理形式化/证明失败；本项目的区别假设仍须落在 sense-version 来源、gloss-span→方向规则支持及规则图证据链，并经匹配实验验证。 |
| [Language Model as Planner and Formalizer under Constraints (Huang et al., ACL 2026)](https://aclanthology.org/2026.acl-long.624/) | CoPE 在 BlocksWorld/CoinCollector 中加入 initial/goal/action/state 四类自然语言约束；每域100条，三位标注者写非重叠约束后筛选。比较直接 planner 与 PDDL 1.2/PDDL3/SMT/LTL formalizer、编辑和最多三轮修订；主评测每域人工配对100项，以 ground-truth PDDL 验证计划。 | ACL 官方全文核读任务定义、数据、实验、结果、错误分析与限制。作者指出 plan correctness 可能出现“计划有效但 formalization 不忠实”的 false positive；20 项抽查为 0 只能是小样本审计。合取、否定和歧义仍是其未覆盖现象。 | 为受控自然语言约束形式化、按现象切片与 solver-backed downstream validation 提供主会先例；但不处理 WordNet sense、gloss-span support、typed Horn 或源绑定 proof DAG。对项目最关键的是把语义支持、人审形式化、proof replay 与下游效用分开测；不可移植 CoPE 数值。详见Phase265 深度报告和[全文筛读补充日志](../sources/literature_screening_log_2026-10-08_acllong2026_cope_fulltext_phase265.json)。 |

| [The Faithfulness Gap / BPF (Mohammad & Sheikh, MusIML workshop at ICML 2026; arXiv v1)](https://arxiv.org/abs/2606.16541) | NL mathematical statement→Lean 4 formalization; bidirectional provability fingerprints; mechanically perturbed drift twins, contrastive probes, bounded Lean oracle and 2,183-pair DriftBench | 新近直接邻居：排除“可类型检查/可证明不等于语义忠实”作为宽泛新颖点，也排除把 contrastive drift probes/controlled formalization-drift evaluation 单独称为首次。场所按作者页记录为 MusIML@ICML workshop，非已核实的 ICML 主会论文。 | 作者报告 controlled split 上 BPF+CPG 在 3% FPR 下 detection 89.6%，wild split 384 pair 上 κ=.77（IAA κ=.81）；这些数字未复现。v1 的 Prop. 4.2 证明似乎缺少 probe-set separation/N inclusion 条件；Theorem 8.2 的 Occam 论证也需补足，机器定理数值不可直接当作保证。 | 项目尚可检验的窄假设是 sense/release-bound gloss span→typed direction-specific Horn support，并与 source-linked witness replay、lexical NLI 在同一候选集关联；目前既未证明新颖也未证明有效。BPF 的 probes 可启发盲法挑战集，但 probe labels 不能代替独立 gloss-span source-support gold。详见Phase267报告和[筛读日志](../sources/literature_screening_log_2026-10-08_faithfulness_gap_driftbench_phase267.json)。 |
| [Don’t Judge a Book by its Cover (Borah et al., EACL 2026)](https://aclanthology.org/2026.eacl-long.95/) | Logifus 生成逻辑等价但表层改写的推理问题；LogiQAte 共 1,108 题，其中 272 题为 Obfus FOL | 逻辑等价改写可作为推理鲁棒性诊断；其对象是已有推理题/FOL，不涉及 sense linking、定义来源 span 或 Horn 编译 | 官方全文的任务与附录段已核；Obfus FOL 使用 Prover9 并经双人复核等价，作者报告模型在逻辑混淆下性能下降 | 可启发单独的释义/公式等价改写切片；必须分别评分语义保持、span 支持、证明重放和覆盖，不能据其结果声称本项目鲁棒。 |
| [Unifying Inference-Time Planning Language Generation (Kagitha et al., Findings ACL 2026)](https://aclanthology.org/2026.findings-acl.415/) | 规划文本→按中间表示（NL/Python/PyPDDL/PDDL）组织的 12+ planning pipelines→PDDL solver 与 VAL 验证的 plan | 将中间表示层数、solver feedback 与迭代修订做成可比较组件；不涉及 sense linking、gloss spans 或规则语义支持 | 4 个开源模型、4 个模拟规划环境，每环境 100 个样例；分别报告语法正确和经 ground-truth PDDL 验证的 plan accuracy，3 次运行均值。Level 2 最佳路线在 8/8 模型×领域组合中胜过 Level 0/1；10→50 blocks 的扩展显示更深管线未必更稳 | 为本项目的 pipeline matched ablation、调用/计算预算控制和结构压力分层提供近期评测先例；形式解析与下游计划有效性仍不能替代源文本到规则的语义忠实性。 |
| [R1-RE (Dai et al., ACL 2026)](https://aclanthology.org/2026.acl-long.1587/) | 带实体标记的关系分类 + 关系定义指南 → 模型判定；强化学习奖励分开检查格式与 gold 关系标签 | 是 annotation-guideline-conditioned RE 的近期主会先例；依赖有限关系标签，不构建 sense-linked gloss AST 或规则 | SemEval-2010 Task 8 与私有、人工标注 MDKG；报告训练后 OOD 提升。私有测试集和作者的类人标注行为解读不能独立复核 | 可借鉴把指南显式注入模型输入，并区分格式检查和标签准确率；分类 reward 不证明 gloss-span 语义支持、Horn entailment 或 proof replay，因此不是本项目直接 gold/baseline。 |
| [CARL: Constraint-Aware Reinforcement Learning for Planning with LLMs (Qi et al., Findings ACL 2026)](https://aclanthology.org/2026.findings-acl.1069/) | 有约束/去约束输入→分布差异约束奖励 + 任务奖励→训练规划模型 | 强化模型对任务约束的敏感度，不产出独立逻辑规则或证明证书；T-Eval 隐式约束由 GPT-4o 抽取 | BlocksWorld、TravelPlanner、T-Eval；Qwen3-8B 在论文指定 TravelPlanner 设置 final pass rate 从 RFT 2.2% 到 CARL 56.1% | 约束关注训练可作远期对照；输出遵约或奖励升高不等于 gloss-span 支持。该结果不是本项目可比基线，也不能证明 WordNet 规则语义正确。 |
| [SymbCoT (Xu et al., ACL 2024)](https://aclanthology.org/2024.acl-long.720/) | 自然语言 context→symbolic representation→逻辑规则推理计划，并由 verifier 检查转换和推理链；覆盖 FOL 与 constraint optimization 五个数据集 | ACL 主会已有“NL 转符号 + 规则推理 + 显式验证”完整流程，收窄通用神经符号 pipeline 的新颖空间 | 官方全文检查；其逻辑任务不涉及 WordNet sense 识别、词典 gloss-span→单条 Horn 规则支持或来源绑定可重放证书 | 可对照多阶段错误归因与 verifier 接口，但不是 lexical-definition 方法基线。项目可能的增量只能由 sense/source、directional support gold 和独立证书验证来界定。 |
| [NSF-CoT (Pramanik et al., Findings ACL 2026)](https://aclanthology.org/2026.findings-acl.516/) | Contextual QA 的推理步骤→ground atoms；通过事实消融归因及 Z3/LLM judge 评 groundedness、validity、utility | 逐步上下文忠实度审计与形式校验相邻；展示多个信号必须分开量化 | 官方全文已检查；作者指出 FOL 抽象会漏掉模糊量词、情态、习语，LLM fallback 覆盖也可能变化 | 审计对象是 QA 中间推理步骤，不是义项绑定的词典释义、source-span→Horn 支持标注或 lexical benchmark；不能当作直接基线。 |
| [PrefixNLI (Harary et al., ACL 2026)](https://aclanthology.org/2026.acl-long.63/) | 对 source text 与不完整 hypothesis prefix 作二元 entailment；MiniTruePrefixes 在 SummEditsPrefixes/RAGTruthPrefixes 上较 MiniCheck 高 5.2/14.3 unfaithful-class F1 | 近年的 source-grounded NLI 与生成期事实性控制；prefix 标签允许“存在可信续写”语义，和完整命题支持不同 | 全文核到 benchmark 构造、controlled decoding、误差及限制；误报含浅层 heuristic 与泛化错误，模型英语训练且新闻摘要域 | 是 NLI 评测/生成时 gate 的邻接工作，不是 WordNet 静态 gloss claim、必要/充分规则或证明器基线；其分数不可移植。仅在项目有不完整候选文本时借鉴 prefix slice。 |
| [QASemConsistency (Cattan et al., TACL 2026)](https://aclanthology.org/2026.tacl-1.6/) | 生成文本拆成 predicate–argument QA，再逐 QA 判定是否受可信来源支持；3,098 QA，三名标注者多数票，三任务 Fleiss κ=.67–.79 | 与 claim-level source-support 标注高度邻接，显示同一谓词可有支持/不支持的不同论元关系；但 QA 解析单元不等于有类型定义 AST | 全文核到人类协议、自动 NLI/LLM 结果与限制；其任务无 AND/OR rule structure、sense resolution 或证书 replay | 直接启发每条最小方向规则独立标 source-span 支持，并分别报告分解与支持判断；不构成 WordNet gloss support gold 或形式化方法基线。指标/模型成绩不能跨任务比较。 |
| [QC-NLI (Canby et al., Findings ACL 2025)](https://aclanthology.org/2025.findings-acl.765/) | 以 query/aspect 条件化两份文档间的 entailment 或 contradiction；覆盖 fact verification、RAG hallucination 和文档冲突，21,655 条由既有数据转换的样例 | 直接说明 source-support 标签需固定被判断的语义方面；但作者把长文 source-span attribution 明确列为 future direction | PDF 定向核读：每数据集仅抽 33 或 51 项人工审查，且各标注者共同样本仅 7 项；报告标签质量 75.76%–93.94%。数据仅英语、转换使用 GPT-4o、基线仅 prompting | 可借鉴以原子规则/问题显式条件化 NLI；转化数据量不能解释为人审 gold 规模，且未涉及 gloss sense、Horn 表示或 proof replay。 |
| [HaluMap (Chen et al., Findings ACL 2025)](https://aclanthology.org/2025.findings-acl.96/) | 对源文段与生成文段构建 entailment/neutral/contradiction 矩阵，再用源文内部 self-NLI 背景信号校准，以可视化并估计 faithfulness hallucination | 直接 source-to-claim NLI 与可解释定位邻居；分段粒度可变，但不是逻辑规则或证明图 | PDF 定向核读：校准方法在 SummaC 平均 balanced accuracy 75.8，SummaCZS 为 70.7；作者将研究范围限定为 faithfulness 类幻觉，与 world factuality/其他幻觉类型区分 | 可参考 pairwise source/claim 与背景校准误差；只评价生成文本源忠实度，不判断 WordNet 义项或定义规则的 AND/OR 语义。 |
| [RefNLI (Chen et al., Findings NAACL 2025)](https://aclanthology.org/2025.findings-naacl.450/) | 构造 1,143 个 premise/hypothesis 可能指向不同实体/事件上下文的样例，测量 NLI 的 reference-determinacy 偏差与人类标签分歧 | 对项目的义项/实体对齐前置审查直接相关：若 source 与 claim 参照对象不一致，标签本身会变；不是定义解析方法 | PDF 定向核读定义、benchmark、模型分析和局限；实验固定单一模型架构，作者把扩展更多模型和 LLM 留作后续工作 | 应先冻结 sense/reference identity 再评分来源支持；该基准不含 gloss-span 标注、逻辑规则或证明证书。 |
| [Comprehensiveness Metrics (Dejl et al., Findings ACL 2026)](https://aclanthology.org/2026.findings-acl.1744/) | 对照 NLI、QA、端到端完整性指标；NLI 路线把原子陈述组织成 entailment graph 并输出 covered/missing facts | 与“原子 claim 分解 + 关系图”相邻，但边表示评估器的 NLI 判断，不是逻辑推导超边或 why-provenance | PDF 定向核读：50 样本人工错误审查中 NLI 输出仅 48% 完全正确，QA 66%、E2E 88%；局限含图过简、LLM/检索误差传播、未评价源可靠性 | 可借鉴单独核验原子分解、关系边和覆盖输出；摘要完整性任务不是 gloss-rule correctness，不能把其 NLI graph 当 proof DAG。 |
| [FactCG (Lei et al., NAACL 2025)](https://aclanthology.org/2025.naacl-long.258/) | 文档抽取 context graph，采样多跳子图生成正例 claim，并破坏关系生成负例，用于训练 grounded factuality checker | 图结构用于多跳 claim / evidence 组合，和项目的结构证据使用相邻；图是从普通文档抽取，不是定义编译所得的逻辑规则 | 定向核读官方 PDF 的方法、实验和局限：作者指出关系抽取粒度难确定，抽取图自身不能完美处理源文档内隐含推理；真实 RAG claim 有多跳链 | 可启发多跳/缺边压力集和图抽取误差分析；不处理 WordNet sense、typed AND/OR Horn rules 或可重放 proof，非 lexical entailment 匹配基线。 |
| [FactReasoner (Marinescu et al., Findings EMNLP 2025)](https://aclanthology.org/2025.findings-emnlp.785/) | 长文本拆原子事实并检索上下文，以概率图建模 claim/context 间 entailment、contradiction、equivalence 后估计支持概率 | 是事实性评估中的图式证据聚合近邻，但输出为概率评估，不是确定性证明或规则 provenance | 定向核读官方 PDF 方法、评测与局限；作者指出 atomization、检索及 LLM 关系抽取均影响结果，较丰富关系图的提示调用开销较大 | 可参考将证据冲突与不确定性单独建模；不能证明词典来源规则语义，也不提供 Horn proof replay。 |
| [CiteEval (Xu et al., ACL 2025)](https://aclanthology.org/2025.acl-long.1574/) | 在 retrieval context、query、生成文本等完整语境中细粒度评价 citation quality，构建 CiteBench 和模型指标 | 提醒 binary/ternary NLI support 只是 citation-quality 的一个方面；任务是生成引用评测，不是词汇逻辑编译 | 本轮核对官方页面摘要与书目信息，未读全文；不据摘要补充指标数字或细节 | 借鉴把来源支持与引用充分性区分；不构成 sense-linked gloss gold、规则来源对齐或 proof baseline。 |
| [Self-Correcting RAG (Xu et al., Findings ACL 2026)](https://aclanthology.org/2026.findings-acl.1052/) | MMKP 选择上下文，NLI-guided MCTS 搜索并验证 RAG 答案的 faithfulness | NLI 被用作检索/生成阶段的搜索信号，属于上下游系统近邻，不是形式来源证明 | 本轮仅核对 ACL 官方页面与摘要；未审全文，不能据此判断其证书或内部形式化能力 | 可作 NLI-guided search 的系统类背景；不是 gloss→Horn 获取方法、证书 replay 基线或可比性能结果。 |
| [Transform Retrieval (Guo & Liang, NAACL 2025 Short)](https://aclanthology.org/2025.naacl-short.50/) | 变换 query embedding 以促进 RAG 中的 textual-entailment retrieval | 与寻找能语义支持回答的证据相关，但研究对象是检索向量对齐，不是逻辑推理 | 本轮只核对 NAACL 官方页面与摘要 | 提醒区分 evidence retrieval 与 evidence entailment/proof；不作为 WordNet 或 Horn 方法基线。 |
| [Prover-Guided Correction for NL-to-FOL Conversion (Zhu et al., FLINS-ISKE 2026)](https://link.springer.com/chapter/10.1007/978-981-92-2480-7_17) | 自然语言↔TPTP FOL；E prover/parser diagnostics 进入迭代验证—修复环；出版社摘要报告对 652 个 TPTP 问题的评估 | 近期 prover-feedback 转换修复邻居，显示语法可解析/可验证仍与 source semantics 分离 | 本轮仅核对 Springer 出版页与摘要，付费章节未读；作者摘要明确说 semantic equivalence 仍具挑战；FLINS-ISKE 论文集/LNCS 不列为 ACL/AAAI 主会先例 | 可列作 parser–prover repair 的相邻对照，不是 lexical gloss baseline；需把自动修复率与人工 source-semantic support 另报。 |
| [FOLDCoVe (Asghari et al., ASONAM 2025 / LNCS 16324)](https://link.springer.com/chapter/10.1007/978-3-032-14107-1_6) | 复杂 claim→FOL predicates→低成本 LLM 对长来源逐项核查；出版社摘要报告 HOVER 多跳事实核查准确率改善 | 是 source-grounded claim verification + FOL decomposition 的跨域邻居，非词典定义/义项规则编译 | Springer 元数据和摘要已查；full chapter 未取得。本轮不扩写指标数值、predicate faithfulness 标签或评测细节 | 它进一步支持将 claim→formula、来源逐项核验与形式推理拆开评价；不提供 sense-disjoint gloss-span support gold 或可重放 Horn why-provenance。 |
| [FOL-Traces (Lee et al., Findings EACL 2026)](https://aclanthology.org/2026.findings-eacl.115/) | 1.5M 条程序化 FOL 规则生成多步推理轨迹，以 SymPy 逐步验证；含 7.40M train、5K dev、8.64K test traces，另提供 8.80M curated train | **步骤级逻辑过程验证已有先例**；数据主要为合成 FOL，LLM 实例化谓词；不含 WordNet sense、gloss span 支持或 source provenance | masked operation accuracy 约 45.7%，两步 completion 约 27%；步骤代数验证不说明自然语言支持初始公式 | 应删除“此前没有大规模逐步机检逻辑轨迹”类宽泛表述。仍待检验的是从具体 gloss span 到方向化 typed Horn literal 的语义支持，以及其来源绑定证明的独立重放。全文筛查见[Phase253 日志](../sources/literature_screening_log_2026-10-08_phase253_fulltext_addendum.json)。 |
| [FOLX-KG (Hao & Wu, ACL 2026)](https://aclanthology.org/2026.acl-long.1230/) | ACL 2026 全文复核：KG claim→扩展 FOL 公式→可执行 Python prover 与 Fact-FOLX-KG（43,821 对）；公式解释器与作者标签 100% 一致。数据由公式/子图与模板构造，并辅以 LLM 改写。 | 增加比较谓词、计数量词；两批各 5,000 条 claim 人审一致性报告为 96%/94%，重叠 200 项 Cohen’s κ=0.86；每种方法随机抽 100 条错误预测，分 syntactic / logical / execution error。 | 有执行型 KG 推理程序；全文未描述可独立重放的形式 proof-certificate 工件。它的人审检验 claim–formula 一致性，不检验原始释义 span 对方向性规则的支持。 | 逻辑片段表达力及分层质控已有 ACL 2026 先例，不能把“用 FOL”或“执行程序”当贡献。项目可借鉴人审抽样与错误分型，但须另测 source/version、WSD、span support、necessary/sufficient 方向、proof replay 与 unknown；DBpedia factual claim 指标不能移植为 WordNet gloss 结果。 |
| [NL2Logic (Putra et al., Findings EACL 2026)](https://aclanthology.org/2026.findings-eacl.317/) | 自然语言 premise/hypothesis→递归解析的 FOL AST→确定性两遍 solver-code 生成 | 通用 FOL/NLI，未做 WordNet sense linking、gloss→Horn rule 或定义 source-span mapping | 在 FOLIO、LogicNLI、ProofWriter 上测语法正确率与下游 NLI accuracy；后者是公式语义质量的间接 proxy，并非逐公式人工支持 gold | 作为 AST parser/compiler 强基线；另外检查不一致/不可满足前提、跨句语义、gloss-span 必要/充分方向。接近 99% syntax 或论文 NLI 提升不能证明 lexical rules faithful。 |
| [UFAL-CUNI SemEval-2026 Task 11 system](https://aclanthology.org/2026.semeval-1.418/) | 三段论→LLM FOL parser→transpiler→Prover9；可选翻译和基于删除-重跑的相关前提选择 | 形式有效性和 premise relevance，不是 WordNet taxonomy 或释义知识获取；SemEval workshop proceedings | 报告 shared-task metrics 与模块消融；验证扩展对若干任务使用由训练样本构造的合成数据 | 借鉴明确模块边界、前提 ablation 和低内容效应评测；需在自己的 sense-disjoint gloss gold 上重建基线，不能对比不同任务排行榜分数。 |
| [Hybrid Knowledge Base formal reasoning (Cima et al., AAAI 2026)](https://ojs.aaai.org/index.php/AAAI/article/view/38971) | 逻辑 ontology + 对 concept/role 的 ML classifiers→模型论语义、consistency 与 query answering | 形式化神经符号 KB 框架，不做自然语言/WordNet 定义到 ontology 规则的知识获取 | 提供复杂度定理；作者将 ASP encoding 的实证验证列为 future work | “把学习型分类器和符号 ontology 接起来”不是单独的新颖性；项目要验证的具体切口是 sense/version/source-span 对齐、directional gloss support 和可重放证明，不与其复杂度结果做性能比较。 |
| [VoG: Stepwise Verification on Knowledge Graphs (Zhao et al., ICLR 2026)](https://proceedings.iclr.cc/paper_files/paper/2026/hash/ab1ee157f7804a13f980414b644a9460-Abstract-Conference.html) | 问题→LLM reasoning plan→Freebase/Wikidata triples→stepwise consistency check and plan revision | 多跳 KGQA 的外延三元组与自然语言计划；非 gloss-derived、sense-indexed OR-of-AND Horn rules | LLM + frozen DeBERTa 对比预测 observation 与 retrieved triples；没有独立重放的 Horn proof certificate 或 gloss-span rule support | 已有 ICLR 2026 图上逐步验证先例，故勿泛称“首次在图上验证 LLM 推理”。其中心性/子图连贯性仅列作 future work；本项目应在 adjudicated gold 上检验超图结构是否能预测错误/拒答/审核成本，且不得当作逻辑证据。 |
| [LogicRAG (Chen et al., AAAI 2026)](https://ojs.aaai.org/index.php/AAAI/article/view/40278) | 查询→临时子问题 DAG→拓扑排序与图/上下文剪枝→自适应检索 | 推理时构造的 DAG 表示 query decomposition dependency，不是从 WordNet 定义编译的、保留 AND/OR 分支的 Horn 依赖超图 | 本轮核对 AAAI 官方论文页及摘要；页面报告其目标为 GraphRAG 预构图成本/时延问题，但未在本轮审读全文，不记录具体实验数值 | 相关在“逻辑依赖结构怎样辅助读出/检索”，但与本项目目标相反：LogicRAG 是 query-time、任务特定结构，本项目是 corpus-time、版本固定且需可复算的知识图。可启发独立测量结构构造与 readout 成本；不能据其 QA/效率结论推断本超图有语义效用。 |
| [GenProve (Wei et al., ACL 2026)](https://aclanthology.org/2026.acl-long.228/) | ReFInE 将答案句链接到来源文档/句子索引并标记 Quotation、Compression、Inference；GPT-4o 提议后，经三名筛查者和三名专家核查 evidence sufficiency 与 relation correctness。12,540/5,256/4,838 个 SFT/GRPO/eval instances；14 个模型比较，200 个 eval instance 由三位专家评分。 | 直接先例：细粒度 source attribution、typed evidence-use 与人类证据充分性裁决不能泛称为新颖。作者也指出 provenance 可能遗漏反证或替代解释，不能作为 definitive validation。任务仍是 RAG 生成中句级来源使用关系，不是 WordNet sense/release、gloss span→lexical rule、typed Horn 或独立 proof replay。 | GenProve 报告 provenance P/R/F1=54.96/51.26/51.21，最强列示非 GenProve baseline F1=44.55；其 benchmark 分数不可与 gloss-support / proof-validity 指标横比。可检验的较窄假设是建立义项和版本绑定的 gloss-span→typed Horn literal 支持标注，并独立 replay 规则与 witness；目前没有项目 gold 或 matched 结果证明其新颖性/效果。详见[Phase252 全文筛读日志](../sources/literature_screening_log_2026-10-08_genprove_acl2026_phase252.json)。 |
| [Why-Provenance for Datalog (Calautti et al., AAAI 2024)](https://ojs.aaai.org/index.php/AAAI/article/view/28914) | Datalog query answer→可枚举导致答案的输入事实子集及其推导解释 | 形式逻辑查询 provenance，不是从自然语言定义抽取知识 | 用 proof trees 刻画替代支撑，并以 SAT 增量生成解释 | 与项目证书/provenance 最接近的形式方法基线。当前每个 head 的一条 witness DAG 不是 why-provenance 的全部替代支持；需明确定义证据目标，避免仅复刻“保存 proof DAG”。 |
| [Formal Reasoning over Hybrid Knowledge Bases (Cima et al., AAAI 2026)](https://ojs.aaai.org/index.php/AAAI/article/view/38971) | 逻辑 ontology + ML binary classifiers→hybrid KB query answering | 研究符号/子符号知识的形式推理集成，不从释义构造 ontology | 研究查询回答与复杂度；不是 gloss-to-rule provenance pipeline | AAAI 2026 已有神经符号形式推理工作。应把 NLI 定位为语义候选/校验组件，而非“神经符号结合”本身的新颖点。 |
| [Forer & Hope, Inferring Scientific Cross-Document Coreference and Hierarchy with Definition-Augmented Relational Reasoning (TACL 2026)](https://aclanthology.org/2026.tacl-1.36/) | 科学论文中的概念提及及检索到的上下文→单概念定义、关系定义→跨文档共指与概念层级 | 科学概念级、上下文敏感的层级推断；不是 WordNet sense gloss 的通用逻辑编译 | 生成定义后用于神经模型/层级评分，没有为定义规则提供本项目所需的可重放 Horn 证明证书 | 很近的跨领域先例：全量测试集上 relational definitions 相对 Mistral-7B 将 hierarchy F1 从 56.84 提至 58.03；Hard-10 上 hierarchy F1 提升 6.72（配对 bootstrap p=0.047）。比较时应突出输入定义的来源与上下文、预测对象以及证书语义不同；不可泛称“首次用定义恢复层级”。 |
| [dos Santos & Leal, Can a Large Language Model Replace Humans at Rating Lexical Semantic Relations Strength? (Computational Linguistics 2026)](https://aclanthology.org/2026.cl-2.7/) | 英语/葡萄牙语词对及人类 lexical similarity/relatedness 评分→LLM 连续强度评分 | 词对关联强度，不是 sense 对齐的蕴含方向或定义规则验证 | 以 Pearson 相关系数评估人类评分拟合；不是证明有效性或源 gloss 支持度 | 评估了 45 个数据集分区、多个模型；抽样实验平均相关约 0.701，最佳模型约 0.839。它支持把 LLM/NLI 当作语义评分或候选排序工具，但不能把高相关解释为超类蕴含被验证；项目需要单独标注 relation direction、sense、语义蕴含与 source-span support。 |
| [FormalScience (Meadows et al., ACL 2026)](https://aclanthology.org/2026.acl-long.1057/) | 科学问题/解答→人机协作 Lean4 形式化流程与 200 条 FormalPhysics 资源 | 物理/数学 formalization，不是词典 sense 或 WordNet 关系；本轮已筛读正式 PDF 全文 | 流程构造的数据 formal-validity 为 100%，但模型 statement-autoformalisation 最佳 agent 为 31%；资源 LLM-judge Logical Preservation / Mathematical Consistency 为 72.0% / 72.5% | 形式可运行/可证明与忠实表达 gloss 必须分开评估；后者需盲标 gold/人审。跨领域先例，不是 WordNet 直接实现。 |
| [CriticLean (Peng et al., ACL 2026)](https://aclanthology.org/2026.acl-long.139/) | 数学自然语言题→Lean formalization；训练 critic 判定形式化是否保留原题语义，并与编译器检查组合迭代 | 语义保真 critic 与项目的 source→rule semantic gate 邻接；数学题/Lean statement，不是词义释义、WordNet sense 或 source-span rule support | 500 对 CriticLeanBench；论文报告其 500 题人工评估中 critic 流程准确率 86.0%，compiler-only 为 59.0%；人工/自动分层筛选 | “形式检查通过≠语义忠实”有 ACL 2026 实证先例。可把 NLI/LLM critic 作为候选筛查器，但必须对 blind human source-support gold 报告 precision/recall、校准和 abstention；critic 本身不能成为独立真值。作者注明样本规模、生成器候选质量和 critic 偏差风险。 |
| [Assessing Logical Coherence of LLMs via Fine-Grained NLI (Apaolaza et al., LREC 2026)](https://aclanthology.org/2026.lrec-1.423/) | PhrasIS 自然短语对与其方向反转配对→7 类细粒度推理标签；报告 soft/hard causal coherence | NLI 方向一致性评测方法邻居；不含 WordNet gloss、source-span→rule gold、Horn 证明或证书 | 官方全文报告 PhrasIS >10k phrase pairs；unseen HardCoH 的 DeBERTa-v3-base combined positives 为 0.79。论文明确 coherence 不必然等于 correctness，且单一 PhrasIS 不能代表更广推理任务 | 为本项目增加 gold accuracy 之外的方向反转 stress test；仅对语义上可逆的裁决样例重标反向 gold，报告方向一致性与正确率，保留三类 NLI 标签并与 PhrasIS 七类结果分开。不能把 soft coherence 当语义支持或逻辑有效性。 |
| [Harmful Factuality (Li et al., Findings of EACL 2026)](https://aclanthology.org/2026.findings-eacl.46/) | 对源文实体注入受控事实错误→测试摘要、改写和上下文 QA 是否擅自纠正输入 | 直接关联“事实正确”与“忠实来源”冲突；不是 WordNet gloss 逻辑化/义项关系评估 | WikiEntities 与多种 LLM；论文提出 source-fidelity challenge 并报告限定设置下 prompt mitigation；作者明确语料/模型覆盖有限 | 项目需区分 gloss 支持与外部/WordNet relation correctness；若知识来源冲突，应记录冲突或 unknown，不静默改写 source。跨任务发现不可当作项目效果基线。 |
| [Semantic-KG (Wei et al., NeurIPS 2025 Datasets and Benchmarks Track)](https://proceedings.neurips.cc/paper_files/paper/2025/hash/26cf2796210e804ad554b8734ce0760b-Abstract-Datasets_and_Benchmarks_Track.html) | 利用 KG 生成多域语义相似/不相似自然语言陈述对，并按差异类型细分 | 支持构造类型化语义扰动评测；摘要级筛读，非定义解析或 WordNet 上下位基准 | 官方摘要报告方法性能受领域与差异类型影响，没有单一语义相似方法始终最佳 | 后续 challenge set 应区分 AND/OR、方向、sense/source、属性增删等错误，不能用一个 NLI/相似度总分代表来源支持；该工作不是可直接复用的项目 gold。 |
| [From Hypothesis to Premises: Selective Symbolic Translation (Li et al., AAAI 2026)](https://ojs.aaai.org/index.php/AAAI/article/view/40434) | NL 推理题→高置信 span 的 FOL 翻译 + 假设驱动的回溯推理 | 一般推理任务，不是规模化 WordNet gloss 编译；本轮已筛读 PDF，含五个 benchmark 及 All-NL/All-FOL 消融 | 作者报告 selective strategy 平均较 All-NL 和 All-FOL 分别提高 7.2% / 4.7% | 选择性形式化/abstention 已有 AAAI 主会先例，不能单独 claim novelty。可将 unknown/needs-review 作为系统原则，但阈值需用本项目 gold 校准；LLM reflection 不等于独立 gold。 |
| [DeepProofLog (Jiao et al., AAAI 2026)](https://ojs.aaai.org/index.php/AAAI/article/view/39396) | stochastic logic programs→神经引导 SLD resolution 与证明搜索 | NeSy 推理含 WN18RR 等知识图谱任务，但不涉及 gloss-to-rule 生成 | 本轮已筛读 PDF：把 SLD resolution 映射至 MDP，以动态规划/RL 搜索证明空间 | 区分 certificate replay correctness 与 search cost；学习策略不替代独立 soundness verifier。不可与当前确定性有限正 Datalog checker 直接比较性能。 |
| [Ancient Greek synset selection (Brigada Villa et al., LT4HALA @ LREC 2026)](https://aclanthology.org/2026.lt4hala-1.38/) | LSJ 释义/近义词组→WordNet synset 排名；局部 hypernym-tree coverage 对比 LLM gloss-pair reranking | lexical alignment，不编译通用 FOL/Horn；双人按 0–3 分级评 top-5，第三人盲选代表 synset | 本轮已筛读 PDF；样本仅 16 组（作者称结果为趋势）；报告 pooled binary κ=0.520、ordinal weighted κ=0.611；结构方法整体更稳，LLM reranking 在多义组不稳定 | Phase 9/11 候选 baseline 的直接评测邻居。gold slice 应加入 taxonomy-aware ranking、definition matching、人类义项标签和多义分层。属 workshop，与主会论文分开。 |
| [Open English NameNet (McCrae, LDL @ LREC 2026)](https://aclanthology.org/2026.ldl-1.7/) | Wikidata named entities + WordNet–Wikipedia mappings→OEWN instance-hypernym hierarchy links | WordNet 资源扩展，但输入是实体/知识图谱对齐，不是 gloss 解析 | 本轮已筛读正式 PDF，构建并开放发布实体扩展资源 | 新近 OEWN hierarchy-extension 邻接先例；不能把扩展层级/自动加 hypernym link 本身声称为新贡献。属 workshop，与主会论文分开。 |
| [VSPO (Choi et al., AAAI 2026 KRR)](https://ojs.aaai.org/index.php/AAAI/article/view/38969) | class/property 自然语言定义 + OWL axioms→注入 missing/undefined/misused axiom 错配→生成 competency questions 定位 semantic pitfalls | 与“定义内容是否被逻辑结构忠实表达”直接相邻；不做 WordNet sense disambiguation，也不把释义编译成带论元/变量的 Horn 规则 | 全文已核：六个 ontology、1,563 样例、单次逻辑扰动；以参考 CQ 的 Sentence-BERT cosine≥0.7 评估，并含 leave-one-ontology-out；不产出独立规则证明证书 | 主会先例进一步排除“定义与逻辑运算符错配尚无人研究”的宽泛说法。其合成/相似度评测不等于 gloss-to-rule 人类 semantic-support gold。项目应借鉴控制 AND/OR、方向、删除约束、sense/source 的 mutation challenge，但由盲标者判定，不以语法/编译器通过代替语义审核。 |
| [Do LLMs Really Struggle at NL-FOL Translation? (Brunello et al., AAAI 2026)](https://ojs.aaai.org/index.php/AAAI/article/view/40258) | 自然语言句子→FOL；把 ontology extraction 与 fixed-signature logical translation 明确拆开 | 直接 LT 实验向模型提供 ontology，只测句子公式化；不含 WordNet 多义 sense linking 或 gloss 规则诱导 | Z3 等价判定；另有 connective/quantifier/negation 扰动的 most-similar 与 ranking 探针；作者对部分 DFOLIO 标签做定向错误审计 | 设计 oracle-vocabulary vs end-to-end 双轨评测，报告 WSD/signature grounding 与公式组合误差；不把给定 ontology 的 LT 分数解释成端到端定义编译性能。 |
| [A Logic-Based Approach to Hallucinations in Data-to-Text NLG (Calò et al., *SEM 2026)](https://aclanthology.org/2026.starsem-conference.3/) | 结构化输入/逻辑式→LLM 生成文本；按 input-output logical consequence 分类匹配、过强/过弱、独立、矛盾等情况 | 与“知识可验证/幻觉”动机相邻；强调逻辑后果类型和输入质量/歧义，不做 lexical sense 或 definition-rule construction | 人工参考标注含多标签歧义；酒店域 25 对 α=.73，逻辑域 75 对 α=.85；限定数据到文本对应关系，不判现实世界真值 | 借鉴方向性、多标签/unknown 及人审一致性报告；需另测 source-span→rule support、sense、proof replay。其分类结果不作为本项目 NLI 或规则忠实性基线。 |
| [LLMs as Knowledge Workers (Nirenburg et al., AAAI Spring Symposium Series 2026)](https://ojs.aaai.org/index.php/AAAI-SS/article/view/42583) | OntoAgent analyzer 遇到词汇/组合缺口→LLM 借助本体、词典及部分 meaning representation 提议条目/概念→检查概念与继承约束 | 约束验证与缺口触发采集高度相关；不是 WordNet sense/gloss 到有类型 AND/OR Horn 规则 | 全文实验为单篇船舶维护文本中的 6 个未知词、1 个欠明确复合词；结论处报告 9 个词典条目和 2 个本体概念通过自动约束验证。作者明确指出没有规模化准确率/效率评估，未决案例交由人审。AAAI Spring Symposium Series，不是 technical-track main conference | 作为架构/动机近邻而非同任务 baseline：其 ontology/lexicon 是 OntoAgent 自有世界模型，不生成逐 gloss-span 支持、逻辑证明证书或大规模 WordNet 编译结果。对本项目的启示是测量人工成本、跨域覆盖与约束验证之外的源语义忠实度；不能说人审已消除，也不能据此声称同一系统已实现。 |
| [HyperCoT (Yang et al., ACL 2026)](https://aclanthology.org/2026.acl-long.1172/) | 已构造的 n-ary KG hyperedges→深度敏感的多跳、role-aware Graph-CoT→LLM 补全缺失论元 | 对“沿结构路径读出中间证据”高度相关；输入是角色化事实超图而非定义 OR-of-AND Horn 子句 | JF17K/WikiPeople/FB-AUTO 上用 filtered MRR、Hits@K；完整系统报告 MRR .599/.451/.904，做组件消融、稀疏度、超边删除及路径深度分析。作者明确假设输入 hypergraph 已存在，不处理自动结构构建和提取噪声 | 借鉴路径数/深度/冗余路径敏感性分析；其可读 Graph-CoT 不是可重放逻辑证明，也不验证 WordNet gloss 来源支持。说明“超图上的多跳结构读出/可解释路径”已有 ACL 主会先例，不能泛称首创。 |
| [Cross-Granularity HGRAG (Wang et al., AAAI 2026)](https://ojs.aaai.org/index.php/AAAI/article/view/40623) | 实体节点 + passage 超边→加权超图 Laplacian 扩散实体相似度→结构邻域扩展 passages→LLM 多跳 QA | 是超图 diffusion/readout 和语义+结构融合的邻近方法；实体-段落关联不同于 Horn 逻辑方向/AND 条件 | HotpotQA/2Wiki/MuSiQue；报告平均 QA EM/F1 58.8/69.6，HippoRAG 2 为 55.0/65.0；MuSiQue 1,000 query 的 CPU 检索约快 6.3×，但任务不是 entailment/proof | 可作为“非逻辑结构读出”对照或启发，但必须另列为 retrieval baseline；不能把扩散分数当 proof/witness，也不能对逻辑 hyperedge 直接套无向 Laplacian 而丢掉 AND/OR 语义。 |
| [HyperGraphRAG (Luo et al., NeurIPS 2025)](https://proceedings.neurips.cc/paper_files/paper/2025/hash/df55ee6e59f8ac4a625219e11fe9ddba-Abstract-Conference.html) | 原文档→LLM 提取 n-ary relational facts / entity hyperedges→相似度检索与邻域扩展→与普通文本段融合后生成 | 说明“从文本自动构造超图并用于知识获取/RAG”已有主会工作；但其事实超边没有 Horn 规则的 AND antecedent/OR alternatives 语义 | NeurIPS 2025 主会全文；多域 RAG 评测含 answer/retrieval/generation 与 cost；作者把需更深组合推理列作后续任务 | 与本项目的自然语言来源获取动机相关，但不做 sense-linked WordNet gloss formalization、source-supported Horn rule 或 proof checker。需把“自动从文本建 hypergraph”与“定义逻辑化”明确分开。 |

## 2026-10-05 补充：自然语言证明与分解式蕴含

| 工作 | 输入→输出与评测 | 与本项目的边界 |
|---|---|---|
| [GFaiR (Sun et al., LREC-COLING 2024)](https://aclanthology.org/2024.lrec-main.1436/) | RuleTaker 自然语言事实/规则和配对 FOL 表示→resolution-refutation 风格步骤；按答案及每步 FOL 可推性计 Full Accuracy。Hard RuleTaker** EA/FA 92.2/92.2，RuleTaker-E 83.2/82.7。 | 证明了自然语言逻辑任务中可以评步骤级形式有效性，但不是 WordNet gloss→规则编译；不校验原 gloss 对形式化的 source-span 支持，也无本项目 source-linked 独立证书。有限搜索触顶可能被处理成无矛盾，需区分 `unknown` 与资源截断。 |
| [RDTE / TREEWISE (Weir et al., EMNLP 2024)](https://aclanthology.org/2024.emnlp-main.531/) | QA 分解 premise 按相关性、可接受性/部分事实性、冗余性与 sufficiency 做序数人审；双标一致 raw agreement .79、Krippendorff α .53；RDTE verifier 改善树完整性 judge 分数。 | 是分解推理人审协议近邻；任务允许上下文/常识，整体 sufficiency 不是 gloss 直接支持。报告 1,000 标注与 267+775=1,042 的文内计数不一致。只能启发 rubric，不作为 gloss/NLI gold。 |

两篇完整范围、结果和计数差异见[机器筛读日志](../sources/literature_screening_log_2026-10-05_logic_proof_and_decompositional_nli.json)。

## 2026-10-03 后续核查：新近 verifier 与 provenance 邻接工作

以下为本轮补充全文核查的六项工作；其中 GAVEL、ORACLE 是 ACL Findings（非 ACL main Long Papers），三项为 NeurIPS 2025 proceedings，Roundtrip Autoformalization 是 arXiv 预印本。完整查询和筛选状态见[补充日志](../sources/literature_screening_log_2026-10-03_late_supplement.json)。

| 工作 | 本轮核到的方法/结果 | 对本项目的边界与启示 |
|---|---|---|
| [GAVEL (Findings ACL 2026)](https://aclanthology.org/2026.findings-acl.1789/) | 事实核查主张绑定 sentence/table-cell ID 与引用片段，并做机械 ID/引文匹配验证；论文报告 FEVEROUS 41.80 vs 37.60、HOVER 49.60 vs 45.50。 | 精确引文定位不等于语义蕴含；可借鉴来源标识/片段校验字段，但仍需标注 gloss span 是否支持具体规则。 |
| [ORACLE (Findings ACL 2026)](https://aclanthology.org/2026.findings-acl.687/) | query-specific ontology→FOL→子问题计划；答案靠检索/LLM 执行，评测取三套 QA dev set 各 500 题。 | 是 ontology-to-logic 的邻接先例，不是释义规则生成或 theorem-prover 证书。 |
| [Faithful Autoformalization via Roundtrip Verification and Repair (arXiv:2604.25031)](https://arxiv.org/abs/2604.25031) | NL→形式化→回译→再形式化后用 SMT 对比，并由 LLM 诊断/修复；测试 150 条 Texas transportation 与 77 条 Texas Parks 规则。 | 重要的近邻，但目前是预印本。往返一致仍可能共享同一遗漏；roundtrip 可做辅助漂移诊断，不能取代 sense/source-span gold 与人工忠实性审查。 |
| [On Learning Verifiers (NeurIPS 2025)](https://proceedings.neurips.cc/paper_files/paper/2025/hash/e33b9cc87d3833f6769279e03011cdc1-Abstract-Conference.html) | 给出自然语言序列推理 verifier 的 PAC 学习分析；保证依赖包括 gold reasoner traces 等假设。 | 不是 gloss 项目；提醒必须明确 verifier 的监督来源、适用假设和保证，不能把 checker 通过笼统称为可信。 |
| [KG-RAG dataset pitfalls (NeurIPS 2025 Datasets and Benchmarks Track)](https://proceedings.neurips.cc/paper_files/paper/2025/hash/61a57ab030670598c4200b31100d254c-Abstract-Datasets_and_Benchmarks_Track.html) | 审计 16 个 KGQA 数据集、1,000+ QA pair，平均事实正确率报告为 57%；KGQAGen 用 SPARQL 结构校验生成样本。 | KG 内答案可查询不代表输入 gloss 到规则正确；借鉴对 benchmark 标签/事实正确性的独立审计。 |
| [Deliberation on Priors (NeurIPS 2025)](https://proceedings.neurips.cc/paper_files/paper/2025/hash/b33ad9d46ab2a23b6783d954121d26e3-Abstract-Conference.html) | 用 KG 结构和约束引导 LLM 推理路径，并加入 introspective verifier。 | 可作图结构先验/约束验证邻接基线；不是 sense-level definition support 或可独立重放的证明证书。 |
| [SAVeR (Yuan et al., ACL 2026)](https://aclanthology.org/2026.acl-long.1440/) | 对多样 agent belief trajectories 做局部 evidence/logical audit、错误定位和带 acceptance criteria 的最小修复；全文包含 auditor prompt/schema。 | ACL 主会 faithfulness 邻接方法，不处理 WordNet sense、定义 AST 或必要/充分方向规则；其可检查 acceptance criteria 不是独立规则证明或盲标 gloss-support gold。 | 六个 QA/reasoning benchmark；报告中间步骤 violation 与最终 EM/F1，并披露多轮 audit-repair 成本（HotpotQA 一配置下 8 calls/query）。启发项目记录局部错误、failing span、修复标准与覆盖/成本；不作 matched baseline，也不以 model auditor 替代人工裁决。 |
| [Grammars of Formal Uncertainty (Ganguly et al., NeurIPS 2025)](https://proceedings.neurips.cc/paper_files/paper/2025/hash/30ff6279fb18304d3eac481970157430-Abstract-Conference.html) | 多次采样 LLM 的 SMT-LIB 输出，诱导 task-specific PCFG，以结构不确定性预测形式化正确性/text-SMT 一致性，并做 selective verification。 | 全文核查；候选 AST/规则分歧与该方法有类比，但 SMT benchmark 结构不是 WordNet gloss 的 AND/OR Horn 超边，指标不可直接迁移。 | 四类 benchmark、5 个模型；UQ 分析对选定任务每 item/model 采样 100 次。部分组合报告高 AUROC，但依赖任务/模型且校准可差（文中一配置 ECE=0.4419），并带采样成本。 | 待检验的工程假设：用解析/规则集分歧、AND/OR 分支和 proof complexity 预测人工错误/abstention；在 sense-disjoint gold 上与 NLI-only、结构-only、融合校准器比较 risk–coverage/ECE。不能直接声称该特征在 WordNet 上有效。 |

## 从对照导出的实验问题

建议把投稿贡献写成可证伪的组合假设，而不是“首次”：

1. 给每条 WordNet sense 记录原始 gloss、词性、版本与 source span；对分解出的必要条件/定义备选项分别建模，保留 AND/OR，不先拍平成无向图或任意路径。
2. 将图结构对象与有类型、带方向的公式对象分开。每一逻辑规则都要说明头/体语义、变量绑定、闭包语义、编译器版本及从规则回到 gloss 的证据链。
3. 让 proof checker 对闭包/查询独立重放证书；若失败，返回 countermodel（限声明逻辑片段）或 unknown/unsupported，不能把缺边解释成反例。声明输出是单 witness、所有替代 derivation 的 why-provenance，还是 gloss span 对规则的语义支持；三者不可混称。
4. 在同一批 sense-disjoint 切分样本上分别测 sense linking、定义分解、公式保真、证明 soundness、NLI 语义分类、来源支持率、覆盖率/拒答率。报告每层错误，防止端到端分数掩盖定义语义错误。
5. 基线至少包括：WordNet 原生层级/词典链接；TaxoLLaMA 的 WordNet taxonomy 词汇关系预测路线；WordNetGraph 风格路径图；COLLIE-V/GWC 风格定义关系抽取；sememe-tree 方法（至少按 EMNLP 2025 SememeLP/ACL 2026 SememeLRM 可复现设置做 matched baseline）；直接 LLM/NLI（尤其是 [Greco et al., Findings of EMNLP 2024](https://aclanthology.org/2024.findings-emnlp.881/) 同样输入 WordNet gloss、判断方向性 verb lexical entailment 的设置，需在相同 senses/pairs/gold 上适配）；FOL prover pipeline；数学 autoformalization 的评测分离启示（Poiroux et al.），以及移除证据、sense、AND/OR 或证明校验的消融。若公开数据没有覆盖目标的完整 senses，不可把其测试结果外推至 11 万条，也需说明 reproduced baseline 与 paper-reported setting 的差别。
6. 按 AND/OR 分支数、依赖深度及 witness 展开节点数划分逻辑推理压力层级，另控制 gloss 长度、sense ambiguity 与可用规则覆盖；链式依赖和多分支汇合分别报告。该设计受 AAAI 2025 的规则归纳研究启发，但其合成规则复杂度分类与本项目的 witness 结构不等价，需用自己的标注样本验证。

## 当前实现与证据等级

- 当前 frozen bundle 已复算的是 110,425 个 head、154,206 个 clause 和 917,767 个 dependency literals 的结构闭包/witness；这不等于已经从 110,425 条自然语言 gloss 自动推导出忠实 FOL。
- 当前 Datalog checker 是有限正 Horn 的可执行原型；它证明“输入规则蕴含查询”，不证明原始定义支持输入规则。现有样例与单元测试不能替代 WordNet gold set。
- 文献对照截至目前主要根据官方摘要/元数据和少量已查看的正文片段。对照表中标为“待全文核对”的字段，在拿到全文/代码/附录前不用于定量优越性或严格 novelty claim。
- 论文中的规模、原语闭包及性能数字必须和当前 frozen bundle 的 SHA、graph semantic fingerprint、生成脚本逐项绑定。当前交付 bundle 与内部投稿稿有统计差异，未解决前不得合并不同版本的结论。

## ACL 2025 FOL 查询泛化：相邻评测先例

| 工作 | 全文核到的设置 | 对本项目的可迁移启示与边界 |
|---|---|---|
| [Enhancing Transformers for Generalizable First-Order Logical Entailment (Zheng et al., ACL 2025)](https://aclanthology.org/2025.acl-long.274/) | 55 种 EFO 查询类型（23 seen、32 compositionally unseen），FB15k、FB15k-237、NELL995；分开测未见知识答案与未见查询类型，MRR 为主要指标。TEGA 加入 logic-aware relative positional encoding 与 guided attention。EFO 包含正/负原子、AND/OR 与存在变量。 | 可借鉴把 sense/规则知识切分与 AND/OR 组合泛化分轴，再做交叉压力测试；论文不处理 WordNet/gloss、自然语言来源支持或证明证书，故不是 source fidelity/NLI 的匹配基线，KGQA 指标不可移植。当前项目尚无 gold set，也未复现其代码或数据。全文与核查边界见[筛选日志](../sources/literature_screening_log_2026-10-04_formal_nli.json)。 |

### ACL 2025 NLI 标签与人审协议近邻

| 工作 | 全文核到的设置 | 对本项目的可迁移启示与边界 |
|---|---|---|
| [Entailed Between the Lines / INLI (Havaldar et al., ACL 2025)](https://aclanthology.org/2025.acl-long.1552/) | 将 entailment 分为 explicit/implied，并与 neutral/contradiction 构成四类；10k premises、40k hypotheses，源自四个对话/社会情境数据集，Gemini-Pro 参与扩充。六位专家标注者讨论 16 条校准样例后，对 200 条样例三人标注；报告 Fleiss κ=.711、与构造标签多数一致率 .935。完整语料未全量人审。 | 可借鉴增加推理依据维度，避免把合理的世界知识/语用推断误作 gloss span 支持。其 implication 任务与 WordNet gloss source fidelity 不同，部分机器生成且领域不同；只作标注/压力切片设计参考，不作匹配 baseline 或 source-support gold。细节见[筛读日志](../sources/literature_screening_log_2026-10-04_formal_nli.json)。 |
| [Where Does Proof Search Spend Its Effort? (Saeki & Bekki, NALOMA 2026)](https://aclanthology.org/2026.naloma-1.7/) | wani 依赖类型 NLI prover 的结构化事件日志→proof-search tree、flame graph、rule statistics、failure analysis；tree 明确保留 AND 子目标与 OR 备选分支 | 证明搜索中的操作性分支树，不是 WordNet gloss 编译出的 sense-indexed、有来源 span 的 Horn 依赖超图 | JSeM 720/699 分别核对 336/336 与 1,680/1,680 个 goal 的配对、终止结果唯一性和深度不变量；单例还显示 ΣI 用时约 89%。作者说明尚无语料级评估、形式用户研究或跨 prover 移植 | 是 AND/OR 表示与 trace 重建核查的直接方法邻居；可借鉴结构不变量和失败分型。项目还须验证 gloss-span→rule 支持与义项正确性；该 profiler 的 search-tree fidelity 不证明本项目图的语义有效性。 |
| [From Execution to Exploration (Saeki & Bekki, BriGap 2026)](https://aclanthology.org/2026.brigap-1.1/) | 日语 CCG/DTS formal NLI 的 parse/type-check/proof-search 分支交互选择、缓存，并导出可由 wani 重载的精确 prover 查询；两题搜索例，四名熟悉 lightblue 的开发者参加用户研究。 | 交互式 proof-branch exploration 和可复现 prover-query handoff 的近邻；也限定“可视化分支/重放查询”宽泛贡献。 | workshop 工具论文，两个日语 NLI 例和 n=4 专家用户研究；解决 grammar-development usability/debugging，不做 gloss formalization 或 source-span support。 | source-only proof 需要更强证据：规则前提需逐条绑定已裁决 sense/gloss spans，且独立重放证明语义链；仅能重建 prover query 不够。详细筛读见[机器日志](../sources/literature_screening_log_2026-10-06_acl2026_proof_and_formal_nli.json)。 |
| [From Sentences to Proof Trees (Gupta, EACL SRW 2026)](https://aclanthology.org/2026.eacl-srw.71/) | 从预先给定的相关知识库事实生成 EntailmentBank 多步自然语言 entailment tree，报告结构和语义匹配分数。 | 多步 entailment tree 生成和解释评测近邻；限制“proof tree/结构化 trace”作为单独 novelty。 | EACL Student Research Workshop；主评估是已知相关叶节点的 no-distractor Task 1。作者承认中间步骤可无支持/逻辑不一致，且结构匹配指标会惩罚不同但语义可接受的树。 | 树形可读性不是语义支持证明。项目差异假设仍需独立 gloss-span gold、规则方向/AND-OR 标注和源记录绑定的证书回放，须用匹配实验验证。筛读详见[机器日志](../sources/literature_screening_log_2026-10-06_acl2026_proof_and_formal_nli.json)。 |
| [SLR: Automated Synthesis for Scalable Logical Reasoning (Helff et al., ACL 2026 Long Papers)](https://aclanthology.org/2026.acl-long.16/) | 任务规格→合成 definite Horn ground-truth rule、验证程序、背景事实和带符号标签的正/负样例；约 19k prompts / 20 级复杂度课程 | synthetic ILP 规则归纳与 symbolic judge；闭世界标签，不测 source gloss / WordNet sense / 证据 span 的语义忠实度 | 正式 PDF 报告按规则长度、背景采样和任务规模控制复杂度；错误分析显示语法正确不保证语义规则正确；作者将当前基准限于干净的单规则合成任务，噪声、歧义、多规则交互列为后续 | ACL 主会的强邻居，说明“Horn 规则 + 可执行验证 + 可控复杂度基准”已有先例。可借鉴为独立 checker stress suite/复杂度消融；不能替代人审 gloss-support gold，也不构成可直接比较的性能 baseline。 |
| [LLM-Based Typed Hyperresolution for Commonsense Reasoning with Knowledge Bases (Toroghi et al., ICLR 2025)](https://proceedings.iclr.cc/paper_files/paper/2025/file/67496dfa96afddab795530cc7c69b57a-Paper-Conference.pdf) | 自然语言 FOL clauses + 类型约束 + MNLI-tuned entailment scorer→任意元数 typed theory hyperresolution；可用 commonsense entailment 补齐不完整 KB，并暴露逐步 resolution | **极近的顶会先例**：已组合学习型 NLI entailment、typed hyperresolution 和 proof search；但谓词关系可由 LLM 常识许可/排序，不要求每条新关系有 WordNet gloss span 来源 | >32k 规则/1,000 个 2–7 步 query，多领域 KB；12k+ geography rules/500 query；不完整 KB 上报告 BART 0.97/0.95、RoBERTa 0.96/0.92 accuracy；typed ablation 将 reasoning steps 降至接近一半。reasoning-score 只人工检查 20 个答案正确的随机样例 | 排除“NLI + typed logic/hyperresolution/proof search”作为新颖点。可比差异假设必须收窄为 source-only、sense/version/span 锁定、人工裁决的方向支持和独立证书重放；严格 source_only 路径不得用模型 commonsense entailment 授权无来源前提。 |
| [Neural DTS: Integrating Hyperbolic Classifiers into Natural Language Inference Systems (Kobayashi et al., NALOMA 2026)](https://aclanthology.org/2026.naloma-1.2/) | WordNet synset hypernym edges→order/Poincaré/hyperbolic-cone embeddings→Japanese DTS/NLI 的 wani backward proof search 中动态加入 lexical IS-A axiom | **高度相关的 workshop 先例**：学习型 WordNet hierarchy 已进入逻辑 prover；与本项目区别在词汇 taxonomy axiom 注入，不是从 gloss spans 编译方向性多元规则 | 10D/90% edges 的独立 oracle F1 92.85；集成仅测 20 条日语 upward-monotonicity PoC（Yes F1 .842、macro F1 .850）；另有 100 entailment/180 neutral 的 MED pair 测试，OOV 从准确率分母排除，entailment accuracy 62.12%、neutral 96.64% | Workshop 工作而非顶会主会。排除“WordNet 层级学习用于逻辑 NLI/证明搜索”作为新颖点；只作近邻和对照设计，不移用其任务分数。仍待验证的差异是逐 gloss source-span support、保留 AND/OR 的有类型方向规则与 source-only replay。详见[筛读日志](../sources/literature_screening_log_2026-10-05_neural_dts.json)。 |


### 长上下文证据检索近邻

[EACL 2026 Logic Haystacks](https://aclanthology.org/2026.eacl-short.3/) 在简化英语/FOL 长前提中检索联合矛盾证据，用 Vampire 保证合并前提一致，并通过逐条删除筛出必要充分的唯一证据组。它与本项目未来的候选释义/规则检索压力测试在困难干扰项下定位证据上相邻；也意味着不能泛称证明引导的证据归因或非干扰干扰项为新贡献。其任务只判断合成前提对假设的矛盾，不校验 WordNet sense、定义方向或 gloss-span 蕴含，因此不是匹配 baseline。官方全文筛读见[日志](../sources/literature_screening_log_2026-10-06_logic_haystacks.json)。


### 多证据组合选择与评估邻居

十三篇优先全文核读工作共同收窄了方法与新颖性边界。最近的结构近邻有 [EnoTab](https://aclanthology.org/2026.acl-long.1102/)（显式 AND/OR Evidence Tree、可观察表格 pruning 与 rollback）、[LCDS](https://aclanthology.org/2025.acl-demo.28/)（医疗域逻辑约束、来源映射与专家复核）、[POLITICITE / MULTIATTR](https://aclanthology.org/2024.naacl-long.216/)（人工多源 statement-support 片段/分级标注）和 [CORRECT](https://aclanthology.org/2025.naacl-long.154/)（evidence/context/reference 三层图）。这些都不是 WordNet gloss-to-Horn 证明，但排除了将 AND/OR 证据树、来源归因、多源支持标注或证据图泛称为新贡献。其余九篇涵盖复杂主张的部分覆盖、RI²VER 跨段复核、长上下文 arbitrary-span attribution（SUnsET）、最小充分证据排序、PROBE 分阶段检测、RIGOURATE 分级支持、LAB 的 attribution/abstention、EAPO 过程奖励及 ARK answer-sufficiency retrieval。十三篇均未标注 WordNet gloss 对 sense/version-bound direction-specific Horn rule 的支持或独立 proof replay。逐篇方法与局限见[增量筛读日志](../sources/literature_screening_log_2026-10-06_acl_expanded_delta.json)。

ACL 2025 ETS 的 MCTS 树路径优化 QA reader reward，COLING 2025 Counting-Stars 测量分散的多证据搜集和含错误插入句的联合推理，TACL 2026 Ev2R 摘要提出组合 evidence-reference alignment 与 verdict support。前两者提供候选组合搜索、上下文位置/长度分层的实验设计参考；Ev2R 提醒证据匹配与最终 verdict 支持应联合观测。本项目的定义规则需保留 AND/OR 与 source span，但这些工作均未验证 WordNet gloss→Horn semantic support；ETS reader reward、Counting-Stars 合成 counting score、Ev2R AFC 指标均非匹配 baseline。Ev2R 本轮仅摘要级筛读。详见[机器筛读日志](../sources/literature_screening_log_2026-10-06_evidence_retrieval_supplement.json)。

### ACL Anthology 2026 formalization slice: targeted PDF review

The table records targeted reading of methods, evaluation and limitations sections in the official PDFs. “Targeted sections” does not mean every page/appendix was exhaustively reviewed. Venue tracks are shown because ACL main conference, Findings, and shared-task/workshop papers have different evidential status.

| Work | Task and evidence checked | Relation to this project | Limit / non-comparability |
|---|---|---|---|
| [Extracting First Order Logic formulas from graphical semantic representations (de Vergnette et al., DMR 2026)](https://aclanthology.org/2026.dmr-1.9/) | Existing Yarn graph annotations are interpreted through scope constraints into a set of modal-temporal FOL formulas; targeted sections explain underspecification and dynamic quantification. | A graph-semantic-representation→FOL mapping precedent; use it to distinguish annotation-to-logic from raw-text parsing. | No raw utterance parser, WordNet sense or gloss-span gold; theoretical examples rather than an automatic gloss compiler benchmark; selected Yarn features only. DMR workshop. |
| [Neural Wani (Miyagawa et al., BriGap-3 2026)](https://aclanthology.org/2026.brigap-1.2/) | Neural rule-order prediction guides backward DTT proof search while retaining the symbolic prover. A 50-problem held-out NLI sample used depth limit 9 and returned UNKNOWN on timeout; the authors report up to 1.41× average speedup. | A proof-search cost and explicit timeout/UNKNOWN neighbor. | Does not change proof validity or evaluate gloss formalization. Training uses type-checking data as proxy for scarce NLI proof trajectories; authors identify distribution shift. BriGap workshop. |
| [ARI-KBQA (Gao et al., ACL 2026 Long Papers)](https://aclanthology.org/2026.acl-long.1479/) | Hop-wise query-LF generation followed by KB path-feasibility verification and relation replacement; reports WQSP, CWQ, FreebaseQA and LC-QuAD results, LF non-executable rates, ablations and efficiency. | Close generate→execute→refine precedent for structured logical forms. | Executability and answer quality are judged against the KB; it does not ask whether an original text span entails a definition rule. |
| [YNU-NLP at SemEval-2026 Task 11](https://aclanthology.org/2026.semeval-1.126/) | Qwen2.5-14B parses arguments to JSON/FOL, checks S–M–P term linkage, repairs with Try-Fix, then uses Z3 with a neural fallback. Official task results include accuracy, content-effect and premise F1; ablations separate solver/reflexion components. | Direct NLI/formal-verification pipeline neighbor; useful for parser coverage, fallback and prover-only reporting. | Standard syllogism task, not WordNet senses or Horn rules. Since neural fallback is used on parser/solver failure, aggregate task score is not pure Z3 accuracy. SemEval shared task. |
| [ToolGate (Findings ACL 2026)](https://aclanthology.org/2026.findings-acl.470/) | Hoare-style pre/postconditions gate tool execution and state updates; evaluates ToolBench and MCP-Universe and removes 5%/10% of contract constraints in robustness analysis. | Shows runtime checks can certify execution relative to supplied contracts. | The paper states some ToolBench response schemas are LLM-assisted with expert examples rather than ground-truth specifications; verification is conditional on contract fidelity. |
| [LeVer (Zhang et al., ACL 2026 Long Papers)](https://aclanthology.org/2026.acl-long.1836/) | Smart-contract generation is coupled with Lean autoformalization, proof checking, adversarial attack and repair. It reports expert and execution cross-check pass rates on 300 sampled generations. | Strong cross-domain formal-verifier precedent and a direct illustration of translation-fidelity as a separate metric. | The authors state Lean guarantees concern the translated representation and do not formally establish Solidity-to-Lean semantic preservation; not a gloss task. |
| [PDDLego+ (Gong et al., Findings ACL 2026)](https://aclanthology.org/2026.findings-acl.620/) | LLM formalizes partial environment/goal descriptions into PDDL, then grows or repairs the model from planner/simulator feedback. | Iterative formalization and execution feedback are established design patterns. | Latent incorrect action preconditions/effects can survive if trials do not expose them; simulator success is not proof that a representation is source-faithful. |
| [APF (Li et al., Findings ACL 2026)](https://aclanthology.org/2026.findings-acl.102/) | Engineering requirements become optimization constraints/objectives and executable code; LLM-generated test-instance rankings guide data selection, with antenna simulation as downstream evaluation. The paper reports 7,879 retained samples and a human-ranking check over 30 requirement sets × 15 shared instances (judge–human mean Spearman .80–.83). | Established cross-domain precedent for natural-language requirements→executable mathematical models, external formalization assessment, and downstream utility; broad “first” claims in these areas are not supportable. | Reference rankings are primarily LLM-generated; the small human check is not formula-level semantic gold. The domain is specialized industrial design; no WordNet senses, gloss spans, typed Horn/AND-OR support, or source-bound witness replay. Metrics are not comparable to this project. See the [2026-10-06 prior screen](../sources/literature_screening_log_2026-10-06_acl_formalization_2026.json) and Phase273 supplemental review. |
| [IRAP (Wang & Chen, Findings ACL 2026)](https://aclanthology.org/2026.findings-acl.2042/) | Interactive, retrieval-augmented preference elicitation turns software performance requirements into piecewise satisfaction functions; compares with 10 methods on four datasets. | Shows ambiguity may require stakeholder clarification before formalization. | Piecewise preference functions are domain-specific and do not provide logical entailment, proof artifacts or lexical sense grounding. |
| [AICOE-Tredence at SemEval-2026 Task 11](https://aclanthology.org/2026.semeval-1.229/) | Natural-language arguments are converted to Aristotelian mood/figure forms; official task test and ablation results target content-bias resistance. | A formal-validity/content-plausibility separation precedent. | Assumes exactly two premises plus conclusion; authors identify multi-premise/sorites as future work. Does not establish gloss rule support. SemEval shared task. |

Across these papers, executable or kernel-checkable output never by itself validates the upstream natural-language translation. The most direct methodological consequence is to report separately: source/sense identity, span-to-rule support, formal parse/translation quality, solver outcome (including fallback and resource limits), and proof-certificate replay. These ten works are cross-domain boundary evidence, not matched WordNet baselines or proof of novelty. Per-paper screening depth and notes are in the [structured screening log](../sources/literature_screening_log_2026-10-06_acl_formalization_2026.json).

### ICLR 2026：形式定义检索与语义形式化评估

| Work | Task and evidence checked | Relation to this project | Limit / non-comparability |
|---|---|---|---|
| [CRAMF (Lu et al., ICLR 2026)](https://proceedings.iclr.cc/paper_files/paper/2026/hash/fd83f4e0dcaf1c64ea15bbb1695bb40f-Abstract-Conference.html) | 从 Mathlib4 构建覆盖 26K+ 形式定义与 1K+ 概念的知识库，以概念解析、符号匹配、向量检索和 reranking 取回 Lean 定义，作为数学 autoformalizer 的上下文。 | 明确建立了“自然语言定义索引/检索形式定义→形式生成”的跨域先例；检索增强本身不能单列为本项目创新。 | 大规模形式化正确度以 Lean 编译及模型回译后的 LLM 一致性判断为主；不处理词典 sense、WordNet gloss claim 或逐跨度来源支持，也不是 matched baseline。 |
| [Mathesis (Yu et al., ICLR 2026)](https://proceedings.iclr.cc/paper_files/paper/2026/hash/93d5797656d3e70dca7535160a1458f3-Abstract-Conference.html) | 数学自然语言→Lean 4 formal statement→prover；LeanScorer 分解 premise/conclusion、赋 Match/Minor/Major 三档，再以 Sugeno fuzzy integral 聚合。 | 为语义子任务分解、形式检查、语义评估和 proof success 分轨提供近期主会实例。 | LeanScorer 的 0.92 F1 在 98 项、三位专家的 Gaokao-Formal 子集上核验；它校准的是数学形式化一致性，不是 WordNet gloss-span source support。proof/type-check 仍以形式输入为对象。 |

逐篇方法、样本与评测限制见[结构化全文筛读日志](../sources/literature_screening_log_2026-10-06_iclr26_autoformalization_neighbors.json)。该两篇补充了 ICLR 2026 的定向范围，不改变系统综述/新颖性审计尚未完成的判断。

## 最近邻论文工件状态

对三项外部基线/资源做了官方材料与作者仓库的定向检查：Greco et al. (Findings EMNLP 2024) 的正式 ACL 页面只列论文 PDF，未定位论文代码、测试输出或随附数据；AI-WordNet 指向 dataset-only 仓库且未声明许可证；LREC 2026 作者仓库可见 CSV/RDF 与提示词，但无生成代码或声明许可证，官方会议页面无补充材料。尚未复制或使用外部数据。LREC 集可在许可审查后用于受限的 adjective relation 外部核验，但不能替代项目的 gloss-span 规则支持标注。具体仓库快照和证据见[工件审计](../sources/literature_artifact_availability_2026-10-06.json)。

## ACL 2026：规则依赖图与动态规则证据

| Work | Task and evidence checked | Relation to this project | Limit / non-comparability |
|---|---|---|---|
| [RGCWM (Li et al., ACL 2026)](https://aclanthology.org/2026.acl-long.741/) | 指南规则对被分类为 support/prerequisite/conflict/exclusion，形成固定 pairwise graph；LLM 估计当前候选回答对规则适用/满足的连续 evidence state，再执行 rollout、打分与图传播。官方全文包含 GuideBench、双 backbone、强基线、删边/状态噪声、消融和成本分析。 | 强化了“显式规则依赖图、规则状态、关系传播和结构化推理”已有近期主会先例。该论文也说明图质量和 evidence-state 噪声须分别做压力分析。 | 模型诱导权重和连续状态是近似估计，不是语义 gold、逻辑 entailment 或 proof certificate；pairwise graph 不等于保存完整 AND/OR Horn hyperedge/witness alternatives。没有 sense/release-linked WordNet gloss spans 或 source-only proof replay。GuideBench 分数不能与项目 lexical target 直接比较；一类数据未公开。 |

全文定向范围、事实与限制见Phase 45 报告及[结构化筛读日志](../sources/literature_screening_log_2026-10-07_acl_rule_graph_neighbor.json)。该筛读不是 ACL 2026 proceedings 穷尽检查，也不证明剩余窄任务新颖。
## 2026-10-06：2025 年规则遵循与自动形式化近邻

| Work | Task and evidence checked | Relation to this project | Limit / non-comparability |
|---|---|---|---|
| [RuleArena (ACL 2025)](https://aclanthology.org/2025.acl-long.27/) | 95 条真实 airline/NBA/tax 政策、816 道题；分别评价 rule selection/relevance、rule application correctness 与 answer accuracy。 | 直接提示要区分规则检索/选择与规则正确使用，也可借鉴逐项错误分解。 | 不从 gloss 诱导词汇规则，不做 sense/span binding 或 proof replay；rule-use extraction 部分依赖 GPT-4o 解析回答。不是 WordNet matched baseline。 |
| [LTRAG (Findings ACL 2025)](https://aclanthology.org/2025.findings-acl.126/) | 检索 thought-guided examples，连接 translator、solver、fixer；在 FOLIO 与 AR-LSAT 对 Logic-LM/LINC 作实验。FOLIO 评测使用 182 个过滤后样例；AR-LSAT 使用 231 个 dev 样例作 test。 | RAG + autoformalization + symbolic solver + refinement 的近邻，已排除这一组合本身作为充分新颖点。 | 通用逻辑题而非 glossary/source-span gold；AR-LSAT split 口径须如实注明；fixer 对复杂 semantic error 的修复仍有限。不能直接移植指标。 |
| [MASA (EMNLP 2025 System Demonstrations)](https://aclanthology.org/2025.emnlp-demos.44/) | 多 agent 组合 autoformalization、critique/refinement 和 theorem prover；以 miniF2F Lean4 演示，区分 alignment faithfulness 和 formalization correctness。 | 数学定义形式化系统与分层评估先例；启发显式区分语义贴合与形式可检查。 | 语义指标依赖 GPT-4.1-mini 的高层评判，作者承认需更细准则；非词典 sense/gloss-span 支持评价。 |
| [ReLean / NL2Lean (EMNLP 2025)](https://aclanthology.org/2025.emnlp-main.1586/) | PPO 训练 LLaMA-3-8B 翻译 Lean 4，组合 semantic/tactic/global alignment 与 compile rewards；在 Lean Workbook、ProofNet 做自动及人工评估。 | 强化“可编译”与“语义正确”是不同结果；人审评价是 translation fidelity 的直接先例。 | 数学 Lean 形式化，不处理 WordNet 义项消歧或 gloss evidence spans；其准确率不能与项目候选任务直接对比。 |

逐篇方法、split、结果、局限和筛读范围见[结构化日志](../sources/literature_screening_log_2026-10-06_acl_2025_formalization_rule_neighbors.json)。四篇均为 cross-domain prior art，不是共同 sense-disjoint gold 上的匹配性能比较；相关工作结论仍是定向筛读，不是系统综述或 novelty proof。

## 2026-10-06 Phase 32：2024 自然语言形式化、解释证明与逻辑数据集

| Work | Task and evidence checked | Relation to this project | Limit / non-comparability |
|---|---|---|---|
| [Consistent Autoformalization (Zhang et al., EMNLP 2024)](https://aclanthology.org/2024.emnlp-main.233/) | 从 IsarMathLib 构建 2,744 项 MathLibForm，90/10 随机划分；使用检索示例、去噪与 Isabelle syntax-error feedback。 | 数学定义库构建、检索式示例与 prover feedback 都是正式发表的邻接路线。 | 语法通过率和公式相似度是 correctness proxy；论文承认自然语言项可能过泛且复杂表达的语法通过仍困难。它不提供 sense-linked gloss-span 支持标注。 |
| [Explanation-Refiner (Quan et al., EMNLP 2024)](https://aclanthology.org/2024.emnlp-main.172/) | LLM 产生/形式化 NLI 解释、推理策略与 Isabelle/HOL proof；失败后迭代修订，在 e-SNLI、QASC、WorldTree 评价。 | 直接排除“LLM 形式化解释 + theorem prover 校验/反馈”作为充分创新主张。 | checker 针对编码后的前提、解释和证明步骤；不独立判断其对原始句子的忠实度。论文也要求进一步检验 solver guarantee 的正确性/完备性。 |
| [FOLIO (EMNLP 2024)](https://aclanthology.org/2024.emnlp-main.1229/)；[P-FOLIO (Findings EMNLP 2024)](https://aclanthology.org/2024.findings-emnlp.966/) | 逻辑复杂 NL/FOL 数据；P-FOLIO 增加 0–20 步人工自然语言推理链与单步推理规则、pass@k 评估。 | 可借鉴形式映射、推理链及答案三层标注/评价；其专家标注高质量但规模受资源制约。 | 基准输入是故事前提/结论，不是 WordNet 定义；逻辑正确性不等于 lexical sense 或 gloss source-span 支持。 |
| [TabVer (Aly & Vlachos, TACL 2024)](https://aclanthology.org/2024.tacl-1.89/) | 分解表格 claim，将 claim 与证据 span 对齐并执行确定性自然逻辑 proof，支持相关算术表达。 | 是 claim decomposition、span-aligned evidence 与可执行 proof 的证据核验先例。 | 证据来自表格；自然逻辑有 FOL 表达力缺口，部分多跳 span 推导未被 proof 完整展开，不等价于 gloss-derived Horn provenance。 |
| [Formal Languages for KBQA (Liu et al., Findings ACL 2024)](https://aclanthology.org/2024.findings-acl.45/) | 探查 LLM 对多种形式语言的理解、生成及格式敏感性；few-shot 下正确 logical-form generation 仍困难。 | 提示需单独量化语言到逻辑表达生成错误与目标表示选择。 | KBQA 查询生成不包含词典 sense disambiguation 或 definition source-support。 |

筛读范围、逐条纳排、摘要和六篇 PDF 定向章节范围见[Phase 32 结构化日志](../sources/literature_screening_log_2026-10-06_acl_2024_definition_to_formal_logic_full_screen.json)。该 2024 词族 28/28 条现有精确 URL 日志匹配；它是固定 ACL 词族的有限筛查，不是全文综述、跨库系统检索或新颖性证明。

## 2026-10-06 Phase 30：同词族形式语义与结构生成近邻

| Work | Task and evidence checked | Relation to this project | Limit / non-comparability |
|---|---|---|---|
| [QuaSAR (Ranaldi et al., ACL 2025)](https://aclanthology.org/2025.acl-long.843/) | 在 CoT 中只抽取相关变量/谓词形成准符号解释；本轮定向核对方法、实验和错误分析。 | 部分自然语言形式化与推理的直接方法邻居，说明“只形式化推理所需内容”已有主会先例。 | 未绑定 lexical sense 与 gloss spans，也不测 source-only Horn-rule support；其准确率不是本项目匹配 baseline。 |
| [Natural Language Inference with CCG Parser and Automated Theorem Prover for DTS (Tomita et al., BriGap-2 2025)](https://aclanthology.org/2025.brigap-1.1/) | CCG/DTS 语义分析后用 DTT prover，在 JSeM Verbs 的 36 个问题上报告 24 个正确，并分析解析、知识与 proof-search 错误。 | 形式语义、自然语言蕴含和自动证明器组合的 workshop 先例；也说明 parser 与 proof search 的错误需分开。 | 日语小型 NLI 子集，带有有限 proof-search 深度/时间限制；没有 WordNet gloss 或 source-span 规则标签。 |
| [Neurosymbolic AI for Natural Language Inference in French (Skandalis et al., IWCS 2025)](https://aclanthology.org/2025.iwcs-main.21/) | LLM 辅助类型逻辑语义解析生成 lambda terms，再交由 LangPro；在 SICK-FR 上评价。本轮核对了结果和结论/限制章节。 | 多语自然逻辑 NLI + theorem prover 先例，压缩“LLM/parser + prover”宽泛主张。 | 句对分类不是词典定义编译；作者把法语 lexical KB 作为未来增强方向，没有 gloss-span gold。 |
| [Philosophising Lexical Meaning as an OntoLex-Lemon Extension (Zamborlini et al., OntoLex 2025)](https://aclanthology.org/2025.ontolex-1.6/) | 提案表示 lexical sense 的 textual/formal definitions、解释关系和概念来源；正文以两个概念案例展示模型。 | 直接的词义定义表达与 provenance/context 建模邻居，要求将“形式表示词义定义”从宽泛 novelty claim 中移除。 | 是概念扩展与案例展示，不是 WordNet gloss 自动编译或 benchmark；作者指出实践实现与部分 competency questions 尚待后续研究。 |

其余 33 条新增记录只完成题名/摘要筛查。37 条决策、摘要原文和四篇正文范围见[结构化日志](../sources/literature_screening_log_2026-10-06_acl_2025_definition_to_formal_logic_full_screen.json)；52 条词族的精确 URL 匹配状态与 ACL v3 全局计数见[phase30 对账快照](../sources/acl_screening_reconciliation_2026-10-06_phase30.json)。这些筛查不构成系统综述、召回估计、匹配性能比较或新颖性证明。


## 2026-10-06 Phase 31：claim tree、证据组和验证器近邻

| Work | Task and evidence checked | Relation to this project | Limit / non-comparability |
|---|---|---|---|
| [HalluTree (2025)](https://aclanthology.org/2025.newsum-main.9/) | 把摘要拆成 extractive/inferential/unverifiable 子 claim；前者走 NLI，后者以来源/背景事实和 natural program 推理，组织为 claim tree。 | 最直接的 claim→证据/推理→树式聚合先例；claim tree 和解释链本身不是新颖点。 | natural program 由 LLM 检查，不是独立符号证明；可用背景知识；输出二元摘要事实判定，不是 WordNet gloss 规则支持。 |
| [PGR (Findings EMNLP 2025)](https://aclanthology.org/2025.findings-emnlp.293/) | LLM 生成 MATCH/SEARCH/VERIFY 图推理程序，在 DBpedia 上核验 FactKG claim；分析 execution/entity-matching 错误。 | 显式、可执行的图推理轨迹先例。 | KG 三元组事实核查，不抽取 gloss 规则或标注 gloss spans；报告分数不是项目 baseline。 |
| [Minimal Evidence Groups (TrustNLP 2025)](https://aclanthology.org/2025.trustnlp-main.8/) | 将最小充分证据组识别建模为 set-cover-like 组合问题，在 WiCE/SciFact 及下游 claim generation 上评估。 | 多来源互补证据共同支持和最小充分子集邻居。 | 暂不处理 contradiction；人工参考 MEG 不穷尽，作者不将其视为绝对 gold；web passages 与单一定义 spans 不同。 |
| [SC-Energy (ACL 2025)](https://aclanthology.org/2025.acl-long.1599/) | 对整组自然语言句子/QA 判定一致性并定位冲突项。 | 集合层逻辑一致性与多陈述组合邻接。 | 不是方向规则的来源蕴含评估；数据由规则和 LLM 转换生成，域泛化未解决。 |
| [Local Look-Ahead (Findings ACL 2025)](https://aclanthology.org/2025.findings-acl.825/) | 用 Lean 在每个 proof state/tactic 给 theorem prover 中间反馈。 | 证明步骤级 verifier feedback 先例。 | 已给定形式目标，不验证形式化是否忠于自然语言来源。 |
| [SemQA (FEVER 2025)](https://aclanthology.org/2025.fever-1.14/) | 合并生成问题与参考问题的 embedding 相似度、答案双向 NLI，并与人工判断比较。 | claim-conditioned evidence adequacy metric 邻居。 | 对照有限 reference QA，不标 source spans、不验证 source-only proof。 |

逐项边界见[筛读日志](../sources/literature_screening_log_2026-10-06_acl_2025_nli_logic_proof_full_screen.json)，候选范围与数字见[phase31 对账](../sources/acl_screening_reconciliation_2026-10-06_phase31.json)。该词族 67 条有日志匹配不等于 67 篇全文读完；此处仍是定向 scoping。
## ICML 2026：跨会场的宽泛方法邻居（摘要级）

| Work | Abstract-level evidence checked | Relation to this project | Limit / non-comparability |
|---|---|---|---|
| [Geometry of Reason (ICML 2026)](https://proceedings.mlr.press/v306/noel26a.html) | 把 attention 矩阵当作 token 加权图，计算谱特征以识别数学推理质量；摘要报告七个模型的评估及 proof-search reranking。 | 说明 graph/spectral analysis 已用于推理质量验证，相关工作中应避免把“用图分析推理”写成宽泛新颖点。 | 模型内部 token 图，不是固定 WordNet sense/gloss 依赖超图；无 gloss spans、规则语义支持 gold 或 source-only proof replay。仅摘要筛查。 |
| [Propose, Solve, Verify (ICML 2026)](https://proceedings.mlr.press/v306/wilf26a.html) | 在 verified code generation 中用形式验证信号训练 proposer 与 solver；摘要报告三个 benchmark 上最高 9.6x pass@1。 | 形式验证可作为学习反馈信号已有近期代码领域先例。 | Verus/code generation 与词典释义支持判断任务不同；摘要结果不是本项目 baseline。仅摘要筛查。 |

结构化筛查范围见[机器日志](../sources/literature_screening_log_2026-10-06_icml2026_verification_supplement.json)。该补查不纳入冻结 ACL v3 候选框，也不构成系统综述或新颖性证明。
## NeurIPS 2025：模型推理图与 KG 先验验证

| Work | Evidence checked | Relation to this project | Limit / non-comparability |
|---|---|---|---|
| [Topology of Reasoning](https://proceedings.neurips.cc/paper_files/paper/2025/hash/147521db4d049c75cf18d9ff96bf68f5-Abstract-Conference.html) | 定向核读官方 PDF 的 graph extraction、metric、robustness 与 limitations：从 reasoning-step hidden states 经 K-means 构造状态转移图，分析 cycles/diameter/small-world。 | 近期主会已用模型内部图拓扑分析 reasoning，压缩“图拓扑刻画推理”宽泛说法；也提示静态结构指标须与语义任务证据区分。 | 节点来自模型隐藏态 cluster、边来自连续访问，不是 AND/OR Horn premise dependencies 或 witness proof DAG；没有 gloss/span support gold。 |
| [Deliberation on Priors](https://proceedings.neurips.cc/paper_files/paper/2025/hash/b33ad9d46ab2a23b6783d954121d26e3-Abstract-Conference.html) | 定向核读官方 PDF 的框架、KGQA 实验和限制：蒸馏 relation-path prior、做 constraint checking 与 backtracking；作者指出垂直域约束定义依赖人工介入。 | 对项目的资源先验、约束/检查、失败回退分层有参考价值。 | 既有 KG 路径约束不等于自然语言 gloss 的 source support 或独立逻辑 proof replay；WebQSP/CWQ/MetaQA 结果不是词义关系 baseline。 |

逐篇核读范围见[结构化日志](../sources/literature_screening_log_2026-10-06_neurips2025_graph_verification.json)。这两项是跨会场定向补查，不是系统综述或新颖性证明。

## COLM 2026：组合证据核验、逻辑保持压力测试与语义 grounding

| Work | Task and evidence checked | Relation to this project | Limit / non-comparability |
|---|---|---|---|
| [When Verification Fails (Liu et al., COLM 2026)](https://arxiv.org/html/2604.10990) | 组合式 scientific claim verification；通过保留显著约束、扰动非显著约束来构造 hard negatives，在临床文本/表格/图表上比较普通负例与 compositionally infeasible claims，并测试中间结构证据和 OWA/CWA 提示。 | 最接近“一个规则的主要部分有支持、另一必需 conjunct 需要组合证据且可被反驳”的评测思想；应纳入逐 clause source support 与 composition-sensitive false acceptance 分析。 | 不是词典 sense/gloss-span 标注或 AND/OR Horn 证明 DAG；trace judge 含 LLM rubric；论文结果未经本项目复现，不是 matched baseline。 |
| [LPDS (Mondorf et al., COLM 2026)](https://arxiv.org/html/2605.15393) | 在符号模板问题的 logic-preserving variation 空间估计难度并以 beam search 找出会暴露模型失败的变体；与随机抽样对比。 | 为保持逻辑不变的稳健性/对抗切片提供方法参考；未来可用于审计对释义表面变化的敏感性。 | 数学/结构任务而非 lexical sense 或来源蕴含；释义改写须先独立验证语义不变。文中指出从符号模板迁移至其他变体空间仍待研究。 |
| [Neuro-symbolic PRM (Zi et al., COLM 2026)](https://arxiv.org/html/2608.26329) | 结构化科学推理中先用确定性操作 verifier 筛除不合法候选，再由 PRM 评价语境 grounding；构造 verifier-pass 的语义 hard negatives，并记录操作覆盖/回退。 | 强化将 AST/格式、可执行/类型正确、语义来源支持和 proof replay 分开测量的设计；提醒报告 verifier coverage 与 fallback。 | 特定量化 STEM 操作库，不验证 WordNet gloss entailment。94.2% 覆盖是论文自身的操作库/验证集口径，未知操作会回退到神经 PRM，不等价于证明保障。非项目实验。 |

本轮以 [COLM 官方 accepted-papers 页](https://colm.cc/Conferences/2026/AcceptedPapers)确认录用状态，以作者公开全文筛读方法、实验和限制；会议正在进行，正式 proceedings/最终版本仍可后续复核。三篇均为定向筛读，不覆盖整个 COLM 录用集。逐篇范围、证据层级与限制见[结构化日志](../sources/literature_screening_log_2026-10-07_colm2026_compositional_verification.json)及Phase 55 深度报告。这些工作排除宽泛的组合核验、逻辑保持 stress testing、结构化 trace 和“符号检查 + learned grounding”作为单独 novelty；它们不证明更窄的 sense-linked gloss-span→Horn support 假设已有效或新颖。

## IJCAI 2026：逻辑规则归纳与文本蕴含证明路由

| Work | Task and evidence checked | Relation to this project | Limit / non-comparability |
|---|---|---|---|
| [Neuro-Symbolic Logical Reasoning with Textual Entailment](https://www.ijcai.org/proceedings/2026/989) | 官方 4 页论文定向核读 VANESSA 处理流程、ProofWriter/ProntoQA/FOLIO/LogicBench 子集与报告的误差特征：浅解析、textual entailment 对齐措辞、符号证明，并输出 proof tree。 | 直接先例表明“用 textual entailment 将自然语言短语桥接到符号 prover，并给证明树”本身不是新贡献。系统表现还把 high precision / low recall / unknown coverage 的权衡带入未来评估设计。 | 前提是自包含规则/事实与 QA 结论，不是词义版本绑定的 gloss spans；NLI 步骤仍是可错环节，证明树只在解析与 entailment 对齐正确时支持答案；不提供 gloss→有向 Horn 的人工支持 gold。Demo Track 论文结果不是项目 baseline。 |
| [A Foundation Model for Zero-Shot Logical Rule Induction](https://www.ijcai.org/proceedings/2026/445) | 官方 9 页论文定向核读表示、合成训练、UCI 迁移、逻辑规则恢复、噪声/干扰特征实验与消融。NRI 面向布尔表格数据输出 DNF；14 个 UCI 数据集均值 69.7%，对照为逐数据集训练 EBM 82.7%。 | 近期主会先例覆盖可解释 DNF、AND/OR 结构、zero-shot rule induction 与按规则等价/预测效能分轴报告；宽泛的“学习 AND/OR 规则”不能单独主张新颖性。 | 命题变量对应表格特征，不对应 WordNet sense、词典定义或 source span；预测分类准确率不等于规则被自然语言证据蕴含，也不是 gloss-to-Horn matched baseline。 |

逐篇筛查深度、查询和不外推限制见[结构化 IJCAI 2026 记录](../sources/literature_screening_log_2026-10-06_ijcai2026_logic_neighbors.json)。这是两篇定向邻近筛查，不覆盖 IJCAI 全集，也不证明更窄的 gloss-source-support 问题新颖。


## ACL 2026：组合 NLI、来源跨度与规则图候选（Phase 56）

在冻结 ACL v3 候选框的 2026 `nli_logic_proof_verification` 待筛子集中，对 58 条逐篇做题名/摘要初筛，保留 26 条方法邻近、2 条背景，排除 30 条出本轮实质综合；五篇官方全文定向核读。CARENLI 已有临床推理类型路由、专用 schema solver 与 verifier；COMPACT 已用 clause graph 表示多条款义务/例外依赖；FactAppeal 已做 claim/source span annotation；Ghost Context 研究错误上下文跨度造成的误归因；SciClaimEval 将真实科学主张连到跨模态表格/图证据。故 NLI 分解、规则依赖图、来源跨度和证据核验不宜单独作为宽泛 novelty claim。

这些工作尚不提供 sense/release-linked WordNet gloss、逐 span 的 Horn premise support gold、保留替代推导的 AND/OR witness DAG 或 source-only proof replay 的 matched baseline。这个差异仍是研究假设，须由更完整检索及同 gold/预算实验验证。CARENLI 的 typed-template/小样本限制、FactAppeal 的 claim-source 未逐一链接、COMPACT 预设相关条款已找到、Ghost Context 无人工 judge validation 子集，均提示项目需把语义支持、来源链接、证据检索与形式 replay 分开评价。逐条筛读和范围边界见Phase 56 报告与[机器日志](../sources/literature_screening_log_2026-10-07_acl2026_nli_logic.json)。


## ACL 2026：图式证据检索、faithfulness 与超图先例（Phase 57）

在 ACL 固定 v3 框对 `graph_rule_provenance` 2026 年剩余 117 条题名/摘要完成筛读，29 邻近、61 背景、27 排除；定向核读 Faithfulness Beyond Plausibility、FEVER 的 Evidence Grounding vs. Memorization、EHRAG、STEM 四篇官方 PDF。EHRAG 已用结构+语义 hyperedges 做检索，STEM 已用 query schema graph 与 evidence completeness 评价结构化多跳检索；所以“用图/超图表示上下文或检索证据”不应单独主张新颖。另两篇强调更窄的审计问题：引用了 source triple 不等于它蕴含 claim，标注了 evidence span 也不等于裁决真实依赖该 span。

这几篇工作没有共同提供 sense/release-bound lexical gloss span、方向性 AND/OR Horn support gold、alternative witness DAG 和独立 source-only replay 的 matched evaluation。此项仍待全范围检索与实验验证。详情见Phase 57 报告及[结构化筛读日志](../sources/literature_screening_log_2026-10-07_acl2026_graph_rule_provenance.json)。


## ACL Anthology 2025：WordNet taxonomy、Horn/tree rules 与证据核验（Phase 58）

在冻结候选框中筛完 2025 年 `graph_rule_provenance` 的 133 条记录，28 邻近、60 背景、45 排除；十篇做官方全文定向核读。新增最直接近邻是 ACL Findings 2025 LORex：其在 WordNet 等 taxonomy benchmark 上结合节点定义、层级路径与候选父节点推理做 taxonomy expansion。因此“定义辅助的 taxonomy parent/hypernym 选择”不宜单独主张新颖；应作为优先适配 baseline。另有 FOL/Horn tree-like rule refinement、faithful graph query decoding、KG trees 与 graph fact-checking 近邻。它们未提供 sense/release-bound gloss span→Horn literal support gold 和独立 source-only replay。筛查边界和比较细节见Phase 58 报告及[逐条机器日志](../sources/literature_screening_log_2026-10-07_acl2025_graph_rule_provenance.json)。

## 2026-10-07：来源归因、NLI 和 entailment-tree 近邻（ACL 2024）

| 工作 | 已有能力/证据对象 | 与本项目的关键差异 | 对照含义 |
|---|---|---|---|
| [Post-Hoc Answer Attribution](https://aclanthology.org/2024.starsem-1.4/) | 将答案分解后以 textual entailment 做来源句选择；研究长文档回答归因 | 答案单元→文档句，不是 WordNet sense-bound gloss span→typed Horn literal 支持 | “拆 claim + NLI source selection”不能独立称新；可在同一 gold 改造成 span retrieval/NLI 参照 |
| [Provenance](https://aclanthology.org/2024.emnlp-industry.97/) | 以轻量 NLI 判定 RAG 输出 factuality，并回溯 context chunk | 检索上下文与生成输出；不表示 gloss rule 或独立符号证明 | 需与 NLI source check 对照，同时分开记录 span-level support 和 proof replay |
| [SPEH](https://aclanthology.org/2024.lrec-main.1329/) | entailment tree 的 step feasibility、错误检测/纠正 | 通用 entailment generation；非 sense/release-bound lexical rule extraction | proof tree、step gate、回退不构成充分差异 |
| [INFUSE](https://aclanthology.org/2024.eacl-long.102/)、[TWEAK](https://aclanthology.org/2024.findings-naacl.106/)、[FENICE](https://aclanthology.org/2024.findings-acl.841/) | 细粒度 NLI、hypothesis verification、claim extraction + factuality | 摘要/知识到文本场景，未提供本任务的 gloss-span support gold | 将 claim extraction、source support、逻辑闭包分层记分 |

逐篇筛读边界见[Phase 59 结构化日志](../sources/literature_screening_log_2026-10-07_acl2024_source_grounded_entailment.json)。这一轮为单人标题/摘要全切片初筛及十篇定向章节核查；不是系统综述，也没有新颖性结论。

## 2026-10-07：规则证明与 WordNet 辅助模型检查（ACL 2024）

| 工作 | 已有能力/输入 | 对本项目构成的边界 | 后续对照 |
|---|---|---|---|
| [FRVA](https://aclanthology.org/2024.findings-acl.540/) | 事实筛选、交叉验证和双向 entailment-tree generation；叶事实与中间结论共同支持 hypothesis | 证明树与多来源事实已存在；输入不是 sense-linked gloss | 优先适配为 retrieval + tree baseline，核对 support selection、每步 entailment 与多前提完整性 |
| [Visual-Textual Entailment with Quantities](https://aclanthology.org/2024.lrec-main.1512/) | scene graph/FOL model 与 hypothesis formula 做 model checking；注入 WordNet 同义词、hypernym 与词向量相似度 | WordNet+符号模型检查已存在，但任务是图像场景与句子，不从 gloss 归纳规则 | 作为 WordNet-lexical bridge + formal entailment 的方法参照；需任务适配，不能横比视觉数据成绩 |
| [Learn from Failure](https://aclanthology.org/2024.acl-long.45/) | intuitionistic propositional theorem 用 Lean 形式化；利用正确/失败证明路径训练，并机检证明 | solver-certified formal proof 和 proof search backtracking 不是新模块 | 分开比较 proof validity、源语言形式化忠实度与失败分支成本 |
| [GProofT](https://aclanthology.org/2024.fever-1.14/)、[TruthReader](https://aclanthology.org/2024.emnlp-demo.10/) | claim splitting、证据检索/归因，或回答引用片段展示 | 证据收集与 citation 回溯不等于 gloss-support 或 source-only proof | 用于 evidence retrieval / attribution baseline，另测 source fact quality |

以上为定向相关工作比较，逐条筛读见[Phase 60 日志](../sources/literature_screening_log_2026-10-07_acl2024_nli_logic_proof.json)。

## 2026-10-07：ACL 2024 ClaimVer、TRACE 与图规则推理

| 工作 | 已有能力/证据对象 | 项目比较边界 |
|---|---|---|
| [ClaimVer](https://aclanthology.org/2024.findings-emnlp.795/) | 抽取 claim spans，对每条 claim 匹配 Wikidata triples，输出支持/矛盾/证据不足、相关 triples 与 rationale | claim span 与 KG evidence 已细粒度归因；不是原始 gloss span，也不是规则 proof |
| [TRACE](https://aclanthology.org/2024.findings-emnlp.496/) | 从检索文档生成 KG 并构造逻辑连接的三元组推理链 | RAG evidence chain 已有先例；非词典规则形式化 |
| [Complex Reasoning over Logical Queries](https://aclanthology.org/2024.acl-long.613/)、[RulE](https://aclanthology.org/2024.findings-acl.256/) | KG 上的复杂逻辑查询及规则嵌入/推理 | 规则和组合查询不新；输入关系来自图谱而非 gloss 源 span |
| [Tree-of-Traversals](https://aclanthology.org/2024.acl-long.665/)、[Right for Right Reasons](https://aclanthology.org/2024.emnlp-main.378/) | KG path traversal 与可验证 commonsense QA 解释 | 路径解释不是 source-only proof certificate |

完整筛查范围和 limitation 见[Phase 61 日志](../sources/literature_screening_log_2026-10-07_acl2024_graph_rule_provenance.json)及深度分析。

## 2026-10-07：ACL 2023 text-to-rule 与 WordNet prover 校验

| 工作 | 已有输入/方法 | 与本项目边界 | 比较优先级 |
|---|---|---|---|
| [Self-Supervised Rule Learning](https://aclanthology.org/2023.findings-emnlp.117/) | 句子→AMR/λ-expression→关系 triple；学习文本 predicate 到加权 KG relation/path 的规则映射 | 直接关系映射先例；限制为单 triple 并假定语义解析正确；不是 gloss 原文对 Horn literal 的 support gold | 高：同一文本/关系候选上比较 relation-linking accuracy、规则可解释性，并单独加标 gloss-span support |
| [WordNet Meronymy Correction](https://aclanthology.org/2023.gwc-1.4/) | WordNet–SUMO 关系映射校正，用 FOL ATP 在 WebChild unseen data 上核验 | WordNet relation + symbolic prover 已有；不做 gloss→rule 编译 | 高：对照资源内关系校验，但不得混同原文语义支持 |
| [LLM+ASP](https://aclanthology.org/2023.findings-acl.321/)、[Logic-LM](https://aclanthology.org/2023.findings-emnlp.248/)、[LINC](https://aclanthology.org/2023.emnlp-main.313/) | NL semantic parsing / logical formalization + ASP、constraint solver 或 FOL prover | 排除泛化 neurosymbolic pipeline 的宽泛创新表述；不监督 glossary provenance | 中：作为通用形式化与求解对照，任务输入须适配 |
| [AMR4NLI](https://aclanthology.org/2023.iwcs-1.29/)、[LogicAttack](https://aclanthology.org/2023.findings-emnlp.889/) | 图式语义 NLI 指标及规则驱动逻辑一致性攻击 | NLI graph 与 rule stress testing 有先例；不等于词典规则来源 gold | 中：评估语义图和方向/组合切片 |

更多近邻与限制见Phase 62 报告和[筛读日志](../sources/literature_screening_log_2026-10-07_acl2023_definition_to_formal_logic.json)。

## ACL 2023：WordNet 释义辅助蕴含与来源归因（Phase 63）

| 工作 | 已有输入/方法 | 与项目的边界 | 比较优先级 |
|---|---|---|---|
| [Grounding Lexical Substitution in Entailment](https://aclanthology.org/2023.findings-acl.179/) | WordNet sense gloss + synonym context，sense-aware lexical substitution，以双向 entailment 为判据 | 直接收窄 gloss/WordNet/sense/entailment 宽泛主张；未做 gloss→Horn、多前提 rule support spans、AND/OR provenance 或 DAG replay | 高：复用同 sense/gloss 作为 lexical-entailment baseline，分离词义正确与规则支持 |
| [Ontology Subsumption Inference](https://aclanthology.org/2023.findings-acl.213/) | OWL atomic/complex concept subsumption 与 NLI formulation | taxonomy/NLI 评测先例；不是定义到规则的来源标注 | 中高：适配 hypernym/subsumption slice |
| [Unsupervised Compositional Entailment](https://aclanthology.org/2023.iwcs-1.5/) | WordNet-derived graph 上的 adjective–noun compositional entailment | 图嵌入词汇组合任务与 gloss support 不同 | 中：词汇组合和图方法对照 |
| [PropSegmEnt](https://aclanthology.org/2023.findings-acl.565/)、[NLI4CT](https://aclanthology.org/2023.emnlp-main.1041/) | Proposition segmentation/entailment；multi-evidence NLI/evidence retrieval | 支持粒度与多证据已存在，未逐规则 literal 建 gloss source gold | 中高：span/NLI 和证据召回 baseline |
| [AlignScore](https://aclanthology.org/2023.acl-long.634/)、[Cross-lingual QA Attribution](https://aclanthology.org/2023.emnlp-main.10/) | 文本对齐事实一致性与答案来源归因 | alignment/attribution 不等于语义充分性和 machine-checkable proof | 中：文本支持检索与归因 baseline |

本轮 57 条题名摘要筛查与十篇定向全文核查为单人审计，不支持 novelty claim；详见Phase 63 深度分析。

## ACL 2023：逻辑规则、可验证解析与图上来源证据（Phase 64）

| 工作 | 已有能力/表示 | 与本项目的差异 | 比较建议 |
|---|---|---|---|
| [SPINDLE](https://aclanthology.org/2023.eacl-demo.15/) | Dutch raw text→typed λ terms/type-logical proof derivations；static checker 验证句法/证明合法性 | 通用句法组合解析，不从 WordNet gloss 学词汇 Horn rule，也不标 literal 对应的 gloss span | 适配 checker/形式语义 pipeline；分开算 proof validity 与 definition faithfulness |
| [LATENTLOGIC](https://aclanthology.org/2023.findings-emnlp.304/)、[Simple Rule Augmentations](https://aclanthology.org/2023.acl-short.23/) | 从 KG relational paths 学逻辑规则，或对既有规则做 abduction/inverse/random-walk 扩展 | 来源是结构化 KG/已有规则，不是自然语言释义 span | 只在图规则学习/变换层比较，不以此替代 gloss grounding |
| [Path Spuriousness](https://aclanthology.org/2023.eacl-main.232/) | 量化多跳 KG answer path 的偶然性与合理性 | 路径质量指标不证明每条前提被 gloss 文本蕴含 | 比较 path reasonableness 与 proof replay 是不同指标 |
| [FactKG](https://aclanthology.org/2023.acl-long.895/) | 现成 KG 上 one-hop/conjunction/existence/multi-hop/negation fact verification | 有逻辑推理现象覆盖，但无 definition→relation extraction/source-span support | 借鉴方向、AND、否定切片；KG 与 gloss 的成绩不可横比 |
| [KG-GPT](https://aclanthology.org/2023.findings-emnlp.631/) | Sentence segmentation + graph retrieval + LLM inference | 假设实体提供并依赖检索到的 evidence graph；不是 source-only Horn certificate | 纳入检索+LLM baseline，控制检索上界 |
| [WiCE](https://aclanthology.org/2023.emnlp-main.470/)、[RoMQA](https://aclanthology.org/2023.findings-emnlp.470/) | Claim/subclaim entailment against source documents；multi-evidence QA 与 gold-evidence upper bound | 有 claim/source 与多证据先例，未链接 lexical rule literals 或独立重放 | 对照 claim decomposition、evidence recall/completeness 与 retrieval oracle |

本轮筛读边界、官方 PDF review depth 和逐篇理由见Phase 64及日志。

## ACL 2023：NLI proof generation、链条评价与证据检索（Phase 65）

| 工作 | 已有能力 | 差异 | 比较含义 |
|---|---|---|---|
| [PROVER](https://aclanthology.org/2023.ijcnlp-main.56/) | Commonsense facts + next-step prediction/search 生成多步自然语言 NLI proofs；人工检验 correctness/minimality | 自然语言 chain 不具形式公理保证，不是 gloss-backed Horn source-only replay | 最直接推理链基线；报告 step NLI、人工正确性与证书回放分项 |
| [ReCEval](https://aclanthology.org/2023.emnlp-main.622/) | NLI-based step correctness + V-information informativeness | informal chain score 非符号推导有效性或来源支持 | chain scorer 辅助对照，不能代替 checker |
| [SICCK](https://aclanthology.org/2023.nlrse-1.12/) | controlled compositional NLI，含 hypernym、quantifier、negation、modifiers | synthetic sentence pairs，不是 definition/source gold | 设计 logic phenomenon minimal pairs，标签由专家另行裁决 |
| [RNN-CCG](https://aclanthology.org/2023.naloma-1.4/) | neural CCG parser，面向语法与 semantic theorem-prover 组合 NLI | parser component，而非完整的 gloss formalizer/verifier | syntax route baseline；独立报 parse 与 semantic correctness |
| [FEVER retrieval](https://aclanthology.org/2023.fever-1.4/) | graph/path-based multi-hop document/sentence retrieval + textual entailment | retrieval/evidence selection 不证明 definition entails rule | 对照候选 source span recall 与 gold-evidence verifier 上界 |
| [Multiple Evidence Combination](https://aclanthology.org/2023.bionlp-1.20/)、[CLEVER](https://aclanthology.org/2023.acl-long.374/) | 冲突多证据 claim verification；claim-only 对 claim+evidence 反事实消偏 | 领域或目标是 veracity/bias，不是 gloss rule proof | 测 evidence contribution、冲突处理和 shortcut controls |

筛查范围和限制见Phase 65 深度报告。

## ACL 2022：逻辑形式、NLProofS 与定义/NLI 近邻（Phase 66）

| 工作 | 已有方法 | 与项目的差异 | 适配对照 |
|---|---|---|---|
| [NLProofS](https://aclanthology.org/2022.emnlp-main.7/) | 支持事实 + hypothesis 输入，生成 AND proof tree；RoBERTa verifier 打分并引导 proof search | 学习式自然语言步骤验证；无 gloss-span semantics、typed Horn source ledger 或独立重放证书 | 强 proof-generation baseline；单报 step validity、fact retrieval、formal replay 和 source support |
| [Dual-(m)T5 PL/FOL](https://aclanthology.org/2022.coling-1.481/) | 中文 utterance↔PL/FOL 训练与 validity reward，并用于增强 NLI | 通用语义形式化，不是词典义项或逐 literal source gold | matched parser + independent checker，分开 logical-form fidelity 与 NLI task score |
| [Japanese CCG temporal NLI](https://aclanthology.org/2022.acl-srw.10/) | CCG compositional semantics + temporal axioms + Vampire | 手工语言学/时间公理；不抽 gloss-derived lexical Horn rule | 结构/组合语义前端与 prover 层参照 |
| [ZS4IE](https://aclanthology.org/2022.naacl-demo.4/) | span/relation candidate verbalization + textual entailment | 类型标签判定不等于规则 literal 的必要充分、来源支持 | 候选 verbalization/NLI 直接 baseline |
| [Open Relation Modeling](https://aclanthology.org/2022.findings-acl.26/) | entity definitions + KG paths → definition-like relation descriptions | 从 structured entities 生成 prose；项目方向是原 gloss→formal evidence-bearing rule | definition-conditioned KG text generation 背景参照 |
| [Coq Autoformalization](https://aclanthology.org/2022.mathnlp-1.4/) | NL math proof→Coq，proof engine check | 机器检查已有先例，但数学域与词典语义不同 | distinction checklist：parser correctness vs formal proof vs source meaning |
| [TextGraphs Premise Selection](https://aclanthology.org/2022.textgraphs-1.15/) | 自然语言数学证明前提检索，SBERT/GPT ranking | premise retrieval 不证明 entailment 或 source rule | retrieval recall、embedding baseline、gold-premise oracle |
| [Definition Sentence Embeddings](https://aclanthology.org/2022.starsem-1.12/) | 通过 definition word prediction 训练 sentence vectors 并和 NLI supervision 对照 | definition representation，不生成可重放规则 | lexical embedding/sense scoring baseline |

详细范围与 limitation 见Phase 66 深度分析。

## ACL 2021：形式 prover、Horn 推理与解析稳定性（Phase 67）

| 工作 | 已有输入/方法 | 与本项目边界 | 比较优先级 |
|---|---|---|---|
| [Talking with the Theorem Prover](https://aclanthology.org/2021.paclic-1.44/) | CCG/formal semantics + theorem prover；未证 lexical subgoal 转 readable NL，用户补临时 axiom 后继续 | 直接的词汇缺口与 prover 交互先例；规则非自动从 sense/release-specific gloss/span 抽取，也无 source-only Horn certificate | 高：对比用户补知识、静态 lexicon 与自动 gloss grounding 的覆盖/成本，隔离 proof validity 与 source support |
| [RuleBERT](https://aclanthology.org/2021.emnlp-main.110/) | 给定/从 RDF KG 挖出的软 Horn rules + facts 上训练 PLM 模拟推理 | 软 Horn reasoning 已有先例；没有逐条 gloss literal support 标注或确定性证书重放 | 中高：给定同一 gold rule/fact 的神经规则推理对照 |
| [UniKER](https://aclanthology.org/2021.emnlp-main.769/) | definite Horn 前向链 + KG embedding 做 KG inference | 显式 Horn inference 先例；KG relation triple 不是自然语言 gloss 的语义证据 | 中：对比 rule reasoning 层，不能将 KG 结果当 source-support 对照 |
| [WinoLogic](https://aclanthology.org/2021.emnlp-main.307/) | situation-calculus commonsense formulas 由 Z3 检查是否支持 WSC 答案，再转写自然语言诊断句 | prover 认证只覆盖给定形式输入；不认证自然语言到公式的语义忠实度 | 高：对照“形式蕴含”验证，并新增独立 gloss/formula adjudication |
| [Enforcing Consistency](https://aclanthology.org/2021.acl-short.22/) / [Parser Robustness](https://aclanthology.org/2021.eacl-main.292/) | related utterance program consistency、meaning-preserving semantic-parser perturbation | 解析稳定性和 spurious program 评测有先例；任务不评 gloss literal support | 中：迁移为 paraphrase/构式扰动切片 |

本轮为固定 ACL Anthology 候选框的 direct-keyword slice，单人筛读、未复现；详见Phase 67 报告及[结构化日志](../sources/literature_screening_log_2026-10-07_acl2021_logic_proof.json)。
## 2026-10-07：语义图驱动的正式规则抽取

Recski et al., [BRISE-Plandok](https://link.springer.com/article/10.1007/s10579-024-09747-7)（LRE, online 2024 / volume 2025）用 UD→4lang 图和领域手写图模式抽取德语法规属性，并构造可转成逻辑形式的规则；经双人标注/作者复核的 7,049 句 gold 上评测。全属性端到端完全正确率 46%；只计系统覆盖的 40 个属性为 55%；使用 gold 属性时约三分之二规则完全正确。模式基于完整标注数据形成，作者不把结果解释为跨文档泛化。此工作排除宽泛的“首次图式 NL→形式规则抽取”和“首次人工 gold 评测”，但不是 WordNet/gloss lexical baseline：任务、规则目标和语义来源均不同，数字不得横比。可借鉴分组件与 end-to-end 指标、记录 human suggestions 和模式/测试隔离；项目仍须独立评 source-span support、sense/direction、typed Horn 和 proof replay。详见[筛读日志](../sources/literature_screening_log_2026-10-07_brise_plandok_rule_extraction.json)。

## 2026-10-07：BRISE 语义图规则抽取与 deontic prover

Recski et al., [Explainable Rule Extraction via Semantic Graphs](https://ceur-ws.org/Vol-2888/paper3.pdf)（ASAIL 2021）建立 UD→4lang→任务专用 grammar/pattern→deontic logic rule→theorem prover pipeline，提供逐步解释。这已排除“首次 semantic graph 编译 formal rule 并接 prover”的宽泛主张；但 full-pipeline perfect result 只来自 6 条刻意选定的 toy sentences，作者明确说它不构成完整系统定量评估。另报 10-doc sample 上 attribute extraction P>93/R>51，非 rule correctness。其法律 domain 与 WordNet gloss 的 typed Horn/source support 不同；形式推理通过也不能证明 NL→rule 正确。2021 原型与 BRISE-Plandok 2025 应合并视作一个研究线，不当作两个独立 prior-art counts。详见[筛读日志](../sources/literature_screening_log_2026-10-07_brise_explainable_rule_extraction_2021.json)。

## NeurIPS 2025：形式化忠实度与 WordNet 层级（Phase 115）

| 工作 | 已有输入/方法 | 与本项目边界 | 比较优先级 |
|---|---|---|---|
| [HAR/CoPA](https://proceedings.neurips.cc/paper_files/paper/2025/hash/1d41343cf93afd6456db3d1820ce1a58-Abstract-Conference.html) | 数学题自然语言/非正式解法→statement autoformalization→形式草稿→proof search；HAR 分层生成，CoPA 自举数据 | 近期正式先例覆盖分阶段 autoformalization、形式证明与 proxy data generation；proof validity 不校验 WordNet gloss 对规则/span 的语义支持 | 中：可参考阶段分解和形式有效性报告；数学 benchmark 分数不与词汇任务横比 |
| [miniF2F-Lean Revisited](https://proceedings.neurips.cc/paper_files/paper/2025/hash/72dad95a24fae750f8ab1cb3dab5e58d-Abstract-Conference.html) | 自然语言数学题→Lean formalization→proof，要求证明目标忠实对应原题；修订 formal/informal benchmark 并做人工核查 | 强方法论先例：compiler/type/proof 成功不蕴含输入自然语言→形式语句忠实；不是词义或 gloss-support 工作 | 高：借鉴 source/formal fidelity 独立审计、人工对照和端到端指标；reported score 不是本项目 baseline |
| [Hierarchical Retrieval](https://proceedings.neurips.cc/paper_files/paper/2025/hash/db5e34020dab7c046908bddace8e5cd9-Abstract-Conference.html) | WordNet synset taxonomy→dual-encoder ancestor retrieval；pretrain-finetune 缓解远距离检索损失 | WordNet hierarchy representation/retrieval 先例；没有 gloss parsing、typed Horn、relation-span support 或 proof replay | 低/邻接：用于界定 hierarchy representation prior art；不可作 gloss entailment 或 proof baseline |

本轮仅为三篇官方论文定向筛读，不是 NeurIPS 全量检索或新颖性证明。详见[结构化日志](../sources/literature_screening_log_2026-10-07_neurips2025_autoformalization_wordnet.json)与Phase 115 报告。
## ICLR 2026：语义忠实度评估与 AND/OR phrase interactions（Phase 116）

| 工作 | 已有输入/方法 | 与本项目边界 | 比较优先级 |
|---|---|---|---|
| [ReForm](https://proceedings.iclr.cc/paper_files/paper/2026/hash/419bd6a89ab56e9c09ededb560b06192-Abstract-Conference.html) | 数学自然语言题↔Lean 形式语句；反思式自检/修正；859 项 semantic-consistency expert benchmark；两人独立、第三人裁决 | 强先例：formal compiler validity 与 source/formal semantic fidelity 分开，且有专家审阅；不涉及 WordNet、lexical relations、gloss spans 或 typed Horn proof | 高：借鉴 evaluator audit、双标/裁决和 separate metrics；仅能方法学比较，不能横比词汇任务成绩 |
| [Can LLMs Reason Soundly in Law?](https://proceedings.iclr.cc/paper_files/paper/2026/hash/5513e4a36d7637b697253e77754b67ea-Abstract-Conference.html) | 领域专家标注输入 phrase 相关/无关/禁止；提取模型决策分数的稀疏 AND/OR feature interactions | AND/OR 是数值模型行为归因，不是 Horn rule conjunction/disjunctive alternatives、proof DAG 或 source entailment；phrase relevance 不等于逐 claim text support | 中：限制“AND/OR inference pattern / phrase audit 首创”说法；不构成逻辑证明基线 |

筛读为 ICLR 官方来源定向全文，不是 proceedings 全集或系统综述。详见[筛读日志](../sources/literature_screening_log_2026-10-07_iclr2026_reflective_fidelity_and_andor_audit.json)和Phase 116。

## Findings of EMNLP 2025：推理证明与评价近邻（Phase 120）

| 工作 | 方法/证据范围 | 与项目关系 | 比较边界 |
|---|---|---|---|
| [Stress-Testing the Reasoning Competence of Language Models With Formal Proofs](https://aclanthology.org/2025.findings-emnlp.661/) | ProofGrid 覆盖命题/等式推理的 proof writing/checking、inpainting 和 gap filling，发布 10K+ 形式推导问题 | 形式证明结构、写入与核验属于直接方法学先例 | formal proof replay 不验证 gloss→rule fidelity 或 span support；不是词汇任务 baseline |
| [VerifiAgent](https://aclanthology.org/2025.findings-emnlp.891/) | 两层 meta-verification 加按推理类型选择工具的自适应 verifier | 通用核验工具选择/编排已有先例 | 不等于以冻结 source bindings 为输入的确定性 source-only 独立证书重放 |
| [Assessing LLM Reasoning Steps via Principal Knowledge Grounding](https://aclanthology.org/2025.findings-emnlp.1085/) | principal knowledge units 与 LLM-based step grounding/application/correctness 评价，并有限人工核查自动标出的事实性案例 | 知识 grounding 与 reasoning-step 评价已有先例，自动 judge 需要审计 | 模型知识库存和 LLM evaluator 不是 sense/release-linked 人工 gloss-span semantic gold |
| [DivLogicEval](https://aclanthology.org/2025.findings-emnlp.47/) | 900 项逻辑推理评测框架，关注 accuracy 以外的行为指标及 run variability | 逻辑评测多维性与稳定性可用于设计审计 | 不验证词典释义支持、typed Horn fidelity 或 proof replay |

四篇为官方记录及 PDF 定向筛查，未运行系统/数据；均未进入冻结 ACL v3 查询候选框。该补查不构成 EMNLP 全量 review 或新颖性证明。细节见[结构化筛读日志](../sources/literature_screening_log_2026-10-07_emnlp2025_reasoning_verification_grounding.json)与Phase 120。

## 2026-10-07：KR 2026 Datalog provenance 与近期词汇/规则工作对账（Phase 133）

| 工作 | 已有方法与结果 | 对本项目定位的影响 | 边界 |
|---|---|---|---|
| [Why(-Not)-Provenance for Datalog with Negation](https://proceedings.kr.org/2026/19/)（KR 2026 Main Track） | 基于 justification theory，为 well-founded/stable-model 语义下的 Datalog with negation 定义 why- 与 why-not-provenance；why-support 是可推出目标事实的输入数据库事实集合，recognition 问题为 NP-complete（正 Datalog 已有该复杂度） | 直接先例覆盖 proof tree、alternative supports 和逻辑程序 provenance；不能把 witness DAG、支持集或 Datalog derivation replay 单独写成贡献 | 不评估 WordNet gloss、义项绑定、typed lexical rule 或 gloss-span semantic support。项目差异只能是待测的自然语言 source-span→literal support + source-only certificate 联合合同 |
| [A Foundation Model for Zero-Shot Logical Rule Induction](https://www.ijcai.org/proceedings/2026/445)（IJCAI Main Track；已登记，重核） | 从合成 Boolean DNF 预训练，面向表格任务作零样本规则归纳；报告 14 个 UCI 数据集 | 宽泛 AND/OR rule induction 已有主会先例 | 变量是表格特征，不是义项/释义；预测准确率不是 gloss support |
| [Towards a Gold Standard for Adjectival Hypernymy](https://aclanthology.org/2026.lrec-1.293/)（LREC 2026；已登记，重核） | OEWN definition-conditioned adjective hypernym generation + 人工验证，形成 3,836 pair resource | 作为 taxonomic hypernym/annotation 设计优先邻居；reported consensus acceptance 不能当作整体准确率 | 不标注定义 span 对 typed Horn literal 的支持，也不重放证明 |
| [When Structure Matters: Cross-Lingual Hyperbolic Embeddings for Chinese and English Wordnets](https://aclanthology.org/2026.lrec-1.944/)（Ku et al., LREC 2026 main；全文于 2026-10-05 筛读） | 18 页官方 PDF 全文已筛读：OEWN 名词 hypernym graph → 20-D Poincaré embedding；GPT-5-mini CWN→PWN sense alignment；vocabulary-constrained transfer。所谓 zero-shot 并非 unseen-synset；单次训练末 10 checkpoints 作统计 | 纳入 WordNet taxonomy transfer/hypernym ranking 近邻。其 reported metrics 不能与 gloss-support/NLI 直接比较；CWN 自动对齐未经人审且结构分布不平衡 | 不用 gloss 抽取关系，不标 gloss-span support，也不编译/重放 typed Horn proof。作者声称发布工件但旧筛读未找到项目 URL；代码/数据与许可未独立核验。原文证据见[Phase 2026-10-05 full-text log](../sources/literature_screening_log_2026-10-05_recent_acl_wordnet_slice.json)及Phase237 对账 |
| [Neural DTS](https://aclanthology.org/2026.naloma-1.2/)（NALOMA 2026 workshop；已登记，重核） | WordNet hypernym embedding 在日语 DTS/wani proof search 中动态注入 IS-A axioms | 已有 WordNet 层级学习 + logic-based NLI/prover 的直接组合 | workshop PoC；输入 relation 来自 taxonomy，不是从 gloss spans 抽取规则；小规模分母与独立 oracle score 不可混报 |

本轮新增正式 prior 只有 KR 2026 provenance 论文；另三项为官方全文范围/任务边界的去重对账，不增加独立检索计数。该 targeted screen 不构成 proceedings census、系统综述或 novelty proof。逐项 URL、全文检查范围与限制见[Phase 133 机器日志](../sources/literature_screening_log_2026-10-07_kr2026_provenance_and_lexical_reasoning.json)和深度报告。

## KR 2026：最小支持相关性、FOL 解释与 proof-search 邻接项（Phase 134）

| 工作 | 已有能力/表示 | 与本项目的差异 | 比较含义 |
|---|---|---|---|
| [How Hard is it to Decide if a Fact is Relevant to a Query?](https://proceedings.kr.org/2026/18/)（KR Main Track） | 对数据库 D、布尔 conjunctive query 与事实 f，判定 f 是否属于使查询成立的某个最小子集；给出复杂度边界 | 直接覆盖“输入事实是否是最小支持/解释的一部分”，但对象是数据库事实与 CQ，不是 gloss span 对词汇 Horn literal 的语义支持 | 排除最小支持/事实相关性本身的宽泛新颖性；项目需把 source-span semantic correctness 与必要/充分性作为单独标注目标 |
| [Identifying and Explaining (Non-)Equivalence of First-Order Logic Formulas](https://proceedings.kr.org/2026/61/)（KR Main Track） | 面向自然语言规格学习 FOL 的技术支持，测试公式等价/非等价并解释非等价；在超过 100,000 对公式上报告实验 | 解释对象是形式公式间的非等价，不是自然语言定义到形式规则的忠实抽取，也不提供 gloss 证据 | “解释逻辑形式错误/差异”已有近期主会先例；仍需区分输入形式化的可解释诊断与 source-grounded lexical rule generation |
| [Proof-Search for Normative and Doxastic Reasoning and Its Use in Logical Argumentation](https://proceedings.kr.org/2026/60/)（KR Main Track） | 对 input/output logic 与 normal default logic 构造 modular、rule-based、terminating decomposition tree；成功终止树证成对应论证的 derivability | 形式规则 proof certificate 邻接，不涉及 WordNet sense/gloss parsing、typed lexical Horn 或源跨度判断 | 不把规则分解树可终止并可作推导证书作为孤立新颖点；比较重点仍是来源语义链条 |
| [The Chase in Lean - Crafting a Formal Library for Existential Rule Research](https://proceedings.kr.org/2026/33/)（KR Main Track） | 在 Lean 中构造 existential rules/chase 的形式化框架，重现 universal model、core 等性质并统一部分终止条件 | 是规则推理实现的形式验证/可复现先例，语义对象与项目的有限冻结词汇 Horn witness 不同 | 将机器检查和来源正确性分开：Lean/checker 只能覆盖形式系统及其编码，不自动证明 gloss 对规则的支持 |

本轮依据 KR 2026 官方目录中 proof、support、relevance、explain 等主题选取候选并检查官方摘要；这是有限主题补查，不是 KR 全目录逐篇筛查，也没有检索召回估计。详情见Phase 134 深度报告和[结构化日志](../sources/literature_screening_log_2026-10-07_kr2026_provenance_and_lexical_reasoning.json)。

## Phase 135：EACL 2026 gloss/lexical prediction

| 工作 | 方法/边界 | 比较含义 |
|---|---|---|
| [Where Do LLMs Compose Meaning?](https://aclanthology.org/2026.eacl-long.214/)（EACL 2026 Long Papers） | CAP 对 Transformer 词/短语 activation 做 pooling intervention；WordNet 任务含 gloss→term 的 inverse definition modelling，以及 word→hypernym。后者不输入 gloss；论文不抽 typed AND/OR Horn，也不评 gloss-span support。 | 关闭“LLM 尚未做 WordNet 定义恢复/上位词预测”的宽泛说法。CAP 只统计干预前已答对子集的条件 accuracy drop，不是 full-set accuracy、source support 或 proof validity。需在相同 sense/release/split 上另做 gloss→relation matched baseline。 |

论文未在冻结 ACL v3 候选或现存日志中，显示检索词族漏掉 inverse definition modelling 等表达，不估计领域召回率。详见Phase 135 报告及[结构化日志](../sources/literature_screening_log_2026-10-07_eacl2026_gloss_composition.json)。

## ACL 2026：分步事实核验与原子 claim 分解（Phase 142）

Ye et al., [Teaching Language Models to Check Grounded Claim Factuality with Human Test-Taking Strategies](https://aclanthology.org/2026.acl-long.1468/) 将文档事实性核验拆成 claim 原子事实分解和逐事实支持判断；提示词依次检查主客体是否出现、其描述是否受来源支持、关系是否被支持以及剩余内容能否推断。作者在 FacTax-Benchmark 与 LLM-AggreFact 上报告 balanced accuracy，并提出 SFT+DPO 训练的分解/核验小模型。该文已排除“结构化 prompt、分步 evidence checking、理由生成”单独作为新颖性主张。论文对象是摘要/RAG 的长文档 claim，不处理 WordNet sense resolution、gloss-span→typed Horn support 或 proof/countermodel replay；reported scores 与 token savings 不是本项目结果，也不是可直接横比的 baseline。后续可把其 staged checking 适配为同一冻结 gloss-pair 输入上的 prompt baseline，并单独评估方向、span support、abstention 和成本。见[Phase 142 全文定向筛读日志](../sources/literature_screening_log_2026-10-08_grounded_claim_factuality_acl2026.json)与深度报告。

| [G-IdiomAlign](https://aclanthology.org/2026.acl-long.1794/)（Ye et al., ACL 2026） | Wiktionary gloss 作跨语言 idiom alignment 的语义 pivot；设置 No-gloss/With-gloss generation 对照，使用 embedding similarity 代理并对部分数据做人工评估。 | 证明 gloss contrast 作为一般方法已存在。与项目不同之处在 WordNet sense-level 有向关系、raw-gloss span-to-rule gold、typed AND/OR completeness 与 source-only proof replay；proxy 不能作本项目 gold。 |
| [ReportLogic](https://aclanthology.org/2026.acl-long.384/)（Zhao et al., ACL 2026） | 研究报告逻辑的 rubric-guided pairwise preference；三层八维 taxonomy，由三位专家对 test pairs 多数裁决。 | 一般 human-rated auditability、evidence sufficiency、claim-support quality 已有先例。其单位是报告对，不绑定每条 claim 的外部来源 span、lexical sense 或可重放证明。 |

两篇均不在固定 ACL v3 1,747 项候选框或此前逐篇结构化日志；按 out-of-frame targeted discoveries 记录，不改候选计数，也不据此估计 recall。见Phase 149 报告和[筛读日志](../sources/literature_screening_log_2026-10-08_acl2026_gloss_auditability_addendum.json)。


## ICML 2026 与 NeurIPS 2025：proof, verification 与 source fidelity

| 工作 | 最近的方法/评测 | 与本项目的边界 | 对照优先级 |
|---|---|---|---|
| [APOLLO (NeurIPS 2025)](https://proceedings.neurips.cc/paper_files/paper/2025/hash/3b77109ad4dd4ba82d07cacd4b24207e-Abstract-Conference.html) | Lean feedback 驱动错误定位、子目标拆分、证明修复与重验；已核官方 PDF | 是 formal proof repair 先例；验证 formal statement 下的 proof，不验证 statement 是否忠实表达某个词典 gloss | 中：若评估端到端路线，应与 proof-search/repair 工作分离，并单测 source fidelity |
| [Weaver (NeurIPS 2025)](https://proceedings.neurips.cc/paper_files/paper/2025/hash/715f48023c26ad210321a4c0da67f27c-Abstract-Conference.html) | weak supervision 聚合 reward models/LM judges，用于 repeated-sampling verification | 是 verifier fusion 先例；聚合 judge 信号不等于独立 gold、形式证书或源释义支持 | 中：未来可作 verifier-ensemble 对照，需在人类 source-support gold 上校准 |
| [MuSLR (NeurIPS 2025)](https://proceedings.neurips.cc/paper_files/paper/2025/hash/4a69d58b1a64fd931ef72cd93b71dcbe-Abstract-Conference.html) | 多模态、正式规则驱动的组合逻辑推理 benchmark；本轮仅摘要级 | 支持测原子/组合规则及深度；不含 WordNet gloss、sense binding 或 span-support gold | 中：可借鉴组合/干扰压力切片，不可横比其 VLM 分数 |
| [Beyond Theorem Proving (ICML 2026)](https://proceedings.mlr.press/v306/liu26gl.html) | Lean 下 constructive problem-solving、proof obligation 与形式语义 RPE 指标；摘要级 | 把形式有效与答案等价区分；数学规格不同于词典 gloss 对 lexical rule 的源语义支持 | 高：启发报告 specification fidelity 和 proof validity 不同指标 |
| [Editable Proof Sketch (ICML 2026)](https://proceedings.mlr.press/v306/xiao26q.html) | EditableSketch/SketchRefine incrementally refines proof sketches while preserving established subgoals. | Prior art for localized proof repair/decomposition; does not ground a lexical rule in gloss evidence. | 中：可借鉴为形式证明开发 baseline，不是语义支持 baseline |
| [Learning to Self-Verify (ICML 2026)](https://proceedings.mlr.press/v306/chen26es.html) | generation/self-verification 双目标学习；摘要级 | 学习型 verifier 不是独立 proof checker 或 human gloss entailment gold | 中：作学习 verifier 背景，不可作 source-support 方法基线 |
| [RULEBREAKERS (ICML 2025)](https://proceedings.mlr.press/v267/chan25a.html) | 对比形式规则与常识/事实预期；摘要级 | 提醒形式 validity、lexical entailment 与世界知识 plausibility 不可混为一类 | 高：标注协议应明确不把典型性替代词义关系蕴含 |
| [Mathesis (ICLR 2026)](https://proceedings.iclr.cc/paper_files/paper/2026/hash/93d5797656d3e70dca7535160a1458f3-Abstract-Conference.html) | NL 数学题→Lean→proof；LeanScorer 分解条件/结论并评估 formalization semantic consistency；官方 PDF 定向核读 | 排除通用自然语言 autoformalization + semantic scoring 的宽泛创新主张；LLM-assisted mathematics scorer 不等于 gloss-span gold | 高：适配 formalization-fidelity/semantic-eval baseline 设计，但需重新定义为 lexical source support |
| [Let's Explore Step by Step (ICLR 2026)](https://proceedings.iclr.cc/paper_files/paper/2026/hash/148c0aeea1c5da82f4fa86a09d4190da-Abstract-Conference.html) | 从 Lean variables/proof steps 构造 dependency DAG，拓扑遍历生成探索轨迹；官方 PDF 定向核读 | generic DAG/topological proof-step lineage 已有先例；其图不含 source-document/WordNet gloss attribution 或 AND/OR lexical semantics | 高：必须与其区分通用 DAG 与 source-grounded AND/OR witness/provenance |
| [SCI-Verifier (ICLR 2026)](https://proceedings.iclr.cc/paper_files/paper/2026/hash/7d60bfd8458b67acbbaf18b892338d00-Abstract-Conference.html) | 多领域 expert-grounded answer equivalence benchmark + reasoning verifier；官方 PDF 定向核读 | 人标答案等价并不构成 gloss span 对 rule literal 的语义支持标签 | 中：参考专家标注/分歧处理，不可当作 lexical gold |
| [Variation in Verification (ICLR 2026)](https://proceedings.iclr.cc/paper_files/paper/2026/hash/ea21628f0fc0de542373be4c88343478-Abstract-Conference.html) | 12 benchmarks 分析 verifier 与 generator 能力/题目难度交互；官方 PDF 定向核读 | 通用 verifier 分数不应外推到 gloss semantics；需按难度、generator、condition 分层 | 中：可借鉴 evaluation stratification，不是语义支持 baseline |

此表为选择性更新，不是相关会议 proceedings 全量盘点；筛读层级、APOLLO 元数据冲突与限制见Phase164。

## Phase 166：WordNet sense prediction 与 gloss-based sense annotation 邻居

| 工作 | 方法与评测 | 与本项目的边界 | 对照价值 |
|---|---|---|---|
| [Linguistic Knowledge Graphs for Sense Prediction: A Case-study on Latin](https://aclanthology.org/2026.lrec-1.856/) | 上下文句子 + target sense gloss 做 WSD；检索 Latin WordNet synset/hypernym 与作者元数据；全文定向核读 | Hypernym 在图中已作为 sense metadata，论文不从 gloss 推导 formal rule 或证据 span | 高：作为 gloss/context + WordNet hypernym prompting 设计邻居，需在同一 lexical gold 重做 |
| [CEFR-Annotated WordNet](https://aclanthology.org/2026.lrec-1.292/) | LLM 比较 WordNet 与 EVP gloss、转移 CEFR sense label；全文定向核读；作者声明未人工 spot-check transferred labels | 直接的 LLM WordNet gloss→sense-level label 先例，但非 gloss entailment、typed relation 或 proof | 高：排除宽泛 gloss-to-sense label novelty；下游 classifier F1 不可作 label-level gold |
| [Tokenization Granularity and Medical Term Representations](https://aclanthology.org/2026.bionlp-1.45/) | UMLS term-definition retrieval with WordNet comparison；摘要级 | 表示/检索指标不是关系蕴含或逻辑证明 | 低：定义检索背景 |
| [Konkani Wordnet Resources](https://aclanthology.org/2026.wildre-1.6/) | Konkani WordNet extraction/normalization and resource integration；摘要级 | 资源工程，不是 gloss formalization 方法 | 低：多语资源可复算性背景 |

逐篇筛读和全切片深度账本见Phase166、[结构化日志](../sources/literature_screening_log_2026-10-08_acl2026_wordnet_slice_phase166.json)和[reconciliation](../sources/acl_anthology_candidates_2026-10-08_v6_reconciled_phase166.json)。
## Phase 167：AAAI 2026 形式化与可执行规则近邻

| 工作 | 已有输入/方法 | 与本项目边界 | 比较优先级 |
|---|---|---|---|
| [Do LLMs Really Struggle at NL-FOL Translation?](https://ojs.aaai.org/index.php/AAAI/article/view/40258) | 给定 ontology signature + natural-language glossary；NL→FOL、SMT equivalence、connective/quantifier/negation edits | ontology extraction 未评；没有 sense-bound lexical relation span gold | 高：拆出 ontology/type 与 formula；借鉴公式扰动但须定制 lexical ontology |
| [From Hypothesis to Premises (HBLR)](https://ojs.aaai.org/index.php/AAAI/article/view/40434) | confidence-aware selective translation、LLM semantic verifier、backward hypothesis search | benchmark answer/efficiency，不是可 replay 的来源证明 | 中高：排除 selective translation/backward search 的宽泛新颖性 |
| [StepFun-Formalizer](https://ojs.aaai.org/index.php/AAAI/article/view/40691) | 数学 formal knowledge + reasoning data 合成、SFT/RLVR、BEq | 数学定理 formalization，与 lexical gloss support 不同任务 | 中：背景/autoformalization prior，不作 matched baseline |
| [Language Models and Logic Programs for Trustworthy Tax Reasoning](https://ojs.aaai.org/index.php/AAAI/article/view/41212) | statute/case→Prolog→SWI-Prolog execution，错误/超时可 abstain；AAAI special track | 案例税额 outcome 与人工翻译 gold，不逐条测 gloss-span fidelity | 中高：排除通用 NL rule→Horn execution/abstention 首创 |

此为四篇选篇定向官方 PDF 筛读，不是完整 AAAI census。详见Phase167报告与[结构化日志](../sources/literature_screening_log_2026-10-08_aaai2026_formal_logic_neighbors.json)。
### Phase 170：近期逻辑评测方法邻居

| 工作 | 已有方法 | 边界与项目用途 |
|---|---|---|
| [Logic-Level Evaluation of Logical Table-to-Text Generation (CoNLL 2026)](https://aclanthology.org/2026.conll-main.41/) | 逻辑类型分解评测；NLI/TAPAS/TAPEX verifier 对照；针对分歧作人类 LF-adherence 分析 | 主会评测邻居。输入是表格与逻辑操作而非 WordNet gloss；启发报告 verifier disagreement 和 false rejection，不是 gloss-support baseline。人审为单标注者小样本。 |
| [Semantic Distance for Presburger Formula Generation (NALOMA 2026)](https://aclanthology.org/2026.naloma-1.9/) | Presburger formula 模型集合语义距离与 SFT/GRPO reward | Workshop 公式评测邻居。仅在可处理 Presburger 语义上比较公式；测试为合成数学习题，仍有量词前缀丢失。不能替代 gloss span 对规则的语义支持，也不直接适用于 WordNet。 |

机器记录、全文范围与报告边界见Phase170和[筛读日志](../sources/literature_screening_log_2026-10-08_logic_evaluation_neighbors_phase170.json)。

### Phase 174：ACL Findings 的 NL2FOL 推理时纠偏

| 工作 | 已有方法与证据 | 与本项目的边界 |
|---|---|---|
| [LSEG (Huang et al., Findings ACL 2026)](https://aclanthology.org/2026.findings-acl.1213/) | 对逻辑保持表面变体抽取隐藏状态纠偏方向，以内部层熵触发干预；50 个人工选句做 calibration；以 FOLIO/MALLS 的 logical equivalence 评价，并在 LogicLLaMA checkpoints 上检查迁移。 | 已有推理时表示纠偏与 NL2FOL 等价评价先例；entropy 不是语义正确性或来源支持 oracle。任务不涉及 WordNet sense、gloss span→typed Horn support、source release identity 或 witness-DAG provenance，不是本项目 matched baseline。跨论文比较结果非同设置。 |

这是一篇官方 ACL Findings 全文定向审阅，未修改 ACL v6 固定候选框，不是 Findings 全量 census。详见Phase174报告和[结构化日志](../sources/literature_screening_log_2026-10-08_lseg_nl2fol_findings_acl2026.json)。

## Phase 177：结构引导 logical-form generation 与可验证过程监督

| 工作 | 已有方法/评测 | 与本项目的边界 | 比较含义 |
|---|---|---|---|
| [SELF-KBQA](https://aclanthology.org/2026.findings-acl.177/)（Tian et al., Findings ACL 2026） | 结构感知 KB 子图检索 + Core Reasoning Patterns + semantic score + evidence condensation，引导 LLM 生成可执行 logical forms；在 GrailQA、WebQSP、GraphQuestions 以 answer EM/F1 评估，并做 component ablation/error analysis | Freebase/KBQA 有明确 schema、实体、关系和 logical-form supervision；不解析 WordNet definition spans、不判断 gloss→typed rule support、无 source-only witness certificate | 排除“subgraph-guided executable LF”宽泛新颖性；可借鉴把候选规则结构、语义排序和下游执行分轴评价，但非 lexical gold/baseline |
| [Correct Answers from Sound Reasoning: Verifiable Process Supervision for Language Models](https://arxiv.org/abs/2605.12519)（Kim et al., COLM 2026） | SFT 诱导结构化推理格式，抽取中间 claims，以 chess engine/domain signals 和 GSM8K arithmetic/consistency signals 做 deterministic process rewards；人评 50 traces | 训练过程奖励与领域信号核验，不是形式 proof replay 或自然语言来源语义裁决；人评子集为单一 annotator 与 Claude judge 相关，不是多标注者 IAA | 排除“一般确定性核验推理步骤”宽泛首创；可启发过程层指标与答案正确性分离，但不作 gloss-source support 对照 |

两篇论文的官方来源、全文筛读深度和非系统筛查限制见Phase177报告与[结构化日志](../sources/literature_screening_log_2026-10-08_structural_kbqa_and_process_verification.json)。COLM venue 由[官方 accepted-papers list](https://colm.eventhosts.cc/Conferences/2026/AcceptedPapers)核实；方法细节取自 arXiv v2 全文。表中任务边界不构成新颖性证明。

## Phase 183：候选正确性与下游验证效用

| 工作 | 方法与论文内任务 | 与本项目的边界 | 比较含义 |
|---|---|---|---|
| [Quokka](https://arxiv.org/html/2509.21629v4)（COLM 2026；早期预印本题名 *InvBench*） | 对 LLM 生成的 loop invariant 分别检查候选正确性及其能否帮助证明目标 assertion；verifier 结论为 proved/refuted/inconclusive。以相对 UAutomizer 的额外解题数、总解题数、端到端时间评测，且结果随 timeout budget 变化。 | C 程序 invariant synthesis，不是 WordNet sense/gloss 语义支持；不是项目 matched baseline。形式验证器对输入程序的结论不标注原始自然语言是否支持候选规则。 | 若项目将来测下游 proof utility，应固定 facts/queries/prover 并明确预算，但必须另有人类裁决的 gloss-span→literal support gold。timeout/unknown 不得被算作反例或成功。 |

论文细节、版本沿革和筛查限制见Phase183报告与[机器日志](../sources/literature_screening_log_2026-10-08_colm2026_verifier_utility_quokka.json)。

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
## 2026-10-08：未见符号上的 Horn 逻辑泛化（Phase208）

| 工作 | 任务与证据 | 与本项目的边界 |
|---|---|---|
| [To See the Unseen](https://arxiv.org/html/2604.21632)（Lazić et al., COLM 2026） | 合成 definite/Horn clauses、facts 和 query，以 forward chaining 生成推理轨迹；从头训练小型 decoder-only 模型，评估 seen、unseen-query、all-unseen-symbol 条件。报告未见 token embedding/unembedding 塌缩；copy attention、提高符号多样性以及冻结/重置 embedding 可改善部分 OOD 切片。另报告 Gemma 3 unused tokens 表征更相关、相近微调准确率所需步数较多。 | 关闭“Transformer 的 Horn 逻辑推理”或“一般新符号 OOD 推理”作为宽泛首创；提示未来按词项/义项/surface 分组审查泄漏并单列 OOD 指标。论文是合成逻辑任务，不做 WordNet sense/gloss 到规则抽取、span source-support、AND/OR witness DAG 或 source-only replay；不是项目 matched baseline，论文结果未复现。理论分析有假设，大部分实验为小模型。 |

本轮只做一篇定向全文筛读，并核对[官方 COLM 接收目录](https://colm.cc/Conferences/2026/AcceptedPapers)；LPDS 在 Phase55 已筛读，本轮去重，不重复计数。EMNLP 2026 官方[主会接收论文页](https://2026.emnlp.org/program/main_papers/)当前只有页面标题而无论文记录，因此主会逐篇覆盖继续 pending，不能据此断言没有相关工作。范围和限制见Phase208 报告及[结构化筛读日志](../sources/literature_screening_log_2026-10-08_colm2026_unseen_symbol_generalization_phase208.json)。

## 2026-10-08：大规模 source-linked autoformalization 与依赖图审计（Phase212）

| 工作 | 方法与论文内证据 | 与本项目的边界 |
|---|---|---|
| [AutoformBot: Formalizing Mathematics at Scale](https://arxiv.org/html/2605.29955)（NeurIPS 2026 官方目录列题） | 26 本开放教材→45,000+ Lean 声明；源文本到 Lean provenance；task DAG、declaration dependency graph；faithfulness/proof-integrity/code-quality 三 rubric 与独立 LLM judges。专业数学家审查一本文本时发现占位 axiom、假设偷渡式 mismatch、source/formal statement 偏差和 Lean 版本不匹配。 | 通用 source-linked autoformalization、形式声明依赖图审计与忠实度/完整性分轴都已有先例。它不做 sense-specific WordNet lexical relation、逐 gloss-span→typed Horn support 或 AND/OR witness source replay；非 matched baseline。 |

SpecBridge 也出现在官方题录，但当前官方 poster 页面不可取、作者全文未找到，故只登记为待复查题名。AutoformBot 的人审证据是单本书定性反馈，不是大规模 judge 校准。项目若未来获批开展 Track A，应另测人工 gloss-span gold，并分别报告方向/类型/组合结构和 proof replay。见Phase212及[结构化日志](../sources/literature_screening_log_2026-10-08_neurips2026_autoformbot_phase212.json)。

## 2026-10-08：形式化证据前的语义忠实度 gate（Phase211）

| 工作 | 方法与论文内证据 | 与本项目的边界 |
|---|---|---|
| [FaithSieve](https://arxiv.org/html/2608.26310)（官方 NeurIPS 2026 Downloads 目录列出） | 将自然语言数学证明拆成 EdgeUnits/typed obligations，经语义 gate 后使用 Lean；保留 `passed/refuted/inconclusive`。两名专家盲审 135 条 statement：gate 接受 105/115 条人审忠实语句，也接受 13/20 条人审不忠实语句（FPR 65%）。 | 局部 obligation、formalization fidelity gate、人工校准和 abstention 均有明确先例；gate 不等于语义保证。它不验证 WordNet sense-specific gloss spans 对方向性 typed Horn literal 的支持，也不是项目 matched baseline。 |

因此，未来项目若开展 Track A，应将 source-span semantic support、公式/类型检查、proof replay 和下游效用分开报告，并以独立 adjudicated gold 评估 gate 误报/漏报。此为评估建议而非已冻结协议；Track A 设计仍未获确认。单篇定向全文筛查，不是 NeurIPS 2026 全集审查或新颖性证明；详见Phase211和[机器日志](../sources/literature_screening_log_2026-10-08_neurips2026_faithsieve_phase211.json)。官方目录只核实标题列入，检索条目未公开 track 标签。

## NeurIPS 2026：结构化来源忠实度生成近邻（Phase232）

| 工作 | 最近的方法/评测 | 与本项目的边界 | 对照优先级 |
|---|---|---|---|
| [LogicTree-RAG](https://arxiv.org/html/2609.30943v1)（Zhu et al., NeurIPS 2026；arXiv 标记 accepted） | 研究论文→source-retrieval-grounded hierarchical logic tree→长文专利生成；节点关联生成文本和检索证据 spans。附录 G.3 用 GPT-5 judge 并对 20 个随机测试 case 人审 `fully/partial/unsupported`；另由 3 位专利从业者对 10 个文档作盲法 pairwise 质量比较。 | 已有一般 logic-tree 生成、源证据 span 绑定及 evidence-support 人审先例；不能主张这些一般机制首次出现。论文未做 WordNet sense/relation、gloss→typed AND/OR Horn literal、逐规则 source-span adjudication 或 Horn proof-certificate replay。20-case 人审和 LLM-judge 结果不是 lexical gold，也不是本项目的可比效果。 | 高：必须从一般结构/来源忠实度创新收窄至 sense-specific directional rule support、精确 AND/OR 语义和可回放 formal proof；这些差异目前仍为研究假设。见Phase232报告及[机器筛读日志](../sources/literature_screening_log_2026-10-08_logic_tree_rag_neurips2026_phase232.json)。 |

## ACL 2026：可控逻辑 verifier 与跨表述评测（Phase249）

| Work | Task and evidence checked | Relation to this project | Limit / non-comparability |
|---|---|---|---|
| [SATQuest (Zhao et al., ACL 2026)](https://aclanthology.org/2026.acl-long.96/) | CNF-native 生成 SATDP/SATSP/MaxSAT/MCS/MUS，并以 PySAT 核验结构化二进制答案；沿实例、问题类型、Math/DIMACS/Story/DualStory 格式控制评测。官方全文含 140 对评测 CNF、3,000 对 RFT 数据及一项 80-instance LLM-judge failure audit（10% 人工抽查）。 | 明确先例：可验证逻辑评测器、多个受控问题/表述维度和 solver-backed reward 不是单独新颖点；表述变化也可能造成逻辑能力评测差异。 | 范围是合成命题 CNF 与封闭答案格式；明确不含一阶/模态逻辑、multi-tool 或开放式自然语言。没有 WordNet sense/release、gloss-span→literal support、typed Horn/AND-OR 来源链或 witness provenance。failure audit 不是人工语义 gold；不是本项目 lexical matched baseline。详见Phase249报告及[日志](../sources/literature_screening_log_2026-10-08_satquest_acl2026_phase249.json)。 |

## Phase 217：邻接工作对评价构念的约束

| 工作 | 已核证内容 | 与本项目的边界 |
|---|---|---|
| [FRANQ](https://aclanthology.org/2026.findings-acl.338/)（Findings ACL 2026） | 区分外部 factuality 与 claim 对检索上下文的 faithfulness；长文本评测含 76 个问题并抽样人工核验自动标签。 | RAG context support 不是逐 gloss-span 对 WordNet sense-bound typed Horn literal 的人工 entailment gold。 |
| [When Does Meaning Backfire?](https://aclanthology.org/2025.starsem-1.16/)（*SEM 2025） | MNLI/HANS 的 AMR 条件显示结构输入可能放大表层差异；特定提升不等同于更深语义推理。 | 不能推断本项目图增强有同样效果；需表层匹配实验。 |
| [How Language Models Conflate Logical Validity with Plausibility](https://aclanthology.org/2026.findings-acl.454/)（Bertolazzi et al., Findings ACL 2026） | 全文：1,280 syllogisms / 64 逻辑形式 / 10 组 taxonomy triples，按逻辑形式 70/30 split；同十组 triples 另做 180 条 hypernym/hyponym control。作者报告 validity/plausibility direction cosine .48–.64、validity/hypernymy .10–.13；CoT 与 task-difference steering 降低其 syllogistic content-effect。 | 明确的 plausibility/validity content-effect 与 activation-steering 先例，排除该宽泛新颖性。不是 WordNet gloss-span gold、typed Horn support 或 proof replay baseline；未报告词汇 triple-disjoint split，不能声称词汇泛化。仅作为项目独立 content-effect diagnostic 的方法邻居；本项目还未测得该偏差。见Phase269 全文审读。 |

筛读边界见Phase217报告。

## 证明质量、source support 与证据链可用性

| Work | Task and evidence checked | Relation to this project | Limit / non-comparability |
|---|---|---|---|
| [ProofRank (Petrov et al., 2026)](https://arxiv.org/abs/2605.10379) | Full-text v2: 382 道高中竞赛终答案题；将质量拆为简洁性、计算便利性、认知简洁性、多样性、方法适应性。前三项只在双方正确且论证完整时做比较；报告人工一致性检查及 correctness verifier 失误审计。 | 收窄“correctness/replay 即足以说明 proof quality”的宽泛主张。项目 witness 的节点/依赖/最小性可描述形式证据链结构；若论证可读性或下游可用性是目标，需要单独定义读者、任务并做人评。 | 数学竞赛 proof-quality proxies 不评 WordNet sense identity、raw-gloss span→typed Horn support 或 source-bound witness replay；不能作为项目 matched baseline。作者人工样本有限且标注者相互熟悉；reported results 未由本项目复现。NeurIPS 官方 Downloads/Poster 页面列题，但 arXiv v2 评论写明 ICML 2026 AI for Math workshop 接收，具体 NeurIPS track 与两条记录关系未判定。见Phase270及[筛读日志](../sources/literature_screening_log_2026-10-08_proofrank_phase270.json)。 |
