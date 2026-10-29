# instance_hypernym 人工关系与 gloss-support 审查设计（草案）

状态：候选抽样框已在本地生成；本文件是研究设计草案，不是已签署协议、preregistration、标注结果或分发许可。当前 `config/annotation_preregistration_v3_lock.json` 仍为 `protocol_signed=false`、`distribution_authorized=false`；该锁适用于已有 400 项 gloss-formalization study，不自动覆盖本 pair study。

## 1. 目的与两个不同判断

本研究拟审查 OEWN 的 `instance_hypernym(instance,class)` 以及沿普通 class `hypernym` 推导的 ancestor pair。不能把两种问题混成一项标签：

1. **Sense relation judgment**：依照给定的两个词义，instance sense 是否属于 class sense？标签草案：`yes / no / uncertain / cannot_determine`。允许使用的上下文知识及 “no” 的证据标准尚需协议评审。
2. **Strict gloss-source support**：两条 source gloss 是否足以支持有向 claim `instance belongs to class`？采用 `supported / not_supported / uncertain / unassessed`，另记录 `inference_basis`、每条 gloss 的 `[start,end)` evidence spans 和原因。`not_supported` 只表示所给 gloss 没有支持该关系，不表示相反关系为真。需要外部常识时应标出 `external_world_knowledge`，不能计成 gloss-only support。

Source support 是当前项目的核心目标；sense relation judgment 是不同的外部参照。即使人类认为现实关系成立，如果 gloss 没有说明，也不能把它记为 gloss 支持。反过来，资源图中存在边也不能替代上述任一判断。

现有 canonical annotation schema `0.4` 将一个 item 绑定到单一 sense/gloss；它不能直接忠实表达两个 source records、两个 span 坐标系和一个跨 sense 关系 claim。不得把 pair 行硬塞进旧 schema。现已实现独立的 `wordnet-instance-relation-annotation/0.2-draft` 结构 validator：绑定两个 sense 和各自 gloss SHA-256，分别记录 sense-relation 与严格 gloss-support 判断，并用两个独立 span 坐标空间定位证据。`supported` 与 `gloss_only` sense-relation 在结构上要求两条 gloss 都至少有一个 span；这只是可审查的记录约束，不证明 spans 真的蕴含关系。该 draft 仅由 synthetic fixtures 测试，尚未冻结、做标注者可用性试点或语义验证，也未接入既有 0.4 批次。

## 2. 当前本地候选抽样

新增 `src/analysis/build_oewn_instance_manual_audit_frame.py`，从 byte-verified OEWN 2025 Plus 构造 **320 条 text-free candidate IDs**，每层 64 条。candidate 文件只有 `candidate_id`、`instance_synset_id` 和 `class_synset_id`；随机化 ID 不编码抽样层。隐藏 key 单独保存 stratum、资源状态、最短 class-lift depth 和负例 target pool size。候选文件没有 lemmas、glosses、examples、source text 或标注字段，尚不是 annotator-facing task。

| Stratum | 定义 | 资源池 | n |
|---|---|---:|---:|
| `direct_edge` | OEWN direct `instance_hypernym` pair | 8,599 | 64 |
| `lift_one_class_edge` | distinct instance/class pair，最短提升路径含 1 条 ordinary class `hypernym` edge | 9,112 | 64 |
| `lift_two_plus_class_edges` | distinct pair，最短提升路径含 ≥2 条 class edges | 50,574 | 64 |
| `reverse_direct_challenge` | direct pair 反向，且反向在声明闭包下不可达 | 8,599 | 64 |
| `same_pos_nonclosure_challenge` | 从 7,736 个有 direct instance edge 的 noun instance synset 均匀无放回抽样；每个 source 再从 84,909 noun targets 中均匀抽一个非闭包 target（排除 self 和 reverse-direct challenge） | source-level two-stage frame；每个抽中 source 的 eligible target 数记于隐藏 key | 64 |

固定种子 `20261008`，前四层在对应 unique directed-pair population 内 SRSWOR；最后一层是 source-level SRSWOR 后按该 source 抽一个 eligible target。Python 和 `random.Random (MT19937)` 版本写入 manifest。多个正类 stratum 使用各自可复算的 unique pair population；一个 pair 只进入一个正类最短深度层。正类汇总时，可在预先定义的共同 estimand 下按 `N_h / ΣN_h` 对 direct、lift-1、lift-2+ 分层比例加权。两个 negative/challenge strata 各自报告，不与正类或彼此合并成一个简单 accuracy。64/stratum 并非由预设区间宽度/功效目标推导，不能称作确认性样本量。Phase 81 事后规划审计给出近似 worst-case precision，但不替代预先选择 estimand 和区间方法。

对照用途：前三层可检查资源边/closure 与人类审查的一致性是否随提升深度变化；反向 pair 检查方向敏感性；same-POS random nonclosure 检查有限资源闭包之外的挑战项。候选由图构造，反向/未达只代表资源结构状态，不是真实语义负例抽样。


### Phase 81 precision audit（规划近似，不是功效分析）

使用 `src/analysis/audit_instance_relation_frame_precision.py` 从 text-free manifest 的总体数和样本数复算二元比例最坏情形（p=0.5）的点态 95% 正态近似误差半宽，含 SRSWOR 有限总体修正。当前 n=64 时，direct、lift-1、lift-2+ 三层各约 ±12.2 个百分点；按三层总体 pair 数加权的 closure-positive estimand 约 ±9.3 个百分点；相邻 lift 层差值的最坏情形半宽约 ±17.3 个百分点。若单层目标是 ±10 个百分点，该近似需要每层约 95–96 pairs。不同 estimand、边界比例或非响应会改变实际区间；这些值不构成已验证区间方法或确认性 sample-size/power 结论。

当前 320 pairs 若双人完成，相当于 640 份独立 pair annotations。same-POS nonclosure 的抽样单位是 source synset（7,736 个来源中 SRSWOR 64 个），每个被抽中的 source 再均匀抽一个 eligible target。自然估计对象是 source-macro 平均（每个 source 等权、source 内对 eligible targets 均匀），不是所有非闭包 instance/class pairs 等权的总体比例；该 challenge stratum 单独报告。当前规划审计仅给出忽略 source FPC 的 worst-case 正态近似半宽约 ±12.2 个百分点，不将其与正类或 reverse challenge 合并。若论文问题需要 pair-weighted nonclosure prevalence，需在 protocol freeze 前定义 pair inclusion weights 与对应 estimator/variance，并在冻结前确认 aggregate eligible-pair total 可复算。

复算命令：

```powershell
python -m src.analysis.audit_instance_relation_frame_precision outputs/phase78/instance_relation_candidate_manifest.json
```

该脚本只读取 manifest 聚合计数，不读 candidate IDs、sampling key 或 gloss，不写文件、不作语义计算。

## 3. 未来呈现与盲化（待审）

只有在数据授权、协议签署与 pair schema 冻结后，才从 pinned release 本地提取两条 lemma/POS/gloss，组装关系 prompt。初步建议 annotator-facing 字段只含随机 task ID、两个 senses 的 lemma/POS/gloss 和不显示 OEWN relation status 的关系问题；不得显示 synset IDs、stratum、source relation、路径深度、图特征或生成证据。候选顺序需按两个匿名槽独立随机化。若释义/词形许可和 attribution 未通过，不导出含文本的任务包。

两名独立标注者先盲标，第三方/预定义会议裁决；保留两种标签、span、依据、置信度和裁决轨迹。外部标注开始前还需使用该 frame 之外的试标材料检查理解度和时长，修改后冻结手册；不可把试标或裁决共识称为无误语义真值。

## 4. 可计算结果（待 schema 与计划冻结）

- 两位固定标注者分别报告 sense-relation 和 gloss-support 各标签的一致性、混淆表、span F1、uncertain/cannot-determine 比例及按 strata 的覆盖情况；未解决项不从分母中静默删除。
- 人类裁决后的 relation judgment proportion 与 source-support proportion 分开报告；每个 stratum 单独展示区间。direct/lifted 三个正类层可按其总体 pair 数预注册加权；reverse 与 same-POS negative challenge 不代表同一总体，不并入 pooled score。
- 若比较机器：固定 OEWN release、同一 pair list、model/prompt revision、预算和 blind split；报告 resource-status agreement、sense relation、strict gloss support、NLI、certificate replay、coverage/abstention、成本等分轴结果。资源证明通过不得代替 source-support correctness。
- 本候选 frame 是关系 pair 审查设计的第一版。要做 NLP 自动系统确认性比较，还需验证 split 单位（sense、lemma、实体类别泄漏）、多来源定义展示、基线和统计功效；当前均未锁定。

## 5. 当前文件和状态

- generator：`src/analysis/build_oewn_instance_manual_audit_frame.py`
- 合成测试：`tests/test_build_oewn_instance_manual_audit_frame.py`
- Pair schema draft：`src/logic/instance_relation_annotation_validator.py`
- Pair schema 合成测试：`tests/test_instance_relation_annotation_validator.py`
- Pair 标注手册草案：`docs/instance_relation_annotation_handbook_draft.md`
- Pair schema synthetic-only 记录样例：`tests/fixtures/instance_relation_annotation_0_2_synthetic.json`
- 精度规划审计：`src/analysis/audit_instance_relation_frame_precision.py`；测试：`tests/test_audit_instance_relation_frame_precision.py`
- 统计分析计划草案：`docs/instance_relation_statistical_analysis_plan_draft.md`
- 有限总体区间实现：`src/analysis/finite_population_proportion_intervals.py`；测试：`tests/test_finite_population_proportion_intervals.py`
- text-free candidates：`outputs/phase78/instance_relation_candidate_ids.jsonl`
- 隐藏 sampling key：`outputs/phase78/instance_relation_sampling_key.jsonl`
- manifest：`outputs/phase78/instance_relation_candidate_manifest.json`
- `outputs/phase78/` 被 `.gitignore` 屏蔽，避免把隐藏 strata/key 误带入公开或标注包。

manifest 的内部资源 preflight 对 320 个 pair 都调用 relation producer 并由独立 replayer 重验：resource status 64 direct、128 lifted、128 nonclosure；replay valid、0 errors。候选 SHA-256 `7eb8baf01f5cc7b8e5880558ef5b71691dca39114373cffcc3ebcd051978e146`；sampling key SHA-256 `347c9e2867333d9b268ea33a08483a3709acc3446d10c61b5e8f79fbe7f1f824`；manifest SHA-256 `d4c43ca20f8003f99f2fe803f8acbf8ff5468d04cdbd33db6ce7eea3515244ea`。本地候选物料的完整性不是授权、人工数据或研究结论。

复算命令：

```powershell
python -m src.analysis.build_oewn_instance_manual_audit_frame
```

输出已存在时默认拒绝覆盖；仅在确认重建本地候选和隐藏 key 时使用 `--force`。命令不会抽取/导出 gloss，也不会分发任何文件。

Pair validator 的调用示例（只应输入经授权的 pair annotations）：

```powershell
python -m src.logic.instance_relation_annotation_validator path\to\annotations.jsonl
```

该 CLI 只报告结构校验状态，不回显 gloss 文本，也不判断 relation truth 或 source support 的语义正确性。
