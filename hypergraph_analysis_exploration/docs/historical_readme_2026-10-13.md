# 汇报与核心报告索引

- [15 分钟汇报稿](../../report/research_progress_deep_review_2026-10-12_phase278.md)：可直接用于汇报。
- [Phase278 结构审计](../../report/research_progress_deep_review_2026-10-12_phase278.md)：本轮依赖超图复算及输出说明。
- [Phase277 会议任务对齐](../../report/project_review_2026-10-29-current.md)：当前探索与学长任务的对应关系。
- [Phase276 Lingua-Graph 对照](../../report/project_review_2026-10-29-current.md)：论文联系及研究边界。
- [Phase275 旧结论复核](../../report/research_progress_deep_review_2026-10-12_phase278.md)：早期普通图指标的有效性审查。
- [Phase272 冻结图基线](../../report/research_progress_deep_review_2026-10-12_phase278.md)：AND/OR 闭包与 witness 复算基线。

# OEWN 定义依赖超图：可复算结构审计与后续研究

本项目分析学长提供的冻结 OEWN 定义依赖包，并为“定义 → 形式逻辑 → 可验证推理”建立可复算基线。现有成果包括 Horn AND/OR 结构闭包/witness DAG 审计、正 Datalog 证明证书和 NLI 评测/拒答原型，以及 OEWN 2025 Plus 上的资源内词面 baseline。早期 Phase 9 使用 200 条 pilot；当前人工研究准备是 400 条、24 层的候选确认性标注框（raw gloss 400/400 与 OEWN 2025 Plus 精确匹配，effective definition 为 376/400），**尚未分发或标注，不是 gold data**。目前尚未实现经验证的自然语言到逻辑编译，也没有基于人工 WordNet gold data 的语义蕴含、上下位或 NLI 评测；词面 baseline 只与同一 OEWN release 的直接 hypernym 关系做资源内对照。

归属边界：用户已明确说明工作区中的匿名 AAAI 2027 稿件不是其成果；本项目只把它视为受限内部 prior-work 对照，不能将该稿件的贡献、实验或数据写成用户成果。仓库内实现和复算是否形成新的论文贡献，仍须以许可、贡献记录、人工 gold 和 matched evaluation 证明。

## 先读这些

- Phase207 Git 版本历史审计：当前 `master` 无初始提交；未跟踪工作区范围与后续基线建议见报告。
- [Phase207 Git 状态机器摘要](../sources/git_provenance_readiness_audit_2026-10-08_phase207.json)：只存文件状态计数，不含文件内容或完整路径清单。

- Phase 206 冻结图与 witness 现态复算：Python 3.13.9 现态复跑与 Phase175/184 输出完全一致；AND/OR basis deletion 影响读数也重现。
- [Phase 206 machine replay record](../sources/frozen_graph_witness_replay_2026-10-08_phase206.json)：记录配置、lock、脚本和输出 SHA-256，以及本轮未重哈希全量 payload 的边界。
- Phase 205 Track A strict route 兼容性审计：现有 route 将 rendered premise hash 与 raw gloss hash 绑定；edge/surface identity 需要新版合同。

- Phase 164 相关工作补查：新增官方 NeurIPS 2025 / ICML 2025–2026 定向筛读；区分 proof validity、verifier quality、source fidelity 与 plausibility；不是系统综述。
- [Phase 164 结构化文献日志](../sources/literature_screening_log_2026-10-08_icml2026_neurips2025_formal_verification.json)：记录官方来源、筛读深度、去重与局限。
- 最新深度报告 Phase 163：当前重放 115,235 个 sense-index 来源 payload 的字节数与 SHA-256 校验全部通过；source rights 仍未评估。
- [Phase 163 当前来源 payload 机器结果](../outputs/phase163/source_release_metadata_audit_current.json)：只保存汇总分类、计数与哈希，不含 gloss、义项 ID 或来源路径。
- Phase 162 bundle integrity 重放：六个锁定结构文件与 semantic fingerprint 匹配。
- Phase 161 环境审计：维护 Python 依赖与仓库外数据复算边界；未运行 CI/测试。
- Phase 160 typed route 诊断审计：typed route 可审计性更新；pipeline `/13`；未运行测试或真实 0.7 回放。
- Phase 159 相关工作增量：ACL Industry Track T²、Findings ACL FoVer、SemEval Task 11；只作相关工作边界，不提供项目 matched baseline。
- [Track A 设计裁决备忘录](track_a_design_decision_memo.md)：列出 scope、gold/context、estimand/statistical unit、noun/verb coverage 的建议与未决点；候选 pair 生成前需冻结。
- [研究就绪度与论文主张审计](research_readiness_audit.md)：最新状态与证据边界。

- Phase 75 sort judgment provenance schema/compiler：新增实验 schema 0.6、unresolved 拒绝编译、sort 依据随规则与证明 provenance 保留，并将该字段纳入 IAA 比较；不证明类型判断正确。

- Phase 74 gloss referent/type 契约草案：把词义来源身份、Horn referent variable 和 sort 分开；提出 `Entity/Eventuality` 实验性域，梳理 WordNet gloss semantic parsing 先例及待验证门槛。

- Phase 73 OEWN 类型来源审计：profile 固定 OEWN 2025 Plus 的 POS、45 个 lexname 和两类 hypernym relation；lexname 不直接作为 sort 层级，instance_hypernym 与 hypernym 分开。

- Phase 72 typed proof/countermodel strict route：端到端验证 variable sort 传递、certificate/countermodel replay 和 NLI 高分下的篡改拒绝（合并回归 66 项通过）。

- Phase 71 typed replay 行为验证：直接验证 sort 域、type-table hash 与错 sort countermodel atom 的拒绝行为（10 项 synthetic tests 通过）。

- Phase 70 annotation 到 typed Horn 的变量 sort 传递：新增实验性 schema 0.5 与 compiler v4；v3 标注草案保持 0.4，人工类型来源和真实语义效果未验证。

- Phase 69 类型环境哈希绑定：让 typed proof/countermodel replay 精确绑定 versioned type table；运行时 tampering behavior 仍未验证。

- [Typed Datalog 输入契约](typed_datalog_contract.md)：描述显式版本化 sort/signature 下的参数类型兼容检查，并区分它与 gloss 语义支持。
- [Gloss referent/type 契约草案](gloss_referent_type_contract.md)：记录 unary Horn 变量的实验性语义解释、类型边界与拒绝条件；尚未接入正式标注 schema。

- [研究就绪度与论文主张审计](research_readiness_audit.md)：把结构复算、证明/NLI 原型、人工 gold、许可/归属与发表前依赖按证据状态分开，列出下一阶段 gate。
- 阶段性深度分析报告：汇总当前 goal 的工程进度、研究结论边界与后续证据门。
- Phase 41 来源记录 verifier 复查：记录新 source-payload 完整性门、旧失败日志与当前测试时间线的静态核查；未运行测试。
- Phase 42 IJCAI 2026 全目录补筛：官方 proceedings 目录级词项筛查，没有新增明显标题级近邻；不作为穷尽检索或新颖性证据。
- Phase 43 来源提供方条款复核：更新 GCIDE 0.54 与 NLM MeSH 2026 官方版本/复用证据，冻结 payload 映射与整体清权仍未完成。
- Phase 44 NCIt/OLS 来源复核：记录 NCI 专用 CC BY 4.0 与 NCIt 格式/版本信息；OLS payload 到具体发布仍未绑定。
- Phase 45 ACL 2026 规则图近邻：RGCWM 已有显式规则依赖图与动态证据状态，项目贡献定位需进一步收窄。
- Phase 46 AAAI 2027 归属与定位审计：区分匿名既有稿件、当前冻结包复算和用户新研究，并修正历史文档中缺失的归属语境。
- Phase 47 NLI/source-support schema 对齐：修正过时字段说明，区分 canonical gloss-support annotation 与 NLI pair-review sidecar。
- Phase 48 冻结来源索引字段审计：确认索引本身未记录上游 release/format/license 身份；结论不外推到 payload。
- Phase 49 核心假设可证伪性审查：将端到端增量、AND/OR 结构价值和证据辅助审计写成支持/反证/不可判定矩阵；仍无 gold、matched 结果或新颖性结论。
- Phase 50 来源画像/权利日志对账：新增仅处理聚合元数据的精确标签 crosswalk；统计日志可定位性，保留别名、版本映射与许可兼容为未决事项。
- Phase 51 三个来源家族官方证据补录：补充 OEWN 2025+、Wiktionary 与 ChEBI 官方页面边界并重算 crosswalk；页面条款仍未绑定具体 payload/entry/release。
- Phase 52 GO/IUPAC 版本线索审计：补入 GO 和 IUPAC Gold Book 官方版本/许可说明；具体 release、term ID 与 payload hash 仍未绑定。
- Phase 54 非规范来源元数据审计：对最大来源画像簇计数字段形状并安全提取 host；未恢复 provider，标为 unresolved provenance。
- Phase 55 COLM 2026 组合证据验证近邻：筛读三篇新主会工作，分别收窄组合证据核验、逻辑保持压力测试和 verifier/语义 grounding 的贡献边界。
- Phase 68 typed Datalog signature checker：加入基于版本化 sort/predicate-signature 的闭包与证书校验；类型表仍由调用方提供，不代表 WordNet gloss 语义已验证。
- Phase 67 ACL 2021 逻辑/证明近邻与实现审计：筛查 14 篇关键词近邻、核读六篇官方 PDF，并区分现有 unary Datalog/proof pipeline、尚未连接权威本体的 typed checker 与缺失的 source-support gold。
- Phase 32 深度分析报告：记录 2024 年自然语言形式化/证明近邻筛查、固定 ACL v3 对账进度及其对研究主张的限制。

- [既有 AAAI2027 稿件与新研究定位](research_positioning_and_prior_work.md)：区分匿名既有稿件、当前冻结包结构复算和待验证的新贡献；该稿不是用户成果，也不是可公开引用材料。
- [完整审计报告](../../report/project_review_2026-10-29-current.md)：已复算事实、版本差异、历史分析风险与阶段结论。
- [Selected-witness DAG 复用剖面](selected_witness_dag_profile.md)：区分所有 OR 候选 clause 引用与实际单 witness 证书 DAG 的全量依赖复用统计。
- [全候选依赖弧投影 SCC 审计](dependency_projection_scc.md)：分开报告候选依赖简单图中的强连通分量与无环 selected-witness；不将投影循环解释为 Horn 证明循环。
- [AND/OR 超图压平损失审计](flattening_ablation.md)：在同一 basis 下对照规范闭包、普通弧存在/合取读法及最小推导深度；普通图总体可达集合相同并不意味着证明结构相同。
- [最小 witness 深度审计](minimum_witness_audit.md)：重算每个 head 在冻结正 Horn 图中的最小 grounded 推导深度，并比较现有证书与规范 witness DAG。
- [局部最小深度 witness 的 basis 支持包络](minimum_witness_basis_support.md)：在不拍平 OR-of-AND 规则的前提下，统计 85 个结构 basis 在局部最小深度 witness 家族中的可能/必现支持；结果不是语义重要性或所有全局最浅证明集合。
- [全局最小高度 witness 的 basis 支持包络](global_minimum_witness_basis_support.md)：按根的最小高度预算纳入所有可行子证明，分层比较 depth/OR/AND 结构上的 basis 支持变化；与 Phase 17 局部最小口径并列对照，不代表语义正确性。
- [全量活跃来源 payload 普查](full_source_payload_census.md)：对 112,609 个活跃来源文件逐项校验冻结 checksums，并聚合比较 source part/WSD 与已归属 graph clause。
- [source-record 来源/许可元数据普查](data_release_gate.md#source-record-来源许可元数据普查phase-23)：只读核验索引所引用的全部来源 payload，汇总来源家族、版本标识与显式许可字段覆盖；报告不包含 gloss、义项 ID 或 source path，也不构成清权。
- [Selected-witness 来源链审计](selected_witness_source_lineage.md)：对全体已选 witness clause 直接复核 source link、payload 哈希/字节数和 source-synset identity；不把来源可追溯误称为 gloss 语义支持。
- [冻结包 basis 构成审计](basis_composition.md)：按 POS、来源处理类别和 ID namespace 汇总 85 个结构种子，避免将其未经验证地称为语义原语。
- [冻结包 replay 单例差异](frozen_bundle_replay_exception.md)：对照 bundle 的唯一 canonical-replay mismatch 与其权威 clause 选择政策；保留差异而不擅自改图。
- [方法与评测协议](method_and_evaluation.md)：逻辑对象边界、错误分型及后续评测设计。
- [逻辑蕴含与 NLI 原型](logic_verification.md)：Datalog 证明检查、NLI 评测接口与 abstention 策略。
- [冻结超图 integrity lock](../config/frozen_bundle_integrity_lock.json)：单目标 witness 与 Datalog bridge 重放前固定 bundle manifest、checksums、rules、coverage witnesses、senses index 和来源构建 contract 的内容哈希；锁是本地完整性锚点，不是签名或语义证明。
- [Phase 16/38 OEWN hypernym 校验器](phase16_oewn_hypernym_verifier.md)：面向显式 synset 对的直接/多跳路径证书；附带 360 项九层 resource-only stress frame 及独立回放。不是 gloss 语义 gold 或准确率基准。
- [相关工作梳理](related_work.md)：定向先例、可能的研究切口和待补系统检索。
- [ACL Anthology 固定候选框 Phase 91 全局对账](../outputs/phase91/acl_screening_coverage.json)：以 1,747 条 2016–2026 候选对账 90 个结构化日志，1,286 条有精确 URL 日志记录，461 条尚无任何全局匹配；显式全文 75、定向章节 134、元数据/摘要 851、深度未明 226。旧 v1/v2、v3 和阶段筛读计数保留作历史快照。候选 URL 匹配不是相关性纳入或系统综述完成。详见[检索协议/筛读记录](literature_search_protocol.md)和Phase 91 报告。可复算命令：`python -m src.analysis.audit_acl_screening_coverage`。
- [ACL 2026 形式逻辑候选筛读](../sources/literature_screening_log_2026-10-06_acl_formalization_2026.json)：对 `definition_to_formal_logic` 词族 24 条候选先作题名/摘要决定，再对 10 条作官方 PDF 定向章节复核；记录限定在方法、评测和局限段落，不等于全文/附录穷尽阅读、系统综述纳入或新颖性结论。
- [自然语言定义形式化与评测筛读](../sources/literature_screening_log_2026-10-05_autoformalization_evaluation.json)：EMNLP 2025 数学定义形式化、人工等价 gold 与自动评测指标的边界；不外推为 WordNet gloss 结果。
- [NL→FOL + SMT 论文筛读](../sources/literature_screening_log_2026-10-05_nl2fol.json)：Findings IJCNLP-AACL 2025 的逐步 FOL 编译、pairwise NLI、solver 反模型及多前提 conjunction 失败模式。
- [Entailment-Preserving FOL 筛读](../sources/literature_screening_log_2026-10-05_epf.json)：ACL 2025 EPR 指标的任务、prover 过滤和其不代表 source-formula fidelity 的边界。
- [2026-10-03 逻辑化管线补充筛读](../sources/literature_screening_log_2026-10-03_logic_pipeline.json)：全文核对 NL2Logic、SemEval 2026 模块化 FOL 系统与 AAAI Hybrid KB；区分下游 NLI proxy、证明模块和 WordNet gloss-source-support gold。
- [2026-10-03 图上逐步核验补充筛读](../sources/literature_screening_log_2026-10-03_graph_verification.json)：全文核对 ICLR 2026 VoG，区分 KGQA 一致性核验与 AND/OR Horn 证明，并记录结构读出假设及其待 gold 验证状态。
- [最接近工作的逐项对照](closest_work_comparison.md)：输入/输出、义项与逻辑结构、证明与来源、评测及项目可检验差异。
- [相关工作工件可复现性审计](../sources/literature_artifact_availability_2026-10-06.json)：核对四项最近邻工作的代码/数据入口、仓库快照与许可证声明；未获授权的资源尚未复制。
- [gold slice 标注协议草案](annotation_protocol.md)：schema 0.3 的 WordNet gloss 标注、语义支持原因码、双人标注和分层评测约定（尚无 gold data）。
- [候选确认性抽样设计 v3](annotation_study_design_v3.md)：400 条、24 层且每层至少 2 条的可复算抽样框；400/400 raw gloss 已核对 OEWN 2025 Plus 并导出盲标包，effective definition 仅 376/400 精确匹配。2026-10-06 text-free preflight 对锁定输入哈希、400 项覆盖和 24 层结构检查通过；任务仍未分发或标注，且 lock 的 `protocol_signed=false`、`distribution_authorized=false`，许可审查、preregistration 和真实 gold 均未完成。
- [v3 预注册方案草案](annotation_preregistration_draft_v3.md)：将目标、估计量、盲标、非应答、探索性区间与停止规则整理成可审阅文本；仍未签署或登记，材料许可和人员安排未解决。
- v3 输入材料有机器可读冻结锁 [config/annotation_preregistration_v3_lock.json](../config/annotation_preregistration_v3_lock.json) 和 text-free 审计入口 `python -m src.analysis.audit_annotation_preregistration_v3_inputs`；通过只说明输入哈希/结构匹配，不授予分发权限或表示已注册。取得双人回传后，先用 `python -m src.analysis.audit_annotation_response_coverage <annotator-a.jsonl> <annotator-b.jsonl>` 记录分层覆盖与 schema 状态，再导入和分析。
- v3 本地盲标输入：`outputs/phase7/annotation_batch_2025_plus_v3_400_blind.jsonl`。答案键与 manifest 是独立文件，均被 `.gitignore` 排除；不要将答案键发给标注者。
- [可复现标注候选抽样器](../src/analysis/annotation_sampling.py)：随机面板不依赖图复杂度特征；诊断面板分别富集 OR 分支、宽 AND 和深 witness，图特征对标注者盲化。
- [双标注一致性分析器](../src/analysis/annotation_agreement.py)：随机 panel 在绑定匹配的抽样与盲标 manifest、且完整配对回传时，可计算设计加权类别 κ，并逐标注者报告分析状态、Horn 投影、关系、语义支持与原因码 presence 的设计加权边际比例。原因码为可重叠多标签。边际比例区间是未经稀有比例模拟校准的探索性截断 Wald 区间；非普查零方差时抑制区间，不将独立标注分布解释为共识或裁决真值。κ 零观察分歧时只报告点估计；少于 10 个配对分歧时附探索性警告。诊断 panel 不作总体估计，AST/span/F1 和 item bootstrap 仍是未加权探索性结果。尚无真实双人回传。
- [版本化双槽呈现计划生成与 text-free 审计](../src/analysis/randomize_annotation_presentation.py)、[呈现材料完整性审计器](../src/analysis/audit_annotation_presentation.py)：使用版本化 SHA-256 counter-Fisher–Yates 生成跨 Python 版本可复算的 task-ID 顺序，manifest 绑定算法/生成器源码 hash；可复核四个盲标字段及答案键排除。当前输出仅为 git-ignore 的本地草稿，manifest 明示未授权分发。运行 `python -m src.analysis.audit_annotation_presentation` 只输出计数、状态与哈希，不输出 gloss/task ID。
- [加权 κ 区间设计模拟](../src/analysis/simulate_annotation_kappa_ci.py)：按 v3 真实 24 层配置比较 Taylor 与 delete-one jackknife Wald 区间。四种中等场景条件覆盖率约 94.3%–95.3%；稀疏边际高一致性场景在抑制零分歧区间后，条件覆盖率约 97.9%/99.7%，但可报告率仅约 35%。结果是方法诊断，不是实际标注结果；复算命令和边界见 [v3 抽样设计](annotation_study_design_v3.md)。
- [边际比例区间设计模拟](../src/analysis/simulate_annotation_prevalence_ci.py)：按 v3 设计、5 个合成有限总体/场景 × 1,000 次抽样，比较 clipped Wald 与 logit/arcsine 诊断区间。Wald 在稀有及层间异质场景的条件覆盖率约 89%–90%，候选变换也各有未达名义覆盖的情形；这些区间继续标为探索性，结果不代表真实标注分布。复算命令和完整边界见 [v3 抽样设计](annotation_study_design_v3.md)。
- [数据来源与许可审查](data_provenance.md)：冻结包混合来源、版本缺口、OEWN 许可与公开数据边界。
- [数据发布门槛](data_release_gate.md)：源码许可未声明、冻结包逐来源许可缺口、OEWN pinned archive 哈希与逐输出发布审查要求；这不是法律意见或发布授权。
- [数据发布清单只读校验器](../src/analysis/verify_data_release_inventory.py)：复核本地上游 ZIP 哈希/CRC、归档内许可提示声明、根许可文件状态和冻结包 manifest；一致性通过不代表获得发布许可。
- [Outputs 文件级发布面扫描器](../src/analysis/audit_output_release_surface.py)：只记录输出路径/哈希、JSON 字段名和 Git 忽略状态，不输出字段值、不作发布清权；详见[发布门槛](data_release_gate.md)。
- [Markdown 本地链接审计器](../src/analysis/audit_markdown_links.py)：检查项目 Markdown 中的相对文件链接、heading anchors 与越出项目根目录的链接；不请求或验证外部 URL。运行 `python -m src.analysis.audit_markdown_links`。
- [持续集成检查范围](continuous_integration.md)：跨 Python/操作系统的编译和单测矩阵，以及 CI 不能证明的科学有效性边界。
- [可复算开发环境](reproducible_development.md)：核心 Python 环境、外置数据边界与结果复算记录约定。
- [检索与筛选记录](literature_search_protocol.md)：检索式、来源、纳入标准和系统性限制。
- [2026-10-03 相关工作检索与方法学审计](literature_review_audit_2026-10-03.md)：补充多源检索可达性、AAAI/ACL 2026 全文核查、语义标准 E 与可计算验证 V 的区分；明确不是穷尽系统综述。
- [Phase 9 释义 genus 词面基线报告](phase9_gloss_genus_baseline.md)：200 条样本上的候选覆盖和 OEWN 直接 hypernym 资源一致性检查，不是语义 gold。
- [Phase 11 OEWN 全量名词 genus 词面基线](phase11_gloss_genus_release_baseline.md)：84,909 个名词 synset 的资源内结构对齐 census；不是语义准确率或冻结图评测。
- [Phase 12 释义上下文 sense-ranking 基线](phase12_gloss_sense_rank_baseline.md)：在同一全量候选上增加不使用 hypernym 标签的词项重叠 sense 排序；覆盖率和资源内 proxy 结果均需按 abstention 与评测边界解释。
- [文献筛读日志](../sources/literature_screening_log_2026-10-02.json)：新增官方来源候选、全文筛读状态与逐项纳排理由。
- [2026-10-03 VSPO 补充筛读日志](../sources/literature_screening_log_2026-10-03_vspo_supplement.json)：追加 AAAI 2026 KRR 主会的定义–ontology 逻辑错配工作全文核查、方法/评测边界与项目 mutation-test 启示。
- [相关工作检索协议](literature_search_protocol.md)：定向 scoping review 的范围、查询、纳排、局限与全文复核。
- [2026-10-03 文献初筛日志](../sources/literature_screening_log_2026-10-03.json)：ACL/AAAI 2026 三篇相邻工作的官方摘要筛读记录。
- [2026-10-03 精选全文复核日志](../sources/literature_screening_log_2026-10-03_fulltext.json)：6 篇 ACL/AAAI/LREC 相关官方 PDF 的全文核查；主会、workshop 与 symposium 分列。
- [2026-10-03 后续文献补充日志](../sources/literature_screening_log_2026-10-03_late_supplement.json)：6 篇 provenance、autoformalization、verifier 与 KG benchmark 相关全文的定向筛读；含精确查询、venue 状态和边界。
- [2026-10-03 sememe 碰撞补充日志](../sources/literature_screening_log_2026-10-03_sememe_supplement.json)：EMNLP 2025 SememeLP 与 ACL 2026 Structured Sememe Knowledge 的方法/结果/局限重点全文核对；重新收窄“释义→结构化语义→词汇关系”研究主张。
- [2026-10-03 GraphRefine 定向全文筛读](../sources/literature_screening_log_2026-10-03_graphrefine.json)：补充 ACL 2026 source-grounded KG refinement 近邻，区分人工源忠实度标签、模型 judge、错误类型与覆盖，且不把跨域工作误作 WordNet 直接基线。
- [2026-10-03 faithfulness/uncertainty 补充筛读](../sources/literature_screening_log_2026-10-03_selective_faithfulness.json)：全文核对 ACL 2026 SAVeR 与 NeurIPS 2025 formalization uncertainty；启发局部错误类型、结构不确定性和 abstention/cost 评测，但不作为 WordNet 直接基线。
- [2026-10-03 NL-FOL/逻辑幻觉补充日志](../sources/literature_screening_log_2026-10-03_logic_hallucination_supplement.json)：核对 AAAI 2026 固定 ontology 的 NL-FOL 基准和 *SEM 2026 逻辑后果式幻觉分类，补充分层评测边界。
- [2026-10-03 顶会超图读出全文筛读](../sources/literature_screening_log_2026-10-03_hypergraph_readout.json)：全文核对 ACL 2026 HyperCoT、AAAI 2026 HGRAG、NeurIPS 2025 HyperGraphRAG；区分 n-ary 事实/检索超图与 directed AND/OR Horn 依赖超图，列出可迁移的路径/读出成本实验和不可混同的 proof 结论。
- [2026-10-03 WordNet source/gold 补充筛读](../sources/literature_screening_log_2026-10-03_wordnet_source_gold.json)：全文核查 GWC 2025 AI-WordNet、LREC 2026 OEWN 形容词关系资源及 WordNet—人类直觉对照；区分 relation exact match、下游效用、人类关系判断与 gloss-span 支持。
- [2026-10-04 OpenAlex 候选集与筛选日志](../sources/literature_screening_log_2026-10-04_openalex.json)：8 个可复跑 title/abstract 查询、43 条去重候选、逐条筛选理由；补入 SymbCoT、乌克兰 WordNet hypernym extraction、prover-guided NL-to-FOL repair、FOLDCoVe 四个不同层级的方法邻居。该轮仍是单人定向 scoping supplement，不是完整系统综述或 novelty audit。
- [2026-10-05 ACL 近期 WordNet/gloss 候选筛读](../sources/literature_screening_log_2026-10-05_recent_acl_wordnet_slice.json)：对 2024–2026 切片新筛 18 条标题/摘要，9 条保留；五篇保留候选已有定向章节核验，涵盖 LREC-COLING 2024 主会、OntoLex 2025 workshop 与 OSACT @ LREC-COLING 2024 workshop；指标和语义支持边界已逐项记录。
- [2026-10-05 proof 与 decompositional NLI 先例筛读](../sources/literature_screening_log_2026-10-05_logic_proof_and_decompositional_nli.json)：全文核对 LREC-COLING 2024 GFaiR 与 EMNLP 2024 RDTE/TREEWISE，进一步区分步骤可证明性、上下文论证充分性和 gloss-span 来源支持；也记录 RDTE 论文样本数的内部冲突。
- [2016–2019 ACL 定义与 WordNet 候选筛查](../sources/literature_screening_log_2026-10-06_acl_wordnet_direct_2016_2019.json)：对固定候选框中 82 条待筛记录完成标题/摘要分层（1 direct、43 adjacent、35 background、3 exclude），并定向核读三篇论文；筛查不是穷尽综述或纳入结论。
- [2023 ACL WordNet 候选筛查](../sources/literature_screening_log_2026-10-06_acl_wordnet_direct_2023.json)：对固定候选框中 12 条待筛记录完成标题/摘要分层（0 direct、7 adjacent、4 background、1 exclude）；筛查不是穷尽综述或纳入结论。

- [EMNLP 2024 Unigram-FOL 全文筛读](../sources/literature_screening_log_2026-10-06_unigram_fol.json)：声明式 synthetic FOL/NLI 生成及 Vampire 证明适合作形式引擎压力测试参考，不是 WordNet gloss-support gold。
- [ACL/COLING 2025 与 TACL 2026 多证据检索补充筛读](../sources/literature_screening_log_2026-10-06_evidence_retrieval_supplement.json)：全文核读 ETS、Counting-Stars，摘要筛读 Ev2R；强调联合证据集、上下文位置/长度及证据对结论的支持需分开评价。三篇原在旧 v2 框外发现，已由 v3 新词族召回；Ev2R 为摘要级筛读，不改 v1/v2 历史计数。
- [EACL 2026 Logic Haystacks 全文筛读](../sources/literature_screening_log_2026-10-06_logic_haystacks.json)：长上下文中以形式化生成、可证明不干扰干扰项和反事实删除评测矛盾证据定位；此文在固定候选框外发现，不影响候选池对账计数，也不是 gloss-span gold。
- [LREC-COLING 2024 Diff-Comb Explainer 全文筛读](../sources/literature_screening_log_2026-10-06_diff_comb_explainer.json)：ILP 解释子图选择及答案/解释分轴指标；faithfulness 不等于 gloss 来源蕴含或 proof replay。
- [ACL 2024 MALLS / LogicLLaMA 全文筛读](../sources/literature_screening_log_2026-10-06_malls_nl_fol.json)：核对 NL→FOL 翻译数据、CFG 过滤、人工质量评估与错误类型；其句子级通用语料不等于 WordNet gloss-span 支持 gold。
- [ICLR 2026 ProofFlow 全文定向筛读](../sources/literature_screening_log_2026-10-06_proofflow_iclr2026.json)：依赖 DAG 约束数学证明形式化及 ProofScore 结构/语义/语法评测均属已有先例；区分 proof-step graph 与 AND/OR Horn witness DAG，不把不同对象直接宣称为新颖贡献。
- [Findings ACL 2026 推理边界补查](latest_related_work_addendum_2026-10-06.md)：总结 GRIL 的缺前提检测/暂停策略，并区分信息不足、gloss source-support、NLI contradiction 和程序反模型；该文为 ACL v3 冻结候选框外发现。
- [Findings ACL 2026 逻辑密度近邻](../sources/literature_screening_log_2026-10-06_slkd_findings_acl2026.json)：SLKD 以 LLM 逻辑分解、拓扑深度和操作符数指导数据选择；区分其 reasoning-potential proxy 与本项目的冻结图结构统计及 gloss-source-support gold。
- [IJCAI 2026 逻辑归纳与 proof-tree 近邻](../sources/literature_screening_log_2026-10-06_ijcai2026_logic_neighbors.json)：筛读 NRI 的 proposition-level DNF induction 与 VANESSA 的 textual-entailment + prover + proof-tree 路线；均为定向官方 PDF 筛查，不是 gloss-support matched baselines。

## 可复跑工具

在项目根目录运行（Python 3.10+，仅用标准库）：

```powershell
python src/analysis/frozen_hypergraph_audit.py
python -m src.analysis.audit_frozen_bundle_replay_exceptions
python -m src.analysis.hypergraph_complexity_profile
python -m src.analysis.dependency_projection_scc
python -m src.analysis.flattening_ablation
python -m src.analysis.minimum_witness_audit
python -m src.analysis.minimum_witness_basis_support
python -m src.analysis.global_minimum_witness_basis_support
python -m src.analysis.selected_witness_source_lineage
python -m src.analysis.full_source_payload_census
python -m src.analysis.basis_composition_audit
python src/analysis/witness_query.py oewn-00520548-n
python -m src.analysis.verify_witness_certificate outputs/phase6/witness_oewn-00520548-n.json
python -m src.analysis.verify_witness_datalog_bridge outputs/phase6/witness_oewn-00520548-n.json
python src/analysis/annotation_sampling.py
python src/analysis/annotation_source_audit.py
python -m src.analysis.full_source_index_audit
python -m src.analysis.source_clause_alignment_audit
python -m src.analysis.export_source_clause_mapping_tasks
python -m src.analysis.suggest_source_part_spans
python -m src.logic.source_clause_alignment_validator outputs/phase8/source_clause_mapping_tasks.jsonl
python src/analysis/oewn_release_crosscheck.py
python -m src.analysis.gloss_genus_baseline --output outputs/phase9/gloss_genus_baseline_2025_plus_200.json
python -m src.analysis.gloss_genus_release_baseline --output outputs/phase11/gloss_genus_release_baseline_2025_plus.json
python -m src.analysis.gloss_sense_rank_release_baseline --output outputs/phase12/gloss_sense_rank_release_baseline_2025_plus.json
python -m src.analysis.oewn_hypernym_verifier config/hypernym_claims.example.jsonl --output outputs/phase16/oewn_hypernym_verification.json
python -m src.analysis.verify_oewn_hypernym_certificates outputs/phase16/oewn_hypernym_verification.json config/hypernym_claims.example.jsonl --output outputs/phase16/oewn_hypernym_replay.json
python -m src.analysis.verify_data_release_inventory
python -m src.analysis.audit_source_release_metadata
python -m src.analysis.search_related_work_openalex --output sources/openalex_related_work_2026-10-04.json
python -m src.analysis.annotation_agreement outputs/phase7/annotations_annotator_a.jsonl outputs/phase7/annotations_annotator_b.jsonl --output outputs/phase10/agreement_summary.json
python -m src.analysis.export_annotation_batch
python -m src.analysis.import_annotation_returns returned_annotator_a.jsonl --output outputs/phase7/annotations_annotator_a.jsonl
python -m src.logic.datalog_checker path\to\program.json
python -m src.logic.verified_reasoning_pipeline annotations.jsonl problem.json --output outputs/phase9/query_result.json
python -m src.logic.nli_gate path\to\nli_predictions.jsonl --confidence-threshold 0.9 --model-id nli-model-name --model-revision immutable-commit-or-sha256
# Pair CLI below is exploratory Wilson analysis; composed routing uses the fixed-grid exact-binomial selector.
python -m src.logic.nli_gate --dev-predictions outputs/nli/dev_predictions.jsonl --test-predictions outputs/nli/test_predictions.jsonl --minimum-precision 0.9 --model-id nli-model-name --model-revision immutable-commit-or-sha256 --output outputs/nli/test_report.json
python -m src.logic.annotation_validator path\to\annotations.jsonl
python -m src.logic.annotation_to_datalog path\to\annotations.jsonl --output outputs/phase7/compiled_rule_library.json
python -m unittest discover -s tests
```

结构审计输出到 `outputs/phase6/frozen_hypergraph_audit.json`；basis 元数据构成输出到 `outputs/phase6/basis_composition_audit.json`（85 项中名词 37、动词 23、形容词/卫星形容词 9、副词 3、介词 13；72 个 OEWN namespace、13 个非 OEWN namespace），仅说明结构种子的组成，不是语义原语验证；完整解释见[basis 构成审计](basis_composition.md)。复杂度剖面输出到 `outputs/phase6/hypergraph_complexity_profile.json`，记录 AND 子句宽度、每个 head 的 OR 候选数、所选 witness 深度及深度分层、全部规则依赖扇出，以及选定 witness DAG 的依赖复用；witness DAG 解释和边界见[单 witness 复用剖面](selected_witness_dag_profile.md)。当前包中 witness 深度中位数 320、P90 379，最大 396；29,161 个 head 有多个候选 clause。Phase 14 最小深度重算显示现有 110,425 条 witness 全部已达到各自最小 grounded 深度；详见[报告](minimum_witness_audit.md)。这些结构剖面仅用于后续抽样/压力测试设计，不代表自然语言或语义推理难度。查询输出到 `outputs/phase6/witness_<sense-id>.json`。phase7 抽样器生成不含 gloss 的候选框和 manifest；来源结构审计写入聚合 JSON；OEWN cross-check 默认对已解压的 2025 Edition JSON 分别比对 source raw/effective gloss。运行前按官方 URI 下载对应 ZIP 到项目 `tmp/` 并解压；2025 Plus 可通过 `--release-dir`、`--release-archive`、`--release-name`、`--release-uri` 和 `--output` 参数指定。盲标 pilot 导出器要求候选 raw gloss 全部与固定 2025 Plus release 精确匹配，并产生 blind batch、单独答案键和 attribution manifest；答案键不得发给标注者。若输出已存在，更新时显式添加 `--force`。冻结包默认读取项目同级的 `OEWN`，也可用 `--bundle` 指定其他版本。

phase8 的 `full_source_index_audit` 全量扫描 sense 索引元数据，不打开近 18.9 GB 的 source JSON payload，并核对全量 active source-clause lineage 覆盖；`source_clause_alignment_audit` 校验当前 200-sense frame 所选源文件哈希，并追踪来源 part/WSD ID 与 active graph clauses。两者只输出聚合结构诊断，不含 gloss、sense ID 或文件路径。报告和边界说明见[数据来源与许可审查](data_provenance.md)；来源链接覆盖或对齐计数不能替代人工语义 gold。

Phase 15 现对所有 112,609 个活跃 source JSON payload 做只读结构普查，合计读取 18,134,793,487 字节；逐文件的大小与 SHA-256 均与冻结包 `checksums.jsonl` 一致。所有 payload 的 AND/OR logic tree 可解析，108,727 条来源记录的 DNF 分支数与归属 graph clause 数相同，但只有 3,123 条来源记录的完整 WSD 分支 ID 多重集与图 literal ID 多重集完全相同。后者是结构集合相等，不是 2.77% 语义准确率；证据和解释边界见[全量普查报告](full_source_payload_census.md)。

映射审查导出器复用已验证的 OEWN 2025 Plus raw gloss，并输出 source part/logic 与 active graph clause 的匿名任务；这些任务暴露候选系统结构，因此不是盲测 benchmark。答案键与完整任务文本均由 `.gitignore` 排除，许可未清完前仅限本地。schema validator 可以先只传任务文件检查结构，收到返回后再附加回传 JSONL 检查完整性和证据 span；通过校验不代表语义标签正确。

所有 witness 输出均标记为**结构性定义可用性证书**，不是自然语言语义证明。`verify_witness_certificate` 独立对照冻结 bundle 的 semantic fingerprint、witness 子句、来源索引引用、DAG 边和拓扑序复核导出 JSON；`verify_witness_datalog_bridge` 再把选中的 witness 子句转换为 ground Horn 程序，独立重放 Datalog 证明，并要求证明节点与依赖边多重集和结构证书完全一致。桥接只验证所选图规则的结构闭包，不验证 gloss 语义，也不覆盖其他 OR 子句。桥接结果默认写到 `outputs/phase6/witness_<sense-id>_datalog_bridge.json`，并由 `.gitignore` 排除，避免把本机 source 文档路径意外纳入发布。查询默认最多展开 10,000 个节点；大 DAG 超限时可调 `--max-nodes`，不要默认导出整个语料的全部证明树。

逻辑原型目前只支持有限、无函数符号、无否定的正 Datalog；它不读取 frozen concept graph，也不包含 NLI 模型。AST 编译器只处理经过人工审阅的单变量一元正谓词，必要方向限 atom/AND，充分方向限 atom/AND/OR 且 DNF 最多 64 分支；仅 `semantic_support=supported` 且置信度不低于 medium 的 claim 才编译，其他状态会保留为拒绝记录。组合管线可将规范标注、facts 和 query 一次运行并输出可重放 program 与 proof certificate，但不自动解析 gloss，也不证明规则忠实。输入 schema 和边界见[逻辑蕴含与 NLI 原型](logic_verification.md)。

冻结包默认路径由 `config/project_config.json` 的 `data_source.root` 解析，非绝对路径以项目根目录为基准；所有相关命令仍可用 `--bundle` 显式覆盖。上游包不随项目复制/发布，复算前需按数据来源文档核验版本、manifest 与权限。

## 当前冻结包基线

- 110,425 个 head、154,206 条 Horn 子句、917,767 个依赖 literal。
- 85 个冻结包标记的结构基础项，正 Horn 闭包复算覆盖全部 head；这本身不证明其为普适语义原语或全局最小集合。
- 29,161 个 head 有多个 OR 候选子句；子句体为 AND。
- 依赖头缺失、自依赖、空子句、重复子句均为 0。
- 最大 witness 深度 396；深度 301+ 的 head 占 62.53%。
- 全部 110,425 条 witness 记录完整且唯一；seed 与 basis 一致，非 seed 深度均等于 `1 + max(依赖深度)`，重复/缺失/多余节点及深度错误均为 0。
- 85 项逐一删除均降低覆盖，但这**只说明单删不可冗余，不证明全局最小基数**。

审计值由脚本从冻结包重算，详细内容见 JSON。其他历史的“普通图最短路”、旧版 SCC、Louvain、超图聚类展开、随机空模型或语义社区解释仍未复核，不能替代 Horn 闭包证书或语言学有效性标注。当前新增的[依赖弧投影 SCC 审计](dependency_projection_scc.md)只报告定义清楚的简单图投影结构，同样不声称语义有效；历史状态见完整审计报告。

## 目录约定

```text
config/       项目配置
docs/         维护中的方法、评测和相关工作说明
archive/      未验证的 phase 1–5 探索源码与原始规划（只读保留）
src/analysis/ 当前可复用的冻结包审计、witness 查询、结构复杂度剖面、抽样与来源核对工具
src/logic/    独立的逻辑证明、NLI 评测与标注结构校验原型
tests/        AND/OR、proof certificate、NLI abstention 单元测试
outputs/      可复现的阶段结果；临时脚本仅放项目内 tmp/，确认无用即清理
reports/      审计报告和历史工作记录
```

本 README 中列出的核心审计、logic 原型和测试只用 Python 标准库。phase1–5 普通图投影探索脚本及其辅助模块已从 `src/` 移至只读归档 `archive/legacy_phase1_5/`，对应历史结果仍留在 `outputs/phase1`–`phase5` 和 `reports/`，均未删除，也不属于当前核心 API。它们使用的第三方依赖/旧导入路径未经整理，不承诺可直接复跑。当前可运行入口只列核心审计、来源审查与逻辑原型。

数据包保持外置、只读，不复制进项目。运行前应确认其版本、哈希及授权/许可；不要将匿名投稿稿件、来源原文或未获许可的数据提交到公开仓库。

## 研究边界

当前包把释义分析结果编码为正 Horn 依赖关系。`h` 的 clause 依赖只说明指定定义/解析流程如何支持图中的概念可用性；它不自动意味着对象层面的 `h(x) → d(x)`，更不表示相关命题为真。计划中的定义编译需要保留 sense、类型、变量、量词、否定/情态、作用域与 provenance；NLI 是后续语义评估/筛选环节，而不是形式证明器。参见 [方法与评测协议](method_and_evaluation.md)。

- [v3-minus-v2 新候选逐条筛读](../sources/literature_screening_log_2026-10-06_acl_expanded_delta.json)：113 条增量中新增题名/摘要决定 109 条（相邻 68、背景 33、排除 8），另复用既有深筛 4 条；13 篇优先全文候选均已核读官方 PDF；结构性边界与逐篇局限见增量筛读日志。该轮结束时的 screened 阶段快照为 440/1,747，随后规范化的 443/1,747 是历史快照；当前全局状态以 Phase 91 为准。



### Phase 33 研究进展

参见阶段性深度分析报告。本轮对 ACL v3 两篇 formal NLI/proof-tree 论文作定向筛读，明确 proof-tree 可读性、形式查询复现和来源语义支持属于不同证据层。

### 核心方法证据边界

参见[Source-only 证据链契约](source_only_evidence_contract.md)和Phase 34 阶段审计报告。它们按当前 validator/compiler/prover/source verifier 实现列出哪些输出可被复算，以及哪些语义、许可和模型效果仍需要独立证据。


### 当前逻辑编译器范围

compiler v5 仍只编译共享单一目标变量的一元正 Horn/Datalog 片段。实验性 annotation schema 0.5 可传递裸 variable sort，0.6 可携带 sort judgment provenance 并拒绝 unresolved assignment；可选 typed checker 仍只对调用方签名表做形式校验。多元/量词逻辑、权威 WordNet 类型本体与类型判断语义依据仍未实现/验证。详见[标注协议](annotation_protocol.md)、Phase 75及[Source-only 证据链契约](source_only_evidence_contract.md)。

本轮范围审计记录：Phase 35。
### Phase 36：ICML 2026 跨会场摘要级补查

新增两篇 ICML 2026 宽泛背景邻居：attention token graph 上的推理验证，以及形式验证驱动的 verified code generation。只核对官方 proceedings metadata/abstract，不作为 WordNet gloss-support 的直接 baseline；此补查不改变 ACL v3 统计。范围与限制见Phase 36 深度分析及[结构化筛查日志](../sources/literature_screening_log_2026-10-06_icml2026_verification_supplement.json)。
### NeurIPS 2025 跨会场近邻补查

新增两篇主会工作并核读官方 PDF 相关章节：模型隐藏状态推理图的拓扑分析，以及 KGQA 的先验约束与路径回退。结论是要区分模型状态图、知识图路径约束和 source-bound proof DAG；前两者均不等于 WordNet gloss-span 支持证据。筛读范围与限制见[结构化日志](../sources/literature_screening_log_2026-10-06_neurips2025_graph_verification.json)。

### Phase 40：IJCAI 2026 定向近邻筛读

新增两篇 IJCAI 2026 官方论文记录：VANESSA 已将 textual entailment、符号推理与 proof tree 结合；NRI 已研究可迁移的 DNF 规则归纳。相关工作、对照矩阵、检索协议和就绪度审计同步更新。筛读收紧了宽泛创新主张，但不证明项目更窄的 gloss-span→有向 Horn support 任务新颖或有效。详见Phase 40 报告及[逐篇机器记录](../sources/literature_screening_log_2026-10-06_ijcai2026_logic_neighbors.json)。

### Phase 41：source-record verifier 与组合路由复查

静态复查确认 source verifier 现在检查冻结包锁、sense index、source payload 字节/checksum 和精确 gloss 字段绑定。旧失败日志早于当前测试修改，不能说明当前测试通过或失败；本轮没有运行测试。该层仍不证明上游 release/许可、语义蕴含或裁决正确。详见Phase 41 报告。

### Phase 42：IJCAI 2026 全目录标题级补筛

在官方目录检索 WordNet、lexical、definition、hypernym、entailment、Horn、NLI 等词项，并与 Phase 40 已筛的 VANESSA/NRI 去重。未发现新的明显标题级近邻；该筛查只覆盖目录可见文本，不能支持会议全集无相关工作或论文新颖性结论。详见Phase 42 报告和[机器记录](../sources/ijcai2026_title_screen_audit_2026-10-07.json)。

### Phase 43：GCIDE 与 MeSH 来源条款复核

复核 GNU GCIDE 0.54 archive listing/license page 与 NLM MeSH production-year 下载页/复用条款，并将 2026-10-07 官方页面证据加入来源日志。提供方条款不等于冻结 payload 已逐条匹配 release，更不等于项目清权；详见Phase 43 报告。

### Phase 44：NCIt 与 OLS 聚合来源复核

NCI 专用条款页声明 NCIt 使用 CC BY 4.0，下载页列出 OWL 主格式及 26.09d。尚未将 OLS 缓存 payload 绑定到确切 release/字节，不构成 OLS 或项目的整体发布许可结论；详见Phase 44 报告。

### Phase 45：ACL 2026 规则依赖图近邻

RGCWM 已将 typed rule dependencies 与连续规则证据状态用于推理时规划，故“规则依赖图/状态跟踪”不应独立作为新颖主张；WordNet sense/gloss-span 支持与可重放 AND/OR Horn 证明仍是待实证研究问题。详见Phase 45 报告。

### Phase 46：AAAI 2027 归属与定位审计

匿名既有稿件不是用户成果；其报告数字不得记入新论文结果。历史 Phase 1 文档现补充了材料属性与保密边界，相关工作用语也已明确区分该稿与用户新研究。详见Phase 46 报告。

### Phase 47：NLI 与 source-support 标注记录分层

评测协议已同步当前 schema：NLI 三分类在 `claim-review-record/0.1` pair sidecar 中，方向性 gloss-support 在 canonical `0.4-draft` annotation 中，二者不能互相映射。该修正只对齐文档与现有代码，没有标注结果或授权变化；详见Phase 47 报告。

### Phase 48：冻结来源索引字段覆盖

冻结来源索引中的 115,235 条记录使用一致字段集合，但未包含上游 provider/release/version/format/license 字段，故单靠索引无法完成 NCIt payload 版本绑定。此判断不涵盖索引指向文件可能包含的其他元数据。详见Phase 48 报告。


### Phase 56：ACL 2026 NLI/逻辑候选筛查

对冻结 ACL 候选框中的 58 条 2026 NLI/逻辑记录完成逐条题名摘要筛读，并定向核读五篇官方全文；逐条理由见[机器日志](../sources/literature_screening_log_2026-10-07_acl2026_nli_logic.json)，结论和研究边界见Phase 56 深度分析。全框精确日志对账为 623/1,747，不代表相关工作纳入数量或系统综述。


### Phase 57：ACL 2026 图与来源证据候选

固定 ACL 2026 候选框已全部精确对账（295/295 有日志），其中本轮补筛剩余 117 条图/规则候选，并核读四篇官方全文。筛查结果和范围边界见Phase 57 报告及[逐条日志](../sources/literature_screening_log_2026-10-07_acl2026_graph_rule_provenance.json)。


### Phase 58：ACL 2025 WordNet 与规则推理近邻

ACL 2025 固定候选筛读发现 LORex 已用 WordNet taxonomy、定义与层级路径做 parent expansion；将其作为优先 matched-baseline 候选。筛查范围、逐篇理由和边界见Phase 58 报告和[机器日志](../sources/literature_screening_log_2026-10-07_acl2025_graph_rule_provenance.json)。

### Phase 59：来源归因与 NLI 近邻复核

ACL 2024 固定 source-grounded entailment 切片已完成 84 条题名/摘要筛查和 10 篇定向全文章节核查。来源归因、NLI 回溯和 entailment-tree 已有先例；更窄的 gloss-span→typed Horn 支持与可回放证明仍待 gold 和匹配实验检验。详见阶段报告。当前 ACL v3 对账：957/1,747 条有日志匹配，790 条待筛。

### Phase 60：ACL 2024 逻辑证明与证据树

ACL 2024 剩余 36 条 NLI/逻辑/证明候选已筛查，并定向核读八篇官方全文。FRVA、WordNet 辅助 FOL model checking、Lean 证明验证等先例进一步收紧宽泛创新主张。当前 ACL v3 对账 993/1,747；详见Phase 60 报告。

### Phase 61：ACL 2024 图规则与证据归因

对剩余 100 条 graph/rule/provenance 候选完成筛查并定向核读十篇全文。ClaimVer、TRACE、KG 规则和图遍历解释等先例已纳入对照；ACL v3 对账为 1,093/1,747。详见Phase 61 报告。

### Phase 62：ACL 2023 规则学习与 WordNet/FOL

对 ACL 2023 31 条待筛候选完成筛查和九篇定向全文核读。发现 text-to-KG rule mapping 及 WordNet–SUMO/FOL ATP 先例，相关边界已加入对照矩阵；ACL v3 对账为 1,124/1,747。详见Phase 62 报告。

### Phase 63：ACL 2023 WordNet 释义与词汇蕴含近邻

对 57 条 ACL 2023 source-grounded entailment 候选完成题名/摘要筛读，10 篇官方 PDF 定向核读。发现 WordNet sense gloss 已用于 sense-aware lexical substitution 与双向蕴含判断，收窄了 gloss/WordNet/entailment 的宽泛主张；gloss-to-Horn source support 与可回放 proof DAG 仍待 gold 和匹配实验验证。ACL v3 对账为 1,181/1,747。详见Phase 63 报告和[筛读日志](../sources/literature_screening_log_2026-10-07_acl2023_source_grounded_entailment.json)。

### Phase 64：ACL 2023 文本到逻辑与 KG 规则近邻

筛查 55 条 ACL 2023 graph/rule/provenance 与 WiCE 多证据候选，并定向核读十篇官方 PDF。SPINDLE 已展示通用 NL→typed λ/proof checking；KG 规则学习、规则扩增、path quality、FactKG、多证据 entailment 也有先例。ACL v3 对账达 1,236/1,747；gloss-span→Horn support/replay 仍是假设。见Phase 64和[日志](../sources/literature_screening_log_2026-10-07_acl2023_graph_rule_provenance.json)。

### Phase 65：ACL 2023 NLI 推理链与证据验证

对 16 条剩余 NLI/逻辑/证明候选完成筛查，九篇官方 PDF 定向核读。PROVER 已结合 commonsense retrieval 生成自然语言 NLI proof，ReCEval 评价链条步骤，SICCK 涵盖 hypernym/negation/quantifier；FEVER retrieval + entailment 也有先例。ACL v3 对账 1,252/1,747。WordNet gloss source support 与 Horn replay 仍待共同 gold 实证。详见Phase 65。

### Phase 66：ACL 2022 NL形式化与验证式证明邻居

对 20 条 2022 直接关键词候选完成定向筛查（14 邻接、5 背景、1 排除），十篇官方 PDF 定向核读。NLProofS 已实现 supplied-fact proof-tree generation + trained verifier-guided search；Dual-(m)T5 做 PL/FOL parsing + NLI；CCG/Vampire 与 ZS4IE verbalization+NLI 已有先例。ACL v3 对账 1,272/1,747。gloss-span→typed Horn source support/replay 仍待实证。见Phase 66。

### Phase 88：六条 OEWN 2025+ 来源记录匹配

审计把六条本地来源证据的 ILI 与释义散列联合对齐到固定 2025+ JSON 归档中的唯一记录，复算命令为 `python -m src.analysis.audit_oewn_2025_plus_payload_matches`。该结果没有追踪图规则 lineage，也不改变项目未清权/未发布状态。见报告。

### Phase 89：来源记录到图规则与 witness

复算六条候选来源 payload 到图 head、规则子句、hyperedges 和 selected witness 的结构连接；11 条子句及六个 witness clause 均匹配。4/6 active source-document 记录直接指向候选 payload；其余两条连接到同一 sense 下其他记录。未验证语义支持或许可。见报告。

### Phase 90：selected witness 来源绑定

细化到 selected witness clause 的来源记录后，六个 source documents 的 checksum 都有效，但只有两条与候选 payload path、OEWN ILI/释义散列及定义文本 SHA-256 精确一致。该关联不证明 gloss 语义 entailment。见报告。


### Phase 92：ACL 2022 未匹配候选筛读

完成 130 条题名/摘要筛读；22 条邻近、2 条背景、106 条排除出当前核心综合。4 篇官方 PDF 做了定向章节核读。全局复算为 1,416/1,747 精确 URL 匹配、331 条未匹配；2022 待筛清零。该统计不代表系统综述完成或新颖性证据。见深度报告、[筛读日志](../sources/literature_screening_log_2026-10-07_acl2022_unmatched_title_abstract.json)与[Phase 92 全框快照](../outputs/phase92/acl_screening_coverage.json)。


### Phase 93：ACL 2021 未匹配候选筛读与逻辑验证近邻

完成 2021 年 85 条未匹配候选筛读（26 邻近、2 背景、54 排除出当前核心综合、3 因缺摘要暂缓），对 4 篇官方论文定向核读。全框复算为 1,501/1,747 匹配、246 未匹配；剩余未匹配项在 2016–2020。见Phase 93 深度报告。


### Phase 94：ACL 2020 未匹配候选筛读与关键先例复核

完成 2020 年 94 条候选筛读（29 邻近、3 背景、62 排除出当前核心综合），并对 6 篇官方论文做定向章节核读。全框现为 1,595/1,747 匹配、152 未匹配（2016–2019）；摘要/元数据 1,143、定向 148、全文 75、旧日志深度未明 229。Abzianidze 的 NLI 标签驱动词汇关系学习、Grits 的形容词描述逻辑形式化、WikiNLI、PRover 与细粒度 source support 进一步限制宽泛新颖性表述。见Phase 94 深度报告。


### Phase 95：ACL 2019 候选筛读与定义到图路径近邻

完成 2019 年 68 条未匹配候选筛读（26 邻近、7 背景、35 排除），定向核读 4 篇官方论文。全框为 1,663/1,747 URL 匹配、84 未匹配（2016–2018）。Prokhorov et al. 已从 textual definitions 预测 hypernym/hyponym 图路径并展示 attention；E3 已从 procedural text 抽取规则并做 entailment 判断。创新假设须收窄至 gloss span 归因、sense-aware typed Horn 与独立 witness replay 的联合匹配评测。见Phase 95 深度报告。


### Phase 96：ACL 2018 定义形式化与 proof-based lexical relation 先例

筛读 38 条全局未匹配候选（18 邻近、8 背景、12 排除），定向核读 6 篇官方论文。全框为 1,701/1,747 URL 匹配、46 未匹配（2016–2017）。直接近邻包括 proof-based 短语关系发现、NL定义到OWL 2 DL、WordNet/SUMO的ATP校验，以及 lexical resources+规则模板驱动NLI。研究贡献只能作为 sense-linked gloss span→typed Horn→独立replay 的组合假设待匹配评测。见Phase 96报告。


### Phase 97：ACL 2017 词汇公理注入与自然语言定理证明

筛读最后 27 条 2017 年 unmatched 候选（17邻近、7背景、3排除），定向核读4篇官方PDF。全框为1,728/1,747匹配、19待筛（2016）。proof-gap-driven lexical axiom injection、LangPro自然语言证明、自然演绎相似度特征和解释到概念学习均有先例。研究假设须聚焦义项绑定gloss span、规则来源和独立replay。见Phase 97深度报告。


### Phase 98：ACL 固定候选框覆盖清零

完成 2016 年最后19条筛读（10邻近、6背景、3排除），定向核读5篇官方论文。1,747/1,747个冻结候选URL现均有结构化日志；pending=0，但仍有229条历史日志深度不明、1,276条仅摘要/元数据，此结果不代表全ACL召回或系统综述完成。WordNet/ontology链接、KG与规则联合嵌入、textual entailment graphs等已有先例。见Phase 98深度报告。

### Phase 102：逻辑实现范围审计

确认 gloss compiler 仅支持共享单变量一元正谓词；typed Datalog validator 则仅验证调用方提供的签名和形式程序，不证明 gloss 支持。见Phase 102 报告。

### Phase 103：lex-NLI 与 prover 的最新强邻接

复核 AKBC 2026 接收论文：它已将结构化词汇蕴含、多参考人工 gold、LLM 关系生成与 LangPro 证明评测组合起来；证明覆盖提升并不保证关系语义正确。它不是 WordNet gloss→Horn 系统，相关结果不可横比。宽泛创新主张据此进一步收窄，gloss-span support+typed rule+独立 replay 仍待 gold 实验验证。见Phase 103 报告。

### Phase 104–107：多参考 gloss gold 表示与评分原型

现有 `0.4-draft` 没有把多套可接受完整分析分成互斥 gold alternatives；语义 OR 节点也不能代替这种分组。Phase 105 增加独立 sidecar validator 与 scorer；Phase 106 加入 micro/macro 汇总并规定空 claim 对的处理；Phase 107 使核心评分 API 输出关键源码哈希和 Python runtime 指纹，CLI 另绑定输入文件哈希；Phase 108 将输出契约标识升为 `gloss-analysis-reference-score/0.2`；Phase 109 禁止完整裁决项同时保留 unresolved candidates，并将输入 sidecar schema 升为 `gloss-analysis-reference/0.2`。Phase 110 实现 gloss review 与 OEWN 关系证明的 hash/sense/pair/replay 绑定 validator，并将 replayer 摘要升至 v3；两者尚未运行验证，也没有真实 genus-sense mapping。评分逐套比较完整 alternatives，不取 references 并集；整体 exact match 要求 claim 集、canonical root AST、analysis status 全部相符。原型仍未运行验证或锁定研究协议；400 项输入锁、签署与分发授权不变。见Phase 104、Phase 105、Phase 106、Phase 107、Phase 108、Phase 109与Phase 110。
# Phase 99 更新（2026-10-07）

ACL 框外定向复核确认，BMEAUT 4lang 定义图词汇蕴含已有 2023 年期刊扩展（在线 2022）；其应纳入图式 baseline，且路径解释本身不保证 gloss source-support。ACL 固定候选框现 1,747/1,747 URL 有日志匹配，但仍有 229 项历史核读深度不明，故不代表系统综述完成。详见Phase 99 报告。

# Phase 100 更新（2026-10-07）

沿 4lang 方法线新增 BRISE-Plandok 近邻：领域手写图模式已从法规文本抽取正式规则，并以双标/作者复核 gold 做端到端评价。它不是 WordNet gloss baseline，但排除宽泛“首次图式 NL→formal rules”主张；见Phase 100 报告。

# Phase 101 更新（2026-10-07）

确认 BRISE 2021 已有 semantic graph→formal deontic rules→theorem prover 与逐步解释；6 句 toy 完美结果不是全流程量化。其与 BRISE-Plandok 是同一研究线，不能重复计为独立先例。见Phase 101 报告。


### 2026-10-08 研究状态增量（Phase 183）

最新定向相关工作筛查纳入 COLM 2026 Quokka：将形式候选正确性与相对基准的下游验证效用分开评估，并保留 inconclusive/timeout。该工作是 C 程序验证任务，不是 WordNet gloss baseline。项目评测仍须分别报告人工 gloss-span support、形式类型/证书重放与下游 proof utility；后者若开展须固定 base prover、输入和预算。见Phase183深度报告。

### Phase 184：冻结图现态复算

重跑冻结 AND/OR 图和最小 witness-depth 审计；两份输出与 Phase175 对应文件逐字节一致。当前图结构和 witness 证书未发生漂移，仍只验证形式表示内部一致性，不验证 gloss 语义支持。详见Phase184报告。



- Phase208 未见符号上的逻辑泛化近邻：定向筛读 COLM 2026 命题 Horn 逻辑 OOD 泛化论文；收窄神经符号泛化的宽泛新颖性，并将 EMNLP 2026 主会论文级覆盖维持 pending。
- [Phase208 结构化筛读日志](../sources/literature_screening_log_2026-10-08_colm2026_unseen_symbol_generalization_phase208.json)：记录作者论文、官方录用目录、全文范围、去重和任务边界。
- Phase209 现态环境与发布清单复核：维护代码 140 个 Python 文件 AST 解析通过，发布 inventory 15 项一致性检查全通过；发布 clearance 仍未解决。
- [Phase209 环境机器快照](../outputs/phase209/reproducibility_environment_audit.json)：记录当前运行时、代码树 hash、依赖静态扫描、CI 声明矩阵和外置 bundle 可见性。
- [Phase209 发布 inventory 聚合校验](../sources/data_release_inventory_audit_2026-10-08_phase209.json)：记录 15 项结果，不含绝对本机路径；通过不表示许可已清理。
- Phase210 冻结来源 payload 全量重哈希：当前 115,235 个唯一 payload 全部匹配 checksums；新结果与 Phase163 机器输出逐字节一致，许可与语义支持仍未据此证明。
- [Phase210 当前机器结果](../outputs/phase210/source_release_metadata_audit_current.json)：记录 bundle lock、索引/sidecar/payload 哈希及聚合来源元数据，不含 raw text、义项 ID 或来源路径。
- Phase211 NeurIPS 2026 FaithSieve 忠实度审计：将语义 gate 的双专家校准纳入评测边界；135 条审计中 gate 接受了 13/20 条人审不忠实语句，gate 不能替代 gloss-span gold。
- [Phase211 结构化筛读日志](../sources/literature_screening_log_2026-10-08_neurips2026_faithsieve_phase211.json)：官方标题目录、作者全文、人工审计分母及任务边界。
- Phase215 最小深度替代推导来源覆盖：枚举全部同深度 clauses 并核验来源映射；49 个 head 的全替代来源并集超过单一 witness。
- [Phase215 机器记录](../sources/minimum_depth_alternative_source_audit_2026-10-08_phase215.json)及[聚合输出](../outputs/phase215/minimum_depth_alternative_source_audit.json)：记录输入、实现、输出哈希和新增 payload 增量核验。
- Phase217 定向相关工作补充：区分 external factuality、context faithfulness、gloss-span support、形式 proof validity 与模型 plausibility 效应。
- [Phase217 结构化筛读日志](../sources/literature_screening_log_2026-10-08_faithfulness_validity_plausibility_phase217.json)。
- Phase218 标注与 Track A 启动门审计：复核 v3 输入/呈现完整性、pinned release 元数据差异及尚未满足的签署、许可和设计 gate。
- [Phase218 机器审计记录](../sources/annotation_and_track_a_launch_readiness_audit_2026-10-08_phase218.json)。
- [Phase219 Track A v1 设计草案](track_a_protocol_v1_draft.md)：主终点是 edge-level gloss-span support；分开 source gold 与 exact-condition NLI，并设计 target-sense 分层抽样和四人平衡 NLI 标注面板。仍待研究者确认。
- Phase219 深度分析与[机器设计记录](../sources/track_a_protocol_design_review_2026-10-08_phase219.json)。
- Phase228 相关工作主张边界：确认 pair/multi-component interaction、故障树 JRI/JFI 与 minimal cut-set importance 有既有先例；Phase227 的 21,878 个 pair×head 联合独有损失恰对应 head-level 二元素最小删除割集，不主张交互方法新颖或来源冗余。
- [Phase228 结构化筛读日志](../sources/literature_screening_log_2026-10-08_reliability_interactions_phase228.json)：保存出版商摘要级证据、查询词与不可外推范围。
- Phase229 basis 来源身份链审计：85 个 basis sense 的 166 个 source payload 全部通过 byte/hash/identity 检查；全图 154,206 个 clause 均有 source-index 行。结构 lineage 已核实，但 source-deletion intervention 和 gloss 语义支持仍未确立。
- [Phase229 CLI 与复算输出](../src/analysis/basis_source_lineage_audit.py)、[主结果](../outputs/phase229/basis_source_lineage_audit.json)、[独立路径复算](../outputs/phase229/basis_source_lineage_audit_replay.json)及[机器记录](../sources/basis_source_lineage_audit_2026-10-08_phase229.json)。
- Phase230 source-record bundle removal 对照：在全 sense payload bundle deletion 契约下复算 3,570 个 pair，闭包损失集与 Phase227 seed-only deletion 全部一致；这不是上游 WordNet 文档删除结论。
- [Phase230 实现](../src/analysis/basis_payload_bundle_deletion_audit.py)、[主输出](../outputs/phase230/basis_payload_bundle_deletion_audit.json)、[独立路径复算](../outputs/phase230/basis_payload_bundle_deletion_audit_replay.json)和[机器记录](../sources/basis_payload_bundle_deletion_audit_2026-10-08_phase230.json)。
- Phase231 单 payload 删除敏感性：对 166 个 source-record payload scenario 比较任一来源保留、全部来源必需及 seed-only 闭包；两种来源策略在所有 head×scenario 上均与 seed-only loss set 相同，仍不代表上游来源替代语义。
- [Phase231 实现](../src/analysis/basis_single_payload_deletion_audit.py)、[主输出](../outputs/phase231/basis_single_payload_deletion_audit.json)、[独立路径复算](../outputs/phase231/basis_single_payload_deletion_audit_replay.json)及[机器记录](../sources/basis_single_payload_deletion_audit_2026-10-08_phase231.json)。
- Phase232 NeurIPS 2026 LogicTree-RAG 相关工作审计：新增已接收论文的全文定向筛读，收窄 logic tree、来源证据 grounding 与 evidence-support 人审的宽泛新颖性主张；sense-specific gloss→typed Horn support / proof replay 仍只是未验证差异假设。
- [Phase232 结构化筛读日志](../sources/literature_screening_log_2026-10-08_logic_tree_rag_neurips2026_phase232.json)及[更新后的近邻对照](closest_work_comparison.md)。
- Phase239 ICLR 2026 分层概念与 WordNet hierarchy 筛读及[机器日志](../sources/literature_screening_log_2026-10-08_iclr2026_hierarchical_concepts_wordnet_phase239.json)：全文筛读 HiCEM，收窄 WordNet 层级概念表示/干预的新颖性表述；另一篇论文仅摘要级记录。
- Phase241 仓库基线与本地数据隔离审计及[机器记录](../sources/repository_baseline_hygiene_audit_2026-10-08_phase241.json)：确认 Git 尚无提交/已跟踪文件，`tmp/` 有约 392.8 MB 本地阶段数据；补充索引、缓存和临时目录忽略规则，未暂存、提交、删除或迁移数据。
- Phase245 锁定目标名词切片 genus baseline 资源对齐诊断及[机器记录](../sources/track_a_genus_resource_diagnostic_2026-10-08_phase245.json)：v3 锁定 frame 的 252 个 noun targets 中，启发式覆盖 247 个定义；对同版直接 hypernym 的资源 pair P/R/F1 为 10.7%/36.7%/16.5%。仅是资源边重合，不是 gloss 语义 gold、Track A 决定或模型效果结论。
- Phase246 Track A genus 资源诊断确定性重放及[机器记录](../sources/track_a_genus_resource_replay_2026-10-08_phase246.json)：Phase245 聚合 JSON 在独立输出路径上逐字节重现，SHA-256 一致。证明当前 host/input 的重复运行稳定性，不证明跨环境、语义 gold 或模型效果。首个 Git 快照仍需逐类审核；未 staging/commit。
- Phase247 首个 Git 快照逐路径盘点及[机器记录](../sources/repository_initial_snapshot_review_2026-10-08_phase247.json)：对 812 个候选文件（240.1 MB）记录路径、SHA-256 和初步处理类别；58 项需敏感复核，32 个外部 corpus 文件和 108 个派生输出暂缓决策。此账本不是已批准的发布 allowlist；未 staging/commit。
- Phase248 敏感路径内部仓库筛查及[机器记录](../sources/repository_sensitive_path_review_2026-10-08_phase248.json)：复核 58 项，未检出个人目录、邮箱或凭据模式；21 项保留为 AAAI 2027/内部边界材料，answer-key 由 Git 忽略。只支持内部快照候选筛查，不构成公开许可或完整隐私审计。
- Phase249 ACL 2026 SATQuest 全文筛读及[结构化日志](../sources/literature_screening_log_2026-10-08_satquest_acl2026_phase249.json)：收窄一般 verifier-backed 逻辑评测和多表述控制的新颖性；SATQuest 的 CNF/PySAT 评测不含 WordNet sense/gloss-span source-support gold。
- Phase253 相关工作全文筛读与矩阵 crosswalk、[结构化日志](../sources/literature_screening_log_2026-10-08_phase253_fulltext_addendum.json)及[机器 crosswalk](../outputs/phase253/closest_work_log_crosswalk.json)：全文筛读 5 篇剩余未回指学术论文，修正 Word Ladders 错引；285 个矩阵目标中 280 个回指日志，剩余 5 个均为项目/代码资源。与既有筛读合计 139 份日志、2,042 条题名记录、1,927 个保守簇。此为追溯性审计，不代表搜索覆盖或新颖性证据。
