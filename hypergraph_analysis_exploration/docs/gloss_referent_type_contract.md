# Gloss-derived Horn 变量的 referent/type 契约草案

状态：**实验性语义设计，不是已批准 ontology，也不是已评测类型系统。** schema `0.6-draft` 已能记录每项变量 sort 判断的 status/basis/rationale/evidence spans；新增 `0.7-draft` 另要求显式 `target_variable`，但这些字段均不证明判断正确。在专家审阅和人工 gold 验证前，不得把示例 signature 写成 WordNet 的权威语义。

## 1. 分离三个对象层

1. **Lexical sense / synset**：被定义的词义及其 release-bound ID，是 lexical predicate/claim 的来源身份，不是公式变量所指的个体。
2. **Referent variable**：在 unary Horn 片段中，`?x` 暂解释为目标 lexical predicate 的一个可能指称对象。对 noun 常见为实体，对 verb 常见为事件/状态；这是建模约定，必须逐 claim/sense 允许覆核，不能只凭 POS 或 lexname 判定。
3. **Sort**：限制上述 referent 的有限 Herbrand 变量域。它不是 synset 间的 `hypernym` 边；checker 只核验调用方给定的 sort/signature 内部一致性。

因此 `blacksmith(?x) -> person(?x)` 的 `?x` 是一个候选实体，而 `blacksmith` / `person` 是由词义身份绑定的 unary predicates。不能将 `?x` 填成 WordNet synset ID，也不能把 `noun.person` lexname 当成 `Person` sort 的证据。

## 2. 最小实验性域

建议只用 `Referent` 作为根 sort，并允许两个**可重叠、默认不声明互斥**的粗粒度子 sort：

| 候选 sort | 变量指称 | 初始使用边界 |
|---|---|---|
| `Entity <: Referent` | 个体、物、地点、组织，以及被当作 bearers 的对象 | 普通实体名词；形容词如确实描述实体属性时可用。事件名词、抽象属性名词须逐 sense 判断。 |
| `Eventuality <: Referent` | event、process、state 等事件语义对象 | verb sense 的 unary event-property 投影；eventive noun 可逐 sense 选用。sentence adverb、proposition 等不适合该片段时标 `unsupported/needs_review`。 |

不新增 `Person`、`Animal`、45 个 lexname 或 POS 子 sort。它们可作 predicate label、来源属性或错误分析 strata；若未来要做细类型，必须有独立、版本化、可审查的来源和类型标注数据。当前 checker 使用有限 Herbrand 常量域：不同常量符号是不同 Herbrand 元素，且不支持 equality；但同一常量可在 `constant_sorts` 中声明多个 sort，系统也没有兄弟 sort 的 disjointness 约束。因此本草案不宣称 `Entity` 与 `Eventuality` 互斥。

### 标注决策规则

- `variable_sorts` 的 sort 表示 referent domain，不表示词条分类标签。
- 每个编译 claim 的变量 sort 须由标注者按该 sense 的定义/用法作出，并记录理由；POS 只可作为候选提示。遇到 eventive noun、多义的类型转换、adverb 对整句命题的修饰或无法确定的变量指称时，不猜测，退到人工复核/不编译。
- 对 schema 0.2–0.6 全由同一个 `?x` 共享的 unary atom，predicate signatures 必须接受该 sort 或其父 sort；compiler v6 为 schema 0.7 增加显式目标变量及有限的多元正 Horn 片段。充分方向可用 body-only 变量并逐规则筛选 sort map；必要方向不允许目标之外的 consequent 变量，以避免把存在头伪装成安全 Datalog。其它量词绑定与超出片段的结构仍须明确拒绝，而不是压成 unary atom。
- sort 赋值的 provenance 应绑定到标注者/裁决状态、依据类型、sense/release、schema 与 signature-table hash。0.6-draft 已保存判断 status/basis/rationale/span，并在编译规则中带出该判断及 review status；release/sense 仍由 annotation source 字段承载，signature-table hash 则在 Datalog 证书侧绑定。该拆分只保证来源字段不丢失，不认证依据/类型判断。

## 3. 资源关系不得自动变成变量类型

- noun/verb `hypernym` 是 synset 关系；它可产生 resource-relative lexical relation 结果，但不能仅因有边就自动成为 gloss-supported Horn rule。动词层级还涉及对 event manner 的细化。
- `instance_hypernym` 保持独立。把 WordNet 中的 instance synset 映为现实 referent 常量、singleton class，或一元类 predicate 的成员，属于额外建模选择；当前 OEWN relation record 本身不足以选择其中一种。
- POS/lexname 仅是 release-bound provenance/分层字段。WordNet 的 noun/verb/adjective/adverb networks 与关系类型并不构成一个统一变量 sort lattice；W3C WordNet RDF mapping 也明确说明该映射没有把 hyponym hierarchy 建模成 OWL subclass hierarchy。

因此需要分别报告：（a）输入 lexical resource 中的 synset relation；（b）人工 claim 的 referent sort 和 predicate signature；（c）Datalog 在有限常量域上对所声明类型表的 replay。三者之间的转换必须有显式 adapter 和评测，不得通过“类型检查成功”闭合语义证据链。

## 4. 编译器可支持与不能声称的事情

compiler v5 对旧 schema 继续支持共享单变量的一元正 Horn claim；compiler v6 对 schema 0.7 接受显式目标变量的受限多元正 Horn 规则。0.6/0.7 的 assigned judgment 会作为 provenance 保留，unresolved 不会编译；0.7 每条规则的运行时 sort map 仅保留该规则实际用到的变量。checker 会在调用方 `constant_sorts` 声明的有限域内 grounding，并以 type-table hash 绑定证书。由此可以验证“该有限程序在给定签名下可类型检查/可回放，且被记录的 sort judgment 未在编译链条中丢失”。

它不能证明：sort 判断正确、谓词真值覆盖了所有可能 referents、定义方向被 gloss 支持、开放世界下 claim 为假，或 WordNet taxonomy 就是该 referent domain 的完备实例集合。当前 finite typed Datalog result 仅对所给程序和有限 Herbrand universe 有效。

## 5. 验证门与否证条件

启用研究型 typed gloss evaluation 前，至少需要：

1. 为多 POS、eventive noun、state verb/adjective、sentence adverb、instance synset 与词义近邻设计挑战样例，由两名标注者独立给出 referent domain 和理由并裁决；
2. 报告 `Entity / Eventuality / unknown-or-out-of-fragment` 的一致性、分 POS/定义模式错误，以及 sort 错误对 proof/countermodel route 的影响；
3. 对每条 predicate signature 与 variable sort 绑定 provenance；unknown 类型不得静默退化为宽泛类型后继续计作 source-supported；
4. 在真实回收的 gloss-support gold 和同候选 matched baselines 上证明 typed 路径减少类型错误且不损害 source-support 风险—覆盖。否则类型系统只可称为输入契约/工程原型。

## 6. 相关工作与贡献边界

Rademaker et al. (GWC 2023) 已将 Princeton WordNet gloss 的上下文 sense annotation 投射到 ERG predicates，以构建深层语义表示；此前 Gloss Corpus 项目也建立了 gloss token 到上下文 WordNet sense 的人工连接。因此，本项目不能将 “为 WordNet gloss 做 semantic parsing/WSD” 或“形成 predicate 表示”单独作为新贡献。候选差异仍需在系统检索和实测后判定，暂限于一个待验证问题：sense/release-bound claim 的**方向性 source-span support**能否与类型化、AND/OR 保真的 Horn 规则和独立证书回放形成可评测组合。

来源：[GWC 2023 论文](https://aclanthology.org/2023.gwc-1.30/)、[Princeton WordNet 结构与 relation 说明](https://wordnet.princeton.edu/)、[W3C RDF/OWL WordNet 映射](https://www.w3.org/TR/wordnet-rdf/)。
