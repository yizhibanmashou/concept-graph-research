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
| P0 | T02-1：介词关系保真与结构消融 2026-10-31 全图 Horn 反事实复算：prep 删除207,753个字面量、106,538头不可达；prep+prep_phrase 删除208,100个、106,487头不可达；phrase 增量只使51头恢复可达。 | 全图 `prep` 删除、`prep_phrase` 敏感性、配对/分层结构对照已运行；结构变化不是语义保真。40 条只允许试标。现有源记录的上游版本指纹无法绑定到特定 payload/release，来源家族与许可 unresolved | 先做来源记录到实际上游对象的可复算 crosswalk；并准备非文本的抽样框精度/工时方案草案。不得导出正式释义审查包 | 在总体/来源家族、盲呈现、多条件重复判定、目标等权区间及精度门槛、权限都明确前，不启动正式双盲标注；任何自动关系分类无证据均为 `unresolved` | 专项实现分支包含多个已推送子主题；各 PR 是否存在需在线核实，不能因分支已推送标记为已建 PR |
| P0 | T04-2b：共同文本与真实图输入审计 | 400 个固定 train 目标；WordNet 全形态候选恢复 3,404 个候选出现/2,051 唯一候选，379/400 可评分；21 条 gold 映射/元数据缺陷固定不补；A/B/C/D 共用候选池、共同目标上下文及 352 token 张量宽度 | `emotion_xpu` 为 Python 3.11 / PyTorch 2.12.0+xpu / Intel Arc；已确认 `torch.xpu.is_available()`；128-token 上下文的 A/B/C/D 共同审计通过，最大实际序列 351/512、标记 400/400、窗口截断 3/400；四条件 train-only 完整训练完成并以相同 seed 重放，A/B/C/D 权重 SHA 完全一致 | 当前一轮是工程重放，不是 WSD 效果估计；不读取 dev/test、不在旧 dev 调参。训练日志已保存且四条件各 379 条、loss 有限，重放 checkpoint SHA 一致；这只核验可复现性，不是效果估计。再准备新来源隔离评测。许可和 WordNet/OEWN 跨资源覆盖仍未解决 | `codex/t04-structure-input-design`；本轮代码/文档待提交推送；PR 创建工具曾返回 `Unknown tool`，尚无 PR/CI 状态 |
| P0 | T04-3：WSD 映射、许可和新评估 | 词典库存级 WN3.0→OEWN exact sense-key 覆盖 205,989/206,941（99.54%），POS 细分已复算；241 个 WN3 synset 成员 key 分裂到多个 OEWN synset。逐查 Raganato 五个英语子集：未确认缓存/再分发权；2013/2015 BabelNet 更新仓库不含英语。固定 BERT-tiny 模型卡未公开完整 corpus/version/去重链；预训练重叠与 MNLI/NLI 下游暴露均未核实。未开 benchmark XML/gold | 向原任务发布方核对条款；对拟用模型登记 revision、预训练/监督来源和历史暴露；若权利与隔离 gate 通过，冻结协议后才做一次 benchmark-level coverage audit | 旧 dev 不再调参；FEWS 不能标作独立来源验证；未过许可与 lineage gate 不打开 FEWS/Raganato train/dev/test/raw；“模型卡未提及”不等于无测试暴露；库存覆盖不能替代 benchmark 覆盖 | 本轮逐任务审计已提交并推送到 `codex/t04-independent-eval-source-audit`；PR 搜索 connector 返回 `Unknown tool`，尚无 PR/CI 证据。创建页：https://github.com/yizhibanmashou/concept-graph-research/pull/new/codex/t04-independent-eval-source-audit |
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
| `codex/t04-structure-input-design` | train-only B/C/D 输入、2×2 batching、向量化池化、XPU 反传、监督微批与映射覆盖审计 | 23 项 T04 专项测试通过；train-only 复跑一致；映射问题分解为 18 个无 exact key、2 个 invalid gold、1 个图中缺失；代码/协议已有推送，本轮审计待提交；模型、数据和输出保持本地 ignored | GitHub PR 工具返回 `Unknown tool`，尚无 PR；比较页：[main...codex/t04-structure-input-design](https://github.com/yizhibanmashou/concept-graph-research/compare/main...codex/t04-structure-input-design?expand=1) |

## 状态覆盖（2026-10-31，优先于上方 T04-2b 表格中的“下一动作”）

T04 工程状态：训练候选图覆盖 2,051/2,051；冻结模型/训练数据摘要核验通过。长度排序/pad-1 的真实 gloss 前向相比 ID/pad-1 降低 padding、时延和内存；B/C/D 权重矩阵池化合成均值等价，XPU profile 仍属本机工程线索。在相同固定 train-only 的 400 目标与 A/B/C/D 四表示上，新增全词形候选生成恢复 4 个因首形态漏召回的 gold，候选回到 3,404 次出现/2,051 唯一候选，379 条可评分、21 条来源映射问题不可评分且不补标。128-token 目标上下文 cap 下 3/400 截断、marker error=0，A/B/C/D 13,616 个候选—条件对最大实际序列 351/512；统一宽度 352。`emotion_xpu` 完成 1 epoch、seed17、batch4 四条件训练，每条件均训练 379 条。mean loss A/B/C/D=1.85950/1.85312/1.85398/1.86255；完整重放的四个 checkpoint SHA 完全一致。loss 不可用于条件优劣或 WSD 性能判断；本轮严格 train-only，没有打开 dev/test。此前旧序列化三种子 dev 结果仍只作历史探索，严禁再调参。下一步是独立来源许可、WordNet/OEWN crosswalk 与全候选评测协议；否则不解封测试集。

T04 代码、协议与队列此前已推送至 `codex/t04-structure-input-design`；本轮审计代码与文档已推送；commit/head 以 Git 实际状态为准。GitHub PR 工具返回 `Unknown tool`，本机 `gh` 不可用，因此未创建 PR，也未核实 CI；[分支比较页](https://github.com/yizhibanmashou/concept-graph-research/compare/main...codex/t04-structure-input-design?expand=1)可手动打开。

### 2026-10-31 XPU profile batching 复测（覆盖此前不完整预热测量）

修正 profile 预热方式：编码器先按完整 batch 计划跑完一整遍，再计时第二遍；关系池化也先预热 32 个候选。对比均在 `emotion_xpu`、同一 Intel Arc XPU、固定 BERT-tiny 权重、5,592 个唯一 gloss、2,051 个训练候选、batch size 32 下进行，未读取标签、上下文、dev/test。

| 编码 batch 设置 | padding 比例 | 编码时间 | 编码峰值额外分配 |
|---|---:|---:|---:|
| ID 顺序，pad-to-1 | 58.4% | 1.252 秒（1 次） | 90,208,768 bytes |
| 按长度排序，pad-to-8 | 23.2% | 0.858 / 0.885 秒（2 次） | 53,596,160 bytes |

length-sort + pad-to-8 相较 ID-sort + pad-to-1，本次观测编码时间约低 29%，padding 下降 35.2 个百分点，峰值增量内存约低 41%。这只是单设备 train-only 资源工程 profile，计时次数有限，batch 顺序、shape 与 pad multiple 一起变化，不能归因为单一因素，也不是模型训练或 WSD 质量结果。关系池化约 6.94–7.08 秒，峰值额外分配 339,456 bytes，仍是下一步工程优化点。此前仅预热两个短 batch 的 profile 数字应视为预热不足，不用于稳定吞吐判断。更新后的专项测试 21 项通过；下一步向量化池化并对照数值，再做 train-only 单批反向/优化器 smoke。

## 下一轮建议执行顺序

### T04-3 词典库存级 crosswalk（2026-10-31）

仅读取 WordNet 3.0 `index.sense` 与 OEWN 2025+ entry `sense.id/synset`，按大小写折叠的 exact sense-key 匹配；没有打开 benchmark 句子或标签。总计 206,941 个 WN3 keys 中 205,989 个 exact 匹配（99.5400%），未匹配 952；POS 覆盖：形容词 99.3467%（29,806/30,002）、名词 99.6200%（145,756/146,312）、副词 98.9247%（5,520/5,580）、动词 99.4411%（24,907/25,047）。Synset 层面 116,714 全成员映射到同一 OEWN synset、378 部分映射到单一目标、241 多目标、326 无目标；无单一 sense key 多目标冲突。此为 inventory identifier coverage，不能推出义项同义或 FEWS 映射覆盖。WN30-LFS 同次复算 104,357 项中 103,829 精确连接，174 项缺 WN3 key、354 项 key 不在 OEWN、格式错 0，与旧机器输出计数和 archive hashes 一致。输入 hash、POS 与 failure 类别已写入专项协议；机器 JSON 留在 ignored outputs。4 项 crosswalk 单测通过。

**研究决策影响：**对于基于 WN3 labels 的数据，可以继续评估 exact-key 层级的覆盖，而不必因“整个库存完全不可映射”而放弃；但必须按目标报告多目标/无映射失败，并保留共同可评分分母。FEWS 的 Wiktionary sense ID、同源风险、数据包许可及 test 保护仍各自独立 unresolved，不能解封数据。下一动作是只读盘点其他公开基准的数据/标签许可、原模型训练暴露和现有 splits；若没有一个满足 gate 的未用开发集，本支线暂时维持 train-only 工程阶段。

官方 Raganato evaluation-data 页面列出五个 WN3 统一数据集及评测包下载，但没有提供覆盖全部源任务的统一许可条款；SemEval FAQ 指出历史任务数据由任务组织方分发。评测包含 gold，故本轮未下载。检索到的 SemEval-2007 “须签许可”页属于 Task 9，不是 WSD Task 17，已明确排除。引用和逐任务权利核查门槛见 `t04_structure_isolation_design.md`。

1. **T04 profile 效率与训练 smoke**：对 train-only encoder + relation pooling 加入按长度组织 batch 或其他不改变样本/表示的 padding 优化，向量化逐候选池化；先用数值等价和定长输入检查，再重复量化吞吐/内存。随后仅用 train gold 做单批反向/optimizer 工程 smoke，不读 dev/test、不报告 WSD 指标。
2. **T02 provenance crosswalk**：只用本地 source metadata 与公开目录标识调查能否把 raw-sha256 指纹映射至准确上游对象；无法绑定即正式登记为 unresolved，不生成语义标注样本。
3. **总控和其他三线的就绪工作**：更新 PR 状态；T01 审阅流程、T03 固定任务断言、T05 license/schema 清单仅推进不需数据访问或用户科学决策的部分。

### 2026-10-31 2×2 batching 消融更正

完整预热的 2×2 profile 已完成，排序与 padding 倍数分别对照。ID/pad-1 编码 1.252/1.144 秒、padding 58.4%、额外峰值 90,208,768 bytes；ID/pad-8 为 1.232 秒、63.3%、101,390,336 bytes；length/pad-1 为 0.759/0.810 秒、1.8%、43,971,072 bytes；length/pad-8 为 0.858/0.885 秒、23.2%、53,596,160 bytes。length-sort/pad-1 相比 ID/pad-1 均值快约 35%，padding 低 56.6 个百分点，峰值少约 51%。pad-8 在两种顺序下都无优势；当前 profile 默认值改为 length/pad-1。关系池化 6.94–8.35 秒仍主导耗时。所有输入仍为 train candidate IDs 与图 gloss/rules，不读 labels/context/dev/test；不含反向或优化器。运行次数有限，结论是本机工程优选，非通用性能保证或 WSD 效果证据。

### 2026-10-31 B/C/D 向量化池化初测

把每个候选的 B/C/D 关系均值写成共同节点矩阵上的三行权重，再用一次矩阵乘法求出三种关系向量，减少逐分支/逐边的设备端小算子。与原直接均值定义的合成对照 `torch.allclose` 一致，autograd 梯度可回传；T04 相关 22 项测试通过。按长度排序/pad-to-1、同一 train-only 2,051 候选 profile，新池化 5.724/5.680 秒、峰值增量 25,088 bytes；向量化前数次同设置 profile 为 6.94–8.35 秒、峰值增量 339,456 bytes。粗略时延改善约 18%–32%，峰值增量减少约 93%。计时来自少量重复且池化含 Python 图遍历，仍是工程初测；在固定内存/时钟条件下应继续复测，不能视为 WSD 效果或全训练时长结论。当前下一步为 train-only 单小批反向/优化器 smoke，并记录显存峰值。

### 2026-10-31 合成结构池化 XPU 反向 smoke

在 `emotion_xpu` 的 Intel Arc 上，将可训练标量作用于合成节点向量，经 A/B/C/D 权重矩阵聚合、标量平方损失、反向和 SGD step；loss=11.5733、梯度=23.1466，参数由 1.0 更新到 0.7685，均为有限数。此项只验证 XPU autograd/optimizer 可执行，不读图数据、训练标签、上下文或 dev/test，也不是完整模型训练；下一门槛是在真实冻结 train-only gloss 向量上做一个小批结构前向与反向，并确认内存峰值。

实图文本 smoke 由 `src/analysis/smoke_t04_xpu_train_only_backward.py` 固化：首个 train candidate 的 18 个 OEWN 图 gloss、4 个 OR 分支输入 pinned BERT-tiny，在 XPU 上经过共享编码、A/B/C/D 池化、surrogate loss、37 个参数梯度及 AdamW 更新；surrogate loss=0.8871，peak allocated=87,755,264 bytes。该脚本仅读 candidate_ids 与 graph definitions/rules，不读 labels/context/dev/test。surrogate 目标不是真实 WSD 损失，因此这仍是可复现工程 smoke，不是模型质量或训练有效性证据。

### T04 监督式结构模型微批训练（2026-10-31）

新增 `src/analysis/train_t04_xpu_train_only_microbatch.py`。程序以 seed 17 从冻结 train split 确定抽 2 个 gold-covered 目标，构成 14 个候选、87 个目标/依赖 gloss 节点、31 个 OR 分支；模型固定为已核验哈希的 BERT-tiny，A/B/C/D 均使用完全相同的 `inputs.A` 上下文+原 gloss token 序列，结构分支只改变候选图池化。每个条件独立从相同预训练权重及相同 head 初始化做 1 次 cross-entropy/AdamW 更新；全部 39 个参数张量有有限梯度，XPU 峰值分配 A=164,270,080、B=194,585,600、C=195,894,272、D=194,585,600 bytes。两次精确重放的样本摘要、训练/模型 SHA、四个更新前 loss（A=2.008603、B=1.955209、C=1.985051、D=1.981746）及峰值均一致。该 loss 只是两条训练样本的更新前诊断，不能用于比较效果；没有 dev/test 访问或 checkpoint 外传。此项确认真实 train-only 监督输入能完成一次端到端参数更新；下一步扩展完整 train 的训练日志/资源记录，并在尚不评估 dev 的情况下先审核输入 token 预算和失败样本处理。
