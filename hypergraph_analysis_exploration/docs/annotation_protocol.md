# WordNet 释义逻辑化 gold slice：标注协议草案

状态：协议草案；早期 Phase 9 有 200 条 pilot blind batch。当前 v3 候选确认性设计为 400 条/24 层，raw gloss 400/400 与 OEWN 2025 Plus 精确匹配，effective definition 376/400 精确匹配；400 条本地 blind batch 已导出，但尚未分发或标注，因此没有人工标注、裁决或 gold data。v3 的[预注册方案草案](annotation_preregistration_draft_v3.md)整理了主要估计与停止规则，但尚未签署/登记，不能称作 preregistration；许可和标注人员安排也未解决。适用目标是评估“释义 → 有证据的语义结构/候选规则”，不是给冻结依赖图补一个语义标签后就宣称得到逻辑库。`0.5-draft` 的变量 sort 仍是人工声明输入；referent 域与拒绝规则的实验性方案见[类型契约草案](gloss_referent_type_contract.md)，尚未进入当前 v3 批次 schema 或验证。

## 1. 标注单位与不可混淆的对象

基本单位是一条有稳定版本和来源的 WordNet synset/sense 记录，而不是裸词形。每条记录至少绑定：资源名与版本、synset ID、lemma/POS、原始 gloss、原始文本偏移坐标约定和输入文件哈希。已有冻结图中的 dependency clause 另行保存为 `structural_dependency`，不能自动充当语义 AST 或规则 gold。

对每个 gloss 分四层独立标注：

1. **义项/文本层**：synset ID、lemma、POS、gloss 原文、例句（若有）、来源文件/记录 ID、版本和许可。
2. **语义分析层**：带原文字符区间的语义节点；记录谓词、论元、属性、修饰范围、并列/备选、否定/量词/情态以及未消歧片段。
3. **规则判断层**：每个命题是定义性必要条件、充分条件、双向约束、典型属性、词源/用途说明、例子或不确定；保存方向、变量、类型及证据 span。不能把“常见/典型”静默编为 Horn 公理。
4. **结构投影层**：单独记录是否可投影到目标 Horn 片段、投影规则 ID、被省略/拒绝部分和原因。未支持量词、否定、模态、关系论元或歧义时标 `unsupported/needs_review`，不猜测。

定义语义方向必须显式。对 genus-differentia 风格 gloss，可能出现 `Target(x) → Genus(x) ∧ Differentia(x)` 的必要条件，也可能在充分且恰当的定义判断下考虑反向规则；两者不能仅凭词面顺序互换。常见属性不自动形成必要或充分条件。定义关系、上位关系、一般常识与 frozen graph 的依赖方向分别编码。

## 1.1 语义支持标准 E 与操作性验证 V

标注前先固定规则级语义支持标准 `E_s`：对 sense `s` 的 gloss/source span，判定它是否支持某个**有方向**的 claim。逐项区分 `Target→Φ`（必要条件）、`Φ→Target`（充分条件）和两者同时成立的双向定义；不因公式能被 checker 接受而认定方向成立。若论文任务声称完整释义形式化，还需规定相关内容覆盖标准；部分可形式化时，其他内容必须显式记录为 omitted/unsupported/ambiguous，而不是静默删去。

可计算验证指标 `V_s` 是对 `E_s` 的近似与配套完整性检查，至少分开报告：source/sense/version 身份与哈希、span 精确定位、AST/类型/schema 合法性、编译保持性、相对于输入规则的 proof replay，以及双标注/裁决对 E 的支持标签。ID 存在只证明对象可定位；checker 证明只说明推导遵守输入规则。两者均不能单独判定 gloss 是否支持该规则。未能判断时保留 `unknown/needs_review`，不得按负例或形式化失败混记。

## 1.2 来源支持与隐含推理的分轴标注（新增设计维度）

ACL 2025 的 INLI 将蕴含细分为 explicit / implied，并把 implied 定义为还需要额外认知步骤；这类步骤可能依赖逻辑推理、世界知识、语用或比喻。对本项目而言，“读者可以合理推断”不能自动等同于“WordNet gloss span 支持该规则”。因此 schema `0.4-draft` 将**方向性来源支持**与**推理依据**分开：保留 `semantic_support` 为主标签，另在每条 claim 上记录 `inference_basis` 列表，可取 `lexical_or_paraphrastic`、`compositional_or_logical`、`external_world_knowledge`、`pragmatic_or_conversational`、`figurative_or_metaphorical`、`unclear`。多个必要依据可并列记录；由多个标签表示组合依据，不另设冗余的 `mixed` 值。`unclear` 单独使用；尚未判定支持状态的 claim 使用 `unassessed`。该字段描述作出语义判断所需的最小推理依据，不是 NLI 预测，也不改变 `semantic_support` 的判定标准。

严格 source-support 评测中，依赖未编码的世界知识/社会规范/语用的推断应另标为 implied/external-basis challenge，而不能悄然计作 gloss span 明示支持；若 WordNet 的定义关系在预先声明的语义系统中可由 lexical semantics 组合推出，则应说明该推理规则及其来源。主要 NLI 仍可用三分类 `entailment/neutral/contradiction`，但额外报告 entailment 内部的 explicit-vs-implied 分层，或在独立辅助任务使用四分类；不能把两个任务混成一个 accuracy。详见[INLI 全文筛读日志](../sources/literature_screening_log_2026-10-04_formal_nli.json)。

### `semantic_support` 操作定义

判断单位是一个已绑定 synset、原始 gloss 和 evidence span 的完整方向性 claim，而不是孤立 AST 节点。应先按选定义项理解原文，再判断原文是否支持该 claim 的关系、方向、逻辑运算符、论元和限定范围；不得用 checker 可编译、常识合理、与词条标签相符或 NLI 模型高分替代人工判断。

- `supported`：在该 synset 的 gloss 解释下，引用 span 足以支持 claim 的全部内容和所标方向；没有被省略的限定、例外、否定、情态或范围差异改变其结论。只与 gloss 相容或“听起来合理”不够。
- `not_supported`：已能作出判断，但该 span 不许可 claim 的全部内容/方向，例如 claim 比 gloss 更强、增加未陈述条件、把典型属性升格为必要条件、逻辑范围不匹配，或原文与 claim 冲突。此标签只表示“未获该来源支持”，**不表示 claim 已被证明为假**。
- `uncertain`：已尝试判断，但由于原文或义项存在无法在当前上下文消解的歧义，至少有两种合理解释会导致不同支持结论；记录歧义位置及备选解释。单纯标注者信心低应体现在 `confidence=low`，不能自动改标为 `uncertain`。
- `unassessed`：该 claim 尚未接受语义支持判定，属于工作流状态；不能解释为负面标签，也不得进入接受规则的编译集合。

### 多种可接受分析与公式 OR 的区别

同一 gloss 有时可能允许不止一种合法形式化分解。必须区分：

1. **语义 OR**：gloss 本身断言或列出析取内容，应用 AST `or` 编码，属于某一条公式内部的逻辑结构。
2. **备选分析**：两套不同公式/claim 集各自都是对同一 gloss 的可接受分析；它们是 reference-set 的备选项，不表示 gloss 断言二者析取，也不表示它们必须同时成立。
3. **未解决歧义**：同一解释下，文本或 sense 歧义会改变某条 claim 的支持判断；按 `uncertain` 处理并记录歧义及备选解释。

当前 annotation schema `0.4-draft` 的 `root_node_ids`、`rule_claims` 和 AST `or` 均不为“完整备选分析集合”提供互斥分组语义。不可把多个 `root_node_ids`、若干 claims 或 notes 直接当作多参考 gold；也不要因为两个不同分析都合法就给 claim 标 `uncertain`。当前 400 项仍未获授权的盲标输入不变。若确认性研究需要承认多种形式化，可在正式标注前采用单独版本化的 adjudication sidecar `gloss-analysis-reference/0.2`：以 `item_id` 和 raw-gloss SHA-256 绑定原始来源；每个 `accepted_alternative` 表示一整套可接受分析，引用不可变的规范 JSON annotation-record SHA-256、完整 `root_node_ids` 与被裁决为 supported 的 `rule_claim` IDs，并保存裁决理由。`complete` 必须表示 accepted reference set 已完整穷尽且没有未决候选；若仍有未决候选，整项标为 `unresolved`，不能静默挑一个答案或计入已完成评分分母。当前已有 sidecar validator 与 scorer 原型，详见下文；它们尚未通过测试或研究者协议审查，不属于 schema `0.4-draft` 或现有批次锁。

若后续按多参考方式评分，须在查看系统预测前冻结 adjudicated accepted sets。预测只能与某一个完整 alternative set 匹配；禁止把所有 alternatives 的 claims 并成一个大 gold set，否则会奖励过度生成。原型 `src.analysis.score_gloss_analysis_references` 对每套完整 alternative 单独计算 rule-claim set precision/recall/F1，再以 F1 最高者作该项结果（并列时依次优先整体 exact match、`alternative_id` 字典序）；整体 exact match 同时要求 claim multiset、alpha-normalized canonical root AST 与 `analysis.status` 全部一致。报告 micro（先按每项最高分 alternative 汇总 TP/预测数/reference 数）和 macro（逐项 P/R/F1 的非空算术平均）；空 claim 对不进入 macro 的 P/R/F1 分母，但仍进入**已完成裁决项**的 exact-match 分母并单独计数。`unresolved` 项不计入任何 exact-match/claim-score 分母，必须另外报告数量与占全部 sidecar 项比例。另报告 claim exact、root-structure exact、status match；只对单一 reference 的项目另报严格子集 micro/macro、alternative 数分布及 unresolved 比例。这里的 micro/macro 是未加抽样设计权重的样本级描述值，不是 104,907 项总体表现估计；若要作总体推断，须事先绑定 inclusion weights/frame，并处理拆分与 cluster 依赖。它不合并 alternatives，也不评判 source-span 或 claim 语义；池外候选仍须盲审，不能因某个模型提出就追认 gold。若 v3 研究不采用 sidecar，则结论范围必须明确限于其预先定义的单一裁决 reference，不宣称覆盖所有有效释义分析。

### 多参考 sidecar 原型接口（未冻结）

实现位于 `src/logic/gloss_analysis_reference.py` 与 `src/analysis/score_gloss_analysis_references.py`。Sidecar 顶层字段为 `schema_version`、`item_id`、`source_gloss_sha256`、`adjudication_status`（`complete`/`unresolved`）、`adjudicator_id`、`accepted_alternatives`、`unresolved_candidates`、`notes`。`complete` 必须至少有一个 accepted alternative，且 `unresolved_candidates` 为空；仍有任何候选分析未解决时，整个 item 必须标为 `unresolved`，不进入 claim-score/exact-match 分母。`unresolved` 必须保留至少一个候选且不得有 accepted alternatives。每个 accepted alternative 额外含 `analysis_status`；完整字段例见 Phase 105 报告。annotation-record hash 对排序键、无多余空格的 UTF-8 JSON 对象求 SHA-256；gloss hash 对原始 gloss 精确 UTF-8 字节求 SHA-256。Sidecar 必须与记录集一起校验，以重算 hash 并核对 item、sense gloss、裁决者、analysis status、完整 roots 和 claim IDs；同一 item 的所有 linked records 必须具有相同 `resource/version/record_id/license/input_sha256` 与 `synset_id/lemmas/pos/gloss`，scorer 还会要求预测行与该身份完全对齐，以免同一原文重复于不同资源或义项时误计分。用法：

```powershell
python -m src.logic.gloss_analysis_reference refs.jsonl adjudicated-records.jsonl
python -m src.analysis.score_gloss_analysis_references refs.jsonl adjudicated-records.jsonl predictions.jsonl --output scores.json
```

评分输入要求每个 sidecar item 恰有一条 prediction，且 split 和 gloss hash 与 reference 一致；unresolved 项不计入评分/exact-match 分母，但会按全部 sidecar 项计算 unresolved 比例。核心 `score_reference_sets()` API 与 CLI 评分结果均记录 scorer/claim canonicalizer/两个 validator 的源码 SHA-256，以及 Python 实现名、完整 Python 版本字符串与 `sys.platform`；CLI 另外记录各输入文件 SHA-256。API 直接调用的输入文件 hash 需由调用方另行保存。上述字段支持运行追溯，但不代替环境依赖锁、命令归档、独立输出校验或重复复算。该接口目前是未经运行验证的实现草案，不能据此认为 estimand、双标流程或方案锁已完成。

评分输出契约使用 `gloss-analysis-reference-score/0.2`，当前 scorer 实现标识为 `gloss-analysis-reference-scorer/0.5`；`/0.5` 增加预测与裁决 source/sense identity 对齐检查，输出 schema 字段未变。输出包含 macro 汇总及源码/runtime 指纹；输入为 `gloss-analysis-reference/0.2` sidecar schema，其 `/0.1` 版本不支持完整裁决与未决候选互斥约束，应由当前 validator 拒绝。

schema `0.3-draft` 与 `0.4-draft` 在 `not_supported`/`uncertain` claim 上要求 `support_reasons` 为非空代码列表；`0.2-draft` 作为旧记录格式继续读取。可用原因码为 `content_not_licensed`、`claim_overstates_or_omits_qualifier`、`direction_mismatch`、`operator_or_scope_mismatch`、`source_conflict`、`lexical_or_sense_ambiguity`、`scope_or_reference_ambiguity`、`insufficient_context`、`other`。前五类适用于 `not_supported`，后三类歧义/上下文码适用于 `uncertain`，`other` 可用于两者。`supported` 与 `unassessed` 不应带原因码。原因码便于汇总失败类型，但不代替自由文本说明；对 `not_supported`/`uncertain`，仍应在记录 notes 中写明主要依据/歧义。`confidence` 单独表示标注者对其所给 `semantic_support` 判定的把握程度，不表示 claim 为真的概率，也不改变上面四种标签的含义。裁决时保留双方原始标签和裁决理由。典型属性、例子、用途说明即使被原文直接陈述，也应按其 relation 分类，不能因此升级成定义性 necessary/sufficient claim。

## 2. 机器可读记录建议

先用 JSONL（一行一个标注版本）保存记录：`item_id` 标识同一个源 sense，`annotation_id` 唯一标识某位标注者的一轮独立标注或裁决记录。不同标注者不能覆盖同一行。当前可执行结构校验器为 `src/logic/annotation_validator.py`；它不是完整语义校验器，读取历史 `0.2-draft`/`0.3-draft`，当前 v3 标注草案仍采用 `0.4-draft`。0.3 起将 `support_reasons` 作为 `not_supported`/`uncertain` 的必填字段；0.4 另要求每条 claim 显式填写 `inference_basis`。实验性 `0.5-draft` 增加 claim 级 `variable_sorts`；`0.6-draft` 则以 `variable_sort_judgments` 保存 sort、判定依据、理由与证据 span，并保留 unresolved 判定；实验性 `0.7-draft` 在 0.6 判断基础上增加必需的 claim 级 `target_variable`，供多元 Horn 投影显式识别目标 referent。0.5–0.7 均不替换当前标注批次格式，也不是已登记的研究协议。逻辑 AST 采用受限可扩展的 tagged nodes：

```json
{
  "schema_version": "0.4-draft",
  "item_id": "resource-version:synset-id",
  "annotation_id": "resource-version:synset-id:annotator:pass",
  "source": {
    "resource": "demo-resource-not-WordNet",
    "version": "demo-version",
    "record_id": "synset-id",
    "input_sha256": "35cc1bc218ab41dac6d76c068ab4d4a3b6096cfb72ce09931c3b8745e6c48a8f",
    "license": "illustrative-only"
  },
  "sense": {
    "synset_id": "demo.n.01",
    "lemmas": ["demo"],
    "pos": "n",
    "gloss": "a small bird"
  },
  "analysis": {
    "status": "annotated",
    "nodes": [
      {"id": "n1", "kind": "atom", "predicate": "SMALL", "arguments": [{"kind": "variable", "id": "?x"}], "span": {"start": 2, "end": 7}},
      {"id": "n2", "kind": "atom", "predicate": "BIRD", "arguments": [{"kind": "variable", "id": "?x"}], "span": {"start": 8, "end": 12}},
      {"id": "n3", "kind": "and", "children": ["n1", "n2"], "span": {"start": 0, "end": 12}}
    ],
    "root_node_ids": ["n3"],
    "rule_claims": [
      {"id": "c1", "relation": "necessary", "direction": "target_to_gloss", "formula_node_id": "n3", "evidence_spans": [{"start": 0, "end": 12}], "semantic_support": "supported", "inference_basis": ["lexical_or_paraphrastic", "compositional_or_logical"], "confidence": "medium"}
    ],
    "horn_projection": {"status": "not_attempted", "rule_ids": [], "omissions": []}
  },
  "annotation": {"annotator_id": "annotator-a", "adjudication_status": "independent", "notes": []},
  "split": "unassigned"
}
```

该示例仅示范格式，不是真实 WordNet 标注；SHA 是示例 gloss `a small bird` 的 UTF-8 字节 SHA-256。validator 会重算并校验 `source.input_sha256` 与 `sense.gloss` 完全对应（不做 Unicode 归一化），以发现文本/哈希错配。span 使用 Python Unicode code point、左闭右开区间 `[start,end)`；validator 还检查必需字段、枚举、span 边界、节点引用/DAG、规则证据、`annotation_id` 唯一性，以及同 lemma/synset 不跨 split。schema 0.4 的每条 claim 必须给出非空且无重复的 `inference_basis`；`unclear`/`unassessed` 各自只能单独出现，且 `semantic_support=unassessed` 时必须对应 `inference_basis=["unassessed"]`。这只保证字段结构一致，不证明依据标签正确。对每条 rule claim，其引用公式子树中的每个节点 span 都必须被 claim `evidence_spans` 的并集无间隙覆盖；多段证据可以拼接覆盖。该约束保证每个 AST 节点的原文区间都有证据定位，但不证明这些字符在语义上支持公式。若提供可选的顶层 `provenance`，它必须是对象；其中若有 `source_records`，则每项必须含非空 `path` 和格式有效的 SHA-256，避免后续编译/组合路由对损坏元数据发生运行时崩溃。此结构检查不验证路径真实存在或许可证真实性。validator 不检查公式的语言学正确性、变量绑定语义、predicate 类型或来源许可真实性。双人独立标注应以不同 `annotation_id` 保存，裁决版另存。rule claim 可选包含 `nli_hypothesis` 和 `nli_hypothesis_sha256`；若提供，则必须同时提供，且 SHA-256 必须对应精确 hypothesis 字符串的 UTF-8 字节。它记录供 NLI 评分的候选句，不表示 gloss 已经蕴含该句。使用组合 NLI→proof 路由时，被证明 claim 必须有这两个字段。

### 实验性 0.5 类型声明

`0.5-draft` 的每条 `analysis.rule_claims[]` 增加必需字段 `variable_sorts`，例如 `{"?x":"Entity"}`。该映射必须与该 claim 公式子树实际出现的变量（包括量词 binder）精确一致；缺少、额外或格式错误的声明都会被拒绝。`annotation_to_datalog` 将该映射复制到其生成的每条规则，随后由 typed Datalog checker 按调用方版本化的 `type_system.sorts` 和谓词签名做兼容检查，并将它作为量化域约束。

该字段是人工/调用方声明，不会从 gloss 自动推断；annotation validator 只检查变量覆盖关系，不验证 sort 名称是否属于权威词汇本体，也不确认 sort 判断有原文依据。正式标注前仍需定义 sort inventory、标注指南和裁决规则。v3 的预注册草案、盲标输入和 0.4 回传格式保持不变；任何将 0.5 用于研究数据的决定都须在新一轮协议审阅/冻结中记录。

### 实验性 0.6 类型判断 provenance

`0.6-draft` 每条 claim 要求 `variable_sort_judgments` 精确覆盖公式变量，而不是只提供裸 sort 字符串。例如：

```json
{
  "?x": {
    "status": "assigned",
    "sort": "Entity",
    "basis": "gloss_span",
    "evidence_spans": [{"start": 2, "end": 6}],
    "rationale": "Synthetic example: the referent is interpreted as an entity."
  }
}
```

`basis` 可取 `gloss_span`、`lexical_semantics`、`resource_relation`、`reviewer_convention` 或 `unknown`。已赋 sort 需要 rationale；`gloss_span` 还要有有效 span。尚不能判断时可记录 `status=unresolved`、`sort=null`、`basis=unknown`、空 span 与非空 rationale。validator 接受 unresolved 以保存人工判断状态，但 compiler 会拒绝该 claim。已赋 sort 编译后变为规则的 `variable_sorts`；完整 judgment 和顶层 review status 一并写入 rule provenance，供证书重放。agreement analyzer v12 曾另报 variable-sort judgment multiset micro P/R/F1 与 item-bootstrap 区间；当前 v13 在保留该输出的同时支持 0.7 target-variable 对齐。status/sort/basis/span 纳入对齐标签，自由文本 rationale 保留给裁决、不作 exact-match 一致性标签。

0.6 只证明类型判断记录/传递/回放链条完整，不证明 basis、span 或 sort 判断本身正确。它是实验草案；当前 v3 标注仍使用 0.4，Phase 74 的 `Entity/Eventuality` 仍是假设。

### 实验性 0.7 显式目标变量与多元正 Horn

`0.7-draft` 保留 0.6 的完整 `variable_sort_judgments`，并要求每条 claim 声明 `target_variable`，如 `"target_variable":"?x"`。它必须在 claim 公式的原子论元位置自由出现；若同一变量 ID 也被量词 binder 使用，先 alpha-rename，否则 validator 拒绝。旧 schema 不猜测目标变量，继续走 compiler v6 中与 v5 一致的一元共享变量路径。

compiler v6 的 0.7 路径允许多元原子和常量，但仅限正 atom/AND/OR 子集：充分方向按有界 DNF 编成 `wn_sense:<id>(?x) :- relation(?x, ?y), property(?y)`；每个展开分支都必须含 `target_variable`，其余变量只能出现在 body，且每条生成规则的 sort 映射只含该规则实际使用的变量。必要方向只编 atom/AND，结论 atom 中除目标变量外不得出现其他变量，否则会产生普通安全 Datalog 无法表达的存在头；常量可参与参数。常量 ID 不得以 `?` 开头，该前缀保留给变量。谓词 arity、参数类型、常量 sort 与规则 sort 仍由调用方 type table 校验。

该扩展只扩大规则表示能力，不扩大逻辑语言：NOT、量词、IMPLIES、负谓词、等式、函数符号、充分方向不含目标变量的 DNF 分支、必要方向的 OR 和存在头仍拒绝。双向 claim 可逐方向编译并逐项报告拒绝；严格模式遇到任一拒绝时不接受整体输出。agreement v13 将 `target_variable` 纳入完整 claim signature，并对 0.6/0.7 sort judgments 使用同一字段对齐。0.7 目前是工程实验草案，未经协议审阅、真实标注或 gold 评测；形式类型检查和 proof replay 不证明 gloss 对规则的语义支持。

AST `kind` 的结构约定：`atom` 使用 `predicate` 与 `arguments`；`and`/`or` 使用至少两个 `children`；`not`、`forall`、`exists` 使用 `child`，量词再带 `binder`；`implies` 使用 `antecedent`/`consequent`；`unknown` 需带 `reason`。所有节点都带覆盖 gloss 原文的 `span`。变量 ID 和量词 binder 必须采用 `?name` 形式；量词按词法作用域解释，嵌套 binder 不得同名（需要 alpha-rename），同一根公式内的 DAG 节点不得在不同 binder 环境下共享。自由变量允许保留为开放公式参数，校验器不会猜测它是否是漏标的 binder；编译到正 Datalog 时，符合规则安全性约束的自由变量作为 Horn 规则变量处理。annotation validator 只做结构与 sort-map 覆盖检查，不确认谓词签名/论元 sort 对 WordNet 是否正确、量词语义是否符合 gloss 或公式的语言学正确性。compiler v6 对旧 schema 继续只接受共享单一变量的一元正谓词；实验性 schema 0.7 通过显式 `target_variable` 支持方向受限的多元正 Horn，不支持存在头、必要方向 OR、否定、量词或更广一阶逻辑。0.5–0.7 可经显式 type table 对声明的谓词参数位置做 sort checking，但权威类型本体和 gloss-source semantic support 仍待研究/验证。能力边界和论文主张限制见 [Source-only 证据链契约](source_only_evidence_contract.md#5-已有与待完成的-typed-horn-能力)。

校验命令：

```powershell
python -m src.logic.annotation_validator path\to\annotations.jsonl
```

## 3. 小样本试标与标注者手册

试标建议从 100–200 条开始，只用于测试边界、标注负担和字段缺口，不用于宣称性能。随机主样本按 POS、gloss 长度、逗号/分号标记分层，且刻意不使用图特征；独立诊断样本互斥地富集多 OR clause、全图最大 clause 宽度 P90+、以及在前两类之外的 selected-witness depth P90+，用于覆盖结构压力区。候选框还保存 clause 数、最大 AND 宽度、selected-witness 深度/宽度和 witness 引用复用度，但这些图特征不会展示给标注者。固定种子和完整 manifest 记录各层配额、输入图指纹与候选来源。诊断项不得混入总体性能估计；随机主样本提供不依赖冻结图复杂度特征的对照，减少只挑复杂/系统成功案例的偏差。

两名标注者先独立标注，且在第一轮不查看系统预测。分别报告（a）义项/证据 span，（b）AST 结构与逻辑方向，（c）定义性 vs 典型/百科属性，（d）Horn 可投影性四类一致性；类别型标签报告 Cohen's kappa 或适用的一致性指标，span/树结构另报告 span F1/结构匹配，不能用单一总一致率替代。分歧由第三方或会议裁决，并保留分歧原因。最终测试集按 lemma/synset 隔离，禁止同义项或同 lemma 衍生行跨 split。

现有实现 `src/analysis/annotation_agreement.py` 将两份独立 canonical JSONL 按 `item_id` 配对，并先重跑结构/hash 校验、要求每份文件各有一个独立标注者 ID，检查配对记录的 sense/source/gloss 相同。它报告 status 与 Horn-projection status 的 Cohen's κ、原始一致率/混淆矩阵、规则关系 presence κ、四种 `semantic_support` 状态各自的 item-level presence κ、AST 节点精确标注 span micro-F1、根 AST 结构匹配、规则 formula+direction 多重集 F1、证据 span F1 和完整 claim+evidence 一致性；schema 0.4 下完整 claim signature 纳入 `inference_basis`。旧 schema 记录没有该字段时按空集合比较，不会伪造历史标签。未配对条目单独计数。AND/OR 子节点次序按交换律规范化；AST 根结构对量词绑定变量做 alpha-normalization（以词法作用域中的 de Bruijn 距离表示），常量 ID 和自由变量 ID 保留，故绑定变量重命名不构成结构分歧，而自由变量更名仍会记录为分歧；node/claim IDs 不进入结构比较。节点精确 span 指标仍按原字符区间比较，不随变量绑定规范化。该规范化只检查 alpha-equivalence，不证明逻辑等价或 gloss 语义正确。证据 span F1 是精确边界匹配，不是字符重叠率。对配对 item 做固定 seed=20261003、1,000 次 paired-item percentile bootstrap，输出 95% 区间；κ 的 undefined bootstrap 重复次数单独报告。若所有 paired rows 都是同一类别导致 expected agreement=1，κ 返回 null 并注明 undefined，不用 1 冒充 κ。该工具衡量可复现性，不判断哪位标注者正确；当前尚无真实双人回传，因而没有实际一致性系数。

分析器现按 canonical record 中的 `provenance.sampling_panel` 分面报告；`random_stratified` 与 `diagnostic_not_for_population_estimates` 不会合并。v3 随机 panel 可在同时传入匹配的抽样 manifest 和盲标导出 manifest、完整回收计划样本、每条记录的 batch/frame hash 与 stratum 均通过校验后，报告 status、Horn-projection status、各关系 presence 和各 semantic-support presence 的设计加权 nominal Cohen's κ。权重为层内 `N_h/n_h`，点估计由加权联合分布及其边际计算；Taylor 区间采用分层 SRSWOR 一阶线性化方差与正态 Wald 区间。另有 `marginal_prevalence_by_annotator`，逐位标注者报告分析状态、Horn 投影状态、关系 presence 和 semantic-support presence 的设计加权边际比例、标准误及探索性区间；这些是独立标注者各自的描述分布，不代表共识/裁决真值，也不检验谁标得正确。比例区间是截断正态 Wald 边际区间，不是同时区间；非普查且估计方差为零时不输出退化区间，全普查才给精确点区间。基于 v3 设计的五种合成比例情景、每种 5 个有限总体及每总体 1,000 次抽样，Wald 区间在 p≈0.01 与层间异质场景的条件覆盖率约 89%–90%；logit/arcsine 对照各有未达名义覆盖的情景，所以工具对报告区间标为探索性并附警告，不据此声称替代区间已验证。复算结果与 Monte Carlo 不确定性见 [v3 抽样设计模拟记录](annotation_study_design_v3.md)。该实现把 survey-weighted agreement 方法推广到多分类联合单元；[Statistics Canada 方法论文](https://www150.statcan.gc.ca/n1/pub/12-001-x/2012001/article/11686-eng.pdf)研究的是二元结果，不能视为对本项目多分类代码的直接验证。 κ 区间仍不能作为确认性 95% CI；κ 的模拟及边界见 [v3 抽样设计与模拟记录](annotation_study_design_v3.md)。

设计加权 κ **不适用于 v2 的 160 随机项**：24 层中有 9 层仅抽 1 项且非普查，层内方差不可估；工具会拒绝此设计。诊断 panel 永远单独报告且无总体估计。AST/span/F1、未加权 κ 及固定 seed 的 paired-item bootstrap 仍是观测 panel 内的未加权探索性摘要，不能解释为总体估计或 design-based 区间。所有版本均须有完整双人配对回传才可计算加权结果；真实双人回传仍未提供。

正向 Datalog 编译器仅接收 `semantic_support=supported` 且置信度不低于 medium、关系/方向匹配、公式属于其受限可编译片段的规则。对 schema `0.4-draft`，每条待编译 claim 还必须有非空 `inference_basis`，且所有标签只能是 `lexical_or_paraphrastic` 或 `compositional_or_logical`；包含外部世界知识、语用、比喻、`unclear` 或 `unassessed` 的 claim 保留在输入标注和编译拒绝清单，不生成规则。旧 schema `0.2`/`0.3` 仍可读并保留编译器兼容性，但因缺少此依据字段，不能通过组合 reviewed route 的来源审查，需迁移并人工审阅后才可用于该路由。proof provenance 携带支持标签、confidence 与 inference basis。即便编译并通过 proof replay，也只验证推导遵守该人工输入，不会反向证明语义支持或推理依据判断正确。

两份独立标注的校验与一致性摘要：

```powershell
python -m src.analysis.annotation_agreement outputs/phase7/annotations_annotator_a.jsonl outputs/phase7/annotations_annotator_b.jsonl --output outputs/phase10/agreement_summary.json
# v3 完整随机 panel：另外绑定抽样框与盲标导出批次 manifest
python -m src.analysis.annotation_agreement outputs/phase7/annotations_v3_annotator_a.jsonl outputs/phase7/annotations_v3_annotator_b.jsonl --sampling-manifest outputs/phase7/annotation_candidate_frame_v3_400_manifest.json --batch-manifest outputs/phase7/annotation_batch_2025_plus_v3_400_manifest.json --output outputs/phase10/agreement_summary_v3.json
```

标注者应允许输出：`ambiguous`、`underspecified`、`not_a_definition`、`unsupported`、`source_unclear`。不要求每条 gloss 都产出规则。显式非 `annotated` 状态可以不提供 AST 节点或 root；选择 `annotated` 则必须提供非空 AST root。正确拒绝过度形式化是系统能力，不是标注失败。

## 4. 金标准和推理评测需分层

- **sense**：候选义项识别准确率；sense ID 不一致的下游样本单列。
- **证据对齐**：AST/rule 是否指向足以支持它的原文 span；报告 span precision/recall 和人工 source-faithfulness。
- **逻辑分析**：节点/边/变量/作用域准确率、整树 exact match、必要/充分/典型类别混淆矩阵。
- **投影**：可投影样本上的规则质量，以及 unsupported/partial 的覆盖率与拒答精度；不得只报告成功子集 accuracy。
- **证明**：输入规则正确性与 proof certificate replay 分开测。replay 只能证明推导遵守输入规则，不证明规则从 gloss 正确抽取。
- **NLI/上下位**：独立的双人自然语言判断金标准；以 lemma/sense 分组切 dev/test，dev 校准阈值，test 只评估；报告 macro-F1、各类 precision/recall、Brier/ECE（实现时定义）、coverage、abstention 和分层错误。

### 4.1 先单独建立 source-part 到活跃 graph-clause 的映射层

全量索引中 82,524/115,235 条来源记录的 parts 数与 sense 级 clause 数相等；v2 全量 lineage census 进一步发现 154,206 个 graph clause 均有至少一个来源链接，112,609 条 source records 实际关联活跃 clause，其中 83,241 条 parts 数与归属 clause 数相同。它们仍然只是结构计数/来源覆盖，不是 part-to-literal 内容匹配。再看现有 200-sense frame 内 201 条活跃来源，其中 188 条 DNF 分支数与归属 graph clause 数相等；但按 part WSD ID 集合映射后，仅 7 条来源的整组分支与归属 clause literals 完全相等。详见[全量 source-index 审计](../outputs/phase8/full_source_index_audit.json)和[抽样 source-clause 对齐审计](../outputs/phase8/source_clause_alignment_audit.json)。因此下一轮人工审查要独立记录映射，不得将 parts/clause 计数或 ID 集合相似度当作正确率。

建议为每个活跃 source × clause 关系标注一个独立记录：

- `source_path_hash`、`clause_index`、`part_id`、来源/图/解析器版本；对外报告中只保留哈希和聚合值。
- `mapping_status ∈ {exact, partial, none, ambiguous, unassessable}`，并允许一个 clause 对应多个 part、一个 part 扩展为多个 clause；不强制一一对应。
- `source_span` 指向 raw gloss，`part_span` 指向对应有效释义/part；记录转换前后文本版本，避免把改写片段误当 raw gloss 原文。
- `literal_evidence` 保存支持某个图依赖 ID 的原始 span、WordNet sense/POS 与 WSD 证据；`missing_literals` 和 `extra_literals` 分开记，不能只靠整体相似度掩盖方向错误。
- 语义核验另用独立、按 task ID 关联的记录判断原文是否支持该 dependency/branch 及其方向，枚举 `entailed / contradicted / underspecified / unrelated / uncertain`；不要将这个标签塞进 v0.1 的映射回传。证据映射正确并不自动表示规则在对象层面有效。

可执行的 v0.1 映射回收 schema 与校验器见 `src/logic/source_clause_alignment_validator.py`。每个 task 行须含 `schema_version=source-clause-alignment-task/0.1`、匿名 `task_id`、`raw_gloss`、`effective_definition`、局部 `parts[{part_id,text}]`、局部 ID 的 AND/OR `source_logic` 和单个 `graph_clause[{clause_index,literals[{literal_id,...}]}]`；标注回传只接受 `schema_version`、`task_id`、匿名 `annotator_id`、`mappings`、`unmapped_part_ids` 与 `notes`。每个 literal 恰好标一次；`status` 是 `exact / partial / none / ambiguous / unassessable`：exact 表示证据中的语义贡献足以支持该 literal，partial 表示只支持部分或范围更窄/更宽，none 表示找不到支持片段，ambiguous 表示存在不止一种合理映射，unassessable 表示文本/义项/版本证据不足。`exact/partial` 必须引用至少一个 part 和 raw/effective gloss 证据 span。offset 为 Python Unicode code point 的左闭右开区间。validator 检查任务/标注 schema、AND/OR 树是否恰好引用每个 part 一次、literal/part 引用、`part_text` 证据是否属于该 literal 声明的 supporting parts、证据范围、所有未映射 part 以及一人一批的完整回收；它不验证标签本身正确，也**不接受 entailment 字段**，从 schema 上避免把映射判断冒充为语义结论。

`src/analysis/export_source_clause_mapping_tasks.py` 已从现有 frame 导出 291 条本地任务（来源记录与 active clause 精确关联；6 条 source raw gloss 与官方 OEWN 发布版不一致的 active source 被排除）。任务展示系统 parts/logic 与图 clause，故它是错误分析标注，不是对模型输出设盲的 benchmark；sense ID、source path、pipeline status 和抽样 panel 被隐藏，任务顺序打乱。任务含来自混合冻结包的文本，目前只允许本地内部使用，不能对外分发；答案键单独保存。当前尚无人完成标注。

可选的定位辅助器 `src/analysis/suggest_source_part_spans.py` 对这些任务的 `part.text` 分别在 `raw_gloss` 与 `effective_definition` 中查找大小写敏感的精确子串，并输出 Python Unicode code-point 左闭右开偏移。对当前 291 条任务（696 个 part）的汇总结果是：raw gloss 中 291 个 part 唯一命中、405 个无精确命中；effective definition 中 292 个唯一命中、404 个无精确命中；没有多重命中。该结果**仅表示字符串定位**，不代表证据充分、part 语义正确或 source-part 与 graph-clause 映射成立；无命中可能来自改写/预处理差异。机器输出不包含 gloss 或 part 文本，仅含 task/part ID、状态、偏移和输入/输出哈希；文件受 `.gitignore` 保护。运行命令：

```powershell
python -m src.analysis.suggest_source_part_spans
```

任务文本本身仍是本地内部材料，禁止分发。人工映射时必须独立判断证据与语义，不得将此工具的精确子串命中直接转成 `exact` 标注。

分发前检查导出任务：

```powershell
python -m src.logic.source_clause_alignment_validator outputs/phase8/source_clause_mapping_tasks.jsonl
```

收到同一 annotator 的完整任务和回传文件后复核：

```powershell
python -m src.logic.source_clause_alignment_validator mapping_tasks.jsonl returned_mapping_rater_a.jsonl
```

首轮可作为错误分析而非性能估计：纳入审计发现的 13 条活跃来源分支数不匹配案例和 7 条 WSD-branch 与图 literals 完全匹配案例，并从其余 active/random-stratified 项中另取固定随机对照；来源映射审核者先不查看 pipeline verdict。报告各映射类别、source span 覆盖、缺失/多余 literal 率与双人一致性；此有意富集的批次不能报告 population accuracy。之后再另行冻结足量、按 sense/lemma 分组的随机金标准用于性能比较。

必须包含的反事实/压力样本：并列定义、定义分支、负向/限制词、比较级/程度、隐含论元、循环/互指定义、派生定义、典型属性、义项近邻混淆、缺失原语和来源冲突。错误标签至少区分 sense、span/parse、规则方向、逻辑范围、知识缺口、proof checker 和 NLI/human judgment。

## 5. 与当前代码的接口和退出条件

首版不要把完整 AST 塞入现有 Datalog checker。独立 validator 检查记录与 span/node 引用后，`src/logic/annotation_to_datalog.py` 可将规范记录中人工明确声明的部分规则编译到有限正 Horn 子集；必要方向仅支持 atom/AND，充分方向支持 atom/AND/OR 的有界 DNF。编译器对不支持结构逐 claim 记录拒绝原因并保留源记录。输出是规则库，尚需 ground facts/query 才能调用 proof checker。当前实现是接口原型；Gold slice 双人试标、裁决和真实 WordNet 语义验证仍未完成。

OEWN 上游的 CC-BY 4.0 和归属要求已从官方仓库核对，但冻结包内其他来源、准确 OEWN release 和改写文本的逐条许可仍未确认；边界见[数据来源与公开限制](data_provenance.md)。开始正式标注前须完成该审计，并冻结抽样清单、标注手册、split、baseline 版本、主要指标、阈值选择规则和排除准则。首个数据发布必须去除个人身份信息、公开标签定义与变更记录，并提供原始独立标注、裁决结果和校验脚本。

## 6. 当前 pilot 输入文件

`export_annotation_batch` 会将 cross-check 的 sense/source-payload 级 raw/effective 发布版匹配状态只写入隐藏答案键；导出时逐条验证 source-payload SHA-256 与 frame 来源记录一致。标注回传导入后，这些状态进入 canonical provenance，供区分来源版本/预处理差异与后续解析、逻辑化、推理错误。它们不会暴露在盲标文件中；旧 `/1` cross-check 若缺少 source-payload 级证据，会在答案键中标为 `not_in_legacy_crosscheck`，不得当作有效释义一致的证据。

`outputs/phase7/annotation_batch_2025_plus_blind.jsonl` 是保留的 `/1` 版 200 条随机打乱任务，字段只有 `task_id`、`pos`、`lemmas`、`gloss`；不含 sense ID、依赖图特征、panel 或 stratum。它含 160 条分层随机项和 40 条旧版诊断项（20 多 clause OR、20 高最大 AND 宽度），没有 witness-depth 富集。该版及其答案键、manifest 均保留，不能与新版混成同一评测批次。

`/2` 版本已在独立路径生成，候选帧为 `outputs/phase7/annotation_sampling_frame_v2.jsonl`，release cross-check 为 `outputs/phase7/oewn_2025_plus_release_crosscheck_v2.json`，盲标文件、答案键和 manifest 分别为 `annotation_batch_2025_plus_v2_blind.jsonl`、`annotation_batch_2025_plus_v2_answer_key.json` 和 `annotation_batch_2025_plus_v2_manifest.json`。共 200 项：160 条分层随机主样本，以及互斥的 40 条诊断样本（多 OR 14、高 AND 宽度 13、高 witness depth 13）；这些诊断样本用于错误分析，不并入总体性能估计。`/2` cross-check 中 200/200 条 raw gloss 与固定 OEWN 2025 Plus 发布版逐字匹配；其中 193/200 条 effective gloss 也匹配，另有 7 条 graph/effective definition 与官方原始释义不一致（随机 5、诊断 2）。交叉核验 JSON 对每个 source payload 保留 SHA-256、文本长度、字段有无/空值、raw/effective 与发布版的精确/规范化匹配状态及二者是否相同，但不输出释义文本，使 mismatch 可按 frame 中的 source hash 回溯而不把文本写入报告。当前 7 条中，6 条是 raw match 但同记录 effective 不匹配；另 1 个 sense 有两条来源记录，其中一条 raw match 对应空 effective 字段。它们是版本/预处理证据，不据此判定语义错误，也不静默删除；后续须结合来源 lineage 与人工证据映射调查。盲标任务仍只显示 POS、lemma 和官方 raw gloss；结构特征仅在答案键中，合并回传后进入 canonical provenance，方便按图复杂度分层分析而不破盲。

文件职责：

- `annotation_batch_2025_plus_blind.jsonl`：可以发给标注者的任务输入。
- `annotation_batch_2025_plus_answer_key.json`：隐藏映射及来源证据，只由数据管理员保管。
- `annotation_batch_2025_plus_manifest.json`：来源归属、许可、输入 frame/cross-check 哈希、导出文件哈希与用途限制。

从冻结包重建 `/2` 候选帧、固定 OEWN release cross-check 和盲标批次的完整复算命令如下。frame manifest 会保存候选数及 frame 字节 SHA-256；cross-check 绑定同一 frame 哈希；最后的 pilot manifest 再绑定 cross-check、blind batch 和隐藏答案键哈希。项目 `tmp/` 中的 OEWN cache 是此本地复算的输入，不随输出分发：

```powershell
python -m src.analysis.annotation_sampling `
  --output outputs/phase7/annotation_sampling_frame_v2.jsonl `
  --manifest-output outputs/phase7/annotation_sampling_manifest_v2.json --force
python -m src.analysis.oewn_release_crosscheck `
  --frame outputs/phase7/annotation_sampling_frame_v2.jsonl `
  --release-dir tmp/oewn-2025-plus-json `
  --release-archive tmp/oewn-2025-plus-json.zip `
  --release-name 'Open English WordNet 2025 Plus' `
  --release-date 2025-12-31 `
  --release-uri https://en-word.net/static/english-wordnet-2025-plus-json.zip `
  --output outputs/phase7/oewn_2025_plus_release_crosscheck_v2.json --force
python -m src.analysis.export_annotation_batch `
  --frame outputs/phase7/annotation_sampling_frame_v2.jsonl `
  --crosscheck outputs/phase7/oewn_2025_plus_release_crosscheck_v2.json `
  --batch outputs/phase7/annotation_batch_2025_plus_v2_blind.jsonl `
  --answer-key outputs/phase7/annotation_batch_2025_plus_v2_answer_key.json `
  --manifest outputs/phase7/annotation_batch_2025_plus_v2_manifest.json
python -m unittest tests.test_export_annotation_batch -v
```

覆盖输出需显式加 `--force`。`/2` 导出时须显式传入对应的 `/2` frame、cross-check 和输出路径，避免 CLI 默认路径误覆盖 `/1`。必须由两位标注者分别持有同一份 blind batch，使用不同匿名 annotator ID 独立提交；不得先分享答案键或旧图输出。每位标注者返回一个 JSONL 行/task，字段为 `task_id`、`annotator_id`、`analysis`、`notes`；`analysis` 的结构与上文规范记录一致，`split` 不由标注者决定。合并命令会验证 batch/key/manifest 哈希、task-ID 完整性和唯一性，将 ID 与来源恢复到规范记录，强制 `adjudication_status=independent`、`split=unassigned`，并运行结构 validator：

```powershell
python -m src.analysis.import_annotation_returns returned_annotator_a.jsonl `
  --batch outputs/phase7/annotation_batch_2025_plus_v2_blind.jsonl `
  --answer-key outputs/phase7/annotation_batch_2025_plus_v2_answer_key.json `
  --manifest outputs/phase7/annotation_batch_2025_plus_v2_manifest.json `
  --output outputs/phase7/annotations_annotator_a.jsonl
python -m src.logic.annotation_validator outputs/phase7/annotations_annotator_a.jsonl
```

v3 回传须显式传入 v3 的盲标 batch、答案键与 manifest，输出到独立 canonical 文件，不能误用 `/2` 默认路径：

```powershell
python -m src.analysis.import_annotation_returns returned_v3_annotator_a.jsonl `
  --batch outputs/phase7/annotation_batch_2025_plus_v3_400_blind.jsonl `
  --answer-key outputs/phase7/annotation_batch_2025_plus_v3_400_answer_key.json `
  --manifest outputs/phase7/annotation_batch_2025_plus_v3_400_manifest.json `
  --output outputs/phase7/annotations_v3_annotator_a.jsonl
```

导入器默认生成 `0.4-draft`，保持现有盲标批次行为。只有返回的 `analysis` 已满足所选 schema 的 claim 字段要求时，才可显式选择实验性 canonical schema；例如 0.7 要求每条 rule claim 提供 `target_variable` 与完整 `variable_sort_judgments`：

```powershell
python -m src.analysis.import_annotation_returns returned_annotator_a.jsonl `
  --batch path\to\new_blind_batch.jsonl `
  --answer-key path\to\new_answer_key.json `
  --manifest path\to\new_manifest.json `
  --canonical-schema-version 0.7-draft `
  --output outputs\experimental\annotations_annotator_a_schema_07.jsonl
```

该选项只控制导入后的结构校验版本，不生成或冻结 0.7 标注任务，不会改写 v3 lock，也不证明标注者已被训练或新 schema 已获协议批准。当前锁定 v3 回收材料仍为 `0.4-draft`；任何真实 0.7 盲标批次须另行冻结任务说明、字段示例、类型判断指南和回收计划。

每位标注者使用独立输入/输出文件和 pseudonymous ID；答案键由项目负责人单独保管。回传 JSONL 的最小行格式如下（示例中的 unknown 节点仅表示人工选择 needs-review 时如何保留 span，不是真实标签）：

```json
{"task_id":"WN-0001","annotator_id":"annotator-a","analysis":{"status":"needs_review","nodes":[{"id":"u1","kind":"unknown","reason":"unresolved parse","span":{"start":0,"end":12}}],"root_node_ids":["u1"],"rule_claims":[],"horn_projection":{"status":"not_attempted","rule_ids":[],"omissions":[]}},"notes":[]}
```

### `/3` 候选确认性标注批次

另行生成的 `annotation_candidate_frame_v3_400.jsonl` 是 400 条随机候选，按 24 个 POS×释义长度×标点 strata 抽样，每层至少 2 条；`annotation_study_design_v3.md` 记录抽样事实和待实现的设计加权估计。固定 OEWN 2025 Plus release cross-check 显示 400/400 raw gloss exact，effective definition exact 为 376/400；盲标文本采用官方 raw gloss，不使用改写后的 effective definition。导出文件为 `annotation_batch_2025_plus_v3_400_blind.jsonl`，标注者只见 `task_id`、`pos`、`lemmas`、`gloss`；隐藏答案键和含 attribution、hash、版本匹配证据的 manifest 分别为同名前缀的 `_answer_key.json` 与 `_manifest.json`。三者均在本地 `outputs/phase7/`，且被 `.gitignore` 排除；答案键不得发送给标注者。回传时按上一段示例改用 v3 的三个输入路径及不同的输出文件名。该批次还没有任何标注回传，也没有完成 preregistration 或发布许可审查。

合并工具仅验证格式、来源映射和任务完整性，不判断人工语义标签是否正确；输出保留 `split=unassigned`，并记录逐 gloss UTF-8 SHA-256、来源记录哈希、抽样 panel/stratum、图结构特征、raw/effective 发布版匹配状态、发布版归档哈希和 blind batch 哈希。双人完成后仍须分层计算一致性并裁决，再分配 lemma/synset-isolated splits。合并器测试：

```powershell
python -m unittest tests.test_import_annotation_returns tests.test_annotation_validator -v
```

### Phase 122：多参考 scorer 与确认性 estimand 静态审计

对照当前 `src/analysis/score_gloss_analysis_references.py`、`src/logic/gloss_analysis_reference.py`、输入锁与 preregistration v3 草案，确认 scorer 对每个 `complete` item 分别比较整套 accepted alternatives，按规则 claim multiset F1 最高项选 reference；并列优先 whole-analysis exact，再按 alternative ID 排序。它不把 references 的 claims 取 union；claim exact match、root AST exact、analysis-status match 分别可见，overall exact match 要求三者全部成立。它只评分规则结构，不评分 evidence span、source support correctness 或 NLI。

这套逻辑与协议的“多参考不可合并、逐项最佳匹配”描述基本一致，但它估计的范围必须严谨写成“在 sidecar 已收录的可接受 reference 中，resolved items 的 per-item best-match 描述性分数”：

1. **多参考选择必须预测盲化并完整冻结。** 如果 adjudicator 在查看某模型输出后新增 accepted alternative，该模型会得到不对称优势。Sidecar 的格式校验无法证明 accepted set 穷尽或裁决者未见预测；这些是流程/访问控制证据，必须预先写入执行记录。Best-of-reference 有意承认多个合法形式化，但数值会高于或等于单参考严格匹配，不能单独宣称“唯一正确形式”或普遍模型性能。
2. **未决裁决项不进入 claim score 或 exact-match 分母。** scorer 输出 `unresolved_rate` 和计数，但该 rate 是未加权的；若难例更可能 unresolved，resolved-only score 只能解释为条件于裁决完成的结果。发表时必须同时给出完整测试项、resolved/unresolved 分母与原因、分层完成率/未决率；不能只报 resolved score，也不能把其外推为原始目标总体的表现。
3. **Macro 分母随预测而变。** 实现将 claim comparison 的空/空 item 从 macro P/R/F1 分母排除；当一套 reference alternatives 中包含空 claim set 时，不同预测可能改变哪些 item 进入 macro。故 per-system macro 可作为描述值，但跨系统 paired claim 不应只比较该 macro；须同时报固定分母的 exact-match（所有 resolved 项）与 micro 指标。若要做 macro 的模型间差异检验，先预定义仅由 reference/test frame 决定的共同 item 子集，并让所有系统使用同一分母。
4. **当前输出不是总体推断。** 协议已说明 scorer micro/macro 未加抽样权重；test set 的 split、lemma-group 隔离、selection rule 与 estimator 必须先冻结。若要外推至抽样目标总体，需要预先定义设计权重与 cluster-aware uncertainty estimator；不能把 400 项一致性/释义分析样本自动当作 400 项模型测试集。
5. **“最佳备选”只处理 claim multiset。** 证据 span、gloss 对规则语义支持、source-only proof replay 和 NLI 都需独立指标与其自身 gold；语法/结构一致不能代替它们。

当前 draft 尚未决定确认性研究采用单一裁决 reference 还是多参考 sidecar；Phase 122 不替研究者选择，也未更改 scorer。启动模型对比前应先由研究者选择并锁定 estimand、sidecar schema/hash、prediction-blind adjudication 流程和模型比较分母，再在 synthetic fixtures 上检查 scorer 行为。此次是代码/协议静态审计，没有运行 tests、CLI、gold 或模型预测。详见Phase 122 深度报告。

## Phase 140：当前 blind batch 的适用轨道核查

2026-10-08 对 v3/400 blind 输入、返回 importer、validator 和 presentation manifest 作只读核查。输入只显示 `task_id`、POS、lemmas 与 raw gloss；返回结构可装载带原文 span、方向性规则与 `semantic_support` 的人工分析，因此它适用于未来 Track C 参考集收集（须先锁协议并完成双标裁决），而非已经存在 gold。它不包含冻结的 `(gloss, directional hypothesis)` 候选对，所以不能直接作为 Track A NLI 基准；Track B 也须在裁决后单独固定 formal program/facts/query。presentation order 完整复算通过，但 `distribution_authorized=false`。另外，输入 lock 没有绑定 annotation protocol/schema 哈希，validator 接受多个 draft schema；正式标注前必须选定一个版本并建立新的 lock/签署协议。不得将此审计解释为授权或分发指令。详细证据见Phase 140 报告与[机器审计](../sources/annotation_batch_fitness_audit_2026-10-08_phase140.json)。

### Phase 144：v3 target metadata 与 pinned release 身份核查

新增只读审计命令 `python -m src.analysis.audit_annotation_frame_release_identity`，验证 v3 输入锁中的 7 个 artifact、固定 OEWN 归档及 45 个 taxonomy/27 个 entries 文件，再逐 sense 比较 POS 与完整 lemma set。结果为 400/400 sense ID 可在该 release 找到、400/400 raw gloss cross-check 精确，但 1 项 POS 不一致（`oewn-00240685-r`：frame/source payload 为 `a`，release 为 `r`），另 1 项 frame lemma set 不完整（`oewn-12400298-n`：frame 1 个、release 2 个）。盲批与 frame 一致地复制这两项元数据，因此 blind/frame 一致不能证明对 release 的身份字段完整。

v3 frame 的 POS 来自冻结 graph nodes；lemma list 取首个匹配的 source record，既未由 pinned release 规范化，也未校验完整 lemma set。保留已锁定 v3 文件原字节，不作静默修复。新建 Track A 输入时应按 sense ID 从 pinned release 重取 POS 与全部 lemma，并分别保存 raw-gloss hash、rendered-premise hash。311 个 parent synset 中 172 个有多个 lemma surface；须先冻结 parent lemma 到 hypothesis 的表示策略。OEWN hypernym 关系只用于候选构造/分层，不是 NLI 或 gloss-support gold。当前没有生成 pair、标签或 split；原始 batch 仍 0 回传且未获分发授权。审计细节见Phase 144 报告、[机器审计](../outputs/phase144/annotation_frame_release_identity_audit.json)和[输入清单](../sources/track_a_pair_frame_input_inventory_2026-10-08_phase144.json)。
