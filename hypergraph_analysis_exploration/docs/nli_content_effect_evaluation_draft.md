# NLI 内容效应与干扰上下文评测（草案）

状态：**未签署、未注册、未用于样本或系统比较。** 已有 sidecar validator 与 descriptive evaluator 原型，但尚无标注数据、schema freeze、区间推断或路由集成。目标是将 Phase 84 的 SemEval-2026 Task 11 评测启示转成适配 WordNet gloss-support 任务的可检验方案。该 syllogism benchmark 不是本项目的匹配基线。

## 1. 研究问题与分析边界

核心问题：当 NLI 模型判断一个候选有向 claim 是否被指定 WordNet gloss 支持时，模型输出是否会随 claim 的常识合理性或额外无关文本变化，即使 adjudicated gloss-support label 不变？本分析只测语言模型/文本评分层的稳健性，不测证明证书的逻辑有效性，也不把人工标签当作无误语义真值。

保留主任务 gold 三分类 `entailment / neutral / contradiction` 和既有 dev-calibration-test 主流程。内容效应和干扰上下文分析是预先声明的**次级诊断**：不得用于重选主模型、提示、阈值或主结果；如用来选方法，须另有未触碰的锁定测试集。

## 2. 两类互不混淆的诊断集

### A. 独立合理性分层（无文本干预）

对冻结 gold 中的 hypothesis 单独作 `claim_plausibility` 判断，标注者看不到其 gloss-support 标签、NLI 输出和系统路由。建议标签为 `plausible / implausible / uncertain`，逐条给 rationale；`uncertain` 不并入二元主对比。按 gloss-support gold 与合理性形成 2×2 分层，至少分别报告：

- supported claims 中 plausible 与 implausible 两层的 NLI entailment 分数、正确率、false-negative rate；
- `not_supported` claims 中，gold `neutral` 和 `contradiction` 分别报告 plausible 与 implausible 两层的 entailment 分数、三分类混淆矩阵和 false-positive rate；每个有数据的关系×plausibility cell 报告样本数。gold `entailment` 但 support 不成立的 discordant cases 也保留为独立切片；neutral+contradiction 合并值只能作为辅助量，不能取代两个主切片。无法获得 NLI gold relation 的 unassessed 行按 split 统计，不虚构其关系归属；
- 每层样本量、sense/lemma 覆盖和三分类混淆矩阵；若未来要报选择性 coverage，必须另行冻结只在 dev 选择的阈值。

定义描述性 content-effect gaps：`CE_supported = FNR_implausible,supported − FNR_plausible,supported`；`CE_neutral = FPR_plausible,neutral − FPR_implausible,neutral`；`CE_contradiction = FPR_plausible,contradiction − FPR_implausible,contradiction`。另可计算 `CE_non_entailment`，把 gold neutral 与 contradiction 合并作为辅助量。`FPR` 是预测为 entailment 的比例；缺少任一比较 cell 时对应 gap 为 null。关系切片及合并值的正差都表示 plausible 层误报率更高。所有结果均称为相对人工标签和 plausibility judgment 的差异，不称为真值偏差。neutral 与 contradiction 的独立主切片可避免相反方向的变化在合并值中互相抵消。

这种分层是观察性分析：不同 claim 可能在长度、词汇频率、构式难度和 sense 难度上有差别，不能单独作因果解释。主解释证据应来自下述匹配对比；没有足够匹配样本时只报告描述性分层。

### B. 人工核准的合理性匹配对

`contrast_group_id` 连接一对不同词面实现、但在预定形式结构、gold support label、claim 类型和标注条件上匹配的样例；独立标注确认一条 plausible、一条 implausible。两条均须使用各自固定的 synset/gloss 与 claim，分别得到完整双标裁决；不能仅凭模板作者声明其等价。该设计估计 matched pairs 内的 NLI score/accuracy 差异，不将不同 gloss 的原文混改为同一 source。若无法可靠构造、独立标注并裁决等价 pair，则不做此分析。

主配对量为 `Δ entailment_score = score_implausible − score_plausible`，在相同 gold support 层内报告分布、中位差和按独立 `group_id` 聚类的区间；同时报告配对决策翻转率、错误差异及准确率差。不能把分数下降直接解释成内容效应，除非人工 gold 与匹配约束均通过冻结审查。

### C. 无关上下文压力（严格隔离的诊断输入）

建立独立 `diagnostic_context` 条件：在原始 gloss 和 hypothesis 外附加一段经人工审核的无关上下文。source gloss 字节、其 SHA-256、source spans、hypothesis 和 gold 均不变；context 不得被重新标记为 `source_assertion`。上下文与模型包装模板都要版本化、哈希固定。按 baseline 与 distractor 的成对 NLI entailment 分数变化、三分类 flip rate、accuracy/coverage 变化及 flip confusion 分析。

该条件回答的是“自然语言评分模型是否受非来源上下文干扰”，不表示新输入仍可通过原 source-only 证明 gate。diagnostic rows 永远不能送入 strict proof route，也不能参与主阈值校准；strict route 只接受精确绑定原 gloss/hypothesis 哈希的预测。

## 3. 数据契约草案

既有 `claim-review-nli-export` 行保存主预测。未来如批准诊断集，建议独立 sidecar（草案名 `nli-content-effect-diagnostic/0.1-draft`）至少包含：

```json
{
  "example_id": "opaque-id",
  "contrast_group_id": "opaque-pair-id",
  "split": "dev-or-test",
  "diagnostic_condition": "matched_plausibility_pair",
  "condition_value": "plausible",
  "source_sense_id": "release-bound-sense-id",
  "claim_id": "claim-id",
  "gloss_sha256": "64-hex-sha256",
  "hypothesis_sha256": "64-hex-sha256",
  "model_premise_sha256": "64-hex-sha256",
  "context_sha256": null,
  "gold_support_label": "supported",
  "nli_gold_relation": "entailment",
  "claim_plausibility": "plausible",
  "review_status": "adjudicated",
  "group_id": "lemma-or-source-disjoint-split-group"
}
```

此为 sidecar 原型接口，不包含释义或模型输入原文，不取代 canonical pair schema 或 claim-review sidecar。`nli_gold_relation` 是独立裁决的三分类 NLI 关系；`gold_support_label` 是单独的严格 gloss-support 判断。validator/evaluator 实现在 `src/logic/nli_content_effect.py`，仅支持 JSON 对象列表 API，schema 仍未冻结。测试标签在模型运行时必须隐藏。所有共享 contrast group、sense、lemma 泄漏组、改写族或上下文模板的样例须留在同一 split；多个分组约束冲突时按连通分量合并后切分。validator 会拒绝 `group_id`、source sense、claim、gloss/hypothesis/premise/context hash 在 dev/test 间重复；lemma、改写族和模板家族没有独立字段，生产 sidecar 前必须确保它们已合并进连通分量 `group_id`。字段级自动检查不能证明这个上游分组过程本身正确。

可用 `src/analysis/build_nli_diagnostic_leakage_components.py` 从只含 opaque `example_id` 与 `(namespace, key_sha256)` 列表的 JSONL 建立可复算连通分量，输出 `group_id` 到 `example_id` 的映射及 component-size aggregate。它不分配 train/dev/test，也不生成样本；split ratio、随机化/排序政策与目标单位仍需预先冻结。key 必须由上游生成且不能是原文；低熵 ID 的无盐 SHA-256 只是可猜测的 pseudonym，若需降低重识别风险，应使用外部保管的稳定 HMAC key 或随机 opaque token。builder 的输入格式和命令见[复算说明](reproducible_development.md)。

## 4. 区间、抽样与缺失

主模型阈值继续只在冻结 dev 主数据上用现有校准器选择。诊断对比区间以 `group_id` / `contrast_group_id` 为抽样单位做 cluster bootstrap 或与抽样设计一致的有限总体方法；须在查看 test 结果前选定，并同时报告未调整区间及预注册 multiplicity family 的调整结果。Phase 83 的 pair-strata hypergeometric intervals 不可直接用于合理性分层或匹配对：目标总体、抽样单位与 inclusion probabilities 不同。`uncertain`、`unassessed`、上下文审核失败、预测缺失分别计数；不得默默删除或把它们并为 negative。

样本量应以可接受差值区间宽度/最小实质差异规划，而不是挪用 Task 11 的数据量或 Phase 78 的每层 n=64。未规划和冻结前，所有结果只能是可行性 pilot 或描述性估计。

## 5. 冻结前门槛

需先确认：合理性判断定义与标注指南；哪些 claim 类型可判 plausibility；匹配对形式等价标准；无关上下文审核流程；sidecar 与模型输入边界；split grouping 与 estimand；区间/多重比较；标注许可、工作量和盲化；模型/提示/模板 hash；诊断与 strict route 的禁止互通测试。annotation lock 未签署和分发未授权时，不抽取或分发文本，不启动人工标注。

原型 evaluator `nli-content-effect-diagnostic/0.2` 的 plausibility strata、relation slices 和内容效应 gap 只使用 `diagnostic_condition == "plausibility_stratum"` 的记录；匹配合理性对与无关上下文对只进入各自的 paired diagnostics，不与观察性分层合并。split 总行数仍覆盖该 split 的全部条件。每个有数据的关系切片输出已裁决样本数、三分类混淆矩阵和 unsupported FPR；无法获得 gold relation 的 unassessed 行仅在 split 总量中计数，不分配给关系切片。neutral 和 contradiction 各自 gap 外，旧字段 `CE_not_supported_fpr_plausible_minus_implausible` 保留为合并辅助 gap 的兼容别名。缺 cell 的 gap 返回 `null`，不插补，不计算置信区间或显著性，也不选阈值。预测行必须携带唯一固定的 `model_id`/`model_revision`，sidecar 与预测 example IDs 必须一一对应。当前没有真实评测数据或结果；真实文件读取、导出 manifest/hash 核验和模板上下文生成尚未实现。

## 6. 证据来源与限制

此设计由 SemEval-2026 Task 11 对形式有效性、内容合理性、无关 premises 和 content-effect metrics 的分离评测启发；项目化后仍须独立定义 gold 与估计目标。见[官方论文](https://aclanthology.org/2026.semeval-1.450/)、[官方 PDF](https://aclanthology.org/2026.semeval-1.450.pdf)及[Phase 84 全文筛读记录](../sources/literature_screening_log_2026-10-07_semeval2026_task11_overview.json)。本草案本身不构成创新性、模型稳健性、NLI 效度或研究效果证据。

### Phase269：validity/plausibility 表征先例补充

ACL Findings 2026 的 Bertolazzi et al. 全文在 ten taxonomic term triples 上同时构造 syllogism validity、actual-world plausibility 与 hypernym/hyponym control，并报告二者在模型 activation 方向中的混淆及 steering 诊断。Phase269全文审读给出其样本和结果边界。该实验支持把 plausibility/content-effect 作为独立次级诊断的动机，但不能替代本项目的 gloss-support gold，也不证明本项目模型已有此偏差；其十组词汇 triples 与按逻辑形式切分不构成词汇留出验证。

## Phase 146：contextual premise compatibility

The current evaluator intentionally requires the source-condition `model_premise_sha256` to equal `gloss_sha256`. Therefore it only represents gloss-only input under its current schema. A future lemma/POS-rendered input is a separate versioned context condition with its own premise hash and renderer identity; source gloss and evidence-span coordinates remain separately bound. Calibration and paired-context analyses need explicit leakage versus statistical grouping keys and a declared edge/surface estimand. This is a contract implication, not a measured context effect; see [Phase 146 audit](../sources/track_a_context_contract_audit_2026-10-08_phase146.json).
