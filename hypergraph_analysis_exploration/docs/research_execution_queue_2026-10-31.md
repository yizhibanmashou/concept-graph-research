# 五条研究线执行队列与交接

更新日期：2026-10-31
状态：持续执行队列；不是预注册，也不把未完成的 PR、独立验证或用户决策记作已完成。
总问题：**保留定义中的 AND 联合构造、OR 替代路径及可复用中间概念，是否比普通释义和成对关系为机器理解与人类概念发展带来额外有效信息？**

## 0. 执行规则

1. 先记录当前 main、专题分支、PR/CI 与工作区状态。分支已推送不代表 PR 已创建；PR 未核实前明确写“未创建/状态未知”。
2. 每个任务对应单一问题和单一 PR。代码、协议、运行配置、输入摘要、环境、种子、命令、结果分母、错误案例和失败状态均要可复核。原始冻结数据、语料、标注、模型权重与大体积缓存留在本机。
3. `OEWN/` 永远只读。探索性开发集已反复使用时，不继续靠改预算/种子追分；独立确认集只能在协议、映射、候选与预算锁定后解封一次。
4. 结构事实、表示工程、语义判断、人类认知证据分开报告。结构简化、模型可运行、模拟缓存收益都不能代替定义保真或人类学习证据。
5. 不等待一个研究门槛时，继续其他不依赖该门槛的合成验证、映射审计、数据可行性和维护工作。遇到来源许可、隐私、测试标签或科学主张边界风险时暂停相关操作，保留问题记录。

## 1. 当前检查点

### 可复核的项目状态

- 队列分支本轮起始 HEAD 为 `aa60876`；T02 专项分支 `codex/t02-source-evidence-audit` 已推进至 `d1ec438`，T04 设计分支 `codex/t04-structure-input-design` 已推进至 `d68e9c2`，均已推送。GitHub PR 查询/创建工具与本机 gh CLI 均不可用，分支推送不等于 PR 或 CI 完成。
- 本队列分支 `codex/research-execution-queue-20261031` 当前 HEAD 为 `7cd001d`，本轮新增队列记录后继续推送。此前 PR 搜索/创建调用返回 `Unknown tool`；PR 尚未创建，不把比较页称作 PR。
- T04 `codex/t04-full-candidate-packing` 远端 HEAD 为 `0c9e232401421c5f1cf80a637759dddec3b593c5`，包括完整候选评分、旧行兼容与已核实的 fresh-document XPU 试点记录。`codex/t04-structure-input-design` 的远端 HEAD 为 `d68e9c2`，新增共享节点索引上的 B/C/D ID-only 结构掩码；这两个专题工作目前不在本队列分支中。
- T04 最近几条候选打包/文档簇/结构输入分支的 PR 状态未能通过当前 GitHub MCP 连接核实；旧线程也记有 `Unknown tool`。在 PR 面板或有效 API 可用前，队列只记远端分支和 commit，不声称 PR 已创建或 CI 已通过。
- 本机 Conda 环境 `emotion_xpu`：Python 3.11.15、PyTorch `2.12.0+xpu`、Transformers `5.9.0`、Accelerate `1.13.0`、Intel Arc XPU。`conda run -n emotion_xpu` 下 `torch.xpu.is_available()` 为 `True`、设备数 1，64×64 运算成功；设备属性报告约 16.45 GB。新建 ignored 输出 `outputs/tiny_bert_wsd_smoke_conda_20261031` 做了 4 个 train 记录、仅 A 条件的一批 smoke（seed 17）：checkpoint 保存成功，loss 1.5541；脚本 `--smoke` 路径不读取 dev，也不产生 WSD 准确率。该烟测证明当前 Conda/XPU/权重/训练入口连通，不证明研究效果或更大模型的预算。此前 base 环境缺少 PyTorch 与 `emotion_xpu` 已有 PyTorch 并不矛盾；运行应使用 `conda activate emotion_xpu` 或 `conda run -n emotion_xpu ...`。
- 最新五个相关 Codex 专项线程已查看：T04 数据兼容、候选分块、错误分析与 XPU 记录；T02 用户已决口径和未决来源/抽样 gate；T03 现有 Demo 的功能可靠性和许可/用户研究边界；T05 HTE 词形歧义与许可限制；结构探索的汇报数字边界。线程内容已与当前仓库状态交叉核对，旧线程报告不能覆盖当前 Git 状态。

### 全项目既有结果摘要

| 线 | 可用的既有证据 | 当前不得声称 |
|---|---|---|
| T01 ToLogic | 六例有限枚举 455 候选；`want` 单一 `be without` 输入 130 候选。回放一致，属候选生成/接口工程。 | 未有经独立审定的语义 gold、公式正确率或泛化结果。外部 `without` 接口不是 85 个 basis 之一。 |
| T02 介词结构 | 冻结图 `prep` 删除时 505 个目标出现非空分支碰撞、少 633 条不同分支，另有 623 条新空分支；`prep_phrase` 单独敏感性变化较小但非零。5,625 条 alternative/definition-WSD source record 中，3,444 条有 evidence、共 3,645 项和 82 个原始标签。针对 Kaikki 两标签的 1,082 项复核发现所有 `source_version` 共用一个 `raw-sha256` 指纹，但与定义文本哈希 0/1,082 相等。 | 删除后的结构变化不是语义改善；标签不是已确认独立来源 family。哈希对象和生成器未绑定，不能证明数据版本。license 字段缺失不等于无许可，已有来源网页也不等于冻结条目已清权。 |
| T03 知径 | 现有 Demo 有搜索、义项选择、AND/OR 分支解释、循环提示、设置和历史恢复；已有自动测试与构建记录。 | 模拟/功能通过不证明真实用户理解或学习收益。未经批准不启动参与者研究或另建替代产品。 |
| T04 NLP/WSD | 全候选生成和评分接口、XML occurrence 目标定位、文档隔离 dev 及 tiny-BERT A–D XPU 试点已有实现/记录。最近三种子正确数 A/B/C/D 为 80/82/90/82（分母 333 个目标×种子），配对 D−B=0；B/C/D 输入长度并不相等。 | 不是独立来源验证；旧 dev 已用于方案修订。结果不支持当前序列化配置下完整结构优于 B；也不能证伪结构的一般价值。不能继续在旧 dev 调参。 |
| T05 认知发展 | 有概念缓存/复用模拟和 HTE 少量对齐先导；全图词形存在显著义项歧义。 | 计算复用不等于儿童学习；词形首见年代不等于概念诞生或个体首次理解。HTE 不可系统批量抓取，未经授权不扩展。 |

## 2. 任务队列（按依赖排序，不设虚假完成日期）

状态标签：`READY` 可直接执行；`IN PROGRESS` 已有专题分支；`WAITING FOR DECISION` 需要研究负责人确定口径；`GATED` 需先通过数据/许可/独立评估门槛；`DONE` 仅用于有产物和验证证据的项目。

### G00 · 总控状态与 PR 队列（READY）

**问题：** 每个专题当前的 Git、证据等级和下一依赖是否清楚，避免旧聊天、分支与报告相互冲突？

- 维护本文件的分支 HEAD、PR 状态、前置 gate、任务 owner、验收证据和阻塞原因；每次有状态变化更新日期与本地总报告/快照。
- 为每个提交检查 `git diff --check`、测试输出和 staged 文件；确认无冻结数据、私人材料、原始语料、模型权重或测试标签。
- 当前 T02 PR 创建工具调用 `Unknown tool`。下一次在可用 GitHub 接口恢复时，先检查 PR 列表避免重复，再创建 T02 PR；创建后核对 base/head、diff、CI 与保护规则。
- 验收：报告中每条“已完成”都有当前文件、命令、commit 或 PR 证据；没有把本地计划计为实验成果。

### T02 · 介词与概念组合

#### T02-A · 来源证据覆盖审计（IN PROGRESS）

**可检验问题：** 冻结的 alternative/definition-WSD 子集中，来源 evidence 覆盖到什么程度，哪些原始标签可继续做上游 release/family 对齐？

- 输入范围固定为索引中的 5,625 条记录；只做来源元数据聚合，不导出 gloss、释义、sense ID、路径、locator、URL 或人工标签。
- 既有审计：3,444 条记录带 evidence，3,645 evidence item，82 个精确自报标签；1,512 条无 provenance object，669 条无 evidence list；evidence item 无显式 license 字段。新建保守标签 join 后，原样匹配 6/82 标签、143/3,645 项；仅规范大小写、下划线和空格后唯一匹配 17/82 标签、2,395/3,645 项，无歧义；4 个匹配标签的日志有状态字段（2,270 项），另 13 个没有状态；65 个标签/1,250 项未匹配，主要剩余缺口是 Kaikki/Wiktextract 的 1,082 项。该工作是日志可定位性，不是清权。复算脚本、2 项合成测试和协议已提交 `9220354` 并推送；T02 目标测试共 10 项通过。
- Kaikki/Wiktextract 标签定向审计已更新：5,625/5,625 个 payload 可解析；两类标签共 1,082 evidence items。所有 `source_version` 均呈 `raw-sha256:<64 hex>` 格式，两个标签各只有一个且彼此相同的指纹；与 1,082 条合法 `definition_text_sha256` 均不相同。故可确认字段是摘要形态，不能确认其哈希对象或上游版本绑定。随后核对 Kaikki 官方 raw-data 页和主索引：可见 Wiktionary dump 日期 2026-10-01、处理抽取日期 2026-10-25 及 extractor commit 标识，但 raw-data 页未列出可将本地 `raw-sha256` 绑定至具体对象的 checksum。日期/处理器版本不是本地摘要的来源证明。locator 不是 URL，ontology 字段缺失；`evidence_type` 为 `definition` 881 项、`related_definition` 201 项。目标测试 13 项通过；T02 分支 commit `d1ec438` 已推送。来源版本和许可仍 unresolved；这不是清权结论。
- 继续工作：将已有 Phase 24/25/50–52/124–127 的 source-rights 日志与原始 exact label 对齐；明确这是标签交叉表而非清权。对 OLS provider 标签按 ontology ID 区分，保留 `unresolved` 和上游 payload 未绑定状态；优先核对 GCIDE、MeSH 与 OLS 记录，并为 Kaikki/Wiktextract 查找可验证的本地生成流水线或 snapshot checksum。若绑定证据不存在，明确记为无法消解，不强行赋 family 或许可状态。
- PR 验收：输入 index/payload 摘要、聚合计数、精确标签 join/miss 分母、官方证据链接、版本绑定状态与失败案例；不提交源文本/许可受限数据。必须跑合成测试和 scoped audit，验证输出不含 forbidden fields。

#### T02-B · 四条件结构转换与合成审查（READY）

**用户已决定：** `prep` 是主删除口径，`prep_phrase` 单独做敏感性；类别仅限来源支持的空间/位置、方向/路径、参与者角色、否定/缺失；论元有序，证据不足标 `unresolved`；方向/论元、否定范围、遗漏/添加三轴加总体判断；结构变化和定义保真并列；40 条只作试标；目标等权、分支比例在目标内汇总。

- 现行协议和合成 validator 已定义源 OR 分支非空、变换后空分支显式保留。下一步只在纯合成 fixtures 上扩展边界、重复 occurrence、论元有序、否定 scope 和四条件不覆盖输入等测试；不从介词词形自动补语义关系。
- 验收：原图与所有派生条件均 immutable；条件共享 target/branch/occurrence 身份；每次删除有被删 IDs；类型化关系有证据引用与有序参数；无法判断为 unresolved；空结果不被解释为真命题。

#### T02-C · 结构统计复算（GATED BY INPUT/PR REVIEW）

- 从同一冻结版本复算 `prep` 主分析与 `prep_phrase` 单独敏感性，逐项核对目标、分支和 occurrence 分母；对照组预先固定频率匹配范围与可匹配/不可匹配介词覆盖率。
- 结构侧报告新增空分支、非空碰撞、合并 excess、目标受影响数、依赖闭包/可达变化和共同可比子集；空分支删除与保留两种处理不得混作一项结果。
- 验收：冻结包摘要匹配、输出独立于原图、脚本可重复、各指标有分母、随机或人工挑选样本明确标探索性；结构输出不冒充保真结论。

#### T02-D · 正式保真盲审（WAITING FOR DECISION / GATED）

- 尚需研究负责人确定：可覆盖总体与纳入来源家族；同一单元四条件的呈现与防记忆方法；主要精度目标/置信水平/资源上限。样本量计算必须在标签揭盲前完成。
- 先独立抽样，不复用 40 条 pilot；按目标等权估计，目标内汇总所有可审查 OR 分支比例；对稀有层过采样时保存纳入概率并作设计权重估计。
- 正式运行条件：来源与许可链可复核、审阅者盲化、双标与仲裁流程冻结、目标和分支映射稳定、独立样本框完整。任一条件不满足则只报告描述性结构结果。

### T04 · NLP 应用与 WSD

#### T04-A · 旧接口完整性与候选失败账本（IN PROGRESS）

**可检验问题：** 同一 gold-free 候选生成下，完整候选能否稳定编码/分块评分，训练和推理的候选归一化是否一致？

- 最新已见远端分支包括 `codex/t04-full-candidate-packing` (`0c9e232`)；历史兼容修复 `8e7fe81` 已在其祖先中。需要在可创建 PR 时检查工作分支变更和 CI，不要因线程摘要把兼容修复误当未推送或重做。
- 仅用构造记录验证 legacy/new schema、不可评分目标、候选数不匹配、候选编码失败、microbatch 拼回单目标排序分数、失败不改变剩余候选归一化语义。
- 验收：训练与推理共享同一打包/评分 helper；候选全集先由词形/POS/固定形态生成，不参考 gold；所有失败按原因单列且保留原始目标分母。

#### T04-B · 结构输入等量对照（合成结构视图已验证；真实输入审计待做，训练仍 gated）

- 当前旧 C 的 `edges` 只是重复 B 的依赖别名表；旧 D 与 B 的文本长度不同，不能隔离 pairwise topology 或完整分支结构效应。不得沿用它们作结构增益证据。
- 先制定新序列化：B/C/D 对每个目标和候选共享完全相同的依赖概念与释义 token IDs；C 只改变成对投影信息，D 只改变 AND/OR 分区与论元角色；计量实际/截断 token，并让模型看到的词元预算对齐。用合成图展示 pairwise projection 丢失高阶分支分区。
- 已有 `t04_structure_views.py` 纯合成关系视图；进一步实现 `build_aligned_relation_tensors()`，返回同一 canonical node inventory 上的 B dependency mask、C pairwise adjacency matrix 和 D branch-node incidence matrix。合成比较确认节点/分支顺序不影响张量，且可构造 B/C 完全相同而 D 不同的高阶分区例子。专题测试 8 项通过，`py_compile` 与 `git diff --check` 通过；commit `d68e9c2` 已推送至 `codex/t04-structure-input-design`。这仍不验证 tokenizer token IDs、真实图输入、编码器公平或模型效果。
- 不用旧 SemCor dev 选 checkpoint、预算、字段标记或阈值；先做 code-only/synthetic verification 与新增、独立来源 dev 的合法性和映射审计。无合适新评估来源时停止训练，报告可行性而非继续用旧 dev 搜索。
- 评测来源筛查已写入 `t04_structure_isolation_design.md`：Raganato 五套标准子集列为主评测候选但各自许可、模型暴露及 sense-key 映射覆盖仍待审；FEWS 列为长尾次要候选，并有 Wiktionary 来源重叠风险。新增映射方案：使用冻结 OEWN entry archive crosswalk 审核 WN3.0 keys 的零/唯一/多映射和 POS/lemma 等失败分母；Global WordNet SemCor reannotation 可交叉核对 wn30/oewn keys，但同源于 SemCor/Brown，不能算独立来源确认。其许可证包括 Princeton WordNet 条款与 CC BY 4.0 署名。设计更新 commit `4ec5092` 已推送；未下载 benchmark、未读取测试句/标签。
- 设备：`emotion_xpu` Conda 已验证 torch 2.12.0+xpu / Transformers 5.9.0 / Intel Arc XPU；无需在 base Python 安装 PyTorch。每次训练记录精确环境 lock、驱动、设备、seed、token/padding、步数、运行时和峰值显存。

#### T04-C · 独立评估协议（GATED）

- WN3.0↔OEWN 2025 映射、候选覆盖、重复义项、训练/文档/来源 family 边界、license 和开发集独立性通过前，不解封测试集、不跑确认性分数。
- 主比较预指定为 D−B；其余对照和长尾/结构相近/短上下文切片为次要或探索性。按目标配对，按来源文档或 family 聚类计算不确定性；种子不是独立样本。
- 报告 all-selected denominator、scorable subset、映射失败、上下文无法定位、候选编码失败、每条件实际 token 和失败案例。CI 通过只证明软件行为，不证明结构增益。

### T01 · ToLogic

**已知基线：** 六例 455 候选；want 130 候选，输入含外部 `without`。
**下一项 READY：** 将六例与 want 重放命令、输入摘要、输出计数和类型/角色绑定检查写成可从空环境复现的 recipe；只用既有独立审阅记录，若没有则不创造 gold。
**后续 GATED：** 先冻结人工公式语义标签手册与盲审样本，再比较规则排序器/轻量模型；按构式或义项 family 留出。
**验收边界：** parser、类型、绑定、候选召回、语义可接受度分轴报告；无金标准时只报工程和有限候选覆盖。

### T03 · 知径

**下一项 READY：** 在既有 `concept-dictionary/` Demo 固定 5–8 个行为任务，覆盖多义词选择、AND 前提、OR 替代、循环/不可达、方向/否定与来源展开；用本机合成夹具做状态机/键盘/窄屏/错误数据回归，并核对解释路径是否与真实规则一致。
**验收边界：** 功能 bug 和界面行为可由测试/手工走查报告；模拟交互不能代表真人理解。真实用户任务需要研究负责人批准招募、同意、保存及分析方案。数据授权和来源说明在公开化之前单列处理。

### T05 · 认知发展

**下一项 READY：** 只读盘点 Wordbank、CHILDES、义项级 AoA/词汇知识公开页面的访问条件、版本、年龄/测量定义、数据粒度、词形/词义标识和重用限制，形成公开来源矩阵；不下载受限语料、不批量抓取 HTE。
**随后 GATED：** 先做合法小样本词形–POS–sense 对齐的人工质量审查；对齐质量不足即停，不开展预测。
**模型阶段：** 外部基线先含频率、具体性、POS、普通语义网络；超图增量特征只作预测关联，不作因果解释。
**验收边界：** 报告时间字段真实含义、对齐覆盖/不确定性、外部交叉验证和增量效应；没有儿童或独立行为证据时不声称习得规律。

## 3. 本轮更新记录

- 确认训练依赖位于 Conda 环境 `emotion_xpu` 而非默认 `base`；复核 Python/PyTorch/Transformers/Accelerate 版本、XPU 可用性和设备内存字段。另做 4 条 train 记录的 A-only smoke，checkpoint 成功保存；不读 dev、不报性能分数。新输出留在 ignored `outputs/tiny_bert_wsd_smoke_conda_20261031`。这不是重新训练 A–D，也不改变旧开发集已被重复使用、不可继续调参的研究 gate。
- 将近期 T02、T04、T03、T05 和结构探索线程的结论压缩为当前队列，并同远端分支 HEAD 对照；单个线程中的计划和结果仅作线索，已存在的提交/文件为准。
- 尝试创建 T02 PR；GitHub MCP 返回 `Unknown tool`，因此没有创建 PR，也没有声称 CI 运行。
- T02 审计再扫 5,625/5,625 个 payload，并修正版本形态分类，核验共享摘要与定义文本哈希关系；限定输出只记录计数、不泄漏摘要。进一步核对 Kaikki 官方下载/索引页面，发现页面列出上游日期和 extractor commit，但没有本地摘要的对象绑定 checksum；因此仍无法确定冻结 payload 的 release。目标 T02 合成测试 13 项通过，`git diff --check` 通过；commit `d1ec438` 已推送到 `codex/t02-source-evidence-audit`。PR 状态仍未创建/未核实。
- T04 来源与映射设计补充：核对 Raganato 官方 WN3.0 评测口径和 Global WordNet SemCor reannotation 的双 key 格式/许可；明确其可交叉核验映射但不构成独立来源，并把逐资源映射分母、许可与测试隔离加入 gate。设计 commit `4ec5092` 已推送至 `codex/t04-structure-input-design`；未下载 benchmark 或读取测试标签。
- T04 结构实现进展：为 B/C/D 增加共享节点清单上的 ID-only masks，8 项结构视图测试通过并推送 commit `d68e9c2`。该层没有任何 gloss/tokenizer/corpus/gold 输入；下一步需在不读测试标签前完成真实候选的共同节点清单、token-ID 完全一致审计及共同裁切失败分母，之后再评估结构编码器的参数和算力公平性。

## 4. 当晚退出交接标准

本队列可在晚间连续推进，但“今晚完成”不等于五条科学线完成。一次交接至少列出：完成的代码/协议/复算；失败命令与原因；仍在运行的进程（需实查句柄）；PR/CI 精确状态；未通过的伦理、许可、独立来源与用户决策 gate；下一项独立可做任务。没有足够数据或权限时，用“证据不足/暂停该任务”收尾，不填造结论。
