# T04 下一轮设计：把结构效应与文本长度分开

**版本：** 预注册草案 v0.1（设计审查前；尚未实现、训练或评分）
**日期：** 2026-10-31
**目标：** 检验在同一义项节点和同一释义文本下，保留成对结构或完整分支结构是否提供额外 WSD 信息。

## 1. 本地代码审查得到的关键结论

当前 A/B/C/D 序列化位于 `src/analysis/compact_sense_budget.py` 的 `representations()`。B 已列出目标义项的一跳依赖 ID 和释义；C 在完全相同的 B 上追加 `edges`，其值只是依赖别名列表；没有额外的边端点、依赖—依赖共现边或边标签。按当前 schema，C 与 B 使用同一节点/释义清单，C 的“边”没有表示独立于依赖清单的新成对拓扑。D 才额外记录各原始分支中的成员集合。

现有小模型中，B/C/D 每个目标候选平均非 padding token 分别约 135.87/156.71/160.51；D 比 B 多约 18.1%。因此，历史 C 不能被解释为经过充分表示的普通成对依赖图基线；历史 D–B 差异也同时包含序列化长度和结构字段差异。即使张量都 padding 到 256，也不能据此称有效输入预算相等。历史训练结果只保留为探索性实现结果，不能在新设计下重新解释为结构效应。

这是代码/schema 层面的发现，不是模型性能或语义正确性的结论。研究问题仍值得试验，但比较条件需要重新操作化。

## 2. 假设与估计对象

主要比较为 **D−B**：在节点释义文本、节点集合、文本顺序、候选集、上下文、训练实例、训练预算和模型参数量相同的前提下，完整分支成员关系相对无分组节点清单，对目标级 WSD 排名是否有增量效果。

次要比较为 **C−B** 与 **D−C**：分别估计成对投影，以及成对投影未保留的高阶分支成员信息是否有增量。目标是检验这一受控编码，不是证明某类模型普遍优于所有词义图方法。

允许结果：正增量、接近零、负增量或不确定。没有稳定、足够精确的增益时，保留负结果并停止扩张当前配置。

## 3. 条件定义

| 条件 | 候选侧共同节点内容 | 结构通道 |
| --- | --- | --- |
| A | 目标义项原始 gloss | 无；文本基线。此比较的内容量天然不同，只作应用基线，不作结构隔离主比较 |
| B | 目标 gloss + 同一完整的一跳依赖 gloss 清单 | 依赖节点作为无序集合，不提供依赖之间的分组 |
| C | 与 B 完全相同 | 每个定义分支先组成“目标 + 分支依赖”的集合，再展开为两两边并对所有分支取并集；保留边端点 ID，不保留原分支 ID/边界 |
| D | 与 B 完全相同 | 原始分支成员表：每个分支一个 branch ID，关联目标和该分支的所有依赖节点；分支之间保留为替代分支集合 |

C 是本项目明确定义的 pairwise projection，而不是声称所有现有词义图都采用这一具体规则。D 的 AND/OR 是来源数据中的组合表示，不是未经验证的自然语言逻辑蕴涵。当前资源没有可信语义角色标签，因此不能合成 agent/patient 等角色监督；角色信息一律缺失/unknown。

## 4. 输入和模型控制

### 4.1 同一词汇内容

B/C/D 的节点 ID、释义文本、顺序和 token IDs 必须逐候选完全一致。唯一变量是节点间结构张量/稀疏索引。实现不得把 C/D 结构额外序列化成更多自然语言 token；用同一个结构编码模块读取关系 mask，B 使用无分组 mask、C 使用成对边、D 使用超边成员关系。编码模块、参数量、初始化、优化器和学习步数在三条件完全相同。A 保留现有 gloss-only 基线，并明确其词汇信息不同。

长度审计必须按实际 tokenizer 给出每个 split/条件的非 padding token 分布、最大值和截断率。B/C/D 的 token IDs 哈希必须逐条一致，否则此实现不能支持主比较。结构通道的稀疏边/超边数量和显存/时间另行报告；等 token 数不等于等算力。

### 4.2 节点与分支上限

候选、节点和分支选择不得读取 gold。优先使用完整一跳清单；超出显存/存储上限时，先用仅由训练分区确定的固定上限和确定性排序作统一裁切，B/C/D 共享完全相同的保留节点/分支。若裁切会破坏分支闭合性或使各条件节点集不同，则将该候选标为共同不可编码，保留在原始目标分母并报告原因。不要分别为不同条件贪心装配。

每个目标记录完整候选身份和顺序、gold 映射状态、候选编码成功/失败、上下文定位、节点/分支覆盖、token 统计及结构大小。所有 A–D 使用相同的候选义项集合和顺序；不能按 gold 挑候选，也不能因 C/D 结构编码失败而从该条件的分母静默删除样本。

### 4.3 结构编码器

候选义项的目标节点和依赖节点均由同一个冻结版本的文本编码器编码，结构聚合使用共享的、置换不变的多集合聚合层；同一模块在 B/C/D 之间只接收不同关系索引。B 将所有依赖作为一个平面集合，C 对每个成对边进行共享聚合，D 先在分支内部聚合成员（AND 组），再对分支表示做共享的对称聚合（OR 候选集合）。A 使用相同文本编码器和打分头，但不输入依赖节点。正式实现前用小型合成结构核对：分支及节点重排不应改变输出；C 不含原始分支 ID；D 可区分相同节点并集但不同分支划分的两个候选。

该结构编码器是新的研究实现，不等同于已验证的语义推理器。它仍需和候选文本基线、参数匹配的随机/打乱结构控制比较；打乱控制只能用于训练分区的结构消融，不可改变评估标签或测试输入文本。

### T04-2b synthetic aligned-mask dry-run

新增 `build_aligned_relation_tensors()`，只从合成 target/branch ID 生成共享规范 `node_ids` 上的三种张量视图：B 为平面依赖 membership mask，C 为无向 2-section 邻接矩阵，D 为 branch×node incidence matrix。target index 显式给出；D 分支行、C 邻接和 B mask 均由同一节点清单对齐。8 项单测核对节点/分支重排不变、B 丢弃 branch partition、C 会将不同 D 高阶划分投影为相同张量、矩阵对称且无自环、以及空源分支拒绝规则。例子显示，一个四节点 hyperedge 与同一节点全集上的三个三节点 hyperedges 有相同 B/C 张量、不同 D incidence，说明 pairwise projection 丢失了高阶分支划分。

此 dry-run 不读取 OEWN、gloss、语料、gold 或标签；不调用模型、XPU 或训练。它仅验证 ID-only 关系张量的对齐和结构差异，不验证 tokenizer 侧的 token IDs 等价、释义对齐、真实图覆盖、编码器参数公平或 WSD 效果，不能替代 2b 的真实只读输入审计。正式实施仍需研究负责人批准评估来源与估计对象。

### T04-2b train-only 图候选覆盖审计（2026-10-31）

新增 `src/analysis/audit_t04_train_graph_inventory.py`。程序只从冻结 `train.json` 读 `candidate_ids`，逐一核对冻结 OEWN `nodes.tsv`、`hypergraph_rules.jsonl`、目标/依赖 gloss 是否存在，并验证每个候选能在同一 canonical node inventory 上构造关系视图；不访问 gold/label、上下文、dev/test 文件，也不输出义项 ID 或 gloss。输入摘要与聚合结果存于本机 ignored `outputs/t04_train_graph_inventory_20261031.json`。

复算结果：400 个训练目标包含 3,404 个候选出现次、2,051 个不同候选义项；2,051/2,051 均有目标节点、规则、非空分支和依赖定义，图关系视图失败为 0。按不同候选义项统计，分支数中位数 1、nearest-rank P90 为 3、最大 16；依赖数中位数 5、P90 为 10、最大 28；pairwise 边最大 327，D 的 branch-node incidence cells 最大 112。范围仅是既有训练候选池，不是模型候选覆盖率或全图分布，也不表示每个候选都满足相同 tokenizer 预算。

该初始图清单审计不使用 tokenizer。上述环境和词表“尚未找到”的记录是较早状态，已被下面的 train-only token 审计更新：冻结词表已恢复且摘要匹配，`base` 的 tokenizers 0.23.1 完成只读计数，`emotion_xpu` 保留作 PyTorch/XPU 训练环境。SemCor 重生成所需 NLTK 语料仍须独立核验；本轮不重新生成样本。

### T04-2b train-only 释义 token 对齐与单条长度（2026-10-31）

已从固定 BERT-tiny revision 恢复词表，SHA-256 与训练 metadata 一致；图 nodes/rules 摘要也在运行前逐项验证。新增 `audit_t04_train_shared_token_inputs.py`，仅从冻结 train JSON 读取 `candidate_ids`，metadata 仅读版本及输入哈希，不读取 labels、上下文、dev/test 文件。3,404 次候选出现涉及 2,051 个唯一候选，全部成功构造 B/C/D 共同的有序节点/释义 token 库，token ID 完全相同，失败 0。每个候选最长单条 gloss 的 WordPiece 数 min/median/P90/max=2/17/26/77；所有目标及依赖 gloss 的 token 总和 min/median/P90/max=3/56/120/380。该实现设想是每个 gloss 独立通过同一文本编码器，故单条 gloss 长度决定 512 位置上限；总和表示需编码节点量，不应误作单序列长度并据此裁剪分支。节点/边/分支数仍可能造成不同的真实计算量，须用之后的 XPU 运行日志/峰值内存/时长量化。17 项审计与结构专项测试通过；结果仅验证输入与长度范围，不是语义正确率或模型效果。

### T04-2c 参数无关的 B/C/D 关系聚合合成核验（2026-10-31）

新增 `src/analysis/t04_relation_aggregation.py`，对已编码的节点向量提供一个透明、无可学习参数的参考聚合：A 为目标向量加零关系通道；B 对唯一依赖集合取均值；C 对每条目标+分支 clique 的无向端点均值取并集均值；D 先对每个原始分支（目标及成员）取均值，再对 OR 分支取均值。所有条件输出维度一致，后续 scorer 可共享参数。该选择是最小可解释的接口/基线，不等于推荐最终神经结构，也不代表模型训练已完成。

4 项合成测试覆盖输入/分支置换不变、缺节点/空分支错误、同维度与 A 零关系通道，并构造相同依赖并集和相同 pairwise 2-section、但不同分支划分的例子：B/C 向量相等，D 向量不同。与结构张量和 token audit 共 15 项专项测试在 `emotion_xpu` Conda 运行通过。无语料或真实 label 输入，没有训练、dev/test 访问或性能分数。

### T04-2c train-only XPU 关系算子资源 profile（2026-10-31）

新增 `src/analysis/profile_t04_xpu_relation_aggregation.py`，只读取 train JSON 的 candidate ID 字段和这些目标的规则，不访问标签、上下文、释义文本、dev/test；对节点创建按 ID 哈希固定的随机 128 维向量，并在 XPU 执行已测的无参数关系池化。全量 2,051 个候选处理了 13,526 个目标/依赖节点实例、3,560 条分支和 41,316 个唯一 pairwise 边。相同环境/输入重复两次，设备同步 wall-clock 分别 3.7316/3.8978 秒，即 549.6/526.2 候选/秒；baseline allocated 2,863,104 bytes，重置峰值统计后聚合峰值 3,202,560 bytes，额外峰值两次均为 339,456 bytes。两次输出数值有限、结构计数和哈希一致。结果写入 ignored `outputs/t04_xpu_relation_profile_20261031.json` 和 `_v2.json`。24 项 audit/aggregation 专项测试在 `emotion_xpu` 通过。

解释边界：这个 profile 只测关系池化 Python/XPU 路径，随机向量不含词义信息；内存增量未包含 BERT 文本编码器、BERT 权重/激活、优化器、反向传播、训练 batch padding 或多个候选训练过程，吞吐也不是端到端模型吞吐。它说明当前稀疏结构聚合本身在该 train graph shape 上可运行，不能据此宣称真实训练资源足够或模型有效。

### 状态校正：旧序列化模型已在 Conda/XPU 完成三种子（2026-10-31）

后续检查本机 ignored outputs 发现，`tiny_bert_fresh_doc_xpu_seed17/23/31_20261031` 各有 A/B/C/D checkpoint 和结果记录。每个条件都在 `emotion_xpu`（PyTorch 2.12.0+xpu、Transformers 5.9.0、Intel Arc）成功训练一轮；因此“本机尚未训练”或“当前整体 WSD 训练仍待首次运行”均为过期说法。合并开发正确数 A/B/C/D=80/82/90/82，基于同一 111 个可评分目标的三个重复种子，D−B 净差 0。该数据是内部 SemCor 文档隔离开发样本，但已经用于多轮事后分析，只可作为旧方案探索记录，不能继续调参或当作确认性证据。

这三组 checkpoint 对应先前 JSON 序列化 cross-encoder，不是本设计的逐 gloss shared encoder + relation pooling。其历史 C/D 输入没有按本设计分开构造 pairwise 2-section 和 branch-incidence 结构；各条件实际 token 长度不同。新 pooling 尚未训练或在 dev 评估。下一步使用已记录的固定模型权重摘要在 train-only 输入上做共享文本编码器 + 新关系池化的单批前向资源 profile；若无法恢复原权重文件，才从 pin revision 恢复并复核哈希。后续效果评估必须另行冻结未复用的开发/测试方案、映射与许可，不得回头利用此 dev 选设置。

### T04-2d train-only BERT-tiny + 新关系池化前向资源 profile（2026-10-31）

固定 revision 的模型文件已恢复至本地 ignored `outputs/models/prajjwal1_bert-tiny_6f75de8b/`；`config.json`、`pytorch_model.bin`、`vocab.txt` 的 SHA-256 分别为 `cf3179684f7c360dd6185962d480e7d426ceb8fe49f5db7b64bdc15dba0b8798`、`dab2c2bddcfb48ea430ef63fd76d46d67d704487844d967256a50dd7d7fd0a66`、`07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3`，与既有训练记录和冻结词表一致。新增 `src/analysis/profile_t04_xpu_text_structure.py`，仅读取 400 条 train JSON 中的 `candidate_ids`、对应 OEWN 定义和规则；未访问 label、context、dev/test。对 5,592 个唯一目标/依赖释义用同一 BERT-tiny 单独编码，再对 2,051 个目标候选计算 A/B/C/D 参数无关结构池化。

batch size 32、按节点 ID 顺序动态 padding、2 个 warmup batch 的两次运行，文本编码 wall-clock 为 4.883/4.920 秒（约 1,145/1,137 gloss nodes/s），A/B/C/D 关系池化总计 7.206/7.958 秒（约 285/258 candidates/s）。65,370 个实际 token 被填充到 157,168 个 token 槽，padding 占 58.4%；动态峰值增量为文本编码 90,208,768 bytes、池化 339,456 bytes（后者在模型和节点向量仍驻留时测量）。四种输出均有限。两次摘要中的模型与输入哈希一致，数据结果仅保存在 ignored `outputs/t04_xpu_text_structure_profile_20261031.json` 与 `_v2.json`。

结论限于该 Intel Arc、该 TinyBERT revision、该固定 train 图规模和推理前向：本机确实能够执行共享 gloss 编码与新结构池化；旧序列化训练也已证明小模型 XPU 微调可运行。此 profile 不含 context 编码、打分头、反向传播、优化器或完整训练批次，因此不构成新结构 WSD 训练/精度结果，也不外推更大模型。资源上值得优先优化的是 ID 顺序 batching 导致的高 padding（58.4%）和逐候选 Python/Torch 小算子开销（A–D 池化耗时高于本次 gloss 前向）；下一步只做不看 dev 的等价实现优化与重测，然后再冻结共享上下文/候选打分及训练配置。效果评估仍须先有未复用开发集及许可、映射和统计协议。

真实前向 profile 的候选/节点读取、padding helper 与聚合行为新增 4 项测试；连同此前 24 项输入审计、结构聚合及 profile 测试，本轮 28 项在 `emotion_xpu` 通过。`python -m py_compile src/analysis/profile_t04_xpu_text_structure.py` 通过。数据、模型文件、输出 JSON 和 checkpoint 均保留在本机 ignored outputs，不加入 PR。

## 5. 数据、切分与指标

1. **旧 SemCor 开发集冻结。** 已反复用于方案开发的 120 条样本及其文档隔离子集不得再用于选择上限、池化器、超参数、停止点或主结果。历史结果只作为探索记录。
2. **先做来源和许可审计。** 选定新的公开 WSD 评估来源及其 train/dev/test 划分，检查授权、SenseKey/WordNet 3.0→OEWN 2025 映射和目标覆盖。测试句/标签在协议、代码和配置 hash 冻结前不得读取。若只使用既有 SemCor 训练资源，必须用未进入所有旧模型训练的完整文档做新的内部 train/dev 分配，并证明目标级/文档级无交叉；不能将旧 dev 重新命名为新 dev。
3. **候选空间**由上下文表面形式、词性、词形还原和公开词典索引构造，gold 只用于最后确定标签映射和计分。报告候选映射缺失、跨 OEWN synset 分裂、未映射 gold、共同不可编码目标；主要结果同时给出 scorable accuracy 和固定已选目标分母下的 coverage-adjusted accuracy。
4. **主要指标**为目标级 Top-1 accuracy；次要指标为 MRR、候选覆盖率及长尾分层。长尾定义只依 train 标签频数并在查看新 dev 前锁定；短上下文分层边界也由 token 数/句长定义，不按结果寻找阈值。
5. 至少三个预定随机种子用于训练稳定性描述，但种子不算独立样本。置信区间按目标做配对 bootstrap，并报告 D−B、C−B、D−C 的绝对百分点差和区间。样本量不足以排除有意义的正负差时结论写“不确定”，不追加种子直到显著。
6. 错误分析只用锁定 dev 的一次输出，按未映射/编码失败、候选数、train sense frequency、目标截断、结构节点/分支规模汇总；不得据此回头修改同一实验并继续报告为确认结果。

### 5.1 评测来源可行性筛查（2026-10-31；未下载数据）

| 资源 | 已核实的来源事实 | 适合的评测作用 | 主要 gate |
| --- | --- | --- | --- |
| Raganato unified all-words WSD | 统一框架包含 Senseval-2/3、SemEval-2007/2013/2015 五个测试集；工作中采用 WordNet 3.0 sense inventory | **主评测候选**：标准 all-words 范围更适合检验通用上下文消歧 | 逐子集核对文本/标注许可、下载版本和模型预训练/历史训练暴露；固定 WN3.0→OEWN 2025 映射及一对多/缺失处理；在协议和映射清单冻结前不读取测试句与标签 |
| FEWS | 官方页面说明其从 Wiktionary 释义与例句构建；数据表列出 121,459 条样本、71,391 个 sense type；官方创建代码注明使用 2020-01-01 Wiktionary dump | **长尾/低样本次要压力测试候选**；其目标分布适合考察少样本和零样本义项 | 本图也记录 Kaikki/Wiktextract 的 Wiktionary 来源，故 FEWS 与图释义存在同来源家族及潜在内容重叠风险；不能把它直接称作独立来源确认。需核对 sense-key 对齐、逐条/分家族重叠、标签定义与许可。Datasheet 还提示少量冒犯性例句/义项，需在查看原文前制定最小化暴露与汇报规则 |

来源核查依据：Raganato et al. 的[统一 WSD 论文](https://aclanthology.org/E17-1010/)；[FEWS 官方页面](https://nlp.cs.washington.edu/fews/)、[FEWS datasheet](https://nlp.cs.washington.edu/fews/datasheet.pdf)和[数据创建仓库](https://github.com/facebookresearch/fews)。这里的“潜在重叠”是由两者都源自 Wiktionary 推出的风险判断，尚未做逐记录匹配；此表不表示许可已批准。当前优先顺序是：先做不含测试文本的版本、许可与 sense mapping 元数据审计，再预注册统一 benchmark 子集和一次性评分；FEWS 保持为单独的后续长尾验证，不混入主结果或主开发集。

#### Sense key 映射与来源隔离的执行口径

Raganato 官方页面说明五个标准数据集的标注属于 WordNet 3.0 词义库存。当前代码已有 `audit_wn30_oewn_sense_key_crosswalk._load_oewn_sense_keys()`，可根据固定 OEWN entry archive 对 gold sense key 建立精确映射；正式评估前须逐资源报告零映射、唯一映射、多映射、目标不在冻结图、POS/lemma 不匹配和候选未覆盖，不能把“存在同名 key”直接当作映射通过。映射文件及 OEWN archive 版本必须固定并摘要化。

#### 本机 OEWN 包的义项标识字段检查（2026-10-31）

对 27 个 `entries-*.json` 文件做完整字段名扫描，不输出词条、释义或义项标识值。共 153,888 个 entry、161,875 个 POS 记录和 212,659 个 sense 对象；每个 sense 对象均含字符串字段 `id` 与 `synset`，同时可有额外字段（共见 558 种可选字段组合）。POS 记录可有 `sense`，并可选 `pronunciation`/`form`。按文件名排序后，对每个文件内容 SHA-256 再摘要的组合值为 `8701d5a20cc0f050d03f7d21033307a46c8ddd4432d7274ecc1a7363bcc60038`。这确认现有 WN3.0 exact-key crosswalk 的 OEWN 侧身份字段可从 sense `id` 提取；但本机扫描没有加载 WordNet 3.1 库存，也没有 MASC 标注或实例元数据，因此不能据此推导 WN3.1→OEWN 映射覆盖或 MASC 候选可评测。当前 99.54% 只适用于 WordNet 3.0 整体 sense-key 库存；外部 WN3.1 评估仍必须以冻结的完整库存/官方标识和逐目标映射审计为前置条件，不能用 gloss 相似度补映射。该 schema 检查不读取任何 dev/test 内容，也不解除数据许可、来源独立性或模型暴露门槛。

Global WordNet Association 的 [SemCor reannotation](https://github.com/globalwordnet/semcor) 保留原始 `wn30_key`，另提供随 OEWN 发行更新的 `oewn_key`；仓库说明该资源来源于 Princeton WordNet，并在 CC BY 4.0 下继续维护，底层仍带 Princeton WordNet License 署名条件。[格式与对齐说明](https://github.com/globalwordnet/semcor/blob/main/README.md) · [许可证](https://github.com/globalwordnet/semcor/blob/main/LICENSE.md)。这使它适合作为**sense-key 映射交叉核查和同源文档切分工具**，但它仍是 SemCor/Brown 材料，不能充当独立来源验证，也不能将更新后的标签视为独立标注者 gold。任何使用前还须固定仓库 commit、OEWN release、许可署名、数据变更范围，并核查与已有训练/开发样本及模型训练材料的文本重叠。

执行顺序固定为：先不接触 benchmark 测试句/标签，完成候选资源的许可与模型暴露审查、sense-key 映射覆盖元数据审计；再锁定与已用样本及训练文档不相交的开发方案、候选生成、预算、序列化、配置和分析脚本；最后才对完整保留 benchmark 执行一次评分。若逐子集许可无法核验，或映射覆盖不足且偏向特定词性/义项，则不运行确认性评估，报告缺失项与分母。

## 6. 执行阶段与 PR gate

| 阶段 | 交付物 | 通过标准 |
| --- | --- | --- |
| T04-2a：本设计审查 | 本协议、来源/许可选择、候选与切分清单 | 研究负责人审阅来源和估计对象；测试集确实未读；具体子集许可有来源证据 |
| T04-2b：只读输入审计 | B/C/D 节点清单/token IDs 等价报告、结构 mask 可视化小样本、完整候选覆盖和资源估算、WN3.0 sense-key 映射分母 | 无 gold 候选泄漏；B/C/D 文本完全相同；D 保留分支身份；结构对称性成立；逐资源映射覆盖和多映射均有报告 |
| T04-2c：训练代码 | 共享结构聚合器与 A/B/C/D 接口、固定配置、训练/推断共用输入构造 | 合成检查通过；参数数目、结构扰动、checkpoint 哈希及资源记录可核验 |
| T04-3：冻结评估 | 新 dev 的预定种子结果、配对区间、覆盖与错误分析 | 代码/config/source/hash 在评分前锁定；测试标签未访问；一次性评分 |
| T04-4：外部确认 | 独立 benchmark/FEWS 映射审计与一次评估 | 权限/跨资源映射通过，覆盖充分且与开发来源隔离 |

当前已完成旧序列化实现审查、设计草案和 text-free 关系 schema synthetic check。历史 A–D 与 corrected-context 三种子训练确实已在本机 `emotion_xpu` Conda 环境运行，但旧 C/D 输入没有隔离纯 pairwise 与完整分支效应，且同一 SemCor dev 已被反复使用；这些成绩只能作为探索结果，不能当作本设计的验证。新结构编码器、真实图输入等价审计、逐子集许可和新独立评测仍未完成。此文档不授权读取保留测试集。当前 tiny-BERT 能在 Intel Arc XPU 运行，不代表更大的结构输入模型已经通过显存/算力预算评估。

## 7. 相关研究与本项目的增量

- GlossBERT 将上下文和候选释义配对输入 WSD，说明 gloss 是有效的候选知识来源；它不验证本项目 AND/OR 分支的额外作用：[Huang et al., EMNLP-IJCNLP 2019](https://aclanthology.org/D19-1355/)。
- EWISER 把词汇知识图关系用于 WSD，说明结构化词汇知识可成为模型信号；本项目需证明来源构造分支相对合适的 pairwise 投影有增量：[Bevilacqua & Navigli, ACL 2020](https://aclanthology.org/2020.acl-main.255/)。
- AllSet 提供以多集合函数组合表示超图神经网络的通用框架，可作为 D 条件的架构参考，不是 WSD 效果证据：[Chien et al., ICLR 2022](https://openreview.net/forum?id=hpBTIv2uy_E)。

## 8. 结论标准

- 若 D 稳定优于 B/C，且 token 内容、候选、参数预算和数据切分均受控，可支持“此超图序列/结构编码在此 WSD 数据和模型下有增量”的有限结论；不能泛化到人类概念习得。
- 若 B 优于 A 但 D 不优于 B/C，证据支持额外释义内容有用，但不支持完整分支本身提供当前任务增益。
- 若 C 与 D 无差异，需结合区间和覆盖分析判断是证据不足、pairwise 足够或高阶结构无增量，不能只凭点估计下结论。
- 若结果不稳定、覆盖不平衡、结构信号不充分或评估区间很宽，报告失败/不确定并暂停该模型路线；不要换 dev、预算或切分以追求正结果。

### T04-2d 复核：完整预热与 batch padding 对照（2026-10-31）

前一版 text+structure profile 只预热两个较短 batch，不能提供可靠的稳态时延估计。本次脚本改为对全部 batch shape 完整预热一遍，再测第二遍；关系池化另预热 32 个候选。固定环境为 Conda `emotion_xpu`（PyTorch 2.12.0+xpu、Transformers 5.9.0、Intel Arc）、pinned BERT-tiny、batch size 32；只读取 train candidate IDs 与冻结图定义/规则，不读取标签、上下文、dev/test。样本为 5,592 个唯一 gloss、2,051 个候选，实际 token 数 65,370，最长 gloss 79 WordPiece（注意旧 token audit 记录 77；分词实现和定义文本边界需继续解释该差异）。

| Batch 策略 | padding 比例 | 编码时延 | 峰值增量分配 |
| --- | ---: | ---: | ---: |
| ID 顺序、pad-to-1 | 58.4% | 1.252 秒（一次） | 90,208,768 bytes |
| 长度排序、pad-to-8 | 23.2% | 0.858 / 0.885 秒（两次） | 53,596,160 bytes |

长度排序并 pad-to-8 的两次测量相对 ID 顺序基线显示：编码约快 29%，padding 减少 35.2 个百分点，峰值增量内存约少 41%。两项设置同时变化且 ID 基线只有一次，不能分离排序与 pad multiple 的因果贡献；需按同设置再重复并补充 length-sort/pad-to-1 和 ID/pad-to-8 消融。关系池化约 6.94–7.08 秒，额外峰值 339,456 bytes，现为下一工程瓶颈。该结论仅是本机 train-only 资源工程结果，不涉及准确率、语义保真或训练可行性。21 项 T04 专项/合成测试通过。

### 2×2 batch 排序与 padding 消融补记（2026-10-31）

为分离排序与 pad multiple，完成完整预热的 2×2 train-only profile（batch size 32，5,592 gloss，2,051 candidates）：

| 顺序 / pad multiple | 编码时延 | padding 比例 | 编码峰值增量 |
|---|---:|---:|---:|
| ID / 1 | 1.252 / 1.144 秒 | 58.4% | 90,208,768 bytes |
| ID / 8 | 1.232 秒 | 63.3% | 101,390,336 bytes |
| length / 1 | 0.759 / 0.810 秒 | 1.8% | 43,971,072 bytes |
| length / 8 | 0.858 / 0.885 秒 | 23.2% | 53,596,160 bytes |

同为 pad-to-1 时，length-sort 比 ID-sort 的均值编码时延低约 35%，padding 低 56.6 个百分点，峰值增量内存低约 51%。pad-to-8 没有收益。profile 默认采用 length-sort/pad-to-1。该选择只依据本机工程资源；profile 未读取标签、上下文、dev/test，也不含反向传播和优化器。计时重复有限，应在训练 pipeline 集成后再次复核；关系池化仍比释义编码更慢，接下来优先向量化池化并做数值等价测试。

### B/C/D 关系池化的权重矩阵实现（2026-10-31）

关系均值均可表示为同一节点向量矩阵上的线性加权：B 对唯一依赖节点等权；C 对 pairwise 边的两端累计半权后按边数归一；D 对每个分支（含目标）先取均值，再对 OR 分支等权。实现将三种系数构成 3×N 权重矩阵，一次矩阵乘法得到 B/C/D 向量，A 仍为目标向量拼接零关系通道。分支/节点 canonicalization 与 `pair_ids` 保持不变。

验证：合成例逐项对照原直接均值实现，B/C/D `torch.allclose`；带 `requires_grad` 的向量反传梯度均存在；T04 相关 22 项测试通过。在 `emotion_xpu` 上固定 train-only 输入 2,051 候选、5,592 gloss、length-sort/pad-1，向量化池化两次 5.724/5.680 秒，额外峰值 25,088 bytes。原实现的同设置有限次 profile 为 6.94–8.35 秒及 339,456 bytes。初步观察约 18%–32% 更快、额外峰值下降约 93%；样本量小，Python 图遍历仍在计时内，需在真实训练集成后复核。这仅是资源改进，不支持模型质量结论，也不代表已做新架构反向训练。

### XPU 反向传播与优化器工程 smoke（2026-10-31）

在 `emotion_xpu` / Intel Arc 上用合成节点向量验证权重矩阵池化的 autograd：可训练标量乘节点输入，计算 A/B/C/D 聚合和平方损失，执行 backward 与 SGD step。loss=11.5733，梯度=23.1466，参数从 1.0 更新到 0.7685，均为有限值。该 smoke 只证明合成结构路径的 XPU 反向及 optimizer 可运行；没有加载/训练新模型、没有使用真实目标标签或上下文，也不证明端到端训练资源/效果。下一步在不读 dev/test 的前提下，用真实 train-only gloss 编码的小批次做完整参数更新并测峰值内存。

### 实图释义单候选反向与更新烟测（2026-10-31）

新增 `src/analysis/smoke_t04_xpu_train_only_backward.py`，只从冻结 train JSON 取 candidate IDs，从 OEWN 图读取对应定义和构造分支；不读取 gold labels、句子上下文、dev/test。用 pinned BERT-tiny 对首个候选及其 17 个依赖 gloss（共 18 条、4 个分支；batch 形状 18×30）编码，A/B/C/D 经权重矩阵池化后用明确标注的 surrogate squared-norm objective 反传并执行 AdamW。Intel Arc XPU 返回有限 loss=0.8871、37 个梯度张量，峰值 allocated=87,755,264 bytes，step 正常。此结果只证明真实词典释义输入下小规模编码器—结构池化梯度路径可运行；surrogate loss 无 WSD 监督意义，不能称为训练结果、效果评估或足够支撑全数据训练的资源证明。完整命令由脚本 CLI 提供。

### A/B/C/D supervised train-only microbatch（2026-10-31）

`src/analysis/train_t04_xpu_train_only_microbatch.py` 将新结构分支接入现有 WSD train record 做一次真实标签更新。按 seed 17 抽取同样 2 个 gold-covered train 目标；14 个候选涉及 87 个唯一目标/依赖 gloss、31 个构造分支。四条件在相同 `inputs.A` 上下文+原释义 token 序列上评分，候选 graph features 分别为 A（目标释义向量+零关系）、B（唯一依赖均值）、C（pairwise 2-section 均值）、D（完整 OR branch 均值）；所有条件相同节点释义集合、tokenizer、预算、预训练 encoder 和 head 初始化，每个条件单独作一步 CE/AdamW。代码只打开 `train.json` 与 metadata，不读取 dev/test。

重复两次输出完全一致：selected sample hash=`b14406e815160c5428a2923ae0d00ffe70ec6da138f76431124724bacf075136`，train SHA=`e31e39e8b8ba1360ef89ff20ae13bfc9c7a7a05ac8797814ce69c2ca8167b4d7`，更新前 loss A/B/C/D=`2.008603/1.955209/1.985051/1.981746`；39 个参数张量均有有限梯度，优化器步正常。XPU peak allocated bytes A/B/C/D=`164270080/194585600/195894272/194585600`。以上是一个仅两目标、每条件一次更新的工程 smoke；四个训练 loss 受极小样本和随机 minibatch 支配，**不能比较或解释为 WSD 质量**。没有开发/测试评测，不产生模型 checkpoint。完整命令可由脚本 CLI 运行；profile JSON 留在 ignored `outputs/`。

通过门槛仅为真实 train-only supervision、shared encoder、结构池化、梯度和 optimizer 更新链工作。下一阶段在扩大训练规模前，先审查共同 token/context 序列、图释义编码成本、未覆盖候选的计分规则以及训练失败日志；旧 dev 仍不可用于调参，正式验证 gate 仍是新开发隔离、许可及 WN3.0→OEWN 映射。

### A/B/C/D 完整 train-only 结构 epoch（2026-10-31）

新增 `src/analysis/train_t04_xpu_train_only_structural_epoch.py`，把共享 gloss encoder 与 A/B/C/D 均值池化推进到完整训练分区的一轮工程运行。输入为固定训练 JSON 中 400 个目标（379 个 gold 可评分、21 个不可评分目标保留为不可训练），seed 17；四条件分别完成 190 个 AdamW 更新，target batch=2、graph-gloss batch=32。每个条件都从同一 pinned BERT-tiny 权重和相同随机 head 初始化开始，使用相同乱序训练目标、相同候选、相同 context+candidate-gloss token 序列；唯一条件差异是图关系通道：A 零关系、B 唯一依赖均值、C pairwise 2-section 端点均值、D 分支内均值再对 OR 分支均值。train-only 可评分候选池有 2,008 个唯一义项；每条件处理 3,243 个 context-candidate 输入和 17,265 个 gloss-node 输入实例。后续合成碰撞审计确认 B/C/D 这些均值均会丢失某些不同关系结构，因此该 epoch 只能称为首阶均值池化的工程训练/重放，不能作为“完整结构已送入模型”的证据。

在 `emotion_xpu` / Intel Arc 上，四条件 mean train loss 为 A/B/C/D=1.85719/1.86272/1.86111/1.85932；XPU 峰值 allocated bytes 为 224,224,256/223,901,696/223,901,696/223,901,696；单次 wall-clock 为 29.31/24.70/24.53/23.83 秒。相同输入、样本摘要、训练损失、峰值和四个 checkpoint SHA 在完整重放中完全相同。脚本和结果仅用于确认 379 条训练数据上的完整 optimizer 路径、可复现性与本机资源估算；训练损失不能比较为模型质量，计时仅为单机单次观测，也不构成泛化或公平效果结果。运行未读取 dev/test，也未查看其中标签。

复跑命令（输出目录必须为尚不存在的新目录；输出和 checkpoints 均仅保留本地 ignored）：

```powershell
conda run -n emotion_xpu python -m src.analysis.train_t04_xpu_train_only_structural_epoch `
  --data outputs/tiny_bert_full_morph_union_centered_20261030 `
  --nodes ../OEWN/graph/nodes.tsv `
  --rules ../OEWN/graph/hypergraph_rules.jsonl `
  --model outputs/models/prajjwal1_bert-tiny_6f75de8b `
  --out outputs/t04_structural_epoch_seed17_<new-run> `
  --seed 17 --target-batch-size 2 --graph-batch-size 32
```

专项检查：`py_compile` 通过；训练 schema、relation aggregation 和 XPU profile 相关 13 项单测通过。下一步不在已复用的旧 dev 上评估或调参；先解决外部 benchmark 权利、模型暴露与 WordNet/OEWN 映射 gate，再冻结一次性的全候选评测协议。若 gate 不能满足，T04 的可报告结论保持为工程可复现性与探索性训练，不声称结构增益。

#### 本机 Conda/XPU 启动方式与复跑

训练依赖已在现有 Conda 环境 `emotion_xpu` 中，不需要切换到 `base` 或重新安装 CPU 版 PyTorch。2026-10-31 实测 Python 3.11.15、PyTorch 2.12.0+xpu、Transformers 5.9.0；`torch.xpu.is_available()` 为真，设备为 Intel(R) Arc(TM) Graphics（报告总显存约 16.8 GB）。从子项目目录以模块方式运行，保证 `src` 可导入：

```powershell
Set-Location D:\大学资料\大三\科研实践2026\hypergraph_analysis_exploration
conda run -n emotion_xpu python -m src.analysis.train_t04_xpu_train_only_microbatch `
  --data outputs/tiny_bert_fresh_doc_dev_20261031 `
  --nodes ../OEWN/graph/nodes.tsv `
  --rules ../OEWN/graph/hypergraph_rules.jsonl `
  --model outputs/models/prajjwal1_bert-tiny_6f75de8b `
  --examples 2 --seed 17 `
  --out outputs/t04_train_microbatch_conda_replay_20261031.json
```

此命令已在本轮实际复跑成功：样本、训练集和模型摘要与前次记录一致，四种条件均完成一次 optimizer step。输出 JSON 与模型权重留在 ignored `outputs/`，不进入 Git。`transformers` 对预训练文件中未用于 `BertModel` 的分类/MLM 头报告 `UNEXPECTED`；当前结构编码使用的是匹配哈希的 BERT 主干，这些多余任务头是已知且预期的。两目标单步仅是管线 smoke，不代表训练收敛、资源足够支撑完整训练或任何 WSD 效果。

#### Train-only 覆盖与映射失败审计（2026-10-31）

新增 `src/analysis/audit_t04_train_only_coverage.py`，只读取 `train.json`、其 metadata 和冻结 OEWN nodes/rules；输出汇总数、哈希与截断/标记统计，不记录例句、ID，也不打开 dev/test。400 条训练记录中 379 条有可评分 gold、21 条没有：18 条 exact sense-key 映射缺失、2 条 gold 本身无效、1 条目标不在图中。与此相对，3,404 个候选出现全部通过编码准备状态检查，2,051/2,051 个唯一候选均在图中，候选编码失败为 0。因此当前不可评分样本的瓶颈是 gold 身份映射/数据元信息，不是 XPU 或候选编码器失败；不得临时用模糊映射补标签。

共同输入预算为 256 tokens；A 条件上下文 piece 中位数/P90/最大值为 32/32/32，候选释义为 16/24/85，padding 槽中位数为 207；400 条中有 250 条句窗发生截断，目标起止标记在 400/400 条中均各出现一次。旧序列化 B/C/D 与 A 每行都有差异，因此后续模型对照应继续用当前已定义的共享 `inputs.A` 文本输入，只改变图结构聚合；截断窗口的公平性和 token 总预算需在扩大训练前分析。机器摘要留在 `outputs/t04_train_only_coverage_audit_20261031.json`，不提交。专项审计测试与既有 T04 测试共 23 项通过。

#### Exact sense-key 缺失的 train-only 根因敏感性（2026-10-31）

新增 `src/analysis/audit_t04_train_gold_mapping.py`，仅打开确定性划分中的 SemCor train 文档、WordNet 3.0 词典、OEWN 2025+ sense index 与冻结 nodes，不读取 dev/test 文档。它复现原 400 条固定 train 选例，并核对样本 hash 与已准备 metadata 一致；输出仅含聚合数、输入 hash、训练文档成员 hash，不含句子、sense key、文档名、目标 ID 或标签修复。

结果为：379 条 exact 唯一映射且目标在图中；2 条源标注无效；18 条没有 OEWN exact sense-key 对应。其中 **14 条连 WordNet 3.0 `lemma_from_key` 都无法解析**；另 **4 条是有效 WN3 key，但其 WN3 synset 所有成员 key 均无 OEWN exact crosswalk**，因此连 synset 成员投票也没有可用证据。另有 1 条 exact crosswalk 的目标不在冻结 graph。对 4 条 valid-but-unmapped key，synset-level 敏感性中 4/4 均为 `synset_no_oewn_member_match`。所以“18 条不匹配”不能笼统说成 OEWN 义项映射遗漏，更不能通过模糊词形或邻近义项自动补齐；当前应将它们列为不可评分，并在未来 benchmark 中预先制定明确的跨资源覆盖规则。

在 `tmp/nltk_data`、`tmp/oewn-2025-plus-json.zip`、冻结 `nodes.tsv` 和 `outputs/tiny_bert_fresh_doc_dev_20261031/metadata.json` 上复跑，选例哈希 `6a444ed9823392840efded96b793121e0f9b272d762dff21c2c468c7851a6aa6` 与准备数据一致；解析 246 个 train 文档，dev/test 文档计数均为 0。输出 `outputs/t04_train_gold_mapping_audit_20261031.json` 留在本机 ignored 目录。该分析是覆盖/身份诊断，不评价 SemCor 标签语义，也不授权改变正式评测分母。

#### 词形候选覆盖修复与上下文预算（2026-10-31）

排查发现单一 `wordnet.morphy(surface, pos)` 只返回首选形态，会漏掉仍具词形歧义的词：train 样本中 `found` 没有把 `find` 的候选义项带入，`years` 没有把 `year` 带入，`felt` 没有把 `feel` 带入，共导致 4 个本可 exact 映射的 gold 义项不在候选池。候选构造现改为使用 WordNet 同词性下全部 `_morphy` 形态并集；目标样本排序仍由无标签的固定 sample ID 决定，形态候选不读取 SemCor gold 来增补。 为保持当前 400 条 train 选例 hash 可直接比较，入选资格仍按原先首选形态具备至少两个候选的规则确定；全形态并集仅扩展这些固定目标的候选池。未来若改为“任一形态有至少两个候选即可入样”，必须视为新的抽样总体并重新冻结 sample hash。候选池恢复为 3,404 次出现、2,051 个唯一义项；379/400 exact 可映射 gold 均进入候选池。另 21 条映射/元数据问题依然不可评分，不自动修标签。

上下文 budget 审计按全部 A/B/C/D 及 13,616 个候选—条件输入对统计，不再只看 A。固定候选序列预算 222，加目标上下文 cap 128 与特殊符号，统一张量宽度为 352；A/B/C/D 的实际最大序列长度 351，均低于 BERT-Tiny 位置上限 512。128-token cap 下只有 3/400 句窗截断，起止目标标记错误为 0。32/64/96/128 cap 的截断目标数分别为 250/48/9/3；对应最大序列为 255/287/319/351，全部条件均在各自共同预算内。128 cap 比 32 cap 多约 9.6% 的候选—条件 token 出现量（1,828,331 vs 1,668,395）；这是计算成本，不是效果增益。

训练环境使用 Conda `emotion_xpu`：Python 3.11、PyTorch `2.12.0+xpu`、Transformers `5.9.0`、Intel Arc XPU 可用；`nltk` 不在该环境内，因此数据构造/审计通过本机研究环境运行，模型训练只通过 `conda run -n emotion_xpu ... tiny_bert_wsd_train` 读取已冻结 JSON。train-only 四条件一轮训练已完成并以相同 seed 重放，启动时不读取 dev/test。每条件 379 条，mean loss A/B/C/D=1.859496/1.853116/1.853980/1.862553；checkpoint SHA 在完整重放中逐项一致。该结果只验证工程训练链与确定性，不把 loss 或小样本训练表现解释为 WSD 质量提升。训练命令增加 `--train-only`，避免访问 dev/test。

### T04 外部 WiC 评测源首轮筛选（2026-10-31）

本轮只核对官方项目页、基准论文/ACL 页面和仓库许可文件；未下载或打开 WiC/WiC-TSV/GrainWiC 的任何实例、文本或标签。

| 候选 | 可核实事实 | 对本项目的限制与结论 |
| --- | --- | --- |
| 原始 WiC / SuperGLUE WiC | WiC 官方页声明数据为 CC BY-NC 4.0；SuperGLUE 论文说明提交系统不得在开发中使用构造 WiC 标签时所用的结构化源数据，并举例为 WordNet、VerbNet、Wiktionary sense-annotated examples。 | 本项目图及训练流程使用 OEWN/WordNet、Wiktionary 派生知识；若按官方 SuperGLUE WiC 规则报告，图资源和相关源信息会触及该限制。因此不作为当前结构增强系统的确认性主评测，不能只凭 CC BY-NC 许可认定 benchmark-use 合规。 |
| WiC-TSV | 官方论文将其定义为多领域 target-sense verification，任务可不依赖外部 sense inventory；官方 GitHub 仓库有 MIT LICENSE。 | MIT 文本覆盖软件与仓库文档，不能自动视作数据授权。官方 repo 页面未找到数据集自身许可证/来源授权说明；数据许可和每个子集的文本来源仍 unresolved。不下载/不评测。 |
| GrainWiC fine-grained | 官方数据卡给出 1,185 对、924 个目标词、WordNet 3.1 noun/verb 义项；两套数据均为 test-only。数据卡标 CC BY-SA 4.0，并说明定义和用例来自 WordNet 3.1、按 Princeton WordNet License 使用。 | 任务形态接近义项级 WiC，但同属 WordNet 资源谱系，与 OEWN/WordNet 图存在明显来源邻近；只有 test split，不能调阈值或选模型。可作为未来一次性、明示同源边界的次要评测候选，不是独立来源验证；必须先做不看测试条目的 WN3.1→OEWN 库存级映射、重叠风险和模型暴露核验，并冻结所有决策。 |

**决定：**目前没有经许可、benchmark 规则、来源独立性、sense mapping 和模型暴露五项门槛共同核准的外部确认性测试。WiC 不适合当前 graph-informed 方法的 SuperGLUE 合规结果；WiC-TSV 等数据许可未确认；GrainWiC 仅保留为同源 test-only 次要候选。继续核查时不得打开其 test 文件或基于覆盖数字修方法。首先从公开 license/release 文档与 WordNet 3.1/ OEWN 完整库存建立不触碰 benchmark test item 的 crosswalk 可行性，再决定是否值得申请/使用相应数据。

来源：[WiC 官方许可页](https://pilehvar.github.io/wic/)；[SuperGLUE 论文（WiC 源数据限制）](https://w4ngatang.github.io/static/papers/superglue.pdf?file=superglue.pdf)；[WiC-TSV 官方 repo](https://github.com/semantic-web-company/wic-tsv)及其[代码 MIT LICENSE](https://raw.githubusercontent.com/semantic-web-company/wic-tsv/master/LICENSE)；[WiC-TSV ACL 论文页](https://aclanthology.org/2021.eacl-main.140/)；[GrainWiC 官方数据卡](https://huggingface.co/datasets/cardiffnlp/GrainWiC)。

### 2026-10-31：D 分支均值不是无损的完整结构表示

代码审计发现，当前 `aggregate_relation_views()` 的 D 将每个 AND 分支内 `target + dependencies` 做均值，再对 OR 分支均值做均值；它最终只是节点向量的线性加权，未把 branch×node incidence 交给 scorer。C 虽先构造 pairwise 边集合，随后也只对全部边端点做加权均值。用同一 target `head`、同一依赖节点 `{a,b,c,d}`、两个各含 2 个依赖的 OR 分支作合成反例：`{{a,b},{c,d}}` 与 `{{a,c},{b,d}}` 的分支划分与 pairwise 边集合均不同；但 B、C、D 三个 pooled 向量完全相同。C/D pooled relation 均为 `[5.0, 1.333333...]`。因此当前 B/C/D 的均值池化不能区分该反例中的三种结构；先前“D 保留完整分支结构”的说法只对某些结构例子成立，不能概括此池化算子。完整 train-only A/B/C/D epoch 只验证首阶均值池化的可重放训练，不验证无损完整结构或高阶组合增益。

现有合成测试新增该碰撞作为明确限制，保留另一个 D 可区分不同分支大小的例子，避免从单个正例推断普遍可辨识性。下一版核心 D 条件应将原始 branch×node 归属显式提供给 permutation-invariant branch-set encoder/scorer；C 也必须让 pair endpoint 信息在聚合前经过非线性关系项编码，不能只做线性端点均值。B/C/D 使用相同的关系项编码器与输出维度，参数量和文本节点集一致。先做结构碰撞/置换不变/梯度性质审计，再做 train-only 工程训练；在新实现与 token/算力控制冻结之前，不读取旧 dev 或任何保留测试。此为表示算子审计，不是语义保真或 WSD 性能结果。

为下一实现准备，`aggregate_relation_views(..., include_relation_items=True)` 可选返回未作跨项均值的 B 依赖节点矩阵、C pair-endpoint 项矩阵和 D 每个 OR 分支的独立均值向量；默认仍关闭，既有 train-only 基线不改变。相同节点集的合成反例中 B item 相同，而 C/D item 矩阵不同。新建 `t04_relation_set_encoder.py`，对 B/C/D 项共享同一个 `Linear-GELU-Linear` 非线性映射，再作项集合均值。固定 seed 19 下，CPU 专项 10 项通过；在 Intel Arc XPU 上也复核 B 保持相同、C/D 区分该反例、梯度有限。此原型没有接入 WSD train-only trainer，也没有使用词典或语料数据；不能证明更广泛结构可辨识、语义保真、模型训练效果或 WSD 增益。下一步先完成参数匹配/初始化与所有候选关系项覆盖审计，再接入 train-only 训练器并记录资源和失败项。
