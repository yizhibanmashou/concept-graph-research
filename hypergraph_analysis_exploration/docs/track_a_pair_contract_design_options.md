# Track A pair contract：设计选项与建议

状态：**设计草案，未冻结、未注册、未用于候选 pair 或标注。** 本文件基于 Phase144–146 的 OEWN 输入身份、候选词面与现有代码契约审计；它不是新 schema 的已实现支持声明。

## 建议审议的默认设计

### Target 前提与对照

对于每个候选 target sense 预留两个配对输入条件：

1. `lemma_pos_gloss_v1`：完整 pinned-release lemma set + POS family + verbatim raw gloss。对 `s` 保留原始 OEWN POS，同时在模型可见标签中映射到 adjective。
2. `raw_gloss_v1`：只显示同一段 verbatim raw gloss，作为 target-context ablation。

渲染器应是确定性、版本化的纯函数，并固定 lemma 排序、下划线处理、空白/Unicode 规则、POS 映射和标签分隔格式。source evidence span 始终锚定 raw gloss 的 Unicode code-point 坐标；模型 premise 的 UTF-8 hash 单独记录。人类 NLI reviewer 与模型在一个 condition 内须看到完全相同的 premise/hypothesis。

### Parent hypothesis 表面

默认建议保留 pinned release 中每个 parent synset 的**全部 lemma surface**，每个 surface 单独成为一个精确 hypothesis 候选，并以 `relation_edge_id=(child synset, parent synset, hypernym)` 关联。不要把 lemma 列表合并为一句 hypothesis，也不要将词典序首项称作语义 canonical。对每个 surface 独立裁决，因为不同表层可能有歧义差异。

Phase145 的本地资源盘点给出 322 条 edge、680 个 surface 候选。若两个 context condition 都生成，设计规模最多为 1,360 个 pair-condition 行；若双人独立标注 NLI relation，则最多有 2,720 个初始判断返回。它们仍只是计划规模，不是实际生成量，也不代表 sample size 足够。

Noun hypothesis 可先审查模板 `A/An {child} is a kind of {parent}.`；verb hypothesis 可先审查模板 `To {child} is a more specific way to {parent}.`。两个模板尚未验证自然度、词形、补语结构或适用性；其中 58 条 verb edge 不能在未审阅模板前生成正式候选。模板还需处理复数、mass noun、multiword lemma、particle、词首冠词及语义范围。模板版本与 exact hypothesis 字节必须固定并 hash。

### 标签与 estimand

- `semantic_support` 的目标是：方向性规则是否由 raw gloss 文本直接支持；证据 spans 只指向 raw gloss。OEWN parent edge 不作这个标签的 gold。
- `nli_relation_gold` 是 entailment/neutral/contradiction，对应某一具体 context condition 下的 exact premise × hypothesis。两种 premise 条件不得自动复用同一个三分类标签。
- `resource_relation` 单独记录 pinned OEWN 中的 edge/path，仅作为候选 provenance / resource-relative outcome。
- surface 级结果和 edge 级结果分别报告。若主 estimand 以 edge 为单位，必须在预注册中规定同一 edge 多个 surface 的汇总函数及 edge/target 的权重；不直接用逐行 micro 指标代表 edge-level 结果。

### 新版数据契约与校准单位

审议新增而非原地变更：`claim-review-record/0.2-draft`、`claim-review-candidate-manifest/0.3-draft`、`claim-review-nli-export/0.3-draft`。候选/manifest 要分别绑定 `source_gloss_sha256`、`rendered_premise_sha256`、`hypothesis_sha256`、target lemma-set fingerprint、renderer/condition version、parent synset/relation、`relation_edge_id` 和 surface identity；text-free manifest 不应泄漏模型输入文本。

明确区分：

- `split_leakage_group_id`：根据 target/parent lemma、sense、edge、精确 premise 与其他 preregistered 近重复约束形成的连通组，用于决定 split。
- `statistical_unit_id`：对独立抽样/误差或校准负责的单位，需在 relation edge、target sense 等选项中预注册。
- `relation_edge_id`：把同一 child-parent 关系下的多个 lemma surface 与 premise conditions 联结，以作 edge-level 汇总。

当前 certified NLI selector 要求每个 dev `group_id` 恰好一行，并有 IID 独立单位前提。不得仅把字段改名后就将同一 edge 的多个 surface 当作多个独立校准样本。实现前要决定：每个 statistical unit 预先取一行、将输出在 unit 内聚合，或实现并验证支持 cluster 的校准程序；strict route 的逐 candidate 决策还须与实际校准对象相同。

## 仍需研究者确认的选择

1. **候选表面范围**：所有 parent lemma 分别成候选（推荐；更完整但标注/校准成本高），还是每条 edge 只选一个预先规定的 surface（成本较低但 surface 覆盖受选择规则影响）。
2. **NLI 主 gold**：对每种 exact premise 单独裁决 NLI 三分类（推荐；标签条件明确，但双条件需要成对双标），还是只以 shared raw-gloss `semantic_support` 为主要监督/评价结果，NLI 三分类降为次要条件内结果。
3. **Primary estimand/calibration unit**：表层 pair、relation edge 或 target sense；此选择决定行聚合、有效独立样本数、阈值校准和论文结果解释。
4. **Verb hypothesis grammar**：是否采用建议模板、替代模板，或先仅做 noun pilot 并将 verb edge 留作独立研究切片。

在这些选择完成前，不运行 candidate freezer，不写新 schema validator，不生成 pair/label/split，也不把旧 NLI gate 输出套到新输入。旧 `/0.1`、manifest `/0.2`、export `/0.2` 原样保留。

### 新增相关工作约束（Phase 149）

ACL 2026 的 [G-IdiomAlign](https://aclanthology.org/2026.acl-long.1794/) 已用 gloss/no-gloss 条件对照检验英语 gloss 作为跨语言 lexical meaning pivot 的效应。因此本方案中的 target-context primary 与 gloss-only ablation 只作为控制输入差异的实验条件，不单独主张新颖；主要贡献假设必须落在 sense-bound、direction-sensitive pair contract、raw-gloss span support、AND/OR 结构标签与可独立回放 source-only proof 的联合验证。该研究使用 embedding-based proxy 并只在人评子集校准，不能替代本项目双人裁决的 semantic-support gold。

ACL 2026 的 [ReportLogic](https://aclanthology.org/2026.acl-long.384/) 已对报告级 evidence sufficiency、warrant 和 claim-support 做专家人评。项目避免泛称“首次 human audit claim support”；其待测的较窄任务应显式把具体 gloss span 链接到具体方向性 Horn literal，并把人审语义支持、形式 proof replay 与 resource relation 分开计量。筛读边界见Phase 149 报告。

### 新增相关工作约束（Phase 150）

[Q-CARE](https://arxiv.org/abs/2608.11238) 已将 atomic answer claims 与 retrieved chunks 的逐对支持判断、人标对齐 benchmark 和二元/部分对齐设计用于 COLM 2026 RAG evaluation。因此一般 claim decomposition / claim-support / human verifiability 不能作为 Track A 的宽泛创新点。其 chunk-level support 仍不同于 raw WordNet gloss 精确 span 对某个方向 literal 的语义支持；Q-CARE 的 LLM checker 也不是 source-only proof replay。若做 adapted baseline，须等当前四项 pair-contract 决策冻结，再锁同一输入、gold、split 和预算。详见Phase 150。

### 新增相关工作约束（Phase 151）

[No Free Labels](https://arxiv.org/abs/2503.05061) 表明 LLM judge 的 correctness agreement 与 judge 自身是否答对问题及参考答案是否正确相关，错误参考可能降低一致度；因此 Track A 的 judge 必须以独立的人类裁决 gold 测量，不应依赖模型自生成 gold。 [LogicIF](https://arxiv.org/abs/2508.09125) 已展示可执行 gold 加自然语言 instruction 人工保真核查；但真实 WordNet gloss 没有该程序 oracle，semantic-support gold 仍需 sense-linked 原文 span 双标/裁决。详见Phase 151。
## Phase219 补充：面向实验实施的 v1 草案

设计建议已整理为[独立 Track A v1 草案](track_a_protocol_v1_draft.md)。它将 source-support 的总体单位定为 relation edge，将 child sense 用作 stratified sampling PSU；NLI 对同一 surface pair 做两个 exact premise 条件的配对比较，并建议四人 balanced-incomplete-block 标注面板。新 frame / child-surface / reference-set / power-precision 等选项仍待研究负责人确认，且未生成任何候选或 schema。审计细节见Phase219。
