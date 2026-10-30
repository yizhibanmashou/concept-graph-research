# T04 候选开发语料评估：MASC Sentence Corpus

评估日期：2026-10-31  
状态：**仅完成官方元数据与许可页面筛查；待负责人决定是否将其作为下一步开发语料。未下载语料包、未打开文本或标签。**

## 结论摘要

MASC Sentence Corpus 是目前发现的一个较强 T04 候选：官方介绍称它有约 110,000 句，覆盖 114 个常见多义词，以 WordNet 3.1 sense inventory 进行人工标注；句子来自 MASC 与 OANC，标签说明包含多标注者一致性材料。MASC 官方主页将资源置于 CC BY 3.0 US 条款下，OANC 官方说明其数据可自由用于研究与开发且不受使用、再分发限制。当前官方迁移 release 的 `masc_wordsense.zip` 清单给出 6,796,136 字节及 SHA-256 `ccce5d4468a799531cacb3968b0e07db025dd3fb52d354d556856b27ddc0d732`。

因此，**建议将 MASC 作为 SemCor 之后的候选开发/文档外推数据源，进入“经负责人批准后做只读数据盘点”的阶段**。它能检验模型是否迁移到另一批上下文文本；它不能直接提供对低频义项的覆盖，也不是独立于 WordNet/OEWN 的 sense inventory。只有在样本级条款、WN3.1→OEWN 映射、来源隔离和模型预训练暴露审查通过后，才可冻结实际实验协议。此文档本身不授权下载或读取数据。

## 官方证据与范围

| 事项 | 已核实信息 | 对研究设计的含义 |
|---|---|---|
| 语料规模和标签 | MASC 页面介绍约 110,000 句、114 个词、WordNet 3.1 senses；标签经人工判定。完整集合每条至少一位标注者；每词约 100 句有多位标注者，用于一致性分析。 | 可研究上下文判义与标注不确定性；不能把 114 个常见词包装成完整 all-words 或长尾 benchmark。 |
| 上下文来源 | 句子链接回 MASC 或 OANC 原文；官方将 MASC/OANC 作为开放语言资源。 | 与已反复使用的 SemCor 是不同语料来源，但拆分必须按原文档分组；需检查与超图 source families 及模型预训练数据的实际重叠，不能仅凭名称宣布独立。 |
| 许可 | MASC 首页写明 CC BY 3.0 US；OANC 官方页称数据可自由用于研究和开发、使用及再分发不受限。 | 元数据层面比 SemCor 清楚；下载后仍须核对具体 release 包的随附 license、署名说明和子文件边界，再把状态升级为本项目用途已审查。 |
| 冻结版本 | ANC 官方 2026-09-25 数据迁移 release 的 manifest 记录 `masc_wordsense.zip` 为 6,796,136 bytes，SHA-256 `ccce5d4468a799531cacb3968b0e07db025dd3fb52d354d556856b27ddc0d732`。该 release 声明保留各数据集原有许可。 | 可在批准后固定 artifact 身份并逐字节验 hash；此哈希只识别下载字节，不替代内容许可或标签质量审查。 |
| 义项映射 | 标注 inventory 为 WordNet 3.1；现有本项目词典映射审计重点是 WordNet 3.0 sense key→OEWN。 | 必须新建 WN3.1→OEWN 精确 crosswalk，按 lemma/POS/sense key 或可验证 synset identity 对齐；禁止 gloss 模糊匹配，完整报告一对一、多对一、歧义、缺失分母。 |

来源： [MASC 资源与许可说明](https://anc.org/data/masc/)、[MASC Sentence Corpus 标注方法](https://anc.org/data/masc/wordnet-framenet-annotations/)、[ANC 官方下载页](https://anc.org/data/masc/downloads/data-download/)、[2026-09-25 官方归档 release](https://github.com/nancyide/anc-website/releases/tag/datasets-2026-09-25)、[release 下载清单](https://raw.githubusercontent.com/nancyide/anc-website/ecc70bb/migration/download-manifest.json)、[OANC 数据使用说明](https://anc.org/data/oanc/)。

## 对五线总问题的有效性边界

若使用 MASC，最强可检验主张是：在候选 sense、上下文、训练划分和计算预算一致时，定义中的完整 AND/OR 构造能否比只加 gloss、依赖 gloss 或无向 2-section 更好地区分 MASC/OANC 的未见文档上下文。候选仍来自 OEWN，因此该结果测试的是**新上下文上的机器判义迁移**，不是独立词典资源的语义真值验证。

MASC 的词集由人工选取为常见多义词，不足以支持“长尾义项整体改善”的结论。可以预先把按训练频次分层作为次要分析，但不能把该分层改称为独立的长尾 benchmark，也不能根据已读开发标签重新挑词。短上下文可按预注册的上下文窗口消融作为次要分析。

## 若负责人批准，按以下顺序推进

1. **先封存来源与标签文件身份**：只下载官方归档到 Git 忽略的本地 `outputs/`；比对字节数和 SHA-256；记录 release commit、URL、许可文本和文件清单。此阶段只查许可/说明，不展示或解析样本句、sense 标签。
2. **先做 sense crosswalk，再看标签**：从可审计的 WordNet 3.1/本项目词典版本建立精确映射；固定 POS、lemma、synset 关系及冲突类别；若映射率或类别结构不足，停止模型效果实验并报告覆盖率。
3. **按原始文档划分**：基于 sentence corpus 暴露的 source-document ID，先制作不含 gold sense 的分组清单，按稳定 hash 分配 train/dev/holdout；同一原始文档不得跨 split。拆分与映射程序、随机种子、源文件哈希先冻结，再读取/评分标签。若 ID 无法可靠恢复原文档，停止“文档独立”主张并重新设计。
4. **控制预训练暴露**：现有 BERT-tiny checkpoint 的完整预训练语料清单尚未核实。确认数据无暴露前，不以其结果声称无泄漏；优先考虑训练语料可审计的 encoder，或将随机初始化小模型作为独立主分析，并把外部预训练版本列为敏感性对照。
5. **固定 A/B/C/D 与估计量**：A 原始 gloss；B 加依赖概念 gloss；C 在相同 B 信息上编码 AND 分支内无向 2-section；D 保留完整 AND/OR 分支及有序角色。控制目标、候选全量覆盖、上下文、输入/算力预算和初始参数。主要比较 D−B，C−B 为成对关系增量，A−B 为增补 gloss 增量；统一记录不可评分候选，禁止 gold 驱动裁剪。先在 train/dev 开发，不查看 holdout 标签。
6. **统计与报告**：以目标实例作配对单位，报告 macro/coverage-adjusted 指标、每词差值、seed 波动和不可评分分母；按词目标与原文档做预先规定的聚类重采样。单独报告标注分歧、映射失败、方向/角色错误、短上下文和频次子组。Holdout 只能在代码、映射、输入预算、主要比较和停止规则冻结后评分一次。

## 本次未做与当前决策

- 没有下载 release asset、读取 corpus 文件、解析样本/标签或计算覆盖率；所有上述结果只是基于官方说明的来源可行性评估。
- 未确认超图的全部来源 occurrence 与 MASC/OANC 文档家族无重合；未核实 BERT-tiny 的训练语料快照；未构建 WN3.1→OEWN 映射；这些是数据实验启动前的阻塞项。
- 请负责人决定是否批准 MASC 作为下一 T04 开发语料。批准后先执行第 1–3 项只读/label-blind 门槛，不自动解封 holdout，也不改变主研究问题。
