# Phase 9：释义起始名词词面基线

状态：已在 2026-10-03 对 200 条 OEWN 2025 Plus blind pilot 样本完成可复算运行。该阶段是一个很弱的词面候选 baseline 和数据连通性诊断，不是释义解析器、语义 gold 评测或逻辑化结果。

## 研究问题与方法

问题限定为：不调用模型或外部 POS tagger，仅从名词 gloss 起始片段能否提出一个词面 genus 候选，并在多大比例上与同一 OEWN release 中目标 synset 的直接 hypernym 关系对齐？

`src/analysis/gloss_genus_baseline.py` 执行以下确定性步骤：

1. 核验 blind batch、答案键及 OEWN 2025 Plus 发布压缩包 SHA-256 与 manifest 一致。
2. 从 `entries-*.json` 建立发布版名词 lemma→synset 索引；从 `noun.*.json` 读取样本目标 synset 的直接 hypernym IDs。
3. 只处理名词 gloss：跳过开头的限定词；若以 `someone/something` 等不定代词开头则 abstain；否则在前 12 个 token 中找最早的、最长的 1–4 token 精确名词 lemma 匹配，并排除目标 lemma 本身。保留候选在原始 gloss 中的字符 span 和所有候选 synset IDs。
4. 将候选与目标 synset 的 OEWN 直接 hypernym 列表比较；只要候选 lemma 的任一名词 sense ID 出现在列表中，就计为资源关系命中。

该策略没有词干化、词性上下文判断、WSD、AND/OR 解析或规则生成。候选多义项未消歧，因此“任一 sense 命中”是宽松比较，不能解读成义项级 precision。

## 结果

| Panel | 样本数 | 可评估名词目标* | 找到候选 | 候选覆盖率 | 任一候选 sense 命中直接 hypernym | 命中/候选 |
|---|---:|---:|---:|---:|---:|---:|
| random_stratified | 160 | 99 | 96 | 96.97% (96/99) | 40 | 41.67% (40/96) |
| diagnostic_not_for_population_estimates | 40 | 30 | 29 | 96.67% (29/30) | 12 | 41.38% (12/29) |
| 总计 | 200 | 129 | 125 | 96.90% (125/129) | 52 | 41.60% (52/125) |

另有 71 条非名词样本被此 baseline 明确标为 `unsupported_pos`，4 条可评估名词目标没有找到候选。候选 lemma 平均关联 3.05 个 OEWN 名词 sense，最多 16 个，说明表面词项匹配距离可用于关系验证所需的 sense resolution 仍有明显缺口。

*“可评估名词目标”指名词目标且 2025 Plus 发布版记录至少有一个直接 hypernym；本 pilot 的 129 个名词目标均有直接 hypernym。random panel 是按多个属性分层抽样而非简单随机抽样，以上是样本描述，不应未经加权或独立抽样设计解释成全 OEWN 总体估计。40 条诊断样本按设计也不得用于总体估计。

## 解释边界与研究含义

- 命中只表示“释义前段抽到的词汇 lemma 至少有一个义项在 OEWN 中被列为该 target 的直接 hypernym”。这是同一资源内部的结构一致性/词面 baseline；不是人类 gold、自然语言蕴含、规则来源支持或独立有效性证据。
- 同一 OEWN 发布版同时提供词汇索引与评估关系，结果可能受资源建构决策影响；未来应增加双人 sense/definition gold、独立词典或盲审 hypernym 标签。
- 高候选覆盖、低关系命中表明“找一个早期名词”容易，但“选对定义头/义项”难。不能因此推论复杂 parser 必定有效；后续需与 POS/chunk/依存模型及 LLM 解析候选作同一标注集对比。
- 此工具不将候选自动写入 Horn graph，不发出蕴含规则，也不声称比纯神经方法更可靠。后续可把 candidate + span 作为人工 review 或 NLI 过滤的输入，不可未经审核并入正式知识库。

## 复算

需要项目内 OEWN 2025 Plus 解压目录、压缩包和 phase7 batch/key/manifest（后两者已被 `.gitignore` 排除，仅限数据管理员本地使用）：

```powershell
python -m src.analysis.gloss_genus_baseline --output outputs/phase9/gloss_genus_baseline_2025_plus_200.json
```

现有结果只保存任务 ID、候选 lemma/span/synset IDs 和聚合状态，不复制 gloss 原文。核对过的 release archive SHA-256 为 `8832b8fa26a14c0ba8c99bb1ef8db6f9e122a6d9193b65ca9e0ef572580fee7e`。机器可读结果在 [phase9 JSON](../outputs/phase9/gloss_genus_baseline_2025_plus_200.json)。
