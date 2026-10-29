# OEWN 释义标注 v3：预注册方案草案

**状态：内部草案，尚未预注册、签署或冻结。** 本文把当前 400 条 v3 抽样设计、标注 schema 和分析器的已实现行为整理为可审阅方案。它不是对外注册记录，不代表标注已开始或取得研究结果。标签揭盲前，研究负责人仍须审阅本方案、解决发布/来源 gate 并记录实际冻结版本。

## 1. 研究问题和范围

本阶段只研究人类能否以现有规范，对冻结包目标总体中的 OEWN 释义进行结构化分析，并报告标注者间的可复现程度和各自的总体加权边际分布。它**不检验**自动解析器、超图方法、NLI、上下位预测或推理准确率，也不检验新颖性。

目标问题：对于抽中的义项释义，两位互盲标注者如何分别分布在分析状态、Horn 投影状态、规则关系存在状态及语义支持状态上？同一条释义上的两位标注者对这些类别及其 AST、方向和证据 span 的一致程度如何？

不设模型有效性零假设或优效性假设，因为当前阶段没有冻结的模型预测或 matched baseline。所有方法效果问题留给有独立裁决标签、预先切分且未用于模型/阈值选择的后续研究。

## 2. 总体、样本与材料冻结

- 目标总体：本项目已定义的冻结超图 `nodes.tsv` 中 `oewn-` namespace、POS `{n,v,a,r}` 且 definition 非空的 104,907 个节点。该总体是特定冻结包的节点框，不外推为其他 OEWN release 的总体。
- 样本：400 个 `random_stratified` 项；24 个 POS × 官方 raw gloss 字符数 × 标点 strata；各层最少 2 项，层内无放回抽样。结构诊断样本数为 0，不补入其他富集案例。
- 固定抽样 seed：`20261004`。已记录 frame SHA-256：`ba17121d29b7c5140a897505a0a245b5964203f75d335e889cd7137bb2b0028d`。执行前必须重新生成或读取确切 frame、重新校验 SHA、manifest、盲标 batch 与 OEWN 2025 Plus archive；只要不一致即停止分析并先说明版本差异。
- 纳入释义要求在已生成样本中为 OEWN 2025 Plus raw gloss 精确匹配。已有本地复核记为 400/400；该文本匹配只证明 release 对齐，不代表语义标签正确。
- 标注材料只含盲化 `task_id`、POS、lemmas、raw gloss。标注者不可查看另一人标注、系统输出、冻结图 clauses、witness、答案键、抽样权重/stratum 或分歧汇总。不得把含混项静默排除。
- 已有 frame 与 blind batch 当前位于 `.gitignore` 路径；其存在/字节状态必须在实际执行时重新确认。任务发布前须完成[数据发布门槛](data_release_gate.md)要求的逐文件许可审查和 attribution。不得将该内部草案解释为分发授权。

以下哈希描述 2026-10-04 核对的当前本地 snapshot；只用于识别拟用材料，不代表这些被忽略的文件可对外发布。

| 材料 | SHA-256 |
|---|---|
| 候选抽样 frame JSONL | `ba17121d29b7c5140a897505a0a245b5964203f75d335e889cd7137bb2b0028d` |
| frame manifest | `ab91cd6bede5ccdbd202140c34e85988f2616f46985b9b52deff28cffb57e9bb` |
| OEWN release cross-check | `280b51b4ec96754771af3e738c6bd0fad650ee657a3c09f79eaade5baf955d04` |
| blind annotation batch | `dac533223c82bdd95dec6774d15a6350f10a1a9a07411db8bd0ca1c29997b6d5` |
| batch manifest（绑定 frame、batch、cross-check 与答案键哈希） | `b25088d4899c4ddeb6faf88a703d314dee43e93f963509d435e78979d3addc14` |
| OEWN 2025 Plus source archive | `8832b8fa26a14c0ba8c99bb1ef8db6f9e122a6d9193b65ca9e0ef572580fee7e` |

当前盲标 batch 已核验为 400 行、400 个唯一 task ID，且暴露字段仅为 `task_id`、`pos`、`lemmas`、`gloss`。本次检查未发现 `annotations_v3_annotator_*.jsonl` 回传文件；当前工作树中尚无人工标注回传。

## 3. 标注程序与标签

两名预先指定且互相独立的标注者各自完成同一批全部 400 项（合计 800 次 item-level 标注）；首轮互盲且不接触模型预测。使用已记录的 [标注协议](annotation_protocol.md) 与 `src/logic/annotation_validator.py` 的 schema；每名标注者使用唯一匿名 ID，保留其独立原始记录。当前两人是固定标注者对，不是从目标标注者总体随机抽样；因此 κ 只估计这两人在目标 item 总体上的配对一致性，不支持对其他标注者或标注者总体可靠度的推断。

每条记录至少标注：

1. `analysis.status ∈ {annotated, ambiguous, underspecified, unsupported, needs_review, not_a_definition, source_unclear}`；只有 `annotated` 要有非空 AST root。其余状态可无 AST，并须用 notes/unknown reason 说明主要理由。
2. 对每个 claim 标注关系、方向、公式节点、精确 raw-gloss evidence span、`semantic_support ∈ {supported, not_supported, uncertain, unassessed}` 和 confidence；标签依照[标注协议中的操作定义](annotation_protocol.md)。必要、充分、双向定义、典型属性、例子及其他关系不得互相折算。对 `not_supported`/`uncertain` 填写符合状态的 `support_reasons` 代码及 notes 理由；`not_supported` 表示原文未支持该 claim，不自动表示其反命题成立；`uncertain` 表示语义歧义未解，`unassessed` 表示尚未评估。
3. `horn_projection.status ∈ {projectable, partial, unsupported, not_attempted}`，并记录规则 ID 和 omissions。形式可编译不等于释义语义支持；不支持/不确定状态保留在分母中。
4. 字符偏移使用 Python Unicode code point、左闭右开 `[start,end)`。标注者不能通过删去 unsupported、ambiguous 或 needs-review 项提高成功率。

### 3.1 多参考 adjudication 的确认前决策

本研究的结构标签是从 gloss 得到的公式/规则集合；不同标注者可能提出不同但都被原文许可的形式化。将这类合法备选误算成错误，会低估一致性和系统性能；把所有备选 claim 合并成一个 union gold，又会奖励过度生成。因此，正式锁定确认性 estimand 前必须在以下两种方案中明确选定一种：

- **单一 reference 方案**：第三位裁决者为每项选择一个主 reference；承认只对该裁决 reference 评估，裁决理由另存。不能宣称测到所有合法形式化的 recall。
- **多参考方案**：在不查看任何模型输出的前提下，让裁决者可接受多套完整分析，并将其写入独立、版本化的 `gloss-analysis-reference/0.2` sidecar。每个 alternative 绑定完整 annotation record hash、root node IDs、claim IDs 与 rationale；whole-analysis alternatives 必须保持为各自的 sets，不能取 claims union。

多参考 sidecar 的状态约束：`complete` item 至少有一个 accepted alternative，且不得包含 unresolved candidate；只要仍有候选分析未决，整项保留为 `unresolved`，从完整裁决评分分母排除并单独报告。这样不能把“已确认至少一个有效答案”误读成“所有可接受答案已穷尽”。

二者不能在揭盲后依据结果选择。多参考方案已有未冻结原型：`src/logic/gloss_analysis_reference.py` 校验 sidecar 与不可变 annotation-record hash 的绑定；`src/analysis/score_gloss_analysis_references.py` 对完整 alternative 分别计算 claim-set F1，并把根 AST 与 status 纳入整体 exact match，同时输出按 claim 汇总的 micro 和逐项 macro。宏平均不含 claim 预测与 reference 同为空的项目；这些项目计入已完成裁决项的 exact-match 分母并另行计数。Unresolved 项不进入 exact-match/claim-score 分母，但须按全部 sidecar 项报告数量与比例。原型尚未运行验证、未经过标注者/研究者审查，也尚未锁定 schema/代码 hash；本草案的主要 estimand、报告顺序及 single-reference subset 的解释仍须在任何预测揭盲前书面确定。当前 400 项 input-lock 不包含 sidecar/schema 版本，也不改变 `protocol_signed=false`、`distribution_authorized=false`。因此这仍是签署/注册前必须裁决的设计项，不是已冻结的多参考研究协议。

两人回传后先进行 hash/schema/task-ID 完整性检查与互标一致性计算，再由指定的独立第三位裁决者或预先书面确定的裁决会议处理分歧。裁决记录另存，不覆盖两份独立标注；保存每项分歧和裁决理由。裁决标签只构成该样本的操作性 reference，不被称为无误的语义真值。

正式开始前还须冻结任务呈现顺序、预计时长、分段/休息安排与中途退出处理。本地 presentation plan v2 为两个匿名槽指定不同固定种子；`src.analysis.randomize_annotation_presentation` 按 `sha256-counter-fisher-yates/1` 对锁定 blind-batch task ID 排序，保留原 task ID，回传仍按 `task_id` 对齐。算法、生成器源码 hash 写入 presentation manifest；它使用固定 SHA-256 计数器规格，不依赖 Python `random.shuffle` 的跨版本实现。顺序 plan 不是原抽样/盲标 batch lock 的一部分。当前已根据 draft plan 在 git-ignore 的本地目录生成两个供内部审阅的 preview views；其 manifest/file hashes 记录在被忽略的 `outputs/phase7/annotation_presentation_v2/presentation_manifest.json` 中。preview 不是可行性试标，也不是正式锁定。正式启动前须先完成人工协议及来源许可审阅、用 frame 外独立材料评估 400 项负担和标签可理解性，再按已审版本生成并锁定正式 presentation views 和 hashes，并在受限执行记录中保存 presentation slot 到匿名 annotator ID 的映射。若采用外部盲标工具，必须核对其实际展示顺序并保留审计 schedule；不得仅凭导入文件行序推断展示顺序。试标只用于修改手册和安排工时，不并入正式数据；任何改动需在正式标签产生前冻结。抽样权重与独立标注者 estimand 不随呈现顺序改动。

## 4. 主要估计量和报告顺序

### 主要描述性估计量

对标注者 A、B **分别**估计下列类别的设计加权边际分布，不先把两人标签合并成共识：

- `analysis.status` 每个类别的加权比例；
- `horn_projection.status` 每个类别的加权比例；
- 每项是否有规则关系 claim 的加权比例；
- 每个 `semantic_support` 状态是否出现的逐项加权比例。
- 每个 `support_reasons` 原因码是否出现的逐项加权比例；该指标表示至少一条 claim 使用该码的 item-level prevalence，不解释为 claim-level 频率。

在完整响应且仍符合层内随机抽样假设时，类别/二元边际比例为 `p̂ = Σ_h (N_h/N) p̂_h`；常规分层 SRSWOR 方差形式为 `Σ_h W_h² (1−n_h/N_h) s_h²/n_h`。按 annotator 分别报告类别计数、加权分布、有效样本量、standard error 和区间状态。边际区间不提供同时覆盖保证，也不是裁决 gold 的比例。

### 一致性与结构性次要结果

- `analysis.status`、`horn_projection.status` 的设计加权 nominal Cohen’s κ、加权观察一致率、机会一致率和列联表；
- 每条释义是否至少有一个 rule claim 的设计加权 prevalence 与 κ；各关系类型、semantic-support 状态和 `support_reasons` 原因码是否出现的逐项 prevalence 与 κ 作为分项结果；
- 原始一致率、未加权混淆矩阵；AST node span micro-F1、root structure match、formula+direction 多重集 F1、evidence span F1、完整 claim+evidence 一致性；
- 未配对/无效回传数、按层完成率及所有 rejection/unknown 状态分布。

κ 区间只按当前实现报告为探索性 Taylor/Wald 摘要，并同时报告可报告率、欠覆盖警告和零分歧状态；不得将其称为已校准的确认性 95% CI。稀有比例的 Wald 区间也未校准。模拟发现 p≈0.01 与层间异质条件下 Wald 覆盖约 89%–90%，极稀有场景仅约 55% 样本能报告非退化区间。原因码是可重叠的多标签，按 item presence 单独估计；不得把各码比例相加解释为 100%，也不将其视为互斥的根因分类。分析脚本及 CI 版本须在执行前锁定；任何替代 estimator 都要在看真实标签前完成方法论选择和适用的模拟验证。

### 裁决样本与后续性能评测

裁决可用于构成本样本的标注基准，但不从本轮产生自动方法的性能或因果结论。此后若比较模型，须先锁定所有预测、模型 revision、prompt/parser/compiler/prover 版本和候选预算；按 sense 与 lemma-group 做无泄漏 split；只在 development 选择方法/阈值；在未用于方法选择的 test 上一次性报告。分别报告 sense、结构/方向、source-span support、Horn projection、proof replay、NLI gold quality、覆盖/拒答、成本和人工裁决结果。校验器或 proof replay 成功不得计作 semantic-support 正确。

## 5. 缺失、排除与停止规则

- 不做事后定向删样或依据标注结果替换个案。raw-gloss/release mismatch、文件/hash/schema 错误及资格条件失败均单独列明原因与 stratum。
- 当前设计加权 κ 实现要求完整随机 panel 的计划样本都双人配对，且 frame/batch hash 与 stratum 核验通过。任一项缺失时，不报告此实现的总体设计加权 κ；报告响应/匹配计数并暂停该 estimand，不能把权重改成 1，也不能把未配对项默认为负例。
- 当前工具没有经校准的非应答调整方法。若存在非应答或 release mismatch，不通过事后补抽修复；应在不查看标签的前提下先冻结调整方法并实现/验证，或从明确的新目标总体重建 frame、重新抽样并重新注册相应方案。两种方案均需保留原始抽样与偏离日志。
- 若发生盲化泄漏、任务材料版本错配、未授权文本分发、schema 更改或预定 estimator 更改，暂停主要分析，记录偏离；修正后的探索结果与原方案分开标记。
- 真实研究中断或标注退出按 item 和 stratum 报告。不得只报告可形式化子集的分母。

## 6. 代码和执行校验

执行时固定并记录：frame/batch/manifest 与 archive SHA-256、annotation schema 版本、validator 与 agreement analyzer 文件 hash、Python 版本、两份原始回传 hash、裁决记录 hash、实际日期、deviation log 与分析命令。当前 v3 新回传仍采用 `0.4-draft`（历史 `0.2-draft`/`0.3-draft` 仅作兼容读取）；此前协议记录的 analyzer 为 `wordnet-annotation-agreement/12`。v7 加入 `support_reasons` 的 item-level reason presence、一致性与完整 claim signature 对比；v8 将 `inference_basis` 纳入完整 claim 一致性；v9 对 AST 公式结构按量词作用域做绑定变量 alpha-normalization，自由变量仍保留名称；v10 将 claim 级 `variable_sorts` 纳入公式/标签比较；v11 对实验性 `0.6-draft` 比较 sort judgment 字段；v12 另报 variable-sort judgment multiset micro P/R/F1 与 item-bootstrap 区间。之后 analyzer v13 为实验性 0.7-draft 把 `target_variable` 纳入完整 claim signature，并将 sort judgment 对齐扩至 0.7；当前 v3 双标仍使用 0.4，0.5–0.7 不是已冻结方案。rationale 自由文本保留给裁决而非 exact-match IAA。正式双标前须确认结构一致性定义、手册、schema 和 analyzer 版本。本次分析器变化不构成预注册或已完成的标注。原因码只做多标签诊断，不替代自由文本理由或裁决。当前 `config/annotation_preregistration_v3_lock.json` 的范围仅为抽样/盲标输入的字节完整性与 schema preflight，不锁定本协议或分析器版本；正式标注前须先完成审阅、冻结协议，并在运行时记录本段列出的代码与材料哈希。

任务材料另有机器可读锁 `config/annotation_preregistration_v3_lock.json`，并可用以下入口执行 text-free preflight：

```powershell
python -m src.analysis.audit_annotation_preregistration_v3_inputs
```

该入口只输出各项检查状态、聚合计数和输入 SHA-256，不输出 gloss、task ID 或 sense ID。它检查锁定文件哈希、frame/manifest 一致性、样本与 strata 数、release cross-check 的逐项 raw-gloss 匹配、盲标字段与答案键覆盖、归档哈希，以及是否已有回传文件。 呈现视图另有 `python -m src.analysis.audit_annotation_presentation`，会对照 locked batch 与 draft plan 重放两个 task-ID 次序、比对文件/manifest hash 与四字段覆盖，并拒绝意外额外文件；只输出 aggregate status/hash，不输出 gloss 或 ID。该 audit 的 integrity pass 同样不代表 protocol signature、许可审核或分发授权。`integrity_pass=true` 仅表示当前输入字节与结构符合锁文件；脚本固定报告 `distribution_authorized=false`，也不表示许可审查、方案签字、外部注册或人工分发已经获批。任何材料有意改版时，必须人工审阅版本差异并同步修订草案与锁文件，不能把更新哈希当作自动批准。

完整回传后的现有分析入口：

```powershell
python -m src.analysis.audit_annotation_response_coverage `
  outputs/phase7/annotations_v3_annotator_a_returns.jsonl `
  outputs/phase7/annotations_v3_annotator_b_returns.jsonl
python -m src.logic.annotation_validator outputs/phase7/annotations_v3_annotator_a.jsonl
python -m src.logic.annotation_validator outputs/phase7/annotations_v3_annotator_b.jsonl
python -m src.analysis.annotation_agreement `
  outputs/phase7/annotations_v3_annotator_a.jsonl `
  outputs/phase7/annotations_v3_annotator_b.jsonl `
  --sampling-manifest outputs/phase7/annotation_candidate_frame_v3_400_manifest.json `
  --batch-manifest outputs/phase7/annotation_batch_2025_plus_v3_400_manifest.json `
  --output outputs/phase10/agreement_summary_v3.json
```

response coverage audit 使用盲标 task ID 与答案键中的抽样 stratum，按层汇总预期数、有效数、漏项、重复项、可定位的返回行结构错误、annotation schema 错误，以及有效记录中的 analysis/projection 状态分布；无法归入层的未知 task、无效 JSON 和非对象行另报全局计数。它同时核对 blind batch/answer key 与抽样 manifest 的 frame hash、层内配额及两份回传是否对应两个不同且各自一致的匿名标注者。输出只含聚合计数与回传、batch、答案键和 manifest 文件 SHA-256，不含 task ID、sense ID、标注文本或 annotator ID。只有 `complete_valid_paired_return=true` 才满足完整回传条件；否则保留覆盖报告并暂停设计加权估计，不得删去无效/未知项后继续估计。该报告不计算一致性或语义正确性。

这份执行草案本身不证明脚本实际覆盖所有研究 estimand；运行前须对照 schema/分析代码检查字段与报告，再用仅含合成标签的 smoke case 检查接口。只有得到项目负责人与标注者对最终文本的书面确认、材料许可 gate、具体注册记录和注册时间戳，才可把状态改成 preregistered。当前尚未满足这些条件。

## 7. 注册前必须冻结的行政信息

| 项 | 当前状态 |
|---|---|
| 方案责任人、作者贡献与既有稿件/数据归属 | 待确认；不得把 `AAAI2027.pdf` 的工作记作本项目用户成果 |
| 两位标注者、第三方裁决者及冲突处理 | 人员未指定 |
| 标注者目标总体及一致性外推范围 | 当前设计是两位固定标注者；仅估计固定 pair 的项目总体一致性，不外推到标注者总体；若需广义标注者可靠度，需另行增加标注者并调整设计/模型 |
| 800 次任务负担、时长/休息、独立任务排序 | 工作量/可理解性未试标；已生成基于固定 SHA-256 计数器 Fisher–Yates 算法的双槽本地 draft preview views（400 项/槽），manifest SHA-256 `e8709e907a1950aad989f69978f20cb45ef94bcabe7b6205c4e1072b9e821222`，未纳入正式 preregistration，`distribution_authorized=false`。仍须协议/来源审核、frame 外可行性试标、正式 view 哈希锁定及实际 slot/annotator 受限映射 |
| 任务开始/结束日期及标注者间隔 | 未指定 |
| 发布形式、OEWN attribution 文本、逐条许可结论 | 未通过 release gate |
| 注册平台、公开/封存状态、持久链接或登记 ID | 未选择、未登记 |
| 方案、抽样框、盲标任务、分析代码最终 hash | 执行前重算；此工作区没有首个 Git commit 作为可冻结版本 |

未解决这些项目时，本文件保持“草案”，不能对外声称已 preregistered。

### Phase 121：标注 v3 预注册输入完整性复核（2026-10-07）

重新执行 `src/analysis/audit_annotation_preregistration_v3_inputs.py`，21 项输入完整性/契约检查全部通过。400 条候选 frame、400 条 blind batch、400 条答案键、24 个 strata 与 OEWN release cross-check 完整对齐；七项冻结输入/来源材料哈希与 lock 相符。结果落于[可复算 preflight artifact](../outputs/phase121/annotation_preregistration_v3_input_preflight.json)，同时绑定 audit script 与 lock SHA-256。

该结果只证明当前工作区的文件字节、schema 和内部链接满足 preflight 契约。它没有标注回传（0 个文件），协议仍未签署，没有外部 preregistration ID，`distribution_authorized=false`。因此该批次尚未成为人工 gold，不能启动分发或报告标注结果；许可审查、负责人/标注者安排、注册与外部试标等启动 gate 仍需解决。完整分析见Phase 121 深度报告。

### Phase 122：多参考 scorer 与确认性 estimand 静态审计

对照当前 `src/analysis/score_gloss_analysis_references.py`、`src/logic/gloss_analysis_reference.py`、输入锁与 preregistration v3 草案，确认 scorer 对每个 `complete` item 分别比较整套 accepted alternatives，按规则 claim multiset F1 最高项选 reference；并列优先 whole-analysis exact，再按 alternative ID 排序。它不把 references 的 claims 取 union；claim exact match、root AST exact、analysis-status match 分别可见，overall exact match 要求三者全部成立。它只评分规则结构，不评分 evidence span、source support correctness 或 NLI。

这套逻辑与协议的“多参考不可合并、逐项最佳匹配”描述基本一致，但它估计的范围必须严谨写成“在 sidecar 已收录的可接受 reference 中，resolved items 的 per-item best-match 描述性分数”：

1. **多参考选择必须预测盲化并完整冻结。** 如果 adjudicator 在查看某模型输出后新增 accepted alternative，该模型会得到不对称优势。Sidecar 的格式校验无法证明 accepted set 穷尽或裁决者未见预测；这些是流程/访问控制证据，必须预先写入执行记录。Best-of-reference 有意承认多个合法形式化，但数值会高于或等于单参考严格匹配，不能单独宣称“唯一正确形式”或普遍模型性能。
2. **未决裁决项不进入 claim score 或 exact-match 分母。** scorer 输出 `unresolved_rate` 和计数，但该 rate 是未加权的；若难例更可能 unresolved，resolved-only score 只能解释为条件于裁决完成的结果。发表时必须同时给出完整测试项、resolved/unresolved 分母与原因、分层完成率/未决率；不能只报 resolved score，也不能把其外推为原始目标总体的表现。
3. **Macro 分母随预测而变。** 实现将 claim comparison 的空/空 item 从 macro P/R/F1 分母排除；当一套 reference alternatives 中包含空 claim set 时，不同预测可能改变哪些 item 进入 macro。故 per-system macro 可作为描述值，但跨系统 paired claim 不应只比较该 macro；须同时报固定分母的 exact-match（所有 resolved 项）与 micro 指标。若要做 macro 的模型间差异检验，先预定义仅由 reference/test frame 决定的共同 item 子集，并让所有系统使用同一分母。
4. **当前输出不是总体推断。** 协议已说明 scorer micro/macro 未加抽样权重；test set 的 split、lemma-group 隔离、selection rule 与 estimator 必须先冻结。若要外推至抽样目标总体，需要预先定义设计权重与 cluster-aware uncertainty estimator；不能把 400 项一致性/释义分析样本自动当作 400 项模型测试集。
5. **“最佳备选”只处理 claim multiset。** 证据 span、gloss 对规则语义支持、source-only proof replay 和 NLI 都需独立指标与其自身 gold；语法/结构一致不能代替它们。

当前 draft 尚未决定确认性研究采用单一裁决 reference 还是多参考 sidecar；Phase 122 不替研究者选择，也未更改 scorer。启动模型对比前应先由研究者选择并锁定 estimand、sidecar schema/hash、prediction-blind adjudication 流程和模型比较分母，再在 synthetic fixtures 上检查 scorer 行为。此次是代码/协议静态审计，没有运行 tests、CLI、gold 或模型预测。详见Phase 122 深度报告。
