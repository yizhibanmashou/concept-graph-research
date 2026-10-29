# Phase 12：释义上下文 sense-ranking 基线

状态：已在经哈希固定的 OEWN 2025 Plus 名词子集全量运行并完成强制重跑复现。该阶段在 Phase 11 的起始名词词面候选后增加一个透明的词项重叠排序器；属于弱 WSD baseline 与资源内结构对齐诊断，不是人工语义 gold、定义蕴含验证或逻辑系统评估。

## 问题与方法

本阶段问：找到第一名词 lemma 候选后，释义中该候选以外的上下文，能否帮助排序该 lemma 的 OEWN 名词 sense？候选发现完全沿用 Phase 9/11 的确定性策略（前 12 个 token 中最早出现的最长 1–4 token 精确名词 lemma，并排除目标自身成员），以免把候选召回改动和 sense 排序混在一起。

排序器移除候选 lemma 的原文 span 及目标 synset 成员词形，将剩余上下文和每个候选 sense 的释义转为小写内容词集合，以 OEWN 2025 Plus 全部名词释义计算的平滑 IDF 加权二元 TF-IDF cosine 排序。无共享内容词时 abstain；最高分并列也 abstain，不以 sense ID 打破平局。排序不读取目标的 hypernym 边、冻结图、候选 sense 的 taxonomy 邻居或目标标签。只有排序结束后，才用同一 OEWN release 的直接 hypernym ID 作资源内评估代理。

实现：`src/analysis/gloss_sense_rank_release_baseline.py`；单元测试：`tests/test_gloss_sense_rank_release_baseline.py`。输出只保留聚合指标，不输出释义文本、逐条 sense 预测或逐条错误样例。

## 全量结果

| 指标 | 结果 |
|---|---:|
| 名词 synset / 定义字符串 | 84,909 / 84,910 |
| 有直接 hypernym 的定义实例（分母） | 77,173 |
| 起始名词词面候选覆盖 | 74,854 / 77,173（96.995%）|
| 可与至少一个候选 sense 对齐的候选池 | 28,449 / 74,854（38.006%）|
| 可用上下文唯一选出 sense | 13,528 / 77,173（17.529% coverage）|
| 唯一 top-1 决策命中直接 hypernym | 5,843 / 13,528（43.192% 决策命中率）|
| top-1 命中 / 所有可评估定义实例 | 5,843 / 77,173（7.571%）|
| 有任一正确 sense 的候选池中，匹配 sense 排名在 top-1 / top-3 / top-5 / top-10 | 20.539% / 22.061% / 22.106% / 22.110% |
| 候选排序时因无上下文词重叠 abstain | 61,326 个候选定义实例 |

因此，“存在正确候选 sense”与“文本上下文能选出正确 sense”是不同环节。相较 Phase 11 的 38.006% any-sense 候选池对齐，top-1 的 43.192% 是在仅 17.529% 覆盖上计算，不能解读为全量 sense 准确率。把排序候选限制到确有直接 hypernym sense 的 28,449 个候选池后，top-1 检索率为 20.539%；这是由同一资源关系定义的条件性 proxy，也不是独立 gold。数据反映这个简单词项重叠器信息量不足，应保留 abstention 并转向人工标注、带 POS/语法的上下文模型及独立评测，而不是据此接纳规则。

## 解释边界

- 词面候选仍是较早的 heuristic；本阶段只隔离评估“候选池给定后，朴素词项上下文排序”的增量，没解决候选漏召回、词形变化、POS、短语中心语或语境义项建模。
- OEWN 释义和直接 hypernym 关系来自同一 release，目标关系不是独立人工判定；任何 sense 对齐率都只能称资源内代理。
- IDF 语料含本次评测资源的候选定义，是无监督、transductive 的 release-local 权重；不能宣称为跨数据集泛化结果。
- 同义词成员掩码、停用词和 tokenization 均为确定性词面操作，不处理词形还原、否定/量化/作用域或关系类型。
- 此实验不读冻结 Horn 超图，不生成定义规则，不测试 85 个 basis、witness DAG、Horn proof、NLI，也不验证某个定义是否逻辑蕴含某个 hypernym。
- 不应把本结果与 AI-WordNet、其他任务或论文中的 sense/WSD 指标横向比较；只有统一的人工 gold slice、拆分和候选池协议才允许强比较。

## 复算与来源指纹

从项目根目录运行：

```powershell
python -m src.analysis.gloss_sense_rank_release_baseline --output outputs/phase12/gloss_sense_rank_release_baseline_2025_plus.json
```

强制复跑时添加 `--force`。输入发布包为 Open English WordNet 2025 Plus（release date 2025-12-31）；压缩包 SHA-256：`8832b8fa26a14c0ba8c99bb1ef8db6f9e122a6d9193b65ca9e0ef572580fee7e`。运行逐字节核验 27 个 entries JSON 和 26 个 noun JSON，53 个文件的聚合指纹：`feb374376407168e8392fe664682c81a0c9d70c3c7ad5bdd5d4416aa149a2b6c`。强制重跑前后输出 SHA-256 均为 `dbc676bf576ae66cf62ac5bec7f1ca87260a9f7af8ed93751a48e2c830d7aaa6`。全部分层汇总和数据指纹见[机器可读输出](../outputs/phase12/gloss_sense_rank_release_baseline_2025_plus.json)。

## 建议的下一步

1. 建立按 lemma/sense 隔离的双人 gold slice，标注 head span、候选 sense 与定义是否支持指定关系，并记录歧义/拒答。
2. 在同一 gold slice 比较首名词 heuristic、POS/chunk/依存解析、词典候选排序和上下文 WSD；报告覆盖、拒答、precision/recall、分层区间与错误类型。
3. 只将人工审定的 sense、span、逻辑 AST 与来源映射送入带证据的规则编译；分别做 AST/逻辑审阅、独立 proof replay 和盲测 NLI/人类语义验证。

这样可以分开定位词面候选、义项消歧、图知识覆盖和推理/语义判定的错误，不把其中一层的 proxy 指标误当端到端可靠性。
