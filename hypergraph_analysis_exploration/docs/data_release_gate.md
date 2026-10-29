# 发布物许可与数据边界门槛

审计日期：2026-10-08（Phase275 完成 Phase274 输出面扫描后续人工检查；Phase220 来源权利覆盖更新、Phase209 inventory 一致性复核仍是相应专项的最新证据）。本文是工程发布清单，不是法律意见，也不判断各来源许可之间的法律兼容性。机器可读状态见 [`sources/data_release_inventory.json`](../sources/data_release_inventory.json)；详细来源审计见[数据来源与许可审查](data_provenance.md)。

运行 `python -m src.analysis.verify_data_release_inventory` 可只读复核 inventory 与本地固定归档、根许可文件状态及冻结包 manifest 的一致性。该命令不会修改许可状态，也不会作法律判断；缺失本地归档时会报告检查失败，不会自动下载或重建文件。

## 当前结论

**目前不能把整个工作区直接当作可公开发布的代码+数据项目。** 目前证据足以支持在本地复算冻结包结构和 OEWN 资源内关系，但不足以批准冻结包、带 gloss 的任务/输出或整个项目的发布。

2026-10-05 复跑 `python -m src.analysis.verify_data_release_inventory`：退出码 0，`inventory_consistent=true`；两份 OEWN ZIP 的 SHA-256 和 ZIP CRC、bundle manifest 的 head/clause/source-record 数、graph SHA-256、semantic fingerprint 与 head-kind 计数均匹配。工具仍返回 `release_clearance=not_cleared_for_public_release`，且确认 bundle 归档无内置许可文件、项目根目录无代码许可文件。该次核验只证明本机清单/归档/manifest 一致，不改变逐来源许可未评估的结论。
2026-10-08 Phase209 现态复跑：`inventory_consistent=true`，15/15 检查通过；OEWN ZIP SHA-256/CRC 与 bundle manifest 关键计数和图摘要一致。状态仍为 `not_cleared_for_public_release`；本项检查不处理来源逐条许可，也不验证 gloss 对规则的语义支持。脱敏聚合结果见[Phase209机器记录](../sources/data_release_inventory_audit_2026-10-08_phase209.json)，审计过程见Phase209报告。

| 发布对象 | 当前证据 | 当前决定 | 解除门槛 |
|---|---|---|---|
| 项目源码与文档 | 根目录没有 `LICENSE` 或 `LICENSE.md`；仓库尚无首个 Git 提交/远端 | 未声明代码许可；不得推断许可类型 | 权利人明确选定许可并批准版权/第三方声明，再加入许可文本 |
| OEWN 2025 / 2025 Plus 本地 JSON | 官方 2025-edition 页面固定了版本、下载 URI；本地归档 SHA-256 与项目记录一致。官方 LICENSE.md 说明 OEWN 基于 Princeton WordNet（适用 WordNet License），并在 CC BY 4.0 下进一步开发；分享/改编需向 Princeton WordNet 与 OEWN 团队署名，底层 WordNet 数据仍受其原始条款约束 | 可作为固定版本的本地分析输入；外发/再分发时必须逐项落实声明条件。下载 ZIP 不自带 license/readme 文件，需随发布单独保留官方许可和署名信息 | 锁定 tag/release、URI 与 SHA-256；提供 attribution 和上游许可链接/文本；人工确认改动说明与许可兼容；仅发布必要最小内容 |
| 学长提供的 154,206 clause 冻结包 | README/manifest 能核实包版本、图哈希和头数；可见 107,136 OEWN namespace、3,000 external、289 numbered-local heads，并含 115,235 份定义/WSD/来源 JSON；manifest 没有按记录给出确切上游 release/license | 仅限内部只读审计；整个包及 gloss-bearing 内容不公开 | 为每个来源记录重建 origin/version/license/attribution；筛除未清来源；对转换/改写和整包派生数据库单独作发布审查 |
| 标注任务、答案键、映射样本 | 路径已由 `.gitignore` 保护；部分文件含 raw/effective gloss、sense identity、来源路径或冻结图结构 | 仅本地内部分析，不分发 | 逐文件筛选、许可与数据保护审查；若公开，重建最小授权数据或发布合成/脱敏替代物 |
| 聚合审计与基准输出 | 一些报告为 text-free 聚合，但 Phase 16 关系证书、phase 9–12 资源比对等仍可能含 synset ID、relation、来源文件名或可复算数据库事实 | 不作整目录 blanket clearance；逐输出评估 | 做输出级内容扫描与许可/提取范围评估；确认发布所需输入可合法获取并且重算命令不依赖私有文件 |

## OEWN 版本和本地档案证据

上游 release 页面称 2025 与 2025 Plus 于 2025-12-31 发布，并列出 JSON 下载；Plus 包含从 Open English Namenet 中挑选、经人工核验的 proper nouns。2026-10-05 复核官方许可页：OEWN 基于 Princeton WordNet（适用 WordNet License），并在 CC BY 4.0 下进一步开发；分享或改编时须同时署名 Princeton WordNet 与 Open English WordNet 团队，底层 Princeton WordNet 数据仍受其原始条款约束。[官方 2025 release](https://github.com/globalwordnet/english-wordnet/releases/tag/2025-edition) · [OEWN LICENSE.md](https://github.com/globalwordnet/english-wordnet/blob/main/LICENSE.md) · [Princeton WNDB_License.txt](https://github.com/globalwordnet/english-wordnet/blob/main/WNDB_License.txt)。

在当前工作区，本地归档哈希复核为：

- `tmp/oewn-2025-plus-json.zip`: `8832b8fa26a14c0ba8c99bb1ef8db6f9e122a6d9193b65ca9e0ef572580fee7e`
- `tmp/oewn-2025-json.zip`: `7d749f6e2c39e6970e4997839dcf6e42fd281f3c2fae0171d2192bae8cfa4b51`

这两个 ZIP 与展开目录被 Git 忽略；忽略只避免把本机缓存误提交，**不等于该数据包已清权**。Plus ZIP 当前检查到 73 个成员、包内无 license/readme-like 文件，因此可发布副本需另附上游声明和版本信息。该哈希只证明本机字节固定，不证明冻结 bundle 中每条 gloss 来源于此 release。

### 2026-10-07：OEWN 2025 Plus 400 项盲标批次的 source-specific gate

Phase 121 输入 preflight 的锁定结果显示：400/400 raw gloss 与固定归档 cross-check 精确匹配，candidate frame、blind batch、manifest、cross-check 与答案键均通过其哈希/schema 门；该 preflight 同时明确 `protocol_signed=false`、`distribution_authorized=false`、无 external registration ID、无 annotation return files。批次 manifest 已记录 OEWN 2025 Plus 版本与归档哈希、归属/版权、CC BY 4.0 URI、官方 OEWN license notice URI、未改写 raw gloss 的处理说明和“仅作 annotation input”的用途限制。

官方 OEWN LICENSE.md 要求 attribution 给 Princeton WordNet 和 Open English WordNet team，并说明底层 Princeton WordNet 条款继续适用于该数据；Princeton 官方页列出 WordNet 数据库许可要求。[OEWN 官方许可](https://github.com/globalwordnet/english-wordnet/blob/main/LICENSE.md) · [Princeton WordNet 许可页](https://wordnet.princeton.edu/license-and-commercial-use) · [2025 release](https://github.com/globalwordnet/english-wordnet/releases/tag/2025-edition)。本地 manifest 的 attribution 字段提及 Princeton WordNet 与 OEWN 团队，且链接官方 license notice；本项审查记录其元数据与来源链，不作对许可兼容性或具体分发权限的法律判断。

**Gate 状态不变：** 该输入审计不能授权把批次发给外部标注者或公开发布。下一步须由项目负责人在审阅上游条款、使用场景与归属要求后明确记录外发范围；若更改已锁定 manifest/lock，必须重新生成并复核相关哈希，不能静默改写锁定输入。详细机器证据见[来源许可证据日志](../sources/source_release_rights_evidence_2026-10-06.json)中的 `annotation_batch_v3_rights_review_2026_10_07` 和Phase 132 报告。

### 2026-10-08：Phase185 版本化许可通知与 v3 frame 身份复核

Phase185 重跑 release identity audit，输出与 Phase144 逐字节一致（SHA-256 `373e25677bd9805443aa76770f2aa8daab8e7c56048dd065bed9277ba6f4d6aa`）。400/400 raw gloss 与本地固定 OEWN 2025 Plus ZIP 精确匹配，目标 sense 也均存在；但锁定 frame/source payload 仍有 1 条 POS 与 release 不一致、1 条 lemma set 不完整。blind batch 与 frame 一致，因此继承问题。不得直接修补 v3；若研究方案获批，应从固定发行版派生新版本 frame，复核 POS/lemma 并重建依赖 hashes。

许可来源改用版本固定证据：[OEWN 2025 release/tag](https://github.com/globalwordnet/english-wordnet/releases/tag/2025-edition) 对应提交 `dc343f2`；该 tag 的 [LICENSE.md](https://raw.githubusercontent.com/globalwordnet/english-wordnet/dc343f2/LICENSE.md) 与 [WNDB_License.txt](https://raw.githubusercontent.com/globalwordnet/english-wordnet/dc343f2/WNDB_License.txt) 的 SHA-256 分别为 `672cc8b5663e8dc74c4b07a9dcf477193853575b119908fd3dc0aeeb60a9dbbb` 与 `df30ec18fbabcdaf031b79ea026d3e6b959010cffe6dd7be9ac137822175b904`。后者指向 WordNet 3.1；[官方 WordNet 3.1 release](https://github.com/globalwordnet/english-wordnet/releases/tag/3.1)确认其 Princeton WordNet 3.1 来源及 WordNet License 背景。Princeton 当前许可页呈现 3.0 文本，不应单独替代这条 3.1 版本化 notice；本项目不据此判断法律兼容性。

固定 JSON ZIP 有 73 个成员，未含 license/readme/notice 类文件；未来获准分享的材料应保留适用 notice 与署名。现有 lock 仍为 `protocol_signed=false`、无 external preregistration ID、`distribution_authorized=false`；`release_clearance=not_assessed`，且本次审计只覆盖此 OEWN 输入，不清理混合来源 frozen bundle。机器记录见[Phase185 权利与身份复核](../sources/oewn_2025_plus_annotation_release_rights_review_2026-10-08_phase185.json)、[身份审计](../outputs/phase185/annotation_frame_release_identity_current.json)及深度报告。

## 首次公开发布前的最小流程

1. 先完成源码权限/贡献人确认并明确选择项目代码许可；未经作者授权，本项目不替用户选 MIT、Apache、GPL 等许可。
2. 拟发布清单按文件列出：来源、版本、哈希、许可、署名、修改说明、是否含 gloss/identity/源路径、是否重分发数据库实质部分。
3. 冻结包、raw/effective gloss、任务答案键以及含义项身份的输出默认为排除；仅凭 `oewn-*` 命名空间、文件哈希通过、或上游 OEWN 有开放许可，不足以解除排除。
4. 使用一个没有冻结包、没有 `.gitignore` 缓存的干净 checkout，执行 [CI 所覆盖的编译与合成单测](continuous_integration.md)；另对声称可复算的数据实验明确输入下载步骤、版本、哈希和许可证。
5. 每个准备发布的报告/图/JSON 都要进行单独的数据来源和标识扫描；不能因一个聚合报告不含 gloss，就推断整个 `outputs/` 目录可公开。

## Outputs 文件级筛查（Phase 18）

只读扫描器 `src/analysis/audit_output_release_surface.py` 为 `outputs/` 下每个文件记录相对路径、字节数、SHA-256、JSON 字段名和 Git 忽略状态；它**不保存字段值**，也不把任何文件标记为可发布。字段名检查只是启发式筛查，无法发现任意字段名下的文本、图像中的文字、许可证兼容问题或数据库实质提取，因此所有项目仍须人工审查。

复算命令：

```powershell
python -m src.analysis.audit_output_release_surface
```

默认报告写到 `outputs/phase18/output_release_surface_audit.json`；该清单包含本地文件路径和哈希，已由 `.gitignore` 排除。重复运行需显式加 `--force`。2026-10-03 本机扫描覆盖 44 个输出文件；5 个文件含 gloss/lemma 等文本风险字段，12 个文件含 sense/head/task 等身份或来源字段。扫描发现的带风险字段文件已加入 `.gitignore`，但忽略规则只防误提交，不表示它们已获许可或对外发布禁令的法律判断。最新细目在本机忽略报告中复算，不作为公开清权证据。

2026-10-06 为避免覆盖既有本机忽略报告，只读直接调用审计函数重新扫描当时 `outputs/`：覆盖 63 个文件，字段名启发式标记 12 个文本风险文件、21 个身份/来源风险文件；39 个文件被 Git 忽略，24 个未忽略。未忽略文件中没有身份/来源风险键；唯一未忽略的文本风险键是 Phase 18 报告的 `proof_family.definition`，经对照生成器确认它是算法定义说明字符串，不是词典释义或 source text。

2026-10-08 Phase274–275 覆盖当前 212 个输出文件：22 个命中文本/词汇字段名、41 个命中身份/来源字段名、53 个被 Git 忽略；类型为 186 JSON、19 JSONL、5 PNG、2 PY。四个未忽略的文本字段名命中经有限结构检查为计数/算法说明而非 gloss 载荷。五张 PNG 和两份脚本已逐项检查：两张图显示 OEWN/外部 source ID；两个旧脚本已改用项目配置和项目相对输出路径，但对应投影指标仍属不可作论文主张的 legacy exploratory analysis。字段扫描/人工可见内容检查不构成来源许可清权，也不检查所有 JSON 值或图片中的隐蔽信息。机器清单保存在本机忽略的 [`sources/output_release_surface_audit_2026-10-08_phase274.json`](../sources/output_release_surface_audit_2026-10-08_phase274.json)，阶段报告见Phase274与[Phase275](../../report/research_progress_deep_review_2026-10-12_phase278.md)。状态仍为 `not_cleared_for_public_release`。

## source-record 来源/许可元数据普查（Phase 23）

`src/analysis/audit_source_release_metadata.py` 从 `indexes/senses.jsonl` 遍历所有唯一 source-record 路径，逐文件核对 `checksums.jsonl` 并解析 payload。它只汇总处理目录家族、有限枚举的来源 inventory/schema/pipeline 标签、来源记录字段出现次数，以及字段名中可能表明许可、来源或版本的键；不保存 gloss、lemma、义项 ID、source path 或字段值。报告同时绑定 bundle integrity lock、sense index、checksum sidecar 与 payload 序列哈希。

复算命令：

```powershell
python -m src.analysis.audit_source_release_metadata
```

默认输出 `outputs/phase23/source_release_metadata_audit.json`，路径由 `.gitignore` 排除；重复运行需显式传 `--force`。2026-10-05 本地完整复算通过 bundle integrity lock v2，扫描 `indexes/senses.jsonl` 的 110,425 条 sense 记录和 115,235 条唯一来源引用；115,235/115,235 个唯一 payload（18,734,636,389 bytes）均可解析且其字节数与 SHA-256 均匹配 `checksums.jsonl`，重复路径引用和畸形索引记录均为 0。来源目录家族计数为：fully-parsed glosstag 84,393、ready-for-lingua 21,664、alternative/definition-WSD 5,625、strict proper-name 1,752、standard external 1,259、nonstandard merged 537、recovered history 5。字段名启发式在 0 个 payload 中发现显式许可/版权/署名类字段；来源/版本/哈希等来源线索字段在 115,235 个 payload 中均有出现。以上报告只保存白名单分类和字段路径计数，不含 gloss、lemma、义项 ID 或源文件路径。

字段细目还显示，嵌套 `source_record` 中 `target_source_inventory` 出现在 3,125 条、`target_source_kind` 出现在 2,488 条记录；更具体的 `source_version` 位于 provenance evidence 子结构，仅覆盖 3,118 个 payload，`download_url` 覆盖 254 个。它们是字段出现次数，不是已经核实的来源到发行版/许可证映射；该审计也没有验证 URL 可用性、来源声明真实性或多个证据字段能否共同确定唯一上游。故“来源/版本线索字段覆盖全部 payload”不表示逐条版本均已识别。

这次普查把来源追溯工作拆成可盘点的字段覆盖与家族计数。字段名启发式找不到许可键不证明许可不存在；来源/版本字段出现也不等于其权利已确定。当前 bundle 仍缺逐记录可核实的上游 release、适用 license 与 attribution 绑定，所以报告的 `release_clearance` 仍为 `not_assessed`。无论报告结果如何，均不得自动提高项目发布 clearance，仍需逐来源人工确认 origin/version/license/attribution 及兼容性。完整机器汇总在被忽略的 `outputs/phase23/source_release_metadata_audit.json`。

2026-10-06 的 Phase 24/25 在[数据 provenance 审计](data_provenance.md)中对替代释义来源家族逐条核验 5,625 份 payload checksum，并将 90 个候选来源 profile 与高频来源方的官方条款证据并列记录。审计发现 GCIDE、MeSH、EMBL-EBI OLS 和多个独立本体来源；它缩小了待人工核查范围，但没有验证所有 payload 与上游发行版的逐条映射，也没有解决许可兼容性。因此冻结包、释义材料和带身份结果的“仅内部使用”门槛维持不变。

项目发布状态只在所有门槛均有可查证记录后更新。本文件本身不构成授权，也不自动开放当前被忽略的本地缓存、冻结包或任务文件。

2026-10-06 Phase 39 对 Phase 23 source metadata census、发布 inventory、标注 lock 和本机 archive/bundle 一致性检查作了汇总复核，并解释 alternative/definition-WSD 目录的 5,627 个 JSON 文件中有 2 个不是被索引的 source-record payload。复核没有改变 `not_cleared_for_public_release` 状态；详见阶段性深度分析报告 Phase 39。

2026-10-07 Phase 88–90 将 OEWN 2025+ 六条候选 evidence 唯一匹配到固定归档记录，并以 sense identity 连接到六个图 head、11 条 rule/hyperedge 和 selected witness。精化后的 lineage/3 显示，只有 2/6 selected-witness source documents 同时包含候选 payload 路径、匹配的 OEWN ILI/定义散列和定义文本 SHA-256；另两条候选仅见于非 witness 子句，另两条无 active-clause 来源路径。结构 lineage 不证明 gloss 语义支持，不清理 bundle 其余来源，也不判断许可兼容性。项目仍为 `not_cleared_for_public_release`；详见Phase 90和[机器输出](../outputs/phase89/oewn_2025_plus_graph_lineage.json)。

## GCIDE 0.54 子来源范围补充（Phase 124）

上游 v0.54 README 的来源模型说明，GCIDE 定义可能来自 1913 Webster、WordNet 1.5、Century Dictionary 或志愿者，且一个段落可含多来源标记。GPL v3-or-later 的提供方声明不等于这些子来源已在冻结项目中逐条绑定，也不自动解除混合 source-record bundle 的发布限制。`GCIDE_0.54` 画像现有 1,573 payload 画像计数与 1,580 evidence-object 计数来自不同审计口径，尚未对账。必须先把候选 payload 与确切官方 0.54 archive/记录标签对上，并追踪其进入规则/witness 的路径，再考虑任何子集发布。当前不下载/再分发该 archive、不判定条目授权；整体 clearance 不变。见Phase 124和[结构化证据](../sources/source_release_rights_evidence_2026-10-06.json)。

### GCIDE profile 计数对账（Phase 125）

新审计器在冻结 bundle 内仅扫描索引指向的 5,625 个 alternative/definition-WSD payload（约 1.40 GB），验证其冻结 checksums，并汇总 GCIDE evidence 字段。1,573 个 payload 含 `GCIDE_0.54` 来源标记，共 1,580 条 evidence objects；每项均有 `source_version=0.54` 与格式合法的 definition SHA-256，按 payload 的 multiplicity 为 1×1,567、2×5、3×1。此结果对账了 Phase 24 payload profile 数与权利日志 evidence-object 数，但没有把哈希匹配到官方 tarball、恢复段落级子来源或审查规则/witness 使用；发布状态仍未清权。详情见[审计 artifact](../outputs/phase125/gcide_source_evidence_census.json)。

### 官方归档哈希交叉审计（Phase 126）

官方 FTP 的 0.54 tar.gz 已下载到本地并与 GNU 下载页公布的 MD5 一致；归档内 179,781 个 `<def>` 块与 1,562 个冻结定义哈希按明确命名的变换交叉比较。原始内层字节命中 88 个不同冻结哈希；去标签、HTML 解码、NFC、空白归一化后命中 846 个（归档出现 854 次）。受限 same-payload 核查表明，1,579/1,580 条 GCIDE evidence hash 等于其 `synset.raw_definition` UTF-8 SHA-256；另 1 条未匹配同 payload 字符串，却在归档中规范化命中一个 WordNet 标记段落。多数匹配因此绑定到冻结 gloss 文本；异常项提示一条具体的 WordNet 混合来源审查线索，但不代表独家来源、语义支持或 rule/witness lineage。归档 detached 签名未验证，段落标记也不足以裁定其他条目的混合子来源或许可。归档匹配不会改变项目的 `not_cleared_for_public_release` 状态。审计范围、指纹及局限见[Phase 126 artifact](../outputs/phase126/gcide_archive_hash_crosswalk.json)和报告。

### 全 GCIDE 来源族的 graph/witness 路径审计（Phase 127）

1,573 个 GCIDE payload 均唯一对应 sense index identity；1,188 个 payload 在 active clause source document 中，886 个被 selected witness clause 的来源文档直接引用，302 个只在其他活动子句中，385 个完全没有 active-clause 来源路径。1,530 个非 seed witness clause 均与 graph rule/hyperedge 对应；40 个 seed witness 不选取 clause。唯一 WordNet-marker 异常 hash 所在 payload 没有 active source-document/witness 路径。以上是冻结包内部路径级证据，不表明释义文本推出规则，也不清理许可证；整体 `not_cleared_for_public_release` 状态不变。见[Phase 127 artifact](../outputs/phase127/gcide_graph_lineage.json)与深度报告。

### Selected-witness gloss 到归档子来源标记（Phase 128）

在 886 个 selected-witness-linked payload 中，506 个 gloss hash 在 GCIDE 0.54 archive 中按明确命名的规范化匹配；46 个 payload 匹配到至少一个 WordNet-marked 段落，433 个匹配到至少一个 Webster 1913-marked 段落。两类及其他来源 marker 可重叠，因为同 hash 可能出现在多个段落。此项只给出匹配与标记共现线索，不证明 source span 语义支持规则 literal 或授权再分发；380 个未匹配项也只是在当前 transform 下无命中。归档签名未验证，整体 release gate 不变。见[Phase 128 artifact](../outputs/phase128/gcide_marker_witness_crosswalk.json)和报告。


### Phase 163 当前全量 payload 复算

2026-10-08 以自定义新输出重放 `audit_source_release_metadata`，未覆盖 Phase23 忽略报告。115,235 个唯一来源 payload（18,734,636,389 bytes）均与 checksums 的长度和 SHA-256 相符，重复路径与畸形索引记录均为 0。当前结果文件 hash 与 Phase23 历史产物相同。0/115,235 payload 含 license/copyright/attribution/rights 类字段名只是结构启发式，不能据此判定许可不存在；`release_clearance` 保持 `not_assessed`。见[Phase163机器结果](../outputs/phase163/source_release_metadata_audit_current.json)与报告。
## Phase218 现态清单复核（2026-10-08）

再次运行 `python -m src.analysis.verify_data_release_inventory`，`inventory_consistent=true`，15 项一致性核查通过；工具仍将状态保持为 `not_cleared_for_public_release`，因为此命令只核对本地归档、清单和 bundle manifest，不判断各来源许可兼容性。v3 preflight 及 presentation preview 也仍明确 `distribution_authorized=false`。见Phase218启动门报告与[机器记录](../sources/annotation_and_track_a_launch_readiness_audit_2026-10-08_phase218.json)。

## Phase220 来源权利 crosswalk 现态（2026-10-08）

只读复算将 90 个 Phase24 source profiles 与权利日志按 exact source-label 对账：25/90 profiles 命中同名日志，65/90 未命中。profile-payload 计数合计 3,595，不能当成唯一记录数；命中只代表来源标签有日志行，既不代表 payload/archive/version 对齐，也不代表许可兼容、署名充分或公开授权。最大的未匹配组仍是 22 个 `noncanonical_or_nonscalar` profiles（1,199 profile-payload 计数）；MeSH 和 OLS 需分别按格式/版本/实际缓存字节与记录做 crosswalk。项目状态保持 `not_cleared_for_public_release`。详细范围和下一步见Phase220报告及[机器 crosswalk](../sources/source_rights_coverage_audit_2026-10-08_phase220.json)。

## Phase221 MeSH/OLS 记录绑定进展（2026-10-08）

5,625/5,625 个受限来源族 payload checksum 通过；目标为 461 unique payload、631 MeSH/OLS evidence objects。130 个 direct MeSH/OLS-MeSH 共现 payload 的 identifier 末段经显式 token 规范化后与当前 NLM MeSH REST API 逐项匹配，130/130 返回 200 并回显相同 ID。此项只建立当前记录 ID 可解析，不建立 frozen cache 的历史 release/serialization/bytes；OLS 本地 source_version 仍是 `local_exact-query_cache_snapshot`，公开状态因此不变。NLM 的 attribution/currentness 条款仍需在任何再发布讨论中落实；本项目仍为 `not_cleared_for_public_release`。详见Phase221报告及[机器记录](../sources/mesh_ols_record_binding_audit_2026-10-08_phase221.json)。

### Phase 222 前向捕获合同状态（2026-10-08）

新 schema 仅规定未来采集应怎样绑定 frozen payload/evidence ordinal 与上游 artifact/API bytes；当前 checkout 没有可连接的 producer，故合同尚未集成。不能把当前 API ID 解析提升为历史版本绑定，不能从 provider notice 自动推断许可兼容或发布授权。冻结混合来源数据的 `release_clearance` 与公开 gate 均不变；下一步先定位或建立 versioned acquisition component，再做 schema validation 和端到端 replay。见[合同](source_evidence_capture_contract.md)、[schema](../config/source_evidence_capture.schema.json)与Phase222报告。

### Phase 223 外置 producer 边界（2026-10-08）

Frozen bundle 没有包含其历史逻辑化/WSD producer；历史 pipeline label 没有实现哈希，引用的两个输入文件当前不可用。完整的历史生成流程因此不能仅凭冻结输出重放。source-DNF 覆盖和结构 replay 统计不会决定许可；release clearance 仍为 `not_assessed`。以后任何新采集都必须记录 producer、parser、normalizer 精确实现哈希和上游字节身份，见[捕获合同](source_evidence_capture_contract.md)与Phase223报告。
