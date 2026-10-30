# 五线科研执行队列

更新日期：2026-10-31。此文件记录当前可执行工作、依赖、放行门槛和 GitHub 交付状态；科学问题和完整阶段定义以[五线总控路线图](research_program_roadmap_2026-10-30.md)为准。任务状态按实际证据更新，不代表项目完成比例。

## 全局决策和证据边界

总问题是：在相同可用定义信息下，完整概念构造中的 AND 联合条件、OR 替代分支和可复用中间概念，是否比原始释义及普通成对依赖关系，为机器理解和人类概念发展提供额外价值？

- 结构变化、定义语义保真、下游模型表现、人类认知解释是四类不同证据。
- 冻结 OEWN 只读；改写均输出为派生视图并保存输入摘要。
- 测试集标签不进入候选构造、训练、纠错或开发期调参。
- 用户已批准 T02 结构与定义保真并列报告、`prep` 主分析/`prep_phrase` 敏感性、窄关系类别和 unresolved、三轴加总体判断、40 条只作试标、目标等权汇总。
- 用户已允许工程 PR 在检查通过后直接合并且不强制一人批准；这不替代 T02 科学设计、许可或真实参与者研究的用户决策。

## 当前 GitHub 交付清单

远端 `main` 在本次核验时为 `2416f5f`。四个研究分支均已从本机推送后再次以 `git ls-remote` 核对：

| 支线 | 远端分支/提交 | PR 状态 | 下一步 |
|---|---|---|---|
| T02 | `codex/t02-sampling-precision` / `fe02bef`；schema dry-run `codex/t02-schema-dry-run` / `9e1ef8e` | 抽样框、分层成本和精度敏感性脚本已推送；PR 创建/查询接口仍返回 `Unknown tool`，尚无确认 PR | [打开抽样方案 PR 创建页](https://github.com/yizhibanmashou/concept-graph-research/pull/new/codex/t02-sampling-precision)；正式样本仍等待目标精度/工时决策 |
| T03 | `codex/t03-demo-task-audit` / `f4b0454` | 五任务验收文档及只读真实图 API smoke 已推送；PR 创建 connector 返回 `Unknown tool`，未确认 PR/CI | [打开知径验收 PR 创建页](https://github.com/yizhibanmashou/concept-graph-research/pull/new/codex/t03-demo-task-audit)；后续做来源内容人工回查与窄屏/键盘核查 |
| T04 | `codex/t04-structure-input-design` / `2bb56c5`（含 `38b5595`、`f679af7`、`ec24055`）；原形态并集分支 `codex/t04-morphology-candidate-union` / `afa2248` | 结构隔离设计、Conda/XPU 训练记录、合成关系 view checker 和硬件烟测已推送；PR/CI 查询接口仍不可用，#37 的 head/open/merged 状态未核实 | [打开结构设计分支 PR 创建页](https://github.com/yizhibanmashou/concept-graph-research/pull/new/codex/t04-structure-input-design)；另在 GitHub 核对 #37 与 CI |
| T05 | `codex/t05-data-feasibility` / `59edb70` | Wordbank schema/访问 gate 已补；PR 创建/查询仍返回 `Unknown tool`，尚无确认的 PR 编号 | [打开创建页面](https://github.com/yizhibanmashou/concept-graph-research/pull/new/codex/t05-data-feasibility)，创建后记录 PR 编号与 CI |

GitHub connector 本轮 `create_pull_request` 调用实际返回 `Unknown tool`；不是代码或远端 push 失败。工具恢复前，分支已经在线，PR 创建链接可直接使用。不得在报告里把远端分支说成 PR，也不得据此声称 CI 通过。

## P0：当前关键路径

### Q0 · 让 PR 队列可审阅（总控）

- **状态：** 等待 GitHub PR 创建/查询能力恢复，或仓库所有者从上表页面创建。
- **交付：** T02、T05 PR 编号；T04 #37 当前 head 与状态；每个 PR 的 changed files、CI/checks、review thread 和 merge 状态快照。
- **验收：** PR 的 head commit 与本表一致或有解释的后续提交；CI 结果核对到具体 revision；检查数据和忽略文件没有误入 diff；只有用户已授权且检查通过才执行工程合并。

### Q1 · T02 正式盲审前的设计 gate

- **已完成证据：** 冻结全图结构敏感性：`prep` 删除 623 个新空分支/633 collision excess；`prep_phrase` 单独删除 12/1；联合删除 638/634。schema v0 在 40 条试标样本完成 text-free dry-run，语义关系均 unresolved。
- **工作量复核：** 五个 prep 影响 strata 的目标/分支分别为新空 508/1,102、碰撞 501/1,599、两者 4/19、其他受影响 88,045/123,823、未受影响 21,367/27,663；六项合成测试与冻结图 audit 通过。高风险层仅占 0.918% 目标，分层抽样的人工成本不能用统一全图均值代表。
- **精度/成本情景：** 目标数 200 的假设分配下，三项 paired contrast simultaneous Hoeffding 半宽约 ±31.3 pp / 约 3,359 个 branch-condition-review 单元；约 1,050 目标约 ±10 pp / 12,774 个单元。单元数不等于人工小时；样本与每条任务时长仍未确定。计算脚本 `t02_stratified_precision_sensitivity.py` 三项测试通过，没有使用 40 条试标标签。
- **状态：** 结构描述可复现；正式人工保真尚未启动。来源总体、同一项目多条件的盲化呈现、置信区间精度与工作量仍待研究负责人审定。
- **下一步（不依赖标签）：** 对候选来源做许可/数据字段盘点；用目标数而不是分支数做精度/资源方案；设计随机匿名呈现、条件顺序/记忆控制和双标仲裁流程。
- **放行：** 只有总体、抽样概率、簇结构、最小精度目标、双人标注流程和来源许可明确后才抽正式样本；40 条 pilot 不进入正式分析。
- **停止：** 来源权利不明、无法来源家族隔离、presentation 方案造成明显泄盲或精度超出可用资源时，转为描述性结构论文，不启动确认性保真评估。

### Q2 · T04 当前 tiny 配置的决策关口

- **已完成证据：** SemCor 官方 train 内 13 文档隔离 dev，120 选中/111 可评分；XPU Conda `emotion_xpu` 上三种子 A/B/C/D 均值 24.02/24.62/27.03/24.62%；MFS 36.94%。D 对 B 配对净差为 0；对 C 为 −8/333。描述性审计发现 D 每目标每候选非 padding tokens 比 B 多约 18.1%。
- **状态：** 当前 tiny BERT 与输入序列化不支持完整结构有增益；样本小、同源、候选预算事后选择、长度不平衡，不能外推或证伪更一般假设。旧和新 dev 均不得再调参；测试分区未读。
- **下一步：** 已有 `t04_structure_isolation_design.md` v0.1 和纯合成关系 view checker；5 项测试证明节点/分支重排不变、B 丢弃分组、C 两两边投影会丢失高阶分支区分。checker 不读取真实图/语料、不含编码器。本轮在 `emotion_xpu` 中通过 512×512 XPU 矩阵乘烟测；运行时报告约 16.8GB，但不是专用显存测量。BERT-tiny corrected-context 三种子已经训练，现有同源开发集 A/B/C/D 汇总 24.02/24.62/27.03/24.62%，D−B 为 0；这是复用开发集上的探索结果，不是独立结论。新结构隔离 v0.1 的真实图只读 coverage/token/sparsity 审计仍等待负责人对审计对象和评估来源确认；确认后再冻结 estimator 和实现对照，当前不动测试集或在旧 dev 调参。
- **放行：** 数据许可、候选映射、独立开发来源、模型权重/硬件、预算、强基线、主要估计量和停止规则全部冻结。
- **停止：** 若无法建立输入信息公平对照或拿不到独立开发来源，停止 tiny-BERT 结构增益宣传，保留负面试点作为工程/方法结果。

## P1：并行支线

### Q3 · T01 ToLogic 人工语义审阅准备

- **已完成：** 六例共 455 个候选、want 单分支 130 个候选；重放和接口审计证明工程候选生成可复现，但没有独立 gold 或语义准确率。`without` 是用户提供的外部接口，不属于 85 basis。
- **下一步：** 固定审核指南，明确候选是否满足目标义项、参与者/角色、否定/缺乏、额外含义、证据定位与“不确定”；用已有 20 条 want 样本做流程试标而不估计准确率；记录审核者意见和仲裁分开存放。
- **放行：** 至少两名独立审核者可按手册一致使用“不确定”；新测试案例按义项/构式家族留出。未经用户或老师批准，不把自动排序结果当 gold。
- **停止：** 释义来源或审核员时间不足时，只报告枚举、绑定和接口覆盖，不训练/调参排序器。

### Q4 · T03 知径现有 Demo 的任务化核查

- **已完成：** 新增 `concept-dictionary/docs/task_based_evaluation.md`，定义义项搜索消歧、定义与来源、AND/OR 多步、循环/缺失、介词方向/否定五类任务和功能/认知两类证据门。后端 14、前端 9 项测试通过，构建通过；格式检查因两份未改的 TSX 文件失败。对冻结指纹 `6a26db5d…` 本机只读 API smoke：square 搜索返回72候选并含多个不同 POS/sense，square/about-1/in-5 共8分支均标记 source available；指定 `in-5 → oewn-04937655-n → in-5` 返回 cycle。未人工审阅来源释义、未开浏览器、未招募用户。分支 `codex/t03-demo-task-audit` / `f4b0454` 已推送。
- **下一步：** 逐条回查来源文件的实际文本与目标义项/依赖 occurrence；重点记录 square 案例已知的 `right` 义项风险。再做浏览器端窄屏、键盘可达性和真实 UI 任务核查；原协议 Gate C 的理解/学习研究须先经伦理、同意、隐私和样本设计批准。模拟与 API 通过不等于理解效果。
- **放行：** 每个界面解释能回溯目标、完整分支和依赖 occurrence；错误与边界状态有可见说明。用户体验确认后，才讨论小规模访谈/学习任务。
- **停止：** 只有功能模拟时，仅报告路径展示正确性与可用性风险，不作“用户学会/理解”的主张；未获伦理、同意和保存方案，不招募真实参与者。

### Q5 · T05 外部数据盘点

- **已完成：** 官方 Wordbank、CHILDES/TalkBank、Brysbaert–Biemiller 页面审查；Wordbank 官方 Data 页及 datapage schema 源码核对出 child/word/child-by-word 粒度、item 字段和 `datasets.license`，未下载儿童级响应。见 [T05 可行性文档](https://github.com/yizhibanmashou/concept-graph-research/blob/codex/t05-data-feasibility/hypergraph_analysis_exploration/docs/t05_data_feasibility_2026-10-31.md)。
- **下一步：** 完成 Wordbank 英语工具、表单、年龄范围、item 定义、逐数据集 license 和固定 release 表；schema 暴露 Redivis API token 依赖，本轮未尝试从本机凭证获取访问。向 AoA 权利方确认数据访问与衍生义项映射权。CHILDES 只筛选许可证明确且时间密度合适的具体语料。
- **放行：** 每个 dataset/corpus 有明确版本、访问权、license、单位定义和可再分发限制；义项映射指南和 source/lemma split 先冻结。
- **停止：** 没有合法可用的义项级数据时，继续报告图计算性质；不把词形 norm 冒充义项习得，也不使用未授权第三方副本。

## P2：跨支线综合与最终判定

1. **统一概念接口**：为 T01/T02/T04 的义项、依赖 occurrence、角色、否定和完整分支设稳定术语及公开 schema；不把构造边解释为逻辑蕴涵。
2. **结构信号对语义结果**：T02 获得独立保真标签后，比较被删/边界保留/关系类型化差异；必要时作为 T04 输入信息控制，而不是直接复制 POS 删除结果进模型。
3. **外部验证**：T04 的独立来源结果与 T05 许可通过的预测分析分开报告；人类认知结论需真实发展测量或行为数据。
4. **总假设判定**：按每条证据级别逐项回答“支持/反对/证据不足/资源不允许”，允许结论为负或有条件有效；不得用一个方向的结构收益替代另一个方向的语义/认知验证。

## 每轮执行日志模板

每次阶段更新至少补齐：

```text
日期 / 当前分支和 head：
研究问题 / 假设：
数据版本、许可、文件摘要：
协议和偏离：
命令、环境、随机种子：
分母、覆盖、失败/排除：
结果和不确定性：
错误分析与不能推出的结论：
PR、CI/head、review、merge 状态：
下一步、前置 gate、负责人：
```

状态仅允许：`ready`、`in progress`、`waiting for user decision`、`waiting for data/access`、`done`、`stopped with reason`。被推送的分支不等于 PR；CI 未查到具体 head 不等于通过；试标不等于正式样本；新模型不等于有效结果。
