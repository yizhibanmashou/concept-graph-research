# 研究就绪度与论文主张审计

> CI 状态说明（2026-10-29）：本文是历史快照，其中子项目 workflow 不会在当前仓库自动运行；相应研究测试矩阵已配置到[根工作流](../../.github/workflows/checks.yml)，但尚未在 GitHub 运行。当前范围见[CI 说明](continuous_integration.md)。

**当前状态快照：2026-10-12（更新至 Phase277）**

### 当前总览（Phase266–277）

- **会议方向对齐（Phase277）：** 9 月 30 日的直接任务是对现有 WordNet 依赖图做初步分析；Phase1 确实执行了传统图描述，Phase275 已撤回其过宽统计/语义解释。Phase272 的 AND/OR-aware closure/witness replay 深化了对现有超图的结构审计。团队提出的十万级义项逻辑化、真实 gloss→logic fidelity 与自然语言推理效果仍未完成。当前结论以[项目总报告](../../report/project_review_2026-10-29-current.md)为准。

- **Lingua-Graph prior-art 更新（Phase276）：** ACL 2026 的共享句子结构表示与 task decision 分层要求收窄“显式图/局部子结构复用/可解释性”的宽泛新颖性；其 entity-span hostability 不是 source-support 或 entailment 评测。项目较窄的 sense-bound gloss→typed Horn + AND/OR proof replay 差异仍未由 adjudicated gold 或 matched experiments 验证。文献对照见[最近工作矩阵](closest_work_comparison.md)，项目当前有效性边界见[总报告](../../report/project_review_2026-10-29-current.md)。

- **形式化与 witness 证据：** Phase266 的现态机器记录显示，固定冻结图上的 witness 结构与指定 ground Datalog 证明可重放（3,596 nodes、14,923 dependency edges、3,512 rules；0 replay errors）。这支持一个 source-linked 形式实例及其 replay，不证明 gloss 语义支持、WSD 正确、开放世界蕴含、许可或端到端方法效果。后续 Phase68–72 已有带类型 Datalog checker 和合成 pipeline replay 的实现及聚焦行为验证；它验证声明的 type table 下的有限程序，不构成 WordNet lexical typing 或自然语言 gold。
- **完整冻结图当前复算：** Phase272 重跑完整 frozen hypergraph 与 minimum-witness 审计；分别与 Phase213 输出逐字节一致。lock、AND/OR closure、110,425 条 witness 和最小深度证书全部通过。selected-witness descendants 对精确删除损失在 66/85 次高估、19/85 次相等。此为固定输入下的结构可复算证据，不证明 gloss semantic support；本轮未重读全部 source payload。
- **人工语义评测与启动 gate：** Phase266 preflight 的 400 项/24 strata 输入检查通过，但当前 lock 仍是 `protocol_signed=false`、无外部注册 ID、`distribution_authorized=false`，标注回传为 0。没有双标裁决的 gloss-span source-support gold、IAA、真实模型输出或 matched baseline；Track A v1 仍是设计草案。
- **实现兼容边界：** Phase268 静态审计确认 legacy claim-review `/0.1` 将 raw gloss hash 与 premise hash 绑定，并以 premise 坐标检查 span；它缺少 Track A 的 relation-edge/surface/condition 外键与独立面板 provenance。Phase271 在 validator 0.3 上将 synthetic producer→replay→bridge 以独立目录复算两次，三份成功 JSON 字节一致；坏 manifest pin、缺失候选和 query 三元组错配（报告哈希已匹配）均 fail closed。该结果只验证工程接线，不是实际 lexical candidate。新 Track A 合同仍待研究设计和许可/责任 gate 冻结后版本化实施。
- **相关工作与论文主张：** Phase267–270 已筛读形式化忠实度、drift probes、validity/plausibility 与证明可用性评价的近邻。ProofRank 将数学 proof utility 分为正确性之外的 proxy；本项目的结构重放和图指标不能解释为解释质量/效用。Phase270 的 147-log 索引与矩阵 crosswalk 详见阶段报告；计数只反映已有筛读日志/矩阵的可追溯性，不等于系统综述召回率或新颖性证明。所有论文级有效性、新颖性、lexical generalization 和证据链效用仍未验证。
- **APF 补充对账：** Phase273 发现 2026-10-05 ACL 候选快照中的 pending 状态与 2026-10-06 既有筛读日志冲突；后者已将 Findings ACL 2026 APF 保留为邻接先例并定向阅读 §3–4。Phase273 补充人类 ranking check 与评测边界，没有新增候选或唯一论文。APF 说明通用 NL→executable formalization 不能单独主张新颖，但不提供 WordNet gloss-span support 或 Horn proof gold；项目窄差异仍未证实。
- **归属与发布：** AAAI 2027 匿名稿继续仅作内部 prior-work 对照，不是用户成果。来源许可、release-to-payload 归属和公开数据/代码发布资格仍须逐项审核；哈希完整或资源官网公开不自动等于本项目有再分发权。
- **当前 outputs 发布面：** Phase274 对 `outputs/` 现存 212 个文件重跑只读字段/路径/hash 扫描；22 个命中文本字段名、41 个命中身份/来源字段名、53 个被 Git 忽略。四个未忽略文本字段命中经有限结构检查为整数计数或算法说明字符串。Phase275 随后查看全部 7 个非 JSON 文件；两张图显示 source/sense 标识，脚本改为相对项目配置但统计仍属探索性，均未因此清权。发布状态不变。见Phase274报告、[Phase275报告](../../report/research_progress_deep_review_2026-10-12_phase278.md)及本机忽略的[审计清单](../sources/output_release_surface_audit_2026-10-08_phase274.json)。
- **Phase1 旧结论复核：** Phase275 确认 Phase272 的 85-basis 正 Horn 闭包和 witness 深度统计可作为结构事实；旧 cycle 数无可复算 detector，旧幂律回归与 pairwise projection clustering 不支持幂律/小世界或自然语言互定义结论。两份历史脚本已去除绝对本机路径，但其统计方法仍不适用于论文推断；五张图可见源/义项标识且未经许可清权。见[Phase275深度报告](../../report/research_progress_deep_review_2026-10-12_phase278.md)。

证据入口：[Phase266 现态与 replay 记录](../sources/phase266_current_state_audit_2026-10-08.json)、[Phase268 合同兼容审计](../sources/track_a_contract_compatibility_audit_2026-10-08_phase268.json)、[Phase269 文献全文审计](../sources/phase269_validity_plausibility_fulltext_audit_2026-10-08.json)、Phase270 ProofRank 全文审计、[Phase271 bridge 复算审计](../sources/phase271_bridge_replay_audit_2026-10-08.json)、[Phase272 完整图复算](../sources/frozen_graph_witness_replay_2026-10-08_phase272.json)、[Phase272 深度报告](../../report/research_progress_deep_review_2026-10-12_phase278.md)、[当前研究定位](research_positioning_and_prior_work.md)、[主张—证据交叉表](research_claim_evidence_crosswalk_2026-10-08_phase204.md#当前状态增补-phase266271-2026-10-08)、[阶段索引](../README.md)。

Phase273 的补充对账见深度报告、[2026-10-06 既有筛读日志](../sources/literature_screening_log_2026-10-06_acl_formalization_2026.json)、[补充筛读日志](../sources/literature_screening_log_2026-10-08_apf_findings_acl2026_phase273.json)和[近邻矩阵](closest_work_comparison.md)。

### Phase263：旧文献去重快照的当前实现重建

Phase250–252 的旧去重器源码未保存，但输入日志快照仍在。以当前 CLI 重跑 137/138-log 集合后，输入指纹、summary 和 cluster assignments 均与历史输出一致。全 JSON 的差异限于历史/现态实现 SHA，以及当前实现从已有 venue 文本为 KDD 2026 的 P00200 提取 DOI（cluster 和 record 两个字段）；旧 JSON 没有该 DOI。Phase250 和 Phase252 历史输出互相逐字节一致。当前索引不冒充旧脚本逐字节重放，且该 DOI 未由本审计独立外部核验。详见Phase263报告、[结构化比较](../sources/literature_log_legacy_output_replay_2026-10-08_phase263.json)和[现态重建输出](../outputs/phase263/)。

### Phase262：当前文献矩阵回指与去重索引现态复算

当前 closest-work 矩阵有 312 次外链、297 个唯一目标；302 次链接出现和 289 个唯一目标能回指结构化筛读日志。未匹配的 8 个目标/10 次出现是 5 个代码/项目资源和 3 个 Princeton WordNet 文档/数据 URL，修订 crosswalk 后学术引用候选未匹配为 0。对账只表示 bibliography log traceability，不是检索覆盖率、系统综述或新颖性结论。当前 142 条文献日志的 Phase256 去重索引由现有 CLI 重算并与保存 JSON 逐字节一致。Phase250–252 记录的去重实现 SHA-256 与当前脚本不同，本地没有该旧实现文件且 Git 无已提交历史；当时 replay 记录保留，但精确 producer 版本无法从当前工作区重建。见Phase262报告、[机器输出](../outputs/phase262/closest_work_log_crosswalk.json)及[source record](../sources/closest_work_current_matrix_crosswalk_2026-10-08_phase262.json)。

### Phase261：当前 Git 候选快照增量盘点

本轮对 `git ls-files --others --exclude-standard` 结果生成逐路径当前哈希账本：863 个未跟踪、非忽略文件，共 271,109,408 bytes；相对 Phase247 基线有 805 个哈希未变、7 个变化、51 个新增，旧清单路径没有消失。新增路径一律标记为未审阅并等待人工决定；25 个路径命中有限的限制语境关键词筛查，但该数量不等同于隐私或公开风险判断。Phase247 的类别只是建议处理类别；当前账本不是内容审查完成的发布 allowlist。仓库仍为 0 tracked files / 0 commits，本轮未 staging/commit。见Phase261报告和[逐路径机器清单](../sources/repository_current_snapshot_inventory_2026-10-08_phase261.json)。

### Phase260：WN30-lfs producer artifact 与可复现性边界

ISI 的 LFToolkit 页面提供 compiled JAR，称工具由 parse-tree XML 与另一个 transformation-rules file 驱动；工具 API 有 processing status、LF output 和 rule-ID trace，uncovered tree nodes 可以留下 partial output，页面警示变量可能未正确链接。JAR 已下载并哈希（32,613 bytes；manifest 为 J2SE 1.4.2_05），但本机没有 Java runtime。当前项目/归档未发现 WN30-lfs 专用 rule file、Charniak parser tree/config、WordNet GlossTag 输入映射或 per-synset producer log；官方 WN30-lfs ZIP 只有最终 XML。因此 generic JAR 可获取不等于 pipeline 可重放，`partial/complete` 也不能当作语义 gold；更没有证据把 13,578 个缺失 offset 逐条标为 parse failure。该状态是当前工作区的 artifact availability 结果，不证明文件历史上从未公开。详见Phase260报告和[结构化审计记录](../sources/wn30_lfs_producer_reproducibility_2026-10-08_phase260.json)。

### Phase259：WN30-lfs 来源 lineage 与 XML key schema

原始 ILF-WN 论文将 WN30-lfs 描述为 WordNet 3.0 gloss 的逻辑形式资源，并说明解析失败项不在其中；这只能给出资源层的例外描述，不足以逐 ID 解释当前 crosswalk 中的 13,578 个缺失 offset。对 Princeton 官方 ZIP 的可复算结构盘点得到 104,357 entries、104,321 unique keys、36 个重复 key occurrence；每个 entry 有 `word`、`status`、`gloss`、`lf`，部分有 `sublf`。XML entry 没有 offset 或 WordNet release 属性；root 的 `version="1.0"` 不表示 WordNet 版本。Princeton senseidx 文档明确 sense number/offset 会随数据库版本变化，跨版识别应使用 WordNet `sense_key` 或版本映射；WN30-lfs 的 `lemma#pos#sense_number` 不是 sense_key。因此严格 ID join 需绑定声明发行版，Phase257 的 88.4599% 不变，174 keys 和 13,578 缺失 IDs 的单条原因仍未证明。该盘点不评估 LF 语义或许可。见Phase259报告、[CLI](../src/analysis/audit_wn30_lfs_source_schema.py)、[机器结果](../outputs/phase259/wn30_lfs_source_schema.json)和[source record](../sources/wn30_lfs_source_schema_2026-10-08_phase259.json)。

Phase258 对 Phase257 中 174 个未映射 WN30-lfs keys 作受控字符串诊断：23 个在同 lemma/POS 下有唯一 gloss 候选，1 个有歧义，38 个只在其他 lemma 有同 POS 精确 gloss 候选，38 个同 lemma/POS 但无精确 gloss 候选，74 个没有精确 lemma/POS 或 gloss 候选。4 条候选仅在移除 `SOMETHING_N` 占位符后命中。`Twentieth_Amendment#n#1` 对应候选词项冲突的例子说明，精确 gloss candidate 不等于身份真值；Phase257 的 88.4599% strict ID coverage 不变。此诊断未确定 112 个无精确 gloss 候选的原因，也未评估 LF 语义。见Phase258报告、[CLI](../src/analysis/audit_wn30_lfs_unmapped_entries.py)、[机器输出](../outputs/phase258/wn30_lfs_unmapped_diagnostic.json)及[source record](../sources/wn30_lfs_unmapped_entry_diagnostic_2026-10-08_phase258.json)。

Phase257 用 Princeton WordNet 3.0 官方包建立 WN30-lfs 的严格 synset 身份 crosswalk。`index.sense` 的 206,941 行覆盖 117,659 个 `(POS, offset)`，与 release data files 完全对齐；WN30-lfs 104,357 个 XML entries 映射到 104,081 个唯一 IDs，严格 ID coverage 为 88.4599%，WordNet IDs 缺 13,578 个，映射到库外 ID 为 0。另 174 个 entry keys 未严格匹配；无模糊 fallback。多 entry/offset、exact duplicate keys 和 `partial/complete` 状态冲突单列。可复用 CLI、完整 missing-ID 输出、输入/脚本/输出哈希均有记录，独立 scratch replay 字节一致。该证据只支持资源身份覆盖，不支持 gloss→LF 语义正确率；WN30-lfs 授权未确认。见Phase257报告、[CLI](../src/analysis/audit_wn30_lfs_synset_crosswalk.py)、[机器输出](../outputs/phase257/wn30_lfs_synset_crosswalk.json)及[source record](../sources/wn30_lfs_synset_crosswalk_2026-10-08_phase257.json)。

Phase256 更正 Phase255 对 XWN 的证据深度描述：作者 6 页报告已做定向章节筛读，其试验重点是 preprocessing/WSD，不是端到端 LF 语义忠实度评测。Princeton WN30-lfs 官方压缩包已下载并结构解析：104,357 条 entry 均含 gloss/LF，51,614 `complete`、52,743 `partial`，13,565 条含 sub-LF；与 117,659 synset 总量的 88.69% 只是未经 offset crosswalk 验证的计数比。2012/2015 已有 XWN LF 连通性审计与自动修正先例：报告 54.05% disconnected-variable rate，修正后 23.82%；这些是 parser-defined 结构指标，不是 gloss-span 语义正确率，2015 改进计数沿用同一 parser。新增证据因此排除了“LF 一致性检查/修正本身无先例”的宽泛说法。剩余 source-span→方向化 typed rule 支持与 source-bound proof replay 仍无独立人工 gold、matched baseline 或项目效果。归档无 README/license，未清权；也未运行资源工具链重放。见Phase256报告、[结构化日志](../sources/literature_screening_log_2026-10-08_phase256_xwn_wn30_resource_reaudit.json)和[最近工作矩阵](closest_work_comparison.md)。

Phase255 沿 Phase254 的 2001 年直接先例继续筛读：ILF-WN (CICLing 2010) 对 WordNet 3.0 gloss 自动做 POS/依存解析并生成扁平中间逻辑形式，但不是标准 FOL；`conj_or` 是协调结构标签，不应等同析取 Horn clause。该版只为单义词加 sense offset、未应用 WSD，定量 gold fidelity 评测未完成。Rus 2004 的双人复核/moderation 和 predicate/argument/exact LF 指标是一般评测方法先例，不是 gloss-span source-support gold。XWN progress report 仅摘要/元数据核验；WN30-lfs 是 ILF-WN 论文提及的资源，尚未独立重放。Phase255 机器索引覆盖 141 份日志/2,050 条记录，形成 1,934 个保守书目簇；矩阵 291 个不同目标中 286 个匹配日志，5 个未匹配项均是项目/代码资源。独立重跑 JSON 逐字节一致。该 crosswalk 不衡量检索覆盖，且仍无 source-support gold、matched baseline 或论文级效果。见Phase255报告、[筛读日志](../sources/literature_screening_log_2026-10-08_phase255_wordnet_logic_lineage.json)、[矩阵](closest_work_comparison.md)和[机器输出](../outputs/phase255/)。

Phase254 全文定向筛读 Moldovan & Rus (FLAIRS 2001)，发现直接历史先例：WordNet gloss 已被转成带义项标记的逻辑谓词、动词论元槽位与 AND/OR 结构，并演示 QA 用途；81% 是 400 条手工 LFT 上的规则覆盖率，不是语义准确率。ACL 2001 同作者 companion 本轮仅核官方摘要/元数据，版本关系待全文比对。撤回“首次 gloss→logic/AND-OR/QA”类宽泛主张。Findings ACL 2024 WSL 与 LREC-COLING 2024 homonymy 工作分别作为上下文 span+sense linking 与粗粒度义项识别邻接先例记录，均非 gloss literal support gold。剩余 source-span→typed rule/witness replay 仍是未验证假设；无语义 gold、matched 2001 baseline、论文级效果，AAAI 2027 归属边界与许可状态不变。详见Phase254报告、[筛读日志](../sources/literature_screening_log_2026-10-08_phase254_direct_prior_art.json)和[矩阵](closest_work_comparison.md)。

当前代码和结构输出支持冻结包上的可复算图审计、Horn/Datalog 结构证书与单义项/claim 级 strict proof/NLI 路由；尚无经人工裁决的 WordNet gloss-span→typed Horn source-support gold、matched baseline 或项目效果结论。匿名 AAAI 2027 稿件明确不是用户成果且受内部使用限制；任何利用该稿/数据的研究都需遵守既有归属与授权边界。冻结来源许可未清权，Track A 研究者裁决/预注册/外发授权仍未完成；400 项 locked v3 与拟议 Track A 是不同协议。Phase218 的 `protocol_signed=false`、`distribution_authorized=false` 与无回传状态仍意味着不得把现有 frame 当作 Track A gold。Phase229 的 witness/source lineage 与 Phase230/231 的结构敏感性结果仅支持冻结快照内部属性；不验证 gloss source semantics。Phase238 确认 strict proof/NLI 路由已组合，但 relation-edge/surface/condition 到 candidate/claim 的 Track A 外键合同仍未闭合。Phase240 的 NeurIPS APTP 筛读收窄了独立 proof checker 的宽泛新颖性。Phase241–242 发现当前 Git 仓库无提交/无跟踪文件，已有 800 个未跟踪候选文件约 240 MB；已忽略本地索引、缓存和临时目录，但初始快照仍需逐路径内容审核。Phase243 的图与 witness 结构复算输出分别与 Phase213/224 artifact 逐字节一致。Phase244 进一步对 115,235 个唯一 source payload（18.73 GB）全量重哈希，均匹配 frozen checksums，聚合输出与 Phase210 逐字节一致；这不证明来源真实性、适用许可或 gloss 语义支持，`release_clearance` 仍为 `not_assessed`。Python 源码/测试静态导入扫描未发现第三方 import，CI 仅是配置证据；拟议的 sense-specific gloss→typed AND/OR Horn support 与 proof replay 仍只是未验证的研究假设。Phase245 在锁定 v3 混合词性 frame 中按 `pos=n` 筛出 252 个 noun targets，重建 genus 启发式并对照同一 OEWN release 的 264 条普通直接名词 hypernym 边：candidate coverage 98.0%，资源 pair P/R/F1=10.7%/36.7%/16.5%。该资源对齐诊断不是 gloss semantic gold、独立语义验证或 matched model result；Track A 协议、标注与授权仍未完成。详见Phase245 报告和[机器记录](../sources/track_a_genus_resource_diagnostic_2026-10-08_phase245.json)。Phase246 将 Phase245 genus 资源诊断输出到独立 scratch path 重放，JSON 与原输出逐字节一致；该结果仅支持当前 host/input 的确定性，不证明跨环境或语义有效性。Phase242 记录的首个 Git snapshot 候选为 800 文件、240,040,154 bytes；当前仓库仍无已跟踪基线，sources 中包含 42,545,068-byte ACL 导出快照及多代候选库，需先完成逐路径发布 allowlist。Phase246 未 staging/commit、未迁移或删除文件。详见Phase246 报告及[机器记录](../sources/track_a_genus_resource_replay_2026-10-08_phase246.json)。Phase247 对首个 Git 快照的 812 个当时未跟踪路径（240,093,564 bytes）生成逐路径 SHA-256/大小/初步类别账本：405 个项目文件候选、200 个研究记录候选、58 个敏感复核项、9 个 legacy 文件、108 个派生输出与32个外部 corpus 快照。该账本不是内容审查完成的公开 allowlist；21 个文件命中 AAAI 2027/内部使用边界关键词，需逐文复核归属与可公开性。当前 Git 仍无 tracked file/commit，未 staging 或提交。详见Phase247 报告、[机器记录](../sources/repository_initial_snapshot_review_2026-10-08_phase247.json)与[逐路径清单](../sources/repository_initial_snapshot_path_review_2026-10-08_phase247.json)。Phase248 对 Phase247 标记的 58 个敏感路径做内部仓库筛查：未发现个人目录、邮箱或凭据赋值模式；21 个文件含 AAAI 2027/内部使用边界引用，作为内部材料保留，公开副本需逐项审核或脱敏。锁定配置仅引用被 `.gitignore` 排除的 answer key；一个测试 fixture 标记为 synthetic。此为模式/结构筛查，不是全面隐私、版权或许可审查；未 staging/commit。详见Phase248报告和[机器记录](../sources/repository_sensitive_path_review_2026-10-08_phase248.json)。Phase249 全文筛读 ACL 2026 SATQuest：CNF→五类 SAT 任务由 PySAT 客观核验，评测显式操纵实例、问题类型与题面格式。该先例收窄“verifier-backed 逻辑评测/多轴控制”宽泛新颖性；但其命题 CNF 与合成格式不含 WordNet sense/release、gloss-span 到 literal 支持或 AND/OR witness provenance。其 80-instance failure audit 由 LLM judge 标注、10% 人工抽查，不是 source-support gold。未来评测须将答案/证明正确与自然语言证据支持分开，并对 premise/rendering 条件配对评价。见Phase249报告与[筛读日志](../sources/literature_screening_log_2026-10-08_satquest_acl2026_phase249.json)。Phase250 对 137 份结构化筛读日志中的 2,036 条题名记录建立跨轮去重索引，形成 1,923 个保守簇、88 个多记录簇，并标记 3 个 DOI/年份冲突候选。该索引只用于日志导航与去重审阅，既有材料仍是多轮定向筛读，不构成系统综述候选分母、穷尽检索或新颖性证明。见Phase250报告与[机器索引](../outputs/phase250/literature_log_dedup_index.json)。Phase251 对最近工作矩阵中的 295 个外部链接出现项建立日志 crosswalk，285 个不同目标中 273 个精确回指结构化筛读日志；12 个目标未命中（7 个学术引用、5 个项目/代码链接）。此为引用可追溯性审计，不衡量调研覆盖度；FOL-Traces 只有标题级 `already_in_matrix` 记录，6 个其他论文引用需回查来源记录。见Phase251报告与[机器 crosswalk](../outputs/phase251/closest_work_log_crosswalk.json)。Phase252 全文筛读 GenProve（ACL 2026），将句级来源链接、Quotation/Compression/Inference 类型与人类 evidence-sufficiency 核验作为既有先例；其来源 triple 不是可执行 Horn 证明，也不包含 WordNet 义项/版本及 gloss-span→rule 绑定。补录后日志索引包含 2,037 条题名记录/1,924 簇，矩阵目标到日志的匹配升至 274/285，仍有 6 个学术引用无精确记录。见Phase252报告、[筛读日志](../sources/literature_screening_log_2026-10-08_genprove_acl2026_phase252.json)与[当前 crosswalk](../outputs/phase252/closest_work_log_crosswalk.json)。下方较早阶段记录用于保留审计历史；冲突时以日期较新的报告与机器记录为准。

Phase253 全文核对 WordNetGraph、Gulbe et al.、TROVE、FOL-Traces 和 Word Ladders；修正 Word Ladders 错误 Anthology 链接，并将“WordNet 定义→图→可解释蕴含”“gloss→义项词汇关系”“细粒度句级 provenance”“程序验证的 FOL 轨迹”记录为既有先例。矩阵 285 个不同链接目标中 280 个精确回指筛读日志；剩余 5 个均为代码/项目资源。139 份日志含 2,042 条题名记录/1,927 个保守簇。该 crosswalk 仅衡量书目追溯，不是检索覆盖或系统综述；sense/release-bound gloss-span→typed Horn 支持和 source-bound proof replay 仍属未验证假设。见Phase253报告、[全文筛读日志](../sources/literature_screening_log_2026-10-08_phase253_fulltext_addendum.json)及[机器 crosswalk](../outputs/phase253/closest_work_log_crosswalk.json)。

Phase180 仅刷新 EMNLP 2026 官方题录可用性：当前 accepted-paper 页没有可见论文条目，coverage 保持 pending；不把未命中解释为无相关研究。见Phase180。

Phase181 把环境复算从一次性静态快照变成仓库内可运行命令；当前 CI 矩阵和 import scan 仍是配置/源码证据而非运行级保障。外置 bundle 仍需独立 integrity replay，来源许可与项目发布 clearance 均未解决。见Phase181。

Phase182 核对 Goedel-Code-Prover（COLM 2026）后，宽泛的 proof tree、层次化分解和 kernel-checked proof 不再能单独支撑新颖性主张。作者任务从 Lean 规格开始，不含自然语言到规格的转译；项目尚无 gloss-span semantic gold 或 matched baseline。该筛读是单篇方法邻接证据，不产生项目效果或新颖性结论。见Phase182。
Phase208 定向筛读 COLM 2026 的 *To See the Unseen*：合成 definite/Horn 逻辑上的未见符号泛化已有近期主会先例，需将神经模型 OOD 泛化与 gloss-span→sense-specific relation support 分开。论文未提供 WordNet/gloss 语义 gold、来源证明或本项目 matched baseline；EMNLP 2026 官方主会页当前仍无可见论文条目，覆盖保持 pending。详见Phase208和[筛读日志](../sources/literature_screening_log_2026-10-08_colm2026_unseen_symbol_generalization_phase208.json)。
Phase209 在当前 Python 3.13.9 环境重新扫描 src/tests：140 个 Python 文件 AST 解析错误 0、未发现第三方顶层 import；inventory/归档/manifest 一致性 15 项全通过，但 `release_clearance=not_cleared_for_public_release`。这些结果不等于 CI 实际运行、全量 source payload 重哈希或许可清理。见Phase209。
Phase210 在当前配置 bundle 上全量重哈希 sense-index 引用的 115,235 个唯一 payload，全部匹配冻结 checksum，0 重复路径、0 畸形索引；新审计 JSON 与 Phase163 机器结果逐字节一致。此证据支持 bundle 字节复算一致，不支持来源清权或 gloss 语义蕴含。详见Phase210。

Phase211 定向筛读 NeurIPS 2026 目录列出的 FaithSieve，记录其 135 条双专家语义 gate 审计：13/20 条人审不忠实陈述仍被接受（FPR 65%）。这强化了独立 source-support gold 的必要性，但不改变项目数据、schema 或未确认的 Track A 方案；详见Phase211。

Phase212 核读 NeurIPS 2026 目录列出的 AutoformBot：26 本教材形式化为 45,000+ Lean 声明，并以 task/declaration dependency graphs 和 faithfulness/proof-integrity/code-quality rubrics 评估；一本文本的专家反馈记录占位 axiom 与源形式语句偏差。通用 source-linked autoformalization 与图辅助忠实度审计已有先例，但非 WordNet lexical baseline；项目仍缺 gloss-span gold 与 matched evaluation。SpecBridge 只找到题名，全文不可得，未作方法判断。详见Phase212。

Phase213 从当前 bundle 重跑 frozen hypergraph 与 minimum witness 两条命令，两份结果均与 Phase206 逐字节一致；closure、nodes/hyperedges 与全部 witness 证书通过。Basis deletion 复算仍显示 selected-witness descendants 在 66/85 情形高估 exact AND/OR closure loss。未重哈希全量 payload；结果不证明 gloss 语义支持或许可。详见Phase213。

Phase216 持久化了 127,380 条最小深度替代 clause→source document 映射，并新增 replay verifier 从冻结 graph/index/checksum 重建后逐行完全匹配。映射仅含确定性哈希键与 source payload checksum/byte count，不含明文路径、义项 ID 或 gloss；哈希为可与 bundle 关联的伪名，不是匿名化。此次只检查映射元数据，不读取 payload；payload bytes/identity 仍由 Phase215 的 37 个增量关联加 Phase199 基线支持。该结构和 payload 自洽性不等于 gloss 语义支持。详见Phase216、[机器记录](../sources/minimum_depth_alternative_source_map_2026-10-08_phase216.json)和[映射文件](../outputs/phase216/minimum_depth_alternative_source_map.jsonl)。

Phase215 遍历全部 110,340 个非 basis head 的 127,334 条最小深度替代 clause：每条均有来源文档链接，source-record/checksum 元数据无缺失；合并 Phase199 selected/compact payload 基线与本轮 37 个新增 payload 的 checksum/identity 核验后，全部替代来源关联均有字节及身份核验依据。单一 witness 的来源文档集合在 49 个 head 上小于全部替代 clause 的并集。该结果只补充来源 provenance 覆盖，不证明 gloss 语义支持、规则正确性或许可。详见Phase215与[机器记录](../sources/minimum_depth_alternative_source_audit_2026-10-08_phase215.json)。

Phase214 静态复核现有 NLI/证明路由：固定阈值精确二项校准的有限样本保证依赖 IID 单位、冻结模型/网格和稳定目标分布；唯一 group ID 不能证明 IID。严格导出绑定的是调用方声明的模型 revision 和文件哈希，不是推理执行 attestation。Phase176 核心实现哈希仍一致，Phase205 所记 Track A 双哈希与 edge/surface 缺口未变；设计备忘录仍未获批准，故没有迁移 schema。详见Phase214与[机器记录](../sources/nli_proof_route_contract_review_2026-10-08_phase214.json)。

Phase 153 的设计建议将主研究问题定为 raw-gloss spans 对义项绑定 relation edge/typed literal 的直接支持，将 exact-context NLI relation gold 作为各输入条件独立的次级结果；parent lemma surfaces 嵌套于 edge，target-sense 等权汇总，split 与不确定性按 lemma/sense/edge 连通组处理。由于当前 calibration gate 假设 IID dev groups，该协议要么开发经验证的 cluster-aware calibration，要么不声称其风险保证。首轮 noun-only 可避免未经审查的 58 条 verb hypothesis templates。建议细则见[Phase153设计备忘录](track_a_design_decision_memo.md)与深度报告；尚未锁定或实施。

Phase 154 补充指出 hierarchical selective-risk control 与 within-cluster dependence 不是同一问题。HG-CRC 的嵌套 group masks 在 IID calibration rows 上控制 group-conditional risk；当前 Track A 若保留 edge/surface/condition 嵌套，不能将其组成员资格直接称作独立 calibration units。项目在选定统计单位、聚合动作与 strict route 输出目标后，方可判断是否开发新的校准算法。见Phase154和[筛读日志](../sources/literature_screening_log_2026-10-08_hierarchical_group_risk_control.json)。

Phase 156 实现了实验性 annotation schema `0.7-draft`：显式自由 `target_variable`、多元正 Horn 方向安全条件、按生成规则裁剪的 sort map，以及 agreement v13 对齐。旧 schema 仍走共享变量 unary 路径；新 schema 未进入当前 v3 标注协议，也未运行测试、Datalog replay 或真实标注。行为/证书正确性须待运行级合成边界检查。详见Phase156报告。

Phase 157 对 0.7 下游 source-only proof path 做了静态调用链审计，修复多元 source fact 到 query target 的 AST grounding matcher，并将 pipeline 升至 `/12`。此修改尚未运行 proof/countermodel 或 bundle replay；锁定 blind v3 importer 继续输出 0.4，实验 schema 的 blind return/import round-trip 未实现。见Phase157报告。

Phase 152 对当前 v6 与 Track A 实现边界作复核：ACL v6 的精确 URL 日志匹配为 1,748/1,748；LoReFact 与 LREC 2026 OEWN adjectival-hypernym 工作已有全文筛读，Phase142 grounded-claim paper 则是与该候选快照一致的框外发现。CodeGraph 当前索引为 140 files、2,466 nodes、4,915 edges；静态调用关系确认旧 NLI export/validator 尚无 contextual premise path。四项 Track A 数据设计未裁决前，不生成新版 schema 或 pair。详见Phase 152 报告。

Phase 88 将 OEWN 2025+ 来源 profile 中六条候选记录的 `(ILI, definition_text_sha256)` 联合键唯一匹配至固定 JSON 归档记录。Phase 89–90 将六条 payload 结构性连接到图 head、11 条规则/hyperedge 与 selected witness；收紧到 selected witness 源文件时，只有 2/6 同时包含候选 payload 路径、匹配的 OEWN ILI/定义散列及相同定义文本 SHA-256。四条无此 selected-source 链的候选分为“仅非 witness clause”两条与“无 active-clause source path”两条。所有 crosswalk 都不构成自然语言正确性或全 bundle rights clearance 的证据。

Phase 91 对冻结 ACL Anthology v3 候选框（1,747 条，2016–2026）匹配全部 90 个结构化筛读日志：1,286 条至少有一项精确 URL 日志记录，461 条尚无全局匹配；显式全文 75、定向章节 134、摘要/元数据 851、深度无法确定 226。461 条全部来自 2016–2022，2022 年尚有 130 条。URL 匹配不代表相关性纳入、词族级覆盖、系统综述完成或全文阅读；详见Phase 91 报告。

Phase 92 筛完了 2022 年此前无日志匹配的 130 条候选：22 条保留为邻近工作、2 条为背景、106 条排除出核心综合；四篇做了官方 PDF 定向章节核查。全局对账更新为 1,416/1,747 URL matches、331 unmatched；2022 pending 为 0，余下未匹配项在 2016–2021。新增邻居显示 NLI tableau soundness/completeness、natural-logic proof paths、缺失前提的双向演绎/溯因验证、词汇语义网络与形式语法图整合均已有先例；Hypergraph Transformer 也限制宽泛超图新颖性表述。以上仍是单人 scoping，不能证明创新性或系统综述覆盖率。详见Phase 92 报告。

Phase 94 筛完 2020 年此前无匹配候选 94 条（29 邻近、3 背景、62 排除出核心综合），对六篇官方论文做定向章节核读。全框现为 1,595/1,747 匹配、152 未匹配，均在 2016–2019；深度分布为全文 75、定向 148、摘要/元数据 1,143、旧日志深度未明 229。Abzianidze 已将 NLI 标签监督的词汇关系学习接入 natural-tableau prover；Grits 已研究形容词到描述逻辑定义，WikiNLI 已自动构造 lexical entailment，PRover 已约束 proof graph，Goyal & Durrett 已做依存弧级 source support。项目需以 gloss-span→typed rule 的语义正确性和独立 replay 做窄化、匹配式验证，不能主张宽泛的“首次词汇关系逻辑证明/首次定义形式化/首次证明图”。详见Phase 94 报告与[全框快照](../outputs/phase94/acl_screening_coverage.json)；此结果不是系统综述或新颖性证明。

Phase 95 筛完 ACL 2019 未匹配候选 68 条（26 邻近、7 背景、35 排除），四篇官方 PDF 定向核读。全框更新至 1,663/1,747 匹配、84 unmatched，全部在 2016–2018。最直接先例 Prokhorov et al. 已从 textual definitions 生成知识图谱 hypernym/hyponym 路径，并用 attention 可视化路径节点对应输入词；E3 已从 procedural text 抽取规则并判断其是否被对话蕴含。因此 gloss→可解释词汇路径和自然语言来源规则抽取均不能作宽泛“首次”主张。可能的差异只能落在 gloss-span 级可审查归因、sense-aware typed Horn 语义 gold、source-only entailment 与独立 witness replay 是否联合成立并带来匹配评测增益。详见Phase 95 报告和[全框快照](../outputs/phase95/acl_screening_coverage.json)；这不是系统综述完备或新颖性确认。

Phase 96 筛读 2018 年未匹配候选 38 条（18 邻近、8 背景、12 排除），六篇官方 PDF 定向核读。全框为 1,701/1,747 匹配、46 未匹配（2016–2017）。直接近邻包括自然演绎证明学习短语对应、自然语言定义转 OWL 2 DL、WordNet/SUMO ATP 审计、词汇资源和手写规则模板用于 NLI、typed entailment graph 与短语/token 级关系标注。故宽泛的“首次定义形式化/首次自然演绎词汇证明/首次 WordNet 自动证明审计/首次 typed entailment graph”均不成立；项目组合假设须由 sense-linked gloss、精确 span、typed Horn 规则与独立 replay 的 matched gold 评测验证。见Phase 96 报告及[全框快照](../outputs/phase96/acl_screening_coverage.json)，不构成全领域新颖性证明。

Phase 97 筛读 ACL 2017 年最后 27 条无匹配候选（17 邻近、7 背景、3 排除），对 4 篇官方 PDF 定向核读。全框更新为 1,728/1,747 匹配、19 未匹配（2016 年）。Martínez-Gómez et al. 已通过监测不可证子目标按需加入词汇公理并继续定理证明；LangPro 提供自然语言 natural-logic tableau proof；Yanaka et al. 使用自然演绎 proof 特征建模语义相似度；Srivastava et al. 从自然语言解释联合学概念和解析。故不能主张首次按需词汇公理注入、透明自然语言证明或解释到概念学习。项目假设需验证 gloss-derived、sense-linked、span-attributed Horn 规则与 source-only entailment、独立 replay 的组合价值。见Phase 97 报告和[全框快照](../outputs/phase97/acl_screening_coverage.json)；候选框 pending 清零不等于系统综述完成。

Phase 98 筛完 ACL 2016 年最后 19 条未匹配候选（10 邻近、6 背景、3 排除），定向核读 5 篇；固定 ACL v3 框现为 1,747/1,747 URL 有结构化日志匹配，pending=0，全文75、定向167、摘要/元数据1,276、旧日志深度不明229。直接近邻包括专家标注构建领域 ontology/glossary、WordNet/SUMO 等资源映射事件 ontology、KG+逻辑规则联合嵌入，以及 gold textual entailment graphs。该 URL 覆盖不证明全 ACL 检索召回、深度筛读完备或系统综述完成。新颖性仍未证实，须转入 ACL 外引文追踪及 gloss-span→typed Horn→source entailment/replay matched gold 实验。详见Phase 98 报告和[全框快照](../outputs/phase98/acl_screening_coverage.json)。

Phase 99–101 在 ACL 固定框外追读 BMEAUT/4lang 的 2023 期刊后续，以及 BRISE 2021 原型和 LRE 2025 语料扩展。三者已排除“首次可解释定义图词汇蕴含”“首次 semantic-graph→formal-rule/prover”宽泛主张；BRISE 的早期 toy-set perfect result 与后续语料结果按版本和任务分别记录。它们不是 WordNet gloss matched baselines；项目的 sense/release-bound span support 与 typed AND/OR Horn replay 仍是待测假设。见Phase 99、Phase 100、Phase 101。

Phase 102 核实了逻辑实现边界：annotation compiler v5 仅编译共享单变量上的一元正谓词片段（sufficient 方向的 AND/OR 经最多 64 个 DNF 分支展开）；独立 typed Datalog validator/checker 可检查调用方提供的多元谓词签名及有类型证书/反模型回放，但并不生成 gloss 规则，也不认证签名本体或 source entailment。见Phase 102 实现范围审计。

Phase 103 全文筛查 de Jong et al. 的新近 AKBC 2026 接收论文 *Explaining Textual Entailment with Lexical Entailments*：其在 SNLI/SICK 上构建多参考 lex-NLI gold，并把 LLM 生成的词汇蕴含送入 LangPro；作者发现 proof coverage 增益常包含语义不可靠的词汇关系。该工作是结构化词汇解释+人工 gold+形式证明的强邻接先例（AKBC workshop，非 ACL/ICLR/NeurIPS 主会），但输入为 NLI 句对而非单条 WordNet gloss，也没有逐 literal gloss-span gold。不能再提出“首次结合结构化词汇蕴含解释、人工评测与 prover”的宽泛主张；项目的 gloss-source evidence 组合仍只是待验证差异假设。见Phase 103 报告和[筛读日志](../sources/literature_screening_log_2026-10-07_lex_nli_formal_proofs_akbc2026.json)。

Phase 104 静态审计确认，现有 `0.4-draft` annotation schema 没有给互斥的整套可接受分析建多参考分组；语义 OR 节点也不等于标注分析 alternatives。Phase 105 新增 `/0.1` 多参考 sidecar validator 与 scorer 原型；Phase 106 加入 micro/macro claim-set 指标，明确 complete-only exact denominator、unresolved 分母与空 claim 对处理；Phase 107 使评分 API 输出增加四个核心源码哈希及基本 Python runtime 指纹，CLI 另绑定输入文件哈希；Phase 108 将评分输出契约升至 `gloss-analysis-reference-score/0.2`，并将 scorer 实现标识升至 `/0.3`；Phase 109 禁止 `complete` sidecar 保留 unresolved candidates，将输入契约升至 `gloss-analysis-reference/0.2`，并将 scorer 标识升至 `/0.4`，避免未决分析进入已裁决评分分母。Phase 110 实现 gloss-review→OEWN relation-link hash/pair validator，并升级 hypernym replay summary 到 v3，将 query/report hashes 纳入对账；尚无人工 genus-sense mapping，代码未运行或协议锁定；旧 v2 replay 快照需重新生成才可供 bridge 使用。Scorer 不做抽样设计加权，不能据此估计 104,907 项冻结总体方法性能。研究评测和发布 gate 仍未完成。见Phase 104、Phase 105、Phase 106、Phase 107、Phase 108、Phase 109和Phase 110。

Phase 111 明确 genus span 的语义须由人工裁决，并收紧非空白 span 结构约束；Phase 112 要求 bridge 输入由外部 SHA-256 锁定的 candidate manifest，复用既有 validator 校验 sidecar/manifest 一一对应；Phase 113 新增 bridge row 与 validation report JSON Schema，并要求 bridge candidate 集合完整覆盖 sidecar 候选集，避免 unresolved mapping 静默离开分母。Phase 111–113 的新逻辑、schema 和 CLI 均未运行验证；尚无人工 genus-sense mapping、标注回传或 bridge 实证。详见Phase 111、Phase 112和Phase 113。

Phase 114 的官方 ACL 2026 词汇关系检索大多命中既有条目，没有新增 direct baseline；官方 proceedings 目录显示 ACL 2026 long papers 达 2,223 篇，确认项目 1,747 行 ACL v3 仅为跨年检索候选框而非 proceedings census。该小规模去重不估计 recall 或证明 novelty。见Phase 114和[机器日志](../sources/literature_screening_log_2026-10-07_acl2026_lexical_relation_dedup.json)。

## 当前就绪判断

项目状态文档记录 Phase 86 曾有 247 项 `unittest` 回归通过；这不是当前 checkout 或 Phase 111–113 改动的验证结果。NLI 内容效应 evaluator 当时仅由合成记录验证，不读取真实 gloss/模型导出，也不进入严格 proof route。项目已有固定资源结构审计、witness/Datalog 交叉回放、有限正 Datalog/typed replay 与 NLI calibration/export gate 原型；这些只证明程序范围内结构/逻辑及输入身份，不证明自然语言释义忠实支持规则。

| 目标面 | 当前有证据的状态 | 尚缺的关键证据 |
|---|---|---|
| 冻结超图与 witness DAG | 固定 bundle 的结构统计/证书重放已多阶段复算；Phase 175 现态重放核对 110,425 heads、154,206 clauses、917,767 literals、85 basis，closure 与全部 witness 结构验证通过；最小深度 witness 全部重放有效。Phase 76–77 对 OEWN `instance_hypernym` 作独立资源内验证与 320 条压力复放 | 不能外推到 gloss 真值、义项判定或开放世界；尚缺独立第三方实现交叉复算及语义 gold |
| WordNet gloss → 规则 | 多版 annotation schema、span/source-record validator、受限 AND/OR→正 Horn compiler；v5 只支持共享单变量上的一元正谓词，sufficient 方向最多展开 64 个 DNF 分支。Phase105 有独立多分析 sidecar validator/scorer 原型 | 无真实标注 gold/IAA；0.4-draft 未显式表示整套备选分析；多参考接口未运行验证/协议锁；通用 validator 不生成 gloss 规则，签名与 sort hierarchy 也不是经来源审定的 WordNet ontology |
| 蕴含与 NLI | Datalog checker 可对调用方提供的正 Datalog 程序做证书/反模型构造与回放；typed 模式绑定显式签名表 hash；另有 source-only source-record gate、dev/test hash export gate及 Phase 86 描述性内容效应诊断工具 | 无冻结模型预测、真实校准 gold、matched baselines 或端到端 gloss-entailment 评测；逻辑证书只证明相对于给定程序/签名表的形式结论，不等于 source text entailment |
| 人工 pair study | Phase 78 text-free 320 candidate IDs；pair schema 0.2-draft、SAP 与 Phase 83 finite-population 区间原型 | `annotation_preregistration_v3_lock.json` 仍为 `protocol_signed=false`、外部注册为空、`distribution_authorized=false`；截至本快照没有标注回传。pair study 的方法/许可/标注负担仍未冻结 |
| 数据来源与发表 | AAAI 2027 匿名稿明确标注为非用户成果，仅作受限内部定位对照 | release/bytes/许可逐源清查未完成，`release_clearance` 未定；不可据此准备对外分发文本/稿件 |
| 新颖性与相关工作 | 近邻包含 COLLIE-V、BMEAUT/4lang、BRISE 图规则/prover、WordNet-NLI、lex-NLI (AKBC 2026 接收)、LSEG 推理时 NL2FOL 纠偏与近期 ACL/ICLR/IJCAI/COLM 工作；Phase 98 ACL v3 框为 1,747/1,747 URL 匹配（全文 75、定向 167、摘要/元数据 1,276、深度未明 229）；Phase 99–103 追读 4lang、BRISE 与结构化 lexical explanation 线 | URL 对账不等于全文/摘要筛读完备或全领域召回；ACL 外仍是定向追踪，尚未运行 BMEAUT/4lang matched adaptation、COLLIE-V induction、Greco-style direct-LLM baseline 或 lex-NLI 风格 gloss 适配；共同 adjudicated gold、IAA 和 source-support 结果缺失，组合差异及新颖性仍未验证 |

这次全局状态审计的底稿见Phase 87 深度报告。AAAI 2027 的作者归属边界见[定位备忘录](research_positioning_and_prior_work.md)。

本快照的整体阶段判断见阶段性深度分析报告、Phase 32 深度分析及Phase 33 深度分析。Phase 28 增加 `route_pipeline_batch_from_export` 编排接口，但项目仍无真实 annotation returns、校准 NLI gold 或端到端匹配评测；新增 API 不改变下表的实证状态。Phase 32 完成固定 v3 中 2024 `definition_to_formal_logic` 词族日志覆盖，Phase 33 又对两篇 2026 formal NLI/proof-tree 候选作官方 PDF 定向筛读。当前全局 exact-URL 对账为 565/1,747，待题名/摘要筛查 1,182；深度计数为全文 56、定向章节 52、摘要/元数据 305、未明 152。详情见[Phase 33 日志](../sources/literature_screening_log_2026-10-06_acl2026_proof_and_formal_nli.json)及[Phase 33 reconciliation](../sources/acl_screening_reconciliation_2026-10-06_phase33.json)。

Phase 35 静态范围审计确认现有 compiler 仍是一元正 Horn/Datalog 原型；Phase 36 增补两篇 ICML 2026 摘要级跨会场背景工作，未改变 ACL v3 reconciliation 或实证缺口。详情见Phase 35与Phase 36。

工程与语义证据边界按当前实现进一步列在[Source-only 证据链契约](source_only_evidence_contract.md)及Phase 34 静态审计报告：certificate replay、source payload hash/sense/gloss match 和 AST span coverage 各支持窄的结构/身份声明，不能替代人工 gloss-support gold、权利/归属审查或匹配实验。

Phase 39 重核发布 inventory 与本机 OEWN/frozen bundle 一致性，并确认 source-level release clearance 仍未评估、annotation protocol/distribution authorization 未满足；详见Phase 39。Phase 40 在 IJCAI 2026 官方 proceedings 中定向筛读两篇：VANESSA 已组合 textual entailment、符号推理和 proof tree；NRI 已展示 proposition-level DNF induction。它们降低宽泛 pipeline 与规则归纳 novelty claim 的可信度，但不是 glossary source-support baseline，也不改变无人工 gloss-support gold、无 matched evaluation、无发布授权的实证状态；详见Phase 40和[结构化日志](../sources/literature_screening_log_2026-10-06_ijcai2026_logic_neighbors.json)。

Phase 41 静态复查确认 source-record verifier 已把 annotation path/hash 声明与冻结包锁、sense index、payload bytes/checksum 和精确 gloss 字段绑定；失败诊断日志早于当前测试文件修改，因此当前回归用例状态未知，本轮没有运行测试。该 verifier 仍不证明上游 release/许可、规则语义支持或人类裁决正确，详见Phase 41。Phase 42 对 IJCAI 2026 官方 proceedings 做了全目录标题级补筛，没有发现 VANESSA/NRI 之外显眼标题命中；这不构成全摘要/全文审查或新颖性证据，详见Phase 42及[筛查记录](../sources/ijcai2026_title_screen_audit_2026-10-07.json)。

截至本次状态复核，`config/annotation_preregistration_v3_lock.json` 仍记为 `protocol_signed=false`、`external_preregistration_id=null`、`distribution_authorized=false`，标注回传文件为 0。这里只核对 lock 字段和回传文件名数量，没有运行 text-free preflight；blind task/answer key 继续限于本地内部使用，不能据此启动外部分发或正式标注。

Phase 43 更新了 GCIDE 0.54 与 MeSH 2026 的官方版本/复用条款页面证据，未完成 payload-to-release bytes 绑定、来源内容第三方材料审查或具体发布方案判断；不改变 `release_clearance=not_assessed`。详见Phase 43与[来源证据 JSON](../sources/source_release_rights_evidence_2026-10-06.json)。

Phase 44 查明 NCI 专用 NCIt 条款页声明 CC BY 4.0，并记录商标限制与官方发布格式/版本信息。OLS 聚合记录仍未映射到精确 NCIt release、序列化和字节，故不改变 `release_clearance=not_assessed`。详见Phase 44。

Phase 45 定向核读 ACL 2026 RGCWM，确认通用规则依赖图、规则状态和结构传播已有强主会邻居，进一步收窄 novelty framing。该工作不提供 WordNet gloss-span semantic gold 或可重放的 source-only Horn proof；本项目剩余差异仍是假设，需系统检索和 matched gold 实验验证。详见Phase 45。

Phase 47 修正了评测协议中过时的 schema 描述：NLI 三分类已进入独立 `claim-review-record/0.1` sidecar，canonical annotation `0.4-draft` 仍存独立的 gloss-support 标签。字段合同现在与现有 schema/exporter 一致；仍无真实标签回传或标注授权，详见Phase 47。

Phase 48 对冻结 source-record 索引的 115,235 行作字段集合聚合，确认索引层没有显式 provider/release/version/format/license 字段。此结果不能外推到索引指向的 payload；OLS/NCIt 版本绑定与 `release_clearance` 仍未解决。详见Phase 48。

Phase 49 将主要研究假设明确为同一人工 source-support gold、隔离切分和相同预算下的风险—覆盖增量比较，并为结构保留和证据/回放辅助写出可证伪的次要假设。当前无 gold、无 matched 结果，所有假设仍未验证；数值判据需在合法 pilot 后、test 标签揭示前预注册。详见Phase 49与[评测协议](claim_verification_evaluation_protocol.md#可证伪的研究假设与判据预注册前草案)。

Phase 50 把 Phase 24 的 90 个 aggregate source profiles 与权利证据日志按 source label 精确交叉；17 个 profile 组合、2,326 个 profile payload 计数有同标签日志项，73 个组合仍是字面未命中（其中可能包含别名）。此结果只是 crosswalk 可定位性，不是清权比例。Phase 23 的 payload 字段扫描和 Phase 48 的 index 字段扫描范围不同：payload 有来源/版本线索，索引本身仍无这些身份字段。具体 release/bytes 映射和兼容性未解决。详见Phase 50。

Phase 51 基于当前官方页面，为 OEWN 2025+、English Wiktionary 和 ChEBI 三个明确画像标签补入资源家族证据，crosswalk 变为 20/90 个 profile 组合、2,334/3,595 个跨 profile payload 计数可精确定位。页面级 terms 仍未绑定到候选 payload 的具体 bytes/entry/release；其他来源别名未审，不能解释为清权覆盖。详见Phase 51。

Phase 52 对 `local_go-basic.obo_snapshot` 和 `v5_local_snapshot` 补查 GO/IUPAC 官方版本与许可说明；更新 crosswalk 为 22/90 个画像组合、2,343/3,595 个 profile payload 计数精确匹配。具体 GO 日期 release、IUPAC term identity/revision 和 payload bytes 仍未绑定；清权状态不变。详见Phase 52。

Phase 54 对 Phase 24 最大的非规范来源画像簇做字段形状与 host 抽取，确认 1,202 条非规范 `source` 值均为字符串，受控 URL parser 未恢复 host；其中 1,079 个 profile payload 计数只有 hash-shaped version 且无 `download_url`。这不足以判断字符串内实际内容，故整体仍 unresolved；不对外分发或套用来源许可。详见Phase 54。

Phase 55 对 COLM 2026 官方 accepted-papers 列表中三篇近期方法邻居做定向全文筛读：组合式 claim falsification、logic-preserving difficulty search、以及 symbolic validity/semantic grounding 分轨。它们进一步限制了宽泛贡献表述，并提示需加入组合 hard negatives、语义保持压力测试及 verifier coverage/fallback 报告。筛读不改变 ACL v3 计数，也不构成 matched evaluation、新颖性判断或系统综述；项目依然没有可授权的 gloss-support gold 或匹配实验。详见Phase 55及[筛读日志](../sources/literature_screening_log_2026-10-07_colm2026_compositional_verification.json)。

## 按研究目标核对

### 核心假设判定门

| 假设 | 当前可查证证据 | 下一项必要证据 | 失败/不可判定解释 |
|---|---|---|---|
| H1 source-only 端到端路线在相同覆盖/风险下优于预先指定基线 | 有三轨道协议、route/proof replay 工程和候选标注设计；无回传标注、semantic-support gold 或 matched baseline 结果 | 许可与归属清理；协议/候选 manifest 锁；盲标裁决；同候选、同预算、group-disjoint 的强基线比较 | 有足够精度而未达到预注册主效应判据，则收窄/撤回增量主张；gold、权利或比较不齐则保持不可判定 |
| H2 保留 AND/OR 能改善整体规则/方向判断 | 固定快照有结构消融；只证明该图中的结构/深度差异，无 gloss gold | 在裁决 claim 上与预定义压平基线比较 exact formula、方向错误和 unsupported entailment | 仅 replay 或结构计数差异不支持语义收益；无人工 gold 则不能识别 |
| H3 span/回放帮助人工审计 | 有 span/schema/独立 replay 接口设计；无盲化人审对照 | 盲化带/不带证据界面的审阅实验，报告定位耗时、错误接受及标签一致性 | 只证 verifier replay 成功不代表审阅体验或判断更好 |

| 目标层 | 当前可查证证据 | 状态 | 仍缺的关键证据 |
|---|---|---|---|
| 审计冻结超图、AND/OR 结构与 witness DAG | [冻结包审计](../outputs/phase6/frozen_hypergraph_audit.json)、[最小深度审计](minimum_witness_audit.md)、[basis 支持包络](global_minimum_witness_basis_support.md)、[来源链审计](selected_witness_source_lineage.md)、[压平消融](flattening_ablation.md) | 对锁定快照的结构属性、所选 witness 及来源引用已有多项可重算分析；这些对象不是语义 gold | 需逐项固定数据版本与上游归属映射；需要 source-span→规则语义支持人审后，才可讨论图规则是否忠实于释义 |
| 关系/上下位校验 | [Phase 16 producer/replay](../outputs/phase16/oewn_hypernym_verification.json)、[Phase 118 producer](../outputs/phase118/oewn_hypernym_stress_v1_verification_v2.json)、[Phase 118 replay v3](../outputs/phase118/oewn_hypernym_stress_v1_replay_v3.json)、[Phase 119 合成 bridge fixture](../examples/synthetic_gloss_oewn_bridge/README.md)、[claim verification protocol](claim_verification_evaluation_protocol.md)、[bridge validator](../src/analysis/verify_gloss_oewn_relation_links.py)、[bridge schema](../config/gloss_oewn_relation_link.schema.json) | Phase 118 结构压力重跑 360 条、独立 replay v3 为 valid/0 errors；Phase 119 用一条显式 synthetic sentinel fixture 跑通 candidate freeze→producer→replay→bridge，并确认错误 manifest pin 会 fail closed。Schemas 与实际合成 fixture 均通过校验。上述均为工程契约证据 | 真实、获授权的人审 mapping 和 bridge 端到端研究数据仍缺；没有人工 sense-relation 与 gloss-span directional-support gold；压力集不是准确率样本，资源闭包外不等于语义反例 |
| Gloss→形式规则 | [annotation schema/protocol](annotation_protocol.md)、[受限 Horn compiler](logic_verification.md#标注-ast-datalog-受限编译器)和 [compiler 实现](../src/logic/annotation_to_datalog.py) | 人工提交的 AST 可经 schema 校验后编译为限定正 Datalog；编译拒绝条件已包含支持标签、置信度、方向及 schema 0.4 的 `inference_basis` | 尚无经人审并双标的 WordNet 形式化 gold；尚无从自然语言 gloss 自动生成 AST/变量/作用域/有类型规则的已验证端到端系统；编译可执行不证明规则忠实 |
| 蕴含/证明与 NLI | [reviewed pipeline](../src/logic/verified_reasoning_pipeline.py)、[Datalog checker](../src/logic/datalog_checker.py)、[source-record verifier](../src/logic/source_record_verifier.py)、[NLI 评估协议](logic_verification.md) | 有限正 Datalog 证明/反模型回放、fact 与规则到 test sense/gloss 的哈希绑定、NLI 校准及拒答接口已实现；source facts 需绑定到同 sense/gloss、已裁决且 supported 的 gloss atom，并通过 AST 论元逐位 ground-match 与 target-variable/query binding；fact source paths 与引用标注的 source-record paths 交叉核对；certificate replay 核对 claim refs；Phase 26 verifier 已接入组合路由并可复用 bundle context；Phase 28 增加 `route_pipeline_batch_from_export`，统一编排逐条严格路由并摘要输入 hash；compiler `/6`、pipeline `/13`，Phase160 报告重算 typed-program validation | 尚无真实 annotation returns 可实际复核；上游确切发行版、许可、来源标签真实性与人类裁决正确性仍未独立核验；无真实冻结模型预测、人工 gold、同切分 matched baseline；strict export 的 manifest SHA 仍须外部固定且模型运行真实性仍需审计；批量 API 当前逐项重验 dev/test 文件，未测性能；无论文级性能结论 |
| 人工确认性标注 | [v3 抽样框/设计](annotation_study_design_v3.md)、[预注册草案](annotation_preregistration_draft_v3.md)、`config/annotation_preregistration_v3_lock.json` | 400 条、24 层候选任务框；raw gloss 与 OEWN 2025 Plus cross-check 为 400/400，effective definition 精确匹配为 376/400。2026-10-06 重跑 text-free preflight：integrity pass，输入哈希、frame/manifest、400 项覆盖与 24 strata 全部通过，尚无回传；这些仍是候选材料而非标注结果。当前 κ 目标限于两位固定标注者 pair | 当前 lock 明示 `protocol_signed=false` 与 `distribution_authorized=false`；preflight 虽通过仍不授权外发。无双人回传、裁决或一致性系数。800 次预定 item-level 标注的负担未试标；任务顺序问题已在设计/代码层推进：版本化 SHA-256 计数器 Fisher–Yates plan/exporter 已生成 2 个本地 draft preview views（400 项/槽）；manifest SHA-256 `e8709e907a1950aad989f69978f20cb45ef94bcabe7b6205c4e1072b9e821222`，并绑定算法/生成器源码 hash。它们未锁入 preregistration，且不是 frame 外工作量试标；尚无外部呈现或 slot—annotator 受限映射。还需完成人工协议审阅、固定版本哈希、来源许可/归属审核、标注者/裁决者安排及明确的分发授权 |
| 相关工作与新颖性 | [相关工作综述底稿](related_work.md)、[逐项对照](closest_work_comparison.md)、[检索协议](literature_search_protocol.md)、[v3 查询扩展审计](../sources/acl_query_expansion_audit_2026-10-06.json)、结构化筛读日志 | 已覆盖多轮 ACL Anthology/其他官方来源检索及 2026 近期邻近工作；2026-10-06 全文核读 COLLIE-V/BMEAUT，并筛查固定 ACL 候选库 2016–2019（82 条）、2021–2022 与 2023 切片，发现定义语义角色、definition-augmented NLI、释义数据增强和关系获取等先例；新增核读 Greco et al. (Findings EMNLP 2024)，其 WordNet gloss-conditioned 方向性 lexical-entailment 任务应作为直接 LLM baseline 候选；NeurIPS 2024 KGD-L 将 WordNet definitions/hyponyms 编为用于检测适配的语言知识图，作为跨域图构建先例；新增筛读 SemEval 2026 Task 5 的 GuysLLM 与 SemTechLab/HINTS，纳入 graded sense-plausibility 的 NLI/span 特征候选，但任务不是 gloss source-support；全文定向筛读 NAACL 2025 Code4Logic，确认 code-mediated NL→FOL 与 prover/downstream logic 已有先例；全文定向筛读 Findings EMNLP 2025 FOL Closeness Metrics，纳入受控公式扰动和 metric sensitivity 设计，同时明确其 LLM-judge 对齐不是 source-support gold；全文定向筛读 Findings ACL 2025 Disambiguate First, Parse Later，确认 ambiguity-first interpretation coverage 与分阶段 semantic parsing 已有先例；另全文筛读 ACL 2026 contract-checked reasoning DAG，排除 DAG+结构 gate+证书作为充分创新点；新增 ICLR 2026 CRAMF 与 Mathesis 两篇全文定向筛读，确认定义检索增强 autoformalization 及形式检查/语义评估/证明分层已有数学领域先例 | 目前仍是定向 scoping；ACL v3 关键词候选框扩展为 1,747 条；Phase 29 新日志 reconciliation 后有 447 条精确 URL 日志匹配（56 全文、35 定向章节、204 摘要/元数据、152 深度未明），另 1,300 条待题名/摘要筛查；基线 v3 audit 的 443/1,304 是 Phase 29 前快照，当前重算见 [reconciliation 记录](../sources/acl_screening_reconciliation_2026-10-06_phase29.json)；其中新增 ACL 2026 形式化主题切片 24 条题名/摘要决定，10 条做了官方 PDF 定向章节复核，均非全文/附录穷尽阅读。新增词族追回 Logic Haystacks、ETS、Counting-Stars 等已知漏检项，但不构成召回率证据。2016–2019 的 78 条保留记录中，3 篇做了针对性全文核读，其余 75 篇只有题名/摘要筛查；2023 的 11 条保留记录均只有摘要筛查；另有未匹配候选与跨库空白。COLLIE-V induction、BMEAUT matched adaptation、Greco-style direct-LLM matched evaluation 与 SemEval-style graded plausibility adaptation 均未运行，未形成共同 gold 上的 baseline；缺少完整跨库、可复现纳排与最终 novelty audit；未证明研究假设新颖 |
| 开源与可复算 | [CI 工作流](../.github/workflows/tests.yml)、[CI 说明](continuous_integration.md)、[发布门槛](data_release_gate.md)、[来源元数据审计](../outputs/phase23/source_release_metadata_audit.json) | CI 配置在 Ubuntu 上覆盖 Python 3.10–3.13，在 Windows 上覆盖 3.10 和 3.13；phase 23 报告冻结包来源 payload 完整性锁有效且 source-level rights 未评估 | 本快照没有 CI 运行结果；当前不执行测试套件。仓库无项目代码许可；冻结包、任务/答案键和带身份的结果不能因哈希正确或上游某个版本开放而默认公开 |
| 新论文归属及增量 | [定位备忘录](research_positioning_and_prior_work.md) | 已明确 AAAI 2027 匿名稿不是用户成果，仅作为内部 prior-work 对照 | 需取得可使用既有稿件/数据的授权和版本对照；新贡献须由独立问题、同数据基线与人工 gold 支撑，不能把既有结构审计重新包装为新论文贡献 |

### 2026-10-06 ICLR 2026 ProofFlow 增量

定向筛读 [ProofFlow](https://proceedings.iclr.cc/paper_files/paper/2026/hash/5fce5198dbf92d5ff45f74504431e2ff-Abstract-Conference.html) 后，相关工作状态增加一项已核官方全文的方法近邻：proof-step dependency DAG、结构约束消融、syntactic/semantic/structural composite score 及人工核验 benchmark 均已有数学 autoformalization 先例。因此任何“依赖 DAG + 形式化忠实度验证”宽泛主张必须降级或改写为对象明确的研究假设。它与本项目 gloss-derived AND/OR Horn 及 source-span semantics 不同，但这只是任务边界，不是已证新颖性；须共同 gold 与 matched experiments 验证差异价值。筛读记录：[结构化日志](../sources/literature_screening_log_2026-10-06_proofflow_iclr2026.json)，[逐项对照表](closest_work_comparison.md)。本增量不改变无独立 WordNet source-support gold、无 matched baseline、无已证新颖性及未清权的总体结论。

## 发表前的依赖顺序

1. **先冻结合法来源和归属边界**：确认既有材料可用于内部研究的范围，逐来源评估 release/version/license/attribution；在明确授权前不向外部标注者发送任务或答案键。
2. **完成协议审阅和预注册锁定**：审定 `inference_basis` 标签、判例、source-span 规则、双标/裁决流程、拒答和偏离处理；再固定 schema、validator、抽样框、盲标包与分析器哈希并签署/注册。
3. **取得有效独立标注与裁决**：分别保存两位标注者原始记录和裁决记录；验证完整回收，不对无效/非应答样本静默删项；报告各标签分布、设计权重、适用的区间、协议偏离与一致性。
4. **锁定 matched baselines 后评测**：同一 sense/lemma/source split、候选和预算上比较资源标签、词面、sememe/定义模型、直接 NLI、LLM 逻辑化与规则/proof 路线；分开报告关系正确、gloss-span support、逻辑/类型正确、proof replay、NLI 指标、拒答/覆盖与成本。
5. **更新系统检索并审查贡献独立性**：用最近候选池和专业数据库补完定向筛读，保留逐篇排除理由；逐项对照 AAAI 2027 既有主张和公开方法。若没有 gold、直接对照和归属证据，论文中的效果/新颖性只能写成假设，不能写成结论。
6. **发布前进行独立干净环境复算**：在不含本地忽略缓存/私有冻结包的 checkout 上复算可发布结果，逐文件复核代码许可、数据许可、归属和输出提取风险；只有实际 CI 与复算日志通过后才报告发布就绪。

## 当前最关键的断点

结构分析和证明对象已有较多固定快照上的工程验证；最限制下一步论文证据的不是再加一条图指标，而是：**获准且可审计的 sense-linked gloss 标注 → 独立 source-support gold → matched baseline 与错误分析。** 在这个证据链建立前，项目可以报告资源相对结构结果、接口边界和研究假设，不能声称从 WordNet 定义学到了有效知识、改善了蕴含/上下位判断，或已经找到新颖贡献。

2026-10-06 Findings ACL 2026 框外补查：官方全文筛读 Qiu et al., *Pause or Fabricate?*。GRIL 的缺前提检测和 pause/clarify 训练是一般推理边界控制先例；不能替代 WordNet gloss-span support、NLI gold 或 source-only proof/countermodel。论文在冻结 ACL v3 候选框外，通过 ACL Anthology 定向检索发现；不修改 1,747 候选框计数或召回结论。研究边界与全文/附录筛读范围见 [补充综合](latest_related_work_addendum_2026-10-06.md) 和 [结构化日志](../sources/literature_screening_log_2026-10-06_gril_findings_acl2026.json)。
### Findings ACL 2026 SLKD 增量

Bi et al. 的 [SLKD](https://aclanthology.org/2026.findings-acl.436/) 以 LLM 逻辑分解、AND/OR/NOT 操作符数与嵌套深度构造自然语言推理样例的密度 proxy，并用于逻辑基准上的 SFT/RL 训练样本选择。它是逻辑结构复杂度/拓扑评分的近期先例；作者明确指出分解噪声、有限模型族与跨域适用性限制。对本项目的审计结论是：冻结 hypergraph 的 depth/OR/AND 统计只描述给定图结构，不能单独当作 gloss support、语义难度或创新证据。论文不在冻结 ACL v3 候选框，筛读记录见[机器日志](../sources/literature_screening_log_2026-10-06_slkd_findings_acl2026.json)与[补充综述](latest_related_work_addendum_2026-10-06.md)。


当前形式化实现范围补记（Phase 35）：annotation compiler v3 仍是共享单变量的一元正 Horn/Datalog 原型，validator 没有 predicate-signature/argument-sort type checker；checker 的 arity consistency 不是类型检查。故文献定位中“typed AND/OR Horn”仍是未来研究假设。类型扩展门槛和分层评测要求见[Source-only 证据链契约第 5 节](source_only_evidence_contract.md#5-已有与待完成的-typed-horn-能力)。
2026-10-06 Phase 36 跨会场补查新增两篇 ICML 2026 摘要级背景工作（attention 图谱式推理验证；形式验证驱动代码生成）。它们不构成 WordNet gloss source-support 直接基线，未改变 ACL v3 计数或本审计对人工 gold、许可和 matched evaluation 缺口的判断。详见阶段报告和[筛查日志](../sources/literature_screening_log_2026-10-06_icml2026_verification_supplement.json)。



Phase 37 跨会场工作进一步区分模型内部 reasoning topology 与 KG prior/path constraint 两种路线；它们都没有提供 WordNet gloss-span source-support gold 或 source-only replayable Horn proof。Phase 38 则把资源关系 verifier 从 3 条 smoke claim 扩展为 360 项九层 deterministic stress frame，修复 replay 暴露的 self-link `child_pos` 缺失，并获得 `valid=true`、0 errors 的独立重放。两轮都不改变 ACL 候选对账，也不弥补当前 semantic gold/许可/matched-baseline 缺口。详情见Phase 37 报告、Phase 38 报告及[Phase 38 机器记录](../outputs/phase16/oewn_hypernym_stress_v1_manifest.json)。




Phase 56 对冻结 ACL 2026 NLI/逻辑候选子集的 58 条完成题名/摘要筛读，26 邻近、2 背景、30 排除；对 CARENLI、Ghost Context、FactAppeal、COMPACT、SciClaimEval 五篇官方全文作定向章节核读。精确 URL 日志匹配从 565/1,747 增至 623/1,747，待筛 1,124；此计数是日志覆盖而非相关工作纳入或系统综述数字。全框仍有 1,124 条无精确匹配，本轮未解决新颖性、source-support gold、许可或 matched baseline 缺口。详见Phase 56和[逐条日志](../sources/literature_screening_log_2026-10-07_acl2026_nli_logic.json)。


Phase 57 完成 2026 年 `graph_rule_provenance` 剩余 117 条题名/摘要筛查，定向核读四篇官方全文；结合 Phase 56 的 58 条 NLI/逻辑候选，本 ACL Anthology 2026 固定候选框 295/295 均有精确 URL 日志匹配。全框总匹配 740/1,747、待筛 1,007；深度为全文 65、定向章节 52、摘要/元数据 471、先前未明 152。URL 匹配不是相关工作纳入数或系统综述完成。超图检索、graph evidence retrieval、citation 和 span annotation 均已有先例，但都不能替代 sense-linked gloss support gold 或可重放证明；核心新颖性/效能仍未证实。见Phase 57 报告。


Phase 58 对 2025 年 graph/rule/provenance 余下 133 条逐篇题名摘要筛查，定向核读十篇官方论文。发现 LORex（ACL Findings 2025）直接在 WordNet taxonomy 上结合节点定义和层级路径做父节点扩展，应列为优先 taxonomy baseline；FOL/Horn tree-rule refinement 和 graph-constrained logical parsing 也有先例。当前全框 exact-URL 命中 873/1,747，待筛 874；2025、2026 年均全量 URL 匹配，但匹配不表示全文阅读或相关工作纳入。新颖性、source-support gold、许可和 matched comparison 均未解决。见Phase 58。

### Phase 59 文献边界更新（2026-10-07）

ACL 2024 的来源归因与 NLI 邻居已进一步收紧宽泛主张：Post-Hoc Answer Attribution 以 textual entailment 选择回答来源，Provenance 将 NLI factuality 判断回溯至 RAG context chunks，SPEH 已在 entailment trees 中研究步骤可行性与纠错；claim-level factuality 也有 INFUSE、TWEAK、FENICE 等评估参照。逐条证据和对照见Phase 59 报告。

因此当前仍未建立的研究证据不是“是否有 NLI/来源归因/证明树”，而是同一 sense/release-bound gloss 上、每条 typed AND/OR Horn literal 的裁决级 source-span support，以及独立 replay 与 matched baseline 是否带来可测价值。该差异仍是假设：无双人裁决 gold、无 IAA、无匹配分数；不能表述为新颖性或有效性已证实。固定 ACL v3 对账为 957/1,747 exact URL matches，剩余 790；日志匹配深度分布为全文 75、定向章节 62、摘要/元数据 594、深度未明 226。

### Phase 60 文献边界更新（2026-10-07）

ACL 2024 近邻补查发现，FRVA 已将事实检索/核验与双向 entailment tree 组合；Iokawa & Yanaka 已在视觉文本蕴含中使用 WordNet 词汇注入与 FOL 模型检查；Lean theorem proving、失败路径回溯、claim/source attribution 也有明确先例。详见Phase 60 报告。因此“WordNet + formal entailment”“retrieved evidence + proof tree”“可执行 prover 验证”不可独立作为新颖性主张。

研究差异仍需限定在可实测合同：sense/release 对齐、每个 typed Horn literal 的 gloss-span support、AND/OR completeness、source-only witness replay，以及共同盲测 gold 上的 matched baselines。当前无该 gold、IAA 或 matched 结果；未证实的部分应继续标记为假设。ACL 固定框当前 993/1,747 exact URL 匹配、754 pending，深度分布 75/70/622/226（全文/定向/摘要元数据/深度未明）。

### Phase 61 文献边界更新（2026-10-07）

ACL 2024 图/规则词族补筛发现 ClaimVer 已提供 claim-span 级 KG evidence attribution，TRACE 已从检索文档构造知识图推理链，复杂逻辑查询、KG rule embedding、KG traversal 与可验证解释也均有先例。故“claim attribution”“graph evidence chain”“rule reasoning”“可解释路径”均不能独立支撑 novelty。细节见Phase 61 报告。

要验证的窄假设需区分 claim-span 与 evidence-span：项目要求标注的是规则依赖的原始 gloss span，并将 sense/release 对齐、literal 支持、AND/OR 完整性、proof replay 独立测量。当前无 adjudicated gold、IAA 或匹配结果。ACL v3 进度 1,093/1,747 exact URL 匹配，654 待筛；深度 75/80/712/226。

### Phase 62 文献边界更新（2026-10-07）

ACL 2023 补查发现，self-supervised relation-rule learning 已将文本逻辑 triple predicate 映射到 KG relation/path；WordNet–SUMO meronymy correction 已以 FOL ATP 检查资源关系；LLM semantic parsing + ASP/FOL solver 也已有多个系统。这些先例进一步否定了“文本转规则”“WordNet关系+prover”“NL形式化+solver”作为单独 novelty 的说法。细节与 limitation 见Phase 62 报告。

必须检验的窄差异是 gloss 原句 span 对规则 literal 的支持，而非 relation mapping span、NLI claim-span 或图中关系三元组。source-span gold、AND/OR completeness 与 witness DAG replay 尚未得到人工结果；仍是假设。固定 ACL 框 1,124/1,747 精确 URL 匹配，623 pending。

### Phase 63：WordNet gloss 与 lexical entailment 近邻

ACL 2023 的 *Grounding the Lexical Substitution Task in Entailment* 已将 WordNet sense gloss 和 synonyms 注入 lexical substitution 上下文，并使用 mutual entailment 判据。故“WordNet gloss + sense-aware entailment”不再适合作为宽泛创新主张。候选窄差异是 gloss 到多前提 Horn literal 的 source-span support、AND/OR 完整性和独立 witness DAG replay；目前没有 adjudicated gold、IAA 或 matched results，仍是研究假设。实现审计亦显示 typed predicate signature/type checker 尚未完成。见Phase 63。

### Phase 64：NL→逻辑、proof checking 与 KG 规则邻居

SPINDLE 已展示从荷兰语到带静态 type-check 的 λ/proof derivation；LATENTLOGIC、逻辑规则增强和 Path Spuriousness 分别覆盖 KG rule learning、rule transformation 和 path quality；FactKG、WiCE、RoMQA 覆盖结构化 KG claim verification 及来源/多证据支持。因此这些模块级能力不能独立写成 novelty。剩余窄假设是 sense/release-bound gloss-span 对每一 typed Horn literal 的支持、完整 AND/OR 证据及 source-only DAG replay 能否形成可审计并在盲测 gold 上优于匹配对照的 pipeline。当前仍缺真实 adjudicated gold、IAA 和 matched baseline；项目中的 typed argument signature 仍须代码审计。详见Phase 64。

### Phase 65：NLI proof 与证据验证的模块边界

PROVER 已将 commonsense retrieval、自然语言中间步骤和多步 NLI 结合，并用人工检查 proof correctness；ReCEval 已评链条步骤正确性与信息量；SICCK 涵盖 hypernym、量词和否定下的组合蕴含；FEVER retrieval 与多证据事实核验也有成熟做法。因此“使用 NLI 检查证明链”“生成多步解释”“收集多段证据”不应单独作为 novelty。要检验的窄差异是原始 WordNet gloss 对每条有向 Horn literal 的 span support、source-only facts、AND/OR completeness 以及独立 deterministic replay。当前还缺经许可的 adjudicated gold、IAA 和共同盲测结果；项目现有形式 checker 只能证明给定程序内的结构推导。见Phase 65。

### Phase 66：Verifier-guided proof 与 logical form precedent

NLProofS 已对 supplied facts 生成 multi-premise proof tree，并以训练所得 verifier 为步骤打分、搜索；其 verifier 是自然语言 valid/invalid 分类器，不等于 solver 对 canonical typed Horn program 独立重放。Dual-(m)T5 已将文本解析至 PL/FOL 并用于 NLI；CCG/Vampire 与 ZS4IE verbalization+NLI 也有先例。故 verifier、proof-tree、NL→logic 或 NLI integration 模块本身不能作为独立 novelty。需单独验证 gloss-span source support、predicate typing、source-only premises 与形式证书。真实 gold、IAA、matched baselines 仍缺，不能作语义效果结论。见Phase 66 报告。

### Phase 67：ACL 2021 逻辑近邻与当前实现审计

ACL 2021 近邻筛查进一步表明，互动式 theorem-prover lexical subgoal (Sumita et al.)、soft Horn reasoning (RuleBERT)、definite-Horn KG inference (UniKER) 和 solver-verified commonsense support (WinoLogic) 都有既有工作。项目差异只能作为待测的 source-span support + sense/release binding + AND/OR proof alternatives + source-only replay 组合假设；本轮非穷尽文献检索不支持 novelty 断言。

文件级实现检查显示，项目已有经人工审核 annotation→受限 unary positive Datalog→certificate replay/NLI routing 骨架，span 对齐 validator 检查格式/offset 而不判定语义真值。predicate arity 检查不等于 argument typing；typed Horn 尚未实现。真实双标裁决 gold、IAA、source-span semantic-support 指标、matched baseline 和模型结果仍缺。CodeGraph 用户已选择初始化，但本机没有 `codegraph` 命令且当前工具清单无对应 MCP；`codegraph init -i` 调用失败，因此此处审计为文件级。没有运行项目测试。详见Phase 67 深度报告。

### Phase 68：显式 signature table 的可选类型检查

已加入 `typed_program_validator` 并静态接入 Datalog closure/certificate/countermodel replay 与 pipeline problem 的 optional `type_system`；synthetic example 和输入契约见[typed Datalog contract](typed_datalog_contract.md)。本原型验证的是调用方给定类型签名下的形式兼容，尚无权威 lexical type ontology；canonical annotation schema 尚未原生保存 variable sort，当前依赖 rule-ID side table。只做了 py_compile，未跑样例/测试；运行时行为和 predicate inventory 尚未验证。类型正确性不等于 gloss 支持，人工 gold/IAA/NLI/matched outcomes 仍缺。见Phase 68 报告。

### Phase 69：类型环境与逻辑证书绑定

后续代码审阅发现 typed replay program 中的 type table 有 SHA-256，但证书/反模型没有随身携带该哈希。已补充 `type_system_sha256` 并要求 replay 与当前表精确匹配；typed countermodel 的全部 ground interpretation 也接受 signature 校验；规则变量的 closure grounding、certificate binding 与反模型规则满足检查均限制在声明 sort 的常量域中，避免仅做表面签名匹配却沿用未排序 Herbrand 域。Phase 69 当时仅做语法编译和静态审阅；后续对父/子 sort binding、哈希缺失/不匹配、错误 sort countermodel atom 的 10 项聚焦测试通过，见Phase 71 报告。这仍是 synthetic program 行为证据，不验证类型表与 gloss 语义。

### Phase 70：canonical annotation 到 typed Horn 的变量 sort 传递

新增实验性 `0.5-draft`：每条 rule claim 必须精确声明其公式子树变量的 `variable_sorts`；validator 检查覆盖关系，compiler v4 将 sort 映射写入每条派生 Horn rule，已有 typed Datalog checker 据此校验并约束变量域。0.4–0.5 均执行 gloss-grounded `inference_basis` 编译门，agreement analyzer v10 将变量 sort 纳入 claim 比较。0.2–0.4 继续兼容，当前 v3 标注草案和盲标材料仍固定使用 0.4。该实现消除了实验 typed 流程只靠编译后 rule-ID side table 承载变量 sort 的接口断点，但 sort 仍为调用方/标注者声明，未有来源审定的 lexical ontology，也未有人工 gold 或语义验证。61 项聚焦测试通过；不构成 gloss 支持或研究有效性结果。见Phase 70 报告。

### Phase 71：typed Datalog 域与篡改拒绝行为

新增 3 个直接 checker 行为测试，包含 sort subtype membership、certificate type hash 缺失/更换、countermodel type hash 篡改及错 sort atom 注入；`tests.test_datalog_checker` 共 10 项通过。其范围限于 synthetic type table 和有限正 Datalog replay，不是 WordNet 类型/释义语义有效性证据。见Phase 71 报告。

### Phase 72：typed checker 到 strict route 的端到端连接

新增 pipeline 端到端 synthetic tests：0.5 annotation variable sort 进入 replay program；证明后类型表版本变化会让 certificate replay 失败并拒绝候选；有效的程序内反模型可产生 scoped non-entailment route，hash 篡改则变成 abstention。pipeline 12 项通过，Phase 70–72 五模块合并回归 66 项通过。NLI 只使用合成高分 rows，且未过 source-only semantic gate；这不是自然语言、WordNet 或模型效果评测。见Phase 72 报告。

### Phase 73：OEWN lexname 与 typed inventory 来源边界

新增 profile 对 pinned OEWN 2025 Plus 聚合 POS、lexname 和关系类型：45 lexnames、120,564 synsets、93,395 `hypernym` 与 8,599 `instance_hypernym`。OEWN/WordNet 文档将 lexfiles 描述为 POS 与逻辑分组；这不足以认证其为 variable-sort hierarchy。现有 Phase 16 verifier 不含 instance_hypernym。profile 通过 archive byte verification 和重复计算，synthetic audit tests 2 项通过；变量指称/域值域、lexical predicate signature 和 source-support gold 仍未确定。见Phase 73 报告。

### Phase 74：Gloss referent/type 契约草案

为 compiler v4 的共享 unary variable 提出暂定 `Referent`→`Entity/Eventuality` 域，要求每个 claim/sense 经人工选择并拒绝仅按 POS/lexname 自动定型；当前 schema 0.5 未存类型来源/裁决 provenance。契约未进入编译器，也无真实类型标注/一致性结果。GWC 2023 的 WordNet Gloss Corpus→ERG predicates 先例已纳入 novelty 边界；source-span directional support + typed AND/OR replay 仍是假设。见Phase 74 报告与[类型契约](gloss_referent_type_contract.md)。

### Phase 75：Sort judgment provenance 链实现

新增实验 0.6 schema，要求公式变量 sort judgment 完整覆盖并带 status/basis/rationale/span；unresolved judgment 可留档但 compiler v5 不生成规则。已赋 sort 与判断 provenance 随 rule/certificate 回放，agreement v12 增加 sort-judgment 独立 micro P/R/F1 与 bootstrap interval。validator/compiler/agreement/Datalog/pipeline 等 73 项聚焦回归通过。该实现不评价依据或类型判断的语义真值，不产生真实类型 IAA 或 gold；当前 v3 标注仍固定 0.4。见Phase 75 报告和[标注协议](annotation_protocol.md)。

### Phase 78：instance pair 人工审查前置设计

当前 annotation lock 仍未签署或授权分发，因此只生成被忽略的 320 条 text-free pair IDs 与 hidden sampling key。五层候选经 producer/独立 replay preflight；direct/lift depth 正类总体计数可用于未来分层加权，challenge strata 单独报告。现有 0.4 schema 绑定单个 sense/gloss，不能直接表达两个来源的关系支持标注；需设计 pair-specific schema/validator。尚无 gloss 导出、人工标注、裁决或效果评估。见[Phase 78 设计](instance_relation_human_audit_design.md)和阶段报告。


### Phase 79：pair schema draft

pair-level validator 原型已加入，synthetic tests 覆盖数据结构约束；它将 relation judgment 与 strict gloss-support 分离，并独立跟踪双 gloss spans/hashes。当前仍未冻结或做标注者试用，也没有语义 gold。Phase 78 candidate frame 未变、仍 text-free；`protocol_signed=false` 和 `distribution_authorized=false` 不变。专项测试 8 项、全项目 232 项回归通过；该实现不是人工标注、语义验证、效果证据或新颖性结论。见Phase 79。


### Phase 80：pair study 手册草案

已将 pair schema 更新至 `0.2-draft`，每项 sense relation 与 gloss support 都要求独立 rationale；新增盲化/判定/裁决/报告手册草案。关键未决项仍包括许可与 attribution、`no` 的证据门槛、sense-relation 可用知识范围、认知试标、estimand/区间和未回收处理。文档是可审阅建议，不是签署方案；lock 仍未授权，未创建文本任务包或进行人工标注。另有 synthetic-only JSON fixture；validator 专项 10 项、全项目 234 项回归通过；见Phase 80。


### Phase 81：pair frame 规划精度

当前每层 n=64 不是基于目标精度/功效设定：单层最坏情形 pointwise 95% 正态近似半宽约 ±12.2pp，closure-weighted 正类汇总约 ±9.3pp，相邻 lift 层差异区间半宽约 ±17.3pp。same-POS nonclosure 是 source-macro 两阶段样本，不代表 pair-micro 总体。结果仅用于规划，最终 estimand、区间与扩样目标仍需预注册。新增 text-free audit script，3 项测试通过；全项目 237 项通过。见Phase 81。


### Phase 82：pair study analysis plan

统计分析计划已形成未签署草案，指定建议的 closure-positive weighted support-label prevalence，定义 strata/challenge、uncertain 与 unassessed/nonresponse、双标和 span 指标；未冻结区间、多重比较或样本精度目标，亦未做 power。人类裁决只作 noisy reference。计划不改变 lock，也不构成 preregistration 或分发授权。见Phase 82与[统计分析计划](instance_relation_statistical_analysis_plan_draft.md)。


### Phase 83：有限总体区间原型

已实现推荐的 exact hypergeometric inversion + Bonferroni interval 方法，并通过 `N≤8` 全部有限总体/样本观测组合的穷举 nominal-coverage 测试。可构造分层加权主 estimand 与 contrasts 的 simultaneous conservative bounds，缺失值按 worst-case 拓展。模块 4 项专项、全项目 241 项测试通过。方法仍待研究负责人审定，same-POS two-stage challenge 不由此覆盖，也无人工语义结果。见Phase 83。

### Phase 84：SemEval 2026 形式/内容效应评测近邻

对 SemEval-2026 Task 11 官方任务论文作全文定向筛读：其四类 syllogism 设置控制语义合理性、语言和无关前提，并将 content effect 与准确率区分。这为本项目的 NLI/释义解释模块提供了压力测试设计参照：应分开测形式结论与内容偏置，并单独看干扰前提影响。该任务不做 WordNet sense-linked gloss-span support、Horn 编译或 proof replay，因此不是匹配 baseline；相关组合价值仍是研究假设。未独立复现论文结果。见Phase 84与[结构化筛读记录](../sources/literature_screening_log_2026-10-07_semeval2026_task11_overview.json)。

### Phase 85：NLI 内容效应/无关上下文评测草案

将 Phase 84 启示具体化为独立的未冻结方案：在主 NLI 三分类和 dev/test 路由之外，分别设计人工合理性分层、形式约束匹配对及无关上下文成对压力测试。明确诊断预测不能校准正式阈值、上下文不能作为 source assertion 或进入 source-only proof gate；Phase 83 区间方法也不适用于这些新 estimand。方案未实现、未注册、未获标注授权或用于数据比较。见[评测草案](nli_content_effect_evaluation_draft.md)与Phase 85 报告。

### Phase 86：NLI 诊断 sidecar 与描述 evaluator 原型

新增 `src/logic/nli_content_effect.py`：校验 text-free sidecar、匹配合理性对/同源 gloss 上下文对、label 与模型哈希、配对身份及 group split；对锁定预测输出按 support/plausibility 切片的描述率、两个 content-effect gap、配对分数差和决策翻转率。模块显式标记 `diagnostic_only`、`threshold_selection_performed=false`、`proof_route_eligible=false`、`inference_performed=false`，并不导入或调用路由器。新增六项 synthetic-only tests；NLI/strict pipeline 相关测试 33 项、全项目回归 247 项通过。没有真实数据、置信区间、模型比较或 semantic claim。详情见Phase 86。


Phase 93 已筛完 2021 年此前无匹配的 85 条 ACL 候选（26 邻近、2 背景、54 当前核心综合排除、3 缺官方摘要待补）。四篇官方论文定向核读补上 LogicNLI 显式证明追溯、EEV 对解释gold逻辑有效性的人工审计、NeuNLI proof tree、ParaPattern 操作级自然语言演绎先例。全框现为 1,501/1,747 URL 匹配、246 未匹配，剩余未匹配项均在 2016–2020；2021 有 3 条待补摘要、22 条旧日志深度不明。此类 scoping 仍不能证明新颖性或系统综述完成。见Phase 93 报告及[机器快照](../outputs/phase93/acl_screening_coverage.json)。
### Phase 99 增量：4lang/ BMEAUT 同线期刊工作

ACL 框外定向全文复核 Kovács et al. 的 NLE 2023 *Explainable lexical entailment with semantic graphs*，核实为 BMEAUT SemEval 2020 的期刊后续，不重复计作独立方法家族。该文已展示从词典定义构造 4lang 图、按图路径判断词汇蕴含、加入 WordNet 并提供可解释路径；故“首次可解释定义图 lexical entailment”不成立。论文同时报告边语义过宽、义项/图边错误会导致错误蕴含，图路径不能替代来源支持核验。项目潜在差异仍限于 sense/release-linked gloss span→typed AND/OR Horn→source entailment→独立 replay 的联合 gold 评测假设；没有 gold 或 matched baseline，不能报告新颖性或性能增益。见Phase 99 报告与[筛读日志](../sources/literature_screening_log_2026-10-07_4lang_explainable_lexical_entailment.json)。

### Phase 100 增量：图模式到 formal rule 的领域邻接先例

Recski et al. 的 BRISE-Plandok 以 UD→4lang 图及领域手写 patterns 抽取法规属性和正式规则，并发布 7,049 句经双人标注/作者复核 gold；文章报告规则 end-to-end 完全正确率为 46%（全属性）、55%（仅 40 个手写 pattern 覆盖属性），gold-attribute 条件约三分之二。作者指出 pattern 基于全标注集形成，未验证跨文档泛化。该工作排除宽泛“首次图式自然语言规则抽取与 gold 评估”，但并非 WordNet gloss 或 lexical entailment baseline。当前项目仍缺 gloss-source semantic gold、匹配基线和 source-only replay 结果。详见Phase 100 报告及[筛读日志](../sources/literature_screening_log_2026-10-07_brise_plandok_rule_extraction.json)。

### Phase 101 增量：BRISE 原型的 theorem-prover 路线

ASAIL 2021 BRISE 原型已将 UD→4lang 图模式映射为 deontic logic 规则并送入 prover，同时提供逐步说明；其完整抽取仅在 6 条 toy 句上调到 perfect，论文明确这不是端到端定量证据。attribute extraction 的 P>93/R>51 来自十文档样本，不等于规则正确率。该原型和 BRISE-Plandok 2025 属同一演进路线；prover correctness 不能认证 source→formal rule fidelity。项目的 gloss/sense/span/Horn 差异仍待人工 gold 与 matched baseline 检验。见Phase 101 报告和[官方全文筛读日志](../sources/literature_screening_log_2026-10-07_brise_explainable_rule_extraction_2021.json)。

### Phase 115 增量：NeurIPS 2025 formalization fidelity 与 WordNet retrieval

官方 NeurIPS 2025 记录中新增 HAR/CoPA、miniF2F-Lean Revisited 和 Hierarchical Retrieval 三条定向全文/章节筛读，均未见于此前本地矩阵。最近的评测方法启示是必须独立审计原自然语言到形式化目标的忠实度；形式证明通过只覆盖给定形式输入。WordNet Hierarchical Retrieval 则使用 taxonomy links，不做 gloss parsing。没有发现这三篇可直接作为 gloss→Horn/source-span matched baseline 的工作。筛读没有扩展 ACL 固定候选框，也不构成 proceedings-wide review 或 novelty evidence。当前就绪状态未改变：bridge 未做端到端运行、无 gloss support gold/IAA、无 matched baseline 或干净环境复算。详见Phase 115与[结构化日志](../sources/literature_screening_log_2026-10-07_neurips2025_autoformalization_wordnet.json)。
### Phase 116 增量：ReForm semantic consistency 与法律 AND/OR interaction

ICLR 2026 官方全文筛查新增 ReForm（数学 formalization semantic consistency、859 项专家标注、双标/第三人裁决）和法律模型 AND/OR interaction audit（专家判定 phrase 相关/无关/禁止）。前者排除“形式正确性外加入语义忠实度人工评价”作为宽泛新颖点；后者排除宽泛 AND/OR phrase pattern 归因主张。后者的 feature interaction 不等于逻辑 Horn/Witness 证明。两者都不是 WordNet gloss lexical baseline。项目仍无 source-gloss semantic-support gold、IAA、matched baseline 或 bridge 全链运行。筛读局部边界见Phase 116 报告与[日志](../sources/literature_screening_log_2026-10-07_iclr2026_reflective_fidelity_and_andor_audit.json)。
### Phase 117 增量：selected-witness lineage 输入完整性与代码指纹

结构来源审计 v2 已对完整固定 bundle 重跑。新入口先通过 `frozen_bundle_integrity_lock.json` 验证六个锁定 bundle files，并独立比对 bundle checksums sidecar 中的 `graph/selected_basis_atoms.txt`；报告保存 manifest、basis、rules、witness、sense index、checksums、integrity lock hashes，以及五个实现文件的 SHA-256 与 Python/platform。观察到 110,340/110,340 条 selected clauses 有 source link，110,382 个 payload（17,583,887,267 bytes）checksum 和 source/head identity mismatch 均为 0；结构 lineage gate 全通过。v2 artifact 另通过独立的 [Draft 2020-12 JSON Schema](../config/selected_witness_source_lineage.schema.json) 校验。该补强修复 Phase 19 v1 未把 basis hash 写入 artifact、未统一核 frozen bundle lock 的复算缺口。它仍不验证 gloss-span 语义支持、WSD、方向关系或发布许可。详见Phase 117与[新版 artifact](../outputs/phase117/selected_witness_source_lineage.json)。

### Phase 118 增量：OEWN hypernym producer 与 replay v3 运行复核

Phase 118 使用固定 OEWN 2025 Plus 发布版重新运行既有 360 条 stress claims：producer 生成 `oewn-hypernym-closure-verifier/2` 输出，独立 replay v3 核验全部 claim、路径和指纹，结果 `valid=true`、0 errors。两个 bridge schema 通过 Draft 2020-12 meta-schema 检查。它关闭新版关系 verifier/replay 仅静态审阅的运行缺口，但 stress frame 不是概率准确率样本，OEWN 关系证书也不是 gloss entailment。没有真实且获授权的 adjudicated mapping 与外部 manifest，因此 bridge CLI 仍未端到端运行。详见Phase 118 报告、[producer 输出](../outputs/phase118/oewn_hypernym_stress_v1_verification_v2.json)与[replay v3](../outputs/phase118/oewn_hypernym_stress_v1_replay_v3.json)。

### Phase 119 增量：bridge 合成端到端 wiring

Phase 119 用两个 sentinel candidate（`SYNTHETIC FIXTURE ONLY - NOT A WORDNET GLOSS`）运行 candidate manifest freezer、hypernym producer、replay v3 和 relation bridge validator；一个 synthetic-adjudicated wiring row 和一个 `unassessed` denominator row 均在成功报告中保留。正确 manifest pin 时结构 report 为 `valid=true`，错误 pin 与缺失 unresolved bridge row 时均拒绝；claim-review 的 NLI 与 semantic-support 保持 unassessed。该 fixture 证明的是接口/哈希/候选分母契约在人工构造输入下能够贯通，不证明 `adjudicated` 字段是真实人审、sense mapping 正确或 gloss 支持关系。真实 mapping、授权及 gold 仍缺。见Phase 119 报告与[合成 fixture](../examples/synthetic_gloss_oewn_bridge/README.md)。

### Phase 120：EMNLP 2025 定向文献审计

新增四篇 Findings of EMNLP 2025 官方全文定向筛读，压缩形式证明、通用核验 agent、知识 grounding 和逻辑评测的宽泛 novelty 空间。候选框外补查，不改 ACL v3 1,747 条冻结分母；截至 2026-10-07，EMNLP 2026 conference date 仍在未来，因此不作 2026 proceedings coverage/absence claim。该轮没有补上项目关键的 sense/release-linked gloss-span semantic gold、真实 adjudication、IAA 或 matched experiment，也没有做独立复现。剩余研究假设仍需以授权数据和共同 gold 验证，不能宣称已证新颖性/效果。见Phase 120 报告与[结构化日志](../sources/literature_screening_log_2026-10-07_emnlp2025_reasoning_verification_grounding.json)。

### Phase 121：标注 v3 预注册输入完整性复核（2026-10-07）

重新执行 `src/analysis/audit_annotation_preregistration_v3_inputs.py`，21 项输入完整性/契约检查全部通过。400 条候选 frame、400 条 blind batch、400 条答案键、24 个 strata 与 OEWN release cross-check 完整对齐；七项冻结输入/来源材料哈希与 lock 相符。结果落于[可复算 preflight artifact](../outputs/phase121/annotation_preregistration_v3_input_preflight.json)，同时绑定 audit script 与 lock SHA-256。

该结果只证明当前工作区的文件字节、schema 和内部链接满足 preflight 契约。它没有标注回传（0 个文件），协议仍未签署，没有外部 preregistration ID，`distribution_authorized=false`。因此该批次尚未成为人工 gold，不能启动分发或报告标注结果；许可审查、负责人/标注者安排、注册与外部试标等启动 gate 仍需解决。完整分析见Phase 121 深度报告。

### Phase 122：多参考 scorer 与确认性 estimand 静态审计

对照当前 `src/analysis/score_gloss_analysis_references.py`、`src/logic/gloss_analysis_reference.py`、输入锁与 preregistration v3 草案，确认 scorer 对每个 `complete` item 分别比较整套 accepted alternatives，按规则 claim multiset F1 最高项选 reference；并列优先 whole-analysis exact，再按 alternative ID 排序。它不把 references 的 claims 取 union；claim exact match、root AST exact、analysis-status match 分别可见，overall exact match 要求三者全部成立。它只评分规则结构，不评分 evidence span、source support correctness 或 NLI。

这套逻辑与协议的“多参考不可合并、逐项最佳匹配”描述基本一致，但它估计的范围必须严谨写成“在 sidecar 已收录的可接受 reference 中，resolved items 的 per-item best-match 描述性分数”：

1. **多参考选择必须预测盲化并完整冻结。** 如果 adjudicator 在查看某模型输出后新增 accepted alternative，该模型会得到不对称优势。Sidecar 的格式校验无法证明 accepted set 穷尽或裁决者未见预测；这些是流程/访问控制证据，必须预先写入执行记录。Best-of-reference 有意承认多个合法形式化，但数值会高于或等于单参考严格匹配，不能单独宣称“唯一正确形式”或普遍模型性能。
2. **未决裁决项不进入 claim score 或 exact-match 分母。** scorer 输出 `unresolved_rate` 和计数，但该 rate 是未加权的；若难例更可能 unresolved，resolved-only score 只能解释为条件于裁决完成的结果。发表时必须同时给出完整测试项、resolved/unresolved 分母与原因、分层完成率/未决率；不能只报 resolved score，也不能把其外推为原始目标总体的表现。
3. **Macro 分母随预测而变。** 实现将 claim comparison 的空/空 item 从 macro P/R/F1 分母排除；当一套 reference alternatives 中包含空 claim set 时，不同预测可能改变哪些 item 进入 macro。故 per-system macro 可作为描述值，但跨系统 paired claim 不应只比较该 macro；须同时报固定分母的 exact-match（所有 resolved 项）与 micro 指标。若要做 macro 的模型间差异检验，先预定义仅由 reference/test frame 决定的共同 item 子集，并让所有系统使用同一分母。
4. **当前输出不是总体推断。** 协议已说明 scorer micro/macro 未加抽样权重；test set 的 split、lemma-group 隔离、selection rule 与 estimator 必须先冻结。若要外推至抽样目标总体，需要预先定义设计权重与 cluster-aware uncertainty estimator；不能把 400 项一致性/释义分析样本自动当作 400 项模型测试集。
5. **“最佳备选”只处理 claim multiset。** 证据 span、gloss 对规则语义支持、source-only proof replay 和 NLI 都需独立指标与其自身 gold；语法/结构一致不能代替它们。

当前 draft 尚未决定确认性研究采用单一裁决 reference 还是多参考 sidecar；Phase 122 不替研究者选择，也未更改 scorer。启动模型对比前应先由研究者选择并锁定 estimand、sidecar schema/hash、prediction-blind adjudication 流程和模型比较分母，再在 synthetic fixtures 上检查 scorer 行为。此次是代码/协议静态审计，没有运行 tests、CLI、gold 或模型预测。详见Phase 122 深度报告。

### Phase 123：执行态 matched-baseline readiness crosswalk

现将三轨协议与当前实现/工件逐项对账：[evaluation readiness matrix](evaluation_readiness_matrix.md)。截至 2026-10-07，冻结超图来源结构和 OEWN taxonomy stress replay 有结构性可复算证据；bridge 成功/失败只在 synthetic fixture 上验证。Pair verification 没有项目候选对、人工 NLI/semantic-support gold、模型分数或 dev/test 预测；oracle-formalized prover 与 source-only/end-to-end 路由没有真实 gold-backed run。Phase 121 的 400 项 annotation package 通过本地输入完整性检查，但 0 回传且未签署/未授权。

因此三个 track 的共同输入、基线类别与分离指标已有协议设计，但尚无真正的 matched baseline result。启动顺序现明确为：逐源 rights/attribution gate → 冻结 primary estimand/不确定项处理 → claim-pair frame/hash 和 group split → 获授权双标/裁决 gold → 冻结模型/预算/held-out 预测 → 分轨运行与独立 replay。任何当前结果只可支持其窄工程/结构结论，不能写成模型有效性或新颖性证据。

### Phase 124：高频 GCIDE 来源族的许可/来源粒度

官方资料确认 GCIDE 0.54 的项目级声明为 GPL v3-or-later，README 描述 1913 Webster、WordNet 1.5 与志愿者等段落级混合来源。此信息不会将冻结 payload 自动绑定到 archive，也不能排除单个 definitions 的第三方来源/署名要求。机器 triage 的 1,573 payload 画像数与 rights log 的 1,580 evidence-object 数量单位不同，仍需解释。发布 clearance 不变；需要 exact release byte/entry crosswalk 和 source-tag-to-rule/witness lineage 才能判定任何子集范围。见Phase 124 报告。

### Phase 125：GCIDE 证据计数与冻结 payload 完整性

有限范围 census 已精确解释 GCIDE profile 的计数差：1,573 个唯一 payload 包含 1,580 个 evidence objects；六个 payload 有多条 GCIDE evidence（5 个含两条，1 个含三条）。5,625 个目标 payload 的冻结 checksum 全部匹配。1,580 条 evidence 均声明 v0.54 且带格式有效定义 hash，但未提供 ILI；尚未对官方 archive 内容匹配或评估子来源。该审计可用于复算来源记录结构，不能作为许可结论。见Phase 125。

### Phase 126–127：GCIDE 归档匹配及 graph/witness 路径

Phase 126 下载与 GNU 公布 MD5 一致的 GCIDE 0.54 tar.gz，对 1,562 个不同 evidence hash 做原始字节与规范化文本 crosswalk；846 个 hash 在命名的去标签/HTML/NFC/空白变换下命中。1,579/1,580 evidence hash 等于同 payload `synset.raw_definition` 的 UTF-8 SHA-256；唯一异常命中一个归档中带 WordNet marker 的段落，但不是独家归属证明。Phase 127 又将全体 1,573 个 GCIDE payload 唯一连接到 sense index identity；886 个路径进入 selected-witness 来源文档，302 个仅在非选定 active clause，385 个无 active-clause 来源路径。唯一异常 WordNet-marker payload 在无活动路径组中。结构路径不证明文字语义支持 literal，亦不清权；无 gloss-span gold、matched baseline 或发布授权。见Phase 126 报告、Phase 127 报告及[Phase 127 artifact](../outputs/phase127/gcide_graph_lineage.json)。

### Phase 128：selected-witness gloss hash 与来源标记

886 个 selected-witness-linked GCIDE payload 中，506 个 gloss hashes 在 GCIDE 0.54 归档按标签剥离、HTML 解码、NFC 与空白归一化命中；46 个有至少一个 WordNet-marker passage match，433 个有 Webster 1913 marker match，489 个有任一非空 marker，17 个未恢复 marker。标记/匹配类别按 hash 聚合且可重叠。380 个 payload 未在当前 normalization 下命中。此为 gloss 字符串与候选归档段落的内容对应以及 witness source path 的结构 link，不验证某 source span 语义蕴含某 rule literal；权利 clearance 仍未解决，真实 gloss-support gold 与 matched baseline 仍缺。详见Phase 128 报告和[机器 artifact](../outputs/phase128/gcide_marker_witness_crosswalk.json)。

### Phase 131：多参考 gold 的 source/sense identity 绑定

审查发现旧 scorer 只检查 item_id、raw-gloss 哈希和 split，没有对齐预测与裁决 gold 的资源/版本/record/synset/POS。现要求同一 sidecar item 的所有 linked annotation records 共享 source/sense identity，prediction 也必须与该 identity 匹配；scorer 版本升至 `gloss-analysis-reference-scorer/0.5`，schema 字段不变。该修补仍未运行测试，且没有真实多参考 gold/预测，不能说明标注可靠性或模型表现。详见Phase 131 深度报告。

### Phase 132：OEWN 2025 Plus 400 项盲标批次的 source-specific rights gate

逐项核对 Phase 121 锁定结果与批次 manifest：400/400 raw gloss 与 pinned OEWN 2025 Plus archive crosscheck 精确匹配；manifest 含 attribution、copyright、CC BY 4.0 与官方 license notice URI、修改说明和用途限制。官方 OEWN 条款要求署名 Princeton WordNet 与 Open English WordNet team，并保留底层 Princeton WordNet 条款边界。该核对增加的是候选批次的来源链/署名证据，不是法律意见或分发批准。锁状态仍为 `protocol_signed=false`、`distribution_authorized=false`，0 个回传文件；因此不得据此向外部标注者分发或公开发布。详见Phase 132 深度报告与[发布门槛](data_release_gate.md)。

### Phase 133：KR 2026 provenance 与 2026 lexical/rule-work 对账

新增 KR 2026 Main Track 的 Datalog why(-not)-provenance 为直接形式 prior：proof-tree supports、多个输入事实解释和程序 provenance 均有前例，且识别问题复杂度已分析。IJCAI 2026 NRI、LREC 2026 adjective hypernym gold、NALOMA 2026 Neural DTS 已存在于项目文档，本轮做官方全文范围复核与去重，不重复计新发现。由此 witness/provenance、宽泛 AND/OR rule induction、WordNet hierarchy + logic prover 均不能单独支撑新颖性。剩余的 gloss-span→typed Horn source-support + source-only replay 仍是待检验假设，无 gold 或 matched result。见Phase 133 深度报告与[结构化筛读日志](../sources/literature_screening_log_2026-10-07_kr2026_provenance_and_lexical_reasoning.json)。


### Phase 134：KR 2026 最小支持与形式证明邻接 prior

官方 proceedings 的有限主题筛查补出数据库 query minimal-support relevance、FOL 公式非等价解释、终止 proof-search 分解树与 Lean chase 形式化。它们排除最小支持成员关系、解释形式差异、规则证明证书或 machine-checked rule reasoning 单独作为贡献；没有直接评估 sense/release-linked WordNet gloss-span 到 typed Horn 的语义支持。该筛查只读所选条目的官方摘要，不是完整 proceedings review。人工 source-support gold、IAA、matched baseline、真实授权运行仍缺。详见Phase 134及[筛读日志](../sources/literature_screening_log_2026-10-07_kr2026_provenance_and_lexical_reasoning.json)。

### Phase 135：EACL 2026 WordNet gloss/lexical prediction prior

补入 EACL 2026 CAP 官方全文筛读。它已用 WordNet gloss 做 inverse definition modelling（definition→term），也评估 word→hypernym；二者不同于逐 gloss-span 支持 typed AND/OR Horn literals。CAP 结果条件于干预前正确样本。论文缺席原 ACL v3 candidate file，发现的是检索词族盲点。项目 source-support gold、IAA、matched run 仍缺；详见Phase 135。

### Phase 136：ACL 释义条件词汇预测检索扩展

候选生成器增加 definition-conditioned lexical prediction 词族，基于当期官方导出生成独立 v4，v3 文件保持冻结。v4 与 v3 精确 ID 差分为 +1 / -0；新增候选是 EACL 2026，词族命中另含一篇旧框 2020 论文。v4 有 1,748/1,748 精确 URL 日志命中，但 229 条历史深度未明，因此并非全量筛读/综述纳入。导出哈希变化限制单因素归因。详见Phase 136及[机器审计](../sources/acl_query_expansion_audit_2026-10-07_phase136.json)。

### Phase 137：固定 ACL 导出同源消融

将 ACL 官方压缩 export 固定为 SHA-256 537d57a62d42ca43c16d71ccd284d57d53ffe9d4cfa42521acef083508e245d9，并增加离线复用/词族排除能力。相同输入字节下，旧词族 union 为 1,747 IDs，与 frozen v3 ID 集合和旧族命中数均一致；添加释义条件预测族后为 1,748，恰好新增 EACL 2026 一条、无删除。完整候选框仍有 229 条筛读深度未明；这一结果不估计领域召回或系统综述完整度。完整复算材料见Phase 137 报告及[机器审计](../sources/acl_query_expansion_audit_2026-10-07_phase137.json)。raw bulk snapshot 含窗口外材料并有混合许可边界，仅作本地复算输入。

### Phase 138：搜索器流式解析与固定导出输出等价

ACL 搜索器由整文件解压/解析改为逐 BibTeX 条目处理。对 Phase 137 固定快照复算，131,647 条目与 1,748 个候选在 ID、共同记录字段和旧词族命中数上完全一致；解压内容哈希相同，日志对账深度保持不变。运行期间工作集采样约 69 MiB，旧运行观察值约 966 MB，但未进行受控峰值基准。该优化提高当前工作流可持续性，不构成解析器一般正确性证明或候选召回/新颖性证据。见Phase 138 报告与[机器审计](../sources/acl_streaming_parser_audit_2026-10-08_phase138.json)。

### Phase 139：OEWN 2025 Plus genus 词面基线当前态复算

当前工作树重新处理 84,909 个名词 synset、84,910 条定义字符串，并逐字节核对固定压缩归档中的 53 个 entries/noun JSON。当前输出与 Phase 11 聚合产物字节级一致；候选覆盖为 74,854/77,173，候选任一 sense 命中同版直接 hypernym 为 28,449/74,854。该结果是同资源、any-sense 结构 proxy，只证明这项确定性 census 可复算；无人工 sense/genus mapping、source-span support gold、独立词典验证或 matched baseline。annotation v3 仍 0 回传且未签署/未授权，主 gate 未改变。详见Phase 139 报告及[机器审计](../sources/oewn_genus_baseline_replay_audit_2026-10-08_phase139.json)。

### Phase 140：400 项 blind batch 的实验轨道适配

只读核查将 v3/400 的作用划清：返回协议可收集 gloss 结构、方向性 rule claim 与原文 span，冻结 schema/protocol 后可贡献 Track C 人工参考；它不是 Track A claim-pair frame，Track B 需 adjudicated rules 加独立固定 facts/query。两个 presentation slot 的 seed/hash 与 400 行均通过 audit replay，answer key 未纳入。当前 presentation 与数据 lock 仍未授权/未签署，0 回传；此外 lock 未固定 annotation schema/protocol hash，validator 同时接受 0.2–0.6 draft 版本，必须在标注前选定并锁定。见Phase 140 深度报告和[机器审计](../sources/annotation_batch_fitness_audit_2026-10-08_phase140.json)。

### Phase 141：Pair verification 的 premise/context 可识别性

Track A 当前记录/manifest 只将 raw-gloss premise 与 sense ID/POS 绑定，未包含 target lemmas 或冻结的 hypothesis 模板；NLI export 只按 premise/hypothesis hash 绑定评分。因此模型可见的词义上下文目前没有明确操作定义，human vs model input 是否 matched 尚不能判定。推荐将 lemma+POS+verbatim gloss 的版本化上下文作为 primary premise，并把 raw-gloss-only 留作配对消融；新 schema 分别绑定 raw gloss 与 rendered premise hash。现有 `/0.1` hash 不变量不应被原地更改。pair 候选、标签和模型结果仍为空。详见Phase 141 深度报告与[机器审计](../sources/claim_pair_premise_context_audit_2026-10-08_phase141.json)。

### Phase 143：source-only 路由代码契约盘点

静态核查确认 pipeline 在 source_only 下拒绝未分区事实、剔除 resource/external facts，并要求纳入的 source assertions 带 sense、gloss hash、source path 和 reviewed-claim refs；类型校验在 closure 前 fail closed。证明与有限程序反模型均分别独立 replay，非法/不支持逻辑程序进入 unknown。正向 NLI route 还须通过 adjudicated rule/fact binding、测试 pair hashes 与固定 source bundle 校验。此项只核对实现契约，不表示代码已在真实 gold 上运行，也不证明注释语义正确。实际 gate 仍是未冻结的 pair estimand、0 标注回传、未授权和无模型结果。详见Phase 143及[机器审计](../sources/verified_reasoning_route_contract_audit_2026-10-08_phase143.json)。

### Phase 144：Track A source identity 复核

v3/400 的 sense ID 与 raw gloss 均在固定 OEWN release 中匹配，但一项 POS 不一致、一项 target lemma set 不完整；frame 与 blind batch 一致地保留旧字段，不代表它们通过 release identity validation。未来 pair frame 必须按 release record 重取 target POS/全部 lemma，parent synset 有多个表面形式时需先定 hypothesis policy。未改写历史 batch，未创建 pair/gold，也未解除授权 gate。机器审计及完整限制见[Phase 144](../outputs/phase144/annotation_frame_release_identity_audit.json)和报告。

### Phase 145：parent lemma 与 split-group 可行性

当前 400-sense source 在直接 hypernym 子集上有 322 条 edge。每条 edge 展开 release 中所有父 lemma 得 680 个候选表面（无 target-sense × lemma 碰撞），比每 edge 单一词面多 358 行；单词面规则若取字典序，仅是可复现选择而非语义优选。多词面候选须用 relation-edge ID 绑定并同 split，且 exact surface hypothesis 独立标注。候选 freezer 的 `group_id` 可表达 split 隔离分组，但现有 text-free manifest/0.2 没有 parent synset/edge ID，因此需要新版本承载资源 provenance，保留现有哈希契约。当前基于目标/父义项与 lemma 的草案闭包为 279 组件、最大 26 行；精确 renderer 和 split strata 冻结后必须重新计算，不能直接据此宣称 split 已满足。参见Phase145 报告。

### Phase 146：claim review context contract crosswalk

字段级静态审计发现四个迁移点：raw gloss 与 model premise 目前同 hash；source evidence span 依 premise 坐标；manifest 缺 parent synset/relation-edge provenance；`group_id` 同时承担 split isolation 和 certified dev calibration 一组一行。新路线应 在独立版本中绑定 raw-gloss hash、rendered-premise hash、source-gloss spans、renderer、parent relation 和不同的 leakage/statistical unit。 `nli_content_effect`、claim-review validator、freezer、exporter、resource bridge、nli gate、strict pipeline and docs all need coordinated version support. Context condition's NLI gold target and cluster aggregation remain unchosen. Evidence: Phase 146 report and [static audit artifact](../sources/track_a_context_contract_audit_2026-10-08_phase146.json).

### Phase 148：witness × Datalog bridge replay

当前格式 bridge 与单目标结构证书通过重放：3,596 nodes、14,923 dependency edges、3,512 ground rules；Phase117 全量 selected-source lineage 的 bundle hashes 与当前冻结包相同。Phase6 历史 bridge 的当前 replay 只在 proof-result 对象相等检查失败；具体差异为当前 checker 的证书节点新增 `source_bindings`、`source_claim_refs`，历史 artifact 创建时所存 summary 为 valid、证书可复核且节点/边集合相同。审计器将这个兼容性漂移显式记录，并以当前格式 artifact 作为可重复入口。它不建立 gloss-span semantic support、WSD 正确性、开放世界蕴含、替代 clause 有效性或许可清权。详见[机器审计](../outputs/phase148/witness_example_replay_audit.json)、[当前 bridge](../outputs/phase148/witness_oewn-00520548-n_datalog_bridge.json)和深度报告。



### Phase 150 增量：claim-support 先例边界

COLM 2026 Q-CARE 已提供原子 claim↔检索片段 pairwise support 与 human-labeled verifiability benchmark 先例。由此进一步排除一般 claim-support 或 human auditability 作为宽泛新意；项目仍无 sense-linked gloss-span semantic gold、matched baseline 或 proof-semantic evaluation。Q-CARE 不是同任务基线，也不改变授权、标注回传、效果或新颖性状态。见Phase 150 深度报告和[筛读日志](../sources/literature_screening_log_2026-10-08_colm2026_qcare_fulltext.json)。


### Phase 151 增量：judge 参考、可执行 oracle 与 gloss gold

No Free Labels 进一步说明 correctness judge 的可靠度依赖其自身求解能力及参考答案正确性；LogicIF 以代码执行产生答案 gold 并独立人工核查自然语言 instruction fidelity。项目应分别维护 judge calibration、形式/结构回放、自然语言 gloss-span support gold 三条证据；前两者不能替代第三者。尚无本项目 annotation returns、matched baseline、source-rights clearance 或已证新颖性。详情见Phase 151和[筛读日志](../sources/literature_screening_log_2026-10-08_colm2026_grounded_logic_addendum.json)。
### Phase 159：新增相关工作对评测分轴的约束

ACL 2026 Industry Track 的 T² 用依赖定理行为测试补足编译检查；Findings ACL 2026 的 FoVer 用形式 verifier 生成 PRM 训练标签并在 NLI 上评估；SemEval 2026 Task 11 将控制 syllogism 的有效性、内容 plausibility、无关前提与语言条件分开。三者均不能替代 WordNet sense-linked gloss-span semantic-support gold。当前 frozen graph/proof replay 仍只验证给定形式表示及其证书；没有新源语义 gold、匹配基线或有效性/新颖性结论。详见Phase159及[逐篇机器日志](../sources/literature_screening_log_2026-10-08_formal_correctness_nli_addendum.json)。

### Phase 160：typed pipeline 结果诊断审计

静态调用链确认，类型系统随 program 进入 `verify_query`，而 `verify_certificate` 和 `verify_countermodel` 会独立校验 typed signature table 与证书 hash；类型表变化已由既有测试覆盖（本轮未运行）。本轮仅增强结果可读性：pipeline 将 typed validation failure 映射到稳定 `invalid_typed_program` unknown 原因码，strict route 从 replay program 重新计算并在 `evidence_checks.typed_program_validation` 暴露报告，未提供 `type_system` 则明确为 `not_requested`。版本升为 `/13`。这是诊断与可追踪性改进，不是新的 soundness 证明，也没有真实 0.7 proof/source-bundle 回放。见Phase160报告。


## Phase 161 当前复算环境状态（2026-10-08）

受维护 Python 源码与 tests 的 132 个文件 AST 均可解析；扫描未发现非标准库且非项目内的顶层导入。Python 3.10+ 标准库政策与声明 CI 矩阵一致，但本轮没有执行 CI/测试。项目仓库不携带外置冻结 bundle；本机只确认配置目录及 manifest 存在，尚未验证锁定 payload，因此不把完整数据审计记作已复算。该结果不改变论文有效性/新颖性、Track A 授权或语义 gold 状态。见Phase161 报告和[机器审计快照](../sources/reproducibility_environment_audit_2026-10-08_phase161.json)。


## Phase 162 bundle lock 当前重放（2026-10-08）

配置的外置 frozen bundle 通过项目 integrity lock：semantic fingerprint 与 6 个必需文件 SHA-256 匹配。该 verifier 不逐一检查 checksums sidecar 所列的全部 source-record payload，因此只确认锁定结构文件当前一致，不等同于全量数据包完整性、来源真实性或语义验证。未运行测试/CI/模型或 proof route。见Phase162报告及[机器结果](../outputs/phase162/frozen_bundle_integrity_replay.json)。


## Phase 163 当前来源 payload 完整性（2026-10-08）

当前复算覆盖 sense index 引用的 115,235/115,235 个唯一 source-record payload、18,734,636,389 bytes，均解析成功且匹配 checksum sidecar；重复路径和畸形索引记录均为 0。此次 aggregate 与 Phase23 保留报告字节一致。该检查支持冻结包内部字节完整性，但不确定上游 release/license/attribution，也不验证 gloss 支持、图规则语义、人工 gold 或论文主张。发布 clearance 仍为 `not_assessed`。见Phase163报告和[机器结果](../outputs/phase163/source_release_metadata_audit_current.json)。


## Phase 164 当前相关工作边界（2026-10-08）

PMLR ICML 2026 Volume 306（2026-09-29 发布）提供最新会议快照；官方增量筛读补充 NeurIPS APOLLO/Weaver/MuSLR、ICML2026 constructive formal problem-solving、editable proof-sketch refinement 与 learned self-verification、ICML2025 RULEBREAKERS。新增先例加强以下边界：proof repair、verifier fusion、自验证训练、形式规则 benchmark 和 formal-vs-plausibility 分轴均有工作；它们不是 WordNet sense/release-bound gloss-span→typed Horn source-support matched baseline。筛查不是系统综述或全量 proceedings census；项目新颖性/有效性仍未证。详见Phase164报告。

## Phase 165：ICLR 2026 相关工作对新颖性边界的影响

官方 ICLR 2026 定向全文筛读发现：Mathesis 已研究 NL 数学问题→Lean formalization→proof 的流程并给出 LLM-assisted 语义评分与专家标注；DExploration 已从 Lean proof dependencies 构造 DAG 并拓扑遍历；SCI-VerifyBench 采用 expert-grounded answer-equivalence 标签；verification-dynamics 工作报告 verifier 与 generator 能力及问题难度之间的交互。由此，通用 NL→formal、proof dependency DAG/topological traversal、expert answer verification benchmark 均不能单独作为创新主张。现有工作未核验 WordNet 义项/release-specific gloss spans 对方向性 typed AND/OR Horn literal 的支持，也未提供本项目所需的 source-only witness provenance 证据。该差异仍需理论定义、对比基线和人工 gold 验证，当前不能称为已证明新颖性。四篇单 reviewer targeted screen，不是 ICLR 全量综述；见Phase165报告与[机器日志](../sources/literature_screening_log_2026-10-08_iclr2026_formalization_verification.json)。

## Phase 166：WordNet/gloss 2026 直接近邻更新

冻结 ACL v6 的 2026 `wordnet_gloss_lexical_relations` 九篇候选切片现有深度为全文 5、定向章节 2、摘要 2；该数字来自 exact-URL structured-log reconciliation，不是相关性纳入率。新核读发现 contextual WSD 可直接给定 sense gloss 并加入现成 WordNet hypernym 图；WordNet gloss 也已被 LLM 与外部词汇级别释义作 sense-level 相似匹配/标签转移。后一工作没有人工 spot-check labels，且下游性能只是间接校验。因此不能把 gloss→sense label transfer 或 WSD+WordNet hypernym prompting 作为宽泛创新；项目需要直接评估 sense/release-bound source span 对 directional typed rule 的蕴含，并独立重放 proof。未有该类项目 gold 或 matched baseline，窄差异仍是假设。见Phase166报告与[机器日志](../sources/literature_screening_log_2026-10-08_acl2026_wordnet_slice_phase166.json)。
### Phase 167：AAAI 2026 formalization 与 rule execution 新近边界

官方选篇显示，固定 ontology/gloss 下的 NL→FOL+SMT 评测、逻辑扰动、selective translation/backward reasoning、数学 autoformalization、NL statute→Prolog execution 均有 2026 先例。应把本项目的 ontology/referent/type、formula construction、gloss-span fidelity、formal replay、source provenance 与 NLI accuracy 分轴；不能从 SMT 或程序执行正确直接推断 source semantics。目标中的精确 WordNet sense/release-bound span-support 与 source-only witness replay 仍无匹配 gold/baseline，仍是假设。记录见Phase167报告和[结构化日志](../sources/literature_screening_log_2026-10-08_aaai2026_formal_logic_neighbors.json)。Track A protocol choices remain unresolved; no pair generation or schema migration was performed.

### Phase 168：匿名既有稿件与用户成果归属边界复核

本轮对核心文档与现存阶段记录的全文搜索未发现把 AAAI 2027 匿名稿件的成果直接归给用户；用户已明确否认作者/成果归属，文档也标记为不可公开引用/分发。修正综合报告中易混淆的“用户提供”措辞，定位备忘录补入 Phase166–167 的公开 prior-art 收窄结论，并更新本页状态快照。尚未独立核验稿件作者、投稿状态、许可或冻结包完整来源权利；这些仍为外发/发表 gate。见Phase168报告。

### Phase 169：Track A 实施门槛与协议边界

现有 400 项 source/gloss frame 的输入锁只做字节完整性与 schema preflight，且 `protocol_signed=false`、未外部注册、未授权分发；Phase153 提出的 relation-edge/surface source-support 与 exact-condition NLI gold 是不同 estimand、标注单位和候选框。当前 exporter 的 hash-pinned manifest 校验、source verifier 的 payload/sense/gloss 校验，不证明来源使用许可、人工语义支持或 cluster-valid calibration。先解决 exact release rights 与研究协议，再建独立 Track A manifest；不改旧锁、不把现有 400 项 frame 当新研究 gold。细节和实施顺序见Phase169报告。

### Phase 170：近期逻辑级评测近邻

CoNLL 2026 主会的 logical table-to-text 评测显示，NLI/表格验证器选择会改变结果；人审将真正 LF 不忠实、被表格蕴含但偏离目标 LF、以及 verifier false rejection 分开。其任务不是词典释义，且人审仅单人有限样本。NALOMA 2026 workshop 的 Presburger model-set semantic distance 给出形式公式语义级比较方法，但实验基于合成数学文本，量词仍常丢失；不能作为 gloss-support 指标。项目要分别报告形式有效性、确切输入条件 NLI、gloss-span support 和 source-only replay。见Phase170报告与[结构化日志](../sources/literature_screening_log_2026-10-08_logic_evaluation_neighbors_phase170.json)。

### Phase 175：当前冻结 AND/OR 图与 witness 复算

现态冻结包重放核对了完整正 Horn closure、manifest/checksum graph SHA、nodes/head 与 hyperedges/rules 一致性，以及全部 110,425 条 witness 的结构和深度；所有检查通过。最小深度分布 median 320/P90 379/max 396，全部已选 witness 已是最浅。Phase175 初次比较把根包含 exact loss 与不含起点的 descendants 混用；Phase179 统一排除根后为 66/85 高估、19/85 相等、0/85 低估，不能据此替代闭包重算；本次精确删除影响全部非零，但不能推出 basis 全局最小。Phase14 最小深度 JSON 与现态输出逐字节一致；Phase6 主审计已重跑并新增非根损失/对齐比较字段。结论只针对冻结正 Horn 表示，不涉及 gloss 语义。见Phase179更正报告、Phase175报告与两份[冻结图审计](../outputs/phase175/frozen_hypergraph_current.json)、[minimum-depth审计](../outputs/phase175/minimum_witness_current.json)。

### Phase 174：ACL Findings 2026 推理时 NL2FOL 纠偏先例

LSEG 用逻辑保持表面变体和内部层熵进行推理时干预，并以 FOLIO/MALLS logical equivalence 评价；单篇全文筛读。其论文缩小“逻辑纠偏+公式等价评价”的宽泛创新空间，但不测 WordNet sense、gloss-span→typed Horn source support 或 source-only witness replay。它不是项目 matched baseline；公式等价、程序证明有效与来源语义支持需分开评价。固定 ACL v6 候选框及 denominator 未改，检索仍不是系统综述。见Phase174报告和[筛读日志](../sources/literature_screening_log_2026-10-08_lseg_nl2fol_findings_acl2026.json)。

### Phase 173：PMC OA 文章级许可边界

PMC 官方说明 Open Access Subset 的许可按文章变化，应查看各文章许可声明；OA 标签不能覆盖嵌入的第三方材料。当前两个候选 payload 分属两个 profile，文章身份、source_version 和逐项条款均未绑定，自动获取方式也未审计。rights log 已登记官方规则，但这不清除本地 payload 权利；exact-label crosswalk 为 25/90 profiles、2,348/3,595 计数，未匹配 65/90 profiles、1,247 计数，`release_clearance` 仍为 `not_assessed`。见Phase173报告与[机器交叉表](../outputs/phase173/source_rights_crosswalk_current.json)。

### Phase 172：Glottolog 5.3 来源家族级证据

官方 Glottolog 页面列出 5.3 发行文件并声明该版本为 CC BY 4.0；本地 privacy-filtered profile 为 3 个 payload，但 source_version/source_ontology 缺失，未绑定具体发行文件、记录或哈希。rights log 增至 17 个标签；exact-label 命中为 23/90 profiles、2,346/3,595 profile-payload 计数，仍有 67 个 profile/1,249 个计数未匹配。登记了官方家族级发布/许可证据，不等于具体本地 payload 权利清除；总 `release_clearance` 仍为 `not_assessed`。见Phase172报告和[机器交叉表](../outputs/phase172/source_rights_crosswalk_current.json)。

### Phase 171：现态来源覆盖与 OEWN witness lineage

最新 exact-label crosswalk 显示精确匹配仍是 22/90 profile（2,343/3,595 profile-payload 计数）；相较 Phase52，rights evidence 输入 SHA 已变化但覆盖数不变。六个 exact-release OEWN payload 当前重放仍得到 6/6 sense-index 唯一引用、11/11 clause-hyperedge join、6/6 selected witness checksum 验证；仅 2 个 selected-witness source document 具备候选 payload path 与匹配 ILI/definition hash。该 lineage 是结构证据，不是 gloss-support gold、上游子来源独家归属或发布许可。详见Phase171报告。

### Phase 183：Quokka 正确性与验证效用先例

COLM 2026 Quokka 将候选 invariant correctness 与目标验证的增量效用拆开测量，保留 verifier inconclusive，并报告相对 UAutomizer 的增量 solved cases 及计入 LLM 成本的端到端耗时；GPT-5.2 的增量解题数随 60s/500s 预算由 21 降至 1。该程序验证证据收紧了项目评价边界，但不能作为 gloss-support 方法或数据 baseline。当前项目仍缺人工 source-span support gold、matched verifier utility 对照及相关效应数据；所有窄差异继续为研究假设。定向单篇筛查，不是系统综述或新颖性证明；见Phase183报告和[机器日志](../sources/literature_screening_log_2026-10-08_colm2026_verifier_utility_quokka.json)。

### Phase 184：现态冻结图与 witness 证书复算

两条仓库分析 CLI 在当前工作区成功重放。Phase184 冻结图审计与最小深度审计 JSON 分别与 Phase175 对应文件逐字节一致；冻结规则 SHA 未变，integrity lock、全闭包、节点/超边对账和 witness certificate 均通过。selected witness 全部达到最小深度。该结果支持形式表示内的当前可复算性，不证明 gloss 语义、sense 正确性、来源许可、全局最小 basis 或论文效果；source-span gold 与 release clearance 门槛仍未解除。见Phase184报告和[产物目录](../outputs/phase184/frozen_hypergraph_current.json)。

### Phase 185：OEWN 输入身份与版本化许可 notice

400/400 raw gloss 与固定 OEWN 2025 Plus 归档完全匹配，但 v3 frame 有 1 条 POS 不一致、1 条 lemma set 不完整；blind batch 与 frame 一致，故继承这两项问题。官方 tag-pinned 许可 notice 已记录哈希，并由官方 WordNet 3.1 release context 对齐底层版本；这没有形成法律清权。`protocol_signed=false`、无 external preregistration ID、`distribution_authorized=false`，混合来源 bundle clearance 仍为 `not_assessed`。v3 锁定文件未修改；研究方案批准后如需修正身份字段，应从 pinned release 新建 frame 版本。见Phase185深度报告与[机器证据](../sources/oewn_2025_plus_annotation_release_rights_review_2026-10-08_phase185.json)。

### Phase 186：Track A schema 与实现契约交叉审计

静态哈希绑定审计确认：现有 instance-relation/0.2 是固定 `instance_of` 的双义项 span 格式，其候选 producer 抽取 instance membership/lift/challenge；claim-review NLI manifest 只绑定单一 source sense 与 premise/hypothesis hash，dev selector 还要求每个 group 一行；blind importer 则把单义项任务合并为 0.4–0.7 draft canonical record。三条线可复用校验模式，但不能直接表达 Track A 的普通 hypernym relation-edge、parent surface、逐 premise-condition NLI 和独立 raw-gloss support gold。协议未确认前不迁移 schema。机器 crosswalk 与边界见Phase186 深度报告及[代码哈希记录](../sources/track_a_schema_contract_crosswalk_2026-10-08_phase186.json)。

### Phase187：固定 OEWN 版本的 hypernym 候选底表

基于 v3 锁定的 400-sense target IDs 和固定 OEWN 2025 Plus archive，builder 枚举 322 条 direct `hypernym` edge（310 个 child senses、311 个 parent senses），按 edge 展开 parent 的全部 release lemma 得 680 个 surface rows；条目级 release POS/lemma 均来自 archive，而不取用存在 1 条 POS、1 条 lemma-set mismatch 的锁定 frame 字段。审计输出无 gloss/hypothesis/label/split，已由 `.gitignore` 排除。此资源候选总体不是 semantic support gold、NLI 标签或规则抽取性能。见Phase187 深度报告、[机器 replay audit](../sources/oewn_hypernym_candidate_inventory_audit_2026-10-08_phase187.json)及本机忽略的[候选清单](../outputs/phase186/oewn_hypernym_candidate_inventory.json)。
### Phase188：候选 surface 政策的 workload 情景

固定 target 集合的 322 条 direct hypernym edge 中，noun 占 264 edge/507 parent surfaces，verb 占 58/173；310 个 child senses 中 12 个有两条 parent edge。对 Phase153 两个 premise 条件和双标建议计算，选择一个 child lemma surface/edge 时 all-POS 需 2,720 次 NLI 判断、noun-only 2,028 次；若纳入所有 child lemma × parent lemma combinations，则为 4,424 与 3,364 次。该差异要求明确 child lemma policy，但不是 power、有效样本量或协议选择。现有 IID calibration gate 仍不能直接覆盖 edge/surface 多行。见Phase188 深度报告和[机器聚合审计](../sources/oewn_hypernym_candidate_workload_audit_2026-10-08_phase188.json)。
### Phase189：EMNLP 2026 主会题录与 workshop 覆盖分层

官方 accepted-main-papers 页检索结果仍只有标题和页脚，正式会程仅列主会 oral/poster 场次；ACL Anthology 的 EMNLP 2026 定向检索与 event URL 当前也没有可核对的单篇主会记录。因此 main/findings paper-level coverage 继续 pending，未命中不能解释为没有相关研究。官方 workshops 列出 AKBC 2026；其 lex-NLI 接收论文已在 Phase103/130 全文筛读，属于近期强邻接，但不是 main-track 记录，也没有新增计数。详见Phase189报告和[机器日志](../sources/literature_screening_log_2026-10-08_emnlp2026_availability_refresh_phase189.json)。
### Phase190：Phase187→188 候选工作量链路独立重放

现态运行 `python -m src.analysis.audit_oewn_hypernym_candidate_workload --output outputs/phase188/oewn_hypernym_candidate_workload_phase190_replay.json`，新输出与 Phase188 原 workload JSON 逐字节一致，SHA-256 均为 `d9a8562968e4386e4f9f038cb295b9717c94f47ad8f8c55a396c0132ffa8ae98`；builder、auditor、lock、frame、OEWN archive 与 inventory 输入哈希也分别与既有审计记录一致。该证据限于当前固定数据和聚合工作量，不证明 gloss 支持、gold 有效性、power 或项目效果；锁定 frame 的一条 POS mismatch 和一条 lemma-set mismatch 仍待决。见Phase190报告及[机器审计](../sources/oewn_hypernym_candidate_workload_replay_2026-10-08_phase190.json)。
### Phase191：locked frame/release mismatch 的候选影响审计

新增聚合审计器连接 frame 身份差异和 direct-hypernym inventory：1/400 POS mismatch 对应 0 条 edge，因此 noun 候选仍为 264 edges/507 parent rows；1/400 lemma-set mismatch 对应 1 条 noun edge，locked-frame surface 投影的 all-child pair 为 1,105，pinned-release surfaces 为 1,106。两类 mismatch 不重叠。源记录存在两个 lemma-list variants，但不能仅据此裁定研究目标应采用哪个版本；新 pair context 依现有 provenance 设计继续采用 pinned release，locked v3 frame 未改。详见Phase191报告和[机器审计](../sources/oewn_candidate_identity_impact_audit_2026-10-08_phase191.json)。

### Phase192：unsupported NLI 内容效应按关系拆分

Evaluator 现在对 `not_supported` 样本按 gold neutral、contradiction、discordant entailment 分层，并在 plausible/implausible/uncertain 格中报告计数、三分类混淆矩阵和 false-positive rate；neutral、contradiction 的 plausible-minus-implausible FPR gap 分开给出，合并 non-entailment gap 仅为辅助量。草案 JSON 重复键已清除，缺任一比较格仍返回 `null`。本轮没有真实数据或模型结果、未运行测试/CI；设计草案仍未签署、未注册，指标尚未接入 strict route。见Phase192报告。

### Phase193：NLI 诊断条件分母隔离

发现 evaluator 的 plausibility strata/content-effect gaps 曾把独立合理性分层、匹配合理性对和无关上下文对合并，导致不同 estimand 共用分母。现已只让 `plausibility_stratum` 进入分层与 gap；两类配对样本仅进入各自配对结果。Evaluator 输出版本升至 0.2，并保留旧 unsupported gap key 作为合并辅助值的兼容别名。静态审查和 CodeGraph 索引确认新代码位置；未运行测试/CI，无真实数据结果。详见Phase193报告。

### Phase194：NLI sidecar 跨 split 身份泄漏防护

Validator 此前只以 `group_id` 检查 dev/test 泄漏，无法发现错误 group assignment 导致的同一 sense、claim 或相同文本输入 hash 跨 split。现新增这些可见身份字段的独立 split-membership 检查，并包括 context hash；错误信息仅报告泄漏字段类别，不输出具体 ID/hash。lemma、改写族及上下文模板家族仍须预先合并进 `group_id` 连通分量，当前字段不足以自动验证这一上游步骤。未运行测试/CI 或读取数据；边界见Phase194报告。

### Phase195：可复算的 NLI leakage component 构造

新增 `src.analysis.build_nli_diagnostic_leakage_components`，仅接受 opaque example IDs 与 namespace/hash leakage keys，使用并查集生成传递闭包 group ID，输出成员映射、组件大小分布和输入 hash。该工具不读文本/标签、不生成 pair、不分配 split 或 statistical unit；哈希不构成匿名化。当前仅做源码结构审阅与 CodeGraph 索引，未用真实输入或运行测试；见Phase195报告。

### Phase196：witness DAG 的树展开压力

冻结图中的 selected witness DAG 有 664,732 条依赖边，全部 110,340 个非 basis witness 都达到最小深度；递归展开后，99,144/110,425 个根的树节点出现次数超过 10^12。在同深度 clause alternatives 内，108,224/110,340 个 selected witness 根并非其固定递归选择定义下可达到的最小树规模。该结果说明共享 DAG 对压缩证明至关重要，也显示“最小深度”与“最小展开树”是不同目标；它不证明较小证明更忠实或更有语义支持。分析器及边界见Phase196报告。

### Phase197：最小深度下的 compact witness 选择

新增确定性策略：只在最小 grounded depth 的 clauses 中选择递归树节点出现次数最小者，平局按 body 字典序；新生成的 witness certificate 由现有 validator 校验，独立递归大小也与动态规划逐 head 对齐。对比 selected witness，树展开 median/P90/max bit length 从 66/83/91 降到 63/80/88，超过 10^12 次出现的根从 99,144 降到 97,131；DAG edge count 则从 664,732 增至 666,435。结果仅为形式图成本优化，不能说明 semantic support、证据忠实度或实际运行资源改善；该策略没有设为默认 witness，也未修改 frozen graph。详见Phase197报告。

### Phase198：compact witness 来源索引链路

对 5,802 个与原 selected clause 不同的 compact witness 选择做索引级核对：110,340/110,340 条规则仍有 active source-document link，所有 link 都能映射到对应 head 的 `source_records` 并有 checksum sidecar metadata；selected 与 compact 均链接 110,382 个 source documents。本轮未读取 source payload bytes，因而未重新验证新增 clause 来源文件的实际 SHA/identity，也没有 semantic support 判断。见Phase198报告及[机器审计](../sources/compact_witness_source_trace_audit_2026-10-08_phase198.json)。

### Phase199：compact witness 来源 payload 的全量字节/身份复核

对原 selected 与 compact witness 两种关联集合的 110,399 份 payload 并集（17,588,076,573 bytes）逐文件重算 checksum/byte count，并将 payload synset identity 对齐各自 witness head。两侧各 110,382 个 source-document/head pairs 全通过；hash、字节数和 identity mismatch 均为 0。此闭合冻结 bundle 内的字节与结构来源链，但仍不证明自然语言 gloss 支持规则或 license clearance。见Phase199报告及[机器审计](../sources/compact_witness_source_trace_audit_2026-10-08_phase199.json)。

### Phase200：变更 clause 的 source logic / WSD branch 结构对齐

对 5,802 个 changed heads 的 selected/compact clause 分别与 payload DNF part branches 的 automatic WSD synset-ID union 比较。精确 branch-union match 为 129/5,802 vs. 137/5,802；配对 head 中 compact-only 59、selected-only 51、两者均命中 78、均未命中 5,614。subset match 为 5,676 vs. 5,679，配对 compact-only 7、selected-only 4。所有 payload checksum/identity 复核通过。微小净差异是事后描述性 WSD 结构诊断，无统计推断，不证明语义支持或紧凑方案更忠实。详见Phase200报告与[机器记录](../sources/compact_witness_source_logic_alignment_2026-10-08_phase200.json)。

### Phase201：ACL 2026 跨视图逻辑推理先例与主张边界

ACL 2026 长文 *Discovering a Shared Logical Subspace* 已通过自然语言/符号逻辑配对表示学习跨视图子空间，并在多种逻辑 benchmark 上做推理时干预；因此“联合自然语言与符号表示改善逻辑推理”不是可单独主张的新颖点。它仍未处理词典义项绑定、逐释义 span 对 Horn literal 的支持标签或 source-payload-bound witness replay。结合 Phase200，目前形式闭合的结论仍局限于冻结 bundle 的来源字节/身份与自动 WSD-ID 分支结构重合；语义支持、许可证与项目效果均未证实。详见Phase201报告、[筛读日志](../sources/literature_screening_log_2026-10-08_acl2026_shared_logical_subspace_phase201.json)和[Phase200机器记录](../sources/compact_witness_source_logic_alignment_2026-10-08_phase200.json)。

### Phase202：Track A 当前代码接口无法直接接成端到端 gold 路线

固定 OEWN inventory 提供 322 个 relation edges / 680 parent-surface rows，但不含 gloss、渲染 hypothesis、标签或 split；现有 claim-review manifest 是 child-sense 单 premise/hypothesis，未绑定 parent surface/`relation_edge_id` 或分别绑定 raw-gloss/rendered-premise hash；盲标 importer 则是单义项 gloss 分析返回。代码有可复用的完整性/哈希模式，但当前不存在直接可跑的 Track A 路径。设计合同形状仍取决于 source-support 单位、exact-condition NLI、surface/POS 选择和统计/校准单位；这些决定前不生成 candidate pair 或 schema。详见Phase202报告及[机器审计](../sources/track_a_implementation_compatibility_audit_2026-10-08_phase202.json)。

### Phase203：KCR 进一步收窄图路径和 trace reward 主张

ACL 2026 KCR 已将冲突上下文变成文本与局部图推理路径，并用 embedding/distribution 与字符串相似奖励优化 trace/答案一致性。因此，通用图路径和 trace consistency reward 不能单独主张新颖。KCR 不判断 WordNet gloss span 对 typed Horn literal 的支持，也不提供 source-bound proof replay；它的 LLM reward 不是形式 oracle。项目窄化假设仍未证实。见Phase203报告与[机器日志](../sources/literature_screening_log_2026-10-08_acl2026_kcr_graph_reasoning_phase203.json)。

### Phase204：H1–H3 有反驳判据，但还不能作效果判断

当前协议已规定支持、反驳与不可判断三类结果，故核心假设不是不可证伪；但 primary estimand/阈值、候选数据合同、双人 gold 与 matched runs 均未冻结/获得。结构证书和 payload identity 的现有证据不蕴含 gloss semantic support、H1 效果、H2 表示收益或 H3 人审效用。逐项状态、有限证据和反驳读数见[Phase204 主张—证据交叉表](research_claim_evidence_crosswalk_2026-10-08_phase204.md)与深度报告。

### Phase205：source-only proof/NLI strict route 尚不兼容 Track A 双哈希与 edge 身份

源码静态追踪发现，composed route 将 `premise_sha256` 与 raw source gloss hash 作为同一身份绑定，并以 `wn_sense:<sense_id>` 为 query 键。故已渲染的 lemma+POS+gloss premise 不能通过现有来源绑定，现 manifest/route 也不能绑定 relation edge 与 parent surface。可复用的是单义项规则编译、来源 payload 校验与形式证书 replay；不能将其计作 Track A pair/edge 端到端能力。见Phase205深度报告和[机器兼容性审计](../sources/track_a_proof_route_compatibility_audit_2026-10-08_phase205.json)。

### Phase206：冻结图与最小深度 witness 的现态复算

当前 `frozen_hypergraph_audit` 和 `minimum_witness_audit` 在 Python 3.13.9 下重跑成功，分别与 Phase175/184 输出字节哈希一致。冻结正 Horn 图结构、basis closure 与 witness certificate 未漂移；85 项 basis deletion 中 witness descendants 对精确 AND/OR closure loss 高估 66 次、相等 19 次，没有低估。它们不是精确删除影响替代物。此项不覆盖全部 payload 重哈希、释义语义支持、许可或 NLI/人工效果。可复跑命令、输入与源码哈希见Phase206报告和[机器记录](../sources/frozen_graph_witness_replay_2026-10-08_phase206.json)。

### Phase207：Git 仓库尚未建立初始版本基线

当前 `master` 无 commit，tracked files 为 0；893 个非忽略未跟踪文件、390 个忽略文件。此状态不能支持 repo-level diff 或完整源码树提交身份；Phase206 的文件级 hash 记录仍能绑定具体复算，但不构成提交历史。首个 commit 应在审阅纳入范围、压缩档与数据边界后建立。本轮未暂存或提交。见Phase207报告和[机器摘要](../sources/git_provenance_readiness_audit_2026-10-08_phase207.json)。
**Phase217 更新（2026-10-08）**：三篇定向筛读分别约束 external factuality/context faithfulness、结构化 AMR 视图的表层线索效应、validity/plausibility 混淆。研究评估应将固定 release/sense 词汇事实、人工 gloss-span support、形式 proof replay 和模型内容效应分为不同终点。本轮没有 gold、matched baseline、项目效果或许可状态的新证据；Bertolazzi et al. 仅摘要级。详见Phase217报告与[筛读日志](../sources/literature_screening_log_2026-10-08_faithfulness_validity_plausibility_phase217.json)。
**Phase218 现态复核（2026-10-08）**：重跑 v3 input preflight（400/400、24 strata、0 回传、`integrity_pass=true`）和 presentation preview audit（两槽各 400 项、`integrity_pass=true`），但两者均不授权分发，protocol 未签署；pinned-release 对账仍有 1 项 POS 与 1 项 lemma-set mismatch。release inventory 15 项一致性检查均过，但 clearance 仍是 `not_cleared_for_public_release`。因此 v3 文件可内部重放但不可据此启动人工标注；Track A 独立 estimand/design 尚未冻结，不能生成 pair/gold/split。详见Phase218报告与[机器记录](../sources/annotation_and_track_a_launch_readiness_audit_2026-10-08_phase218.json)。
**Phase219 设计草案（2026-10-08）**：独立 Track A v1 规定 edge-level source-span support 为主终点、child sense 为抽样 PSU、两种 exact premise 条件的 NLI 为配对次级模型评价，并提出四名 NLI 标注者的平衡不完全区组，以避免同一标注者重复看相同 pair 和固定 rater-condition 混淆。方案明确 264/507/841 旧框架工作量不是 power 证据；新 frame、估计单位、child surface、reference 结构、精度目标和许可/授权仍未确认。无 pair、label、split 或 schema 生成。见[设计草案](track_a_protocol_v1_draft.md)、Phase219报告和[机器记录](../sources/track_a_protocol_design_review_2026-10-08_phase219.json)。

**Phase220 来源权利覆盖审计（2026-10-08）**：Phase24 候选来源中 25/90 profiles 与 18-label 权利日志精确匹配，65/90 未匹配；profile-payload 计数合计 3,595，不是唯一记录数。此结果用于安排 MeSH/OLS 与非规范来源族的版本和记录级绑定工作，不构成任何 clearance。研究设计 gate 未裁决，gold、matched baseline、效果与新颖性证据仍缺。详见Phase220报告与[机器 crosswalk](../sources/source_rights_coverage_audit_2026-10-08_phase220.json)。

**Phase221 MeSH/OLS 来源绑定（2026-10-08）**：5,625 个来源族 payload checksum 通过；631 个目标 evidence objects 均有 external ID 和 locator 字段，但均缺 download URL。130 个同 payload direct-MeSH/OLS-MeSH ID 经 token normalization 后可在当前 NLM REST API 逐项解析。OLS 当前版本 metadata 可读，但冻结数据仍无法绑定具体 cache snapshot；未据此推断许可或公开授权。项目的研究性 gold、matched baseline、有效性/新颖性证据仍未补齐。详见Phase221报告与[机器审计](../sources/mesh_ols_record_binding_audit_2026-10-08_phase221.json)。

## Phase222 来源 evidence 捕获合同（2026-10-08）

当前 checkout 未找到 `source_evidence` producer；新 schema/合同仅为未来 acquisition 定义输入绑定、上游版本、API/artifact hash 和获取时间，不更改或回填冻结数据。由此，来源身份可解析与历史版本/字节可验证仍是两个不同状态，当前来源包的许可/公开状态不变。集成 gate 是找到原 producer 或建立 versioned acquisition component，然后实现 schema 校验和端到端 replay；这项前向合同本身不构成 gold、效果或新颖性证据。见Phase222报告、[合同](source_evidence_capture_contract.md)和[schema](../config/source_evidence_capture.schema.json)。

## Phase223 外置 producer 与结构 replay 边界（2026-10-08）

Recovered history 保存了 `Wn2Lingua/KaikkiBasisHeldoutEvaluation` 描述性标签，却没有 producer 实现 hash；所引源文件不可用，bundle 仅含 graph reader。尽管 154,206/154,206 clauses 有 source-DNF evidence，canonical replay 只精确匹配 110,424/110,425 heads。故历史数据结构可部分核验，端到端生成过程不可复现；该结果也不提供 gloss semantic gold。捕获 schema 已补 producer/parser/normalizer hash 必需项，等待新 acquisition component 落地。详见Phase223报告和[机器审计](../sources/source_producer_boundary_audit_2026-10-08_phase223.json)。

## Phase266：当前冻结图证明链与 v3 输入锁复放（2026-10-08）

当前 v3 preflight 仍是 21/21 检查通过、400 项、24 strata、0 个回传；其脚本和输入 lock 与 Phase218 的 SHA-256 相同，协议未签署且分发未授权。bounded source-linked witness/Datalog bridge 现态重放通过：3,596 节点、14,923 条依赖边、3,512 条 ground rules，Phase117 保存的来源链 artifact 仍绑定当前 bundle；Phase266 报告与 Phase148 逐字节相同。历史 bridge 的唯一 mismatch 仍为后续加入的 proof-certificate `source_bindings`、`source_claim_refs` 格式字段。本轮未重读全部来源 payload。以上只证明固定 bundle 下结构和指定 Horn proof 可重放，不验证 gloss 语义支持、WSD、开放世界蕴含、许可或整体方法效果。详见Phase266 报告与[机器审计](../sources/phase266_current_state_audit_2026-10-08.json)。
