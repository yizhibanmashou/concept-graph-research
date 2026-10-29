# 方法对象与实验协议

## 当前可验证对象

冻结包把每个 head `h` 表示为若干候选子句的析取；每个子句中的依赖共同成立：

```text
h := C1 OR C2 OR ... OR Ck
Ci := d1 AND d2 AND ... AND dm
```

给定冻结包标记的 basis 集合 `B`（这里只指规则文件中的结构基础项；不据此认定它们是语言学/认知意义的 semantic primes，也不据此认定全局最小），最小正 Horn 闭包按下式迭代：

```text
Cl(0) = B
Cl(t+1) = Cl(t) ∪ { h | some clause C of h satisfies C ⊆ Cl(t) }
```

当前冻结包的 85 个结构 basis 按节点元数据包含 37 个名词、23 个动词、8 个形容词、1 个卫星形容词、3 个副词和 13 个介词类节点；72 个属于 OEWN namespace，13 个为非 OEWN namespace。该异质构成见[basis 构成审计](basis_composition.md)，支持的是包内结构 seed 的描述，不支持将它们统称为语义原语或 sememe。

冻结包的 `coverage_witnesses.jsonl` 为每个非基础 head 选一条见证子句。只要每个依赖的深度严格小于 head 的深度，这些选择形成无环 witness DAG，可独立检查结构性闭包证书。它说明概念在该规则系统中可由基础项推出，不证明定义译文忠实，也不自动推出对象层面的真值条件蕴含。

## 目标方法：定义 → 逻辑 → 可验证推理

### NL→FOL 方法基线与语义金标准边界

ACL 2024 MALLS/LogicLLaMA 是适配比较的候选：它对 GPT-4 生成的句子级 NL–FOL 对做 CFG 检查、错误模式过滤，并使用 1K 人工标注子集做 translation-quality 评估；官方全文筛读及边界见[记录](../sources/literature_screening_log_2026-10-06_malls_nl_fol.json)。若未来适配到定义语料，应冻结相同的 sense-linked gloss 输入和输出预算，用相同双标 gold，报告可解析率、量词/连接词/方向错误及公式等价；另单独报告 gloss-span support、义项关系正确性、proof replay 与 abstention。其过滤后 92.8% correct 是不同任务/数据上的语料质量报告，不能作本项目先验精度或基线分数。MALLS 没有共享 sense/predicate 命名空间，也不做 fact check，故不能覆盖项目的 source-only 证明目标。

NAACL 2025 [Code4Logic](https://aclanthology.org/2025.naacl-long.547/) 是另一项 NL→FOL 适配候选：它用渐进式代码生成构造公式，并评测 FOLIO/MALLS 与 LogicNLI、RuleTaker、VitaminC 下游推理；筛读边界和论文自身指标见[记录](../sources/literature_screening_log_2026-10-06_code4logic.json)。若移植到 WordNet gloss，须共用 sense-linked 输入、输出/token 预算、候选集、lemma/sense 隔离切分及同一盲标 gold；报告公式结构/等价单独结果，再分别报告 source-span support、关系方向、proof replay 和 abstention。论文的 Logic Equivalence 与下游分数来自不同数据/设置，不能直接当作本项目基线；Code4Logic 本身也没有 gloss-source support gold。

Findings EMNLP 2025 [FOL Closeness Metrics](https://aclanthology.org/2025.findings-emnlp.910/) 对量词、否定、AND/OR 等做控制扰动，发现 BLEU、LE、Smatch++、BERTScore 等对表面内容与逻辑结构变化的敏感性不同；metric 与 o3-mini 排名的对齐实验不等同于大样本人类 gold。筛读记录及数值边界见[日志](../sources/literature_screening_log_2026-10-06_fol_closeness_metrics.json)。本项目应在公式层分别核验结构合法性、对谓词/变量重命名的不变性以及对逻辑操作符误改的敏感性；任何公式相似度/solver 指标都不能替代 sense、方向和 gloss-span source-support 的盲标结果。

Findings ACL 2025 [Disambiguate First, Parse Later](https://aclanthology.org/2025.findings-acl.863/) 在 text-to-SQL 中先生成并补全多种自然语言解释、再逐一做 SQL parsing；其主要目标是 full interpretation coverage。迁移到本项目的设计启示是把候选 sense/reading 覆盖、公式解析/编译和 gloss-span 支持拆为独立层，并允许 `ambiguous`/`needs_review` 而非强制选一个优先解释。SQL 执行等价依赖数据库与 gold query，不适用于判断 gloss 是否支持某个方向性规则；本项目需由 sense-disjoint 人工 gold 评估各层。全文筛读边界见[日志](../sources/literature_screening_log_2026-10-06_saparina_parse_later.json)。

ACL 2026 [From Trajectories to Graphs](https://aclanthology.org/2026.acl-long.2004/) 进一步表明推理 DAG 上的确定性结构 gate、接口兼容检查与紧凑证书已有主会先例。项目 witness-DAG/proof certificate 评估因此应把结构合法性作为必要的 engineering check，而把潜在论文贡献限定为更强的 source binding：每个用到的规则事实是否来自匹配 sense/gloss 的已裁决 claim、相应 source span 是否被支持、proof 是否独立回放且保持 source-only。应分别报告结构证书通过率、source-support precision/recall、逻辑证书 replay 和端到端 claim outcome；结构 gate 通过不能计作语义支持。该 ACL 工作的论文结果不移作本项目基线；详细边界见[筛读日志](../sources/literature_screening_log_2026-10-06_contract_checked_dag.json)。

SemEval 2026 Task 5 的 GuysLLM 与 SemTechLab/HINTS 提供了 NLI 初始化、目标词 span 交互和 graded-rating 建模候选：[GuysLLM](https://aclanthology.org/2026.semeval-1.314/)将故事和 sense definition/example 输入 NLI-finetuned DeBERTa 回归，[HINTS](https://aclanthology.org/2026.semeval-1.284/)则以 NLI-MPNet 特征预测人类 1–5 评分分布。二者是 workshop task 系统，任务和分数不可与本项目 gloss→方向 claim 评测横比；若改造成 baseline，须在同一 sense-linked gold 与数据切分上训练/评估，并分开标记目标词定位特征、gloss source-span support、方向正确性和 proof replay。筛读边界见[日志](../sources/literature_screening_log_2026-10-06_semeval_word_sense_plausibility.json)。

ACL 2024 [Diff-Comb Explainer](https://aclanthology.org/2024.lrec-main.40/) 将答案准确率、解释 Precision@K、解释一致性和答案—解释 faithfulness 分开报告；其 faithfulness 只衡量答案预测与正确解释事实是否共同出现，不代表来源文本支持或逻辑证书正确。项目应在候选 NLI accuracy、gloss-span semantic support、selected evidence coverage/precision、独立 proof replay 和 end-to-end answer/claim outcome 间分开记分；Knowledge partition 必须一致，source-only 条件不能暗中使用 ConceptNet/WordNet 外部 grounding。论文全文筛读见[日志](../sources/literature_screening_log_2026-10-06_diff_comb_explainer.json)。

EMNLP 2024 Unigram-FOL 提供可控 synthetic FOL/NLI stress-test 设计：简化英语与 TPTP 由同一 grammar 绑定，solver 确定标签、Vampire 保存证明，且可切片测等号、量词、否定、条件句和多前提逻辑。项目可据此建立**仅用于形式编译/推理引擎的独立合成套件**，明确每项 expected formula、solver label、proof trace 和扰动因素；其具体边界见[筛读日志](../sources/literature_screening_log_2026-10-06_unigram_fol.json)。合成 suite 通过只说明受控输入片段上的工程正确性，不能进入 WordNet semantic-support 分母、不能替代双标 gloss gold，也不能证明自然语言 compiler faithful。

1. **证据与义项**：保留原始 gloss、WordNet sense ID、POS、来源记录、解析版本与人工修订；义项消歧不应只用图入度等结构特征。评测至少区分 oracle-sense（给定人工确认 sense/signature）与 end-to-end（系统自行链接）的设置；两者差距用于隔离词汇 grounding 错误与后续公式化错误。这一拆分借鉴 NL-FOL 工作对 ontology extraction 与 fixed-signature translation 的区分，但对象和任务不同。
2. **语义 AST**：把 gloss 分析为有类型的谓词/论元、修饰、量词、否定、情态与作用域；显式表示歧义与多种释义，而不是过早压成无类型概念 ID。记录逻辑语义歧义（connective precedence、量词/否定 scope）和 sense/source ambiguity，必要时允许多标或 abstain。
3. **带方向的定义规则**：为义项 `s` 生成 `H_s(x̄) ←def Φ_s(x̄)`。方向、变量、谓词类型、定义性/常识性知识及每个逻辑片段的来源都需保存。除非来源确实支持，不使用双向等价。评测中把 source→rule support 与公式是否逻辑等价于一份 gold formalization 分开；前者是本项目关键语义目标，后者只能检验形式表示层。
4. **Horn 投影及 provenance**：`src/logic/annotation_to_datalog.py` 是标注 AST 到正 Datalog 的受限编译层。compiler v5 为 schema 0.2–0.6 保留一元共享变量片段；compiler v6 为实验性 schema 0.7 要求显式 `target_variable`，允许多元正谓词。必要方向只接受 atom/AND，且结论 atom 中不能有非目标变量；充分方向支持正 AND/OR 的至多 64 分支 DNF，要求每一分支都包含目标变量，额外变量只出现在 body。否定、量词和其他超出片段的结构显式拒绝；双向声明逐方向编译并标示拒绝。规则必须显式标记 `semantic_support=supported`、置信度不低于 medium；schema `0.4-draft` 及更新草案还要求非空 `inference_basis` 且每个依据标签仅为 `lexical_or_paraphrastic` 或 `compositional_or_logical`。其他依据和支持状态留在输入及拒绝列表中，不会因形式可编译而升级为 gloss 来源规则。置信度与推理依据门槛尚未经 gold 集校准。每条规则连回解析节点、原文证据 span、支持标签、置信度、推理依据、来源和转换器版本。该原型尚未在真实 WordNet gold 标注上验证。
5. **证明服务**：对给定前提和目标返回蕴含、反例/不可判定或资源超限；附上完整使用规则、前提、来源和可重放证书。闭包 witness DAG 与 FOL 定理证明证书属于不同层；当前另有受限桥接器将冻结 DAG 的选中子句重放为 ground Datalog 并交叉核对节点/依赖边，但只验证结构一致性，不补足 gloss 语义忠实性。
6. **NLI/人工语义门**：NLI 用于候选对排序或评估自然语言语义，不充当证明器，也不直接把高分写成无证据公理。对蕴含候选另分“是否由 gloss 的词汇/组合内容直接许可”与“是否还需外部世界知识、语用或比喻推断”；后者可作为隐含推理压力切片，但不能冒充 source-span support。INLI (ACL 2025) 已有显式/隐含蕴含区分与有限三人标注验证，然而其对话/社会情境标签不等于词典来源忠实度。主三分类 NLI 与 entailment 内部推理依据分层分别报告。schema `0.4-draft` 已为每条 claim 加入结构校验的 `inference_basis`，但标签定义仍需在双标前审阅和冻结；当前没有真实 gold 来检验其可标注性、一致性或与 source support 的关系。标签可以区分支持、过强/过弱、矛盾、独立、歧义和 unsupported；遇到歧义、形式化缺失或来源冲突时应拒答/送审。逻辑幻觉分类研究显示 input-output correspondence 与现实世界真值是两种问题，因此本项目也分别报告 source support 与资源外 truth/commonsense，不合成单一“无幻觉”分数。

oracle-sense 与 end-to-end 结果需分别报告覆盖率、公式结构/语义正确率、source-span support、proof replay、NLI 质量和 abstention；若只报告端到端总分，无法判断错误来自 WSD/词汇表对齐还是逻辑组合。可加入联结词、定义方向、量词/否定 scope 的控制扰动，但扰动检测不能代替人工 source-faithfulness gold。公式 closeness 指标也需在受控扰动上做 application-specific sensitivity check，并将 LLM judge 对齐与盲标 source-support 分开。参见[NL-FOL/逻辑幻觉补充日志](../sources/literature_screening_log_2026-10-03_logic_hallucination_supplement.json)。

**形式 verifier 不等于 source-fidelity verifier。** ICLR 2026 ProofBridge 使用 Lean 检查生成证明，并让 LLM 产生相对参考 Lean theorem 的双向等价证明；Lean kernel 核验后者只建立两份形式对象间的关系。它仍依赖参考 formalization 忠实于原始自然语言这一前提。因此本项目必须分别报告 (i) schema/compiler 与 proof/countermodel replay 的形式正确性，(ii) rule/formula 相对经审核参考表示的逻辑等价性（若实现），(iii) sense-linked gloss→方向 claim 的人工 source-span 支持。资源中已有的 hypernym links 和冻结 hypergraph clauses 属资源/形式对照，不得未经独立人审就充当第 (iii) 项 gold。[ProofBridge 筛读](../sources/literature_screening_log_2026-10-06_proofbridge.json) 是方法学近邻，不是 WordNet matched baseline。

ACL Anthology 2026 形式化切片的定向全文复核进一步提示：生成后的执行/solver 成功仍有条件依赖上游表示忠实度（LeVer 明确将 Solidity→Lean fidelity 留作限制；ToolGate 的部分合同规格本身由 LLM 辅助构造）。若候选系统带有 prover 失败后的神经回退，应分别报告 `formal_proved`、`formal_refuted/unknown/resource_limit`、`fallback_prediction` 与最终混合系统输出，不把回退正确计成 prover 证明。另需保留多前提大于二的 AND 组合切片：SemEval 2026 syllogism 先例主要限于两个前提，且其作者将多前提/sorites 留作后续，因此简单二前提有效率不能替代任意宽度 Horn body 的组合验证。这些属于评测设计边界，不是本项目已验证结果；逐篇全文章节范围见[ACL 2026 形式化筛读日志](../sources/literature_screening_log_2026-10-06_acl_formalization_2026.json)。

WordNet/OEWN 关系只能作为**资源相对标签**，不能单独充当人类语义真值或 gloss-span support。Cao et al. 的 GWC 2025 模板 elicitation 在 28,494 个保留 triplets 上发现多数人类关系 triplet 在 WordNet 中无直接记录，且 WordNet taxonomy path length 不是可靠的人类 hypernym 直觉代理；该研究是词/关系层人类直觉实验，不是义项对齐的 gloss entailment gold，不能据此把 WordNet 全盘判错。反向地，Augello et al. 的 LREC 2026 OEWN 形容词 benchmark 是经理论约束和人审校准的有用外部 relation slice，但仅覆盖 1,148 个高频、已消歧形容词；consensus 保留率也不表示每条均经过人类双盲核验。AI-WordNet 的 PWN 3.0 外部 cloze 任务同样重视 distractor 效用，作者明确允许某些非 hypernym/反方向候选仍具任务效用。故至少分别报告：`OEWN relation agreement`、`human lexical-relation judgment`、`gloss-span supports directional rule`；这三个结果不可互换。方法和限制见[WordNet source/gold 全文补充](../sources/literature_screening_log_2026-10-03_wordnet_source_gold.json)。

### 对邻近 proof/NLI 评测的操作性补充

GFaiR (LREC-COLING 2024) 的步级 FOL 可推性评估和 RDTE (EMNLP 2024) 的五级分解质量标注都不是 gloss-span support。当前正 Datalog checker 对其明确支持的有限、无函数符号片段完整计算 least Herbrand model：`entailed_in_positive_datalog` 表示片段内精确蕴含，`not_entailed_in_least_herbrand_model` 表示片段内精确非蕴含（附可验证有限模型），两者都不代表 gloss 语义支持或开放世界真值。当前没有搜索预算截止，因此 `resource_limited` 不是现有返回状态；`verify_query` 对格式错误/不支持输入仍抛 `ValueError`，但 reviewed pipeline 现将求解阶段的这类错误包装为 `unknown`。组合路由会重放证明证书或有限反模型；NLI 阈值通过而反模型有效时返回 `not_entailed_in_supplied_program`，未知状态则返回 `abstain_unknown_proof_result`。后续跨逻辑片段/有界 prover 的评测协议应区分 `proved`、`not_proved`、`unknown` 与 `resource_limited`，并把 source semantic label 单独记录；其中 `not_proved` 不能覆盖已经验证的反模型，也不能与计算耗尽混同。RDTE 的 relevance/redundancy/factuality/sufficiency 可作为设计人工 rubric 时的诊断维度，但不能把 context-dependent sufficiency 当作 definition-only entailment。文内样本总数存在 1,000 vs 267+775 的冲突，项目若借鉴其协议应以自身可审计分母为准。筛读证据见[结构化日志](../sources/literature_screening_log_2026-10-05_logic_proof_and_decompositional_nli.json)。

## 必须区分的错误类型

评测集还应包含受控的语义错配 challenge slice：在人工审校的 source→AST→directional claim 上，分别构造 AND↔OR、necessary↔sufficient、删除某个定义约束、替换 sense/source evidence 等单因素 mutation。目标不是让 parser/compiler 仅凭语法判定真伪，而是测系统是否保留候选/版本/来源并可靠 abstain，以及独立标注者是否能检出 source-support 变化；记录每种 mutation 的检出率、错误拒绝、未发现率和审核一致性。`tests/test_annotation_to_datalog.py` 现有一个 AST 级约束删除合成回归用例，只验证删除合取项会扩大当前 Horn 编译器的可导出结论；它不是自然语言错配检测，也不代表 challenge set 或模型评测。该设计受 AAAI 2026 VSPO 的控制逻辑错配启发，但本项目目前尚未构建此 challenge set 或评测任何模型，不能声称已有 semantic pitfall detector。

| 层 | 可能错误 | 可观测证据 |
|---|---|---|
| sense/WSD | 词形对应错义项 | sense ID、候选义项、上下文与人工标注 |
| 释义解析 | 论元、修饰或分支识别错 | 原文 span 到 AST 节点对齐 |
| 逻辑化 | 方向、量词、否定、变量或作用域错 | 有类型公式、编译器诊断、人工语义核验 |
| 知识覆盖 | 规则图缺少支持边/定义 | 证明失败核心、缺失谓词/规则、来源检索 |
| 推理 | 闭包实现/证明搜索出错 | 小型独立 verifier 重放证书 |
| 语义判定 | NLI 或人审判断错/不确定 | 校准、分歧、拒答率与复核标签 |

程序化推理的局部错误可再区分为 **syntax/compilation**（候选形式或转换器不能生成合法程序）、**logical-form mismatch**（程序可运行但未忠实表达 AST/规则）与 **execution/verifier**（形式表达正确但查询/执行/证书重放行为错误）；这一三分法与 ACL 2026 FOLX-KG 的错误分析相邻。它不能取代上表的 source/sense、方向性 semantic support 和缺知识错误：本项目需记录跨层归因及“首个失效层”，同一案例允许多标签。现有单测只证明已构造反例会触发特定检查，不是任何错误类别的真实发生率。

## 语义目标 E 与可计算验证 V：不可合并

借鉴近期 autoformalization 框架中“语义保持条件”与“可计算验证指标”的区分，本项目采用更适合**有向、可能不完整的定义规则**的记号：`E_s` 是义项 `s` 的规则级语义支持标准，`V_s` 是对 `E_s` 的一组操作性检查，而不是语义等价的代名词。

- `E_s`：给定固定版本的 sense、gloss 和证据 span，每条输出规则必须按其声明方向与粒度得到原文支持，不能引入 span 中没有根据的属性。必要条件 `Target(x) → Φ(x)` 与充分条件 `Φ(x) → Target(x)` 分别判断；只有双向均被支持且内容覆盖达到预设要求，才可称双向定义约束。若声称完整形式化，还需标记目标相关 gloss 内容的覆盖或明确列出未形式化部分。
- `V_s`：分别检查引用的 source/sense/version 能否解析、字符 span 是否精确存在、AST/逻辑片段是否良构、编译是否保持方向与 AND/OR、proof certificate 是否可由独立 verifier 重放，以及双人/裁决标注对 `E_s` 的判断及一致性。前五项可以自动化，但它们各自只核验局部性质；语义支持 gold 才是对 `E_s` 的经验性近似。
- **分开报告**：source/ID integrity、AST/compiler validity、相对输入规则的 proof replay、人工 source-faithfulness、lexical relation/NLI performance 与拒答覆盖率。proof certificate 另报告实际使用的 fact `knowledge_partition`，区分 source-only 证明与依赖资源事实/外部假设的结论；组合路由还要求每条实际使用规则绑定到测试样例的同一 sense 与 premise gloss，避免跨义项/跨释义规则迁移。partition 标签仍是输入声明，需独立 source audit。Phase 19 已把全图 selected-witness clause→source-document 索引→checksummed payload→同一 synset identity 做成直接复核，但仍不覆盖 gloss-span 对 literal 的语义支持。不得将这些阶段压成一个“verified=true”；Phase 19 的定义和结果见 [来源链审计](selected_witness_source_lineage.md)。

具体标注字段和边界见[annotation protocol](annotation_protocol.md)；本轮文献证据与检索限制见[相关工作审计](literature_review_audit_2026-10-03.md)。

## 评测设计

- **数据切分**：按 lemma/sense 组隔离，避免同词多义或近重复定义泄漏；另做按来源/词典切分的迁移测试。训练、开发、测试释义及派生 clause 不可跨集合。
- **基线**：人工/专家逻辑化上界；原始释义 NLI；WordNet definition-augmented NLI（Nishida et al. 2018，原 SNLI/MNLI 结果不可跨任务引用）；eXtended WordNet/ILF-WN/WN30-lfs 与 WordNetGraph 类定义解析/建图；Princeton Gloss Corpus + ERG 的 sense/深语义解析；COLLIE-V/GWC 词典知识抽取（COLLIE-V 是 WordNet gloss→带 AND/OR entailment axiom 的强直接先例，须优先作方法对照）；BMEAUT 的 Wiktionary→4lang 图→lexical entailment（须作为 definition-graph baseline）；CL 2025 taxonomy-aware semantic parsing；LLM 直接 NL→FOL；NL2Logic 式递归 AST parser + 确定性生成器；LLM+独立 prover；ICLR 2025 LLM-TH 启发的 NLI 评分 + typed hyperresolution 条件；NALOMA 2026 Neural DTS 启发的 WordNet hypernym embedding + DTS/prover 条件；本系统去除 provenance、sense 对齐、证书验证、NLI 各项消融。NL2Logic 的 NLI benchmark 结果只是其论文任务内的间接语义指标，必须在同一 WordNet gold 上重实现或适配后才能成为本项目 matched baseline；LLM-TH 的 commonsense-enabled 推理和 Neural DTS 的 taxonomy-based axiom injection 都不同于严格 source-only 目标，只有在本项目同一 gold 上适配、明示资源/常识前提与覆盖范围后，才可作为任务内比较，不能引用论文任务分数作本项目基线。SemEval 2026 parser/transpiler/Prover9 分模块与 premise-deletion 消融可作为组件设计参考，不可跨任务比较 leaderboard 数字。历史资源仅在代码/数据/许可和版本可获得时复现，否则明确作为表示/评测协议对照，不以引用代替实验。
- **几何组合表示对照（待实现）**：将 KDD 2026 subspace embeddings 纳入最高优先级的表示基线：在同一冻结 claim pairs 上评估 subspace inclusion 对原子 NLI 的打分，以及 AND/NOT geometric composition；其原论文 600-pair 组合任务仅在代码/数据许可与可复算性核验通过后作外部复现切片。项目自己的组合 gloss slice 须对原子与组合 pair 分别做人审裁决，不因某 baseline 原子题出错而从主集合剔除；baseline-filtered conditional subset 仅作次要诊断。NLI relation、gloss-direction `semantic_support`、sense/version correctness、source-span 和 proof replay 分轴报告；soft-projector approximate logic 不作为符号校验器。细化的组合构造、盲审、筛选偏差与指标协议见[候选验证协议的 KDD 组合切片](claim_verification_evaluation_protocol.md#kdd-2026-几何组合基线的-gloss-适配切片)；论文事实与筛读边界见[KDD 子空间日志](../sources/literature_screening_log_2026-10-05_iclr_lattice_and_kdd_subspaces.json)。
- **词汇层级 + 证明搜索对照条件（待实现）**：在相同人工确认的 sense、同一 gloss、候选预算及 sense/lemma-group 隔离切分下，比较 (A) direct NLI 对 gloss→candidate claim 排序；(B) LLM-TH-inspired entailment ranking + typed hyperresolution，并显式分区 resource facts / commonsense assumptions；(C) Neural-DTS-inspired WordNet hypernym ranking/embedding + prover，将 taxonomy relation 当作外部词汇公理；(D) 严格 `source_only` 规则生成与独立 proof replay，语义支持只由盲化人工 gold 裁决。B/C 是本项目适配条件，不声称复现相应论文系统。共同报告 sense/link correctness、taxonomy-relative hypernym correctness、方向规则 correctness、gloss-span support、proof replay validity、coverage/abstention、每例耗时和外部前提使用率；B/C 的证书有效性不能记作 gloss 支持，D 的 proof replay 也不能代替 semantic-support gold。若路由无法共享相同候选或预算，应把不可比项标出并分层呈现，不合并成一个总分。论文事实与筛读边界见 [LLM-TH 记录](../sources/literature_screening_log_2026-10-05_iclr_llm_th.json)及[Neural DTS 记录](../sources/literature_screening_log_2026-10-05_neural_dts.json)。
- **候选关系验证与生成评测分轨（待实现）**：避免把“系统会不会产出有用候选”与“给定候选时能不能判对”混作一个准确率。Track 1 为共享候选的 claim verification：固定 exact gloss/hypothesis 对，候选来自独立专家规则、所有系统输出的去重并集及预先声明的单因素挑战变体；逐项随机 ID、打乱次序并隐藏候选来源，双人按 sense/span 判定。对同一对分别采集三类标签：NLI relation gold `entailment / neutral / contradiction`、规则级 `semantic_support`（是否由该 gloss 按标注方向支持）、以及 `inference_basis`；不能把 `not_supported` 自动改写成 NLI `contradiction`，因为未被 gloss 支持不等于与 gloss 矛盾。还要保留必要/充分方向、完整 AND/OR 公式、证据 span 与不确定状态。Track 2 为端到端 candidate generation + proof：各系统只看同一 test gloss，在锁定的候选数 K、token/计算预算和模型版本下生成候选及证明；与盲标后的共同候选池精确或经预先冻结的结构规范化对齐，池外输出须另行盲标，不能默认判错或判对。报告每个系统的候选覆盖、精确率/召回率、source-support、sense/link accuracy、proof replay、abstention 与成本；Track 1 的分类分数不得替代 Track 2 的生成召回，证明重放率也不得替代语义正确率。
- **候选集冻结与泄漏控制（manifest/validator/adapter 已实现，评测仍待数据与授权）**：每条测试 claim 绑定 `sense_id`、固定 release、原始 gloss UTF-8 SHA-256、精确 hypothesis UTF-8 SHA-256、direction、candidate-set version 和盲标状态；KDD 组合切片另在候选 manifest v0.2 中锁定 operator、negated component IDs 和完整 formula hash。模型/规则与生成参数先锁定，test 候选输出冻结并记录 hash 后才开始人审，审阅期间不得替换候选或把 gold 回流给系统。模型产生的假设可进入合并候选池，但人审材料不显示系统名、得分、图特征或来源路由；独立 gold 不得用于提示、阈值、模型/规则选择。对方法间共有的候选子集与各自完整输出分别报数，避免只在容易重合的子集比较；按 lemma-group 做互斥 train/dev/test，并另保留 source/dictionary cold split。`src.analysis.freeze_claim_review_candidate_manifest` 从无标签候选对产生不含文本与 gold 的清单；`src.logic.claim_review_validator` 可按外部 pin 的清单 hash 核对 sidecar 完整性、文本 hash、证据 span、状态约束及 train/dev/test 的 group/sense 隔离，并校验组合组件引用、匹配来源和分割及依赖无环；`src.analysis.export_claim_review_nli_predictions` 要求同一外部清单及其 hash，将模型分数与已裁决的 NLI relation gold 按 candidate ID 一对一连接，拒绝未裁决 dev/test 行，并将组合类型和同一 model ID/revision 随评分行输出；export manifest 记录两份预测 JSONL 的 hash。组合 proof/NLI 路由必须经 `route_pipeline_result_from_export` 并提供外部锁定的 manifest hash，该入口核验输出文件与 split/model 一致性，并在打分前剥除 test gold。已有 v3 annotation sampling lock 只锁义项样本，不锁 claim/hypothesis；本研究尚无经外部固定的 claim manifest。canonical rule annotation 的 `semantic_support` / `inference_basis` 只提供另两个分层标签，任何一个字段都不能替代 NLI gold。导出器要求校准 dev 每个 lemma-group 恰好一行，以符合当前认证阈值选择器的独立样本假设。当前没有可用候选 gold、标注者验证或分发授权，工具通过只表示工程门可运行，须先冻结具体采样比例、双标裁决手册和分歧处理，再启动确认性比较。
- **独立执行协议**：candidate pool 的标注单元、pool sealing、3 条评测轨道、四种路由条件、指标分母、blind review 与启动 gate 详见[候选关系验证协议](claim_verification_evaluation_protocol.md)。其 sidecar JSON Schema 仅是结构草案，尚无 hash/span/split validator，也没有 candidate adjudication 数据。
- **主要指标**：sense 准确率；谓词/论元/作用域级精确率召回率；完整公式语义正确率；有来源规则精确率；蕴含 soundness 与 coverage；证书独立重放率；NLI accuracy/macro-F1/Brier/top-label ECE；在锁定 test 上的 gate precision/recall/coverage。组合路由的 dev 校准使用固定阈值网格上的精确二项检验与 Bonferroni 家族校正，需报告 IID 独立组假设；通用离线 evaluator 的 Wilson 搜索只作探索性分析，不作为有限样本保证；反例/拒答质量；错误类型归因准确率；人工审核时间；运行时间与内存。
- **来源支持的标注粒度**：近期 QASemConsistency 将生成句拆为 predicate–argument QA 并逐单元审查 source support，说明粗粒度整句/整条 claim 可能掩盖一个谓词下部分关系受支持、部分不受支持的情况。项目可借鉴“最小可判定 claim”标注，但必须保留必要/充分方向、变量绑定和 AND/OR 结构，不能把每个原子单独判定后误当成合取规则整体受支持。ACL 2026 PrefixNLI 的标签针对不完整文本，按“是否存在受来源支持的合理续写”定义；它启发的是独立的前缀/不完整候选压力切片，不能与本项目完整定义规则的 entailment 标签混用。两项工作均未测 WordNet 定义形式化，作为协议设计近邻而非直接性能基线；全文细节见[筛读日志](../sources/literature_screening_log_2026-10-05_fine_grained_support.json)。
- **与人工/参考公式的逻辑形式对照**：在有双人裁决 gold AST/FOL 的子集上，分别报告 schema/AST 有效率、标准化后 exact match、双向 theorem-prover equivalence 和原 gloss 到每条方向规则的 source-span support。双向证明只说明模型公式与给定 gold formula 在选定逻辑片段内等价；如果 gold 公式自身未经独立语义裁决，它不能验证 gold 或候选公式忠实表达释义。可将结构相似度与 prover 等价并报，但两者都不能替代 source-support gold。此分层受到近期 CCG→FOL theorem-prover 评测方法启发；该论文在 SICK 上筛选与参考 parser/prover 标签相符的 entailment/contradiction 数据，因此其准确率不是 WordNet gloss 指标，也不直接作为项目 baseline 分数。
- **人审协议**：双人独立标注并报告一致性；盲化方法来源；分别判定公式忠实性与 entailment，不让 prover 可证性替代语义正确性；报告全部样本数、抽样方式、置信区间与争议处理。可用 `src/analysis/annotation_agreement.py` 计算配对 status/projection κ、公式/AST/证据 span 一致性，并以固定随机种子的配对 item bootstrap 给区间；该脚本仅描述标注复现性，不裁决标签真伪，当前没有真实标注数据可供计算。
- **结构压力分层**：复用 `outputs/phase6/hypergraph_complexity_profile.json`，按所选 witness depth（0、1–5、6–25、26–100、101–300、301+）、head 的 OR 备选数与 witness clause 的 AND 宽度分层；另记录所有候选子句引用及所选 witness DAG 中依赖节点被其他 witness 复用的次数。二者不是同一统计：候选规则引用跨越所有 OR 分支，selected-witness 引用只在每个 head 的一条被选 AND 子句上计数。当前图 witness depth 中位数为 320，301+ 占 62.53%；选定证书 DAG 有 664,732 条依赖边，引用次数 P90 为 7、最大 27,777，且 65,334 个节点未被其他所选 witness 引用。详见 [selected-witness 结构剖面](selected_witness_dag_profile.md)。另有[全候选依赖弧投影 SCC 审计](dependency_projection_scc.md)：744,947 条唯一弧中出现 949 个循环 SCC，但投影丢失 AND 超边语义，因此只能作结构分层候选，不能称为 Horn 循环证明或语义难度。Phase 14 的[最小 witness 深度审计](minimum_witness_audit.md)显示原 selected witness 的所有 head 已达到冻结图中最小 grounded 推导层数，因此“缩短深度”不是当前图上的改进空间；替代 witness 的边数和证据质量仍须分别评价。上述深度、引用复用和投影 SCC 都不是语义难度或语义重要性；统计只用于覆盖样本和设计 query 级成本实验，待 gold 标注后才可检验其与语义/逻辑错误的关联。
- **长上下文证据压力切片（待实现）**：Logic Haystacks（EACL 2026）表明形式可控、难以词面剔除的非干扰项可用于压力测试长前提中的矛盾证据定位；其简化英语/FOL 合成任务不是 gloss 语义 gold。待双人 sense/span gold 与 matched baselines 到位后，可在固定目标 gloss 周围加入人工确认不支持目标的相似释义/规则，按上下文长度、证据位置、证据集合大小和相似度分层；分别测 source-span precision/coverage、联合证据充分性、错误证据排除、删除必要性、独立证书重放率、abstention 和人工复核成本。Counting-Stars (COLING 2025) 已使用证据数量/位置与上下文长度压力轴；Ev2R (TACL 2026) 摘要提醒将参考证据对齐与 verdict support 同时纳入考察（本轮仅摘要筛读），故这些指标需分别呈现而不能互相替代。必须先由人工确认 distractor 不支持目标；未经裁决的候选不能称为“provably non-interfering”。不把论文在其模型/提示/任务上的 128 句退化结果外推为项目阈值。详见[全文筛读日志](../sources/literature_screening_log_2026-10-06_logic_haystacks.json)。多证据选择与评估的后续邻居见[补充筛读日志](../sources/literature_screening_log_2026-10-06_evidence_retrieval_supplement.json)。
- **稳健性**：按 POS、定义长度、歧义度、来源、解析成功状态分层；做原语/子句扰动、证据缺失和版本变化测试。零证据输出与“未知”应单独计分。结构复杂度须与这些语言学因素分开建模，避免把图深度当作定义难度代理。另设尚未实现的形式化鲁棒性 stress slice：从双人裁决样本制作人审确认的 meaning-preserving gloss 变体与受限逻辑片段内的等价公式改写，并配少量只改变一个语义因素的对照项；冻结模型/提示，对比 sense、方向、规范 AST、source-span 绑定、证明器状态与 abstention 是否按预期保持或变化。每个变体都须保留原始来源及人工等价标签；若等价性或 span 迁移无法裁决则标 unknown，不纳入“保持率”分母。该设计受 CoPE 与 LogiQAte 的压力测试思路启发，但本项目尚无变体、标注或结果，不能声称鲁棒性已验证。
- **AND/OR 证据树先例与超图读出对照**：ACL 2026 EnoTab 已把 query semantic units 显式构造成 AND/OR Evidence Tree，并以逐节点 table pruning、状态检查和 rollback 执行；它不是 Horn proof，但说明 AND/OR evidence tree / observable tree execution 本身已有顶会先例。NeurIPS 2026 LogicTree-RAG 另已将源文档 spans 绑定到层次 logic-tree 节点，并以 LLM judge 和人工抽审评估证据支持；因此一般的层次证据树、来源 span grounding 与支持度人审同样不能单独作为新颖性主张。LogicTree-RAG 的专利生成任务不是 gloss→typed Horn 评测，其结果也不可直接横比；项目的 sense-specific 差异仍是假设。若未来做表示基线，可对照树执行忠实性、叶子 evidence support 与目标任务适配；不能把 EnoTab 的 TableQA 分数当 gloss 任务基线。另 HyperCoT（ACL 2026）使用深度敏感的角色化多路径读出，HGRAG（AAAI 2026）使用加权 incidence diffusion；这些可启发替代路径数、深度与检索成本对照，但其 n-ary facts/entity-passage incidence 均非本项目的有向 `OR(AND(body))` 规则。若实现 Laplacian/中心性 baseline，应单列为结构诊断，并加上保留 AND/OR 的逻辑证书读出作对照；扩散分数不得代替 entailment/proof。全文比较见[超图读出补充筛读](../sources/literature_screening_log_2026-10-03_hypergraph_readout.json)及[Phase232筛读记录](../sources/literature_screening_log_2026-10-08_logic_tree_rag_neurips2026_phase232.json)。
- **图结构读出假设（待验证）**：VoG（ICLR 2026）在已有 KG 三元组上做逐步 LLM 验证，并把中心性/子图连贯性列为未来可探索的上下文选择信号；它没有验证这些特征对释义逻辑化有效，也不输出形式证明。项目可在 gold 建立后按 sense/lemma 组切分，比较（a）词面、POS、长度、歧义度与来源质量基线，（b）有向简单投影的度/中心性、SCC、最短路等有损特征，（c）保留 clause 备选数、AND 宽度、grounded witness depth、最小高度证明家族/复用等 AND/OR-aware 特征。预测标签须是双人裁决的错误类型或 source-support 状态；报告分组外测试的 macro-F1/AUPRC、校准与 risk–coverage，并另测人工复核时间/证书搜索成本。简单图指标仅作结构对照，所有统计关联都需控制词性、释义长度、歧义度及来源因素；在 gold 数据到位前不训练、不报告其语义预测效果。筛读边界见[VoG 补充日志](../sources/literature_screening_log_2026-10-03_graph_verification.json)。
- **witness basis 支持包络**：Phase 17 计算“每个节点均选自身最小深度 clause”的局部家族；Phase 18 进一步按根的最小高度预算纳入所有可行子证明（包括 slack 子证明及有预算时 basis head 的规则备选），得到当前编码图上的全局最小高度证明家族。两者都保留 OR 与 AND，不等价于 semantic-prime 重要性或 gloss 支持。定义和结果见[Phase 17](minimum_witness_basis_support.md)及[Phase 18](global_minimum_witness_basis_support.md)。
- **发布物**：版本化语料清单与许可、哈希、schema、可复跑命令、固定随机种子、单元测试、证书 verifier、去标识的错误样本和模型/工具版本。

## 本阶段不应声称的结论

仅凭当前冻结包与网络投影统计，不能声称已实现 WordNet 的 FOL 蕴含、自然语言上下位校验、NLI 验证、普遍可靠性提升、顶会新颖性或最小原语集合全局最优。当前可复算结果限于给定冻结正 Horn 图上的结构闭包、所选 witness DAG 和单原语删除敏感性。

语义层原型已开始实现，但范围有限：见 [正 Datalog 证明检查器与 NLI 语义门](logic_verification.md)。它们尚未在 WordNet 标注数据上测量，因此不会改变上述结论边界。

gold slice 的记录结构与当前可执行校验边界见 [标注协议草案](annotation_protocol.md)。validator 只做格式、span、AST DAG、rule evidence 和 split hygiene 检查，不将通过 schema 校验等同于语义标注正确。

全量 source-index 与 payload 普查已覆盖全部活跃来源：112,609 个 source payload 的文件大小和 SHA-256 均匹配冻结 `checksums.jsonl`；全部逻辑树可解析，108,727 条来源记录的 DNF 分支数与归属 graph clause 数相同，但完整 WSD 分支 ID 多重集与图 literal ID 多重集完全相同的仅 3,123 条。154,356 个 source-clause 归属对中，150,599 个 graph clause ID 集合是至少一个完整 WSD 分支并集的子集。结构数相等或包含都不能判断 sense 正误、span 支持、规则方向或 gloss 蕴含；特别是 WSD union 可能包含非逻辑贡献词，graph literal 也可能经过筛选/归一化。主要待解问题由 payload/logic-tree 可用性转向 part→WSD→graph literal 的内容映射及其语义支持，必须在许可清晰的小型双标 gold slice 上验证。全量结果和定义见[Phase 15 报告](full_source_payload_census.md)。

Phase 9 已实现并运行一个第一名词 lemma 词面 baseline：在 160 条 random-stratified panel 中，99 个可评估名词目标有 96 个词面候选，候选中 40/96 的任一候选 sense 出现在 OEWN 直接 hypernym 列表。它是同一资源内部、感知宽松的结构代理值；由于含义项多义和未经人工确认，不是 hypernym accuracy。方法、所有 panel 分子分母、输入哈希和限制见 [Phase 9 报告](phase9_gloss_genus_baseline.md)。该结果支持下一轮优先实现候选义项消歧和双人 definition-head/span 标注，而不应把词面命中直接编译进 Horn 规则。

Phase 11 将同一弱 heuristic 用于 OEWN 2025 Plus 全部名词 synset：84,910 条定义字符串中，77,173 条存在直接 hypernym；其中 74,854 条找到词面候选（96.995%），28,449 条候选的任一 sense 与同版本直接 hypernym 对齐（38.006% 候选命中率；36.864%/全部可评估定义）。该 census 仍是资源内、any-sense 的宽松结构 proxy，不是语义准确率；它不涵盖冻结依赖图的 110,425 个 head，也不评估解析、逻辑化、证明或 NLI。逐 lexname 结果、分母定义及哈希见 [Phase 11 报告](phase11_gloss_genus_release_baseline.md)和[机器可读 JSON](../outputs/phase11/gloss_genus_release_baseline_2025_plus.json)。

Phase 12 在同一第一名词候选池上增加 release-local 二元 TF-IDF cosine sense 排序，屏蔽候选 span 与目标成员词，且不向排序器提供目标 hypernym 标签。全量中 13,528/77,173 个定义实例得到唯一 top-1（17.529% coverage），其中 5,843 命中同一 OEWN 直接 hypernym（43.192% 的已决样本；7.571%/全部可评估定义）；其余多数因无上下文词重叠 abstain。候选池 any-sense 对齐仍为 38.006%，在确有任一对齐 sense 的候选池中 top-1 retrieval 为 20.539%。这些结果只是 transductive 词面 ranker 对同资源 taxonomy 的 proxy，不能作为 gold WSD/蕴含准确率；详见 [Phase 12 报告](phase12_gloss_sense_rank_baseline.md)和[机器可读 JSON](../outputs/phase12/gloss_sense_rank_release_baseline_2025_plus.json)。

不要直接把该 38.006% 与 AI-WordNet (GWC 2025) 的 64.8% hypernym direct-hit 作数值比较：后者是新 lemma 的训练/预测任务，candidate generation 与 target population 不同；本项目数值是对已有 OEWN gloss 做首名词词面检索并按任一候选 sense 的宽松同资源对齐。两者只有在同一个人工 sense-disjoint gold slice、统一输入和指标上重跑后，才可作强基线比较。
## ICLR 2026 autoformalization 邻居带来的评测约束

CRAMF 在 Mathlib4 上把自然语言概念检索与形式定义 retrieval 接入 Lean autoformalization，故宽泛的“检索定义来 grounding 形式化”已有 ICLR 2026 先例；其数学任务上的编译率、回译 LLM consistency 与 retrieval hit rate 不能移作 gloss-support 指标。Mathesis 的 LeanScorer 将自然语言 premise/conclusion 拆成子任务、给出分级 match 标签并聚合，且在 98 项三专家标注集上校验；这可启发把 gloss 解析错误按最小语义单元分层，但其评分不提供词典来源跨度或词义方向金标准。本项目仍应逐层独立报告 gloss→sense/source binding、span→claim 支持、逻辑形式/类型检查、证明回放与 end-to-end outcome；不能把定义检索命中、编译通过、LLM 一致性或 theorem success 合并为一个“忠实”指标。两篇的全文核查范围与结果边界见[筛读日志](../sources/literature_screening_log_2026-10-06_iclr26_autoformalization_neighbors.json)。

Phase 139 以当前工作树和固定 OEWN 2025 Plus 输入重跑后，聚合 JSON 与 Phase 11 字节级一致。该复算确认计算结果可重复，不提高其为语义 gold、义项级 genus 精度或独立有效性证据的等级；详见Phase 139。
### Phase 170：验证器一致性与形式语义指标的分轴报告

CoNLL 2026 的 table-to-text 全文分析显示，NLI/TAPAS/TAPEX 验证器的选择会影响结论，并通过人审区分 true error、entailed-but-off-LF 与 verifier false rejection；但该任务不是词典释义，且人审规模有限。NALOMA 2026 的 Presburger semantic distance 可作形式公式集合语义比较，却仍会丢失量词，且不评自然语言来源是否支持公式。故本项目评测报告应分别呈现：解析/类型有效性、可判定条件下逻辑等价、每个确切 premise 的 NLI、人工 gloss-span→rule support、source-only 证书 replay，并分析 NLI 与其他验证器的分歧。任何一个子指标都不能充当整体 source-faithfulness 证明。详见Phase170筛读。

### Phase 174：逻辑等价与来源支持分开验证

ACL Findings 2026 的 LSEG 以 FOLIO/MALLS logical equivalence 检查 NL2FOL 输出，并使用内部熵变化做推理时纠偏。对本项目，至少要分开回答：(1) 规则是否在受限逻辑片段内可编译、类型正确且 proof/witness 可重放；(2) 形式表达是否与预先审核的参考形式等价；(3) 固定 WordNet sense 的哪一段 gloss 是否支持这条有向 Horn claim。前两项都不能单独推出第三项。模型置信、熵变化或 verifier agreement 只可作为路由/诊断特征，不能升级为 `semantic_support` 标签。LSEG 是 NL2FOL 邻居而不是 matched baseline；将来若做生成器鲁棒性对照，须先定义同一 sentence-to-formula 任务和校准/测试隔离。筛读范围及局限见Phase174报告。

### Phase 175：AND/OR closure、单 witness DAG 与 basis 删除影响

当前 frozen graph 的删除影响需由精确 AND/OR least-fixed-point closure 在删去 basis 后重算；不能把单选 witness DAG 的普通 descendants 当作等价指标。Phase175 的初始比较混合了含根节点的 closure loss 与不含起点的 descendants。Phase179 将两者统一到非根节点后，85 次删除中 descendants 高估 66 次、相等 19 次、低估 0 次；旧字段仍保留以便追溯。结构上，合法 witness certificate 意味着任何失去精确支持的非根节点必属于该 seed 的 witness descendants；未选 OR 子句可使 descendants 高估损失。对每个 node 的 minimum-depth witness certificate 可确定性重放，但同深度 OR 备选及证据质量不是 tie-break 目标；需要保留完整候选 clauses 和语义来源标签。当前图审计只验证固定正 Horn 表示、输入 hash、闭包与 witness 结构，不为任一 gloss literal 提供语义支持证据。输出与解释见Phase179更正报告、Phase175报告和机器结果[冻结图审计](../outputs/phase175/frozen_hypergraph_current.json)、[minimum-depth审计](../outputs/phase175/minimum_witness_current.json)。

### Phase 178：通用 Horn closure 中的空 body 规则

`frozen_hypergraph_audit.closure` 现将空 body 子句按空合取为真的 Horn 语义处理：其 head 在初始传播队列中作为已导出事实，再继续触发依赖该 head 的其他子句。Phase175 固定 bundle 中的 empty-clause 数为 0，因此原冻结图闭包与删除影响的报告数字不受该修正影响；修正扩展通用闭包函数对含事实规则的适用性。CodeGraph 影响图显示该函数还供 `basis_sensitivity`、冻结图 audit 与 flattening ablation 使用。此为代码审阅所得语义修正，未运行测试或重算报告；边界见Phase178报告。

### Phase 204：研究假设判据与 Track A 执行状态

H1（source-only 端到端增量）、H2（AND/OR 相对压平的语义价值）和 H3（证据/回放对人工审阅的帮助）均属于预先写出反驳条件的研究假设，不是当前方法效果。当前可报告的证据仅覆盖被冻结图结构证书、witness/source payload 的字节与身份一致性以及 Phase200 自动 WSD ID 分支重合诊断；它们不验证自然语言支持、人工审阅效用或 risk–coverage 增益。Phase202 已确认 Track A 当前没有 edge/surface/condition-aware 的端到端合同，所以候选冻结器/NLI exporter 的存在只证明通用工程组件，不证明 Track A 已可直接执行。该边界及逐项主张状态见[Phase204 主张—证据交叉表](research_claim_evidence_crosswalk_2026-10-08_phase204.md)与Phase202 互操作性报告。

Phase205 进一步确认当前 source-only strict route 以测试 `premise_sha256` 同时匹配 raw gloss 的 source hash；这是 raw-gloss condition 的身份关系，不适用于另行渲染的 lemma+POS+gloss condition。当前 query/claim route 亦不绑定 Track A 的 parent sense、parent surface 与 relation edge。故“已有人审 source-only proof route”仅适用于其现有单义项 annotation 合同；它不证明 Track A 的 pair/edge 路径已实现。任何适配须分别绑定 raw source 与 rendered input，并保留 relation-edge identity；须等协议裁决后在新版合同中实现。见Phase205 报告。
