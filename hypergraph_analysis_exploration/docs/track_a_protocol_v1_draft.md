# Track A v1：WordNet gloss relation-support 与条件化 NLI 评测（设计草案）

**状态：研究设计工作稿，未获研究负责人确认、未预注册、未冻结；没有创建候选或标注任务。** 本稿把已有 Phase153/188/202/205 证据转成可执行设计，不改 v3 输入锁，也不代表许可或分发授权。

## 1. 研究问题与结果边界

### 主问题：词典 gloss 是否支持资源关系

在预先声明的 OEWN 2025 Plus release 与本项目 hypergraph target-sense 交集中，直接 noun-hypernym edge 的关系方向是否由对应 child sense 的 raw gloss 中可定位 span 支持？主单位是 `relation_edge=(child_sense,parent_synset,hypernym)`；同一 edge 的不同 parent/child lemma surface 不重复计入这个主终点。

主估计量是目标总体直接 noun-hypernym edge 中 `supported` 的设计加权比例；同时报告 `not_supported / uncertain / unassessed`、edge-free target senses 比例与未完成比例。`not_supported` 只表示此 gloss 未授权该关系，不表示关系为假。由于候选以 OEWN 已有直接边筛选，本研究估计的是**资源边的 gloss 支持率**，不是自动抽取器精确率/召回率；召回率/精确率必须另含未被 OEWN 边预筛的提议规则与真负例框。

### 次问题：exact-pair NLI 对 premise 条件是否敏感

对同一 surface pair、同一 hypothesis、同一模型/prompt 比较两个配对 premise 条件：

- `lemma_pos_gloss_v1`：pinned-release target lemma set + POS family + verbatim raw gloss；
- `raw_gloss_v1`：同一条 verbatim raw gloss，不呈现 lemma 与 POS。

主要 NLI 结果是每个条件下模型预测与该 exact premise × hypothesis 的人类三分类 gold（`entailment / neutral / contradiction`）一致率，以及两条件配对准确率差。该对比测试的是“lemma+POS+gloss 这一**组合呈现**”与 gloss-only 的差异，不单独识别 lemma 与 POS 的贡献，不自动构成模型内部语义理解或因果机制证据。两个条件的 NLI labels 必须各自独立裁决。

### 互相独立的标签

`gloss_support` 是 edge-level 的方向性 source-span 判断；`nli_relation_gold` 是 condition-specific exact premise/hypothesis 的蕴含关系；`resource_relation` 记录 release 中是否存在该边；`formal_replay` 记录固定规则/签名/类型下能否验证形式证书。不得把其中任何一项复制或代替另一项。

## 2. 总体、抽样与 frame

1. **总体候选定义**：冻结 hypergraph 内符合预先声明 target-sense 限定且可与 pinned OEWN 2025 Plus 唯一对齐的 noun senses；从同一 release 导出 POS、完整 lemma set、raw gloss 和全部直接 noun-hypernym edges。记录无法对齐、多重对齐、没有直接边和 POS/lemma 差异，不能静默修补。
2. **抽样单位**：child target sense 是 primary sampling unit（PSU）；在抽中的 sense 内纳入所有符合条件的直接 noun-hypernym edges。strata 先按 pinned-release 字段重建；可沿用目前建议的 POS × raw-gloss-length × punctuation 分层，但 noun-only 后空 strata 合并规则、层配额、抽样 seed 与 inclusion probability 都须重新冻结。
3. **新 frame**：先重新定义并生成 release-derived frame，再分层抽样。锁定 v3 frame 的 400 个项目仍可用于交集、工作量和偏差对账，但不直接作为 Track A frame：现有证据显示它有 1 个 POS 与 1 个 lemma-set mismatch，且源自不同目的的释义可靠性研究。不得覆盖 v3 frame、batch、manifest 或 lock。
4. **规模**：旧 inventory 的 264 noun edges / 507 parent-surface rows / 841 child×parent surface combinations 是 400-sense frame 上的方案估算，不是新 frame 的保证计数、样本量依据或统计功效证明。新 frame 冻结后必须重算总体、strata、候选 edges 和工作量。
5. **主权重**：若目标问题是“总体候选 edge 的 gloss 支持率”，edge-level Hájek/比率估计按 child-sense inclusion probability 加权：每条 edge 使用其 child PSU 的设计权重；置信区间保留 strata 与 PSU 聚类。另报 target-sense 等权的二级估计（先在 sense 内汇总其直接 edges，再按 sense 设计权重汇总）。edge-free senses 不记作不支持 edge，单独报告覆盖率；不能把 edge 加权估计冒充“平均词条”的 sense-level estimand。

## 3. surface 设计与任务量

- **Parent surfaces**：推荐每个 parent synset 的全部 pinned-release lemma surfaces 均独立形成 hypothesis，不使用未经论证的“canonical lemma”。
- **Child surfaces**：推荐将该 child sense 的全部 pinned-release lemma surfaces 与 parent surfaces 交叉，避免任意选一个 child lemma；各surface 继承同一个 relation-edge ID，但作为不同 NLI exact-pair 行。若研究负责人优先控制成本，可选择每个 child sense 一个由冻结确定性规则选出的 surface；需承认该规则会限制模型结论的 surface 覆盖，且须在看标签/预测前锁定。
- **方向模板**：noun-only 首轮。建议模板候选 `A/An {child} is a kind of {parent}.`，但冠词、复数、mass noun、多词 lemma、标点/大小写需先制定确定性 renderer，并经 frame 外独立可理解性/自然度预试；任何不适用项记入模板覆盖分母，不临时改写。58 条 verb edges 保留为后续独立模板研究，不混入第一轮。
- **conditional workload**：旧框架下 noun-only 若每 edge 选一个 child surface，507 个 surface pairs × 2 个 premise conditions = 1,014 pair-condition rows；双标为 2,028 个 NLI judgments。若纳入全部 child×parent surfaces，841 pairs × 2 = 1,682 rows；双标为 3,364 个 judgments。source-support 仍按 264 个 relation edges 双标，为 528 个初始 judgments。以上只算 workload，不代表 power、precision 充分、可承受或新 frame 实际计数。

## 4. 标注员、盲化与随机分配

### source-support panel

每个 relation edge 由两名独立标注员在 raw gloss 上标 `supported / not_supported / uncertain`，保存 Unicode code-point `[start,end)` span、方向、推理依据和理由；尚未评估为工作流状态 `unassessed`，不得混入前三类。分歧由预先指定且不看模型预测的裁决者处理；保留两份原始判断和 adjudication 记录。此面板不看 NLI 输出或 OEWN “答案边”状态。

### NLI panel

每个 exact pair-condition 由两名独立标注员判断 `entailment / neutral / contradiction`；裁决者在所有独立判断锁定后处理分歧。建议使用 **4 人平衡不完全区组**：对每个同一 surface pair，任一标注员只看两种 premise 条件中的一种；在 leakage component / POS / presentation batch 内随机且平衡地交换两组标注员所见条件。这样避免只靠把两条条件隔开几行来假装没有记忆效应，同时避免固定“某两人只标条件 A”导致 annotator 与 condition 混淆。每人须跨不同样本看到两种条件，但不同时看到同一 exact pair 的两个版本；每个标注员的实际任务量要事先核算。

source-support 与 NLI 最好由不同面板执行，以免同一批人先见支持标签再判 NLI；如人力只能支持共享面板，须分阶段、隐藏此前答案并把潜在 criterion leakage 列为限制，不能称为独立验证。

按 leakage components 分组防止相同 lemma/sense/edge/rewrite 跨 split；在标注面板内部按 component 分配两条件与 rater-pair mapping。每位标注员内任务顺序用种子化随机化，并对 POS/批次/条件量做平衡；冻结 seed、分配算法、呈现文件 hash 和实际展示日志。现有 v3 双 slot preview 只覆盖另一项 400-row study，不能直接当作 Track A 四人分配器。

## 5. 分析与验证

### gold 质量

在裁决前报告 source-support 与 NLI 各自的双标列联表、原始一致率及预注册的类别不平衡敏感的一致性量；按标签分别报告 support span overlap/F1、方向和关系 exact match。报告裁决率、uncertain/unassessed、模板不适用、拒答/缺项和每个分层分母。裁决集是操作性 gold，不是无误语义真值。

### 模型结果

- 主 source-support 率：按抽样设计和 PSU×stratum 做有限总体/分层 cluster 区间；分析代码与小样本/稀疏层校准在揭盲前检查。不得按单条 surface bootstrap。
- NLI 条件差：在同一 frozen surface pair 上计算模型在对应 exact-condition NLI gold 上的正确性差；先在 relation edge 内汇总 surfaces，再在 child sense 内汇总 edges，最后按 target-sense 抽样设计权重汇总。**建议的主要 NLI 条件差 estimand 为至少有一个可呈现候选 pair 的 target senses 中的 target-sense-equal 平均差**，避免 parent-edge 数较多的义项仅因 edge 多而占更大权重；同时报告 edge-population-weighted 差异作为敏感性分析。edge-free senses、模板不适用和缺失标签不进入准确率分母，须分别报告设计加权覆盖率/缺失率。source-support 的主估计仍是 edge-population 加权率，两者不可混为同一 estimand。以 target sense/预先冻结 leakage components 作 cluster 推断，报告缺失/不确定的分母。
- 若希望调 threshold 或 selective risk：dev calibration 的独立单位必须与 split/leakage/统计结构兼容。当前 strict selector 要求 IID `group_id` 一行，不能直接用重复 surfaces；在 cluster-valid 校准方法未实现并验证前，NLI 主结果限 threshold-free 描述性准确率/混淆矩阵，不声称风险控制保证。
- 模型、revision/API date、prompt、解码参数、输入 renderer、预算和输出解析器均固定；同一 exact pair 的两 condition 采用同模型版本与相同调用预算，并按配置记录输出稳定性。严格证明 route 另报告 source/hash/type/replay，不与 NLI accuracy 合并。

### 内容 plausibility 与图结构效应

Phase217 及既有 NLI 内容效应草案提示 plausibility 与 logical validity 可混淆，图表示也可能放大表面 cue。本 v1 不把 post-hoc plausibility strata 当作 primary covariate 或因果操纵；若保留，须另设盲化 plausibility 标注、匹配样例标准和独立的未触碰诊断集。不得看结果后挑选“常识合理”的词条来解释 condition gap。

## 6. 样本量、精度和先导试标

当前 400-sense/24-strata 的旧框架及 264 noun-edge 估算不能证明足够的 power 或区间精度。目标设计确认后，先规定主估计量的最小实质差异或最大可接受区间半宽；再用符合实际分层、每 sense 多 edge、surface 嵌套与预期标签分布的模拟做设计精度/功效敏感性分析。没有可靠 pilot 比例时覆盖合理范围（含最保守 Bernoulli variance）并报告假设，不从 AMR、FRANQ 或其它任务借样本量。

在新 frame 外准备独立的可理解性/耗时先导材料；先导标注不并入主样本、不用于调模型。任何手册/模板/协议调整须在主 frame 解盲和预测比较前冻结。题目由高阶主题集群分派，以免同一标注者在相邻题中看到近重复 edge。

## 7. 与现有软件的兼容边界

Phase202/205 静态审计已确认现有候选 freezer、claim-review manifest、single-sense importer 与 proof route 不能表达 Track A 全合同：缺 relation-edge/parent-surface/condition foreign keys，且 rendered premise hash 与 raw source-gloss hash 被错误地要求相等。获批后应**新增版本化**合同，分别绑定 `source_gloss_sha256`、`rendered_premise_sha256`、`hypothesis_sha256`、renderer/condition version、`relation_edge_id`、child/parent synset 和 exact lemma surfaces；另保存 split-leakage component 与 statistical/PSU unit。旧接口保持可回放，不靠扩展现有字段名假装语义相同。

只有主设计、label manual、权利与责任人 gate 冻结后，才能实施候选 freezer / schema validator / randomized panel assignment / NLI exporter / proof-route binding。实现须以 synthetic fixtures 验证 hash 分离、condition-specific labels、重复 edge/surface、未知/拒答与泄漏连通分量；通过这些只证明接口契约，不证明人工语义标签正确或方法有效。

## 8. 研究负责人需裁决的项目

| 决策 | 本稿建议 | 影响 |
|---|---|---|
| Track A 目标总体与新 frame | frozen graph target-sense × exact pinned release 的合格交集，按 release metadata 重新建框/抽样 | 决定外推范围、strata、权重和候选总数 |
| 主 estimand | noun direct-edge 的设计加权 gloss-span support 率 | 若改为 sense-equal，论文问题和分母都改变 |
| child lemma policy | 全部 child × parent surfaces；成本优先时一个冻结 surface/child | 决定词面覆盖、候选数与结论范围 |
| NLI premise 条件 | 上述两个 condition 成对；NLI gold 对 exact condition 独立判断 | 只识别 lemma+POS+gloss 的组合呈现差异 |
| 标注参考结构 | 全部 acceptable analyses 作为独立 alternatives，避免并 union；边界不清者保留 unresolved | 决定 source claim score 分母；也可选单一裁决 reference，但不能声称合法分析 recall |
| 标注人力 | source-support 两人独立 + NLI 四人平衡面板 + 独立裁决者 | 不足时须明确降格/改变误差结构，不可隐藏同 pair carryover |
| 校准 | 未验证 cluster-aware procedure 前，NLI 只作无阈值描述性 secondary result | 避免 IID 假设与重复 surface 冲突 |
| 精度/功效目标 | 先指定主要 rate/difference 的最小关心效应或区间半宽，再仿真 | 不可把候选计数直接称为样本量充分 |

以上都是可供确认/修改的建议，不是已作出的研究者决定。任何重要选择变动后，需先更新本设计并重核 workload 与统计单位，之后才进入新 frame freeze。

## 9. 阶段内不执行的事项

当前不运行 candidate freezer、不渲染正式 hypothesis、不生成 pair/label/split、不更新 schema/lock、不调用模型、不外发标注任务、不更改 release clearance。研究设计可讨论、修订、签署和登记后，再按该版本实施。
