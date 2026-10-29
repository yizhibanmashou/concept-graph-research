# 最新相关工作补充：推理边界控制与框外发现

审查日期：2026-10-06。本文补充当前相关工作矩阵，记录近期 Findings 论文及其对项目边界的影响。各项均为单篇定向筛读，不是系统综述，也不证明项目的新颖性。

## 检索与纳入

- 数据库：ACL Anthology 官方论文页与 PDF。
- 定向检索词：`missing premise`, `grounded reasoning`, `clarify and pause`。
- 命中：Qiu et al., *Pause or Fabricate? Training Language Models for Grounded Reasoning*, Findings of ACL 2026。
- 全文范围：22 页 PDF 的问题定义、方法、遮蔽数据构造、主要实验、完整/域外分析、局限及附录数据构造和超参数消融。
- 固定框关系：该文不在 ACL v3 1,747 条冻结候选集；这是官方站点框外定向发现，不回填候选计数，也不据此推断召回率。
- 来源：[ACL Anthology 论文页](https://aclanthology.org/2026.findings-acl.1155/)；[官方 PDF](https://aclanthology.org/2026.findings-acl.1155.pdf)；结构化逐篇记录见[机器筛读日志](../sources/literature_screening_log_2026-10-06_gril_findings_acl2026.json)。

## 论文内容与证据边界

GRIL 把输入充分性识别建模为交互决策：缺前提时模型应澄清/暂停，补足信息后再解题；信息完整时则直接作答。训练集通过遮蔽数学题中的候选数值句构造，附录说明用预训练 LLM 判断遮蔽后的问题是否可解，以标记 essential 与 redundant premise。论文报告不同模型规模和多个完整/缺前提/域外任务的结果；以 Qwen2.5-1.5B、GSM8K-Insufficient 为例，表 1 报告 premise detection 4.6%→90.8%、task success 1.8%→61.6%。这些都是原论文在其数学任务上的结果，不能移用为 WordNet 或自然语言定义蕴含结果。

作者列出的限制包括依赖结构化输出解析动作，以及以轮次/响应长度代理效率，没有直接测量澄清质量和用户负担。构造标签还受到“遮蔽数值句 + LLM solvability 判断”这一数据流程约束。故该工作适合作为一般 inferential sufficiency、pause/clarify 行为的相关工作，而不是词汇语义 baseline。

## 对本项目的影响

该先例要求进一步降低宽泛创新表述：一般性的缺前提检测、拒答、暂停和主动澄清已被研究。项目仍待检验的窄问题是：在 sense 与释义版本固定的条件下，系统能否分别识别资源未覆盖、gloss source-span 不足、逻辑程序中的有效反模型和求解未知，并让这些带明确来源的状态在 gloss 关系任务上改善校准、coverage 与错误归因。

这些状态语义不同，不能合并：`not_supported_by_gloss` 不自动等于 NLI `contradiction`；有限闭世界程序中的反模型只针对显式程序；来源文件/人工审阅缺失属于证据不足。项目的现有路由协议已经区分其中若干状态，但是否在真实标注 gold 上有效尚未测量。需在盲审 gloss-span gold 和 matched baselines 上检验，不能把 GRIL 指标或当前结构证书当成支持证据。

## 当前相关工作综合判断

现有矩阵已识别多个更近的直接或方法邻居：释义导出的 lexical relations、WordNet gloss-conditioned directional entailment、定义到结构化语义、NL→FOL 与 solver 验证、proof DAG/结构证书、长上下文多证据定位，以及信息不足时的暂停机制。宽泛的“WordNet 定义自动抽关系”“定义转逻辑”“proof DAG 可解释/可验证”“证据不足时拒答”都不宜单独作为新颖性主张。较窄候选仍只是研究假设：sense/release 绑定的 gloss span 对多前提有向 AND/OR Horn 规则的独立语义支持 gold，加上同一 source-only proof/countermodel 的可重放证据链。此差异仍须通过完整跨库检索、合法数据/归属审核与共同 gold 上的匹配实验验证。

## Findings ACL 2026：逻辑结构密度与推理拓扑

Bi et al., [*Logical Structure as Knowledge*](https://aclanthology.org/2026.findings-acl.436/) 提出 SLKD：由 LLM 从逻辑推理样例抽取谓词、常量与公式，构造前提集合和单条推导链，再以表达式计数、操作符、嵌套深度等形成训练样例密度分数，并用于 SFT/RL 数据选择。论文报告四个逻辑基准、36,788 个训练样例、4,743 个测试样例；作者将分数称作 reasoning-potential proxy，并承认模型家族覆盖有限、LLM 分解会引入噪声且跨域迁移有待验证。它与项目冻结 AND/OR 图的结构画像相邻，意味着结构密度/推导复杂度指标并非可独立主张的新贡献。两者对象仍不同：项目画像是既定图的结构统计，SLKD 是自然语言推理样例上的训练数据权重；任一者都不测 WordNet gloss 的 source-span 忠实度。详见[结构化筛读日志](../sources/literature_screening_log_2026-10-06_slkd_findings_acl2026.json)。
## 固定 ACL v3 中的 2025 规则与形式化近邻

从固定 ACL Anthology v3 的 `definition_to_formal_logic` 待筛记录中，优先核读 RuleArena、LTRAG、MASA 与 NL2Lean/ReLean 四篇 2025 论文。前者评估真实自然语言规则的选择、应用和答案；LTRAG 结合检索示例、形式化、symbolic solver 与 LLM repair；MASA 演示数学定义的 multi-agent autoformalization；ReLean 在数学语句→Lean 上组合语义/结构/编译奖励及人工评价。它们强化了任务分轴要求：规则选择/应用、语法/编译、proof validity、源语言语义忠实需分开评测。

四项均没有 sense-linked WordNet gloss-span source-support gold；仅属跨域邻居，不能作为项目效果的 matched baseline。筛读日志及 candidate/export hash 见[机器记录](../sources/literature_screening_log_2026-10-06_acl_2025_formalization_rule_neighbors.json)。以新增日志重算固定 v3 exact-URL reconciliation 为 447/1,747，其中 full-text 56、targeted sections 35、metadata/abstract 204、depth unresolved 152、待题名/摘要 1,300；原始冻结候选文件未修改，计数含义见[reconciliation snapshot](../sources/acl_screening_reconciliation_2026-10-06_phase29.json)。这仍是有界 ACL 候选框，不是系统综述或召回率估计。

## IJCAI 2026：端到端方法组件的宽泛先例

本轮在 IJCAI 官方 proceedings 按 `logical rule induction`、`textual entailment proof tree` 和 `proof tree entailment` 定向检索，核读两篇官方论文 PDF：[Neuro-Symbolic Logical Reasoning with Textual Entailment](https://www.ijcai.org/proceedings/2026/989)（Demo Track，4 页）和 [A Foundation Model for Zero-Shot Logical Rule Induction](https://www.ijcai.org/proceedings/2026/445)（Main Track，9 页）。逐篇结构化记录：[IJCAI 2026 筛读日志](../sources/literature_screening_log_2026-10-06_ijcai2026_logic_neighbors.json)。

第一篇 VANESSA 工作把自然语言规则/事实经浅层解析与文本蕴含桥接后送进符号 prover，输出答案 proof tree；作者报告符号版本在措辞变化时 recall 会下降，并将不能完成判断的情况保留为 Unknown。它意味着“文字蕴含 + 符号推理 + 证明树”整体路线已有主流会议先例。第二篇 NRI 从数据学习 proposition-level DNF，说明可解释 AND/OR 规则归纳也已有近期先例；但其 Boolean/tabular features 不是 sense-linked gloss propositions，任务成绩不验证自然语言来源支持。

这两项降低宽泛 novelty claim 的可信度，但没有回答词典任务的实证问题：固定 sense 与 release 的原始 gloss spans 能否由独立标注支持一条方向明确的多前提规则；规则再经过 source-only proof/countermodel replay 后，是否比同切分的直接 NLI、资源闭包、词面及逻辑化基线更可靠？这仍是研究假设；本轮不是 IJCAI 全集筛查，也没有运行模型或复现其数值。
