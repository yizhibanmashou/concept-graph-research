# T02 正式盲审：抽样框、精度与来源限制

**状态：** 设计备忘录；未生成正式样本，未读取/使用任何人工标签。
**日期：** 2026-10-31
**目的：** 在用户已确定的目标等权估计下，明确全图抽样框、稀有结构 strata、来源字段边界和样本量敏感性，为之后冻结正式样本提供依据。

## 1. 本轮结构抽样框审计

新增 `src/analysis/preposition_sampling_frame_audit.py`，只读冻结图节点 POS、`source_root` 和超边规则；不读 gloss、标签或人工结果。复现：

- 110,425 个 target、154,206 条原始分支；`pos=prep` 主口径影响 89,058 个 target（80.65%）。
- 按 target 的排他结构影响 strata：508 个出现新空分支、501 个出现非空分支碰撞、4 个同时出现两者、88,045 个有 prep occurrence 被删但没有新空分支/碰撞、21,367 个未受影响。五层合计 110,425。新空/碰撞重叠仅 4 个 target，二者不能简单相加。
- 新增分层工作量核查：五层原始分支数分别为新空 1,102、碰撞 1,599、两者兼有 19、其他受影响 123,823、未受影响 27,663；每目标均值依次为 2.169、3.192、4.750、1.406、1.295 branches。高风险三层共 1,013 个目标，占 0.918%，但平均每目标约 2.685 分支；按 4 条件×2 名审阅者估算，每目标每分支对应 8 个 branch-condition-review 单元。该计数比统一套全图 1.397 分支/目标更能估计分层抽样的负担，但不含释义长度、回查、分歧与仲裁工时。
- `nodes.tsv` 中只有 7 种 `source_root` 标签；各组 target 数（从小到大）为 30、537、792、1,259、1,752、21,662、84,393。最大两组占全图约 96.0%。节点文档已明确 `source_root` 表示构造 lineage/处理来源标签，不等同于已核实的独立上游词典或来源家族。
- 因此，不能把 7 个 `source_root` 值当作 7 个独立 dictionary clusters 做 cluster bootstrap，也不能据此宣称跨来源家族泛化。当前可支持的是对该冻结图有限总体的 target-level 设计推断。要做来源家族层级结论，必须先从许可审核过的原始 provenance 独立建立 upstream source-family crosswalk，并审计映射歧义；未建立前相关估计不启动。

复现命令（从 `hypergraph_analysis_exploration/` 运行；输出必须是新本机文件）：

```powershell
python -m src.analysis.preposition_sampling_frame_audit `
  --bundle ../OEWN `
  --out outputs/t02_sampling_frame_audit_new.json
```

输出含输入 SHA-256 和聚合 strata，不含定义文本、人工标签或目标级抽样名单。该摘要只对应 prep 主口径；`prep_phrase` 敏感性分析仍单独执行。

本轮冻结输入摘要：`nodes.tsv` `9bde0367d0ba1f62f7f4810b05693a82f1dcb32767c2fe7f0e88055991e23bd1`；`hypergraph_rules.jsonl` `c07dd37342ab399244a091501a21ada9e2f9f706efb1dc34d6b8ebc16a8a0a53`。

## 2. 可估计对象与抽样

抽样单位是 target；同一 target 的全部可审查 OR 分支及四个结构条件作为配对重复测量。先在每个 target 内计算各条件的分支标签比例，再对 target 等权估计。严格次要结果是 target 的所有分支均 faithful 的比例。分支不能作为独立样本计数。

推荐从冻结全体 target 建立分层无放回样本。分层变量至少包括：

1. `prep` 变换影响层（新空、新碰撞、同时发生、其他受影响、未受影响）；
2. target 的 POS 粗类；
3. 已验证的来源家族（若后续 provenance crosswalk 通过），否则仅记录 `source_root` 作为固定图的构造 lineage 协变量，不称其为来源家族。

新空、碰撞两类合计只涉及约 0.92% target；若按比例简单随机抽样，稀有结构错误类型可能几乎不进入审阅。可在这些 strata 过采样，以提升局部保真诊断能力；所有 target 的入样概率和有限总体权重必须保存，population estimate 使用预定加权估计。全体平均和受影响/高风险层条件估计分开报告，不以过采样原始比例代替总体比例。正式样本排除既有 40 个流程试标 target IDs；试标只用于手册和流程、审阅耗时，不估计保真率或决定样本量方差。

对 `prep_phrase` 敏感性分析必须另报结构框和对应标签估计，不把其 target 与 prep 主口径的结果混成一层。四条件的标注顺序需对审阅者随机化；同一 target 的四版不得紧邻，以降低记忆/对照偏差。标签原始记录、仲裁及映射名单本机受控保存，不进入 Git。

## 3. 样本量敏感性（不是最终样本量）

为避免拿 40 条流程试标估计未知标签率，这里用仅依赖取值范围的 Hoeffding 上界作保守参照。它不使用 pilot 标签，不是基于预期效应的传统功效分析；最终分层加权设计需按 strata 总量与配置重算，并计入标注不可判定/失访和 reviewers 时间。

对每个 target 的保真比例 `y_i ∈ [0,1]`，简单随机抽样估计单个总体均值，双侧 95% 最坏情形半宽 ε 所需 n 满足 `n ≥ ln(2/0.05)/(2 ε²)`。对同一 target 的两条件差 `d_i ∈ [-1,1]`，范围为 2，单个配对差值估计满足 `n ≥ 2 ln(2/0.05)/ε²`。若三种变换相对 source 均作为 co-primary，并用 Bonferroni 同时控制 95%，配对差值采用 `n ≥ 2 ln(2·3/0.05)/ε²`。有限总体 110,425 下本表 FPC 影响很小；来源分层/过采样的设计效应未计入。

| 目标精度半宽 | 单个条件总体均值（target） | 单个配对差 | 3 个配对差同时 95% |
| --- | ---: | ---: | ---: |
| ±10 个百分点 | 185 | 738 | 958 |
| ±7.5 个百分点 | 328 | 1,312 | 1,703 |
| ±5 个百分点 | 738 | 2,952 | 3,830 |

以上配对差界限刻意保守；相关条件的真实差值方差可能较小，但 40 条试标不得用于估计该方差。全图平均 1.397 条分支/target，按四条件、双标计算，n=185 约为 2.1k 条 branch-condition judgments；n=738 约为 8.2k。实际工作量要按抽中 strata 的真实分支数和试标测得的每条用时更新，不能把 branch 数当成统计 n。

### 分层过采样敏感性（工作量与加权精度并列）

为显示稀有结构层过采样的代价，另计算一个**假设分配**：`empty_and_collision` 4 个 target 全取；`new_empty`、`new_collision` 各抽 50 个；其余名额按总体比例分给 `other_affected` 与 `unaffected`。估计总体时用各层真实总体权重 `W_h=N_h/N`，不使用样本原始比例。令 `S=Σ_h W_h²/n_h`；均值最坏半宽为 `sqrt(log(2/0.05)·S/2)`，三项配对差同时 95% 最坏半宽为 `sqrt(2·log(2·3/0.05)·S)`。区间采用有界变量 Hoeffding 近似、不利用有限总体修正；配对差范围为 [-1,1]。这里的 50 仅是工作量敏感性参数，不是已选样本数或高风险层充分精度承诺。分支负担按已观察 strata 平均原始分支数外推，4 条件×2 名审阅者对应约 8 个 branch-condition-review 单元/分支。

| 假设目标总数 | empty/collision/both/other/unaffected 分配 | target 等权总体均值 95% 最坏半宽 | 三个配对差同时 95% 最坏半宽 | 预计分支数 | 预计审阅单元（分支×4 条件×2 人） |
| ---: | --- | ---: | ---: | ---: | ---: |
| 200 | 50/50/4/77/19 | ±13.7 pp | ±31.3 pp | 420 | 3,359 |
| 500 | 50/50/4/319/77 | ±6.8 pp | ±15.4 pp | 835 | 6,683 |
| 800 | 50/50/4/560/136 | ±5.1 pp | ±11.6 pp | 1,251 | 10,005 |
| 1,050 | 50/50/4/761/185 | ±4.4 pp | ±10.0 pp | 1,597 | 12,774 |

因此，200 个目标更像流程/可行性样本，不能给出窄的总体配对差区间；即使总数 1,050，±10 pp 也只是这个有界、同时区间公式下的总体保守精度。每个稀有层只有 50 个时，其层内三对比较仍非常不精确（最坏同时半宽约 ±43.8 pp）；若要精确比较局部高风险层，需要更大层内样本和相应成本。以上不是传统功效分析，不基于 pilot 标签或目标效应。对标注小时的换算仍须由 40 条 pilot 另测每个 target/branch 的回查和双标时长。

复现上表（在 `hypergraph_analysis_exploration/` 中运行；输入仅为结构 frame audit）：

```powershell
python -m src.analysis.t02_stratified_precision_sensitivity `
  --frame-audit outputs/t02_sampling_frame_workload_audit_20261031.json `
  --out outputs/t02_stratified_sensitivity_new.json
```

输出为本机 ignored JSON，脚本要求新输出路径、不读取 gloss/labels/IDs。该情景计算脚本的 3 项测试与抽样框审计脚本的 6 项测试共 9 项均通过。换算为实际 reviewer-hours 仍需流程试标耗时；不能仅凭分支数估工时。

## 4. 冻结样本之前仍须完成

1. 明确建立可审计的上游来源家族 crosswalk；`source_root` 不能代替它。
2. 研究负责人选择主报告精度（如 ±10 pp 或更窄）、是否把三个相对 source 的差异设为同时 co-primary，以及每名审阅者可承担的时间。
3. 用 40 条 pilot 只估计每条审阅耗时、locator 回查率和不确定标签操作性；不读取/用于总体保真率。
4. 结合分层有限总体大小确定每层 n_h 和入样概率，再做独立随机抽样、保存 seed、frame hash、包含概率、失访替补规则及 reviewer assignment。
5. 冻结手册、数据/许可、变换器、样本 ID、分析代码和精度后，才生成私有盲审包。否则结果只能是探索性。

## 5. 验证范围

抽样框审计的六项和情景计算的三项合成单测均通过；扩展只统计各结构层 branch 总数/每目标均值，并从聚合摘要计算加权精度与预估审阅单元。对本机冻结包完整运行得到 110,425 targets、154,206 branches、7 个 `source_root` 标签和上列分层计数。输入摘要与现有 full-graph report 一致。机器输出写入 ignored `outputs/t02_sampling_frame_workload_audit_20261031.json` 与 `outputs/t02_stratified_sensitivity_20261031.json`，schema 分别为 `preposition-sampling-frame-audit/2` 和 `preposition-stratified-precision-sensitivity/1`。这些检查只验证样本框计数及无标签精度/工作量情景，不触及释义、语义保真、正式抽样或用户未提供的原始来源许可。
