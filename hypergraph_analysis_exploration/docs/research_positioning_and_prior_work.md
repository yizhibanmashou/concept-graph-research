# 既有 AAAI2027 稿件与新研究定位

状态：内部研究定位备忘录；初稿 2026-10-04，最近更新 2026-10-08（Phase270）。本文对匿名 `AAAI2027.pdf` 的历史描述仅沿用此前内部定位审计；Phase168 没有打开或复制该 PDF。用户已明确说明该稿件不是其成果；本备忘录不将稿件贡献归给用户，也不将其当作可公开引用的发表论文。

## 使用边界

`AAAI2027.pdf` 封面标注为匿名投稿稿，并明确禁止分发、引用或公开分享。当前仅将其作为私下研究材料，用来识别已有工作与版本差异。不得把稿件正文、补充材料或专有结果纳入公开仓库、论文、演示或外发标注包；任何对外使用前都需要权利人确认投稿状态、贡献归属及许可。即使后续获准引用，也须按实际作者和正式出版状态准确署名，不能暗示用户完成了该稿件中的工作。

## 稿件已经报告的工作

按稿件摘要、贡献列表和结果章节，既有工作已经报告：

- LexiCompile：从词典释义恢复定义逻辑、论元上下文和义项依赖，并将接受的结构投影为保留 AND/OR 的正 Horn 程序；EntranceRefine 在人工语义审查后迭代修订入口。
- 最终冻结程序：110,425 个 head、154,206 条 clause、85 个全覆盖且经逐项删除验证的 inclusion-minimal entrances；稿件明确没有证明全局最小基数或唯一性。
- Tree-MDL：在 3,057 个候选库存上分析 witness replay 成本与记忆编码成本，并报告候选 hub spectrum；作者将其界定为计算模型，不是测得的人类认知成本或习得顺序。
- 人工与 held-out 评估：稿件报告 400 条编译阶段专家判断、200 条生成定义后审计，以及 1,000 个 held-out sense 的连接结果（884 个仅经 OEWN inventory 路由，116 个需要外部词汇资源中介）。这些数字仍属于该匿名稿件的报告，未经本仓库独立复验。

因此，“从 WordNet 定义自动构建 AND/OR Horn 图”“85 basis 覆盖约 11 万义项”“witness 路径”“Tree-MDL hub”“基于人工复核的入口修订”和“held-out 义项可连接”都不能作为本项目的新贡献，也不能把稿件实验写成本用户成果。

2026-10-05 又补入三项早期直接先例：Bond et al. (COLING 2004) 以 HPSG/MRS 从日语词典定义抽取词汇本体关系；Moeljadi & Bond (GWC 2016) 从 Wordnet Bahasa 定义 head 抽取词汇关系；Almiman & Ramsay (RANLP 2017) 将 WordNet/词典定义改写为带方向的自然语言推理规则，并对样本做人类 meaning/grammar 判断。它们分别收窄“定义→语义表示/本体”“WordNet gloss→层级关系”和“定义→方向规则+人工验证”这些宽泛主张。COLING 2004 的 Goi-Taikei 类层级比较不是 gloss-span 支持金标准，MRS 抽取也不能等同完整 Horn 编译或独立证明证书。故当前研究假设应限于有版本和义项身份的 claim、逐条 gloss-span 支持判断、完整有类型 AND/OR Horn 语义及独立 proof/unknown 重放；这些都必须经新增方法对照和真实双标 gold 验证，不能因冻结包已有 AND/OR 结构而声称已实现或有效。筛读依据及 Almiman & Ramsay 文献内部 recall 数值不一致记录见[专门日志](../sources/literature_screening_log_2026-10-05_definition_to_rules.json)。

2026-10-06 对 ACL 2024 的 [MALLS / LogicLLaMA](https://aclanthology.org/2024.acl-long.375/) 做官方全文复核后，NL→FOL 翻译、大规模公式数据、语法过滤、1K 人工质量评估及错误类型驱动过滤均应视为已有方法。该论文不使用 WordNet gloss、不判词汇关系方向、不标原始定义 span；因此不能当成项目 gold 或匹配性能结果，但可指导适配式翻译基线和错误分层。其人工评估 92.8% correct 的过滤后比例是作者在自身生成语料上的报告，不能外推为本项目的预期精度。筛读边界见[机器日志](../sources/literature_screening_log_2026-10-06_malls_nl_fol.json)。

2026-10-06 对 EMNLP 2024 [Unigram-FOL](https://aclanthology.org/2024.emnlp-main.301/) 的全文筛读进一步细化了“合成形式验证”的边界：context-sensitive grammar 可配对生成简化英语和 TPTP 公式，solver 与 Vampire 能为形式问题给标签/证明；但论文未做人审，且没有验证真实 gloss 的 source-span 对齐。若借鉴，只应用作逻辑引擎压力测试，不作 WordNet 释义金标准或源语义有效性的证据。[筛读记录](../sources/literature_screening_log_2026-10-06_unigram_fol.json)。

2026-10-06 还全文核对了 [Diff-Comb Explainer](https://aclanthology.org/2024.lrec-main.40/)（LREC-COLING 2024）：它已在 WorldTree 上用 ILP 选择解释子图，并将答案准确率、解释精度、一致性与 answer/explanation faithfulness 分列；但后者不是规则对来源的蕴含验证，且背景依赖含 ConceptNet `is-a`。应将它纳入证据图与评测设计邻居，不能把“ILP + explanation graph + faithfulness metric”作为宽泛新颖性主张，也不能直接迁移其结果。[全文筛读日志](../sources/literature_screening_log_2026-10-06_diff_comb_explainer.json)。

宽泛创新表述还要受以下直接先例约束：[COLLIE-V](https://aclanthology.org/2020.lrec-1.396/) 已从 WordNet gloss 自动诱导带嵌套 AND/OR 的 entailment axioms，并有双人语义评价；这是 WordNet gloss→组合公理的重大直接碰撞。[BMEAUT](https://aclanthology.org/2020.semeval-1.15/) 已从 Wiktionary 定义建 4lang 语义图并与 WordNet 合并用于 lexical entailment，是定义图→词汇蕴含的直接先例。因而可检验的研究假设只能集中于同一 sense/release 与逐条来源 span 绑定、整体方向性规则支持及可独立重放的证明/反例能否带来测得的改进，不能声称这些差异目前已构成新颖贡献。代码与资源检查显示 BMEAUT 的 MIT 旧版代码可固定到公开 SemEval 分支提交，但依赖旧运行环境和外部释义/测试下载；COLLIE-V 公开资源和工具链不能据现有公开材料确认论文 induction 流程可端到端重跑。故它们目前分别是“可尝试适配、尚未复现”和“资源对照可行、induction 复现待核实”，不是已有 matched baseline。复现门槛与指标见[逐项对照](closest_work_comparison.md#复现适配可行性门槛2026-10-06)及[全文核读日志](../sources/literature_screening_log_2026-10-06_acl_wordnet_direct_2020.json)。

2016–2019 固定 ACL 候选切片补筛后，另一条必要边界是：WordNet gloss 内部角色/句法模式已有人工分析（Silva et al., CogALex 2016）；WordNet 定义也已作为上下文 NLI 模型的外部知识（Nishida et al., RepL4NLP 2018）；Gloss Corpus 的上下文义项标注同样早有资源工作（Rademaker et al., GWC 2019）。唯一在该候选切片被题名/摘要判为直接定义→方向规则生成的是 Almiman & Ramsay 2017，且已在先前全文日志中核读。故“组合这些单项组件”不足以确立增量；联合来源支持标注与可回放证明是否提供独立价值仍须共同 gold 和 matched baselines 验证。[切片筛查与两篇全文追读记录](../sources/literature_screening_log_2026-10-06_acl_wordnet_direct_2016_2019.json)。

对同一固定候选库 2023 年 pending 切片的摘要筛查未发现新的直接定义→形式蕴含工作，但命中释义数据增强 WSD、WordNet 关系预测和 hypernymy 结构修订等近邻。这些结果补充了应比较的任务类型，不足以支持关于其全领域新颖性的否定结论；见[2023 筛查日志](../sources/literature_screening_log_2026-10-06_acl_wordnet_direct_2023.json)。

## 稿件快照与本项目冻结包不是同一已证实版本

两者 headline counts 相同，但关键结构统计不同：

| 指标 | 匿名稿件报告 | 当前冻结包复算 |
|---|---:|---:|
| heads / clauses / basis | 110,425 / 154,206 / 85 | 110,425 / 154,206 / 85 |
| dependency literals | 917,248 | 917,767 |
| maximum witness depth | 404 | 396 |
| basis 单删覆盖损失（min / median / max） | 28,263 / 108,499 / 109,954 | 21,002 / 108,251 / 109,939 |

稿件另报 15,608 个 cycle vertices；当前项目投影审计得到 15,623 个循环分量节点。当前包 semantic fingerprint 为 `6a26db5de732d90e7eb1ae700eec5c6f34e9c28fa83f35d2eb616c6abb8d4e41`。相同计数不能证明规则版本相同；在拿到稿件版本的规则文件、精确 fingerprint 定义和构建配置前，不得合并统计、声称复现稿件、或把当前包结果归给稿件作者/用户。

当前项目可准确表述为：对收到的一个独立冻结包做结构审计、证书回放、来源文件完整性审计与压平消融。Phase 21 量化此包中普通图松弛造成的结构信息损失；这是对给定 snapshot 的新分析，不等于语义有效性验证或已证明的新颖方法。

## 可发展的新研究问题（假设，尚非贡献结论）

较有希望的研究方向不是再做一遍 basis recovery 或 graph construction，而是对**形式化输出是否被原始义项定义支持**建立可审核、可对照的实证链：

1. 以固定 release、sense identity 与 raw-gloss span 为单位，双人盲标必要/充分/双向/典型属性/不支持/不确定，并保留有类型 AST、AND/OR、scope 与 omitted content。
2. 将每个有方向的 rule claim 绑定 source span、WSD 和文件哈希；独立区分 source support、AST/类型合法性、编译保持、proof replay 及 NLI 判断。
3. 对 `proof / finite-program countermodel / unknown` 路由做 sense/lemma-disjoint 评估，使用真实人工 gold 测 soundness、coverage、abstention、校准与错误归因，而不把闭包可达性当作自然语言蕴含。
4. 在匹配样本上比较词面和 sememe-tree 定义基线、直接 NLI、LLM autoformalization+solver、普通图松弛及保留 AND/OR 的方法；控制 release、sense、source 与候选预算。

这一路线能否形成论文贡献，取决于广泛相关工作检索、直接可比 baseline、双人标签质量及实测增益。稿件已包含 definition compiler、专家检查、入口 refinement、witness/Horn 验证和认知解释，因此仅把这些模块重新串起来、增加 NLI gate 或换一套结构图都不足以构成 novelty claim。现有 `/2` pilot 只是未标注任务包；尚无真实双标、裁决、语义 gold 或 NLI 模型评测。

### 2026-10-07 Phase 49：把核心差异收窄为可证伪假设

把目前最重要的实证假设写为：在同一获准、sense/lemma/source 隔离的裁决候选池和相同生成预算下，source-only 的 gloss→有方向规则→AND/OR Horn→证据/证明路由，相比预先指定且可复现的强基线，能否在同等 source-support 风险下提高覆盖，或在同等覆盖下减少不受支持/方向错误输出。主要终点应是经盲审 source-support gold 上的风险—覆盖比较；NLI relation、WordNet relation、形式有效性、公式/方向正确性与 proof replay 分项报告，不合并为“准确率”。

次要假设是：保留 AND/OR 是否比简单图压平更能保护整体公式/方向判断；证据与回放是否改善盲审者错误定位且不增加错误接受。若结构只提高 replay、未提高整体语义/来源支持，不能据此声称语义收益；若证据回放可复算但人工审阅效果未测，也不能声称提升可审计性体验。判据表已写入[验证与评测协议](claim_verification_evaluation_protocol.md#可证伪的研究假设与判据预注册前草案)。效应阈值、主比较、区间与多重比较处理需要在合法 pilot 后、揭示 test 标签前锁定；当前无 gold/基线结果，故 H1–H3 均保持未验证。若充足精度下主要比较与基线无差异或更差，应撤回/收窄增量主张；权限、gold 或共同基线不足则是不可判定，不作支持性结论。

## 相关工作扫描后的基线分层（2026-10-04，仍属定向 scoping）

近期补充进一步表明，基线不能只放“简单图 vs Horn 超图”。建议按任务层次组成同一批盲标 sense/claim 样本上的比较矩阵：

| 层次 | 至少比较的路径 | 主要可回答的问题 |
|---|---|---|
| 词汇资源/释义关系 | WordNet 原生 taxonomy 与 lexical links；WordNetGraph；AI-WordNet；SememeLP 与 SememeLRM（ACL 2026，从定义预测/构造 sememe tree，再做 lexical relation / entailment） | 义项链接和关系预测是否优于现有资源/释义方法；是否保留原始 gloss 的分支与来源证据。SememeLRM 已覆盖定义→结构化语义→词汇关系的宽泛路径，不构成 source-span/typed-Horn baseline |
| 神经表示与逻辑组合 | ICLR 2026 Lattice Representation Hypothesis（WordNet hierarchy 上的 embedding/FCA meet/join）；HiCEM（ImageNet labels 由 WordNet hypernym hierarchy 派生，支持层次概念干预）；Moreira et al. KDD 2026 subspace embeddings（WordNet hierarchy、HyperLex、SNLI、零样本 AND/negation；soft logic 为近似） | 表示几何能否恢复层级/概念组合；与显式 gloss-derived rules、来源证据和 proof replay 的任务边界是什么 |
| 语义形式化与 prover | 直接 LLM typed-rule/JSON；ACL 2025 Entailment-Preserving FOL/EPR；TACL 2025 FoVer；ACL Findings 2025 NL2FOL；Findings ACL 2026 FOVER（PRM 训练标签）；ICLR 2025 LLM-TH typed hyperresolution；NALOMA 2026 Neural DTS 的 WordNet hypernym axiom + DTS prover；AKBC 2026 已接收的 lex-NLI→LangPro；适配后的 NLI→FOL→prover；SLR 风格合成 Horn checker stress set | 形式化和 prover 是否增加方向正确、source-supported 的规则，而非只增加可执行性或标签保持；EPR 只能作下游 label-preservation 指标，不能代替逐 gloss 的语义标注。LLM-TH、Neural DTS 与 AKBC lex-NLI 已展示 NLI/学习型/LLM 词汇知识进入 proof search，不能把这些宽泛组合称新颖。可检验差异假设仅是 source-only 证据约束、sense-linked gloss span 支持、有类型方向 AND/OR 定义规则与独立证书重放。SLR 只适合作为合成逻辑引擎校验/复杂度控制邻居，不能用其闭世界样例代替 gloss-support gold |

证明系统的 producer/checker 分离也有跨域先例：[Generating and Checking DNN Verification Proofs](https://proceedings.neurips.cc/paper_files/paper/2025/hash/5f326d2e040a20d52438873f5d727e58-Abstract-Conference.html)以 APTP 二叉 case tree 与独立 checker 验证 DNN 不可满足性。它不能支持 gloss 语义忠实度，但意味着本项目不能单独把可重放证书、小 checker 或 proof mutation tests 当作新意；还需测 source-linked rule support 的增量价值，并明确 checker 的可信边界。见Phase240全文筛读。
| 证明/解释结构 | 普通依赖图投影；自然逻辑 entailment tree；TableQA 的 AND/OR Evidence Tree（EnoTab，非形式证明）；保留 AND/OR 的 Horn proof DAG | 前提覆盖、分支/方向正确性、证书重放率、证明规模及成本 |
| 选择性判断与一致性 | direct NLI；带 verifier 的 selective route；方向可逆样例的反向最小对 | 风险—覆盖与校准；预测能否随方向改变而保持 gold 一致，而不是只看 self-consistency |

各层需复用同一 sense-disjoint / lemma-disjoint 切分、输入预算与人工裁决标签；结果分别报告 relation correctness、gloss-span support、结构/编译合法性、proof replay、NLI gold accuracy、abstention 和成本。ACL 2025 的 [Entailment-Preserving FOL](https://aclanthology.org/2025.acl-long.286/) 是直接的 NL entailment→FOL/prover 对照，其 EPR 指标可作为标签保持诊断但不是源句公式忠实度；[FoVer](https://aclanthology.org/2025.tacl-1.61/) 是 NL→logic→Z3 对照；ACL Findings 2026 的 [FOVER](https://aclanthology.org/2026.findings-acl.403/) 用 Z3/Isabelle 检查已形式化轨迹并生成 PRM 标签，但不验证 premises 是否忠实于原始文本，PRM 排序也不是 proof certificate replay；Findings IJCNLP-AACL 2025 的 [NL2FOL](https://aclanthology.org/2025.findings-ijcnlp.8/) 是 FOL/SMT 与反模型路线；LREC 2026 的 [PhrasIS 方向一致性研究](https://aclanthology.org/2026.lrec-1.423/) 只启发方向反转诊断。不同任务标签和输入均须重做 matched evaluation，不能直接引用其分数作为本项目基线。ACL 2026 的 [SLR](https://aclanthology.org/2026.acl-long.16/) 可补充为可控合成 Horn 推理/验证器压力测试的设计邻居；它的干净单规则 ILP 与闭世界 judge 不测试自然语言 source support。筛读边界见[定向日志](../sources/literature_screening_log_2026-10-05_acl_slr.json)。FOVER 的全文筛读及 scope 边界见[2026-10-06 机器日志](../sources/literature_screening_log_2026-10-06_formal_verification_prm.json)。

此轮只增加了定向候选和官方来源核查，未形成可复现的穷尽式数据库检索，也未读完每项相关工作的附录/代码。尚无证据证明组合假设新颖；当前可用表述仍是“候选研究问题/待检验假设”。具体查询与 PhrasIS 全文筛读边界见 [2026-10-04 定向筛读日志](../sources/literature_screening_log_2026-10-04_directional_nli.json)，其他候选的逐项状态见 `docs/closest_work_comparison.md` 及此前日志。

### 自动形式化中 verifier 与 source-faithfulness 的边界

ICLR 2026 ProofBridge 把 Lean type checking、受限 tactic 的双向等价证明与 LLM repair 组成验证循环；在作者设定内，这是比 parser 成功或 LLM judge 分数更强的形式证据。但其 equivalence target 是参考 Lean theorem，且作者明确假设该 reference faithfully translates the NL theorem。由此得到的可迁移方法结论是：必须把 `formal-program validity`、`equivalence-to-reference` 与 `source-to-reference faithfulness` 分开报告。对于本项目，外部 OEWN/WordNet hypernym relation 或已形式化的 reference clause 也只能作资源/形式对照，不能代替盲审 gloss-span support gold。[ProofBridge 全文筛读记录](../sources/literature_screening_log_2026-10-06_proofbridge.json)。该单篇对照不说明本项目方法新颖或有效。

### 证明与人工蕴含评测的新近边界

GFaiR (LREC-COLING 2024) 已在带平行 FOL 标注的自然语言规则任务中检查推理步骤，RDTE/TREEWISE (EMNLP 2024) 已对递归 QA 分解制定多维人审并评估树完整性；因此“有 proof trace verifier”或“人工评判分解蕴含”均不能单独作为新贡献。可继续检验的范围应要求 gloss-origin、sense/release/version 与 span 的逐规则绑定、方向性 source-support gold，以及独立重放 source-only AND/OR Horn 证书。GFaiR 的步数封顶与 RDTE 的上下文 sufficiency 还分别提示：搜索预算超限必须与语义 Unknown 分列，contextual argument sufficiency 必须与 gloss-only support 分列。项目尚无实证证明这些设计效果或新颖性；详细筛读见[日志](../sources/literature_screening_log_2026-10-05_logic_proof_and_decompositional_nli.json)。

### ACL 2026 RGCWM 对宽泛规则图主张的约束（Phase 45）

RGCWM 已在 ACL 2026 主会将规则间 typed pairwise dependency graph、动态规则证据状态、rollout 和图传播用于规则遵循。因此“显式规则依赖图/状态跟踪/图传播”也不应作为独立新贡献。RGCWM 的模型估计不等于形式蕴含或 source-span 证书；但这个任务差别本身仍不能证明新颖性。后续贡献论证必须通过系统近邻检索以及合法来源上的 sense-disjoint 人工支持标签与 matched baseline 实验来建立。Phase 45 筛读和适用边界。

### v3 增量全文筛读对研究差异的收窄（2026-10-06）

13 篇全文优先候选已逐篇核读；其中结构边界最直接的是 ACL 2026 [EnoTab](https://aclanthology.org/2026.acl-long.1102/)，它使用显式 AND/OR Evidence Tree 表达 TableQA 条件并让每次 pruning 可检查/回滚，因此“AND/OR evidence tree”或“可观察树执行”不能单独称为新贡献。ACL 2025 demo [LCDS](https://aclanthology.org/2025.acl-demo.28/) 已将医学规则、来源相似度映射、句级归因与专家修订放在同一系统；NAACL 2024 [POLITICITE](https://aclanthology.org/2024.naacl-long.216/) 已提供多源 statement-support 子集和人工分级标签；ACL 2025 [CORRECT](https://aclanthology.org/2025.naacl-long.154/) 已将 evidence/context/reference 文档组织为异质图。这些仍不构成词典定义形式化的直接先例：EnoTab 树操作表格过滤，LCDS 规则不是形式蕴含校验，POLITICITE 不绑定词典义项或 Horn 规则，CORRECT 图用于 learned verdict prediction。

因此，唯一仍可保留为待检验差异假设的是**固定 WordNet/OEWN sense 与版本的 gloss-span 对方向性、多前提 Horn clause 的独立语义支持 gold，以及可重放 source-only proof/witness**。它不是已证实的新颖贡献：仍须完成全库/跨库系统检索、公开既有稿件与当前冻结数据的版本/归属核对，并在合法取得的双人裁决 gold 上与多源 NLI、定义形式化和逻辑推理基线作 matched evaluation。新增逐篇范围、方法和限制见[ACL 增量筛读日志](../sources/literature_screening_log_2026-10-06_acl_expanded_delta.json)。

### 2026-10-07 最新定义—词汇解释—形式证明近邻复核

两项近邻进一步收紧上述差异假设。de Jong et al. 的 lex-NLI（AKBC 2026 已接收；截至 2026-10-07 仍为 arXiv v1，workshop 尚未举行）从 SNLI/SICK premise–hypothesis pair 预测多参考有向 lexical-entailment set，再将生成关系交给 LangPro；它已经结合结构化词汇解释、人审多解 gold 与形式证明。因此“结构化 lex explanation + gold + prover”不应作为本项目创新主张。Wang et al. 的 SememeLRM（ACL 2026 主会）从 definition 预测/构造结构化 sememe tree，并评 lexical relation classification / entailment；因此“从定义抽取结构化词汇语义并用于 lexical relation”也已有直接先例。[ACL Anthology 官方记录](https://aclanthology.org/2026.acl-long.224/)、[AKBC 官方接收论文/日程](https://www.akbc.ws/2026/)与[AKBC 论文 arXiv v1](https://arxiv.org/abs/2609.32491)已核对发表状态和任务单位。

两者与本项目的边界是**输入、目标和证据单位不同**：lex-NLI 的输入是句对，lex set 是解释该 pair 的 context-specific 词汇关系，不要求每条关系被单条词典 gloss 的字符 span 支持，也不等于完整证明；SememeLRM 学习 definition-based sememe tree / relation prediction，不产出带独立 soundness certificate 的 Horn entailment。故可能的项目问题只能窄化为：在同一固定 WordNet/OEWN sense/release 上，人工能否裁决每条方向性 typed AND/OR Horn literal 是否被原 gloss span 支持，并独立重放 source-only proof/witness；该问题的增量效用与新颖性仍须用 matched baselines、盲审 gold 和跨库检索证明，目前均未证实。筛读与数字边界见[AKBC 2026 结构化日志](../sources/literature_screening_log_2026-10-07_lex_nli_formal_proofs_akbc2026.json)、[SememeLRM 矩阵条目](closest_work_comparison.md)和Phase 103 报告。

### Phase 166–167：2026 新近 WordNet-gloss 与 autoformalization 边界

ACL Anthology 2026 的 LKG Latin 工作已将 sense gloss 与已有 WordNet hypernym graph 用于 contextual WSD；CEFR-Annotated WordNet 已用 LLM 比较 WordNet gloss 与外部词汇释义并转移 sense-level labels。故“WordNet + gloss + LLM sense prediction”及宽泛的 gloss-to-sense label transfer 不应作为新论文独立贡献。两者未给出 gloss-span 到方向性 typed Horn literal 的 gold，亦无 source-only proof replay；CEFR 标签也未人工逐项 spot-check。筛读边界见Phase166报告与[机器日志](../sources/literature_screening_log_2026-10-08_acl2026_wordnet_slice_phase166.json)。

AAAI 2026 又有固定 ontology/gloss 下 NL→FOL + SMT equivalence 和逻辑扰动评测、选择性形式化与反向推理、数学 autoformalization，以及法规文本到 Prolog 执行/拒答的先例。因此这些宽泛方法同样不能单独作为新贡献。它们与匿名 AAAI 2027 稿件是不同的外部 prior-work 记录；均不得归为用户成果。AAAI 2027 材料仍受匿名稿件自身的禁止分发/引用/公开分享声明约束；AAAI 2026 与 ACL 2026 只按可公开官方记录引用。筛读范围见Phase167报告与[机器日志](../sources/literature_screening_log_2026-10-08_aaai2026_formal_logic_neighbors.json)。

截至 Phase168，本项目保留的候选差异仍只是待验证假设：固定 OEWN/WordNet release 与 sense identity 下，人工能否裁决 raw-gloss span 对方向性 typed AND/OR Horn rule 的支持，并将使用的事实绑定到同一 source payload 后独立 replay。还没有这类项目 gold、共同切分 matched baseline 或效果证据；当前冻结图复算、结构证书和 NLI 原型都不能替代它们。匿名稿件的作者贡献、稿件状态和数据授权也未由本项目独立核实。

## 后续工作门槛

- **基线与归属**：获得可使用既有稿件/数据的授权及清晰贡献归属；独立列出其功能、评测和数据与本项目之间的差异。
- **版本对齐**：请求上游提供稿件 snapshot 与当前冻结包的可核对版本映射，解释 literal/depth/deletion/SCC 等统计差异。
- **语义证据**：在核实任务材料可由标注者合法使用后，完成双人 blind annotation、裁决和一致性报告；许可不明确前不外发含释义的任务、答案键或冻结来源。
- **独立性检验**：依据人工 gold 跑 matched baselines、消融、sense/lemma 分组评测与错误分析。若没有真实 gold 和可比基线，只能报告研究假设与工程原型。
- **文献审计**：扩展当前单人、定向 scoping review；在完整检索式、去重候选集、纳排日志和直接方法比较形成前，不做“首个/新颖”的断言。

本备忘录用于约束当前项目的归属和新颖性表述，不是对匿名稿件科学结论的独立复现，也不是发表许可意见。


Sileo 的 [Logic Haystacks (EACL 2026)](https://aclanthology.org/2026.eacl-short.3/) 将简化英语/FOL 生成扩展为长上下文矛盾证据定位：使用 Vampire 控制合并前提的一致性，并以删除反事实筛出唯一且必要充分的证据行。它提示本项目不能把证明引导的证据抽取、必要/充分证据识别或形式控制的长上下文干扰项单独写成新颖点。可借鉴的后续实验是假设性 stress slice：在人工裁决 gloss gold 上加入近似但不支持目标的释义/规则，再测 span 支持、删除必要性及证书重放；不得把合成 benchmark 结果外推为释义有效性。该文在冻结候选框之外被定向发现，故不属于原候选计数。[全文筛读日志](../sources/literature_screening_log_2026-10-06_logic_haystacks.json)。


2026-10-06 多证据检索增补检索命中 ACL 2025 ETS、COLING 2025 Counting-Stars 与 TACL 2026 Ev2R。ETS 已把证据句组合搜索建模为树并以 reader reward 指导 MCTS，因此不能将“超越逐句打分的组合证据搜索”笼统视为创新；Counting-Stars 已将多证据搜集、错误证据排除、位置与长度作为可控评测轴；Ev2R 摘要指出参考证据对齐与 verdict 支持可联合评估。它们均不处理 WordNet sense-linked gloss 到方向性 Horn clause 的语义忠实度或可重放形式证明。后续可检验的项目差异仍是来源定义本身的语义支持 gold 与显式逻辑结构，而非一般多证据检索。Ev2R 仅摘要核读；筛读状态和边界见[机器日志](../sources/literature_screening_log_2026-10-06_evidence_retrieval_supplement.json)。

### ICLR 2026 ProofFlow：proof dependency DAG 已有先例

[ProofFlow](https://proceedings.iclr.cc/paper_files/paper/2026/hash/5fce5198dbf92d5ff45f74504431e2ff-Abstract-Conference.html) 已在数学证明 autoformalization 中以 DAG 约束 lemma 依赖、用 no-DAG 变体作消融，并通过 ProofScore 合并图结构、语义评分与 Lean 编译结果。因此，本项目不得将 dependency-DAG-constrained formalization、结构忠实性评测或“编译正确之外也评语义/结构”单独包装为贡献。任务对象仍有差异：ProofFlow 的 DAG 节点是证明步骤；本项目的目标对象是 gloss-derived directed Horn clauses（AND antecedent 与 OR alternatives）及其 selected-witness derivation。图表示不同本身不能证明新颖；须在 source-span 支持 gold 和 matched baselines 上证明 sense/release 锚定、规则级支持标签及独立 source-only 证书重放提供额外实测价值。ProofScore 中语义/部分结构评价使用 Claude Sonnet 4，故它是 LLM-judge 评测近邻，不是独立 gloss-support gold。具体方法、benchmark、指标与边界见[官方 PDF 定向筛读日志](../sources/literature_screening_log_2026-10-06_proofflow_iclr2026.json)。

### Findings ACL 2026 SLKD：复杂度/密度指标已有先例

[SLKD](https://aclanthology.org/2026.findings-acl.436/) 从逻辑推理样例抽取谓词、常量和公式，按前提集合、单条推导链、操作符数与嵌套深度估计 reasoning-potential，并用来组织逻辑任务训练。故不能将一般逻辑密度评分、推导复杂度排序或密度引导的数据筛选单独表述为新贡献。本项目当前的 witness depth、OR alternatives、AND body width 和 basis usage 画像是冻结图的结构审计特征，尚非 gloss 语义复杂度预测；若要声称其能预测标注错误、支持质量或复核成本，需在 blind gold 上控制 gloss 长度、POS、歧义度与来源后进行分组外验证。[官方全文定向筛读日志](../sources/literature_screening_log_2026-10-06_slkd_findings_acl2026.json)。
2026-10-06 从固定 ACL v3 候选框优先筛读 RuleArena、LTRAG、MASA 与 NL2Lean/ReLean 后，新增边界是：真实自然语言规则的选择/应用评价、检索辅助 autoformalization、agent+prover 数学形式化、以及 compile 与语义对齐联合奖励都已有近期 ACL/EMNLP 先例。它们不构成 WordNet/gloss 的 matched baseline，但进一步排除把规则引导推理、RAG→形式逻辑→solver、自我修订、多智能体形式化或编译/语义双评估单列为 novelty。准确的差异假设仍必须落在 sense/release/source-span 标注 gold 和共同基线实测上；筛读边界见[逐项对照](closest_work_comparison.md)及[机器日志](../sources/literature_screening_log_2026-10-06_acl_2025_formalization_rule_neighbors.json)。


### 2026-10-06 Phase 31 补充：HalluTree 对证据链主张的影响

ACL Anthology 2025 New Frontiers in Summarization Workshop [HalluTree](https://aclanthology.org/2025.newsum-main.9/) 已将 claim decomposition、证据片段、层级 claim tree、extractive NLI、inferential natural programs 与逐步 LLM 检查结合。因此“用证据树/DAG解释多跳推理”不能单独作为宽泛创新点。它的 natural program 由 LLM 检查，并可包含未经来源核验的 background knowledge；项目可能的边界是固定义项/版本、gloss span 到方向性 AND/OR Horn support 的映射以及 source-only 可重放证书。该差异仍是待验证假设。详情见 `docs/related_work.md`、`docs/closest_work_comparison.md` 和 Phase 31 结构化筛读日志。

### 2026-10-06 Phase 40：IJCAI 2026 收紧规则学习与证明链主张

IJCAI 2026 NRI 在 Boolean/tabular examples 上执行 zero-shot DNF 规则归纳，VANESSA neuro-symbolic QA 已把 textual entailment、符号推理和 proof-tree explanation 接在同一路线中。因此“学习 AND/OR 规则”与“文本蕴含 + prover + proof tree”不可单独作为新贡献。对本项目仍可检验的边界只涉及义项/发布版锚定、gloss-span 对方向性多前提 Horn 规则的人工语义支持、以及受限 source-only 证明/反模型回放；这些构成研究问题，尚未证明新颖或有效。文献任务差异和评价限制见 [IJCAI 2026 筛读日志](../sources/literature_screening_log_2026-10-06_ijcai2026_logic_neighbors.json)。

### 2026-10-07 Phase 65：NLI proof-chain 邻居与验证分层

ACL 2023 PROVER 已从 premise/hypothesis 生成自然语言多步 proof，结合外部 commonsense retrieval，并由人工检查步骤；作者指出自然语言 proof 并无 formal axiomatic guarantees。[ReCEval](https://aclanthology.org/2023.emnlp-main.622/) 将链条视为 informal proofs，以 NLI 评步骤正确性、V-information 评信息增益。[SICCK](https://aclanthology.org/2023.nlrse-1.12/) 测试 hypernym、quantifier、negation、modifier 下的组合 NLI；FEVER retrieval、跨文档 verification、多证据聚合亦已有先例。由此需要明确拆分“自然语言 chain judged plausible”“NLI label”“proof checker 对给定规则集返回 valid”与“source span 语义支持每条 Horn rule”。建议同一盲标 split 上比较 PROVER/ReCEval-style chain、direct gloss-NLI、evidence retrieval upper bound 与 formal Horn replay；source-support 和 replay 作为独立终点。逐篇限制见Phase 65 报告及[筛读日志](../sources/literature_screening_log_2026-10-07_acl2023_nli_logic_proof.json)。

### 2026-10-07 Phase 66：强 proof/NLI 对照与任务边界

NLProofS (EMNLP 2022) 对 supporting facts 与 hypothesis 生成 proof tree，以独立训练的 RoBERTa valid/invalid verifier 评分候选步骤，beam/search 选择较高总分 proof；在 RuleTaker 和 EntailmentBank 报告步骤/事实/完整 proof 表现。其自然语言步骤 verifier 不是形式 theorem prover，也不把每个 fact 绑定到 WordNet gloss span。Dual-(m)T5 已从文本产生 PL/FOL，且把预测 logical forms 用于增强下游 NLI；Japanese CCG compositional semantics + Vampire 已做形式化 temporal NLI；ZS4IE 把 relation labels verbalize 成 hypothesis 并用 NLI 作零样本抽取。由此应将项目的 claim 拆成 (i) rule/formula fidelity to gloss, (ii) source-span attribution, (iii) static type/AND-OR structure validation, (iv) source-only proof replay, (v) NLI judgments。NLProofS、Dual-(m)T5、direct NLI、ZS4IE-style verbalization 和 premise retrieval 应适配到同一 blind gold；它们原任务成绩不可直接横比。逐项证据见Phase 66。

### 2026-10-07 Phase 87：Neural DTS 全文补核与 sense 聚合边界

复核已在 2026-10-05 录入的 Kobayashi et al., [Neural DTS (NALOMA 2026)](https://aclanthology.org/2026.naloma-1.2/) 官方全文后，确认它是高度相关的 workshop 方法先例，不是 ACL/ICLR 主会级别证据，也不是新发现。它用 WordNet synset hypernym edges 训练 order/Poincaré/hyperbolic-cone 关系模型，再将阈值通过的词汇 IS-A 分数动态注入日语 DTS `wani` proof search；集成评估仅 20 个向上单调性 PoC。独立 oracle 对表层词的所有 synset-vector pairs 取最大分数，故在缺少上下文义项约束时属于 any-candidate-sense 选择；这提示项目匹配 baseline 必须显式锁定 sense，避免把“任一候选义项成立”误报为目标 gloss 支持。此为对其聚合规则的设计风险推论，并非论文已报告错误。该工作没有从 gloss span 抽规则或提供 source-only support gold；详细证据增补见[筛读日志](../sources/literature_screening_log_2026-10-05_neural_dts.json)。

### KR 2026：proof support / provenance 是既有形式化对象

KR 2026 Main Track 的 [Why(-Not)-Provenance for Datalog with Negation](https://proceedings.kr.org/2026/19/) 以 proof trees/justifications 的输入事实 supports 解释 Datalog 输出，并为带否定程序给出 why- 与 why-not-provenance。这意味着本项目不得把 proof support、多个可行 witness 或 provenance-aware replay 作为独立新颖性来源。可检验的区分假设须转到**原始定义的来源证据**：特定 release/sense 的 gloss span 是否在语义上支持各条方向性、typed Horn literal；再将规则绑定到同一来源并独立重放 source-only witness。KR 论文不做这项自然语言支持判断；该边界仍需共同盲标 gold 和 matched evaluation 支持，尚非 novelty 结论。详见[Phase 133 结构化筛读](../sources/literature_screening_log_2026-10-07_kr2026_provenance_and_lexical_reasoning.json)。

KR 2026 的相邻结果进一步说明，“最小支持事实是否相关”已有查询解释复杂度研究，FOL 公式非等价解释与终止 proof-search decomposition tree 也有正式主会工作。它们分别解释数据库事实支持、形式公式差异和规则推导，不评价特定词典义项的原始 gloss span 是否蕴含方向性 typed Horn literal。筛查进一步压缩广义 explanation/support/certificate novelty；并未证明所剩的 sense/release-linked span-support 与 source-only replay 联合契约新颖或有效。范围与摘要依据见Phase 134。

EACL 2026 的 [CAP compositional robustness study](https://aclanthology.org/2026.eacl-long.214/) 用 WordNet gloss 做 inverse definition modelling（definition→term），并另测 word→hypernym，排除“LLM 未从 WordNet gloss 恢复词项”或“未测试 WordNet 上位词预测”的宽泛主张。它没有验证 gloss span 对方向性 typed Horn literal 的支持；CAP accuracy drop 仅针对干预前答对的子集。新定位须与 gloss-to-term、gloss-to-relation 分别匹配，不能把条件鲁棒性数值当 source-support 或逻辑推理结果。该论文在原 ACL 候选框缺失，提示检索词需扩充；见Phase 135。

2026-10-08 对 ACL 2026 Ye et al. *Teaching Language Models to Check Grounded Claim Factuality with Human Test-Taking Strategies* 的官方全文定向核查进一步收窄了方法主张：把复合 claim 拆成原子事实，按实体/属性/关系/推断步骤判断来源支持，并生成 rationale，已有 ACL 主会先例。它可启发同一 gloss-pair 输入上的分步 factuality prompt，但其长文档摘要/RAG 基准不包含 WordNet sense、释义 span→Horn literal gold 或形式证书重放。不能把该论文的 benchmark 分数或 token 降幅作为本项目证据；项目仍需自己的 sense-bound blind gold 和 matched baseline。范围与限制见Phase 142 深度报告和[机器日志](../sources/literature_screening_log_2026-10-08_grounded_claim_factuality_acl2026.json)。

### Phase 174：推理时 NL2FOL 纠偏不是来源语义验证

Findings ACL 2026 的 LSEG 以逻辑保持输入变体和 layer-wise entropy 做推理时隐藏状态干预，并用 FOLIO/MALLS logical equivalence 报告表现。它使“仅靠逻辑纠偏或公式等价提升”不能作为宽泛新颖性主张；同时，其任务不处理 WordNet sense、释义证据 span、外部来源使用权或 witness source lineage。本项目仍必须靠独立的 gloss-span 人工支持标签和 source-only replay 评估，不能把熵或相对参考公式等价提升当作语义支持。该发现为一篇定向全文筛读，非全会场审查或新颖性证明。见Phase174报告及[结构化日志](../sources/literature_screening_log_2026-10-08_lseg_nl2fol_findings_acl2026.json)。
### Phase 170：逻辑评测验证器与语义公式距离的新边界

CoNLL 2026 主会已把 LF execution、LF-conditioned fidelity、logic-type identification 与 LF-free generation 分轴，并通过有限的人审分析验证器假阴性与 off-LF-but-entailed 输出；这压缩“用 NLI/自动 verifier 一项分数衡量逻辑忠实度”的主张。NALOMA 2026 workshop 的 Presburger 模型集合距离又说明，形式公式可在可判定片段里做语义级比较，但其合成数学任务仍发生量词丢失，且不回答源释义是否支持规则。项目需独立报告 schema/type、logical consequence/replay、exact-condition NLI 和 gloss-span 人工支持；仍没有项目 gold、matched baseline 或效果/新颖性证据。见Phase170与[筛读日志](../sources/literature_screening_log_2026-10-08_logic_evaluation_neighbors_phase170.json)。

### Phase 177：结构引导生成与过程级确定性验证的既有先例

Findings ACL 2026 的 SELF-KBQA 已将结构化知识子图与语义排序用于可执行 logical-form 生成；COLM 2026 的 VPS 已将结构化 trace 与领域 verifier 用于过程监督。两者分别收窄“结构化图指导逻辑生成”与“一般过程声明可确定性核验”的宽泛新意。相应地，本项目窄研究假设必须把检验单位收紧到 release/sense-linked gloss span 是否支持各条方向性 typed AND/OR Horn literal，并测量 source-only proof replay 是否带来额外审计价值；条件差异本身不能替代匹配的人类 gold、基线和统计有效评估。当前仍无此项目实证。逐篇边界见Phase177报告和[结构化日志](../sources/literature_screening_log_2026-10-08_structural_kbqa_and_process_verification.json)。

### ACL 2026 KCR 对图路径与过程奖励主张的限制（Phase203）

KCR 已从互相冲突上下文构造 text/graph reasoning traces，并用 coherence/consistency reward 训练冲突仲裁模型；故“显式图路径+trace reward”不能单独作为贡献。该工作不是形式 proof verifier，也没有 WordNet sense-bound gloss-span→Horn support 或 source-only witness replay。项目只能把该差异保留为待匹配 gold 验证的假设。见Phase203 深度报告和[全文筛读日志](../sources/literature_screening_log_2026-10-08_acl2026_kcr_graph_reasoning_phase203.json)。

### NeurIPS 2026 LogicTree-RAG 对来源忠实度主张的限制（Phase232）

[LogicTree-RAG](https://arxiv.org/html/2609.30943v1) 已在专利草稿生成中使用层次 logic tree、节点级 source evidence spans，并以 GPT-5 judge 加 20-case human audit 评估 fully/partial/unsupported 支持状态，另有三位专利从业者的文档级盲审。因此，一般的“logic tree + 来源 span grounding + evidence-support 人审”不是本项目可主张的首创。其任务未覆盖 WordNet sense/release、逐条 gloss-span 对方向性 typed AND/OR Horn literal 的裁决或 Horn proof replay；这些只能保留为未验证的任务差异假设，须由 sense-disjoint 人工 gold 和 matched baselines 检验。筛读深度与证据限制见Phase232报告及[结构化日志](../sources/literature_screening_log_2026-10-08_logic_tree_rag_neurips2026_phase232.json)。

## 当前定位补记（Phase267–270，2026-10-08）

Phase267 全文审读 BPF/DriftBench 后，以下表述从本项目候选新意中排除：形式可证明与自然语言忠实度可能分离、使用 contrastive/drift probes、建立 controlled formalization-drift benchmark。该论文被作者归于 ICML 2026 workshop，未独立核实具体接收记录；作者实验数据未复现。Phase269 将 ACL Findings 2026 validity/plausibility 论文从摘要升级为全文：它在十组 taxonomy triples 上分析 syllogism content effect，并使用同批 triples 做 hypernym control；它不是 gloss-source support gold 或词汇留出基线。两篇工作的任务都不能证明本项目有相同效应，但进一步要求把 model plausibility、exact-pair NLI、resource relation、source-span support 和 formal replay 分开报告。Phase267 · Phase269

### Phase270 补记：证明质量是独立构念

ProofRank 将“正确之后还要比较可用性”操作化为五类数学证明 proxy，并报告了人工一致性差异与 verifier 漏步错误。因此项目中的形式 replay 和 witness 结构指标不可改称“证明质量”或解释效用。近期输出先用“可重放证据链/结构属性”描述；若增加可读性或效用主张，另行预注册读者、任务、维度、盲评和一致性分析。ProofRank 是概念/评测邻居，不是词典义项或 gloss-to-Horn 匹配基线；详细范围见Phase270。

Phase268 的源码审计确认旧 claim-review `/0.1` route 绑定 raw-gloss 与 rendered-premise 哈希，并以 premise 坐标验证 span；它缺 Track A 所需的 relation-edge/surface/condition keys 和独立 panel provenance。因此“现有 NLI/proof route 已支持 Track A 端到端评测”不成立。新增合同需在 estimand、总体、surface/POS、独立标注面板、统计单位、许可及责任 gate 冻结后再实施；旧路由只能作为 legacy 组件和哈希/校验模式参考。Phase268 报告与兼容审计

目前仍可检验但**尚未证明新颖或有效**的假设是：对固定 WordNet/OEWN release 与 sense，人工能否独立判断 raw gloss 的原始 span 是否支持每条方向明确、类型约束、保留完整 AND/OR 结构的 Horn literal/rule；把该判断与同一来源的 source-only witness/proof replay 绑定后，是否在共同盲标 gold 和匹配基线上带来可测的风险—覆盖或审计价值。当前冻结图 replay 支持结构与指定形式推导可复算的有限声明；typed checker 支持调用方声明的有限 type table；二者均不提供 WordNet 类型 ontology、词义消歧正确性或 gloss-support gold。没有双标裁决数据、IAA、真实模型输出、matched baseline 或冻结后的结果，故不写论文级准确率、效用或新颖性结论。匿名 `AAAI2027.pdf` 仍仅是内部 prior-work 边界，绝非用户成果。

### Phase273 新增：Findings ACL 2026 已有工程需求到可执行模型

Li et al. 的 [APF](https://aclanthology.org/2026.findings-acl.102/) 把自然语言工程要求形式化为可执行数学优化模型，并用 test-instance ranking 与下游天线优化评价流程。它进一步排除“首次 NL→executable model / 形式外部评价 / 执行效用”的宽泛贡献。其排名 reference 主要由 LLM 产生，30 组要求的人类 ranking 对照不是逐公式语义 gold；任务不含词典 sense、gloss span、typed Horn 或 source-bound proof replay。项目更窄的 sense/release-bound gloss-span support + replay 仍是待跨库核查与匹配 gold 实验的假设，不能从任务差异直接推出新颖性。见Phase273报告和[筛读日志](../sources/literature_screening_log_2026-10-08_apf_findings_acl2026_phase273.json)。
