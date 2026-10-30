# T05 认知发展：外部数据可行性与执行路线

审查日期：2026-10-31  
状态：桌面数据源审查与研究设计；尚未下载数据、接触参与者或取得义项级结果。  
核心问题：词典构造中的联合条件、替代分支及可复用中间概念，能否在控制词频、词性、具体性及普通语义网络特征后，为儿童词汇/义项发展提供可复现的增量预测信息？

## 1. 先界定能回答的问题

T05 不能把以下指标混成一个“概念习得年龄”：

1. **词形词汇表现**：家长报告儿童是否理解/产出某个 CDI 项，随年龄如何变化。
2. **义项知识表现**：儿童是否知道某个特定词义；同一词形的不同义项可以不同。
3. **语境使用**：儿童在自然对话中何时、如何使用一个词形；出现一次不等于理解全部义项。
4. **构造图性质**：一个目标有多少联合分支、中间概念复用、构造深度或可达性。

图结构是待检验的预测特征，不是人类概念系统的直接观测。模型预测如果成立，首先是外部预测关联；没有纵向识别或行为实验，不应写成图结构导致儿童更早习得。

## 2. 数据源审查

| 数据源 | 可用观测与潜在价值 | 与 OEWN 义项对齐的困难 | 访问、许可与风险 | 当前决定 |
|---|---|---|---|---|
| Wordbank / CDI | CDI 是家长报告的早期词汇理解/产出量表；官方数据页提供 child、word、child-by-word 三种层级及不同年龄、人口学/工具信息。适合估计**词形/问卷词项层面**年龄曲线，可作为 B+C 外部预测的次要任务。 | CDI item 不自带 OEWN sense key；`uni_lemma` 是跨语言条目的概念性 gloss 映射，不是 WordNet/OEWN synset ID。家长报告的词项掌握不能证明儿童只知道一个义项。复合词、变体、同形异义词、具体问卷措辞均需核查。 | 官方页面说明数据可免费下载且 Redivis 版本化；具体数据集许可由 `datasets.license` 字段区分，主页默认 CC BY 4.0 不覆盖标为 CC BY-NC 的条目。当前公开说明未确认登录要求，获取时再核实。 | **可先做许可与词项元数据盘点；** 若用于可公开研究，固定 Redivis release、工具版本、逐数据集许可、CDI 表单版本。结果只能称词项层面，除非另有义项标注。 |
| CHILDES / TalkBank | 自然会话转录、说话者年龄/对话语境和纵向语料可能帮助人工判断语境中的词义使用，或分析词形表达出现轨迹。 | 语料记录词语使用，不直接测量理解或习得；单次首现受采样、对话机会、转录和家庭差异影响。需按语境人工映射到 OEWN 义项，并保存不确定/多义情况。纵向且可比的样本可能较小。 | 官方说明有公开网页、注册后数据、受控数据三个访问级别；大多数转录需注册，部分语料/媒体受控。TalkBank 一般规则为 CC BY-NC-SA 3.0，除非具体语料另有规定；不应把原始转录、个人信息或不可再分发内容上传 GitHub。 | **暂不下载。** 若走该路，先选一个具备明确语料级许可、年龄元数据及足够纵向密度的语料，提交数据保护与用途审查，再做本地-only sense coding feasibility pilot。不能以 transcript 首现替代理解年龄。 |
| Brysbaert & Biemiller 2017 / Living Word Vocabulary | 论文描述约 44,000 个词义、来自 31,000 多个词形/多词表达；以儿童不同年级的知识测试构造 test-based AoA，是当前最接近**意义级**的公开常用测量路线。 | 测试记录与 OEWN synset 不一定一一对应；原始词义拆分、定义和图义项粒度不同。需检查同词多行、词性、多词表达、测试来源及空缺。 | UGent 论文条目将出版物版权状态标为 “No license (in copyright)”。第三方文件或 R 包中的许可声明不足以代替权利人/官方来源确认；数据的再分发及衍生映射权利目前未厘清。原指标是年级测试标准，不是幼儿首学时间。 | **科学问题匹配度高，权利门槛未过。** 先核对官方数据可取得方式、逐字段授权和许可；未确认前不抓取、镜像、提交或据第三方 CSV 建模。即使获准，也只能称年级测试知识/AoA proxy。 |

来源与可核事实：Wordbank 当前主页说明其 CDI 数据规模、家长报告性质及默认许可；FAQ 说明 Redivis 版本/下载方式、CC BY 与部分 CC BY-NC 的差异。[Wordbank](https://langcog.github.io/wordbank-datapage/), [FAQ](https://langcog.github.io/wordbank-datapage/faq.html), [Data page](https://langcog.github.io/wordbank-datapage/data.html)。CHILDES 的访问分级和 TalkBank 使用规则见[官方访问说明](https://talkbank.org/childes/access.html)与[版权/使用规则](https://talkbank.org/0share/rules.html)。Brysbaert & Biemiller 数据规模、论文和权利字段见[UGent 官方书目条目](https://biblio.ugent.be/publication/8535511)；其“年级测试测得的词义知识”定义也应以原文为准，而不能简写成幼儿首次习得时间。

### Wordbank 官方字段核查（2026-10-31）

当前官方 [Data 页面](https://langcog.github.io/wordbank-datapage/data.html)确认三类导出粒度：child-level、word-level、child-by-word（长表或宽表）；均可按年龄、工具、规范样本标记及页面列出的人口学字段筛选。word-level 表给出 `item_id`、`item_kind`、`item_definition`、`category`、`uni_lemma`、`age`、`n_children`、`prop_produces`，Words & Gestures 表单另可有 `prop_understands`。child-by-word 长表包含匿名 `data_id`、月龄 `age`、人口学字段和 item 字段，并记录 `produces`；理解响应只适用于支持理解测量的表单。首轮分析必须固定表单与测量类型，不能把结构不同的问卷版本直接拼成同一响应变量。

`uni_lemma` 的官方说明是供跨语言轨迹使用的跨语言概念性 gloss，对应 items 表中的统一 lemma；它没有被说明为 WordNet/OEWN synset 编号，也不解决多义词词义划分。因而 Wordbank 可用于词形/问卷 item 层的词汇轨迹或预测，不能单独回答“某个 OEWN 义项何时习得”。从 item 到 OEWN 的映射应另建、报告覆盖与歧义，并将未匹配和一对多项保留为显式状态。

数据页指向版本化 Redivis 当前 release，要求记录数据集版本；当前 contributors 页面注明其所列 datasets 表构建于 2026-10-20。许可应按选中数据集的 `license` 字段核查并按该数据集的相关论文引用。数据页还注明 Elison English (American) WG 当前暂不出现在 word-level/常规导出视图，因其 item 导入问题仍在处理，但数据仍包含于 Redivis；因此元数据盘点必须区别“未显示/导出”与“数据不存在”，不可据此把该问卷当作覆盖为零。此审查只读取公开页面，没有下载或导出响应数据，也未登录 Redivis。

官方 [datapage 源码仓库](https://github.com/langcog/wordbank-datapage)的 schema 文档把核心表粒度说明为：`instruments` = language × form，`datasets` = contributed dataset（含 `license`），`administrations` = child × test，`items` = item × instrument，`item_responses` = administration × item。官网当前 contributors 构建从 `datasets` 表展示 language、form、dataset name、contributor、citation、license、administration 数；当前页面不在静态 HTML 中列出全部行。源码说明这些核心表从 Redivis 加载，程序化取表需要 Redivis API token。因此本轮可以确认字段和获取路径，但没有逐数据集许可、英语 form 及 n 的清单；没有用户授权的 Redivis 访问时不得从本机凭证推断权限。后续只需获得官方公开页面可见的元数据或经用户授权的只读访问即可完成这张清单，不需要提取 child-by-word 响应表。

### 官方页面复核与变量使用限制（2026-10-31）

本轮重新核对 [Wordbank Data 页面](https://langcog.github.io/wordbank-datapage/data.html)、[FAQ](https://langcog.github.io/wordbank-datapage/faq.html) 和[贡献者清单](https://langcog.github.io/wordbank-datapage/contributors.html)：

- 当前贡献者清单标注其 `datasets` 元数据构建于 2026-10-20，要求记录 Redivis release/download date 并引用所用数据集的相关论文；若使用 full English dataset 可引用 Wordbank 数据库，normative English data 还应引 Fenson et al. (2007)。此规则不能代替逐项目 license 字段核对。
- 官方 Data 页面明确：by-word proportion 把 missing responses 当作 negative；`prop_understands` 只对包含 comprehension 的 Words & Gestures (WG) form 可用，其他 form 只提供 produces。若建模比例或行级响应，必须固定 form/measure，报告 missingness 及这个计分口径；不能把“缺失”解释成经过观察的“不理解/不产出”。
- Elison English (American) WG 因 item 导入问题暂未进入 word-level views 和常规 exports，但仍在 vocab norms 与 Redivis 数据集中。候选清单应标为“该视图暂缺/需查 Redivis”，不能算作零覆盖。
- FAQ 说明英文 CDI form 可向 Brookes Publishing 购买；数据集可用许可不代表可以将问卷全文、题项或量表材料复制进本仓库。后续仓库只保存 item ID、必要的非版权元数据、映射状态和许可允许的聚合结果。

Brysbaert–Biemiller 的 [UGent 官方书目记录](https://biblio.ugent.be/publication/8535511)说明论文讨论的是来自 Living Word Vocabulary 的约 44,000 meanings、31,000 多个 word forms/多词表达的测试知识估计；该记录列出的下载是论文 PDF，并标 `Copyright statement: No license (in copyright)`。因此，开放获取论文可读不等于原始 Living Word Vocabulary 行数据可自由复制或再分发；当前仍没有行级数据许可/获取证据，义项级 AoA 映射保持停止状态，需由权利方确认。

TalkBank 当前[官方访问等级页](https://talkbank.org/0share/access.html)区分 open access、registration required、approved access 和 controlled access；具体 CHILDES corpus 的注册要求和许可需逐语料检查。通用 [TalkBank 使用规则](https://talkbank.org/0share/rules.html)注明默认 CC BY-NC-SA 3.0，除非该语料另有说明，并限制受控/可识别材料的存放与分享。不能只用“CHILDES 是公开数据”作为整个语料集的授权结论。

上述复核仅读取公开页面与论文书目信息，没有导出 Wordbank 响应、儿童级记录、CDI 题项或 TalkBank 转录。逐 dataset 的 license、form 数量、管理数及实际访问等级仍需单独清单。

## 3. 路线选择：B+C，不把词形结果伪装成义项结果

### B：可计算的外部预测

优先顺序不是“先把大数据下载下来”，而是先确认目标测量与权利：

1. **低风险元数据盘点**：在不下载/保存响应级数据的情况下，列出 Wordbank 英语工具、年龄范围、item 定义、各数据集 license 和 Redivis release 元数据；给出覆盖清单及未覆盖原因。Wordbank 若可用，第一轮明确为词形/问卷项预测，而非义项预测。
2. **义项级可行性决策**：并行向数据权利方核实 Brysbaert–Biemiller 原始行数据的合法访问与衍生映射许可。若允许，再做受控词义到 OEWN 对齐；若不允许，T05 的义项级预测暂缓，不用未授权副本替代。
3. **词形到义项映射**：先定义一对一、多个 OEWN 义项、一个外部项目对应多个义项、multiword expression、POS 冲突、无匹配和不确定等标签。至少双人独立映射并保留分歧；训练/验证/测试按词形家族或定义来源分组，避免同一 lemma 的不同义项跨 split 泄漏。
4. **冻结样本和基线**：在查看模型结果前固定纳入规则、有效样本数、评估 split、指标及停止规则。外部基线至少包含年龄/年级、词频/儿童定向语料频率、具体性、词长、词性、polysemy，以及可得的普通语义网络距离/中心性；加入 hypergraph 的 basis 可达、分支数/大小、复用和深度特征。只在训练 split 内标准化/选择特征。
5. **增量评价**：优先比较 baseline 与 baseline+构造特征的来源/词形家族隔离预测；报告外部测试上的绝对指标与增量、置信区间、校准和分层误差。若使用 Wordbank 年龄响应，需尊重儿童/问卷层级，采用分层模型或适当聚类估计，避免把每个 item×age×child 响应当独立样本。年级 AoA 可作为序数/区间目标，不应无依据换算为精确月龄。

### C：计算性质与认知证据分开

现有复用缓存模拟可继续作为图的计算性质分析；下一步应强化 source-/POS-/degree-preserving null、根顺序和图版本稳健性。它提供的是“结构在指定算法下能否节省搜索状态”的计算证据。与 Wordbank/CHILDES/AoA 的外部预测结果并列，而非合成一个认知分数。若未来需要因果发展主张，应另立有时间顺序、机会暴露测量和适当控制的纵向/行为研究方案，并由用户审定伦理与参与者流程。

## 4. 分阶段里程碑与交付门槛

| 阶段 | 交付 | 放行条件 | 停止/降级规则 |
|---|---|---|---|
| T05-A 数据盘点（当前） | 本文件；源、release、项目/语料 license、单位、年龄范围、sense-ID 支持表 | 信息来自官方页面或权利方；日期与链接可追溯；不保存响应级数据 | 许可项不明确时保持 blocked-for-data，不下载或上传 |
| T05-B 对齐 pilot | 本地受限、小样本、双人词形/义项映射及歧义记录；只提交空 schema/聚合覆盖 | 数据权利确认；样本纳入规则与映射手册冻结；来源字段和撤回/删除条件清楚 | 映射可靠性不足、样本有效义项数不足或来源无法分组，则不进入建模 |
| T05-C 外部基线 | 可复现 baseline、数据 split manifest、特征字典、预测分数和错误分析 | 锁定评价指标/区间；按 lemma family/source 分组；测试仅一次用于结论 | 模型只拟合词频/语义网络即可解释结果时，如实报告无增量 |
| T05-D 构造特征增量 | baseline vs baseline+超图特征；独立 source/lemma-family 预测 | coverage、license、split、missingness 与有效样本精度过关 | 增益不稳定或区间不支持有意义改进，则停止该特征方案 |
| T05-E 认知解释 | 可审计的受限结论或新的行为实验协议 | 独立发展测量支持；区分预测、描述、因果；用户批准参与者研究 | 仅计算模拟或词形级报告时，不得写成儿童义项习得机制 |

**下一项可自主执行工作**：在不读取任何本机 token 的前提下，判断 Wordbank 官方页面/API 是否能匿名读取 dataset 表的纯元数据；如不能，则继续保留逐 dataset license/form/administration 清单为 waiting-for-access，不尝试账户授权。并核实 Living Word Vocabulary 原始行数据的权利方获取途径；只形成覆盖与访问可行性，不下载响应级数据。**当前用户决策 gate**：是否接受 Wordbank 词形层面结果作为独立的次要预测任务；不论回答为何，它都不能代替义项层面问题。

## 5. 复现、隐私和 Git 约定

- 数据下载和含儿童级响应/对话文本的结果只留在有许可的本机 ignored 目录；Git PR 仅包含协议、空 schema、可公开脚本和汇总统计。
- 每个数据 release 记录官方版本、访问日期、license、下载/过滤代码、文件摘要、表格粒度、纳入数、映射覆盖率及排除原因。
- 不保存 API token、Redivis 登录缓存、儿童姓名/生日、原始转录或可回溯个人身份的信息到仓库；下载需要账户授权的材料时不尝试从本机凭证推断许可。
- 真实参与者研究、未成年人数据收集、招募或联系学校/家长，均不属于自动执行范围；需要伦理/机构流程和用户明确决定。

## 6. 本 PR 的边界

本文件是数据可行性研究计划，不报告任何新的人类数据实验，也没有新下载数据。它适合单独审阅和合并；后续获取数据应另开 PR，先处理授权与空 schema，再处理不含原始响应的分析代码。当前已有的图缓存模拟数值仍详见总路线图和本地总报告；不能将模拟复用率写成习得年龄预测成果。
