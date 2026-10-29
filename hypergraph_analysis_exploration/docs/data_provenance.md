# 冻结包数据来源、版本与公开边界

审查日期：2026-10-05。本文区分 OEWN 上游资源的许可与学长提供的合并冻结包的来源/许可；前者不能自动覆盖后者的每个组成部分。当前工程发布门槛另见[数据发布门槛](data_release_gate.md)及[`data_release_inventory.json`](../sources/data_release_inventory.json)；它们是工程 provenance 状态记录，不是法律意见。

本地默认冻结包根目录从项目根目录下的 `config/project_config.json:data_source.root` 解析；命令行可通过 `--bundle` 指向经核验的其他只读副本。配置路径只解决可移植性，不构成来源版本或许可验证。

## 已核实的包内事实

冻结包 `OEWN` 的 `README.md` 将其标为 110,425 heads / 154,206 clauses，并明确不是原生、未处理的 OEWN 数据库；图已经历定义筛选、替换/改写、WSD、OR 分支合并及其他构建策略。manifest 记载 107,136 个 `oewn` namespace head、3,000 个 external head、289 个 numbered-local head，包含 115,235 个完整来源 JSON 文件，且没有包含当前逻辑化 pipeline。该包的图 SHA-256 为 `c07dd37342ab399244a091501a21ada9e2f9f706efb1dc34d6b8ebc16a8a0a53`，semantic fingerprint 为 `6a26db5de732d90e7eb1ae700eec5c6f34e9c28fa83f35d2eb616c6abb8d4e41`。

对 `indexes/senses.jsonl` 的 source-record path 集合与 `sources/**/*.json` 文件清单作了只报聚合值的交叉核对：115,235 个唯一索引路径全部存在；磁盘上共有 115,237 个 JSON，额外的两份不是 source-record payload，而是 `basis85_law_complete_or_runtime_manifest_v1` 与 `definition_pos_uniqueness_writeback_manifest_v1` 构建记录，且均通过包内 checksum 核验。因此 manifest 的 115,235 source-record 计数与文件系统差异可解释，不应误报为缺失/未索引 gloss。检查没有输出 ID、文件名或定义文本。

按 `sources/Synset/` 六个处理目录只数 JSON 文件，分别为：`fully_parsed_glosstag_plausible_wsd` 84,393、`ready_for_lingua_glosstag_plausible_wsd` 21,664、`alternative_or_definition_wsd_frozen` 目录 5,627、`strict_proper_name_definition_wsd_frozen` 1,752、`standard_definition_wsd_external` 1,259、`nonstandard_definition_wsd_success_merged` 537；另有 `sources/recovered_history/` 5 个 JSON。Phase 23 全量索引审计在 alternative/definition 目录中只找到 5,625 个被索引的 source-record payload；目录比索引多出的 2 个 JSON 是构建辅助记录，不属于 115,235 个 source-record payload。因此目录文件数不可直接相加为来源记录数。以上是文件位置/处理阶段的聚合数，不是互斥 sense 计数、正确率或许可证类别；特别是“fully parsed/ready for Lingua”是流水线状态命名，不等于人工语义验收。

抽查 `oewn-00001740-a` 的来源 JSON 可见 `synset.raw_definition` 与 `definition.definition` 并不相同：有效释义移除了括号中的 usage 信息，同时从释义派生出 4 个 parts 并给出 OR 结构。这是来源加工记录，不应未经语言学复核就等同于原始 WordNet gloss 的逻辑真值条件。具体的版本 ID、license 字段和固定 upstream release 信息没有在该冻结包 manifest 中一并声明。

冻结包中的 `provenance/hypergraph_source_contract.json` 将该包标为 `opt_in_frozen_extension`，其 base inventory 为 109,603，并声明 18 类扩展/覆盖来源：既有 head 的额外 OR 分支、877 个 dependency heads、cycle-repair replacements、definition/POS replacement、多个按 basis 闭包约束的 rewrite 批次，以及最终 law/complete OR 扩展；另声明 21 项 strict-instance head exclusions 和 10 个 ID aliases。其余 source families 的策略并非统一追加：包括 union、replace-entire-head-clause-set、subsumption-minimize 等不同装载模式。该 contract 说明当前 110,425-head 图是一个多阶段冻结构建产物，不应被描述成对 11 万条原始 OEWN gloss 的一次性直接转换。contract 本身仍是构建规则/来源 lineage 元数据，不给每条文本补上游版本或许可证，也不证明其逻辑规则符合释义语义。

对上述 contract 文件本机计算的 SHA-256 为 `ca1690bb3c4a6687bf0e26922eee8ddab1b21e1a700b3bc1b697afd6fcc6d6c0`，并与冻结包 `checksums.jsonl` 一致。现在该文件也纳入项目 [bundle integrity lock](../config/frozen_bundle_integrity_lock.json)；重放前会与项目锁及 bundle checksum 双重核对。contract 中多批 rewrite 声明 `entity_anchors_are_external_denotational_constants`，因此不能假设所有 `external` namespace 都是可公开分发的词典义项文本；需在逐来源许可审查中把外部常量/义项身份与定义文本分开盘点。

## OEWN 上游许可与包级限制

2026-10-05 复核的 Open English WordNet 官方 [LICENSE.md](https://github.com/globalwordnet/english-wordnet/blob/main/LICENSE.md) 说明：OEWN 基于 Princeton WordNet（适用 WordNet License），并在 CC BY 4.0 下进一步开发；分享或改编须同时署名 Princeton WordNet 与 Open English WordNet 团队，底层 Princeton WordNet 数据仍受其原始条款约束。该许可说明**没有**确定本冻结包内外部 Wiktionary/其他来源、编号本地义项、人工/LLM 改写文本的许可，也没有仅凭当前包证明抽出的每条 `oewn-*` 文本对应哪个准确上游发布版。

2026-10-05 按官方 [2025-edition release](https://github.com/globalwordnet/english-wordnet/releases/tag/2025-edition) 复核两个 JSON URI：2025 Edition 为 `https://en-word.net/static/english-wordnet-2025-json.zip`，2025 Plus 为 `https://en-word.net/static/english-wordnet-2025-plus-json.zip`；release 页面说明 Plus 还含经筛选/人工验证的 Open English Namenet proper nouns。当前本机归档 SHA-256 分别为 `7d749f6e2c39e6970e4997839dcf6e42fd281f3c2fae0171d2192bae8cfa4b51` 和 `8832b8fa26a14c0ba8c99bb1ef8db6f9e122a6d9193b65ca9e0ef572580fee7e`。它们固定的是本机 OEWN 输入字节，不证明混合冻结包每条 gloss 的出处，也不等于公开分发已完成清权。对本机 2025 Plus JSON ZIP 检查到的 73 个成员中没有 license/readme-like 条目；如分发该包需另附准确许可/署名信息，并单独核验兼容性。

因此采取以下数据治理规则：

- 当前工作只在本地只读使用冻结包；不把完整 package 或 gloss 文本复制到可公开仓库。单独的 pilot blind batch 仅从官方 OEWN 2025 Plus 抽取已核对 raw gloss，并随包保留 CC BY 4.0 attribution 和发布版/哈希元数据。
- 试标抽样框只包含 `oewn-*` namespace、标准 POS `n/v/a/r`，排除 external 与 numbered-local 项。该候选框只写 sense ID、结构特征、释义哈希、来源包内相对路径和源文件哈希，不携带 gloss 原文。
- 当前抽样框实际 eligible 数为 104,907；它比 manifest 的 107,136 个 OEWN namespace heads 少的部分由非标准 POS 和标准 POS 下缺少定义文本的记录组成，精确排除数保存在抽样 manifest。
- 抽样框含结构字段与 diagnostic-panel 标记，是项目内部管理/复算文件，`annotator_visible=false`；不能直接给盲标者使用。`src/analysis/export_annotation_batch.py` 仅在 frame hash、2025 Plus release identity/archive hash、全体候选 ID 和 raw gloss exact-match 证据全部一致时，导出 `outputs/phase7/annotation_batch_2025_plus_blind.jsonl`。标注者文件只含 task ID、POS、lemmas 和原始 gloss；synset ID、图特征、抽样 panel/stratum、来源路径另存在受限答案键，不应给标注者。这个文件是待标任务输入，**不是标注结果或 gold set**。因 lemma/POS 与原文释义对界定标注目标有用，它们仍可见；此处的 blind 专指对系统输出、图结构和抽样类别设盲。
- 公开 benchmark 前，需将每条原始 gloss 与确定的 OEWN release 原文比对，记录 release/tag/文件 URI 和内容哈希；对转换文本、WSD 候选、例句和引入的外部资源逐条审许可证并保留署名。CC-BY 4.0 不可推定适用于这些其他素材。
- 若无法重建某条 gloss 的版本或许可，则将它排除在公开数据集之外；内部结构统计与外部发布数据集分别报告。当前 Plus 样本全数 raw-gloss 对齐，不表示有效释义的转换已被验证，也不替代发布前对改写文本和整个冻结包做逐项许可审查。

## 可复查入口

- 上游 bundle：`../OEWN/README.md`、`manifest.json`、`checksums.jsonl`、`indexes/senses.jsonl`。
- 候选抽样器：`src/analysis/annotation_sampling.py`。
- 生成物：`outputs/phase7/annotation_sampling_frame.jsonl` 与 `annotation_sampling_manifest.json`；候选框不含释义文本，不等于标注集，也不能用于估计系统精度。random panel 仍只按 POS、释义长度和标点分层，刻意排除图结构特征；diagnostic panel 互斥覆盖多 OR、宽 AND（最大子句宽度 P90+）及深 selected witness（P90+，排除前两类），明确不得用于总体性能估计。候选框保留 selected-witness depth/width 与证据复用度供后续分层分析，但不暴露给标注者。抽样定义和特征边界见[标注协议](annotation_protocol.md)。
- 来源结构复核器：`src/analysis/annotation_source_audit.py`；它对抽样框引用的 source JSON 核验 SHA-256，并只输出 `definition.logic.op`、分解 part 数、原始/有效 gloss 是否变化、source root/pipeline 等聚合计数，不输出释义或公式文本。结果写入 `outputs/phase7/source_structure_audit.json`；字段计数相等不构成语义对齐证明。
- 全量索引结构审计：`src/analysis/full_source_index_audit.py` 只读取冻结包的 `manifest.json` 与 `indexes/senses.jsonl`，不打开约 18.9 GB 的 source JSON payload；完整扫描 110,425 个 sense、115,235 条索引来源记录，并输出不含 ID、释义、lemma 或路径的聚合结果 `outputs/phase8/full_source_index_audit.json`。输入图 SHA-256、semantic fingerprint 与 sense index SHA-256 记录在报告中。结果与 manifest 的 sense/source-record 计数相符，索引 identity 唯一且无畸形记录。审计 v2 还在索引内全量核对 `active_clause_sources` 与同 sense 的来源记录路径：154,206 个 graph clause 均至少有一个 source lineage；154,356 个 source-record/clause link 均唯一且能在该 sense 的 source-record metadata 中找到；无重复 link、缺失来源或畸形 active 映射。112,609 条来源记录至少关联一个活跃 clause。
- 全量索引显示 115,235/115,235 条来源记录都有整数 `parts` 元数据；其中 82,524 条（71.61%）的 parts 数与所属 sense 的图 clause 数相同，3,360 条更少、29,351 条更多。限定在 112,609 条有活跃 clause lineage 的 source records 后，83,241 条的 parts 数与其被归属 clause 数相同，68 条更少、29,300 条更多。前一组比较的是 source record 对所属 sense 的全部 OR clause 数，后一组比较的是它实际被索引为来源的 clause 数；两组都只是计数，不是内容对应正确率。所有 graph clause 有 source lineage，只能说明索引没有无来源 clause，不能说明某条定义 part 支持了对应 literal。

所有 110,425 个 sense 的每条来源记录都有 parts 计数。3,995 条来源记录的 raw 与 effective definition 字符串不同。source status 有 89,969 条为 `success`，其余 25,266 条因状态值不在安全白名单内统一归为 other/missing；不导出未知状态原文。上述结构统计均不证明释义忠实度、蕴含正确性或 Horn 规则有效性。全量 `senses.jsonl` 索引中的 `parts` 字段只有整数计数，没有 part ID、文本或可复原的 AND/OR 树，故不能靠索引完成逐 part 对齐；Phase 15 已读取全部活跃 source payload 并完成 part/WSD/graph literal 的结构集合普查，但仍未有人审 source span 支持或语义映射。对已有 291 条内部任务运行的精确子串定位仅输出 ID/偏移候选，并不补足语义证据。下一步仍需在许可清晰的样本上人工标注并裁决该证据。
- 唯一 canonical replay 不一致已被[单例差异审计](frozen_bundle_replay_exception.md)显式记录；机器输出 `outputs/phase8/frozen_bundle_replay_exceptions.json` 交叉检查 manifest、上游 replay 报告、索引、图规则和 witness。冻结包自身选择保留 archived authoritative graph clause，不自动并入来源重放中的另一分支。该差异不被本项目静默修复，也不构成 gloss 语义结论。
- 全量索引审计复跑（在项目目录执行）：`python -m src.analysis.full_source_index_audit`；需要覆盖既有报告时明确加 `--force`。输入冻结包只读，报告输出路径限制在项目目录内。测试：`python -m unittest tests.test_full_source_index_audit -v`。
- 活跃来源 clause/part 追踪：`src/analysis/source_clause_alignment_audit.py` 从既有 200-sense frame 出发，逐个核验来源 JSON SHA-256，只比较 `indexes/senses.jsonl` 中标记为活跃来源的 clause，不把未参与冻结图的候选来源混入对齐结果。报告为 `outputs/phase8/source_clause_alignment_audit.json`，不输出文本、ID 或路径；它区分 source `logic` 的分支数、按来源归属的图 clause 数、part ID 与 logic 叶子集合，以及 part WSD sense-ID 集合与归属 clause 的集合重合。该检查是内部 200-sense frame 的结构诊断，160 条分层随机项和 40 条诊断项仍须分开解读，不代表全量性能或语义正确率。
- 当前 frame 的 207 条来源文件均通过 frame 哈希校验；其中 201 条在索引中标记为图的活跃来源，6 条未活跃。201 条活跃来源的 logic 树均能解析，part ID 与逻辑叶子 ID 集合一致；188/201 条的逻辑 DNF 分支数与该来源实际关联的 clause 数相等，13 条不等，值得作为版本/投影差异案例复核。按 part WSD 结果合并 sense-ID 集合后，仅 7/201 条来源的分支集合多重集与归属 graph clause 完全一致；299 个来源-clause 归属对中，289 个 clause 的 ID 集合是至少一个合取分支 WSD ID 并集的子集，而仅 9 个精确相等。后两项不是语义质量分数：WSD union 可能包含非逻辑贡献词，图 literals 也可能经历筛选/归一化；精确重合与否都不能裁决释义蕴含。它们恰好说明“分支数匹配”远弱于 clause 内容映射，需要人工逐项判断映射关系与缺失/多余文字来源。
- 复跑：`python -m src.analysis.source_clause_alignment_audit`；需覆盖既有报告时加 `--force`。审计限定为最多 1,000 个 sense、16 MiB/来源文件，校验冻结图哈希、每条抽样来源文件哈希，并限制报告只能写入项目目录。测试：`python -m unittest tests.test_source_clause_alignment_audit -v`。
- 内部人工映射任务导出：`src/analysis/export_source_clause_mapping_tasks.py` 将已核验的 2025 Plus raw gloss、effective definition、parts/logic 与图 literal 展示文本组合成一条 source×active-clause 任务；根据 sense index 精确匹配来源路径，仅保留 raw gloss 与官方发布版一致的 active source，且固定种子打乱任务顺序。当前从 200 个 sense 候选生成 291 条任务；207 个候选来源文件通过哈希核验，其中 201 条为 active 来源、6 条未 active；另有 6 条 active source 的 raw gloss 与官方版不一致而排除（涉及 8 个 source-clause 任务）。任务文件 `outputs/phase8/source_clause_mapping_tasks.jsonl` 仅供本地内部 error analysis，含 gloss 与冻结包派生定义，**不得对外分发**；`source_clause_mapping_answer_key.json` 含 sense ID 和相对源路径，受 `.gitignore` 保护，不得交给标注者。汇总 manifest 记录输入哈希与许可待审状态。
- 任务导出复跑：`python -m src.analysis.export_source_clause_mapping_tasks`；覆盖时加 `--force`。导出后、分发前只做结构核验：`python -m src.logic.source_clause_alignment_validator outputs/phase8/source_clause_mapping_tasks.jsonl`。收到单个标注者完整返回后，在任务文件后加其 JSONL 回传路径；validator 会检查任务完整性和 span/ID 结构。标注映射层不是 entailment 标注，也不是 gold data；另需人工语义核验，且在逐来源许可审查完成前任务只限本地使用。
- 另将候选逐条与官方 OEWN JSON 发布版比对，脚本见 `src/analysis/oewn_release_crosscheck.py`。报告不复制释义，但含 sense ID 与 source-payload 哈希，因此只供本机审计并由 `.gitignore` 排除。v2 对 source JSON 中的 `synset.raw_definition`（raw gloss）和 `definition.definition`（有效/加工 gloss）分别比较，并在每个 source payload 粒度保留哈希、长度、字段有无/空值、精确/规范化匹配状态和 raw/effective 相等标志；这能定位差异到文件而不输出原文。官方 2025 Edition 的压缩包 SHA-256 为 `7d749f6e2c39e6970e4997839dcf6e42fd281f3c2fae0171d2192bae8cfa4b51`：旧 `/1` 的 200 个候选中 197 个 ID 存在、197 条 raw gloss 精确匹配、190 条 effective gloss 精确匹配。官方 2025 Plus 压缩包 SHA-256 为 `8832b8fa26a14c0ba8c99bb1ef8db6f9e122a6d9193b65ca9e0ef572580fee7e`：新版 `/2` 的 200/200 个 ID 存在且 raw gloss 精确匹配，effective gloss 精确匹配 193/200。三个仅在 Plus 中匹配的条目均来自 `strict_proper_name_definition_wsd_frozen`。新版 `/2` 的 208 份 source payload 中有 7 份 raw/effective 字符串不等，恰对应 7 个 effective 不匹配 sense；其中 6 条 source record 是 raw 匹配而非空 effective 不匹配，另 1 条是 raw 匹配但 effective 为空。它们是版本/预处理差异，不足以判定语义错误，须进入 lineage 与人工忠实度审查。这仅证明 200 条样本 raw gloss 对齐 2025 Plus，不证明全量 107,136 个 OEWN namespace 都来自该版或未作后续修改。
- match-only 报告分别包括旧 `/1` 文件 `outputs/phase7/oewn_2025_release_crosscheck.json`、`oewn_2025_plus_release_crosscheck.json` 和新版 `/2` 文件 `oewn_2025_plus_release_crosscheck_v2.json`。项目 `tmp/` 当前缓存的 OEWN ZIP 与展开数据是多个本地复算流程（包括 Phase 16 和 Phase 7 `/2`）的固定输入，不是纯临时输出；可按该目录 README 与许可文档复用，清理前必须先确认下游使用。报告固定保留当次 archive SHA-256、frame SHA-256 和发布版身份。
- 标注包复跑：先确保 2025 Plus 归档哈希为 `8832b8fa26a14c0ba8c99bb1ef8db6f9e122a6d9193b65ca9e0ef572580fee7e`，再运行 `python -m src.analysis.export_annotation_batch`；覆盖旧结果需加 `--force`。对应测试为 `tests/test_export_annotation_batch.py`。答案键 `outputs/phase7/annotation_batch_2025_plus_answer_key.json` 含 sense 映射与来源路径，只可由数据管理员保管；manifest 内有盲标文件和答案键 SHA-256、归属/版权声明、CC BY 4.0 与官方许可文本链接，以及“抽取、乱序、加 task ID，释义原文不改”的修改说明。
- 对这 200 个唯一候选 sense 的 207 份来源 JSON 做了结构抽查：顶层 `definition.logic.op` 为 AND 52、ATOM 83、OR 72；207 份记录都有 parts，140 份 parts 数恰与图 clause 数相等，另有 7 份 raw/effective gloss 字符串不同。这里的 207 是来源记录数而非独立 sense 数；数量相等只表示结构计数吻合，不验证 clause 与 parts 的意义对应、方向或源 gloss 忠实度。抽样框内的 source root/pipeline 也混杂，不能把总体结果概括成单一流水线表现。
- 复跑：`python src/analysis/annotation_sampling.py`。默认 160 条按 POS × gloss 长度 × 标点分层的抽样，加 40 条基于 OR 候选/子句宽度的诊断样本；诊断样本不得并入总体性能估计。

## 全量活跃来源 payload 补充审计（Phase 15）

Phase 8 的 source-index census 只读索引元数据，不打开约 18.9 GB 的 payload。Phase 15 之后，这个范围已扩展到所有被 `active_clause_sources` 引用的来源 JSON：112,609/112,609 个活跃 payload 均成功解析，逐文件大小和 SHA-256 与 `checksums.jsonl` 一致，合计 18,134,793,487 字节；报告另记录 `checksums.jsonl`、sense index、图规则哈希和按索引顺序形成的 payload digest。文件、释义、sense identity、WSD ID 和 source path 均不写入报告。

所有活跃来源的逻辑树都可解析，112,597/112,609 个逻辑叶子 ID 集合与 part ID 集合一致；108,727/112,609 条来源记录的逻辑分支数与被归属的 graph clause 数相同。对齐到内容集合后，仅 3,123/112,609 个来源记录的完整 WSD 分支 ID 多重集与对应图 clause literal ID 多重集一致。逐 clause 看，154,356 个归属对中 150,599 个图 literal 集合是某个完整 WSD 分支并集的子集，4,887 个与至少一个分支并集完全相同。后三组是结构集合统计，不能代替 sense、span、方向或蕴含的人审；特别是 WSD union 可能包含非逻辑贡献词，图也可能对 literal 做筛选和归一化。完整分母、哈希及限制作见[Phase 15 报告](full_source_payload_census.md)，复跑命令为 `python -m src.analysis.full_source_payload_census`。


## 全量来源记录的版本与许可字段覆盖（Phase 23）

2026-10-05，`src/analysis/audit_source_release_metadata.py` 对冻结 sense index 引用的 115,235 个唯一 source-record payload 作完整只读复核。110,425 条 sense 索引记录中没有畸形来源记录或重复 payload 路径；全部 payload 成功解析，且 18,734,636,389 字节的文件内容逐个匹配冻结 `checksums.jsonl`。审计同时验证 bundle integrity lock v2，并将索引、checksum 清单与按顺序构成的 payload 摘要写入本机忽略报告。

来源目录家族由 fully-parsed glosstag 84,393、ready-for-lingua 21,664、alternative/definition-WSD 5,625、strict proper-name 1,752、standard external 1,259、nonstandard merged 537 和 recovered history 5 条构成。payload 字段名扫描在 0/115,235 个文件中发现显式 license/copyright/attribution/rights 类键；来源/版本/哈希等 provenance 字段至少命中每一个 payload。直接位于 `source_record` 的 `target_source_inventory`/`target_source_kind` 字段分别出现于 3,125/2,488 条记录；嵌套 evidence 中的 `source_version`/`download_url` 字段覆盖分别为 3,118/254 个 payload。后者的字段覆盖只说明包内存在来源线索，不证明这些线索足以唯一确定上游发行版或适用条款，也不证明任何数据可再分发。许可状态仍为未评估，需逐来源把 origin、版本、许可及署名与上游证据对应并审查兼容性。机器报告路径 `outputs/phase23/source_release_metadata_audit.json` 被 `.gitignore` 排除，不输出释义、身份或来源路径。

### `target_source_*` 标签的来源追踪含义

对机器报告中两个受限枚举作了分布核对。`source_record.target_source_inventory` 有 3,125 次字段记录、25 个标签；`source_record.target_source_kind` 有 2,488 次字段记录、5 个标签。前者同时混有外部资源名、冻结基线名和内部 basis/rewrite 批次名，因此不能直接当作 25 个上游数据集或许可类别。后者描述构建/替换路径，也不是来源授权状态。

| `target_source_inventory` 标签 | 记录数 |
|---|---:|
| `oewn_plus_noninstance` | 753 |
| `kaikki_selected_gloss` | 427 |
| `basis_963_D_rewrite_union_389` | 389 |
| `basis_1209_all_clauses_require_self_278` | 281 |
| `oewn_2025_plus` | 243 |
| `manual_external_supplement` | 221 |
| `basis613_D_low_impact_review` | 153 |
| `kaikki_full` | 141 |
| `Synset_frozen_110425` | 109 |
| `suspicious_94_from_basis_723` | 94 |
| 其余 15 个标签合计 | 314 |

| `target_source_kind` 标签 | 记录数 |
|---|---:|
| `strict_wsd_external_concept` | 1,180 |
| `existing_frozen_head_alternative_definition` | 703 |
| `recursive_distance_oewn_plus_dependency` | 243 |
| `manual_semantic_gap_dependency` | 221 |
| `recursive_distance_dependency` | 141 |

上述为字段值出现次数，不是相互独立的来源数、sense 数或许可清单；同一上游材料可能被多个构建批次引用，标签本身也未被上游 release 文件逐项核实。它们适合用来确定人工 provenance crosswalk 的核查顺序：先逐一厘清明确标为 OEWN、Kaikki 和 manual external 的上游证据，再沿 basis/rewrite 标签回溯构建记录与其父来源。任何分组仍须绑定实际上游版本、许可、署名及必要修改说明；在核实之前，所有分组的发布状态仍为未评估。

## 替代释义来源证据候选清单（Phase 24）

为从字段存在计数推进到可追踪的来源簇，新增 `src/analysis/audit_source_release_candidates.py`。该脚本限定扫描 `alternative_or_definition_wsd_frozen` 家族，通过 sense index 找到来源载荷，逐份对照冻结 checksum，并只读取 `source_record.alternative_definition_provenance.source_evidence` 中的来源标签、版本、ontology、证据类型和下载 URL 主机名。报告不保留释义、义项身份、外部 ID、source path、完整 URL 或其他原始证据文本；报告 JSON 位于被 `.gitignore` 排除的 `outputs/phase24/source_release_candidate_triage.json`。

复算命令：

```powershell
python -m src.analysis.audit_source_release_candidates
```

报告将 bundle integrity lock、sense index、checksum sidecar 和所选 payload 序列摘要绑定起来，并列出来源证据 profile 的载荷计数。它是有限来源家族的候选 crosswalk，不覆盖另外的 source family，也不验证来源标签是否真实、下载 URI 是否仍可用、上游版本/许可/署名是否匹配或多个证据能否唯一确定 release；它不授予任何发布 clearance。修改报告需显式加 `--force`。

2026-10-06 首次复算结果：目标家族在 sense index 中有 5,625 个引用，5,625/5,625 个唯一 payload（1,401,596,052 bytes）均通过 checksum 与 bundle integrity lock 核验；其中 3,444 份含非空 `source_evidence`，合计 3,645 个 evidence objects，归并为 90 个受限字段 profile。字段值计数显示 GCIDE 0.54 为 1,580 个 evidence objects、MeSH 2026 descriptors 为 356 个、EMBL-EBI OLS 为 275 个；另有 Wikidata、Uberon、ENVO、OBI 等来源。254 份载荷含下载 URL，报告只留主机名聚合（主要为 `dumps.wikimedia.org` 80、`api.gbif.org` 73、`ftp.gnu.org` 26），不留完整 URL。1,202 个 evidence objects 的来源标签因不符合安全标签格式而归入 `noncanonical_or_nonscalar`，需在本地受限环境逐项追溯；1,082 个版本字段中的内容哈希归并成 `content_hash_value`，没有在候选 profile 中输出哈希值。

这是重要的范围发现：这个替代释义子集包含多种词典/生物医学/本体来源，因此仅核对 OEWN 与 Kaikki 不足以完成权利审查。上述所有数字都是载荷或 evidence-object 计数，不代表独立上游作品数；字段/版本/域名都不能单独确定许可证或再分发权。结合 Phase 23 的全量字段普查（0/115,235 payload 出现显式许可类键），下一项 provenance 工作应优先核对 GCIDE、MeSH、EMBL-EBI OLS 等来源及被归并标签，再按具体上游 release、记录范围与署名条件逐项建表；目前仍没有来源级发布 clearance。

## 高频来源的官方条款定向复核（Phase 25）

2026-10-06 针对 Phase 24 的高频标签查询了来源方/注册方官方页面，并将 URL、支持的事实、适用边界和未决项记入 [`source_release_rights_evidence_2026-10-06.json`](../sources/source_release_rights_evidence_2026-10-06.json)。这是一份 source-level evidence log，不是法律意见；“官方页面写了什么”和“冻结记录确实来自该版本且可按该条款再分发”是两个不同判断。

- **GCIDE 0.54（1,580 个 evidence objects）**：GNU 官方归档列出 2024-12-31 的 `gcide-0.54`，项目许可页面写明 GPL version 3 or later。当前尚未将冻结 payload 的内容哈希与该 release 的原始文件及其随附许可逐项核对，也未判断冻结加工/派生内容的发布义务；所以状态是“找到上游声明，冻结版本与载荷映射未核实”。[GNU GCIDE archive](https://ftp.gnu.org/gnu/gcide/) · [GNU GCIDE license](https://gcide.gnu.org.ua/license)
- **MeSH 2026（356 个 evidence objects）**：NLM 官方页面按 production year 提供 MeSH，并列有 2026 DTD；NLM 下载条款要求明确署名 NLM，并要求再发布者保持最新版本，或显著说明内容已非最新。条款页自标最后审阅于 2019 年，现仍由 2026 年复核过的下载页链接；它没有给出这里可直接填入的标准 SPDX/Creative Commons 标识，不能把“免费提供”改写成 CC0 或其他许可证。[NLM MeSH downloads](https://www.nlm.nih.gov/databases/download/mesh.html) · [NLM data terms](https://www.nlm.nih.gov/databases/download/terms_and_conditions.html)
- **EMBL-EBI OLS（275 个 evidence objects）**：OLS 是聚合服务，不是统一许可证；官方页面建议优先使用各 ontology 的上游 OWL/API，而非其内部格式 dump。当前 provenance evidence 将 275 个记录归到 MeSH、NCIt、ChEBI、FoodOn、DOID 五类，需按各自版本逐项确认。对照页面中，ChEBI 标为 CC BY 4.0，FoodOn 的 OBO Foundry 条目标为 CC BY 4.0，Disease Ontology 条目标为 CC0 1.0；这些仍不能证明冻结条目就是页面所示 release。[OLS downloads](https://www.ebi.ac.uk/ols4/downloads) · [ChEBI licensing](https://www.ebi.ac.uk/chebi/about) · [FoodOn registry](https://obofoundry.org/ontology/foodon.html) · [Disease Ontology registry](https://obofoundry.org/ontology/doid)
- **OLS 的 MeSH 与 NLM MeSH 要分开处理**：当前 OLS MeSH 条目显示 version 2025 和 CC0-1.0，而本冻结来源簇标为 MeSH 2026，NLM 自己的下载条款另有署名/时效要求。它们提示了表示与版本边界，不能据 OLS 元数据覆盖 NLM 条款，也不能将两者视作同一 release。[OLS MeSH entry](https://www.ebi.ac.uk/ols4/ontologies/mesh?tab=classes)
- **NCIt 的具体许可仍未确认**：NCI 一般信息重用政策表示未另行标记的 NCI 文本可重用并要求署名，但这不足以识别这里的 NCIt serialization、发行版和 source-specific license。[NCI reuse policy](https://www.cancer.gov/policies/copyright-reuse)
- **Wikidata（59 个 evidence objects）**：Wikidata 官方页面将 main、Property、Lexeme 和 EntitySchema 等结构化数据列为 CC0；其他 namespace 的文本为 CC BY-SA 4.0。仍须确认冻结提取来自哪个 namespace、哪个 dump snapshot，不能只凭 `Wikidata` 标签套用 CC0。[Wikidata licensing](https://www.wikidata.org/wiki/Wikidata:Licensing) · [Wikidata database downloads](https://www.wikidata.org/wiki/Wikidata:Database_download)
- **较小本体/词典来源簇**：候选报告还识别 Uberon 41、ENVO 18、OBI 17、PATO 7、NCBI Taxonomy 6 和 English Wiktionary 14 个 evidence objects。OBO 注册页分别列出 Uberon CC BY 3.0、ENVO CC0 1.0、OBI CC BY 4.0、PATO CC BY 3.0、NCBITaxon CC0 1.0；冻结 metadata 只给 Uberon/ENVO/OBI/PATO 本地 snapshot 标签，没有可与发行版绑定的日期。OBO Foundry 要求按各 ontology 的版本 IRI 与本体自身 license 元数据做逐版本核验，因此这些注册页仅是候选证据。[Uberon](https://obofoundry.org/ontology/uberon.html) · [ENVO](https://obofoundry.org/ontology/envo.html) · [OBI](https://obofoundry.org/ontology/obi.html) · [PATO](https://obofoundry.org/ontology/pato.html) · [OBO version/citation policy](https://obofoundry.org/citation/Citation.html)
- **NCBI Taxonomy 需要先分清数据库与 OBO 翻译**：注册页说明 NCBITaxon 是 NCBI Taxonomy 的 OBO/OWL 自动翻译并列 CC0 1.0；其 2026-07-18 Dashboard 的 taxslim 报告却提示 ontology 文件缺许可、version IRI 无法解析。冻结标签还未确定指数据库本体还是 OBO/OWL 翻译，更没有版本绑定，不能直接认定 CC0 适用于冻结载荷。[NCBITaxon registry](https://obofoundry.org/ontology/ncbitaxon.html) · [NCBITaxon Dashboard report](https://dashboard.obofoundry.org/dashboard/ncbitaxon/dashboard.html)
- **English Wiktionary（14 个 evidence objects）**：其版权页说明原创词条文本采用 CC BY-SA 4.0 与 GFDL 双许可，并提醒某些页面可能含第三方材料或额外声明。冻结来源记录没有具体页面历史/条款映射，不能仅凭项目级许可推断所有释义来源与署名要求。[Wiktionary copyrights](https://en.wiktionary.org/wiki/Wiktionary:Copyrights)

## Phase 50：画像标签到权利日志的保守 crosswalk

Phase 23 的 payload 字段审计与 Phase 48 的索引字段审计作用范围不同：前者扫描 115,235 个 payload 的来源/版本字段名，后者只检查索引本身的字段。因此“索引没有版本字段”不能改写为“payload 没有版本线索”；反过来，payload 出现 `source_version` 也不代表具体版本已和上游发布字节绑定。

`python -m src.analysis.reconcile_source_rights_coverage` 对 Phase 24 的来源画像聚合与权利证据日志按**完全相等的 source label** 对账，不读取 source payload。90 个 profile 组合含 58 个来源标签；与 11 条权利日志标签精确 join 得到 17 个 profile 组合、2,326 个 profile payload 计数。其余 73 个组合（48 个来源标签）及 1,269 个对应 payload 计数没有精确标签命中，包含 22 个 `noncanonical_or_nonscalar` profile（1,199 个 payload 计数）。此计数只反映字面标签可定位程度；别名、历史标签和聚合来源尚未规范化，不能从“未精确匹配”推出“没有条款证据”或“不可发布”。完整输入 SHA、source 标签与状态、限制见[机器交叉表](../outputs/phase50/source_rights_crosswalk_audit.json)及Phase 50 报告。

此 crosswalk 不修改 Phase 23 的全量字段结论，不重算 Phase 24 来源画像，也不将匹配项视为已清权。下一步应人工确认未命中别名，再为每个 canonical source 绑定精确上游发行版/serialization 与文件哈希，逐项评估许可、署名和适用输出。项目 `release_clearance=not_assessed`、`not_cleared_for_public_release` 均保持不变。

## Phase 51：官方证据支持的资源家族补录

针对三个可直接识别的画像标签，将官方来源页面复核结果写回权利证据日志，并重新计算 Phase 51 crosswalk。OEWN 画像记录的 `source_version=2025+` 与官方 release 页公布的 2025+ edition 名称相符；官方 license 页列出 OEWN/Princeton WordNet attribution 与底层条款边界。[OEWN release](https://github.com/globalwordnet/english-wordnet/releases/tag/2025-edition) · [OEWN license](https://github.com/globalwordnet/english-wordnet/blob/main/LICENSE.md)。English Wiktionary 标签/host 可定位到该项目的官方版权说明，但无 entry revision/hash，且页面可能含第三方材料。[Wiktionary copyrights](https://en.wiktionary.org/wiki/Wiktionary:Copyrights)。ChEBI 标签和 EMBL-EBI host 可定位到 ChEBI 官方 about/license 页面；该页说明 CC BY 4.0 与 EMBL-EBI 条款，但画像缺版本/ontology，具体 item/source chain 未绑定。[ChEBI about/licensing](https://www.ebi.ac.uk/chebi/about)。

将这三行加入来源权利证据后，精确同名 crosswalk 从 17/90 profile 组合、2,326/3,595 profile payload 计数升为 20/90、2,334/3,595；未精确命中从 73 组合/1,269 计数变为 70/1,261。它只表示日志按标签可定位性变化，不能称为“清权覆盖率”。画像计数不是独立 sense 数；所有新增记录都保留 payload→release/hash 和归属链未核实状态。结果及差异见Phase 51 报告和[机器 crosswalk](../outputs/phase51/source_rights_crosswalk_audit.json)。

## Phase 52：GO 与 IUPAC Gold Book 的本地版本线索

两个候选画像有可辨认的本地版本字段：`local_go-basic.obo_snapshot`（5 个 profile payload 计数）与 `v5_local_snapshot`（4 个计数）。GO 官方下载页列出 go-basic 的 OBO 格式；GO 的引用与许可指导要求保留 dated release/version 并声明 CC BY 4.0。IUPAC Gold Book 官方 about 页标示 5.0.0；官方 term metadata 页面说明每个 term 可带版本/许可数据，individual term 页面列出 CC BY-SA 4.0，并与 collection-level licensing 联系方式区分。[GO 下载](https://geneontology.org/docs/download-ontology/) · [GO 引用/许可](https://geneontology.org/docs/go-citation-policy/) · [GO 归档示例](https://release.geneontology.org/2026-01-23/ontology/index.html) · [IUPAC Gold Book about](https://goldbook.iupac.org/pages/about) · [IUPAC 官方 term metadata 示例](https://mail.goldbook.iupac.org/terms/view/S06210/plain)。

本地字段并无精确 GO 日期版号或 IUPAC term ID/revision/hash。因而这些页面用于说明资源家族和应保留的 release/term 线索，不能证明具体 payload 正是页面所述 release/item，也不能判断实际再发布适用范围。按两个 source label 补录后，精确 crosswalk 变为 22/90 profile 组合、2,343/3,595 profile payload 计数；68 组合/1,252 计数仍未精确匹配。此为日志定位数，不是发布许可覆盖。详见Phase 52 报告和[机器 crosswalk](../outputs/phase52/source_rights_crosswalk_audit.json)。

## Phase 54：非规范来源字符串的结构审计

为评估最大的 `noncanonical_or_nonscalar` 画像簇，扩展 `src/analysis/audit_source_release_candidates.py`，新增 source metadata value-shape 分类和受控 URL-host 提取。对 `alternative_or_definition_wsd_frozen` 的 5,625 个 payload 重跑并校验 checksums：3,645 个 evidence objects 中，2,443 个 `source` 值是 canonical label string，1,202 个是非规范字符串，跨 1,199 个画像 payload 计数；没有 object/array 类 `source` 值。扫描没有从任何 source 字符串中恢复安全 HTTP(S)/FTP host。非规范 source 类别中的 2 个 profile（1,079 payload 计数）还伴随 hash-shaped `source_version`、无单独 `download_url`，所以哈希不补足 provider/release identity。[Phase 54 机器报告](../outputs/phase54/source_release_candidate_triage_host_recovered.json)与阶段报告。

这一结果只适用于该 5,625-record 来源家族，也只证明分类/host 抽取没有恢复来源身份；由于不读取原始字符串，不能判定其内部是否含可恢复的 source label。故这一簇保持 `unresolved_provenance`，不能自动当作一个 provider 或适用某个 license。机器输出仅含类别计数/host 类别与哈希；原始 payload 仍未进入发布审计产物。

此次复核支持的结论是：已找到若干来源方的现行/对应版本条款页面，足以把核查对象从宽泛标签缩到具体资源及待验证问题；但没有任何条目因此自动获准公开。尤其是 OLS/本体来源须逐 ontology 和 snapshot 做版本绑定，GCIDE/MeSH 须将本地证据连接到官方 release，`noncanonical_or_nonscalar` 分组还待在本地受限材料中解析。结构化来源证据日志覆盖以上定向复核，但不是完整来源许可清单：[source_release_rights_evidence_2026-10-06.json](../sources/source_release_rights_evidence_2026-10-06.json)。完整项目与冻结包的发布状态保持未清权。

### 2026-10-07 Phase 43：GCIDE / MeSH official-page follow-up

官方页复核补充到结构化日志的 `followup_review_2026_10_07` 字段：[GCIDE 0.54](https://ftp.gnu.org/gnu/gcide/) 目录列出 2024-12-31 的 tar.gz/tar.xz/zip 和 detached signature 文件，项目 license 页声明 GPL-3.0-or-later；本轮没有下载 archive 或验签。[NLM MeSH 下载页](https://www.nlm.nih.gov/databases/download/mesh.html) 当前列出 2026/2027 production-year DTD，并说明 descriptor/qualifier XML 年更、SCR/RDF 工作日更新；其[复用条款](https://www.nlm.nih.gov/databases/download/terms_and_conditions.html)要求显著署名及再发布时保持最新或明确披露非最新。条款页没有为该数据标注 SPDX/CC 标识。本补充仍没有将冻结 evidence 对象绑定到确切 archive bytes、格式或具体 redistribution；`release_clearance` 和两项 source `license_status` 均未升级。详见Phase 43 报告。

### 2026-10-07 Phase 44：NCIt 条款与 OLS 记录映射

NCI 专用 [NCIt 条款页](https://evs.nci.nih.gov/ftp1/NCI_Thesaurus/ThesaurusTermsofUse.htm)声明 CC BY 4.0，并说明 “NCI Thesaurus” 是商标；[下载页](https://evs.nci.nih.gov/thesaurus-downloads)列出 OWL 主格式和 26.09d（2026-09-28）版本。来源日志现记录这些提供方事实。OLS 子项仍有 78 个 evidence objects（Phase 24 候选 profile 中 56 个缓存 payload），尚未绑定具体 NCIt release、格式、字节或归属，因此不能据此清理 OLS 整体或项目发布状态。`release_clearance=not_assessed` 不变。详见Phase 44 报告和[结构化来源证据](../sources/source_release_rights_evidence_2026-10-06.json)。

### 2026-10-07 Phase 48：source-record 索引字段覆盖

对冻结包 `indexes/source_records.jsonl` 的 115,235 行作了字段集合聚合，没有输出记录值。所有行使用相同字段集合；其中没有 provider、上游 release/version、serialization、artifact hash 或 license/attribution 字段。因此该索引本身不足以把 OLS/NCIt payload 绑定至具体发布。这个结论仅限索引层，不能推断被索引 payload 没有其他来源元数据；`release_clearance=not_assessed` 仍不变。详见Phase 48 报告。

### 2026-10-07 Phase 88：OEWN 2025+ 六条候选记录级归档匹配

在 Phase 51/87 的官方资源标签核对基础上，新增 `src/analysis/audit_oewn_2025_plus_payload_matches.py`。审计验证固定 ZIP SHA-256 与 inventory 一致、冻结来源 payload 与其 checksum sidecar 一致，并将六条候选 evidence 的 `(ILI, definition_text_sha256)` 联合键与本机 2025+ JSON 归档逐记录比较：6/6 唯一命中。聚合结果见[Phase 88 机器报告](../outputs/phase88/oewn_2025_plus_payload_release_match.json)，解释见阶段报告。官方 release 页区分 2025 与 2025+，并链接 JSON ZIP；官方 license 页面说明 OEWN 与 Princeton WordNet 的归属/底层条款边界。[release](https://github.com/globalwordnet/english-wordnet/releases/tag/2025-edition) · [license](https://github.com/globalwordnet/english-wordnet/blob/main/LICENSE.md)。

该联合字段命中把这六条来源证据记录绑定到固定归档的一条记录，但未追踪其进入哪些冻结图子句/规则，也未清查混合 bundle 的其余来源。项目和 OEWN-derived data 的 `release_clearance` 仍为 `not_assessed`，没有据此授权任何再分发。

### 2026-10-07 Phase 89：候选来源记录到图对象的结构 lineage

继续以不输出文本/标识/路径的方式，将六条来源 payload 经 `sense_id`/`synset_id` 与 sense index identity、hypergraph head 连接：6/6 唯一引用；六个 head 的 11/11 rule clauses 与 hyperedges 相符；六个 selected witness clauses 均匹配各自 rule 与 hyperedge。任意 active source-document 列表中有 4/6 条出现候选 payload path，但细化到 selected witness clause 后，只有 2/6 selected document 同时包含候选 payload、相同 OEWN ILI/释义散列，并含有散列与候选定义一致的字符串字段；另外两条只出现在非 witness 子句，另两条未见于 active clause documents。深度报告与可复算[机器输出](../outputs/phase89/oewn_2025_plus_graph_lineage.json)区分了这些层次。

该结果是 provenance/结构关联，不是 WordNet 释义语义支持规则的证明，也不证明候选记录是生成这些规则时唯一采用的文本。许可兼容和项目发布状态未改变。

## 人工标注 source-record 绑定预检（Phase 26）

`src/logic/source_record_verifier.py` 针对未来返回的 canonical annotation JSONL 提供只读预检。它把标注中的相对 source path 与冻结包 sense index 的义项映射、标注所附 SHA-256、冻结 checksum sidecar 和实际 payload 字节交叉核对，并检查 gloss 字符串能否在同一 payload 的 raw/effective definition 字段中精确找到。它只输出摘要哈希、聚合计数与失败类别，不输出 gloss、义项身份或文件路径。

```powershell
python -m src.logic.source_record_verifier path\to\annotations.jsonl
```

该 verifier 已接入组合路由：调用 `route_pipeline_result` 或 `route_pipeline_result_from_export` 时传入 `source_bundle_root` 或预先初始化的 `AnnotationSourceBundleVerifier`，路由会针对证明实际引用的标注记录执行同一组字节、索引和释义字段检查；缺少两者或核验失败时 source semantics gate 保持关闭。批量路由可复用 verifier 实例，避免重复扫描大索引；源 payload 每次仍按实际引用重新核对哈希。独立 CLI 仍可用于导入前预检并归档结果。该工具不是标注结果、上游发行版 crosswalk、许可结论或语义 gold。当前 lock 仍记录未签署协议、未授权任务外发，也尚无 annotation return 文件，因此暂无真实回传结果。

### 2026-10-07 Phase 124：GCIDE 0.54 的条目级来源模型补查

GCIDE 是 Phase 24 来源画像中最大的单一明确词典来源族之一：受限机器 triage 报告记有 `GCIDE_0.54` 画像 1,573 个 payload；许可证据日志另记 1,580 个 evidence objects。两项计数单位不同，本轮没有将它们强行对齐。GNU FTP 目录列出 2024-12-31 的 0.54 发布归档及 detached signature，GCIDE 项目许可页声明 GPL v3 或任何后续版本。定向核读上游 auto-sync README 又发现：GCIDE 汇集 1913 Webster、WordNet 1.5 与志愿者补充；README 描述 `<source>` 段落级来源标记，并允许一个定义同时携带多个来源标签。

这使发布审计更具体，但没有清权：当前冻结 evidence 的 `GCIDE_0.54` 标签尚未逐条匹配官方 archive 字节，且没有审计每条定义的子来源标记是否保留、是否有 WordNet 1.5/其他第三方内容或该定义是否进入某个冻结规则/selected witness。对本次没有下载 archive、验签或发出词条正文；只检查官方目录/许可页和项目 auto-sync README。项目 release clearance 仍维持 `not_cleared_for_public_release`。机器补充见[来源许可证据日志](../sources/source_release_rights_evidence_2026-10-06.json)；官方依据：[GNU GCIDE 归档目录](https://ftp.gnu.org/gnu/gcide/)、[GCIDE 许可页](https://gcide.gnu.org.ua/license)、[上游 README 镜像](https://github.com/GitMirroring/gcide)。详见Phase 124 深度报告。

### 2026-10-07 Phase 125：GCIDE profile/evidence 计数对账

新增只输出聚合计数与文件指纹的 `src/analysis/audit_gcide_source_evidence.py`，范围限定到 sense index 指向的 `alternative_or_definition_wsd_frozen` 来源家族，不扫整个 115,235-payload bundle。运行验证 5,625/5,625 唯一 payload 路径与冻结 checksum sidecar 匹配，共 1,401,596,052 bytes；1,573 个 payload 含规范化后的 `GCIDE_0.54` 标签，包含 1,580 个 evidence objects。于是 Phase 124 的 1,573/1,580 差异由计量单位不同解释，而非冲突：在含任意 source evidence 的 payload 中，GCIDE multiplicity 为 1,567 个 payload 各含 1 个、5 个 payload 各含 2 个、1 个 payload 含 3 个；另有 1,871 个 evidence-bearing payload 不含 GCIDE。1,580/1,580 对象 `source_version=0.54`，`definition_text_sha256` 字段格式均为有效 64-hex；该证据没有 ILI 字段。

机器报告为[GCIDE source-evidence census](../outputs/phase125/gcide_source_evidence_census.json)，重跑命令 `python -m src.analysis.audit_gcide_source_evidence --force`。本工具未读取/输出释义值或身份；但它也**未**将定义哈希对照官方 tarball、识别条目级 `<source>` 子来源或追踪至图规则/witness。故它提高了冻结包内部的来源 profile 复算性，不构成上游 release match、第三方授权或 release clearance。详见Phase 125 深度报告。

### 2026-10-07 Phase 126：冻结 GCIDE 定义哈希与官方归档交叉审计

从 [GNU 官方 FTP](https://ftp.gnu.org/gnu/gcide/) 下载 `gcide-0.54.tar.gz` 至本地临时目录。18,876,227 字节归档的 MD5 `2fde298eb57af31e885497b81e634e88` 与 [GCIDE 下载页公布值](https://gcide.gnu.org.ua/download)一致，计算得 SHA-256 `ae9b0187a1d1e7ee86218c707503b5082894c0ba61eeee26d226bca169e7fbd0`；未下载或验证 detached GPG 签名。审计器重验同一冻结来源家族的 5,625 个 payload checksum，并扫描归档 179,781 个 `<def>` 块。1,580 条冻结 evidence 对象对应 1,562 个不同 `definition_text_sha256`。按 `<def>` 内层原始字节计算 SHA-256，命中 88 个不同冻结哈希（归档中 89 次）；去标签、HTML entity 解码、NFC 与空白归一化后，UTF-8 与 cp1252 两条命名路径各命中 846 个不同哈希（归档中 854 次）。

Phase 126 的同 payload 字段核对进一步发现：1,579/1,580 个 GCIDE evidence 哈希精确等于 `synset.raw_definition` UTF-8 字符串的 SHA-256；这些对象也与 `source_record.gloss_levels[0]` 哈希相等，分布于全部 1,573 个 GCIDE-bearing payload。1,572 个 payload 的所有 GCIDE evidence hash 均与 `raw_definition` 匹配；仅 1 个 evidence 对象例外，且其哈希未匹配该 payload 的任何字符串字段。该例外哈希在官方归档规范化扫描中命中一个 `<def>` 段落，其所在段落经正则恢复出 WordNet 来源标记。上游 README 说明段落可有多个来源标记，因此该结果是明确的 WordNet 混合来源审查线索，不是唯一来源裁定。归档 crosswalk 的总体 846/1,562 命中主要将冻结释义文本与 GCIDE `<def>` 作规范化匹配；它不证明释义唯一来自 GCIDE，也不能说明进入了哪条规则。生产端代码未找到，异常对象的 hash 输入字段仍待查。

对规范化命中项做的段落级 `<source>` 标记恢复是基于正则的探索性统计：854 次命中中，664 次所在段落有 Webster 1913 标记、150 次有 WordNet 标记、22 次未恢复到标记；类别可重叠，故不能相加为互斥总数。匹配只表明指定规范化下的内容对应；尚不知道归档端与冻结 gloss 之间所有转换规则，原始哈希命中更少也不表示未命中定义不在归档。标记不能证明唯一来源、sense 对应、语义支持或进入具体图规则/witness。归档 MD5 页面校验值一致但未验签，GPL v3-or-later 的提供方声明也不清理 Webster/WordNet 等子来源。因此来源发布许可仍未清权。

追查仓库内 `definition_text_sha256` 生成逻辑后，仅找到读取/校验该字段的审计和 OEWN 比对代码，没有 GCIDE evidence producer。虽然生成代码不在当前仓库，但同 payload 精确哈希对账支持 1,579 条的输入文本就是冻结 `synset.raw_definition` UTF-8 字符串；剩余一条异常待追溯。冻结 GCIDE 证据未带 ILI，故仍不能与上游具体 sense 唯一对应。归档端与冻结释义之间的实体解码/标记剥离流程也未证实。

机器 artifact 为[归档哈希交叉表](../outputs/phase126/gcide_archive_hash_crosswalk.json)，审计器为 `src/analysis/match_gcide_evidence_hashes.py`；详见Phase 126 深度报告。

### 2026-10-07 Phase 127：GCIDE payload 到 frozen graph/witness 的路径级 lineage

新增 `src/analysis/audit_gcide_graph_lineage.py`，在 Phase 125 同一 5,625 payload checksum 锁定范围内，将 GCIDE-bearing payload path 连到 sense index、graph rule/hyperedge、active-clause source documents 和 selected witness clauses。1,573/1,573 payload 各在 sense index 唯一引用，且其 `synset_id`/`sense_id` 均等于 index identity；对应 1,570 个 distinct graph heads，全部有 rule 与 selected-witness row。40 个 witness 是 seed；其余 1,530 个非 seed witness clause 全部匹配 graph rule 和 hyperedge。

按 source payload path 计，1,188/1,573 出现在至少一个 active-clause source document；其中 886/1,573 进入 selected-witness source document，302/1,573 只出现在非选中活动子句，385/1,573 不在任何 active-clause source document。Phase 126 中唯一 hash 不等于本地 raw gloss、且同 payload 无字符串匹配的对象属于这 385 个未链接项；它在 GCIDE 归档中命中带 WordNet marker 的段落，但当前没有直接 graph source-document 或 selected-witness 链。结构路径只说明文件被索引/引用，不证明 source text 语义支持 literal，也不作独家来源或许可判断。机器 artifact 为[GCIDE graph lineage](../outputs/phase127/gcide_graph_lineage.json)，详见Phase 127 深度报告。

### 2026-10-07 Phase 128：selected-witness gloss hash 与归档段落来源标记

对 886 个被 selected witness source document 直接引用的 GCIDE payload，以本地 `synset.raw_definition` UTF-8 SHA-256 和 GCIDE tarball 的去标签/HTML 解码/NFC/空白归一化定义 hash 做交叉匹配。506/886 个 payload（502 个 distinct gloss hashes）在 0.54 归档中至少命中一个 `<def>`；对应 503 次 archive occurrences。其间 46 个 payload 的 hash 至少匹配到一个带 WordNet marker 的归档段落，433 个至少匹配到一个 Webster 1913 marker 段落，489 个至少有任一非空来源 marker，17 个未恢复到来源 marker。来源类别按匹配 hash 聚合且可以重叠；同一文本可能在不同标记段落多次出现。380 个 selected payload 在本轮规范化下未匹配，不能据此断言归档无对应内容。

这是“冻结 gloss 内容—选中 witness 来源路径—归档段落标记”的结构/内容交叉证据；不证明 marker 所示来源独家贡献、相应词句支持某条 rule literal，亦不构成 WordNet/GCIDE 派生规则准确率或许可结论。artifact 为[Phase 128 marker/witness crosswalk](../outputs/phase128/gcide_marker_witness_crosswalk.json)，代码和解释见 `src/analysis/audit_gcide_marker_witness_crosswalk.py` 与Phase 128 深度报告。

### 2026-10-07 Phase 132：OEWN 2025 Plus 400 项标注包来源与署名 gate

对 `config/annotation_preregistration_v3_lock.json`、Phase 121 preflight 和 blind batch manifest 做了只读对账。preflight 报告 400/400 raw gloss 与 pinned OEWN 2025 Plus archive crosscheck 精确匹配，输入锁和 schema 检查通过；manifest 记录 release/version/archive SHA、attribution/copyright、CC BY 4.0 和官方许可 notice URI、修改说明与用途限制。官方 [OEWN 2025 release](https://github.com/globalwordnet/english-wordnet/releases/tag/2025-edition) 区分 2025 与 2025 Plus；官方 [LICENSE.md](https://github.com/globalwordnet/english-wordnet/blob/main/LICENSE.md) 要求归属 Princeton WordNet 与 Open English WordNet team，并明确底层 Princeton WordNet 条款继续适用于相应数据。[Princeton WordNet 许可页](https://wordnet.princeton.edu/license-and-commercial-use)提供其 WordNet 数据库版权声明与许可文本。

该批次的 manifest 已包含双方署名信息和官方 OEWN 许可链接；因此本轮没有改写被 lock 的 manifest 或 lock 哈希。该来源级审查不会把 `distribution_authorized=false` 改为 true：协议仍未签署，无 external preregistration ID，0 个人工回传。它也不为冻结混合来源 bundle 作任何许可判断。机器字段与未决 gate 见[权利证据日志](../sources/source_release_rights_evidence_2026-10-06.json)的 `annotation_batch_v3_rights_review_2026_10_07`；[发布门槛](data_release_gate.md)保留外发/公开发布需项目负责人明确确认的要求。

### 2026-10-08 Phase 144：annotation v3 的 OEWN target identity 补充核查

新审计程序 `src/analysis/audit_annotation_frame_release_identity.py` 对锁定 v3 frame/blind/key、release cross-check、release archive 和 source payload 做 hash 与身份比对。固定归档 SHA-256 为 `8832b8fa26a14c0ba8c99bb1ef8db6f9e122a6d9193b65ca9e0ef572580fee7e`；45 个 taxonomy 文件及 27 个 entries 文件均与归档一致。400/400 sense ID 存在且 raw gloss cross-check 精确，但 frame/source payload 的 POS 有一项与 release 不同，frame 另有一项漏掉 release lemma。问题来自旧 frame 分别采用冻结 graph POS 与首条匹配 source record lemma，旧 cross-check 并未验证这些字段。不得改写被锁定的 v3 内容；新 pair context 以 pinned release record 为准。完整机器证据及限制见[Phase 144 审计](../outputs/phase144/annotation_frame_release_identity_audit.json)与报告。该发现不改变任何署名/许可授权状态。

### 2026-10-08 Phase 185：OEWN 2025 Plus 固定 tag 的 notice 与 frame 对账

Phase185 复跑 `src.analysis.audit_annotation_frame_release_identity`，结果与 Phase144 逐字节相同（SHA-256 `373e25677bd9805443aa76770f2aa8daab8e7c56048dd065bed9277ba6f4d6aa`）。本地 `tmp/oewn-2025-plus-json.zip` SHA-256 为 `8832b8fa26a14c0ba8c99bb1ef8db6f9e122a6d9193b65ca9e0ef572580fee7e`；400/400 raw gloss 精确匹配，400/400 target senses 可找到，但 frame/source payload 有 1 条 POS 不匹配和 1 条 lemma set 不完整。blind batch 对 frame 的两字段差异均为 0，因此继承 frame 的身份问题。锁定 v3 frame、batch、manifest 和 lock 未改。

本轮将许可证据固定到 [OEWN 2025 release](https://github.com/globalwordnet/english-wordnet/releases/tag/2025-edition) 的 `dc343f2` tag：tag-pinned [LICENSE.md](https://raw.githubusercontent.com/globalwordnet/english-wordnet/dc343f2/LICENSE.md)（19,863 bytes，SHA-256 `672cc8b5663e8dc74c4b07a9dcf477193853575b119908fd3dc0aeeb60a9dbbb`）与 [WNDB_License.txt](https://raw.githubusercontent.com/globalwordnet/english-wordnet/dc343f2/WNDB_License.txt)（1,740 bytes，SHA-256 `df30ec18fbabcdaf031b79ea026d3e6b959010cffe6dd7be9ac137822175b904`）。后者写明 WordNet 3.1；[官方 WordNet 3.1 release](https://github.com/globalwordnet/english-wordnet/releases/tag/3.1)也说明其来自 Princeton WordNet 3.1 并按 WordNet License 发布。Princeton 当前许可页展示 3.0 文本，故仅作为该版本的通用当前页面记录，不能单独取代 OEWN tag-pinned 3.1 notice；本审计不推断许可不兼容，也不提供法律结论。

本地 2025 Plus JSON ZIP 有 73 个成员，但无 license/readme/notice 类文件；这提示未来获准分享材料时需随包保留适用 notice 和 attribution，不构成缺少授权的推断。lock 状态仍是 `protocol_signed=false`、无 external registration ID、`distribution_authorized=false`；整体混合来源 bundle 的 `release_clearance` 仍为 `not_assessed`。该子来源审计不解除任何外发 gate。机器证据见[Phase185 review JSON](../sources/oewn_2025_plus_annotation_release_rights_review_2026-10-08_phase185.json)、[当前身份审计](../outputs/phase185/annotation_frame_release_identity_current.json)和深度报告。


## Phase 163：全量 source-record payload 当前复算

2026-10-08 再次运行来源元数据普查，读取 `indexes/senses.jsonl` 所引用的 115,235 个唯一 source-record payload（18,734,636,389 bytes）。全部 payload 均可解析且逐个匹配 `checksums.jsonl` 中的字节数和 SHA-256；110,425 条 sense 记录中 malformed 为 0，source path 重复为 0，bundle integrity lock 有效。机器结果不输出 gloss、sense ID 或来源路径，其 SHA-256 与 Phase23 保存的聚合报告完全相同。许可字段名启发式命中仍为 0，`release_clearance` 仍是 `not_assessed`；这不是权利审查或语义验证。见[Phase163结果](../outputs/phase163/source_release_metadata_audit_current.json)与深度报告。
## 2026-10-08 Phase 171：最新来源权利交叉表与 OEWN witness 链复算

对 Phase24 privacy-filtered candidate triage 和当前 rights evidence log 重跑 exact-label crosswalk：90 个 profile、58 个标签、3,595 个 profile-payload 计数中，22 个 profile/2,343 个计数与 rights log 精确同名；68 个 profile/1,252 个计数未精确匹配。与 Phase52 对比，候选 triage SHA 未变、rights log SHA 已变，但命中总数未变，因此新证据更新了标签状态而未增加字面 crosswalk 覆盖。此 profile 计数不等于独立上游作品、payload 或 license clearance。

另以当前 frozen bundle 重放六个 OEWN 2025+ release-matched 候选：6/6 唯一连接到 sense index identity，11/11 graph clause 对齐 hyperedge，6/6 selected witness source document checksum 验证通过。selected-witness source document 中，2/6 同时含候选 payload path 和匹配的 OEWN ILI/definition hash；2 个候选只在非选中 active clause，2 个不在 active clause source documents。此结构 lineage 不证明 gloss 对 literal 的语义支持或 bundle 可再分发。机器结果与哈希见Phase171报告及两个[现态 crosswalk](../outputs/phase171/source_rights_crosswalk_current.json)、[OEWN lineage audit](../outputs/phase171/oewn_2025_plus_graph_lineage_current.json)。旧 Phase52/89 artifacts 保留不动。

## 2026-10-08 Phase 172：Glottolog 5.3 官方发布证据与本地绑定缺口

官方 Glottolog 下载页列有 5.3 发行文件，并声明 Glottolog 5.3 使用 CC BY 4.0；该页还说明站点下载由公开 glottolog/glottolog 仓库生成、仓库 releases 存档于 Zenodo。[官方页面](https://glottolog.org/meta/downloads) 当前 privacy-filtered 候选 profile 有 3 个 payload，host 是 glottolog.org，但 source_version/source_ontology 字段缺失，没有本地 payload 到特定发行文件或哈希的关联。因此只新增了来源家族级官方证据，明确 `reuse_clearance=false`，不代表本地记录或整个 bundle 获得再分发许可。

重新运行 exact-label-only 来源交叉表后，rights log 标签由 16 增至 17；精确匹配由 22/90 profiles（2,343/3,595 个 profile-payload 计数）增至 23/90（2,346/3,595），未匹配为 67/90（1,249 个计数）。profile-payload 计数不等于独立作品或授权范围，`release_clearance` 仍为 `not_assessed`。详情见Phase172深度报告与[机器交叉表](../outputs/phase172/source_rights_crosswalk_current.json)。

## 2026-10-08 Phase 173：PMC Open Access Subset 文章级许可边界

PMC 官方说明 OA Subset 的许可因文章而异，应查文章本身的许可声明；其自动抓取限于指定服务，嵌入内容可能另有版权限制。[OA Subset](https://pmc.ncbi.nlm.nih.gov/tools/openftlist/)、[版权通知](https://pmc.ncbi.nlm.nih.gov/about/copyright/)与[按许可检索](https://pmc.ncbi.nlm.nih.gov/tools/articles-by-license/)。privacy-filtered triage 中两个 PMC OA payload 来自两个 profile，均缺少 source_version/source_ontology；未提供文章身份或具体条款绑定。因此只登记官方来源族规则，`reuse_clearance=false`，总体 `release_clearance` 仍 `not_assessed`。rights log 为 18 个标签，exact-label 命中 25/90 profiles、2,348/3,595 profile-payload 计数，未匹配 65/90 profiles、1,247 个计数。详见Phase173报告和[机器交叉表](../outputs/phase173/source_rights_crosswalk_current.json)。

### 2026-10-08 Phase 191：frame/release 差异的下游候选影响

只读聚合影响审计表明，1 条 POS mismatch target 没有 direct hypernym edge，所以 pinned-release 与 locked-frame POS 的 noun edge 计数同为 264，parent-surface 行同为 507。另一条、与 POS mismatch 不重叠的 lemma-set mismatch 位于一条 noun edge：frame 有 1 个规范化表面形式，release 有 2 个；来源记录保留 2 种 lemma-list variant。此观察不确定哪一版符合未来研究 estimand；新候选继续按既有记录使用 pinned release，旧 frame/batch/key/lock 均保留原字节。外发授权与 release clearance 未改变。见Phase191报告及[机器影响审计](../sources/oewn_candidate_identity_impact_audit_2026-10-08_phase191.json)。

### 2026-10-08 Phase 220：来源权利证据覆盖 crosswalk

使用只读脱敏工具把 Phase24 的 90 个候选来源 profiles 与 18 个权利日志标签按精确字符串对账：58 个候选标签中，25 个 profile（2,348 个 profile-payload 计数）有同名日志行；65 个 profile（1,247 个计数）未匹配。profile 中 payload 计数跨组求和为 3,595，**不是唯一 payload 数**；此审计只覆盖 `alternative_or_definition_wsd_frozen` 候选来源族，不代表全 bundle。未匹配部分主要是 `noncanonical_or_nonscalar` 的 22 profiles/1,199 个 profile-payload 计数，不能视作一个统一来源提供方。精确匹配不等于版本/字节绑定、许可兼容或清权，机器记录保持 `release_clearance=not_assessed`。详见Phase220报告和[机器 crosswalk](../sources/source_rights_coverage_audit_2026-10-08_phase220.json)。

MeSH 后续审计应保存缓存格式、生产年、准确 artifact/bytes 与 frozen record 对应关系；NLM 页面还要求显著署名并保持数据最新或披露过时状态。[NLM Terms and Conditions](https://www.nlm.nih.gov/databases/download/terms_and_conditions.html)；[MeSH downloads](https://www.nlm.nih.gov/databases/download/mesh.html)。OLS 托管的 MeSH、NCIt、ChEBI、FoodOn 和 Disease Ontology 必须逐 ontology 分别解析版本和许可元数据；OLS 官方建议需要复用数据时优先上游 OWL/API，API metadata 可提供版本/rights 调查线索但不能证明本地缓存身份。[OLS downloads](https://www.ebi.ac.uk/ols4/downloads)；[OLS API guide](https://www.ebi.ac.uk/ols4/ols3help)。整体发布状态未改变。

### 2026-10-08 Phase 221：MeSH/OLS 记录标识与版本绑定

新增只读审计器 [`audit_mesh_ols_record_binding`](../src/analysis/audit_mesh_ols_record_binding.py)，重新验证 Phase24 所限 5,625 个 payload checksum，并对 461 个 unique MeSH/OLS-target payload、631 个 evidence objects 作字段覆盖审计。全部 evidence objects 都有 `external_id` 和 `source_locator` 字段，但 631/631 缺 `download_url`；OLS 的 275 个 evidence object 仅记 `local_exact-query_cache_snapshot`，不含可识别上游发行版标签。

其中 130 个 payload 同时含直连 NLM MeSH 与 OLS MeSH。原始 ID/locator 字符串不同；对 URI/namespace 末段 token 规范化后产生 130 个候选标识符。只读查询 NLM 官方 REST API，130/130 个请求均 HTTP 200，`identifier` echo 相符。该结果确认当前 ID 可解析，不证明历史缓存的版本、格式、字节或条款身份。[NLM MeSH RDF](https://id.nlm.nih.gov/mesh/)说明其 REST record API；当前 NLM 再分发 terms、更新节奏与格式说明详见其[下载页](https://www.nlm.nih.gov/databases/download/mesh.html)和[Terms and Conditions](https://www.nlm.nih.gov/databases/download/terms_and_conditions.html)。

同日读取 OLS 当前 API metadata，五个 namespace 均成功返回版本/version IRI；其加载时间均在 2026-10-07。OLS metadata 的这些现态版本无法回填到旧的 generic local cache 标记。五个当前 response 都没有 OLS `license`/`rights` annotations 值；这不说明各 upstream ontology 没有许可声明。[OLS downloads](https://www.ebi.ac.uk/ols4/downloads)也指出其内部数据库格式未文档化且可能改变，建议使用 OLS API 或 upstream OWL。完整聚合、response hashes、输入指纹与解释限制见Phase221报告和[机器 artifact](../sources/mesh_ols_record_binding_audit_2026-10-08_phase221.json)。发布 clearance 未改变。

### 2026-10-08 Phase 222：前向 source evidence 捕获合同

对当前 checkout 的 `src/`、`archive/` 与 `examples/` 搜索确认：现有 `source_evidence` 命中属于消费者和审计工具，未发现构造或写入该字段的 producer；因此结论限定为“当前 checkout 无 producer”，不外推到上游工程。新增[前向捕获合同](source_evidence_capture_contract.md)与[JSON Schema](../config/source_evidence_capture.schema.json)，用 payload SHA-256 + evidence ordinal 绑定本地对象，并区分当前记录身份验证与历史 release/bytes 验证。该草案不回填历史缓存、不含 gloss 或 payload path，`rights_clearance` 固定为 `not_assessed`；尚未接入 producer 或完成端到端 replay。详见Phase222深度报告。

### 2026-10-08 Phase 223：外置冻结管线代码边界与合同修订

配置指向的 frozen bundle 仅包含 `tools/read_graph.py` 这一可执行源码。一条 recovered-history 记录标注管线 `Wn2Lingua/KaikkiBasisHeldoutEvaluation`，但该记录引用的原始和 prepared source 文件均不在当前机器，记录也没有 producer code hash。bundle replay 报告 154,206/154,206 clauses 有 source-DNF evidence、source parse errors 为 0，但 canonical replay 为 110,424/110,425 heads 精确匹配；这不能升级为端到端逻辑化代码可复现或 gloss 语义支持。修订后的捕获 schema 强制 producer/parser/normalizer 实现哈希。见Phase223报告和[脱敏机器审计](../sources/source_producer_boundary_audit_2026-10-08_phase223.json)。
# Phase229：basis source-record lineage 复算

冻结包的 85 个 basis IDs 可与 `nodes.tsv` 和 `indexes/senses.jsonl` 一对一匹配，且 POS、lemmas、定义快照逐项一致。sense index 中共关联 166 条 basis×source-record 路径，全部能在 checksum sidecar 中定位；逐文件重算字节数、SHA-256 和 sense identity 均通过。输出和命令见Phase229 报告及[复算 CLI](../src/analysis/basis_source_lineage_audit.py)。

同一审计还核对全图 `active_clause_sources`：154,206/154,206 个 clause 均有且仅有一个有效 clause-index source row，合计 154,356 条 source-document×clause links；没有缺失/重复/越界索引或空 source list，全部关联路径均属于同 head 的 source-record 元数据。此检查是 provenance coverage，不表示不同 source documents 的逻辑替代关系已经定义。

这个结果证明当前冻结包有完整的 basis 身份与 payload 完整性链，**不**证明源 gloss 对 Horn 规则的语义支持、文件许可，或 source-record 删除与 basis atom 删除等价。source intervention 必须先明确规则证据替代语义并重算相应闭包。

在明确的“删除 basis sense 的全部冻结 source-record payload、撤回对应 seed 并禁用以该 sense 为 head 的 clauses”干预下，Phase230 的 3,570 对结果与 seed-only deletion 完全相同。该特定冻结包结论见Phase230报告；它不适用于上游 WordNet 文档删除或单 payload 删除。

Phase231 将删除单位缩小为一个 basis sense source-record payload，在“任一登记来源仍在即保留 clause”与“全部登记来源都须保留 clause”两种显式策略下重算 166 个情景。两种策略的全图闭包损失集均与 seed-only deletion 完全一致；24 个直接闭包核对和独立输出路径复算通过。该结果不验证 producer-level 多来源语义，也不表明不同 source records 语义可互换。见Phase231报告、[CLI](../src/analysis/basis_single_payload_deletion_audit.py)、[机器输出](../outputs/phase231/basis_single_payload_deletion_audit.json)及[机器记录](../sources/basis_single_payload_deletion_audit_2026-10-08_phase231.json)。

