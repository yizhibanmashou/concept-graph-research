# SemCor 文档划分和训练部分映射核查

研究目的：在任何模型训练或评测之前，测量训练数据中的 WordNet 3.0 义项标签通过精确 sense key 接到本地 OEWN 图的覆盖情况。此分析不评估 WSD 准确率，不调整模型，不读取开发或保留测试文档的句子及标签。

SemCor 3.0 作为本项目的独立语料来源，**不作为统一 WSD 标准测试集**。先把所有文档 ID 排序，以种子 17 打乱，前 `floor(0.70*N)` 为 train，接下来的 `floor(0.15*N)` 为 dev，其余为 test。划分在读取语义标签之前确定，并将 ID 分区保存于本地忽略的输出；不根据标签、词形或结果调整。文档分离不保证词形、来源家族或跨语料不重叠，未来模型比较须另加审计。

只遍历 train 的 NLTK `tag='sem'` 标注；对能获得 WordNet lemma sense key 的节点，以大小写折叠后的 key 精确匹配 OEWN 2025+ entry。官方 entry 的裸 synset ID 若在图中找不到，则加 `oewn-` 前缀查找；逐项区分未映射、多目标、目标不在冻结图、目标在图但 WordNet lemma 不属于目标图的同词性候选，以及严格候选覆盖成功；其他无法解析的标签单独统计。WordNet lemma 中 `_` 转空格再与图中的 `/` 分隔词形匹配；词性严格匹配而不做同义替换。重复的词实例分别计数，文档是数据分割单位。标签覆盖与语义等价、泛化、性能是不同问题。

首次运行发现 entry ID 与冻结图 ID 使用不同前缀，造成错误缺失计数；已添加明确归一化并废弃首个结果，重新运行使用新输出文件。

前缀修正后的探索发现，严格候选未覆盖集中在 WordNet 卫星形容词 `s`；追加事后敏感性计数：将 WordNet `a`/`s` 和图的 `a`/`s` 作为同一形容词大类，仅在词形也严格相同时统计可额外覆盖的实例。严格结果仍保留，不使用这些计数修改图或模型；这不是事先固定的主要指标。

本地固定 NLTK 数据 revision `550b6625bcef1f2abff2ff770a5a0d272c9c6b2a`：SemCor 3.0 zip SHA-256 `126fa2e829ab63edd5b3fd9de45ef1d60d6880e01e25abc55b5ac7918a824655`，WordNet 3.0 zip SHA-256 `cbda5ea6eef7f36a97a43d4a75f85e07fccbb4f23657d27b4ccbc93e2646ab59`。上游 [NLTK SemCor 元数据](https://github.com/nltk/nltk_data/blob/gh-pages/packages/corpora/semcor.xml)要求遵守并保留相关版权和免责声明；语料和生成的分区清单只存本机忽略目录，不随项目上传。OEWN entry 和冻结图均记录独立 SHA-256，实际使用许可须分别核验。
