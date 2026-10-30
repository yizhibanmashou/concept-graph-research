# T02 介词关系 schema 与盲审协议草案

状态：schema v0 草案；本轮只冻结用户已决的实验口径并定义结构字段，不转换真实 OEWN 记录、不导出释义文本、不创建人工标注任务包。该文档不是预注册，也不是语义结果。

## 1. 研究问题和结果边界

在固定冻结图及同一目标/分支上，比较介词消融和保留关系信息的表示会造成哪些结构变化，以及定义中可由来源支持的语义信息是否被保留。两个目标并列报告，指标、单位、分母和区间分别呈现，不合成单一总分。

结构变化只说明当前图在给定变换下的组织方式变化；定义保真由独立人工审阅标签估计，不能由节点可达性、路径数或规则类型直接推出。本文不把构造依赖解释成逻辑蕴涵，也不作认知发展结论。

## 2. 用户已决定的协议

- 主结构消融：删除所有 `pos=prep` 依赖 occurrence；`pos=prep_phrase` 单独作为敏感性分析，不与主口径合并。
- 四种表示条件：原图；删除介词；保留未解析边界；仅在来源证据支持时替换成类型化关系。每一条件使用同一冻结输入、目标、分支与展开边界。
- 类型化关系限定为有来源支持的空间/位置、方向/路径、参与者角色、否定/缺失；论元有序并引用原始 occurrence。无法确定类别、论元角色或否定范围时必须标为 `unresolved`，不允许根据介词字符串或 POS 自动补标签。
- 结构变化和定义保真并列报告，单独给分母和解释。
- 保真审阅记录方向/论元、否定范围、内容遗漏/添加三轴，并记录整体判断。
- 已有 40 条材料只用于改进说明手册与流程，不进入正式估计。正式审阅样本独立抽取。
- `without` 的 OEWN 图义项与 ToLogic 中显式外部 `without` 接口是不同对象，数据字段、评价标签与结论不混用。

## 3. 条件和变换记录

每个审阅单元包含一个冻结 target 和一个有稳定 `branch_id` 的 OR 分支。分支内部仍保留原始 AND 输入顺序及 occurrence 身份。条件变换不可原地覆盖输入：需同时保存 `source_branches` 与各条件的结果分支。

源记录中的每条 OR 分支必须至少包含一个前提；空源分支属于输入完整性错误。消融变换后产生的空分支则必须保留为显式结果，并标注 `empty_after_transform=true`，不能与输入空分支混为一谈，也不能解释为无条件真命题。

| 条件代码 | 输入到输出的变换 | 必须显式记录 |
| --- | --- | --- |
| `source` | 原始冻结分支 | 原始 occurrence 清单、来源版本摘要 |
| `prep_delete` | 删除主口径 `pos=prep` 的 occurrence | 被删 occurrence IDs；删除后为空的分支仍保留 |
| `boundary_preserve` | 不猜语义类别，保留介词位置作为未解析边界 | 边界两侧 occurrence；未解析原因 |
| `typed_relation` | 仅对来源可核实的关系建立类型化记录；不能核实时保持 unresolved | 关系类别、带角色有序论元、证据引用、极性/否定作用域 |

`prep_phrase` 敏感性运行应单独标记 `prep_scope=prep_plus_phrase`，不覆盖或替代主分析产物。空分支是变换结果，不得解释为无条件真命题；非空碰撞应与空分支分别计数。

## 4. 记录 schema v0

公开 schema 只保存稳定 ID、索引位置和证据引用，不内嵌释义原文或私人标注。任何 locator 应足以在本机经许可保存的数据中定位来源；提交到公开仓库前仍须单独审查许可和隐私。

### 4.1 单元及来源字段

| 字段 | 类型 | 约束/含义 |
| --- | --- | --- |
| `schema_version` | string | 固定 schema 版本，例如 `t02-relation-v0` |
| `item_id` | string | 审阅单元的稳定匿名 ID；不由条件或标签生成 |
| `target_id` | string | 冻结图目标/义项 ID |
| `source_version` | object | nodes/rules 版本、SHA-256 与转换输入摘要 |
| `source_branches` | array | 原 OR 分支清单；每个分支有稳定 `branch_id` 和有序 `premise_occurrence_ids` |
| `occurrences` | array | occurrence ID、branch ID、branch 内位置、node ID、POS、source locator；重复节点出现时仍是不同 occurrence |
| `conditions` | array | 四条件各自的变换标签、prep scope、结果分支、边界和关系记录 |
| `transform_version` | string | 只读转换器版本；重跑必须可追溯 |

### 4.2 类型化关系字段

每条 relation 至少包含 `relation_id`、`branch_id`、`source_occurrence_ids`、`category`、`predicate`、有序 `arguments`、`polarity`、`negation_scope`、`evidence_refs`、`status` 和 `unresolved_reason`。

`category` 允许 `spatial_location`、`direction_path`、`participant_role`、`negation_absence`、`unresolved`。`predicate` 是有来源依据的窄标签；不确定时为 null。每个 argument 包含 `role`、`occurrence_ref` 和可选的来源 span。论元顺序具有语义意义，禁止把它转成无序节点集合。

`polarity` 取 `positive`、`negative`、`unknown`。`negation_scope` 引用源 occurrence 或 locator span；没有可复核证据时用 `unknown`，不能默认为 positive。`evidence_refs` 应定位支持该类别、角色和作用域的原始来源片段；只引用外部词典 synset 而没有关系证据，不足以断言该关系。

`status=supported` 要求类别、predicate、论元和证据引用齐全；`status=unresolved` 要求写明原因，且不作断言式 predicate。缺少关系证据、无法绑定论元、否定范围歧义、来源不可访问是不同失败原因，应分别记录。

### 4.3 人工保真记录（独立于结构 schema）

人工审阅记录不可写入被冻结的图条件对象。它用独立、访问受限的数据文件关联匿名 `item_id` 与一次审阅；审阅者原始意见、裁决结果与结构产物分开保存。

| 维度 | 建议标签 | 解释 |
| --- | --- | --- |
| 方向/论元 | `preserved` / `changed` / `missing_or_added` / `cannot_determine` | 检查有序角色及方向是否被颠倒、遗漏或新增 |
| 否定范围 | `preserved` / `changed` / `lost_or_added` / `not_applicable` / `cannot_determine` | 区分未观察到损失与没有评估；记录作用域证据 |
| 内容 | `no_observed_loss` / `omission` / `addition` / `both` / `cannot_determine` | 相对原释义记录内容差异，不把未评估记作无损失 |
| 整体 | `faithful` / `changed` / `cannot_determine` | 关键方向、否定或定义内容实质改变即为 changed；不能判断单列 |

每个标签需有简短理由和证据 locator；置信度如收集，作为审阅者主观辅助字段，不解释为正确概率。该标签手册需要在 40 条试标中检验可操作性，再在正式样本抽取前冻结。

## 5. 盲审和正式抽样协议

### 5.1 试标阶段

既有 40 条只用于检查字段理解、样例说明、每条用时、泄盲风险、locator 可回查率与分歧类型。不得将试标计入正式保真比例或四条件比较，也不以试标类别比例决定正式结论。允许根据试标修订手册；每次修订需记录版本和理由。

### 5.2 正式样本框（待冻结）

**统计单位已由用户决定为目标等权。** 抽中目标应纳入其全部可审查 OR 分支；目标内先计算每类标签所占分支比例，再对目标等权平均。另报“目标中全部分支均标为 faithful”的严格次要比例。分支是目标内重复测量，区间估计和重采样以目标及来源家族的嵌套关系为准，不把分支数当独立样本数。

正式抽样仍须锁定来源/语言/词性可覆盖总体、目标与分支去重规则、分层变量、纳入概率及总资源。建议按 source family 隔离；同一释义来源家族不能同时用来调规则和生成确认性评测样本。分层可含关系类别、方向/否定、消融后碰撞或新空分支、未受影响对照；稀有层若过采样，最终估计按已保存的抽样概率加权。

**来源家族 gate 尚未满足。** 冻结包 `nodes.tsv` 的 `source_root` 只有七种构建/处理阶段标签；`indexes/source_records.jsonl` 的字段仅为 `path`、`identity`、`pos`、`lemmas`、定义/parts 及审核状态等，不显式给出 provider、release/version、format 或 license。`OEWN/README.md` 和 `docs/data_provenance.md` 也说明该包是混合来源且经历多轮筛选、改写和 WSD。故 `source_root` 或目录名不能直接作为独立词典来源家族；路径分层也不能证明来源独立。正式样本前需在许可范围内建立可追溯的上游资源交叉表，字段至少包括来源记录 locator、原始资源/版本（若能确认）、家族判定依据、授权状态与 `unresolved` 原因。未能确认的记录不得被强行分配到某个独立家族；在交叉表和覆盖率审核完成前，不宣称 source-family holdout/bootstrap 已实现，也不生成确认性盲审包。

样本量不在本文臆定。负责人需先选择主要估计量、区间置信水平、最大可接受半宽或最小可辨差异、来源家族数量与工作量上限。之后按有限总体及分层/配对结构计算需要量，并对未响应和无法判断率做预先预留。40 条可估计流程耗时，不用于估计保真率。若有效来源家族或样本不足以达到预定精度，结果降级为探索性，不通过反复追加样本追求理想方向。

### 5.2.1 冻结来源证据子集审计（2026-10-31）

进一步检查包内 source payload 后，需区分“索引字段”与 payload 中的嵌套来源证据：索引本身仍不含 provider/version/license 列，但 `sources/Synset/alternative_or_definition_wsd_frozen/` 子集有 `alternative_definition_provenance.source_evidence`。新增的只读工具 `src/analysis/audit_preposition_source_provenance.py` 仅输出聚合字段，不输出定义、释义、义项 ID、路径、URL 或原始 locator；结果保存在被忽略的本地文件 `outputs/t02_source_provenance_audit_20261031_v3.json`，并记录 source index 与所读 payload 集的摘要。

该子集的 5,625 条 indexed source records 均成功读取；3,444 条记录含非空 `source_evidence`，合计 3,645 个 evidence item、82 个原样 `source` 标签。按 evidence item 计，频数最高的标签是 GCIDE 0.54（1,580）、Kaikki/Wiktextract targeted OEWN gap（881）、MeSH 2026 descriptors（356）、EMBL-EBI OLS（275）及 Kaikki/Wiktextract relaxed definition-term fallback（201）。另有 1,512 条记录没有 provenance object，669 条有 provenance object 但无 evidence list。现有 evidence item 没有 license/licence 字段。以上标签是冻结包自报来源字符串，不是已规范化、已验证独立性或已完成许可核查的 82 个 source family；evidence item 数也不是目标数。

这项审计修正了“该路径下没有来源线索”的过宽判断，但**没有通过来源家族 gate**：多数有证据项含 source version、locator 与定义哈希，仍须逐来源核验身份、版本和许可；混合来源标签还需在人工规则下归并或标 `unresolved`。5,625 条只是此处理目录的记录子集，不能外推到全冻结图。下一步可建立“源记录 → 原始来源/版本 → 归一化 family → 许可状态/证据 → unresolved 原因”的可审阅交叉表，并先报告各家族可覆盖的结构 strata。正式确认性抽样仍需负责人审定来源纳入范围、未解析项的处理及工作量预算。

从 `hypergraph_analysis_exploration/` 运行复算（输出路径必须不存在）：

```powershell
python -m src.analysis.audit_preposition_source_provenance --bundle ../OEWN --out outputs/t02_source_provenance_audit_20261031_v3.json
python -m unittest tests.test_audit_preposition_source_provenance -v
```

### 5.2.2 T02 来源标签与权利日志的保守对账（2026-10-31）

来源证据覆盖审计的 82 个 exact label 与本地 `sources/source_release_rights_evidence_2026-10-06.json` 做了两种 join：原样字面匹配命中 6/82 个标签、143/3,645 个 evidence item；随后只对大小写、下划线/空格和重复空白做确定性规范（不做模糊匹配或人工别名推断），命中 17/82 个标签、2,395/3,645 个 evidence item。唯一规范化匹配中 4 个标签有权利日志状态字段，涉及 2,270 个 evidence item；其余 13 个匹配标签无该字段。没有规范化标签碰撞；仍有 65 个标签、1,250 个 evidence item 未匹配。该结果说明历史权利日志的覆盖很大程度受标签写法影响，同时 Kaikki/Wiktextract 两个高频标签（881 + 201 = 1,082 evidence items）仍未与现有权利日志标签对上。

复算代码 `src/analysis/reconcile_t02_source_label_rights.py` 只读两份聚合 JSON，输出精确标签、item/record 计数、匹配状态、日志中的类别状态与输入 SHA-256；不读取源记录释义，不输出 URL、locator、sense ID、source text 或权利证据正文。命令（从本项目目录运行；输出必须是新路径）：

```powershell
python -m src.analysis.reconcile_t02_source_label_rights --audit outputs/t02_source_provenance_audit_20261031_v3.json --rights-log sources/source_release_rights_evidence_2026-10-06.json --out outputs/t02_source_label_rights_reconciliation_20261031_v2.json
python -m unittest tests.test_reconcile_t02_source_label_rights -v
```

匹配只表示能定位到一条已有权利日志记录；GCIDE 状态仍写明 payload/version alignment 未验证，MeSH 状态只记录提供方重用条款而未指派标准许可证，OLS 不是单一许可证。剩余标签或有日志状态字段都不证明上游发行版与冻结 payload 的逐条对应、可再分发兼容性、来源独立性或语义保真。该对账不改变 `not_cleared_for_public_release` 状态，不能据此启动正式盲审。

### 5.2.3 Kaikki/Wiktextract 高占比标签版本形态核查（2026-10-31）

为追查未匹配的两个高频标签，新增 `src/analysis/audit_t02_targeted_source_metadata.py`，只对这两个原样标签汇总 `source_version` 形态、`evidence_type` 枚举、locator/ontology 主机名与字段覆盖；不输出原始版本值、摘要、locator、URL、定义、义项 ID 或本地路径。全量复扫指定子集 5,625/5,625 个 payload 无解析错误，两个标签共 1,082 个 evidence item：targeted gap 881 项（878 条记录），relaxed fallback 201 项（201 条记录）。后续对安全字段的二次比对发现，1,082/1,082 的 `source_version` 均为 `raw-sha256:<64 hex>` 形态；两个标签分别只有一个不同的摘要，且二者相同。字段名和格式只能说明它是一个 SHA-256 标记，**不能说明被哈希的对象是什么**。两标签中 881/881 与 201/201 条记录均有格式合法的 `definition_text_sha256`，但 `source_version` 摘要与该定义文本哈希 0/1,082 相等。因此该摘要不是此处定义文本哈希的直接复写；尚无本地生成器、清单或上游发行字节将其绑定到确定的数据对象/版本。`source_locator` 全部不是 HTTP(S) URL，`source_ontology` 全部缺失；`evidence_type` 分别为 `definition`（881）和 `related_definition`（201）。Kaikki 来源快照、逐记录来源身份和许可仍为 `unresolved`，不进入独立 source-family holdout 或许可放行。

这与 Kaikki 官方 raw-data 页面当前列出的 enwiktionary dump 日期（2026-10-01）并不矛盾：网页说明的是当前公开 raw extraction，不能反向证明冻结包中的这 1,082 项来自同一日期或同一字节版本。2026-10-31 核查时，Kaikki 英语索引还列出 post-processed extraction date（2026-10-25）和 Wiktextract commit identifiers；raw-data 页面列出压缩文件与大小，但页面文本中没有 checksum 字段。这给出了可继续查证的候选快照描述，却不能将本地未知对象的 `raw-sha256` 摘要绑定到该快照。[Kaikki raw downloads](https://kaikki.org/dictionary/rawdata.html) · [Kaikki English dictionary index](https://kaikki.org/dictionary/)。Wiktionary 声明贡献者文本按 CC BY-SA 与 GFDL 发布，同时提醒外部来源内容可能有单独版权条款；这也不能替代逐记录来源和条款核验。[Wiktionary copyrights](https://en.wiktionary.org/wiki/Wiktionary%3ACopyrights)。

重放（输出必须是新路径）：

```powershell
python -m src.analysis.audit_t02_targeted_source_metadata --bundle ../OEWN --out outputs/t02_targeted_source_metadata_20261031_v2.json
python -m unittest tests.test_audit_t02_targeted_source_metadata -v
```

本机 ignored 聚合结果 `outputs/t02_targeted_source_metadata_20261031_v2.json` 的输入摘要：index `b24d7484aa4364f002c05b8a20687e266dcb7868ee97c241d10a2b28b69b4195`；scoped payload set `a18721c319f2deee70168deda60f4deb48f4f2a296975bcb3e36996900246852`。更新后的三项合成测试覆盖摘要格式识别、跨标签相同摘要检测、与定义文本哈希相等/不等判定、host 提取、标签筛选及摘要/私密字段不泄漏。该分析只补强来源可追溯性检查，不构成清权或定义语义验证。

### 5.2.4 来源证据字段对关系类型化的支持度（2026-10-31）

为判断当前冻结来源证据是否能直接支持 T02 的窄关系 schema，扩展只读审计器，仅统计每个 `source_evidence` 对象顶层键是否属于四组字段名：谓词/关系类型、论元/参与者角色、极性/否定范围、证据片段定位。审计不读取这些字段的值，也不访问定义、引文或 locator 内容。已有本地 ignored 输出 `outputs/t02_source_relation_field_coverage_20261031.json`，scope 与前述子集相同；5,625 条记录全部读取成功，3,645 个 evidence item 均未出现四组字段名，带 license/licence 键的 evidence item 也是 0。输入摘要与前述子集一致：index `b24d7484aa4364f002c05b8a20687e266dcb7868ee97c241d10a2b28b69b4195`，payload set `a18721c319f2deee70168deda60f4deb48f4f2a296975bcb3e36996900246852`。

此结果意味着目前不能仅凭冻结包内这些来源证据对象自动赋予“空间/位置、方向/路径、参与者角色、否定/缺失”等支持关系；规则转换应继续将证据不足关系标成 `unresolved`，不可从介词字符串或释义文本猜测标签。它不证明上游资源没有可用语义证据，也不替代逐来源 identity/release/rights 核验或独立人工定义保真审核。字段名匹配本身亦不足以证明正确性；若未来来源生产者补充显式字段，仍需核对字段语义、引用跨度和版本绑定，再进入人工审核。

审计器与合成测试为 `src/analysis/audit_preposition_source_provenance.py` 和 `tests/test_audit_preposition_source_provenance.py`；本轮 2 项单测通过。输出只含聚合数和输入哈希，位于 ignored `outputs/`，不上传仓库。复算时选用一个尚不存在的新输出文件名：

```powershell
python -m src.analysis.audit_preposition_source_provenance --bundle ../OEWN --out outputs/t02_source_relation_field_coverage_<new-run>.json
python -m unittest tests.test_audit_preposition_source_provenance -v
```

### 5.3 盲化、双标与仲裁（执行前需负责人确认）

- 两名审阅者独立标注；隐藏条件名称、机器结构统计、抽样层、另一名审阅者结果及训练/测试用途。
- 审阅者查看原始定义与允许访问的来源证据；呈现内容不泄露转换后的预期关系标签。系统以随机匿名顺序呈现，保存随机种子和呈现顺序。
- 同一原单元的多条件若在同一审阅者处逐条相邻呈现，会产生记忆和比较偏差；拟采用打散呈现并限制单次会话暴露，是否采用分离审阅者或间隔重复由负责人根据人力与盲化风险最终确定。
- 原始意见提交锁定后再比较。裁决者查看原文与双方理由，不看机器汇总和隐藏抽样层；保存双方原始标签、裁决和理由。
- 来源/授权缺失、哈希不一致、条件映射失败或泄盲属于流程失败，先暂停相关单元并记录；`cannot_determine` 是有效标签，不当作缺失或保真。

## 6. 报告指标与停止规则

结构表单独报告目标/分支变化、碰撞目标数与冗余分支数、新空分支数与涉及目标、未解析关系数、共同可达和全体可达指标，逐项写明分母。定义保真表报告每个维度和整体标签的加权比例及区间、双标分布/混淆与适用的一致性统计、无法判断率、失败与裁决比例。对四条件采用同一审阅单元的配对比较；不同 estimand 不混在一起。

发生下列任一情况时暂停确认性解释：来源或许可无法确认；原 occurrence/分支映射不一致；条件盲化失效；关系证据不足却被赋予支持类型；抽样权重或有效 source family 不足以实现预定精度；无法判断/流程失败超过预设限值。失败后报告未覆盖范围和原因，不用结构变化“抵消”定义信息损失。

## 7. PR 分解

1. **T02-1（本 PR）**：共享协议与字段 schema；仅文档，不处理真实图内容。
2. **T02-2（本 PR）**：`src/analysis/preposition_relation_records.py` 提供纯记录 validator 和只读四条件转换；合成测试覆盖分支/occurrence 引用、稳定次序、类型化关系证据与 unresolved 约束。不读真实 OEWN，不生成审阅任务包，也不从介词字符串推断语义关系。
3. **T02-3**：在许可审核通过后生成正式盲审抽样框和访问隔离流程；试标 40 条单独保存。
4. **T02-4**：只有独立双标、抽样计划和来源隔离冻结后，才做定义保真估计与结构结果并列分析。

本协议初稿只定义 schema，不含真实图变换或标注。后续来源字段与 frame overlap audit 是单独记录的聚合元数据计算；均未读取人工试标标签、未读取保留测试标签、未输出释义或生成分发包。后续实现需继续保持这些隔离。

## 8. 来源证据字段审计及其方法含义（2026-10-31）

对冻结包 `sources/Synset/alternative_or_definition_wsd_frozen/` 的来源索引执行只报聚合数的字段审计：5,625 条索引记录均成功解析，包含 3,645 个 source-evidence 对象；3,444 条记录有来源证据列表，669 条没有 evidence list，1,512 条没有 provenance。82 个精确来源标签中，审计到的 evidence 对象里许可证字段为 0；显式 predicate/relation type、argument/role、evidence span locator、polarity/negation scope 四组字段覆盖也都为 0。输入 SHA、计数及字段定义见本机 ignored 产物 `outputs/t02_source_relation_field_coverage_20261031.json`。

这只是对 source-evidence 对象顶层字段名的覆盖检查：没有读取字段值、释义、引文或 locator；字段缺失不能证明上游页面不存在相关材料，也不能证明记录的语义不正确。但它说明**当前冻结记录本身不足以直接支持**把 `prep` occurrence 自动标成空间、路径、角色或否定关系。故四条件的 `typed_relation` 必须逐项附带可复核的原始证据定位；没有定位时仍为 `unresolved`。来源标签与权利日志的规范化匹配只能找到待核查日志行，不能证明精确上游对象、版本、文本哈希绑定、许可兼容或独立来源家族。正式抽样和盲审材料仍暂停，直到可复算的记录级 crosswalk 和权利审查完成。

## 9. OEWN 原始释义与 `prep` 影响框重叠（2026-10-31）

新增只报聚合值的 `src/analysis/audit_t02_oewn_prep_overlap.py`，把已有 400 条 OEWN 2025 Plus candidate frame 与官方发布版 raw-gloss cross-check、冻结图规则连接。程序核验 frame SHA、发布版归档 SHA 和 400/400 raw-gloss exact-match 证据；只输出摘要计数与 SHA，不输出 sense ID、lemma、释义或标签。进一步按 cross-check 中 effective definition 是否精确匹配分层：376 条精确匹配；余下 24 条中，23 条不同、1 条为空。最新聚合结果在本地 ignored `outputs/t02_oewn_prep_overlap_v3_400_20261031_v2.json`，文件 SHA-256 为 `7afb0df27a42a8b2bb1b18b53413b42316efe7130535759385f48f63150428ea`。

此 400 条均来自 `random_stratified` panel，但抽样层是 POS × 原始释义长度 × 标点，不是 T02 介词影响层。全体 559 个源分支中，`prep` 主口径删除 748 个 occurrence、改变 443 个分支并影响 329 个 target；没有新空分支，5 个 target 出现非空分支碰撞。将 `prep_phrase` 并入后删除 750 个 occurrence、改变 444 个分支，target 影响数和碰撞数不变：敏感性口径额外改变 2 个 occurrence 和 1 个分支。effective definition 精确匹配的 376 个 target 中，306 个受 `prep` 影响（693 个被删 occurrence、408/516 个分支改变、2 个 target 有非空分支碰撞）；加入 `prep_phrase` 后该组再多 2 个被删 occurrence 和 1 个改变分支。其余 24 个 target 中，23 个受影响（55 个 occurrence、35/43 个分支改变、3 个碰撞 target），没有新空分支。该 frame 只证明 OEWN 原始释义和图结构干预可以联结，并揭示 effective 改写是需记录的分层变量；它不是 T02 目标总体抽样，不能将任何比例当作总体率或定义保真结果。

**分发状态与解释边界：**400 条候选 frame 的完整性 preflight 通过，但 `distribution_authorized=false`、`protocol_signed=false`、无外部预注册编号且无 annotation returns。不得分发现有 blind batch，也不得将其回填为 T02 的正式样本。40 条原诊断试标继续独立隔离。此次 audit 证明存在一个具有逐项 OEWN 2025 Plus 原始释义精确匹配证据的候选子集；正式 T02 样本仍须按负责人批准的精度、对比和工时要求，从目标总体重新抽样，并完成权利/归属及盲审流程门槛。

复算命令（在 `hypergraph_analysis_exploration` 目录运行；输出路径必须尚不存在）：

```powershell
python -m src.analysis.audit_t02_oewn_prep_overlap `
  --frame outputs/phase7/annotation_candidate_frame_v3_400.jsonl `
  --crosscheck outputs/phase7/oewn_2025_plus_release_crosscheck_v3_400.json `
  --bundle ../OEWN `
  --out outputs/t02_oewn_prep_overlap_v3_400_<new-run>.json
```

## 10. 全部 eligible OEWN 目标的释义来源与 `prep` 结构影响（2026-10-31）

新增 `src/analysis/audit_t02_full_oewn_prep_overlap.py`，在冻结图全部 eligible OEWN 目标上逐条校验来源 payload checksum 和 synset identity，再将同一记录的 raw/effective definition 与固定 OEWN 2025 Plus 发布包比对。随后扩展检查每条活动图分支的 `active_clause_sources`，验证分支数与规则分支一一对应、clause index 连续，且每个 source-document 引用均绑定至 checksum 和 synset identity 已核验的同目标 payload。脚本只写聚合计数及输入 SHA，不写 target ID、lemma、释义、标注或标签。带分支回链的完整 ignored 输出为 `outputs/t02_full_oewn_prep_overlap_lineage_20261031.json`，schema `/2`，SHA-256 `571937a72af641d606034cb39d45bb8d15ceff30245627ee1cb878d5d3fd8082`。

总体包含 104,907 个标准 POS（n/v/a/r）且冻结节点定义非空的 OEWN 目标；104,907/104,907 个目标都找到唯一的 `indexes/senses.jsonl` 身份行，并校验了 109,497 个唯一来源 payload 的包内 checksum 与 payload synset identity。104,886 个目标至少有一条 raw definition 与官方发布版释义精确匹配，21 个未精确匹配。effective definition 中 101,354 个精确匹配，3,553 个非空但不同；该结果是字符串来源匹配状态，不代表定义改写正确或错误。

**构造分支级来源回链结果：**104,907 个目标共含 145,991 条活动图分支、146,134 条分支—来源 payload 引用；每个分支的来源引用均通过同一 synset 身份和 payload checksum 核验。140,170/146,134 条引用的来源 raw definition 与固定发布版逐字匹配；140,109/145,991 条分支至少有一个 raw-exact 来源 payload。共有 101,753/104,907 个目标满足“每一条活动分支至少有一个 raw-exact 来源 payload”，另有 3,133 个整体 raw definition 命中发布版、但未达到逐分支覆盖条件的目标。effective-definition 口径对应 98,323 个全分支覆盖目标。由此，104,886 个整体释义命中不能直接当成所有分支均有释义来源支持的样本框；101,753 只是更严格的**候选覆盖总体**，不是已批准的盲审总体，也不证明分支语义忠实或冻结结构的许可已解决。

同一总体有 145,991 个原始 OR 分支。移除 `pos=prep` occurrence：删去 198,543 个 occurrence，改变 116,616 个分支，产生 358 个新空分支；84,976 个目标受影响，462 个目标出现新增非空分支碰撞，新增碰撞 excess 为 566。`prep_phrase` 敏感性口径相对主口径额外删去 303 个 occurrence、改变 85 个分支、增加 9 个新空分支和 1 个碰撞 excess；受影响目标从 84,976 增至 85,028。该分母不同于旧报告中包含非 OEWN 项目的 110,425 个全图节点，两个总体不可互换。

按 effective definition 字符串匹配状态分层后，精确匹配组有 101,354 个目标，其中 82,066 个受 `prep` 影响；非空不同组有 3,553 个目标，其中 2,910 个受影响。分层仅表明图上干预与来源字符串的重合，不能把 unmatched 解释为低保真，也不能由 matched 推断删去介词没有语义损失。

可在项目目录复算，输出须使用不存在的新路径：

```powershell
python -m src.analysis.audit_t02_full_oewn_prep_overlap `
  --out outputs/t02_full_oewn_prep_overlap_<new-run>.json
```

此全量审计补齐了结构影响总体分母、release-string overlap 和分支到来源 payload 的身份回链，却没有解决原始 provider/release/source family、结构来源权利、人工盲审或精度/工时决定。它不是定义保真实验，也不授权分发样本。下一步应在来源许可可确认的范围内建立 source-family/right crosswalk，再由负责人从合格覆盖总体中确定抽样框，并依据目标等权估计量与资源上限冻结独立盲审样本；没有可核实证据的关系类型仍标 `unresolved`。
