# 五线科研执行队列

更新日期：2026-10-31（北京时间）
状态：持续维护的工程与研究工作队列。这里只记录证据、阻塞、依赖和下一验收点；不将计划写成结果，也不替用户决定科学问题。

## 总研究问题

保留定义中的联合构造（AND）、替代路径（OR）及可复用中间概念，是否比原始释义和普通成对关系，为机器语义理解及人类概念发展提供额外信息？结构事实、表示可行性、语义保真、下游效果和认知解释是不同证据层级。

## 全局执行规则

1. 冻结输入只读；每个分析记录版本、哈希、样本分母、命令、环境、失败和排除原因。
2. 保留的测试文本/标签不用于候选修补、方法选择、阈值选择或调参。任何已反复使用的开发集只可作为历史探索，不再作模型选择依据。
3. 一项 PR 只处理一个可审阅主题。优先在 `codex/<topic>` 分支提交，运行针对性验证，写清问题、改动、验证、限制和未完成 gate；只有 GitHub 工具确认创建时才标记 PR 已开。
4. 每轮有结果时，更新对应专项协议、本队列和本地 `report/project_review_2026-10-29-current.md`，然后运行根目录 `python docs/update_progress_snapshot.py`。根报告、根 docs、数据、模型和实验输出不提交。
5. 若研究决策、权限、许可、来源映射或用户审批缺失，暂停依赖该决定的步骤，同时推进不依赖它的工程核验。

## 当前执行看板

| 优先级 | 支线/工作包 | 当前证据与状态 | 下一动作 | 验收条件 / 停止门槛 | PR / 分支状态 |
|---|---|---|---|---|---|
| P0 | 总控：队列和五线依赖管理 | 路线图已有总问题、分工和阶段门槛；本文件补充逐项工作包、阻塞和 PR 状态 | 每轮先核对实际 Git 状态，再更新本表与根本地报告 | 计划和结果分开；旧日期、提交和 PR 状态以当前仓库及 GitHub 实际返回为准 | 本文件随总控或当轮主题 PR 更新；本轮新增在 T04 分支 |
| P0 | T02-1：介词关系保真与结构消融 | 全图 `prep` 删除、`prep_phrase` 敏感性、配对/分层结构对照已运行；结构变化不是语义保真。40 条只允许试标。现有源记录的上游版本指纹无法绑定到特定 payload/release，来源家族与许可 unresolved | 先做来源记录到实际上游对象的可复算 crosswalk；并准备非文本的抽样框精度/工时方案草案。不得导出正式释义审查包 | 在总体/来源家族、盲呈现、多条件重复判定、目标等权区间及精度门槛、权限都明确前，不启动正式双盲标注；任何自动关系分类无证据均为 `unresolved` | 专项实现分支包含多个已推送子主题；各 PR 是否存在需在线核实，不能因分支已推送标记为已建 PR |
| P0 | T04-2b：共同文本与真实图输入审计 | 冻结训练候选 3,404 次出现/2,051 唯一候选，结构覆盖与 B/C/D 释义 token 清单均 2,051/2,051；最长单条释义 77 WordPiece。旧序列化 A/B/C/D 已在 `emotion_xpu` 完成 3 种子训练，但 D 相对 B 没有净增益；同一 SemCor dev 已用于多轮探索 | 新共享 gloss encoder + relation pooling 的 train-only XPU 前向已重复 2 次；下一步优化 ID 顺序 batch 的 padding 与逐候选池化开销，保持输入/输出数值等价，再做不读 dev 的 train-only 单批反向/优化器 smoke | 旧 dev 仅作历史结果，不再选模型或调参。记录显示推理 padding 58.4%，前向未含 context、scorer、backprop/optimizer；任何性能比较须先补上下文/候选打分架构、共同失败分母、长度和算力对照，并冻结新来源/许可/映射/统计方案 | `codex/t04-structure-input-design` 上的当前实现已推送 `eecab14`；本轮 profile 实现待提交；GitHub PR connector 不可用，PR 未创建 |
| P0 | T04-3：WSD 映射、许可和新评估 | SemCor 内部文档隔离试点已重复使用，不能继续调参；Raganato 使用 WN3.0；FEWS 与图中 Wiktionary 来源可能重叠。完整候选和输入映射需逐目标报告 | 只处理不含测试文本/标签的来源、许可、模型暴露和 WN3.0→OEWN crosswalk 元数据；按子集列零/唯一/多映射、POS/lemma 异常和候选覆盖 | 先冻结子集、许可和映射规则；不满足授权或映射覆盖条件时不解封测试集。确认性评测只能在代码/配置/模型/分析锁定后执行一次 | 后续单独 `codex/t04-frozen-wsd-eval`；不可把旧 dev 结果移名为新评估 |
| P1 | T01：ToLogic 编译与语义审核 | 六例有限枚举和 want/without 重放/静态结构审计可复现；候选覆盖不等于公式语义正确，without 是外部接口且不在原 85 basis | 保持六例作回归；先把语义标签说明、双人独立判定、参数绑定与作用域协议准备齐；由负责人确认外部接口语义再做盲审 | 没有独立语义标签前只报告候选枚举、绑定和语法；不训练 ranker、不声称概念学习或泛化 | `codex/t01-semantic-review-protocol` 等分支已推送；逐 PR 状态需 GitHub 核查 |
| P1 | T03：知径交互原型 | 现有 `concept-dictionary/` Demo 是唯一产品基线；功能测试不代表理解或学习 | 继续在现有 Demo 做固定案例的路径正确性/解释完整性核对，聚焦介词方向、否定、OR 备选、循环和无路径；先用程序断言和无参与者模拟 | 不重建替代系统；真实用户理解/学习实验须由用户决定并完成伦理、招募、同意和数据处理审批 | 小型功能修复单独 PR；不以模拟用户作学习证据 |
| P1 | T05：义项级发展数据可行性 | Wordbank 是多种粒度的问卷数据，CHILDES 首现不等于理解，sense-level AoA 权利/映射未解决；既有图缓存结果仅是算法模拟 | 只核可合法访问的数据集级 schema、许可和词形—义项映射字段；先列许可、语言、年龄、单位、sense ID 和覆盖元数据清单 | 未获得儿童级数据授权或可审计的义项映射时不下载响应、不做预测；不得将模拟写成认知发展验证 | 继续在 `codex/t05-data-feasibility` 上单主题 PR；核查当前远端与 PR 状态 |
| P2 | 跨线整合/外部应用 | NLP/WSD 优先；反向词典、词替换、翻译与人类研究均在下游 gate 之后 | 仅在 T04 有可复验结构增益、跨资源覆盖和许可过关后，启动一项下游复核 | 不用反向词典开发分数取代 WSD 验证；不把图可达性解释成逻辑蕴涵/认知发展 | 尚未启动 |

## 里程碑定义

| ID | 里程碑 | 交付物 | 通过证据 |
|---|---|---|---|
| M0 | 环境/数据/分支盘点 | 输入摘要、分支与 PR 状态、限制清单 | 当前状态由文件、命令输出或 GitHub 实际响应证明 |
| M1 | 协议与测量单位冻结 | 研究假设、对照、标签/估计量、预算、切分、停止规则 | 所有选择先于结果；用户保留的决策有明确记录 |
| M2 | 结构/数据工程核验 | 纯合成测试、只读输入审计、共同失败分母 | 目标范围内覆盖完整，失败原因可追溯，隐私数据不出本地 |
| M3 | 开发/试标执行 | 固定命令、输入哈希、环境、日志和负结果 | 不使用保留测试；试点不冒充确认性结果 |
| M4 | 独立验证 | 一次性冻结评估/独立人工标注/外部数据 | 许可、来源隔离、映射、统计方案和报告都通过门槛 |
| M5 | PR 审阅及总报告 | 一个主题的 PR、可复现报告、错误分析、下一任务 | PR 与 CI 状态经 GitHub 证据核实；根本地进度材料同步 |

## 最近完成的可验证增量

### T04：训练分区共同 token 审计（2026-10-31）

- 训练环境是 Conda `emotion_xpu`，现有 PyTorch `2.12.0+xpu` 可用；纯 tokenizer 审计在 `base` 使用 `tokenizers==0.23.1`，未修改 Conda 环境。
- 由 pinned BERT-tiny revision 恢复的 `vocab.txt` 哈希与冻结 metadata 一致；图文件哈希也经运行前检查。
- train-only 2,051 个唯一候选的 B/C/D 有序目标及依赖释义 token IDs 全部一致；没有读取 labels/context/dev/test。
- 每候选最长单条释义 WordPiece max=77；总节点 gloss tokens max=380 是多条独立输入的总工作量，不是单个 512-token 序列。故不按该总和裁剪节点/分支。
- 17 项专项测试通过。提交 `ee43ce2` 添加审计器，`8c63298` 添加最长单条 gloss 指标并推送。聚合输出与词表保存在本机 ignored outputs。
- 边界：尚未实现新的 B/C/D 图聚合器，未测 XPU 训练峰值、时长、吞吐或结构性能；无语义/效果主张。

## 本轮 PR 工作单

| 分支 | 主题 | 检查 | PR 状态 |
|---|---|---|---|
| `codex/t04-structure-input-design` | train-only B/C/D 共享释义 token、关系池化实现与两类 XPU profile | 28 项专项/合成测试在 `emotion_xpu` 通过；随机结构 profile 与真实 gloss text+structure profile 均只用 train candidate IDs/图定义；模型和结果留在 ignored outputs | 全部代码与协议已推送至 `e1b8ed2`；GitHub connector search/create 返回 `Unknown tool`，PR 未创建。当前分支比较：[main...codex/t04-structure-input-design](https://github.com/yizhibanmashou/concept-graph-research/compare/main...codex/t04-structure-input-design?expand=1) |

## 状态覆盖（2026-10-31，优先于上方 T04-2b 表格中的“下一动作”）

T04 已完成的工程门槛：训练候选图结构覆盖 2,051/2,051；共同目标/依赖 gloss WordPiece 清单对齐 2,051/2,051；最长单条 gloss 77 token；无参数 A/B/C/D 聚合器和 train-only XPU 关系算子 profile 已完成。对 2,051 候选的随机向量 profile 有 13,526 relation-node、3,560 branches、41,316 edges；重复 3.7316/3.8978 秒。固定 BERT-tiny revision 的 config/weight/vocab 哈希已逐项匹配既有训练日志；真实 train-only gloss encoder + A/B/C/D pooling profile 覆盖 5,592 个唯一节点释义与 2,051 候选，重复两次：编码 4.883/4.920 秒，池化 7.206/7.958 秒，ID 顺序动态 batching padding 58.4%，编码/池化峰值增量分别 90,208,768/339,456 bytes。该前向未含上下文、候选打分、反向传播或优化器，不能称新模型训练已完成。28 项专项/合成测试已在 `emotion_xpu` 通过。旧序列化 A/B/C/D 已在 `emotion_xpu` 完成 seed 17/23/31：每条件 379 train，dev 111/120 可评分；各 seed 正确数 `32/33/31/28`、`23/23/31/28`、`25/26/28/26`，汇总 `80/82/90/82`（同一批目标重复三次），D−B 净差 0。旧 dev 已被探索，不再用于调参，旧 C/D 也不等于新关系池化。下一步：先等价优化 padding 和逐候选小算子开销，重跑 train-only profile，再做不读 dev 的单批反向/优化器 smoke；效果评估需另行冻结未复用 dev、来源/许可和 sense-key 映射。

本轮 T04 聚合器、两种 XPU profile、协议和队列更新都在 `codex/t04-structure-input-design` 专题分支；代码与协议提交 `eecab14`、`e1b8ed2` 均已推送，既有 token audit commits 为 `ee43ce2`、`8c63298`。GitHub PR connector 仍返回 `Unknown tool`，且本机未安装 GitHub CLI，因此尚无 PR；可从 [分支比较页](https://github.com/yizhibanmashou/concept-graph-research/compare/main...codex/t04-structure-input-design?expand=1)创建。CI 未核实。

## 下一轮建议执行顺序

1. **T04 profile 效率与训练 smoke**：对 train-only encoder + relation pooling 加入按长度组织 batch 或其他不改变样本/表示的 padding 优化，向量化逐候选池化；先用数值等价和定长输入检查，再重复量化吞吐/内存。随后仅用 train gold 做单批反向/optimizer 工程 smoke，不读 dev/test、不报告 WSD 指标。
2. **T02 provenance crosswalk**：只用本地 source metadata 与公开目录标识调查能否把 raw-sha256 指纹映射至准确上游对象；无法绑定即正式登记为 unresolved，不生成语义标注样本。
3. **总控和其他三线的就绪工作**：更新 PR 状态；T01 审阅流程、T03 固定任务断言、T05 license/schema 清单仅推进不需数据访问或用户科学决策的部分。
