# 形式蕴含检查器与 NLI 语义门

**Phase266 现态复放（2026-10-08）**：单例结构证书与当前 Datalog bridge 使用当前 checker 重放有效（3,596 nodes、14,923 dependency edges、3,512 ground rules），与 Phase148 审计逐字节相同；Phase117 全量 source-lineage 记录的 bundle fingerprint 仍与当前冻结材料一致。此现态复放没有重读全部 source payload，也不判断 gloss-span 是否支持规则。Phase6 历史 bridge 在新 checker 下的对象级差异仍由 `source_bindings`、`source_claim_refs` 后加字段解释，历史 artifact 不标作当前版本可重放。机器结果见[Phase266 审计](../outputs/phase266/witness_example_replay_audit.json)与深度报告。

本阶段新增两个**原型组件**，和冻结包的 gloss-dependency graph 分开运行。它们建立可测试的后续接口，不表示当前已经把 110,425 条释义逻辑化或完成了 NLI 语义评估。

项目现在有两种不能混称的独立重放：`src/analysis/verify_witness_certificate.py` 对照冻结包复核单个 selected-witness DAG 的 head/clause/source-document 引用、指纹、边和深度顺序；本页后文的正 Datalog verifier 则对人工审校规则与显式 facts/query 重放对象层 Horn 推导。前者证明冻结编码下的结构性可用性，后者证明指定逻辑程序下的有限模型推导；二者都不验证自然语言 gloss 是否语义支持规则。冻结图证书示例及运行命令见[结构 DAG 剖面](selected_witness_dag_profile.md)。

单目标 witness replay 与全量 `frozen_hypergraph_audit` 在结构检查前按 [bundle integrity lock](../config/frozen_bundle_integrity_lock.json) 核对 `manifest.json`、`checksums.jsonl`、hypergraph rules、coverage witnesses、senses index 和 `provenance/hypergraph_source_contract.json` 六项 SHA-256，并检查后四项数据文件与 checksums sidecar 的对应值及 rules 文件的 manifest hash。来源构建 contract 也在锁定范围内，避免来源合并/覆盖策略文件漂移而图本身 hash 不变。该项目内锁可发现文件意外漂移，但不是数字签名；更新/替换 bundle 后须先审阅版本差异再显式更新锁。当前工作树尚无 Git commit，故发表级冻结还需记录后续 Git revision 或独立归档 hash。bridge 验证结果会附上本次实测哈希，避免只保留由 manifest 声明的 fingerprint。

## 1. 正 Datalog/Horn 检查器

实现：`src/logic/datalog_checker.py`。输入有限、无函数符号、无否定的正 Datalog 程序：ground facts、普遍量化的 Horn rules `body → head`、以及 ground query。变量以 `?` 开头，规则头变量必须在 body 中出现，谓词元数必须一致。闭包给出 least Herbrand model；query 若存在则导出包括 facts、rule applications、变量代换和 provenance 的证明 DAG，并由独立 verifier 逐条重放。验证器要求证书节点集合恰好等于根结论的可达证明 DAG，拒绝额外孤立节点；若 query 不在最小模型中，则输出完整有限解释（interpretation）及其 SHA-256。`verify_countermodel` 独立检查所有输入事实在模型中、每条规则在该解释下均满足且 query 缺席，因此该模型本身构成当前有限程序内的非蕴含反例。它不声称覆盖程序外知识或开放世界真值。

重要边界：这个正片段没有否定、互斥约束或完整性约束，因此不能检查输入前提是否彼此矛盾，也不能把两个相反自然语言命题自动识别为冲突（除非另行定义并验证约束；当前检查器不支持）。在当前有限、无函数符号的正 Datalog 片段中，`entailed_in_positive_datalog` 与 `not_entailed_in_least_herbrand_model` 都是完整闭包计算后的精确片段内结果；后者另附独立验证的有限反模型。它仅表示 query 不由当前显式程序蕴含，**不表示开放世界的“假”，也不表示这些前提一致、真实或忠实于 gloss**。当前实现没有迭代/时间预算上限，故没有 `resource_limited` 结果；若未来加入有界搜索，预算耗尽必须与反模型或精确非蕴含区分。`datalog_checker.verify_query` 对格式错误及不支持的程序构造仍抛 `ValueError`；`verified_reasoning_pipeline.run_pipeline` 在 Datalog 求解阶段将此类错误转换为 `proof_result.status=unknown`、`reason_code=invalid_or_unsupported_datalog_program`，并保留错误详情。组合路由会独立重放 countermodel；当 NLI 阈值通过且反模型有效时返回 `not_entailed_in_supplied_program`，这是输入程序范围内的结果而非 gloss 矛盾/开放世界假命题。求解状态为 `unknown` 时返回 `abstain_unknown_proof_result`（若 NLI 未过阈值或无校准阈值，则保留对应更早的拒答原因）；不能把 `unknown` 当作蕴含或反模型。

运行接口：

```powershell
python -m src.logic.datalog_checker path\to\program.json --output path\to\result.json
```

规则输入最小 schema：

```json
{
  "facts": [
    {"predicate": "dog", "arguments": ["fido"], "source_documents": ["package-relative/source.json"]}
  ],
  "rules": [
    {
      "id": "rule-id",
      "head": {"predicate": "animal", "arguments": ["?x"]},
      "body": [{"predicate": "dog", "arguments": ["?x"]}],
      "provenance": {"sense_id": "dog-1", "source_documents": ["package-relative/source.json"]}
    }
  ],
  "query": {"predicate": "animal", "arguments": ["fido"]}
}
```

以上只是 schema 示例，不是真实 WordNet 公式。这个检查器的证明严格表示“给定这些形式规则，query 在该规则系统中可推出”；它不验证源 gloss 是否忠实支持规则。上位关系要编码为有方向、带 sense 的谓词/规则，例如 `Dog(x) → Mammal(x)`；普通超图边 `dog-sense → animal-sense` 不能替代有论元的语义公式。

另有一个资源级适配器 `src/analysis/oewn_hypernym_verifier.py`，针对显式的 `(child_synset_id, ancestor_synset_id)` 对在固定 OEWN 2025 Plus `hypernym` 边上做有向 BFS；正例给出最短边路径、来源文件和显式 Horn proof DAG，转移规则写为 `H(x,y) ∧ H(y,z) → H(x,z)`。独立模块 `src/analysis/verify_oewn_hypernym_certificates.py` 重新加载哈希锁定的 taxonomy，逐边重放、检查 rule-application premise/root/source、核对 claim/release 指纹，并用反向搜索复核最短长度；对资源内无路径的结果重新搜索闭包。它可以验证资源内直接/传递链接，但不从 gloss 生成命题，也不证明 gloss 蕴含；`not_in_hypernym_closure` 是资源闭包未找到，不是语义反例。方法、输入哈希、结果和边界见[Phase 16 报告](phase16_oewn_hypernym_verifier.md)。

#### 四类证据的联合解释边界

同一个研究问题可能需要并列呈现以下证据，但不能把它们压成单一的“已验证”标签：

| 证据层 | 当前检查器实际验证的对象 | 不能由该层单独推出 |
|---|---|---|
| 资源关系 | pinned OEWN release 中指定 child synset 到 ancestor synset 的有向路径，或该 release 闭包内无路径 | gloss 支持该关系；资源外的语义真/假 |
| gloss 来源支持 | 当前人工 adjudication 对指定 sense/gloss、span、方向和 typed atom/rule 的判断及 payload 身份 | adjudication 一定正确；未标关系为假 |
| 形式推导 | 给定 facts、rules、query 下的 Horn 证书或有限反模型可独立重放 | 前提来自真实 gloss、规则忠实于自然语言、开放世界矛盾 |
| NLI 行为 | 固定 text-pair、模型身份和开发集选择的阈值下，test scores 是否通过路由策略 | 形式证明有效、OEWN 关系成立、NLI 分数是语义真值 |

只有在同一条候选关系上建立显式的共同身份关联后，才能在结果表中并列这些列。最低限度应分开保留 `relation_edge_id=(child_synset_id,parent_synset_id,relation,direction)`、pinned-release identity、raw-gloss hash、rendered-premise hash 与 renderer version、hypothesis hash/surface、proof query/certificate hash、NLI model+revision+export manifest hash，以及各自独立的状态/拒答原因。一个模块的通过状态不得复制为另一模块的 gold 或通过状态。资源闭包中的负结果也不得填成 `not_supported` 或 NLI `contradiction`。

现有 `verified_reasoning_pipeline` 是 single-sense 的 annotation→Horn→certificate→NLI 路由，严格绑定 sense/gloss 和 NLI text-pair hash；OEWN verifier 则接受显式 synset pair，独立验证 taxonomy 路径。当前没有共享 `relation_edge_id`、parent-surface 身份或可重放的跨模块 join，因此二者不是一个端到端的 hypernym+gloss+proof+NLI 判定器。Track A 若采用双 premise 条件、surface-nested edge 和独立 source-support gold，必须先冻结研究合同，再新增版本化关联 schema；不能仅把现有 `sense_id` 或 hash 字段重命名后宣称兼容。

当前明确不支持：完整一阶逻辑、析取 head、否定/默认规则、等式、函数符号、存在量词、开放世界知识融合、SAT/SMT 求解。有限 Herbrand countermodel 只覆盖提供的程序/词汇表，不代表外部常识中“确定为假”。正式论文系统需对接成熟 FOL/SMT/定理证明器，并验证 solver 证书，而不是扩大本原型边界。

### 标注 AST → Datalog 受限编译器

`src/logic/annotation_to_datalog.py` 将通过 `annotation_validator` 的规范记录编译为独立的正 Horn 规则库；它不自动解析 gloss，也不会把输出直接并入冻结依赖图。编译器只接受 `annotated` 状态且显式、方向匹配的 `necessary`、`sufficient` 或 `biconditional` 声明：

- `confidence=low` 的 claim 不进入规则库，而作为带原因的 rejection/needs-review 项保留；当前最小编译置信度固定为 `medium`。这是一条保守的工程策略，不是已经通过实验校准的阈值；人工 gold slice 建立后应单独评估覆盖率和规则精度，并在开发集预注册/校准。
- schema 0.2–0.6 仍要求一元正谓词且公式原子共享同一个目标变量；实验性 schema 0.7 需显式标出 `target_variable`，仅允许多元正 atom/AND/OR。充分方向每个 DNF body 分支必须含目标变量，其他变量只可出现在 body；必要方向 atom/AND 的结论中不得出现非目标变量。两条路径均拒绝否定、量词和蕴含。
- 必要条件 `Target(x) → Φ(x)` 只接受 atom/AND；每个合取项生成一个 `Target(x) → Aᵢ(x)` 规则。必要条件中的 OR 不展平。
- 充分条件 `Φ(x) → Target(x)` 接受 atom/AND/OR；安全地将正公式转为 DNF，每个分支生成一个 Horn 规则，最多 64 个分支。超过上限时显式拒绝。
- 双向声明分别编译两个方向；若某个方向不受支持，另一个方向可保留，同时记录被拒方向及原因。方向/关系不匹配、典型属性及其他非定义关系不会升级为规则。

每条规则带回 sense、来源记录与 gloss 哈希、证据 span、公式节点、方向、`semantic_support=supported`、该判断的置信度、`inference_basis` 及 compiler 版本；0.7 provenance 还记录 `target_variable`。schema `0.4-draft` 及后续草案只有在依据非空且仅含 `lexical_or_paraphrastic` / `compositional_or_logical` 时才进入程序；较早 schema 可由编译器兼容读取，但不能通过组合路由的来源审查。形式检查不验证语义支持或依据标签本身是否正确。运行方式：

```powershell
python -m src.logic.annotation_to_datalog path\to\annotations.jsonl --output path\to\compiled_rule_library.json
```

输出是**规则库**，不是完整 checker 输入；运行 `datalog_checker` 时仍需显式提供 ground facts 和 query。CLI 报告携带输入 JSONL 原始字节的 SHA-256，以便区分具体标注文件版本；JSONL 空白或行序变化也会改变此文件哈希。编译成功只表示人工声明通过了受限语法转换，证明证书只验证相对于这些规则的推导，二者都不证明标注忠实于原 gloss。`--strict` 可要求任何 claim 被拒时不写输出；已有输出默认不会覆盖。

### 组合运行：标注 → Horn → proof certificate

`src/logic/verified_reasoning_pipeline.py` 将上述人工审校记录、编译器与独立证书 verifier 串成一个可复跑命令。问题 JSON 接受 `facts` 列表、一个 ground `query`，以及可选的 `knowledge_scope`；记录先经 annotation validator 与低置信拒绝策略，再编译规则并执行闭包。结果包含编译拒绝原因、可选的两个输入文件原始字节 SHA-256、规范化 annotation records/problem 内容哈希、可重放 program、proof/countermodel 和事实范围摘要。直接调用 Python API 时没有原始文件字节可哈希，因此原始文件哈希为 `null`，但规范化内容哈希总会生成：它对 JSON 字符串使用 UTF-8、排序对象键、不保留空白差异且拒绝 NaN/Infinity；它不替代 CLI 的原始文件哈希。传入的原始 SHA-256 若格式无效会被拒绝：

```powershell
python -m src.logic.verified_reasoning_pipeline annotations.jsonl problem.json --output outputs/phase9/query_result.json
```

当前没有真实人工 WordNet 记录，故此组合仍不构成端到端 gloss 语义实验。`not_entailed_in_least_herbrand_model` 限于显式输入的事实与规则；它不是开放世界的假命题标签，也不证明 source gloss 是否支持编译规则。求解阶段遇到格式错误或超出正 Datalog 片段的程序时，pipeline 输出 `unknown`，而不是伪造非蕴含反模型。

#### 事实分区与 `source_only` proof scope

为避免把外部常识误当作 gloss 推论，Datalog fact 可选携带 `knowledge_partition`：

- `source_assertion`：由明确引用的 source 文本/记录断言；
- `resource_fact`：来自外部结构化词汇资源或知识库；
- `external_assumption`：资源外补充前提，包括模型生成的 common knowledge；
- 缺失时在证书中视作 `unclassified`。

定义规则作为 `adjudicated_annotation_rules` 单独保存于规则 provenance，不混入事实 partition。`knowledge_scope` 默认为 `all_inputs`，与旧输入兼容；选择 `source_only` 时要求每条原始 fact 显式标类，只把 `source_assertion` facts 放入运行程序，明确排除资源事实与外部假设；保留的 source assertion 必须含至少一个去除首尾空白后仍非空的 `source_documents` 路径，提供 `source_sense_id` 与该释义的 `source_gloss_sha256`，并携带非空 `source_claim_refs`，逐条指向标注记录、claim 与公式 atom node。证明证书的 fact leaf 携带规范化 partition、source binding 和 claim refs，独立回放会核对这些字段；旧式未标类证书仍可回放，但其 leaf 按 `unclassified` 且无 source binding 处理。

组合 `route_pipeline_result` 仅在证明至少用到一个 fact leaf，且每个 fact leaf 都明确且仅标为 `source_assertion`、带来源文档，并至少有一个 source binding 与测试 prediction 的 sense ID 和 premise gloss SHA 匹配时，才可能通过 source semantics gate；它同时要求每条实际使用的规则都绑定到已裁决且 supported 的标注，并且所有规则来源均匹配测试 prediction 的同一 sense ID 与 premise gloss hash。允许同一 gloss 内多条已审核规则共同构成证明，但拒绝借用其他义项或释义的规则。`all_inputs` 模式下不分类的旧事实仍能用于一般逻辑计算，但若被证明使用会令组合路由拒答。最小问题示例：

```json
{
  "knowledge_scope": "source_only",
  "facts": [
    {
      "predicate": "observed_in_gloss",
      "arguments": ["sense-1"],
      "knowledge_partition": "source_assertion",
      "source_documents": ["package-relative/source.json"],
      "source_sense_id": "sense-1",
      "source_gloss_sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
      "source_claim_refs": [
        {"annotation_id": "ann-1", "claim_id": "claim-1", "formula_node_id": "atom-1"}
      ]
    }
  ],
  "query": {"predicate": "wn_sense:sense-1", "arguments": ["entity-1"]}
}
```

路由另外逐条验证实际使用的 fact leaf：claim ref 必须落在已裁决、`supported`、至少 medium 置信度且 inference basis 仅为 gloss-grounded 标签的 claim 子树内；其 atom predicate 必须等于 ground fact predicate，atom 必须是目标变量的一元谓词，ground fact 参数必须等于 query target；sense 与 gloss SHA 必须和测试输入一致。每个引用标注必须含 `provenance.source_records`，fact 的来源路径须与每个引用标注至少一条 source-record 路径相交，且 fact 声明的所有路径都须被引用标注集合覆盖。组合路由现在还会对证明实际引用的标注记录执行本地 payload 字节、sense index 和 gloss 字段复核，但仅在提供 `source_bundle_root` 或复用已初始化的 `AnnotationSourceBundleVerifier` 时 source semantics gate 才能通过。它不确认来源对应的上游发行版、许可或人工裁决正确性；span 到 atom 的映射仍只是结构关联，语义忠实度仍需独立 gold。

新增 `src.logic.source_record_verifier` 提供一个独立的标注来源预检入口：

```powershell
python -m src.logic.source_record_verifier path\to\annotations.jsonl
```

该 verifier 要求每条标注的 `provenance.source_records` 非空；逐条确认相对路径安全、来源 payload 属于冻结包 sense index 中同一义项、标注携带的 SHA-256 与实存字节和冻结 `checksums.jsonl` 一致，并确认 `sense.gloss` 与 payload 的 `synset.raw_definition` 或 `definition.definition` 精确相同。输出只含输入/冻结包摘要哈希、聚合计数和失败类别，不含 gloss、义项 ID 或 source path。它只核验本地 frozen-payload 绑定，不将该 payload 追溯为准确的上游发行版，也不判断许可、公式语义支持或人工裁决正确性；目前没有真实回传标注可用于实际预检。组合路由现已针对证明实际使用的标注记录调用同一 verifier；调用方须传入 `source_bundle_root`，或传入已初始化的 `AnnotationSourceBundleVerifier`，否则来源语义门保持关闭。批量评测建议创建一个 verifier 实例并在整批路由中复用：冻结包完整性、checksum sidecar 和 sense index 只初始化一次；每个样例仍重新读取并哈希该证明引用的 payload 文件。路由结果的 `evidence_checks.source_payloads_independently_verified` 与嵌套 `source_payload_verification` 字段记录核验结果。独立 CLI 仍可用于导入前预检并归档结果。

### 冻结 witness DAG × Datalog 独立交叉重放

`src/analysis/verify_witness_datalog_bridge.py` 为已导出的单目标 witness DAG 建立一个范围受限的交叉检查：先由 structural verifier 对照 bundle 验证指纹、所选 clause、来源索引、深度、边及拓扑序；然后仅将证书中每个非 seed 节点已经选定的 clause 编译为零元 ground Datalog 谓词和 Horn 规则，seed 编为事实。Datalog checker 独立重建 least-Herbrand 闭包和 query 证明证书，桥接 verifier 再要求证明节点集合、依赖边**多重集**与结构 witness 完全一致。规则 provenance 携带 graph fingerprint、head、选中 clause index、proof depth 和 source-document 引用。

```powershell
python -m src.analysis.verify_witness_datalog_bridge outputs/phase6/witness_oewn-00520548-n.json
```

默认结果写入项目内 `outputs/phase6/witness_<sense-id>_datalog_bridge.json`；已有结果需显式 `--force` 才覆盖。完整证书含 source 文件相对路径，默认输出已加入 `.gitignore`。此桥接只证明“给定冻结包中这条已选 witness 路径，目标可由对应 ground Horn 规则推出”，不证明 gloss 蕴含、source 文本忠实性、其他 OR 候选子句或开放世界结论；它是两个结构验证器之间的实现一致性检查，不是独立语义实验。

## 2. NLI evaluator / abstention gate

实现：`src/logic/nli_gate.py`。它不附带模型；读取外部版本化 NLI 模型的三类概率，报告 accuracy、macro-F1、混淆矩阵、多类 Brier score 与 10-bin top-label ECE。需区分两个流程：通用离线 evaluator 保留 `select_entailment_threshold`，它在开发集观测分数上搜索，并用 Bonferroni 调整的 Wilson 界作**探索性筛选**；候选族由同一开发数据决定，且 Wilson 是近似界，因此不能据此声称精确有限样本保证。报告版本 `nli-dev-calibration-test/3` 的这个接口只作离线分析，不是组合路由的校准证书。若任一 dev/test 行带有 `premise_sha256`，所有两侧行都必须提供该字段，且两个 split 的精确 raw-premise hash 集合必须互斥；该附加门槛会发现绕过 manifest exporter 的精确释义重复，但不能发现归一化或语义近重复。

组合在线路由 `route_pipeline_result` 使用 `select_certified_entailment_threshold`：阈值网格预先固定为 0.00 到 1.00、步长 0.01 的 101 个值；对每个非空阈值子集检验零假设 precision ≤ 预设下限，使用精确单侧二项上尾 p 值，并以 Bonferroni 限制整组阈值的错误拒绝概率。因为阈值族不依赖观测分数且逐项检验为精确检验，选中的阈值具有名义家族级有限样本保证；样本不足时拒绝路由。校准结果记录 selector 版本和按 `group_id` 排序、规范 JSON 序列化后的 development-row SHA-256，便于复算时确认校准输入。正式研究入口应每行提供唯一 `group_id`，每个独立组恰有一行；兼容 API 在所有行均无 `group_id` 时会把 `sense_id` 作为分组键补入校准行，并在结果中记录 `grouping_policy` 与哈希覆盖范围，但这不能阻止同一 lemma 的不同 sense 分置两侧。部分行提供 `group_id` 时拒绝混合口径。保证仍以这些校准单位可视为 IID，模型及阈值网格在评估前冻结、且目标分布不发生偏移为前提；唯一 ID 和 dev/test 分组隔离只能检查重复，不能证明独立性或分布稳定。正式 test 指标仍须在未参与方法选择的锁定 test 上报告。风险控制与多重检验的关系见 [Learn then Test 原文](https://arxiv.org/abs/2110.01052)；本实现采用固定候选族上的精确二项检验加 Bonferroni，并非该文所列方法的直接复现。

Phase154 筛读的 [HG-CRC](https://arxiv.org/abs/2607.24562) 是分层 group-conditional selective-risk control 的近期方法先例，可启发未来对预注册的输入条件/POS 子组同时控制 precision risk。论文的严格 split 变体以 IID calibration rows 和独立 test point 为前提；层级 membership 不代表相关样本 cluster 的独立性。若 Track A 保留 edge 内多个 parent surface、每个 surface 又有多个 premise condition，不能把 group hierarchy 当作相关性校正。当前 exporter 仍要求每个 dev `group_id` 唯一，strict route 将同一字段兼作 split 隔离和校准独立单位；多 surface 版本需要先定义独立校准 observation 与线上逐候选动作的对应关系，再设计新版本接口。细节见Phase154和[筛读日志](../sources/literature_screening_log_2026-10-08_hierarchical_group_risk_control.json)。

单文件 CLI 的 `--confidence-threshold` 是另一种 max-class confidence selective 评估阈值，也必须预先在开发集设定。

方向反转一致性应作为单独的诊断指标，而不是替代三类 gold accuracy 或 source-support 判断。LREC 2026 的 PhrasIS 研究用成对反转和 soft/hard coherence 显示模型可能在方向改变时失去一致性，也指出一致但错误仍会得高 soft coherence；其七分类 phrase-pair 指标不能直接移植到此处。待有裁决 gold 后，只对可定义反向标签的样例构造反向 pair，保留原始与反向标签、报告 exact accuracy 和成对 coherence；不支持、含糊或定义方向不确定的条目标为 unknown/不进入可逆子集。具体先例见[定向筛读日志](../sources/literature_screening_log_2026-10-04_directional_nli.json)。

Phase 84 定向全文筛读 SemEval-2026 Task 11 后，另提出将**内容合理性**与**无关上下文**作为隔离的 NLI 稳健性诊断；它们不可折叠进现有 gold、阈值选择或 source-only proof gate。评测设计见[内容效应评测草案](nli_content_effect_evaluation_draft.md)。Phase 86 增加 `src/logic/nli_content_effect.py` 的 sidecar 结构/配对校验及 descriptive evaluator：核验成对条件、hash、模型 identity 和 group split，输出分层/配对描述指标；不选阈值、不做区间推断、不发出 route decision，也不读取文本。其 API 和 synthetic tests 通过，但没有冻结 schema、真实标注或模型结果。该模块与 `nli_gate` 和 verified proof router 分开。

成对评测命令调用离线 evaluator；其中 `--precision-confidence-level` 是 Bonferroni-Wilson 探索性筛选的家族置信度，不会生成组合在线路由所需的精确二项风险控制对象：

```powershell
python -m src.logic.nli_gate --dev-predictions outputs/nli/dev_predictions.jsonl --test-predictions outputs/nli/test_predictions.jsonl --minimum-precision 0.9 --precision-confidence-level 0.95 --model-id nli-model-name --model-revision immutable-commit-or-sha256 --output outputs/nli/test_report.json
```

路由策略是保守的；组合正类门接收 `select_certified_entailment_threshold` 生成的 dev 校准结果对象，不直接接收手写浮点数。校准行须带唯一 `group_id`：

1. 开发集无法达到预先声明的 precision floor → `abstain_no_calibrated_threshold`。
2. NLI 未通过 development entailment 阈值，不标成蕴含（可判 neutral/contradiction，或送审）。
3. NLI 通过且有限反模型经重放有效 → `not_entailed_in_supplied_program`；这只陈述当前 facts/rules 下的精确非蕴含，不等价于 gloss 矛盾或开放世界假命题。
4. NLI 通过但 proof 状态为 `unknown` → `abstain_unknown_proof_result`；没有证书且没有有效 countermodel → `abstain_missing_or_invalid_proof`。
5. NLI 通过、有可重放正证书但规则来源语义未审 → `abstain_source_rule_not_semantically_audited`。
6. 只有 NLI、正证书、来源规则审查都满足时才进入候选支持状态；NLI precision gate 的有限样本保证仅在上述 IID/冻结/同分布假设下成立，不能推出整个证明与来源审查都正确，仍须在人工金标准上测量端到端误差。

`route_candidate` 是低层纯策略函数，其 `proof_certificate_valid` 和 `source_semantics_reviewed` 布尔量由调用方提供，不能单独视为可信 gate。底层 `route_pipeline_result` 完成逻辑证书、来源规则和给定 NLI 行的绑定；研究运行必须再通过 `route_pipeline_result_from_export` 核验哈希固定的完整预测导出及 dev/test 模型身份。该严格入口从 manifest 读取两组预测，目标 test 行的 gold 在交给底层路由前移除：它接收**有标签的 dev 行**与**可不带 gold 标签的 test 预测**，只用 dev 重选阈值，并先检查 example ID、sense/lemma-group 的跨 split 泄漏；然后对 pipeline 结果中的正证书或有限反模型调用独立 verifier，并重新编译 canonical annotations，要求程序规则与重编译输出一致；最后检查证明 DAG 实际使用的每条规则都能绑定回对应的 annotation、claim、sense、gloss hash、source-record metadata 和 evidence spans。annotation validator 要求 claim 所引用公式子树的每个节点 span 都被 claim evidence span 的并集无间隙覆盖；这只是 AST 节点到字符区间的结构关联，不是语义支持证明。此外要求这些 claim 明确标记 `semantic_support=supported`、置信度至少 medium、非空且仅由 `lexical_or_paraphrastic` / `compositional_or_logical` 组成的 `inference_basis`，且 annotation 为 `adjudication_status=adjudicated`。组合路由要求 dev 行有 `example_id`、`claim_id`、`premise_sha256`、`hypothesis_sha256`；test 预测另需 `sense_id`、`example_id`、`claim_id` 和格式有效的成对 SHA-256。test 的 premise 哈希必须等于该 sense 的 canonical gloss 哈希，hypothesis 哈希必须等于 proof 实际使用且已裁决 claim 中保存的候选 hypothesis 哈希，且该 claim ID 必须出现在证明链使用规则中。任一条件不满足即拒答。NLI 概率应来自固定且记录 immutable revision 的外部模型。兼容入口 `route_pipeline_result` 本身不核对 dev/test 模型身份，不能单独用于声称跨 split 模型校准一致。研究运行应改用 `route_pipeline_result_from_export`：先以外部锁定的 export-manifest SHA-256 绑定 `claim-review-nli-export/0.2` manifest；该入口读取并校验 dev/test 预测文件原始 SHA-256、行数、split 标记以及每行 model ID/revision 与 manifest 一致，再按目标 example ID 选出 test 行，移除其 gold 后调用组合路由。导出 manifest 同时保存 sidecar、候选清单、原始 model-score 输入和两份输出 JSONL 的哈希；阈值校准 hash 包含 dev 行中的模型身份。CLI 会打印 manifest SHA-256，正式运行须将该值独立写入预注册/运行锁并传给严格入口。上述哈希证明文件与声明的字节一致，不证明模型服务确实运行了所声明的 revision；仍需保留模型运行环境/调用记录或可复核的本地权重 artifact。只有严格入口通过且外部模型身份声明可审计时，路由结果才具备相应跨 split 校准解释。

研究路由示意调用：`expected_export_manifest_sha256` 必须先写入独立预注册/运行锁；导出目录内 manifest 会验证 dev/test 两份预测文件与模型身份。

```python
from pathlib import Path
from src.logic.verified_reasoning_pipeline import (
    run_pipeline, route_pipeline_result_from_export,
)
from src.logic.source_record_verifier import AnnotationSourceBundleVerifier

source_bundle_verifier = AnnotationSourceBundleVerifier(
    Path("../OEWN")
)
pipeline_result = run_pipeline(records, problem)
decision = route_pipeline_result_from_export(
    pipeline_result, records, target_example_id="candidate-123",
    prediction_export_dir=Path("outputs/nli-export"),
    expected_export_manifest_sha256="<externally-pinned-64-hex-sha256>",
    minimum_precision=0.9,
    source_bundle_verifier=source_bundle_verifier,
)
```

批量研究可调用 `route_pipeline_batch_from_export(items, records, ...)`；每个 `items` 元素形如 `{"example_id": "candidate-123", "pipeline_result": pipeline_result}`。此函数调用同一严格单样例入口，要求批内 example ID 唯一，并对异常 fail-fast，不返回可能被误认为完整的部分结果。它共享同一个 `source_bundle_verifier`，返回规范输入摘要哈希、annotation records 摘要哈希、固定 export 身份与逐条路由。当前实现逐条重新读取并核验 pinned dev/test 文件，先保证复用语义一致，尚未做 export 的一次性预载优化；较大批次的耗时需要实测后再决定是否优化。

```python
from src.logic.verified_reasoning_pipeline import route_pipeline_batch_from_export

batch = route_pipeline_batch_from_export(
    [{"example_id": example_id, "pipeline_result": result}
     for example_id, result in pipeline_results.items()],
    records,
    prediction_export_dir=Path("outputs/nli-export"),
    expected_export_manifest_sha256="<externally-pinned-64-hex-sha256>",
    source_bundle_verifier=source_bundle_verifier,
)
```

该 API 只批量编排已生成的 pipeline results，不生成 problem、预测分数或 gold，也不等于已运行一轮实验。批量成功仍不能替代 test gold 上的离线评价、双人裁决或 source-support 有效性检查。

该绑定检查的是数据与结构一致性，不会验证“裁决为 supported”是否正确，也不会证明 supplied facts 为真；route 返回 `candidate_supported_by_proof_nli_and_review` 仍只是满足显式条件的候选，不是自动接受或无条件事实。在线组合路由不读取 test gold，因此可处理未标注预测；若要计算 test 分类质量，仍须另行用 `evaluate_calibrated_splits` 在锁定的 test gold 上做一次性离线评估。通用 NLI evaluator 为兼容旧数据仍允许不带文本哈希的行，但组合路由拒绝缺失这些字段的行。pair hash 只能证明记录的字符串与指定输入一致，不能证明模型实际使用了该字符串；真实实验还须保存可审计的模型输入/输出、immutable model revision 与 prediction-file hash，并用人工 gold 评价模型和裁决质量。带低层布尔参数的 `route_candidate` 仍留作策略单测/适配用途；研究脚本应从 certificate verifier 和 adjudication records 派生状态，不能手工传 `True`。

通用 NLI 评测行至少包含 `{ "sense_id": "...", "split": "dev|test", "gold": "entailment|neutral|contradiction", "scores": { ... } }`，可带 `example_id`、`claim_id`、成对的 `premise_sha256`/`hypothesis_sha256` 与分组键 `group_id`。离线评测的 test 行需要 gold；在线组合路由的 test 预测不需要 gold。供组合路由的 dev 行必须带齐 `example_id`、`claim_id` 和两个 64 位十六进制 SHA-256；在线 test 预测另需 `sense_id`、`example_id`、`claim_id` 和成对有效 SHA-256：premise 是精确 source gloss，hypothesis 是精确候选句。test 预测还必须与 canonical source gloss 和 proof-used adjudicated claim 匹配。若使用 `group_id`，dev/test 行必须每行都提供；应使用规范化 lemma-group ID 来阻止同 lemma 的不同 sense 跨 split 泄漏。未提供时只按 `sense_id` 防重。每个离线评测文件必须只有其声明 split；example ID 不得在单个文件内重复，也不得跨 dev/test 文件复用。概率必须是有限的 `[0,1]` 数值且和为 1；布尔、NaN、无穷值和非有限大数均拒绝。CLI 报告保存 dev/test prediction 文件 SHA-256；研究运行还应给出 `--model-id` 和 immutable `--model-revision`。gold 需由双人语义标注及裁决产生。应分别报告 NLI 分类质量、概率校准、threshold gate 的精度/召回/覆盖、证明 soundness、source-rule faithfulness 和各错误类别，不把 NLI 准确率包装成证明率。

## 3. 后续连线所需的定义级数据

当前 frozen bundle 有 gloss/sense、dependency clauses 和来源索引，但没有随包提供 logicization pipeline；因此尚无可信的有类型 FOL clause gold、token-span-to-rule provenance、形式化错误标签、NLI 候选集或人工金标准。推进真实实验前，上游/项目需先给一小批双人标注数据：

```text
sense ID + 原始 gloss + 来源/span
        → semantic AST（论元、类型、变量、量词/否定/作用域）
        → directional rule(s) + 编译器版本 + provenance
        → proof checker (valid proof / model counterexample / unknown)
        → NLI scoring + dev-calibrated abstention
        → human adjudication and typed error label
```

下一步应将相同的 gold examples 同时喂给 Datalog prototype 和至少一个正式 prover adapter，单独测试 proof certificate tampering、未支持语法拒绝、sense/source mismatch，以及未知/缺规则时的 abstain 行为。


## 外部假设与来源规则必须分区

TACL 2025 的 FoVer 将由原文转写的 claims、额外 definitions 和 LLM 补充的 common knowledge 放进同一可满足性验证流程；论文结果显示外加常识有时帮助结论判断，也可能造成前提冲突并降低可执行率。这里得到的方法约束是：项目未来扩展问题 schema / proof artifact 时，需把 `source_assertions`、经人工审定的 `definition_axioms`、资源级背景事实和 `external_assumptions` 分开标识。证书应记录每条被用前提的来源类别与标识；针对“仅由 gloss 及其规则支持”的 query，应禁止依赖 external-assumption 集，或另行返回带条件的结论。

当前 `verified_reasoning_pipeline.py` 已实现显式 fact partition、`source_only` 输入过滤、fact-leaf partition/source-binding/claim-ref 证书重放，以及组合路由将每个 source fact 绑定到同 sense/gloss 的已审 gloss atom；仍未独立核验外部来源文件或人工语义裁决，也没有真实 gold 验证该策略。路径与来源标签仍由调用方声明，不能据此声称外部内容真实或 gloss 忠实。FoVer 全文筛读及边界见[结构化日志](../sources/literature_screening_log_2026-10-04_formal_nli.json)。

兼容 API 的分组输入检查也采用 fail-closed 契约：开发/测试行若不提供统一 `group_id`，必须逐行提供非空 `sense_id`；缺失或空值会返回明确的 `ValueError`，避免以裸 `KeyError` 中断。严格 NLI 导出入口会从候选 sidecar 导出 `group_id`，研究运行仍应优先使用该入口。


### 当前原型的类型系统边界

compiler v6 对旧 schema 仍只处理一元正谓词与共享目标变量；仅 0.7-draft 走显式目标变量的有限多元路径。`typed_program_validator.py` 可对显式版本化的 sorts、predicate signatures、常量与规则变量 sort 做形式兼容校验，Datalog closure 与 proof/countermodel replay 会重新运行该检查；pipeline 可携带 caller-provided type table。Phase160 将该检查的重算报告暴露在 strict route 的 `evidence_checks.typed_program_validation` 中；带类型系统但类型无效的程序在 pipeline 返回 `unknown`，原因码为 `invalid_typed_program`。未提供类型系统仍是 `not_requested`，表示 untyped proof，不当作 typed proof 报告。历史 annotation schema 0.2–0.4 仍须通过按 rule ID 的 side table 提供规则变量 sort；实验性 0.5-draft 将 claim 级 `variable_sorts` 编译进每条 Horn rule；0.6/0.7-draft 将 sort judgment 的 status/basis/rationale/evidence spans 和 review status 保留在 rule provenance，0.7 还绑定 `target_variable`，unresolved judgment 不会编译。该 provenance 不证明人工判断正确。两条路径都未连接权威 WordNet 类型本体，也不判断签名是否正确、gloss 是否蕴含规则或 span 是否忠实。0.5–0.7 尚未用于当前 v3 标注草案或真实 gold。输入契约与限制见[typed Datalog contract](typed_datalog_contract.md)、[标注协议](annotation_protocol.md)及[Source-only 证据链契约](source_only_evidence_contract.md)。
### Phase 38：OEWN resource-only stress frame

新增固定种子 20261006 的 360 项、9 层 hypernym stress frame，并完成 producer 到独立 replay 的完整运行。它覆盖直接/不同深度多跳、反向、同 POS 前向无闭包路径、跨 POS、缺失 synset、自指；首次 replay 发现并推动修复 self-link 缺少 `child_pos` 的 producer 输出契约。完整分层和 hashes 见[Phase 16/38 verifier 文档](phase16_oewn_hypernym_verifier.md)及Phase 38 报告。该 frame 仅为资源图实现压力覆盖；不提供 sense/释义准确率、semantic support gold 或开放世界否定。

## Phase 143：source-only 推理路由静态契约审计

CodeGraph 结构查询及当前代码阅读确认，`source_only` 要求所有事实显式分区，只保留带 source path、sense/gloss hash、reviewed claim refs 的 `source_assertion`；resource facts 与 external assumptions 被排除。正向结果需重放 proof certificate，未蕴含结果需重放有限 Herbrand countermodel；非法/不支持程序会转为 `unknown`。组合路由还将 proof facts/rules 绑定到裁决记录、测试 sense/gloss、NLI hypothesis hash，并要求固定 source bundle 的字节/索引核验通过。countermodel 只说明 supplied finite positive program 中未蕴含，不是开放世界否定或自然语言矛盾。此处为代码静态审计，不是运行时验证；没有真实 annotations、pair、NLI export 或 held-out 结果。实现文件哈希与逐项边界见[机器审计](../sources/verified_reasoning_route_contract_audit_2026-10-08_phase143.json)和深度报告。

## Phase 146：严格 source route 对 contextual NLI premise 的边界

当前 strict route 要求 NLI `premise_sha256` 同时等于 source gloss/input hash；此绑定确保 contextual hypothesis 判断能映射回被审阅 source，却不支持在 premise 前插入 lemma/POS header。未来可区分 `source_gloss_sha256` 与 `rendered_premise_sha256`：前者绑定 source facts、reviewed annotation 和 evidence spans，后者绑定 NLI prompt；二者再由外部固定 renderer version/manifest 关联。不得用 rendered hash 替换 source input hash，否则会丢失 source-only proof 证据链；不得将两者视为同一个字节串。此次仅静态检查，尚未实现或授权 contextual route。详见Phase 146。

## Phase 148：历史 Datalog bridge 证书格式迁移

Phase6 的 `oewn-00520548-n` bridge 曾在生成时通过当时的 checker，但当前 checker 对旧 proof result 的逐对象重算会发现 certificate node 缺少后来加入的 `source_bindings` 与 `source_claim_refs` 字段。旧 artifact 的 embedded validation 仍为通过，proof certificate 自身仍有效，且当前复核的节点集、边多重集相同；因此将其分类为 checker/certificate 格式演进，不作为当前可复算产物。Phase148 保存按当前 checker 新生成的 bridge，并由审计 CLI 再独立重放。该结果仅限冻结 witness 的结构性 ground Datalog 可导出性，不涉及 gloss 语义支持、WSD、替代 clauses 或许可。机器记录与复算入口见 [Phase148 audit](../outputs/phase148/witness_example_replay_audit.json) 及 `src/analysis/audit_witness_example_replay.py`。
