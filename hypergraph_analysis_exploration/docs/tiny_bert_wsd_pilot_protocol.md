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

# Candidate batching compatibility audit (2026-10-31)

The trainer accepts both archived pilot rows (no candidate manifest; every stored candidate is scoreable) and the newer full-candidate schema (explicit `candidate_ids` and `scorable_candidate_ids`; label `-1` means the gold candidate could not be scored). The data-only `batchify_rows()` helper is tested independently of PyTorch/XPU so that the old-schema fallback, the new-schema unscorable case, and a candidate-count mismatch are covered without loading corpus rows or training. Five trainer tests and two candidate-data tests pass, and both scripts compile. This is an input compatibility check only: it supplies no evidence about WSD performance or structure benefit. The fix and tests are on `codex/t04-full-candidate-packing` (commit `b7b42b6`).

# Fresh-document XPU run already on disk (2026-10-31)

The machine-local artifacts `outputs/tiny_bert_fresh_doc_xpu_seed{17,23,31}_20261031/result.json` record completed A/B/C/D runs on the document-disjoint SemCor train/dev preparation in `outputs/tiny_bert_fresh_doc_dev_20261031/`. This is an audit of existing artifacts, not a new training run. Rechecking the files confirms the recorded SHA-256 values for `train.json`, `dev.json`, and `metadata.json` match the run metadata. Each seed trained all four conditions on 379 trainable targets; the selected dev set has 120 targets, of which 111 have an encodable gold candidate. Across the three repeated evaluations, correct counts are A/B/C/D = 80/82/90/82 out of 333 target-seed evaluations (mean accuracy 24.02/24.62/27.03/24.62% over scorable targets); D−B is 0 percentage points in the pooled descriptive count. This is not 333 independent targets: the same 111 dev targets are reused across seeds. It remains exploratory and cannot establish a reliable condition ranking or a structure benefit.

The run metadata records candidate budget 222 and joint budget 256, a fixed BERT-tiny initialization, one epoch, batch size 4, and learning rate 2e-5. Coverage is asymmetric at the gold-candidate level: 379/400 train and 111/120 dev are scoreable; all three seeds share the same recorded train/dev/metadata hashes. The result JSON explicitly says development data were used in prior design and no test was read. Do not tune against this dev again. Before a new performance experiment, fix the C condition so it actually encodes pairwise topology distinct from B, equalize usable token/information budgets, and obtain a new independent evaluation source. The full local package/model paths and checkpoints are ignored and must stay local; no corpus, model weights, or predictions belong in Git.

# C-condition representation audit and fix (2026-10-31)

The prior `compact_sense_budget.representations()` encoded C as a flat list of all dependency aliases. That list contains no adjacency information, so the 80/82/90/82 three-seed scores above are not a valid A/B/C/D comparison for the intended pairwise-graph treatment. Preserve those outputs as historical engineering artifacts; do not reinterpret C as pairwise, overwrite them, or rerun the repeatedly used development set.

The proposed operationalization now defines C as the simple undirected 2-section of each candidate's complete AND branches: add one unordered dependency pair when both nodes co-occur in any branch, then deduplicate pairs across OR branches. C carries no direction, argument roles, multiplicity, or target-to-dependency edge. D still serializes the complete branch partition. Thus C intentionally loses which pairs belonged to the same higher-order branch. The same selected dependency glosses are shared by B, C, and D; branch retention and actual token counts must be reported because the corrected C can consume more budget. See `compact_sense_budget_protocol.md` for the full definition and limitations.

Four synthetic tests now cover alias consistency, pair generation, duplicate-edge collapse, and two different hypergraphs that share the same 2-section but have different D branch partitions. No SemCor rows or labels were read for this correction, and no data were regenerated or model retrained. The 2-section is a proposed control representation; obtain scientific sign-off before any new performance run.

The active environment is a Conda environment named `emotion_xpu`, not the default `base` interpreter. On this machine it reports Python 3.11.15, PyTorch `2.12.0+xpu`, Transformers `5.9.0`, and an available Intel Arc XPU. To check the environment without GUI use:

```powershell
conda run -n emotion_xpu python -c "import torch, transformers; print(torch.__version__, transformers.__version__, torch.xpu.is_available(), torch.xpu.get_device_name(0))"
```

No CUDA installation is required for this XPU setup. A training invocation additionally requires the prepared `train.json`/`dev.json`/`metadata.json` directory and a local BERT model directory with `config.json`, `vocab.txt`, and `pytorch_model.bin`; the trainer uses local files only. Example shape (replace `<LOCAL_MODEL_DIR>` and choose a new, nonexistent output directory):

```powershell
conda run -n emotion_xpu python -m src.analysis.tiny_bert_wsd_train --data outputs/tiny_bert_fresh_doc_dev_20261031 --model <LOCAL_MODEL_DIR> --out outputs/tiny_bert_rerun_seed17 --device xpu --seed 17
```

Do not rerun the same dev experiment merely to verify installation; the environment and an actual XPU tensor operation have already been checked, and the prior model runs are present locally.

# Post-hoc target-centered window

Reconstruct only the previously covered train and development sample IDs, use XML offsets to locate the annotated sentence occurrence, and keep it inside a 32-WordPiece prefix-plus-sentence budget. Preserve the original target-form prefix, all sample IDs, labels, candidate order and candidate token tails across A–D; reject a sample if the target cannot fit or if the old prepared input cannot be reconstructed. Candidate and joint budgets do not change. The data builder records original prepared hashes and per-split target coverage. Use the existing tiny BERT trainer with the same settings to compare windows, and identify seeds added after observing results as post-hoc. The development set is reused and cannot establish a final performance claim; held-out documents are not read.
