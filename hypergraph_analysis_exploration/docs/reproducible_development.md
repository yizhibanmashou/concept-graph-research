# 可复算开发环境

## 核心代码环境

受维护的 `src/analysis`、`src/logic` 和 `tests` 使用 Python 标准库，不需要安装第三方包。最低支持版本为 Python 3.10；CI 在 Ubuntu 上检查 3.10–3.13，并在 Windows 上检查 3.10 与 3.13。命令须从仓库根目录运行，以保持 `src.*` 导入路径有效。

Windows PowerShell 可选择创建隔离环境：

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
```

macOS/Linux 可用：

```sh
python3.10 -m venv .venv
. .venv/bin/activate
python --version
```

虚拟环境是可选的；无需执行 `pip install`。受维护代码的 CI 检查命令见[持续集成检查范围](continuous_integration.md)。

## 复算数据边界

轻量的纯代码流程（例如 Markdown 链接审计、逻辑原型和合成输入上的单元测试）不需要外置语料。完整冻结超图审计需要项目配置所指向的冻结 bundle；OEWN 词面 baseline、释义交叉核对及相关来源审计需要相应 OEWN release 或 source payload。运行这些流程前，先核对其阶段文档中的版本、哈希、输入路径及许可条件。外部数据保持仓库外，不要把源 payload、盲标答案键或本机路径加入版本控制。

`archive/legacy_phase1_5/` 是只读历史区，不属于受维护入口；其第三方依赖和旧导入路径未经整理，不保证可复跑。不要据此为核心环境添加依赖。

## 复算记录

每次生成研究结果时，随结果记录所用脚本/提交、命令、Python 版本、输入 release 或 bundle 标识与 SHA-256、输出路径，以及任何跳过项。若输入数据不在当前工作区或无法确认权限，应记录为未复算，而不是用 README 中的历史数字替代本次运行。


## Phase 161：运行环境与外置数据边界审计

维护中的 `src/` 与 `tests/` 共 132 个 Python 文件通过 AST 解析，未发现非标准库且非项目内的顶层导入；本机 Python 为 3.13.9，配置 CI 声明覆盖 Ubuntu 3.10–3.13 和 Windows 3.10/3.13。本轮没有运行 CI 或测试。项目配置指向仓库外 sibling frozen bundle，本机目录和 `manifest.json` 存在，但未执行 bundle integrity replay；因此克隆仓库可重现纯代码/合成流程，不等于可单独复现完整数据审计。机器记录见[Phase161 环境审计](../sources/reproducibility_environment_audit_2026-10-08_phase161.json)，分析见Phase161 报告。


## Phase 162：frozen bundle integrity lock 重放

2026-10-08 使用项目配置解析外置 bundle 路径，并调用只读 `verify_frozen_bundle_integrity()`：manifest semantic fingerprint 和 6 个锁定文件 hash 全部匹配。此入口没有遍历 `checksums.jsonl` 中的所有 source-record payload；不能将结果写成当前全 payload 重算通过。逐文件 hash 见[Phase162机器结果](../outputs/phase162/frozen_bundle_integrity_replay.json)，过程和边界见Phase162报告。


## Phase 163：来源 payload 全量 checksum 复算

2026-10-08 重放 `indexes/senses.jsonl` 引用的全部 115,235 个唯一来源记录，共 18,734,636,389 bytes；全部 JSON 可解析，byte count 与 SHA-256 均匹配 `checksums.jsonl`，无重复路径或畸形索引记录。当前聚合结果与 Phase23 留存报告 SHA-256 完全一致。它是 source-payload 字节完整性证据，不是上游来源真实性、许可或语义有效性证明。见[Phase163机器结果](../outputs/phase163/source_release_metadata_audit_current.json)与深度报告。


## Phase 181：可复跑的环境/数据路径快照

从仓库根目录运行：

```powershell
python -m src.analysis.audit_reproducibility_environment
```

该只读命令输出 `sources/reproducibility_environment_audit_current.json`，摘要包括当前 Python patch 版本、`src/` 与 `tests/` 的 AST/import 静态扫描、显式依赖清单、CI 中的 Python/OS 矩阵、仓库许可文件标记，以及 `project_config.json` 指向的外部 bundle 和 manifest 是否存在。它同时记录维护源码树、审计脚本、project config、integrity lock 和 CI workflow 的 SHA-256。已有输出需显式加 `--force` 替换；`--output` 只允许指定项目目录内的路径。

2026-10-08 本机复算：Python 3.13.9；133 个维护 Python 文件均通过 AST 解析，未检出非标准库且非项目内顶层导入，也没有发现依赖清单；CI 配置包含 Ubuntu 3.10–3.13 与 Windows 3.10/3.13。外部 bundle 路径和 manifest 在本机存在。此报告不执行 CI/测试、不重放 bundle integrity lock，也不哈希所有 source payload；其输出不能证明完整数据复现或任何发布许可。完整分析见Phase181报告和[机器快照](../sources/reproducibility_environment_audit_current.json)。

## Phase 184：冻结图与 witness 现态重放

在工作区中运行 `python -m src.analysis.frozen_hypergraph_audit --output outputs\phase184\frozen_hypergraph_current.json` 和 `python -m src.analysis.minimum_witness_audit --output outputs\phase184\minimum_witness_current.json`。两项命令成功；Phase184 outputs 分别与 Phase175 对应 JSON SHA-256 完全相同。审计只证明固定正 Horn bundle 与形式 certificate 结构，不覆盖 gloss entailment、来源权利、人工 gold 或全局最小 basis。运行范围与统计见Phase184报告。

## Phase 190：OEWN 候选工作量审计的现态重放

从仓库根目录重跑：

```powershell
python -m src.analysis.audit_oewn_hypernym_candidate_workload --output outputs/phase188/oewn_hypernym_candidate_workload_phase190_replay.json
```

该命令对 hash-locked 400 项 frame 与 OEWN 2025 Plus 输入重建 direct-hypernym inventory，再导出聚合 workload counts。必须指定新输出路径；命令默认拒绝覆盖既有 JSON，`--force` 仅在明确要替换时使用。本次 replay 输出与 Phase188 原输出逐字节一致。该流程复核固定输入上的构建/计数可复算性，不检验 gloss 语义、标注 gold、power 或发布权利。详细哈希、结果和限制见Phase190报告及[机器审计记录](../sources/oewn_hypernym_candidate_workload_replay_2026-10-08_phase190.json)。
## Phase 191：锁定 frame 身份差异的候选影响

重放聚合影响审计：

```powershell
python -m src.analysis.audit_oewn_candidate_identity_impact --output outputs/phase191/oewn_candidate_identity_impact_replay.json
```

输出目录必须位于 `outputs/` 下且目标文件不能已存在。审计会重跑锁定 frame/release identity audit 和 pinned-release candidate inventory builder；只写计数，不写 sense ID、lemma/gloss、标签或 hypothesis。它报告 mismatch 率、与 direct-hypernym cohort 的连接以及依赖未确认 surface 策略的计数敏感性。不会修复或重锁旧 frame。Phase191 主输出与独立新路径重放逐字节一致。详细输入哈希、聚合结果和边界见Phase191报告与[机器审计](../sources/oewn_candidate_identity_impact_audit_2026-10-08_phase191.json)。

## Phase 195：NLI leakage component manifest

从项目根目录运行：

```powershell
python -m src.analysis.build_nli_diagnostic_leakage_components opaque-keys.jsonl outputs/nli-diagnostic-leakage-components.json
```

输入必须是 UTF-8 JSONL，每行只包含 `example_id` 与 `leakage_keys`；每个 leakage key 严格含 `namespace` 和小写 64 字符 `key_sha256`。禁止放原文、gold、model scores 或额外字段。共享相同 `(namespace, key_sha256)` 的记录通过并查集传递闭包归入同一个 `group_id`；key 与行顺序不影响成员分组、group ID 和 assignment 排序。manifest 同时记录原始输入字节 SHA-256，所以输入行序改变时 manifest 文件 hash 会变化。输出 schema 为 `nli-diagnostic-leakage-components/0.1`，包含 opaque member IDs 与 group IDs、component size histogram、输入文件 SHA-256；既有输出会被拒绝，不覆盖。

该工具只生成 leakage connected components，不分配 dev/test、不进行分层随机抽样、不声明 statistical unit 或校准保证。低熵私有 ID 的普通 SHA-256 可被字典猜测；此工具不匿名化输入，使用者应提供稳定 HMAC 摘要或随机 opaque token。冻结 protocol 前不得据此建正式 split。实现和边界见Phase195报告。

## Phase 196：witness DAG 树展开审计

从项目根目录运行：

```powershell
python -m src.analysis.witness_tree_expansion_audit --output outputs/phase196/witness_tree_expansion_current.json
```

该命令记录 Phase196 时的 v1 执行路径；目标 JSON 已作为历史结果保留，当前分析器已升级到 v2，直接复用此路径会被安全拒绝。当前版本的复算方法见下方 Phase197。

命令校验 frozen bundle integrity、原 selected witness 结构证书，以及重建的 lexicographic minimum-depth 证书；随后计算 DAG 的递归 proof-tree occurrence 数和最小深度 tie alternatives 下的逐根展开规模上下界。输出不包含 atom IDs 或文本，巨大树规模以 bit length、分位数和阈值计数表达。结果与统计定义见Phase196报告和[机器输出](../outputs/phase196/witness_tree_expansion_current.json)。该命令不评估 gloss support、sense correctness、来源许可或下游效用。

当前版本同时重建最小递归树节点出现次数的 minimum-depth witness certificate：先筛出最小 depth clauses，再动态规划选择树规模最小 body，平局按字典序；重建 certificate 需通过 witness validator，独立递归重算必须逐 head 等于 DP 值。Phase197 复算命令：

```powershell
python -m src.analysis.witness_tree_expansion_audit --output outputs/phase197/witness_tree_expansion_current.json
```

Phase197 聚合结果、代码/输出 SHA-256 和结论边界见深度报告及[机器审计](../sources/witness_tree_expansion_audit_2026-10-08_phase197.json)。这只是形式结构成本基线；未验证 gloss support 或运行时资源，不更改默认 witness 和冻结图。

## Phase 198：compact witness 的 source-index link 审计

运行：

```powershell
python -m src.analysis.compact_witness_source_trace_audit --output outputs/phase198/compact_witness_source_trace_current.json
```

命令读取冻结 rules、selected witness、sense index、checksums sidecar，并重建 Phase197 相同的 compact minimum-depth witness。它比较每条 selected/compact clause 的 source-document link、该 head 的 source_records 元数据及 checksum metadata 条目；仅输出聚合数值。它不读取 source payload bytes，不重新计算 payload hash/identity，也不作语义判定。输出和独立 replay SHA-256、实现哈希及边界见Phase198深度报告与[机器审计](../sources/compact_witness_source_trace_audit_2026-10-08_phase198.json)。每次重跑须指定尚不存在的输出路径。

### Phase199：完整 payload hash 与 synset identity 复核

```powershell
python -m src.analysis.compact_witness_source_trace_audit --verify-payloads --output outputs/phase199/compact_witness_source_trace_verified.json
```

此模式逐个读取 selected/compact 两组 witness source-document 并集，对 payload 重算 SHA-256、byte count，并校验 payload 中的 synset identity 与每组关联 head 相同。每个 payload 默认最多 16 MiB；结果聚合，不输出 path/ID/原文。当前全量复算见Phase199报告与[机器审计](../sources/compact_witness_source_trace_audit_2026-10-08_phase199.json)。它验证冻结来源 payload 的字节和 identity 自洽，不判断 gloss semantic support、许可或来源上游真实性。每次复算须指定一个尚不存在的输出路径。

### Phase200：changed-clause source branch / WSD ID 结构对齐

```powershell
python -m src.analysis.compact_witness_source_logic_alignment --output outputs/phase200/compact_witness_source_logic_alignment_paired.json
```

该命令仅分析 selected 与 compact 选择不同的 heads。它逐个重新验证关联 payload 的 checksum 与 synset identity，解析 `definition.logic` 的 part-ID branches，映射其 `part_results` 自动 WSD sentence synset-ID unions，再与 graph clause literal sets 计算 exact/subset 集合重合及同 head 配对差异。聚合输出和边界见Phase200报告及[机器审计](../sources/compact_witness_source_logic_alignment_2026-10-08_phase200.json)。此结构诊断不评估自然语言语义蕴含，也不能替代人工 gloss-span support gold。

## Phase206：冻结超图与 witness 当前复算

```powershell
python -m src.analysis.frozen_hypergraph_audit --output outputs/phase206/frozen_hypergraph_current.json
python -m src.analysis.minimum_witness_audit --output outputs/phase206/minimum_witness_current.json
```

2026-10-08 在 Windows / PowerShell、Python 3.13.9 上从项目根目录执行，两命令均成功。两份输出与 Phase175、Phase184 对应结果逐字节一致。当前 frozen audit 确认 110,425 heads、154,206 clauses、917,767 dependency literals、85 basis atoms；bundle lock、完整 closure、witnesses、nodes/hyperedges 对齐均通过。单 basis 删除时，selected-witness descendants 在 66/85 例高估精确非 seed AND/OR closure 损失，19/85 相等，0 低估；因此精确删除分析须继续运行 closure。Phase206 复算记录包括解释器版本、输入/实现/输出 hash 和指标边界，见深度报告与[机器记录](../sources/frozen_graph_witness_replay_2026-10-08_phase206.json)。本轮没有重哈希全部 source payload；full-payload 证据仍见 Phase163/199。

## Phase207：Git 变更历史尚无初始基线

只读核查显示当前分支 `master` 尚无 commit，Git tracked file 数为 0；893 个非忽略文件与 390 个忽略文件均处于初始 Git 状态。故当前不能生成完整源码树的 repo-level diff 或依提交 SHA 标识运行版本。Phase206 对具体输入、实现和结果的 SHA-256 记录仍有效，但不能代替 Git 历史。初始提交范围涉及 JSON/JSONL、历史结果和压缩文件，需先确认纳入/排除政策。本轮没有暂存或提交任何文件。状态与建议见Phase207报告和[机器摘要](../sources/git_provenance_readiness_audit_2026-10-08_phase207.json)。

## Phase209：当前维护环境与发布 inventory 复核

```powershell
python -m src.analysis.audit_reproducibility_environment --output outputs/phase209/reproducibility_environment_audit.json
python -m src.analysis.verify_data_release_inventory
```

2026-10-08 在 Python 3.13.9 执行：维护代码 140 个 Python 文件 AST 解析错误为 0、未发现第三方顶层导入，配置的外部 bundle manifest 存在。CI 的 Ubuntu 3.10–3.13 / Windows 3.10、3.13 是静态 workflow 配置，不代表实际 CI 通过。发布 inventory 15 项一致性检查均通过，但 `release_clearance=not_cleared_for_public_release`；此检查不执行完整 payload 重哈希，也不判断许可或 gloss 语义支持。详细边界见Phase209报告、[环境机器快照](../outputs/phase209/reproducibility_environment_audit.json)和[发布 inventory 聚合审计](../sources/data_release_inventory_audit_2026-10-08_phase209.json)。

## Phase210：冻结来源记录全量 checksum 复算

```powershell
python -m src.analysis.audit_source_release_metadata --output outputs/phase210/source_release_metadata_audit_current.json --progress-every 20000
```

该命令验证 bundle integrity lock v2，并逐一读取当前 `indexes/senses.jsonl` 引用的唯一 source-record JSON，核对 JSON 可解析性、byte count 与 SHA-256。2026-10-08 当前复算为 115,235/115,235 个 payload 匹配、0 重复路径引用、0 畸形 sense-index 行，共 18,734,636,389 bytes；聚合输出与 Phase163 的 JSON SHA-256 完全相同：`9ff9ea44209fdb27e7967123ed9570f5a95ca236d6fc147ae955aa34f4d6dc2d`。它验证当前冻结包内部字节自洽，不验证上游真实性、来源许可兼容性或 gloss→rule 语义支持。结果和边界见Phase210报告及[机器输出](../outputs/phase210/source_release_metadata_audit_current.json)。

## Phase213：冻结 AND/OR 图与 witness 当前复算

```powershell
python -m src.analysis.frozen_hypergraph_audit --output outputs/phase213/frozen_hypergraph_current.json
python -m src.analysis.minimum_witness_audit --output outputs/phase213/minimum_witness_current.json
```

2026-10-08 在 Windows 11 / PowerShell、Python 3.13.9 下运行，两条命令均成功。两个 Phase213 输出均与 Phase206 对应 JSON 逐字节一致；冻结图完整性检查、110,425 条 witness 和最小深度证书全部通过。85 个 basis deletion 中，selected-witness descendants 高估精确非 seed AND/OR closure loss 66 次、相等 19 次、低估 0 次，故精确删除影响仍需重算完整 AND/OR closure。记录输入、代码与输出哈希及结论边界见Phase213报告和[机器记录](../sources/frozen_graph_witness_replay_2026-10-08_phase213.json)。本轮没有全量重哈希 source payload；结构证书不证明 gloss 语义支持、许可或下游效果。


## Phase272：冻结 AND/OR 图与最小深度 witness 的再次现态重放

以下命令从 `hypergraph_analysis_exploration/` 运行，数据路径已按当前目录结构调整；复跑时若输出文件已存在，请改用新的输出路径。

```powershell
python -m src.analysis.frozen_hypergraph_audit --output outputs/phase272/frozen_hypergraph_current.json
python -m src.analysis.minimum_witness_audit --bundle "../OEWN" --output outputs/phase272/minimum_witness_current.json
```

2026-10-08 在 Windows 11 / PowerShell、Python 3.13.9 下，两命令均成功。两份 JSON 分别与 Phase213 字节一致：冻结超图 SHA-256 `f8a588a1ea27a77bf42b1be49c85872db7e74b9a86d62b6c92befdea7e2fe516`，最小 witness SHA-256 `0879dac51e1a604f474935be8fc65588ebabecaa3a291a9860fd4eb6005f9dba`。完整 lock、closure、110,425 条 witness 与最小深度证书均通过。85 个 basis deletion 中，selected-witness descendants 高估精确非 seed AND/OR closure loss 66 次、相等 19 次、低估 0 次；精确 deletion 影响仍须重算完整 closure。该复算没有全量重哈希来源 payload，不证明 gloss 语义支持、许可、NLI 或研究效果。详情见[Phase272 深度报告](../../report/research_progress_deep_review_2026-10-12_phase278.md)与[机器记录](../sources/frozen_graph_witness_replay_2026-10-08_phase272.json)。



## Phase214：NLI 与证明路由契约复核

本轮只读对照 Phase176 审计哈希、当前 NLI selector/exporter/strict route、逻辑验证文档及 Track A 裁决备忘录。Phase176 的三个核心源码文件与逻辑文档哈希保持一致。实现使用固定阈值网格上的精确二项检验和 Bonferroni，但有限样本保证仍依赖 IID 校准单位、模型/网格冻结与分布稳定；唯一 group ID 不能证明独立性。导出器及 strict route 绑定调用方声明的 `model_id/revision` 与文件摘要，不构成推理服务的模型执行 attestation。Track A 现有 raw/rendered 双哈希、relation-edge/surface 和 edge-level gold 缺口仍在，设计 memo 仍未批准。本轮未运行测试、模型或数据，也未改 schema/协议。细节见Phase214 报告和[机器审计](../sources/nli_proof_route_contract_review_2026-10-08_phase214.json)。


## Phase215：全部最小深度替代 clause 来源覆盖

```powershell
python -m src.analysis.minimum_depth_alternative_source_audit --verify-new-payloads --output outputs/phase215/minimum_depth_alternative_source_audit.json
```

该命令核对冻结 bundle、selected witness 结构和最小深度，枚举每个非 basis head 的全部 minimum-depth clauses，将 clause index 关联到 source document，并验证 source-record/checksum 元数据覆盖。`--verify-new-payloads` 会先核验 Phase199 输入、实现和输出哈希，再复用其 selected/compact witness payload 基线，只读取此前未覆盖的 document/head payload，校验字节数、SHA-256 与 synset identity。当前增量为 37 个关联/文档、7,694,723 bytes，0 checksum/identity mismatch；历史 110,399 文档 payload 基线不在本轮重复读取。输出会区分本轮实际读取数与复用的历史基线。完整结果及边界见Phase215报告、[机器记录](../sources/minimum_depth_alternative_source_audit_2026-10-08_phase215.json)和[聚合输出](../outputs/phase215/minimum_depth_alternative_source_audit.json)。来源完整性不等于 gloss 语义支持、规则正确性、许可或效果。


## Phase216：替代来源映射生成与独立重放

```powershell
python -m src.analysis.minimum_depth_alternative_source_audit --source-map-output outputs/phase216/minimum_depth_alternative_source_map.jsonl --output outputs/phase216/minimum_depth_alternative_source_audit.json
python -m src.analysis.verify_minimum_depth_alternative_source_map --output outputs/phase216/minimum_depth_alternative_source_map_verification.json
```

第一条命令生成逐条 hashed clause-to-source 关联映射；第二条从 frozen graph、minimum-depth rules、sense index 和 checksums sidecar 重建后逐行精确比较，并核验映射哈希/行数与聚合审计一致。现态结果 127,380/127,380 行一致，映射 54,626,360 bytes。键的 SHA-256 是确定性伪名，不是匿名化；应与冻结 bundle 一起按受限内部数据管理。该 replay 不读取 source payload；payload checksum 与 synset identity 范围见Phase215报告。映射不是 gloss-support 判定或许可清权。详见Phase216报告、[机器记录](../sources/minimum_depth_alternative_source_map_2026-10-08_phase216.json)和[验证输出](../outputs/phase216/minimum_depth_alternative_source_map_verification.json)。
