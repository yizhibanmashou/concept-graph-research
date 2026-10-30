# 小型 BERT A–D WSD 开发试点：固定方案

目标：验证结构敏感的序列编码流程是否能够在共享候选和共同输入预算下训练与比较；不是最终性能主张。模型为 `prajjwal1/bert-tiny`，revision `6f75de8b60a9f8a2fdf7b69cbd86d9e64bcb3837`，BERT 两层、隐藏维 128，权重及词表固定摘要并留在本地。开发集已经用于基线纠错与预算方案设计，不能作独立验证。保留测试文档的句子和标签不读取。

文档划分沿用 SemCor 随机种子 17；从 train 和 dev 分别取按文档 ID、句子序号、词条序号加固定字符串的 SHA-256 排序最小的 400 和 120 个符合条件的目标。条件只用表面词、语料 Penn POS、`morphy`、是否为 `rdf` 实体和图中候选个数（至少 2），不使用 gold 选例。每个目标候选若超过 4 个，根据目标标识与候选 ID 的 SHA-256 排序取前 4 个，选择不使用 gold；未映射或正确义项不在其中的目标被记录为未覆盖且在所有版本一致排除。仅训练标签使用 train gold；开发标签仅在训练完成后用来计分。

每个上下文以 `target: 表面词 context: 句子` 输入，WordPiece 限 32 个 token，目标位于开头；每个候选独立使用局部短别名结构，四种表示的共同候选侧预算为 94 个 WordPiece（含候选自身两个特殊符号）。组合为 `[CLS] context [SEP] candidate [SEP]`，最多 127 token、统一补齐到 128。完整分支按现有 `compact_sense_budget` 的图顺序贪心选择，B/C/D 依赖清单一致；零分支及候选覆盖必须单列。上下文可能因截断丢失部分内容，实验不声称 128 是最佳预算。

四种条件使用完全相同的 BERT-tiny 初始权重、线性打分头架构、候选与训练样本、标签、初始化/洗牌种子 17：A 原 gloss，B 加依赖 gloss，C 在 B 上加成对边，D 在 B 上加完整分支。分别单独微调，一轮、AdamW 学习率 2e-5、批次 4，交叉熵排名损失，记录运行环境和模型摘要；不根据开发结果改学习率或选择版本。开发结果分别报告已覆盖子集准确率、将缺失预测按错计的已选目标准确率、结构分支保留情况；统计单位为目标实例，样本量不足以支持确认性差异或强弱排序。对比 B 与 D 仅是序列化结构的探索，字段标记和分支覆盖可混杂。

为排除工具和设备故障，先在少量训练样本做试运行并记录，正式对照重置模型与随机种子，从同一预训练权重开始。所有语料、选例、权重、模型检查点和结果只存被忽略的 outputs/tmp，不提交 GitHub。模型来源 [BERT-tiny 模型卡](https://huggingface.co/prajjwal1/bert-tiny)和 SemCor 数据许可证须分别遵守。GPU 浮点计算在不同硬件不保证逐字节复现；保存参数、种子、输入摘要和每条件的结果。

数据预试验后追加敏感性方案：原 94 token 候选预算导致已覆盖 train 中 213/251、dev 中 60/76 的 gold 候选没有分支，难以检验结构。追加候选预算 222、总长 256 的版本，其他选择规则不变。该预算是在查看开发集覆盖后选择的，结果只能作为进一步探索，不能视为预注册的正式对照或独立验证。

首次四条件训练后追加种子敏感性试验：对相同 252 条训练和 76 条覆盖开发实例，分别用训练随机种子 23、31 重训全部四个条件；除随机初始化、dropout 和训练顺序外，预训练权重、数据、候选和其他参数不变。三次使用同一开发集，不是独立数据集或统计显著性检验。
# Post-hoc target-position audit

The pilot takes the first 32 WordPieces of `target: ... context: ...` rather than a target-centered sentence window. Reconstruct covered train and development samples from the original SemCor XML positions and sample IDs; compare the reconstructed token prefix to the actual prepared model input, then use the tokenizer offsets to classify the sentence occurrence as fully retained, partially retained, fully removed, or unlocatable. The separate target-form prefix may remain even if the sentence occurrence is removed. Do not read held-out documents or reinterpret these counts as a model-performance effect.

# Post-hoc target-centered window

Reconstruct only the previously covered train and development sample IDs, use XML offsets to locate the annotated sentence occurrence, and keep it inside a 32-WordPiece prefix-plus-sentence budget. Preserve the original target-form prefix, all sample IDs, labels, candidate order and candidate token tails across A–D; reject a sample if the target cannot fit or if the old prepared input cannot be reconstructed. Candidate and joint budgets do not change. The data builder records original prepared hashes and per-split target coverage. Use the existing tiny BERT trainer with the same settings to compare windows, and identify seeds added after observing results as post-hoc. The development set is reused and cannot establish a final performance claim; held-out documents are not read.

# Post-hoc candidate coverage audit

Reconstruct the same 400 train and 120 development target sample IDs. Obtain candidate identities from surface form, provided POS and WordNet morphology before consulting the gold key. Compare gold coverage in the full graph candidate set and the original hash-selected maximum of four, count invalid or unmapped annotations, and report candidate-set sizes. This is an index coverage audit only; it does not establish that all candidates fit the representation budget or predict model accuracy. Test documents stay unread, and samples excluded by the original encoder must not be silently treated as model successes.

# Full-candidate builder context policy (engineering correction)

The full-candidate builder now locates the annotated target by its original XML word position and builds a maximum 32-WordPiece context from a target-form prefix plus a sentence window that contains the actual occurrence. `[unused0]` and `[unused1]` bracket that occurrence; their token IDs are taken from and recorded with the fixed model vocabulary. Neighboring whole XML words are added around the target until the budget is exhausted. If the target cannot fit or the annotated word does not match the stored XML position, the selected sample is excluded from scoring and its sample ID/reason is written to `excluded_targets.json`; the original selected-target denominator remains in metadata. A–D share the same context IDs and candidate order. The old prefix-only pilot remains a separate historical result and must not be described as having used this corrected context.

This is an input-pipeline correction only. At PR #34 merge time it had not been run on SemCor. The subsequent train/dev preparation and its limits are documented below; neither preparation result establishes model performance or makes the repeatedly used development set independent. Before any training, record the exact SemCor/XML, OEWN, graph, vocabulary hashes and candidate budget; report selected targets, excluded target-context failures, sentence-window truncation, gold mapping, candidate encoding failures and scorable targets separately. No held-out test documents or labels are used.

# Candidate morphology audit and all-analysis union (post hoc)

The first real train/dev preparation run used the public NLTK `morphy()` wrapper to obtain one lemma per surface/POS. In the fixed sample, 4 training and 2 development targets had a uniquely mapped gold synset in the graph but outside that one-analysis candidate set. A diagnostic union over all WordNet morphology analyses recovered all six without consulting the gold key: coverage among mapped in-graph golds changed from 375/379 to 379/379 in train and 115/117 to 117/117 in dev. The other 21 train and 3 dev targets were invalid, unmapped, or absent from the graph. This sample was already used for exploration; the result is a pipeline diagnosis, not an independent benchmark.

The builder now keeps the original selected target IDs and eligibility rule fixed, then unions candidates for the lowercased observed surface over all NLTK WordNet 3.0 morphology analyses for its POS. Candidate ordering is deterministic and gold-independent. On the same local sample this adds 71 train and 38 dev candidate-target pairs, removes none, and changes 7/3 target inventories. After regeneration the candidate totals are 3,404/910 with zero candidate encoding failures; mapped in-graph gold coverage is 379/400 and 117/120. The corrected A–D context/label/order/budget invariants were rechecked against the earlier output, with no violations. The implementation uses NLTK 3.9.2's lower-level `_morphy` method because public `morphy()` returns only its first analysis; this is private API and must be re-audited before version changes ([NLTK WordNet API](https://www.nltk.org/api/nltk.corpus.reader.wordnet.html)). This train/dev sample is exploratory and has already informed candidate design. No model was trained: the active Python environment lacks PyTorch, and no extra runtime was installed.
