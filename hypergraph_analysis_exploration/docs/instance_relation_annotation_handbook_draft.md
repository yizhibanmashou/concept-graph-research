# Instance-to-class pair 标注手册（草案）

状态：供协议审阅的工作稿；未签署、未注册、未冻结、未试标，也不是外部标注指令。它只适用于 Phase 78 的 relation-pair 研究，不覆盖既有 400 条 single-sense gloss-formalization batch。当前授权锁仍为 `protocol_signed=false`、`distribution_authorized=false`。此文档不授权抽取、导出或分发 OEWN 文本。

## 1. 研究问题与两个独立判断

每条任务是一条有方向的候选：给定 instance sense `I` 和 class sense `C`，评估 `I instance_of C`。标注者分别回答两个问题，不能用同一个标签代替：

1. **Sense relation**：按两个指定义项理解，`I` 是否确实是 `C` 所表示类别的成员？这是关于两个 sense 的关系判断，可依赖标注者已有的一般语言/世界知识；不得查看 WordNet 关系图、系统输出或本项目 sampling strata。建议禁止在线检索和临时引入外部 reference；若判断必须依赖当前任务未提供、也无法从稳定常识确定的信息，选择 `cannot_determine`，并说明缺少什么。
2. **Strict gloss support**：仅凭任务展示的两条原始 gloss，是否足以支持有向 claim “instance gloss 所描述的对象属于 class gloss 所描述的类别”？不得调用外部事实、资源中的 relation edge、checker/proof、NLI 分数或 annotator 常识来补足 gloss 中缺失的内容。若结论依赖这些外部信息，不能标为 `supported`。

这两个量不互相蕴含：现实关系为真，不表示 gloss 已支持；资源图有边，也不决定任一人工标签。

## 2. 任务呈现和盲化

未来任务包经许可审核后，只展示随机 task ID、两个 sense 的 lemma/POS/gloss、方向说明和本手册允许的标注字段。任务应明确哪个 sense 是 instance、哪个是 class，否则有向问题不可判断。可以把角色标作 A（instance）和 B（class），但不得暴露 synset ID、候选 stratum、直接边/提升路径/闭包状态、source relation、图特征、模型预测、生成规则或 witness/proof。候选顺序和随机 task ID 不携带这些隐藏信息。

标注者不得查询隐藏 key、关系 verifier/replayer 输出、已有盲标答案键或其他标注者记录。两位标注者独立完成并提交锁定后，才能开始分歧裁决。任何 task 若因文本损坏、缺字段或界面问题无法处理，记录 workflow issue 并暂停该条，不推测标签。

## 3. Sense relation 标签

每项选一个标签：

- `yes`：给定的 instance sense 所指对象确实属于 class sense 指定类别；须有肯定依据，而不能仅因资源闭包可达或没有发现反例。
- `no`：有依据判断该对象不属于这个 class sense。仅仅“不知道”“资源里不可达”或“gloss 没提到”不够。
- `uncertain`：存在至少两种合理的 sense/关系解释，或依据互相冲突，且不同解释会改变 yes/no 结果。说明候选解释与造成歧义的片段/背景。
- `cannot_determine`：现有任务信息不足以确定所指对象或成员关系，且无法给出有把握的 yes/no；这不是“不支持”或负例。

`basis` 记录作出 relation 判断时实际依赖的依据码：`gloss_only`、`lexical_or_paraphrastic`、`external_world_knowledge`、`insufficient_context`、`unclear`。可并列多个实际必要依据，不要为了填满字段勾选未使用依据。若标 `gloss_only`，两条 gloss 都要提供证据 span。对 `no`，必须写出支持非成员判断的理由；闭包不可达不是这种理由。

`confidence` 是对该项标签的把握程度（high/medium/low），不是标签为真的概率。低置信度本身不等于 `uncertain`。

## 4. Strict gloss-support 标签

只问两条 gloss 是否共同许可完整的有向 claim，包括关系、方向、类别意义和适用范围：

- `supported`：所有必需内容都可从两条 gloss 按 `lexical_or_paraphrastic` 或 `compositional_or_logical` 推出，且无缺失限定、否定、范围/指称问题。两条 gloss 各标至少一个最小充分 evidence span。
- `not_supported`：释义可理解，但它们没有许可完整 claim；包括缺少关系内容、claim 过强、方向/运算符/范围不符或源内容冲突。它表示“这些 gloss 没支持”，不表示现实关系为假。若只有外部知识能补齐关系，选此标签并记录 `external_world_knowledge` basis 与原因。
- `uncertain`：两条 gloss 存在未能消解的词义、指称或范围歧义，且合理读法会改变支持结果。记录歧义位置和各读法。
- `unassessed`：工作流尚未作出语义判断；不得当作负例、计入已裁决支持率或编译为规则。

原因码按当前 validator 约束填写：`not_supported` 使用 `content_not_licensed`、`claim_overstates_or_omits_qualifier`、`direction_mismatch`、`operator_or_scope_mismatch`、`source_conflict` 或 `other`；`uncertain` 使用 `lexical_or_sense_ambiguity`、`scope_or_reference_ambiguity`、`insufficient_context` 或 `other`。`supported` 与 `unassessed` 不填原因。`inference_basis` 表示该判断实际所需的推理种类；`supported` 只能使用 gloss-grounded 的 lexical/paraphrastic 或 compositional/logical basis。

## 5. spans、rationale 与记录

- 原文按任务包展示的精确字符串定位，不做大小写折叠、Unicode 归一化或标点清理；offset 是 Python Unicode code point 的左闭右开 `[start,end)`。
- 两条 gloss 使用独立坐标空间。只框出支持所选判断所需的最小完整片段；关系由多个片段组合表达时允许多个 spans。限定词、否定词、量词或情态若影响 claim，必须包含在证据或 rationale 中。
- evidence span 是定位，不是证明；标注者必须给每种判断填写自己的非空 rationale。rationale 以简短解释为主，不重复粘贴整条 gloss，也不要写入个人身份信息。`uncertain` rationale 说明分歧读法；`cannot_determine`/`unassessed` 说明缺失信息或未完成原因。
- 结构记录使用 `wordnet-instance-relation-annotation/0.2-draft`。每条标注单独一行；annotation ID 唯一。独立记录不可覆盖；裁决另存并保留双方原始行。validator 只检查结构、哈希、offset 和字段一致性，不判断 rationale/span 是否在语义上正确。
- 可运行的格式样例位于 `tests/fixtures/instance_relation_annotation_0_2_synthetic.json`；其中 gloss、ID、source 均为 synthetic-only，不是 OEWN 数据或人工标注结果。

## 6. 双标、裁决与报告建议

1. 两位标注者对同一冻结 pair frame 独立标注，先完成所有记录再开展讨论；不显示模型/图信息。
2. 裁决者查看两份原始标注与 gloss，但不查看隐藏 sampling stratum、图状态或系统预测；逐项给出裁决标签、rationale 和对 span 的处理，并保留原始分歧。
3. 报告 sense relation 与 gloss support 两个任务各自的标签混淆表、原始一致率、类别分布、置信度、未决/无法判断比例。类别不平衡时不只报单一 kappa；同时列出适用的一致性统计及其定义/区间。
4. 报告按五个预设 stratum 分层结果。direct/lift-1/lift-2+ 可在预先冻结的目标总体下按 pair population 权重汇总；reverse-direct 和 same-POS nonclosure 是独立 challenge strata，不并成朴素 pooled accuracy。challenge strata 是资源结构抽样，不是真值负例。
5. span 指标采用 item 内、按两个 gloss 分开的精确边界与预先定义的重叠指标；先说明一对多 span 匹配方法。不要把“span 重叠”解释成语义充分。
6. 不将裁决共识称为无误真值。任何系统比较都要报告覆盖率/abstention、未决项处理、分层估计/区间，并把 resource agreement、sense relation、gloss support、NLI 和 certificate replay 分轴呈现。

## 7. 签署前必须决定的事项

下列项目尚未由本草案决定，不能由执行者在标注后追认：

1. 许可与 attribution 是否覆盖两个 sense 的 lemma/gloss 组合、保存期限、标注平台和可公开字段。
2. `no` 的可接受证据标准，以及既有知识/在线检索边界；本稿建议不允许在线 lookup，须由研究负责人确认。
3. frame 外试标规模、完成时间记录、排除与重训规则；不得把试标数据并入正式估计。
4. 两位标注者的资格、利益冲突、保密/数据处理要求和裁决人安排。
5. 主要 estimand、正类 stratum 加权目标、区间方法、未回收项/未决项处理、最小可报告分母和停止规则。
6. 与当前 single-sense v3 protocol 的边界、是否另行 preregister、版本号和签署人。

在上述事项解决、pair schema 通过合成验证、frame 哈希固定且 lock 明确授权之前，不生成含 OEWN 文本的 task packet、不外发、不启动正式双标。当前 320 个 text-free IDs 与 hidden key 保持不变。
