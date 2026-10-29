# 飞书截图梳理与可执行研究问题（2026-10-28）

依据用户提供的两份文档截图整理；截图有局部截断，不能视为完整原文。以下区分文献所研究的问题、项目已有数据能回答的问题和待检验假设。

## NLP 应用：从“图有用”走到“结构额外有用”

截图建议 WSD 与义项表示优先，反向词典适合论文实验与网站共用；词汇替换、翻译及语义关系判断作为后续。固定相同候选、编码器、训练数据、预算、信息截断与调参，比较 A 原始释义、B 加依赖释义、C 与 B 相同信息加成对依赖、D 与 B 相同信息保留 AND 联合输入与 OR 分支；若角色本来缺失，不能把它编造成已有金标准。比较 B/C/D 应控制材料及长度，必要时给各版本加入相同预算的分隔符或进行预算敏感性分析。WSD 的 WordNet 3.0 与 OEWN 2025 不可仅按词形或 offset 假定一一映射；必须报告精确、多对一、未映射和歧义覆盖。训练/开发/测试在义项和来源家族层面避免泄漏。

反向词典以独立人写描述评估 MRR、Recall@K、Top-1，另测角色方向与否定；不拿资源释义查询同一个释义当作独立测试。WSD 报总体及频次分层，候选不完整时单独报告覆盖；完整定义是候选表示，不要求上下文逐字提及每项。依赖弧不能直接解释成蕴涵或因果关系。

## 截图中评测与论文链接核查

| 截图方向/链接 | 原始来源能支持的结论 | 对本项目的可执行选型 |
|---|---|---|
| [GlossBERT](https://aclanthology.org/D19-1355/) | 将上下文与候选释义组成配对输入进行 WSD | 作为 gloss-pair 基线；不能单独代表当前强基线 |
| [Gloss-informed Bi-encoder / BEM](https://aclanthology.org/2020.acl-main.95/) | 分别编码上下文和候选 gloss，以相似度检索义项；论文明确关注长尾义项 | 对照 A–D 的自然编码框架；保留目标词/词性候选约束 |
| [统一 all-words WSD 框架](https://lcl.uniroma1.it/wsdeval/) | 五个标准英文测试集都标注到 WordNet 3.0；框架网站还提供训练与结果材料 | 先复现其 WordNet 3.0 评测协议，再用 OEWN entry 的 sense-key 字段精确连接，并按测试标签报告覆盖、缺失和 synset 拆分 |
| [FEWS 页面与数据说明](https://nlp.cs.washington.edu/fews/) / [EACL 论文](https://aclanthology.org/2021.eacl-main.36/) | Wiktionary 来源，提供 few-shot 与 zero-shot 划分，面向稀有义项；数据说明还记录来源和限制 | 作为跨资源长尾压力测试；需显式建立 Wiktionary–OEWN 对齐，不把同名义项直接合并 |
| [EMNLP 2025 LLM 义项研究](https://aclanthology.org/2025.emnlp-main.1720/) | 报告 GPT-4o、DeepSeek-V3 在其 WSD 设置中与专用系统竞争，并分析域与难度 | 现代对照需同一候选和测试协议；论文结论不等于对本项目资源、模型版本或部署成本的保证 |
| [LMMS](https://aclanthology.org/P19-1569/) | 通过 WordNet 传播表示获得全覆盖义项向量，结合上下文表示用于 WSD | 作为 sense embedding 参照；本项目新变量应是构造的组合与分支信息，而不是“有义项向量”本身 |
| [WiC](https://aclanthology.org/N19-1128/) / [WiC-TSV](https://aclanthology.org/2021.eacl-main.140/) | WiC 判断两个上下文中的词义是否相同；WiC-TSV 给定目标义项做 target-sense verification，并覆盖多个领域 | WiC 可测上下文表示；WiC-TSV 更直接测候选义项与完整构造表示的匹配。需做 WordNet/OEWN 对齐或限制到可对齐样本 |
| [MultiRD](https://ojs.aaai.org/index.php/AAAI/article/view/5365) / [WantWords](https://aclanthology.org/2020.emnlp-demos.23/) | MultiRD 报告词典定义及人工描述上的反向词典评估；WantWords 证明交互产品形态可行。WantWords 论文描述集为 200 个人工描述，定义集另为 500 条 | 首选独立人工描述作主指标，定义查询仅作诊断；报告是否与图中词条、释义重复，并核验代码/数据各自许可证 |
| [LexSubCon](https://aclanthology.org/2022.acl-long.87/) / [SWORDS](https://aclanthology.org/2021.naacl-main.345/) | LexSubCon 将词汇资源、释义和句子语义信号用于替换；SWORDS 以人审候选和细粒度适用度评分提高覆盖与质量 | 中期可将结构信号接到上下文替换重排；不能只用义项相似度代替句法、搭配与可替换性 |
| [DiBiMT 2025 正式基准](https://aclanthology.org/2025.cl-2.1/) | 手工整理的词汇歧义翻译基准，2025 正式论文覆盖八种语言组合，并指出通用 MT 指标不能充分衡量消歧能力 | 作为后续应用方向；论文/数据站说明基准访问方式，先核验访问与再分发条款，再区分 gold 已知和端到端消歧 |
| [HyperLex](https://aclanthology.org/J17-4004/) | 以人工评分测量词对的分级类别隶属/词汇蕴涵 | 依赖图需要先抽取类别关系后才能尝试；图可达性不是 HyperLex 分数 |

**建议首轮实际基准顺序：**先做统一 WSD 上的候选召回与 A–D 固定编码对照，再用 FEWS 的 few/zero-shot 切分检查长尾迁移；反向词典优先复现 MultiRD 的人工描述测试。若无可核验映射，宁可报告可对齐子集覆盖和映射误差，也不要把 OEWN 与 WordNet 结果混成一个 F1。强 LLM 只在数据使用规则允许的封闭评估中对照，固定提示、模型快照、输出解析与调用成本。

这些数据站页面可以下载/提供数据，不代表所有内容都允许重新分发。FEWS 来自 Wiktionary，标准 WSD 数据与人工描述集有独立来源和许可；发布前逐数据集查看 LICENSE/Datasheet、署名和派生/缓存文件规则。当前 Git 忽略数据文件，不能声称已经有可从干净克隆复跑的基准。

### 本机数据与映射预审

本机已有一份 **WN30-lfs 条目键 → WordNet 3.0 synset** 的精确 crosswalk 记录：104,081 个唯一 synset 精确匹配，覆盖 88.4599%；174 个条目键未映射，且不使用 lemma/POS 模糊回退。该比率是特定逻辑形式资源按 `lemma#POS#sense-number` 精确对齐 WordNet 3.0 的身份覆盖，不是 OEWN 2025 映射覆盖、LF 正确率，也不是 all-words WSD 测试覆盖。原记录明确指出 Princeton WordNet 的许可不自动覆盖 WN30-lfs。

本机本轮数据文件清单未发现统一 WSD、FEWS、WiC 或 MultiRD 的标准评测文件；当前可运行的 `bank` 和反向词典输入仍是手工冒烟例。后续补做了一个不同于 offset 比较的官方 entry sense-key 审计：WordNet 3.0 的 206,941 个 sense key 中有 205,989 个（99.54%）逐字大小写折叠后出现在 OEWN 2025+ entry 文件；116,714 个 WordNet synset 的所有成员键都指向单个 OEWN synset，另有 378 个部分覆盖、241 个被拆分到多个 OEWN synset、326 个无目标。可复跑脚本 `src/analysis/audit_wn30_oewn_sense_key_crosswalk.py` 和 JSON 结果在根 `report/`。因此 WSD 的 sense-key gold 有较高覆盖的候选桥接，但不能宣称完整、一对一的 WordNet/OEWN synset 等同。仍需取得有明确来源/使用条款的基准测试数据，并针对每个 gold 标签审计映射覆盖、未映射和拆分歧义；测试文本与 gold 不进入训练或调参。

官方统一 WSD 评测页列出五个标准 all-words 测试集及其 ALL 合并集，测试义项均属 WordNet 3.0；单独评测数据包页面标注下载小于 1 MB。当前工作站到 Sapienza 官方网页和 `WSD_Unified_Evaluation_Datasets.zip` 主机的直接请求均超时，本轮未下载数据、未读取 gold，也没有标准测试分数。不要把第三方镜像的可得性等同于官方数据许可；拿到数据后仍需逐实例读取 sense key 并套用 OEWN crosswalk，区分未映射、多目标及 coverage-conditioned F1。来源：[官方评测数据页](https://lcl.uniroma1.it/wsdeval/evaluation-data)、[统一框架主页](https://lcl.uniroma1.it/wsdeval/)。

另一个可核查的数据线索是 [UFSAC 作者的项目仓库](https://github.com/getalp/UFSAC)：其 2.1 版列出用 WordNet 3.0 sense key 标注的五个 Raganato 转换集及 `raganato_ALL.xml`，数据经该项目格式转换；版本说明还记录了多词表达用下划线分隔的修正。仓库提供数据下载链接，但本轮未取得或检查数据。使用前须核对实例 ID、标签、分词和评测范围与原始框架的差异，并分别核验各源语料的使用与再分发条款；仓库代码的 MIT 标记不能自动推定所有来源数据均采用同一许可。

补充了老师所举的借出/借入角色方向检索诊断。对本地全量 OEWN gloss 用同一 BM25 查询 `temporarily let someone else use something that belongs to you`，`lend / loan` 仅列第八；查询 `temporarily use something that belongs to someone else`，前十没有 `borrow`。两条都将 `cannibalize / cannibalise` 排第一，显示词面重合模型没有承担者/物主角色或借贷方向信息。复跑命令分别为：`python -m src.analysis.reverse_dictionary_pilot --query "temporarily let someone else use something that belongs to you" --limit 8` 与 `python -m src.analysis.reverse_dictionary_pilot --query "temporarily use something that belongs to someone else" --limit 8`（工作目录 `hypergraph_analysis_exploration`）。这是对释义自身的诊断查询，不是独立人工描述 benchmark，不能用来报告正式 MRR/Recall。

## 认知与词典结构：哪些可验证

### 已有 85-basis 分析应如何承接

冻结包现有的[85 basis 认知分析](../../OEWN/graph/cognitive_development_analysis_zh.md)与[逐项清单](../../OEWN/graph/basis85_cognitive_inventory.tsv)报告：110,425 个 graph heads、154,206 条 Horn clauses，85 个 basis（72 个 OEWN 义项、13 个非 OEWN 关系义项），覆盖 110,425/110,425；清单把 basis 人工分为 29 个早期/核心、30 个生产性桥梁、18 个语言/逻辑/关系运算、8 个顺序存疑。四个分析输入文件本轮对照冻结清单的 SHA-256 均匹配。

该分析明确把 85 项称为贪心与单点删除意义下的不可删 incumbent，而非候选空间的全局最小值；`proof_depth` 是 Horn 闭包激活轮次，不是儿童习得阶段。其 `shortest_flat_cycle_length` 是把超边投影为简单有向边后的环长，忽略联合前提；不得直接解释为语义循环或心理依赖。`single_deletion_loss` 是覆盖集合变化量，不是 feature centrality 的人类判断。

这使当前项目的直接增量问题更具体：**在严格区分原始介词关系与实体/概念依赖后，13 个介词 basis 的单点删除损失和投影环长度是否异常？** 已做的介词截断试点只看 selected-witness 前沿与既定候选，不检验 basis85 的全局闭包变化，因此两项结果不可互相代替。建议下一步按 POS、语义角色及来源分层做 leave-one-basis-out 闭包审计；对介词单独比较原关系边、关系标签保留的重写与简单删除，再匹配节点度和定义长度的对照组。

对冻结表中 85 行按 `pos=prep` 做的描述性切片显示：介词 13 项的 `single_deletion_loss` 中位数为 107,304，其他 72 项为 108,276.5；`shortest_flat_cycle_length` 两组中位数都为 2，环长不超过 2 的数量分别为 7/13 与 46/72。这里没有做匹配或显著性检验，字段也不保留 AND 超边结构；这些粗略指标没有显示介词明显更不可删或更易形成短环，不能据此说介词“导致”宽连接。原 k=3 前沿截断中约 2,984/3,000 个根改变，是另一种干预，关注的是局部 selected-witness 路径，不能与 seed 删除统计混为一谈。

另对完整 110,425-head、154,206-clause OR-of-AND 图进行了介词 literal 消融（[代码](../src/analysis/preposition_horn_relaxation.py)，机器统计在根 `report/preposition_horn_relaxation_2026-10-28.json`）。介词依赖出现在 122,501 条子句中，共删去 207,753 个 literal。若逐项删除 literal 并保留变空的子句，623 条规则会由 AND 条件变成无条件事实；这个宽松上界把深度中位数从 320 降至 213、109,309 个 head 缩短路径，主要测到的是规则被意外改成事实的后果。更保守地丢弃这 623 个新变空分支后，仅 3,887 个 head 仍有从 basis 出发的推导，106,538 个不可达；在这 3,887 个可达 head 上，原图深度中位数为 34、消融后为 7，2,799 个节点变浅。两种干预都不是保义的释义改写：保留空规则会凭空造事实，删掉规则则可能抹去唯一解释路径。因此这项结果说明介词在现有完整构造依赖中承担重要的桥接/条件角色，却不能证明其制造了“噪声关联”或移除它会改善语义；下一步需要把介词关系重写成带方向与角色的显式关系，再和删边、原结构作同输入预算的对照。

还须和 Sloman–Love–Ahn 区分：其中心性来自人类对概念特征可变性/依赖结构的判断；当前 `single_deletion_loss` 来自图对 seed 删除的计算。两者变量层级不同，现有数值不能用于声称“心理上更中心”。

| 文献线 | 对项目的启发 | 不能直接推出 |
|---|---|---|
| Zhao 等概念自举 | 比较一次性完全展开与保留可复用中间块的结构成本与重复使用量；将块定义为保留完整分支的子图 | 图中频繁出现的子图等于人脑学习出的概念，也不等于复现其成人行为实验 |
| Li 等儿童语料义项增长 | 考察词义簇与外部资源对齐是否可行 | 簇的平均话语年龄、首次理解年龄和 OEWN synset 是同一个测量 |
| Brysbaert–Biemiller 测试常模 | 在权利和义项对齐可核验后，比较图结构指标与独立词义测试等级 | 等级直接是儿童年龄、词形匹配足以建立义项映射 |
| Ramiro 等历史扩展 | 按词形内历史记录比较最近邻链与其他机制，独立审核义项映射与时间不确定性 | 文献首次记载是概念诞生时间，或共现弧就是历史演化路径 |
| 结构中心性、词典网络、语义分解 | 研究依赖节点删除后闭包或解释路径变化；标注关系类别 | 图依赖即心理重要性、早学、具体、原语、因果或不可分解 |

截图中其他可追溯的研究线也需要保持各自的测量对象：[Sloman、Love 与 Ahn 的特征中心性研究](https://onlinelibrary.wiley.com/doi/10.1207/s15516709cog2202_2)用人类可变性/概念一致性判断与概念内部的依赖结构建立联系；它不是任意词典依赖边的直接效标。[词典核心、卫星与最小 grounding 集研究](https://arxiv.org/abs/1411.0129)及[定义环路研究](https://journals.aps.org/prx/abstract/10.1103/PhysRevX.2.031018)测的是定义网络拓扑及其和外部词汇统计的关系。可以在 OEWN 上分析 SCC、环路和可达核心，但需要先定义节点/边映射、去掉词性/介词造成的假边并做置换基线；不能把另一部词典的比例或“早学”结果直接套用到当前图。

**结构成本试点已执行**：复用同一 3,000-root、深度 4 的 selected-witness DAG，按 `(节点, 剩余深度)` 做 LRU 缓存。无缓存有 1,181,367 次递归状态计算；容量 256/1,024/4,096/16,384 键时，按 root 文件顺序分别减少 39.52%/68.13%/87.86%/95.80%；无限缓存减少 96.95%。反序和固定 seed-17 洗牌下，容量 1,024 的减少率为 68.26% 和 63.24%，显示有限缓存对处理顺序敏感。脚本 `src/analysis/witness_reuse_pilot.py` 已扩展，机器结果在根 `report/witness_reuse_capacity_2026-10-28.json`。这只验证指定证书图中的确定性计算可复用性；缓存状态并非心理概念，根顺序也非人的课程操控，不能据此重现 Zhao 等成人因果规则实验或声称学习效率提升。该论文的机制是动态 concept library 在有限搜索中逐步缓存、组合早先发现的子概念，报告四项行为实验共 N=570；详见[原文](https://www.nature.com/articles/s41562-023-01719-1)。

后续外部效标可先做少量人工对齐，制定不可对齐、歧义和分歧处置规则，并报告覆盖及偏倚；再考虑源家族分组留出。Brysbaert 与 Biemiller 的常模包含约 4.4 万词义的测试数据，[论文摘要](https://pubmed.ncbi.nlm.nih.gov/27659480/)说明其与其他习得指标的关系；[Ramiro 等](https://pmc.ncbi.nlm.nih.gov/articles/PMC5877971/)研究的是历史词义出现顺序，而非个体学习时间。

Li、Armstrong 与 Xu 的 [PNAS 2026 研究](https://pubmed.ncbi.nlm.nih.gov/42113977/)分析约 400 万条、覆盖 19–144 月龄儿童及照护者的话语，对 1,270 个词自动形成上下文义项簇，再用词典、人类相似度判断和 LLM 评价心理有效性。论文报告支持“具体义项偏早出现”“语义空间逐渐扩展”和“语义链可解释义项顺序”三项假设。可借鉴“按使用簇而非先验词典义项发现变化”的问题设定；语料年龄不是每名儿童首次理解该义项的实验测量，自动诱导簇也不与 OEWN synset 一一对应。论文页指出 PMCID 全文预计 2026-11-11 开放，而当前日期为 2026-10-28；目前依据 PubMed 摘要核对，未声称已复核全文或获得 CHILDES 原始数据。数据版权和使用条款需单独核对。

## 优先执行与停止条件

1. 修复现有测试并冻结数据哈希与运行环境；先做结构截断/缓存的纯计算试验，不重写原始资源。
2. 为 ToLogic 用现有六例检查输入和 AST 结构，保留参考答案只用于评估；扩展时按构式和义项家族留出，不能从候选反向选 gold。
3. 做反向词典候选生成与可见证据原型；基准数据集与许可核验、人工输入及 OEWN 映射完成前，报告为工程演示。
4. 在标准数据与映射就绪后实施 A–D 与 WSD/反向词典对照，按独立测试和多次随机种子报告，不先宣称增益。
5. 实测中间块的重用与最小展开，联合人工/行为效标之前，不宣称符合认知规律。
6. 后续认知结构分支从 SCC/环路拓扑的 OEWN 描述性复现入手；先按节点类型和关系类型分层，分别与随机重连、词频/释义长度匹配图比较，再决定是否值得人工评定。
