# OEWN 释义逻辑化标注：候选确认性样本设计 v3

状态：**400 条候选样本框已生成、release raw-gloss 核对通过并导出本地盲标包；设计加权类别 κ 与 Taylor 方差原型已实现。模拟发现稀疏边际/高一致性时零分歧会令普通 Wald 区间严重欠覆盖，分析器现抑制零分歧区间，但该压力场景下可报告区间仅约 35%；尚未注册研究方案、完成人工标注/裁决或分发任务。** 它不是人工 gold，也没有方法效果结果。加权 κ 区间目前只能标为探索性；本文件记录实现、失败边界和后续研究 gate。

## 抽样目标和边界

目标总体暂定义为冻结超图 `nodes.tsv` 中 `oewn-` namespace、POS 属于 `{n,v,a,r}` 且 definition 非空的节点。v3 清单记有 104,907 个合格节点；它们代表这个特定冻结包的节点框，不可直接外推为任意 OEWN 发行版总体。冻结包的来源许可仍是逐来源待审状态；即使候选抽中节点带有 OEWN ID，也须先核对其 raw gloss 是否精确来自固定 OEWN 2025 Plus 发布版。

候选框由 `src/analysis/annotation_sampling.py` 按固定 seed `20261004` 生成：随机面板 400 条、结构诊断面板 0 条；24 个 POS × gloss 长度 × 标点层各至少抽 2 条，其余名额按层内剩余容量比例分配并在每层内无放回简单随机抽样。manifest 为每层保留总体数、样本数、纳入概率和 Horvitz–Thompson 设计权重。候选 frame 只含 sense/来源标识、文本哈希、分层和结构字段，不含 gloss；该文件和 manifest 已加入 `.gitignore`。

按固定 OEWN 2025 Plus release 和归档 SHA-256 执行 source cross-check 后，400/400 候选均在发布版中找到且 raw gloss 完全匹配；effective definition 精确匹配为 376/400。盲标输入使用未改写 raw gloss，因此这次 effective mismatch 不剔除候选，但作为 source/effective 版本差异保留在隐藏答案键。导出器生成 400 条本地 blind tasks，每行仅暴露 `task_id`、`pos`、`lemmas`、`gloss`；答案键、cross-check 和导出 manifest 单独保存且被 `.gitignore` 排除。匹配只证明文本/义项版本对齐，不证明 gloss 支持人工 AST 或 Horn 规则。候选来自冻结图总体，不能据此将 104,907 的总体规模改称 OEWN 2025 Plus 全发布版总体；全体 population release 对齐仍未审计。

复算命令：

```powershell
python -m src.analysis.annotation_sampling --random-size 400 --diagnostic-size 0 --minimum-random-per-stratum 2 --seed 20261004 --output outputs/phase7/annotation_candidate_frame_v3_400.jsonl --manifest-output outputs/phase7/annotation_candidate_frame_v3_400_manifest.json
```

本次生成清单的 frame SHA-256 为 `ba17121d29b7c5140a897505a0a245b5964203f75d335e889cd7137bb2b0028d`。抽样复核显示：400 个唯一 item、24 层样本数最小值 2、最大值 94、设计权重范围 2–291.25；按设计权重计算的 Kish 有效样本量约 380.6。对二元总体比例、最坏情形 `p=0.5`，以各层无放回 SRS 的有限总体方差上界计算，正态近似 95% 半宽约 5.01 个百分点。此为缺失为零、所有候选都能有效标注时的规划近似；它不是 κ/F1 的误差界，也不是本项目观测结果或正式区间。

## 预定标注和估计口径

该轮首先建立定义解析可用性 gold，不作模型显著性检验。双人独立盲标后保留全部 `annotated / ambiguous / underspecified / unsupported / needs_review` 状态，不因无法转成 Horn 规则而从分母剔除。拟报告：

1. 全总体释义分析状态和 Horn 投影状态分布，保持不确定/拒答类别显式；
2. 对双人可匹配的 AST 节点、关系/方向、证据 span 与 Horn 投影标签报告一致性；
3. 在后续系统预测冻结后，再以裁决标签评估 source-span 支持、方向正确、Horn 投影、proof replay 与覆盖/拒答；这部分须用独立 sense/lemma-group test，不得用本轮试标分数代替。

总体类别比例采用分层设计加权估计：`p_hat = Σ_h (N_h/N) p_hat_h`，其中 `N_h` 为目标总体中第 h 层数量，`p_hat_h` 为该层样本比例。若有效回收完整且仍为层内无放回简单随机样本，二元比例的设计方差按 `Σ_h W_h² (1 - n_h/N_h) s_h²/n_h` 估计；非应答、release 不匹配和排除情况需逐层报告，不能悄悄补样或把权重改成 1。随机面板以外的结构富集样本只作故障模式分析，不并入总体估计。

两标注者一致性按该设计重加权列联表计算 weighted nominal Cohen's κ：以每条共同标注 item 的层权重 `N_h/n_h` 构造联合分布与边际分布，再计算观察一致率、机会一致率和 κ。当前 `src/analysis/annotation_agreement.py` 在传入本抽样 manifest 与匹配的盲标导出 manifest，并确认所有计划随机项均完成双人配对标注、batch hash 和 stratum 一致后，才对类别型结果计算加权 κ；设计加权范围为分析状态、Horn 投影状态、逐项关系 presence 与 semantic-support presence。同时，`marginal_prevalence_by_annotator` 为两名标注者分别给出分析状态、Horn 投影状态及逐项关系/语义支持 presence 的加权边际比例和分层 SRSWOR 方差。它们描述各标注者的边际分布，不是合并共识或裁决真值；类别区间分别为边际区间，不作同时覆盖保证。非普查情况下若观察到的层内方差为零，会只给点估计并抑制退化区间；全层普查时比例区间为精确点值。当前截断正态 Wald 区间仅作探索性摘要，不是已校准的 95% 推断。

本设计只纳入两位预先指定的标注者，二人都标注全部 400 项。因此加权 κ 的目标是**这对固定标注者在该冻结总体项目上的一致性**；标注者并非从更大的标注者总体随机抽取，κ 不能解释为标注手册对任意新标注者的可靠度，也不能支持标注者总体层级的推断。若论文要主张协议可由其他标注者复现，需要增加独立标注者样本，并采用能区分 item 与 rater 变异的设计/模型；当前双人设计不能回答该问题。

### 边际比例区间的设计模拟

由于比例区间未由 κ 区间模拟覆盖，新增 `src/analysis/simulate_annotation_prevalence_ci.py`，按同一 24 层 v3 manifest 独立生成每层 0.5、0.1、0.01、0.002 prevalence 和层间异质五类有限总体，再每个场景生成 5 个有限总体、每个总体重复分层 SRSWOR 1,000 次。原始区间是截断正态 Wald；logit 与 arcsine-square-root delta 区间仅作为诊断对照，不据这批模拟选择或宣称某种区间已有效。

| 合成场景 | 平均有限总体比例 | Wald 覆盖率 / 可报告率 | logit 覆盖率 / 可报告率 | arcsine 覆盖率 / 可报告率 |
|---|---:|---:|---:|---:|
| 均衡 p=0.5 | 0.49952 | 94.82% / 100% | 94.96% / 100% | 94.88% / 100% |
| 中等 p=0.1 | 0.10038 | 95.12% / 100% | 95.34% / 100% | 95.36% / 100% |
| 稀有 p=0.01 | 0.00979 | 89.72% / 97.9% | 95.85% / 97.9% | 96.42% / 97.9% |
| 极稀有 p=0.002 | 0.00204 | 97.14% / 55.2% | 91.62% / 55.2% | 96.23% / 55.2% |
| 层间异质 p_h=0.001–0.03 | 0.01333 | 89.35% / 99.4% | 96.88% / 99.4% | 94.30% / 99.4% |

覆盖率以已报告区间为分母，同时报告可报告率；原始 Wald 两类场景出现约 89%–90% 条件覆盖率。变换区间在部分场景改善覆盖，但极稀有类别下 logit 覆盖约 92%，arcsine 在异质场景约 94%，没有一个候选在所有情景中同时稳定达到名义 95%。极稀有场景只有约 55% 的样本能报告非退化区间。每个场景总计 5,000 次抽样，覆盖率 Monte Carlo SE 约 0.003–0.004；跨 5 个固定有限总体的覆盖范围也留在机器报告中。该证据足以将当前 Wald CI 标为未校准探索性区间，不足以挑选替代区间或证明普遍覆盖。复算命令：

```powershell
python -m src.analysis.simulate_annotation_prevalence_ci --replicates 1000 --population-replicates 5 --seed 20261006 --force
```

机器报告 `outputs/phase10/prevalence_ci_design_simulation.json` 被 `.gitignore` 排除，记录 manifest hash、各有限总体结果、区间覆盖率、可报告率、Monte Carlo SE 和变换区间诊断。模拟代码和测试纳入源码；实际标注比例未知，不能把模拟结果当作经验标签结论。

方差采用一阶 Taylor 线性化：将 κ 视为加权列联表联合单元比例的光滑函数，求其对各单元比例的梯度，再在层内按 SRSWOR 使用有限总体修正 `Σ_h W_h²(1−n_h/N_h)s²_h/n_h`；区间为正态 Wald 95%。survey-weighted agreement 的 Taylor 线性化和 jackknife 可参照 [Statistics Canada 方法论文](https://www150.statcan.gc.ca/n1/pub/12-001-x/2012001/article/11686-eng.pdf)，但该论文聚焦二元结果；本实现将其推广到多分类名义 κ，来源论文不是这段代码的直接验证。合成单元测试检查加权联合分布、κ 和线性化标准误的解析期望；另对固定 v3 manifest 做了条件有限总体重复抽样模拟，并以分层 delete-one jackknife 方差作交叉比较。

模拟复算命令：

```powershell
python -m src.analysis.simulate_annotation_kappa_ci --replicates 2000 --seed 20261005 --output outputs/phase10/kappa_ci_design_simulation.json
```

脚本按 24 层真实 `N_h,n_h` 配置，为每个场景生成一次合成有限总体，再在各层独立 SRSWOR 重抽 2,000 次；真值是该固定有限总体的 nominal κ。包含三分类均衡、稀有类别（约 2%）、独立边际（κ≈0）、稀疏边际且高一致性（minority prevalence 约 1%、目标 κ≈0.95）和层间 prevalence/agreement 异质五个场景。覆盖率括号内为 Monte Carlo 标准误；“有效”列为 Taylor/jackknife 可用区间数：

| 合成场景 | 固定有限总体 κ | Taylor 覆盖率（可报告区间内） | Taylor 可报告率 | Jackknife 覆盖率（可报告区间内） | Jackknife 可报告率 |
|---|---:|---:|---:|---:|
| 三分类均衡 | 0.5555 | 0.9430 (0.0052) | 100% | 0.9430 (0.0052) | 100% |
| 稀有类别 | 0.4516 | 0.9495 (0.0049) | 100% | 0.9515 (0.0048) | 100% |
| 独立边际、κ≈0 | 0.0007 | 0.9455 (0.0051) | 100% | 0.9465 (0.0050) | 100% |
| 稀疏边际、高一致性 | 0.9483 | 0.9788 (0.0054) | 35.4% | 0.9971 (0.0020) | 34.9% |
| 层间异质 | 0.7031 | 0.9525 (0.0048) | 100% | 0.9530 (0.0047) | 100% |

四个非极端场景覆盖率约 94.3%–95.3%，且模拟都能报告区间。稀疏边际/高一致性场景中，64.6% 的样本没有观察到任何标注分歧；此时 κ 点估计为 1，但真实有限总体 κ=0.9483。分析器不再输出这种零分歧样本的 Taylor 区间，只返回点估计和 `point_estimate_only_no_observed_disagreements` 状态。其余可报告 Taylor 区间为 708/2000，条件覆盖率 97.88%；jackknife 区间为 698/2000，条件覆盖率 99.71%。可报告率仅约 35%，另有 Taylor 27/2000 次点估计不可估、jackknife 133/2000 次方差不可估；平均 Taylor SE=0.0509，而 κ 估计的重复抽样 SD=0.1243。高条件覆盖率伴随低可报告率，不能解释成总体 95% 推断已经解决。样本分歧少于 10 对时分析器另附欠覆盖警告；10 是操作性告警阈值，不是验证过的统计临界点。

这是对“零观察分歧时报告零宽区间”规则的压力测试，不是普遍有效性的证明：每个场景只条件于一个随机生成的有限总体，未覆盖非应答、误分层、不同标注者相关机制、多个有限总体生成 seed 或替代的小样本区间方法。少于 10 个分歧的告警也未被校准；即使超过该阈值，也不能据此推断区间已普遍有效。当前真实双标尚未回传，也没有经验 κ。机器可读汇总见被 `.gitignore` 排除的 `outputs/phase10/kappa_ci_design_simulation.json`，其中保留总体 κ、条件覆盖率、区间可报告率、Monte Carlo SE、零分歧比例、不可估次数、两类 SE、seed 与输入 manifest SHA。

## 开始标注前的 gate

- 已完成本 frame 的 OEWN 2025 Plus raw-gloss 对齐检查：400/400 exact，导出器已生成 400 条 blind tasks。若重建输入或归档导致 SHA 变化，须重新核验；导出器是 all-or-nothing。若以后出现 mismatch，须先在不查看任何标签的前提下界定新的目标总体（如 release-exact 子总体），从该完整合格总体重新抽样并重算各层权重，不能从 400 个旧样本中事后删行或手工替换。
- 逐项解决来源与任务材料的使用/分发许可，保留 OEWN attribution 和修改说明；候选框生成或本地校验不代表获得发布许可。
- 审阅并冻结[预注册方案草案](annotation_preregistration_draft_v3.md)中的标注手册、工具/schema 版本、双标互盲策略、裁决流程、主要估计量及缺失/排除处理；解决草案列出的人员、许可、注册平台和版本 hash 项，然后才称为 preregistered protocol。
- 冻结任务呈现顺序和可行性安排：确认每人完成 400 项（总计 800 次独立标注）的预计负担；用不属于确认性 frame 的材料做时间/可理解性试标，记录休息与退出处理；确定盲化任务是否由工具分别随机排序，并保存仅供审计的顺序/版本信息。若需修改样本量或分配，必须在正式标注与查看标签前重新计算抽样权重、精度规划和分析版本。本地 schedule exporter 与两槽固定种子的草案计划现为版本 2（[计划](../config/annotation_presentation_plan_v2.json)、[排序算法](../src/analysis/presentation_order.py)、[生成器](../src/analysis/randomize_annotation_presentation.py)），使用版本化 `sha256-counter-fisher-yates/1`，不依赖 Python `random.shuffle` 的跨版本实现；Python 官方说明多数随机模块算法可跨版本变化，仅承诺兼容 seeder 下 `random()` 序列稳定（[官方说明](https://docs.python.org/3/library/random.html#notes-on-reproducibility)）。算法以 domain-separated SHA-256、十进制 seed、递增大端 counter 生成 uint64，经 rejection sampling 后执行降序 Fisher–Yates。生成器为两个匿名槽输出独立 task-ID 次序，canonical blind batch、ID 和答案键不变。现有仅供内部审阅的本地 draft views 各 400 项、答案键未包含；manifest SHA-256 为 `e8709e907a1950aad989f69978f20cb45ef94bcabe7b6205c4e1072b9e821222`，两个 view 的文件哈希为 `0faf40b6d662ceff9030a7a0d562e369f42cbb52141935e3a7181d20fa47deb8` 与 `b0f0448a51622028a82cd61ff012e4637338aa5bb178bbe28c6a8ac79d53c1fc`；manifest 同时绑定 plan、算法和生成器源码 hash。text-free 审计入口 [audit_annotation_presentation](../src/analysis/audit_annotation_presentation.py) 可重放两个 task-ID 次序并复核覆盖、来源内容对应与答案键缺失。预览只是基于现行草案计划生成的本地材料，不是工作量/可理解性试标，不构成最终顺序冻结、protocol signature、许可结论或分发授权；正式启动前仍须完成人工协议与来源审核、frame 外试标、最终材料 hash 锁定，并在受限记录中保存 slot 与匿名 annotator ID 映射。若外部工具另行重排，须保存工具实际呈现顺序而不能声称使用本 schedule。
- 先完成独立标注与一致性审查，再生成裁决 gold 和 sense/lemma-group split；系统作者不得先看该 test 标签并据其选择规则、阈值或模型。

现有 `/v2` 的 160 随机 + 40 诊断 pilot 保留为协议试标，不与 v3 合并；它有 9 个非普查 singleton 层，无法用当前 Taylor 方差实现总体 κ 区间。v3 只有候选 frame 和本地任务包；当前仓库没有标注回传、裁决 gold、NLI 模型预测或匹配基线结果。
