# Instance-to-class pair 研究统计分析计划（草案）

状态：**未签署、未注册、未冻结**。这是基于现有 text-free Phase 78 frame 的可审阅方案；不能称为 preregistration 或确认性分析。当前授权 lock 仍为 `protocol_signed=false`、`distribution_authorized=false`。本文不授权抽取或分发 gloss。

## 1. 估计目标

### Primary estimand：closure-positive gloss-support prevalence

目标总体限定为 pinned OEWN 2025 Plus 中下列三类**有向、唯一 instance/class synset pairs**的并集：direct `instance_hypernym`、最短 class-lift depth 1、最短 class-lift depth ≥2。总体量 `N_h` 分别是 8,599、9,112、50,574，合计 68,285。此目标不外推到所有 WordNet gloss、未连通 pair、其他 WordNet release 或一般世界知识。

对 stratum `h`，令 `Y_i=1` 当且仅当裁决后的 `gloss_support` 标签为 `supported`；`not_supported`、`uncertain` 都是“没有得到 adjudicated-supported 标签”，计为 `0`，但必须另报完整四分类比例，不能称它们为语义错误。若 item 是 `unassessed` 或无裁决记录，则是缺失，不得默认为 0。主估计量建议为有限总体 pair-weighted prevalence：

```text
p_h = (1/N_h) * sum_i(Y_i)
theta_support = sum_h (N_h / N_positive) * p_h
```

这估计的是“OEWN closure-positive pair 中，源 gloss 被裁决为足以支持 claim 的比例”，不是 WordNet 关系真值、人工判断无误率或系统准确率。

### Secondary estimands

- 分别报告 direct、lift-1、lift-2+ 的 `p_h` 和完整 support 标签分布。
- 按预先声明顺序报告相邻深度差 `p_direct - p_lift1`、`p_lift1 - p_lift2+`。目前 n=64 的差值区间很宽；这些对比先作为探索性，不以未显著结果宣称无差异。
- sense-relation judgment 的 `yes/no/uncertain/cannot_determine` 分布单独报告。它是双人/裁决 human reference judgment，不是外部核验的 gold，也不能与 gloss-support 比例合并。
- reverse-direct 与 same-POS nonclosure challenge 各自报告，绝不并进 closure-positive 主估计或合成一个 pooled accuracy。

## 2. 抽样与估计

前三个正 strata 在各自 pair 总体内 SRSWOR，每层抽 64 个。正类汇总使用 `W_h=N_h/ΣN_h`，不得使用未加权 `n=192` 的简单比例。对于完全回收且完成裁决的样本：

```text
p_hat_h = sum_sample(Y_i) / n_h
p_hat = sum_h(W_h * p_hat_h)
V_hat(p_hat) = sum_h(W_h^2 * (1 - n_h/N_h) * s_h^2/n_h)
```

其中 `s_h²` 是层内二元结果样本方差。当前推荐的有限总体区间为每层反演等尾超几何检验：在 family confidence `1-α` 下，H 个分层各用 `1-α/H` 的离散精确区间；通过 Bonferroni 获得所有 stratum 同时覆盖，再将 integer success-count bounds 除以 `N_h`，按 `W_h` 加权端点形成 primary interval。任意两层差值端点由 simultaneous stratum bounds 相减。该方案不依赖正态近似，但区间会偏宽；实现与覆盖率测试见 Phase 83。缺失的 sampled outcomes 用 `k` 到 `k+m`（m 为缺失数）形成 worst-case lower/upper bounds。same-POS 两阶段 challenge 不属于此 SRSWOR interval routine。正式签署前仍需审定该方法及 alpha family，保留权重、有限总体和成对单元结构。

same-POS nonclosure 不是 pair-level SRS：它先从 7,736 个 eligible source synsets 等概率抽 64 个，再从每个 source 的 eligible target 中抽 1 个。若保留当前抽样，建议目标定义为 source-macro（每个 source 等权、source 内 eligible target 等权），并单独报告；它不估计 uniform-over-all-eligible-pairs 的 pair-micro 比例。若研究问题需要 pair-micro，必须重新定义 inclusion probability、总体大小和估计量。

## 3. 未决、缺失和裁决

- `uncertain` 是已观测的类别，不是缺失；primary `supported` prevalence 的 `Y=0` 同时涵盖 `not_supported` 与 `uncertain`，但必须分开报告。这样估计的是标签 prevalence，不表示两类语义上等价。
- `unassessed`、无法回收、来源/哈希错误和工作流损坏是不同缺失原因；逐层报告计数与原因，不静默删除。
- 正式主估计要求预定 sample 全部完成双标和裁决。若仍有缺失，报告 design-weighted worst-case bounds：全部缺失均为非 `supported` 的下界，以及全部缺失均为 `supported` 的上界；complete-case 仅作敏感性结果，除非另行预注册有依据的 nonresponse adjustment。
- 先分别计算两位标注者的结果和一致性，再计算裁决标签的 prevalence。裁决不会抹去独立标注，也不能把裁决共识称为无误 gold。

## 4. 标注者一致性与 spans

Sense relation 与 gloss support 分开形成 4 类混淆矩阵、原始一致率和适用的名义型一致性指标（建议报告 Cohen's κ，并同时报告边际分布；κ 未定义时如实标为 undefined）。不只给一个总体一致率。按 strata 展示标签覆盖和一致性；小样本层内指标为描述性。

Span 评价按两份 gloss 的独立坐标空间拆分；在冻结前固定一对多 span matching 规则。至少报告精确边界匹配的 P/R/F1；字符重叠容差只能作为次要指标。span 匹配不代表语义支持。Rationale 保留供裁决和错误分析，不做未经定义的字符串相似度评分。

## 5. 区间、多重比较与精度门槛

Phase 81 以 `p=0.5` 计算的点态 95% 正态近似最坏半宽为：单个 n=64 stratum ±12.2pp；closure-positive 加权总量 ±9.3pp；相邻层差值 ±17.3pp。若单层目标半宽为 ±10pp，正常近似下约需 95–96 pairs/层；若两层差值目标半宽 ±10pp，近似约需 189–190 pairs/层（尚未校正多重比较）。这些是精度规划值，不是 power、最小有意义效果或最终 n 建议。

若做三组所有 pairwise contrasts，应先定义 comparison family，报告调整后区间或 p 值；探索阶段优先报告效果估计和区间，不以未校正 p 值筛选结论。若只确认性检验预先列出的相邻两项，则需在协议中明确 multiplicity policy。当前推荐有限总体区间用离散 exact hypergeometric inversion + Bonferroni；Phase 83 对小 N 做了穷举覆盖率测试。仍需负责人确认它作为冻结方法；Phase 81 正态 planning margin 不能当作覆盖率证明。

样本量/工作量情景须一起登记。当前 320 pairs × 2 annotators = 640 份独立标注记录；若保留两个 challenge 层 n=64、把三个正层提高至 n=96，则共 416 pairs / 832 份记录。这只对应“各层最坏区间约 ±10pp”的规划情景，不保证差异检验功效，也不代表最优分配。

## 6. 机器/NLI 比较边界

本 pair frame 的统计估计首先服务于人工 reference study。未来比较 NLI、逻辑校验、上下位 verifier 或完整 pipeline，须先固定同一 pair list、模型/提示/版本、预算、blind split 和 abstention policy；训练/调参不能看测试标签。报告 resource status agreement、sense relation、strict gloss support、NLI、certificate replay、coverage 与成本等分轴指标。人工裁决是 noisy reference，不能据此把机器相对裁决的分数说成绝对语义真值准确率。冻结图结构通过、证明回放成功与 gloss entailment 是不同结果。

## 7. 冻结前检查项

确认 primary estimand、目标精度/最小有意义差异、标签映射、same-POS target estimand、缺失界限、区间方法、对比族、多重比较策略、双标 workload、annotator qualifications、许可/attribution、来源版本和 task-frame hashes。随后以 frame 外 synthetic/authorized pilot 验证指南可理解性与时长，再由研究负责人按适用流程签署/登记并明确授权。当前均未完成。
