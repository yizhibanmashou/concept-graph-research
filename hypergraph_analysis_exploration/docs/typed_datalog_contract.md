# 显式类型签名下的 Datalog 校验

状态：typed Datalog 校验器已加入 Datalog 查询和证书/反模型回放入口，提供的是**相对于调用方声明签名表的形式类型检查**。有限正 Datalog 的 synthetic tests 已覆盖 sort 子类型域、certificate/countermodel type-table hash 与错 sort model atom 拒绝；它不决定词义、不解析 gloss，也不证明签名/类型本体本身真实正确。

## 输入契约

带类型的 Datalog program 可以附加 `type_system`：

- `schema_version` 固定为 `datalog-type-system/1`；`type_system_id` 和 `version` 标识签名表。
- `sorts` 将每个 sort 映射到父 sort 列表。支持多继承；子 sort 可用于父 sort 要求的位置。类型层级有环或父类型未声明会拒绝。
- `predicate_signatures` 为每个实际使用的谓词声明有序参数 sort 列表。缺少 signature、参数个数不符或参数类型不兼容都会拒绝。
- `constant_sorts` 给 facts、queries 和规则常量声明一个或多个 sort。常量可以具有多个 sort；其中任一 sort 是谓词参数所需 sort 的子类型即可通过。
- 规则变量 sort 可以直接写在 rule 的 `variable_sorts`，或集中写在 signature table 的 `rule_variable_sorts`，以规则 ID 为键；同一 rule 不可同时从两处声明。变量声明必须覆盖规则所有变量且不得多写；缺失声明、未知 sort 或不兼容位置都会拒绝。声明的 variable sort 也是量化域约束：proof search 和 countermodel rule-satisfaction 只允许绑定到 `constant_sorts` 中声明为该 sort 或其子 sort 的 Herbrand 常量。

校验报告包含 type system 的 canonical JSON SHA-256、sort/predicate/constant 数量和逐项错误。`src/logic/datalog_checker.py` 在有 `type_system` 时于 closure 构造、proof certificate replay 和 countermodel replay 前运行该检查；certificate 和 countermodel 都携带该 SHA-256，重放器要求它与当前 replay program 完全一致；certificate 的每个 variable binding 都须落入声明 sort 的域；类型化 countermodel 的整个有限解释（不只程序原有 facts）也须满足同一 signature table，且其反模型检查使用类型约束后的量化域。`verified_reasoning_pipeline.run_pipeline` 可从问题输入接收并保留该签名表，typed replay 中的 rule variable sort 按编译后的规则 ID 显式声明。

合成示例（无 WordNet 或 gloss 数据）可运行：

```powershell
python -m src.logic.datalog_checker config/typed_datalog_problem.example.json
```

该示例用 `Person <: Entity` 检查一个 unary Horn 推导。它只展示 sort 继承和参数兼容性，不是项目真实 predicate/type inventory，也不属于研究评测结果。

## 与 glossary compiler 的边界

变量 `?x` 的实验性 referent 解释、`Entity/Eventuality` 候选域、拒绝条件与类型来源验证门见[Gloss referent/type 契约草案](gloss_referent_type_contract.md)。该草案不是当前 schema 的权威默认值；未经人审的 POS heuristic 不得直接写进 `variable_sorts`。

旧 schema 的 annotation compiler v5 仍只接受一元正谓词、同一目标变量与有界 AND/OR 片段；compiler v6 对实验性 `0.7-draft` 增加显式 `target_variable` 的安全多元片段。历史 schema 0.2–0.4 尚未提供变量 sort，typed caller 可针对编译出来的 rule ID 在 `rule_variable_sorts` 显式提供声明；实验性 schema `0.5-draft` 在每条 rule claim 保存裸 `variable_sorts`；`0.6-draft` 保存带 status/basis/rationale/evidence spans 的 `variable_sort_judgments`，0.7 沿用它并另存 target variable。仅 assigned judgments 会编译为运行时 sorts，unresolved claim 明确拒绝；0.7 每条 rule 只带该规则实际用到的变量 sort。compiler 会将 judgment、review status 与 target variable 保留在规则 provenance。typed caller 仍须提供 sort hierarchy 和 predicate signatures。由此可作形式判断的是：**给定签名表和人工类型判断时，规则/事实/查询的参数位置是否相容，且 provenance 未在编译/证书回放中丢失**。仍不能推出：

- 声明的 sort hierarchy 或 predicate signature 对自然语言/WordNet 是正确的；
- 人工标注的 rule、direction、AST 或 span 符合原始 gloss；
- proof 有效等于 gloss 语义蕴含成立；
- 有限正 Datalog 下不蕴含等于 open-world contradiction。

正式语义工作仍须先确定并版本化类型来源，给出可追溯的 predicate/domain/range 定义；再扩展 annotation schema 将 sort 约束与 source provenance 绑定。类型一致性、source-span semantic support、NLI、资源内上下位闭包和逻辑证书回放必须分轴报告。

### OEWN 资源标签不能直接充当 sort lattice

Phase 73 对 pinned OEWN 2025 Plus 做了结构字段审计：45 个 lexicographer files、120,564 个 synsets；普通 `hypernym` 有 93,395 条直接边，`instance_hypernym` 另有 8,599 条。WordNet 官方将 lexfiles 定义为按 POS 和逻辑分组整理，而非形式化的可继承 sort hierarchy；Global WordNet 格式也区分 class hypernym 与 instance-to-class relation。当前 checker 的 hypernym verifier 只读取 `hypernym`，不覆盖 `instance_hypernym`。因此目前仅能把 lexname/POS 作为 provenance-bound attributes/分析分层候选；需先定义 glossary 编译变量表示的是 sense、概念 extension member 还是 event/other domain，再决定 lexical signatures。详见Phase 73 报告与[机器聚合审计](../outputs/phase73/oewn_type_inventory_audit.json)。
