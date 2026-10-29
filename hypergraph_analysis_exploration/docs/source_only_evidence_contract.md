# Source-only 证据链的可声明范围与最小审计契约

**状态：方法/工程边界说明，不是语义有效性结果。** 本页将当前代码能验证的对象、所依赖的人类判断与尚未建立的论文证据分开。接口依据为 [`verified_reasoning_pipeline.py`](../src/logic/verified_reasoning_pipeline.py)、[`source_record_verifier.py`](../src/logic/source_record_verifier.py)、[`annotation_validator.py`](../src/logic/annotation_validator.py)、[`annotation_to_datalog.py`](../src/logic/annotation_to_datalog.py) 和 [`datalog_checker.py`](../src/logic/datalog_checker.py)。

## 1. 各阶段证据到底证明什么

| 阶段 | 当前可检查内容 | 可支持的窄声明 | 不能推出 |
|---|---|---|---|
| 固定来源记录 | 项目锁定的 bundle 文件哈希、checksum sidecar、sense index、payload bytes、来源是否索引到同一 sense、释义是否精确出现在 raw/effective definition 字段 | annotation 所引用的本地 payload 与仓库所 pin 的冻结 bundle 字节及 sense/gloss 字段一致 | 上游发布者/发行版身份已独立认证；可再发布许可成立；人类语义判断正确 |
| 标注结构 | schema、字符 span 边界、AST/DAG 引用、direction/relation 枚举；claim 证据 span 的并集覆盖其公式子树节点 spans | AST 结构可解析、引用完整，所声明字符区间可定位 | span 在语义上支持 atom/规则；谓词类型、变量绑定解释与 gloss 语义正确 |
| 规则编译 | compiler v6 为 schema 0.2–0.6 保留 v5 的共享单变量一元正 Datalog 路径；为实验性 0.7 接受显式 `target_variable` 的受限多元正规则；0.5/0.6/0.7 的 sort judgments 随 rule provenance 输出，旧 schema 可用按 rule-ID side table；拒绝 unresolved type judgment 和不支持的逻辑片段/标签 | 编译输出与人工输入结构一致且遵守方向专属安全片段；typed 模式相对声明签名表作形式检查；type judgment 与 0.7 target-variable provenance 保持可回放 | 原文推出输入规则；编译片段覆盖完整 gloss 意义；调用方声明的 predicate signature/type hierarchy 权威且语义正确；人工变量 sort 和 target-variable 选择有 gloss 依据 |
| 逻辑求解与证书 | 在给定有限正 Datalog 程序中重算 closure；若带 type_system 则对声明 sort 限制变量 grounding，重放时核 type-system hash 及 typed countermodel atoms；严格路由再比对实际使用规则与 canonical annotations | 该程序内的推导/非蕴含结果可独立复算，证书与输入程序匹配；类型化模式下变量域按声明 signature table 限制 | 开放世界下 claim 为假；输入事实真实；gloss 支持规则；语言学上不存在隐含限定 |
| 组合 source/NLI gate | NLI dev threshold、split/group 隔离、pair hash、proof-used rules、adjudicated claim 与 source payload bytes 的结构/哈希绑定 | 这份 test 预测、锁定程序、声明的人工裁决记录及其本地 source bytes 满足显式路由条件 | 人工 adjudication 的真值、模型服务实际使用所声明权重、校准对目标总体有效、最终 claim 客观为真 |
| 冻结 witness bridge | 结构 witness 的指纹、选定 clause、来源索引、深度/边/拓扑序，并独立交叉重放选中 witness 的 ground Horn 规则 | 特定冻结图快照中所选 witness 与 ground Datalog 证明结构一致 | gloss-span 语义支持、未选 OR alternatives 的推理、完整定义忠实度 |

因此，`candidate_supported_by_proof_nli_and_review` 是严格满足输入条件的**候选路由状态**，不应表述为自动证明释义含义、现实事实真值或标注正确。`not_entailed_in_supplied_program` 仅针对提供的程序/知识范围；不等于 contradiction，也不把 absence-of-proof 当反例。

## 2. 现有 source-only gate 的最小满足条件

正式运行时至少要同时满足以下条件；否则保留明确拒答/unknown 状态，不合并为负例：

1. pipeline 问题显式声明 `knowledge_scope=source_only`，每个事实声明 partition；只有 `source_assertion` 可以进入求解程序。
2. source fact 声明非空 source document、sense ID、gloss SHA 和 claim/formula-node 引用；引用 atom 必须和 fact 谓词及各变量/常量 ground argument 对齐，且目标变量的绑定必须等于 query target；该 atom 属于相关且受支持 claim 的公式子树。
3. strict route 重放证明或反模型，重编译 canonical annotation，并核实 proof 实际使用的每条规则与 claim、direction、inference basis、sense/gloss hash、NLI hypothesis hash 相符；若 replay program 带有 `type_system`，typed validator 必须有效，且 certificate/countermodel 重放绑定同一 signature-table hash。
4. 每个实际使用的 annotation 都通过本地 source bundle verifier：source path 安全、文件与 annotation/checksum 哈希相同、payload 索引到该 sense，释义精确匹配 payload 定义字段。
5. NLI 预测 export 的 manifest 和文件字节哈希需由预先独立固定的 hash 锚定；模型 ID/revision、split、example/group、premise/hypothesis hashes 一致，test gold 不参与在线 gate。
6. 研究报告另用冻结 test gold 计算预测指标，另报 coverage/abstention、错误类型、形式证书状态和 source-support gold；不得用 route 的通过计数代替性能评价。

这些门槛当前属于已有代码/文档中的工程检查。它们不等于存在可用的双人 gold、模型结果、许可审核或成功的科研结论。

## 3. 当前研究证据缺口

- 没有真实双人独立 gloss→AST/规则标注、仲裁记录或人工一致性结果，故不存在可报告的 `semantic_support` 准确率或来源 span 支持准确率。
- 目前 `evidence_spans` 和 AST-node spans 的检查是字符区间定位及覆盖检查；语义关系、方向、必要/充分含义仍由标注者判断，校验器不重新解释自然语言。
- `source_record_verifier` 的信任锚是仓库内的冻结完整性锁；它没有外部数字签名或发布者认证，也不替代上游许可/归属审查。
- `run_pipeline` 生成可回放逻辑结果，单独运行不会使 source semantics gate 自动通过；该 gate 需调用方提供 source bundle root/verified bundle context 并完成组合路由条件。
- frozen witness Datalog bridge 与 annotation-driven source-only route 是不同输入链：前者核验冻结图选中 witness 的结构一致性；后者依赖人工裁决标注。未建立 gold 前不得把二者拼接成“冻结图规则已获 gloss 证实”。
- `config/annotation_preregistration_v3_lock.json` 显示 `protocol_signed=false`、`distribution_authorized=false`。所以当前 400 项 blinded preview 只证明本地文件/顺序完整，不授权外发或正式标注。

## 4. 达到可作论文经验主张前的审计清单

每次实际实验应保存且相互绑定：

- source release 与归属/许可审查记录、项目锁定 bundle semantic fingerprint；
- annotation schema/compiler/checker/route 的版本与源码 commit/hash；
- 独立双标及裁决数据的隐私安全摘要/hash、裁决过程和 span/AST/relation/direction gold；
- NLI model immutable revision、原始模型输入输出/运行方式、dev/test export manifest SHA 和 split/group manifest；
- proof/countermodel 重放结果、逐样例拒答/失败类别、test gold 上的端到端指标；
- 与资源闭包检查、词面/词向量 baseline、gloss-conditioned NLI 和适配 NL→FOL baseline 的 matched split/输入比较。

上述证据目前并未齐备。这张清单用于阻止工程成功状态被误写为论文结论，不表示实验已开始或材料可分发。

## 5. 已有与待完成的 typed Horn 能力

`src/logic/typed_program_validator.py` 新增显式、版本化 signature table 下的 Datalog 参数类型校验。`src/logic/datalog_checker.py` 在 typed program 的 closure、certificate 和 countermodel 路径上重做该检查；`verified_reasoning_pipeline` 可保留调用方给出的 type table，并将其与 replay program 一起带出。它验证 sort 层级无环、predicate 参数位置/arity、变量和常量 sort，以及 subtype 可赋值关系。Phase160 让 strict route 的 evidence checks 显式给出从 replay program 重新计算的 type-validation 报告；invalid typed program 在求解失败时使用稳定 `invalid_typed_program` 原因码，并继续 route 为 unknown/abstain。无 `type_system` 的旧模式仍标为 `not_requested`，不伪称经过类型校验。合成样例仅展示 `Person <: Entity` 的形式兼容。

这不等于已经有项目所需的 WordNet/gloss 语义类型本体。sort 表和 predicate signatures 都是调用方声明的输入；checker 只能判断它们与 program 是否内部相容，不能认证它们是否正确。annotation compiler v5 继续处理旧 schema 的一元正谓词与共享目标变量；compiler v6 仅对实验性 schema 0.7 接受有显式目标变量的有限多元正规则。历史 annotation schema 0.2–0.4 的 typed glossary proof 仍需在版本化 `type_system.rule_variable_sorts` 中按编译后 rule ID 提供 sort。实验性 0.5-draft 提供 claim 级裸 `variable_sorts`；0.6/0.7 为 sort decision 增加 status/basis/rationale/evidence spans，0.7 再声明 `target_variable`；compiler 只接受 assigned judgment 并将来源字段绑定到 rule provenance。结构保真不验证这些判断真值；新 schema 也未用于当前 v3 标注草案，且没有真实类型 gold。故目前准确表述应为：**存在可选的 typed Datalog checker 和实验性原生变量 sort/target 编译路径；类型判断来源现在可被结构化记录，但尚无来源审定的项目类型系统，也没有真实语义 gold 验证该路径**。

下一步需要确定并绑定的输入和验证条件：

- 对每个 predicate 固定参数个数及 argument sorts，并来源追溯、版本化和哈希；
- 明确 type/subtype hierarchy 的权威来源、多继承和隐式 coercion 政策；本校验器当前没有 implicit coercion；
- 扩展 annotation AST/compiler，让变量 sort、predicate signature 与 direction、AND/OR、gloss-span provenance 同步编译，而非依赖人工维护的 rule-ID side table；
- 对 source-only 事实和查询进行相同签名检查，重放 certificate/countermodel 时仍绑定同一 signature hash；
- 在 synthetic malformed cases 上验证类型边界后，再由双人裁决 gold 分别测 predicate typing、source-span semantic support、类型错误拒绝、形式证书有效率和端到端 coverage。

类型一致性永远不能替代人工 gloss semantic-support 标注。当前未有 gold、IAA、matched baseline 或模型结果；不能把校验通过写成 gloss 蕴含正确。具体输入格式见[typed Datalog contract](typed_datalog_contract.md)。
