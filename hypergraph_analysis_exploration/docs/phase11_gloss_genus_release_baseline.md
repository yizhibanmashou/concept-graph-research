# Phase 11：OEWN 2025 Plus 全量名词 genus 词面基线

状态：已对 OEWN 2025 Plus 的名词 synset 全量运行并核验输入文件。该阶段扩展 Phase 9 的确定性词面 heuristic，提供一个资源内结构对齐代理值；不是语义标注、释义解析、逻辑化或 NLI 实验。

## 问题与方法

本阶段问的是：只看释义最前面的词面，能否找到一个名词候选；其任一 OEWN 名词 sense 是否出现在目标 synset 的直接 hypernym 列表中？处理每一条定义字符串时，脚本跳过开头限定词、对 `someone/something` 等起始不定代词 abstain，并在前 12 个 token 中寻找最早出现的最长 1–4 token 精确名词 lemma。目标自身的成员 lemma 被排除。候选有多个 sense 时不做 WSD，“任一 sense 命中”即记为命中。

实现与复算入口：`src/analysis/gloss_genus_release_baseline.py`。输入是项目外只读的 OEWN 2025 Plus 发布包及其解压文件；运行前核验压缩包哈希，并将读取的 entries/noun JSON 文件逐个与压缩包内同名文件作字节级比较。输出仅含聚合统计和输入指纹，不写出 gloss 原文或逐条释义结果。

## 覆盖范围与结果

| 指标 | 结果 |
|---|---:|
| OEWN 名词 synset | 84,909 |
| 定义字符串 | 84,910 |
| 含多条定义字符串的 synset | 1 |
| 有至少一个直接 hypernym 的定义实例（评估分母） | 77,173 |
| 无直接 hypernym、排除出匹配率分母 | 7,737 |
| 找到词面候选 | 74,854 / 77,173（96.995%）|
| 候选任一 sense 命中直接 hypernym | 28,449 / 74,854（38.006%）|
| 命中数 / 全部可评估定义实例 | 28,449 / 77,173（36.864%）|
| 每个候选 lemma 的 OEWN 名词 sense 数（均值 / 最大值） | 3.573 / 33 |

可评估实例中另有 46,405 条得到候选但没有候选 sense 出现在直接 hypernym 列表，2,319 条没有词面候选。匹配率随 lexname 差异明显；例如 `artifact` 为 64.85%（7,725/11,912 个有候选实例），`animal` 为 13.26%（919/6,931），`plant` 为 12.55%（1,000/7,968）。这些差异是分层诊断，不解释为类别语义难度或 parser 表现差异。

这里的一行统计单位是“定义字符串”，而非唯一 synset；由于有一个 synset 有两个定义字符串，总定义数比 synset 数多一。排除没有直接 hypernym 的定义实例后，分母也是 77,173，而不是 84,909 或 84,910。

## 解释边界

- “候选命中”只表示候选 lemma 的至少一个名词 sense ID 与同一个 OEWN 版本记录的目标直接 hypernym ID 相交。这是同资源内部、且因任一义项匹配而偏宽松的结构对齐代理，不是义项级 precision、人工 gold、定义忠实度或自然语言蕴含。
- 词表与比较用的 taxonomy 都来自同一 OEWN release，存在资源内依赖；结果不能充当独立验证。heuristic 没有上下文 POS、短语中心语解析或 WSD。
- 本阶段没有把候选写入冻结 Horn 图或生成规则；不检验 85 个 basis 原语、AND/OR 规则、方向、witness DAG、proof soundness 或 NLI。更不能由此推断可验证知识库已构建完成，或优于神经方法。
- 这是 OEWN 2025 Plus 的名词子集全量 census，不覆盖动词、形容词、副词，也不是冻结包 110,425 个 head 的全量实验；两套资源的计数和目标不可混用。
- 不能把本阶段 38.006% 与 AI-WordNet 论文报告的 64.8% direct-hit 直接横向比较：AI-WordNet 的任务是为未收录新 lemma 预测/选择 hypernym，使用其专门训练与检索流程；本阶段是在已有 OEWN 定义上执行第一名词 heuristic，并以任一 sense 匹配作宽松 proxy，样本单位、候选空间与评测 protocol 均不同。两个数值都不是同一 gold slice 上的对照实验。

## 复算与来源指纹

从项目根目录运行（需本地配置的只读 OEWN 发布包、相应解压目录以及 Phase 7 来源 manifest）：

```powershell
python -m src.analysis.gloss_genus_release_baseline --output outputs/phase11/gloss_genus_release_baseline_2025_plus.json
```

压缩包 SHA-256：`8832b8fa26a14c0ba8c99bb1ef8db6f9e122a6d9193b65ca9e0ef572580fee7e`。本次核验读取并逐字节比对了 27 个 entries JSON 和 26 个 noun JSON；这 53 个文件的聚合输入指纹为 `feb374376407168e8392fe664682c81a0c9d70c3c7ad5bdd5d4416aa149a2b6c`。完整分层数值和输入元数据见[机器可读结果](../outputs/phase11/gloss_genus_release_baseline_2025_plus.json)。输出 SHA-256 为 `270897b9d3d8e27f6851b965f929a6a781f68111c4ec64cfaf4d11807b44773d`；强制重跑后字节级一致。

## 后续工作建议

1. 先人工定义和标注 definition-head span、sense 及直接上位关系，按 lemma/sense 分组隔离 train/dev/test，并以双标注和裁决建立可靠基准。
2. 用这个 heuristic 作为弱 baseline，与 POS/chunk/依存解析、词典式候选和 LLM 候选在同一 gold slice 上比较；报告精确率、召回率、覆盖率、拒答率和置信区间，而非仅报资源内命中。
3. 只有通过 sense/span/逻辑 AST 人审的候选才进入带来源证据的规则编译；随后单独检查 Horn 投影和证明证书，再用盲测 NLI/人工蕴含判断评估语义层。

这一顺序能把词面候选失败、义项消歧失败、逻辑化错误、图知识覆盖缺口和推理错误分开测量。

2026-10-08 Phase 139 使用当前工作树再次运行上述完整基线。53 个 release JSON 输入全部逐字节匹配固定压缩归档，输出与 Phase 11 结果字节级相同（SHA-256 仍为 `270897b9d3d8e27f6851b965f929a6a781f68111c4ec64cfaf4d11807b44773d`）。这补强了计算复现证据，但不改变同源、any-sense proxy 的语义限制。见Phase 139 深度报告与[机器审计](../sources/oewn_genus_baseline_replay_audit_2026-10-08_phase139.json)。
