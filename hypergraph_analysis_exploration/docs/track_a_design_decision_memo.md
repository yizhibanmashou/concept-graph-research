# Track A 设计裁决备忘录（Phase 153）

状态：**建议稿，未获研究者确认、未注册、未生成数据或改变 schema。**

本备忘录把 Phase147 的四个未决选择放进一个共同 estimand、抽样和校准框架内。选择要在标注前冻结，因为事后分析不能修补伪重复、上下文泄漏或条件标签混用。

## 研究问题与两个分离的测量对象

Track A 应分开回答两个问题：

1. **规则来源忠实度（主研究问题）**：给定固定 OEWN child sense 和候选 parent relation，该关系是否被 raw gloss 中可定位的原文证据直接支持？证据单位是 child sense–parent synset 的 relation edge，evidence span 只以冻结 raw gloss 字节/Unicode 码点为基准。若未来测试自动从 gloss 抽取规则，还要增加未由资源 hypernym edge 预筛的候选/负例，否则只能估计“被选中资源边中有多少受释义支持”，不能声称提取精确率/召回率。
2. **NLI 表达与上下文（次级模型评测）**：对每个 exact premise × hypothesis，模型输出的 entailment/neutral/contradiction 是否符合人工裁决？NLI relation gold 依赖具体 premise 条件，不能从一个条件自动复制到另一个条件，也不能替代 raw-gloss semantic-support gold。

这两个对象对应不同单位、标签和误差来源。NLI rationale、validator 通过或资源边存在都不能充当 gloss-span source-support 标签。

## 四项建议裁决

### 1. Parent lemma surface 范围：保留全部 surface，按 edge 嵌套

建议沿用 Phase147：每个 parent synset 的每个 lemma surface 独立形成 exact hypothesis 候选，并绑定 `relation_edge_id=(child_synset,parent_synset,hypernym)`。不得把词典序首项称作 canonical，也不合并 lemma 列表成一个模型句子。

理由：不同 surface 可改变歧义和句法自然度；只抽一项会把未定义的词面选择策略混进测量。成本上限仍是 680 surface rows，而不是 322；同 edge 的 surfaces 是重复/嵌套观察，不是独立 relation edges。

### 2. NLI gold 范围：逐 exact condition 独立标注；另建 relation-level source-support gold

建议对 `lemma_pos_gloss_v1` 和 `raw_gloss_v1` 两种 premise 各自裁决 exact pair 的三分类 NLI relation。若每个 surface-condition 两名独立标注者，最多是 1,360 rows、2,720 份判断。`semantic_support` 则在 raw gloss 上针对 relation edge / typed literal 独立标注 span 与支持关系；不是另一份 NLI 标签。

理由：这样模型在两种条件下的结果能对应各自输入，条件间 accuracy 差异可解释为呈现条件差异；同时主研究仍直接测量“释义 span 是否支持规则”，而非把 NLI 当作来源证明。标注者不得用 OEWN edge 的存在代替文本裁决，资源关系只作为候选来源和分层变量。

### 3. Primary estimand 与校准：目标义项等权的条件差异；按泄漏连通组处理不确定性

建议预注册以下次级模型 estimand：对同一 exact surface pair 计算两个 premise 条件下模型预测是否匹配该条件的人类 NLI gold；先在每条 relation edge 内平均其 surfaces，再在 child sense 内平均多个 parent edges，最后对 target senses 等权平均，比较 `lemma_pos_gloss_v1` 减去 `raw_gloss_v1` 的准确率差。报告逐 surface、edge、sense 的分层结果，避免让 680 行隐式压过 322 个 edge 或多 edge 的 target。

拆分与区间估计按 Phase145 的 lemma/sense/edge 连通泄漏组分组；同组不得跨 train/dev/test。当前草案有 279 个连通组，真实数量须在 hypothesis 和 split policy 冻结后复算。主不确定性区间以该连通组为 cluster 重采样；它是保守的依赖处理单位，不代表组间统计独立已被证明。

现行 certified NLI selector 的 dev 约束是每个 `group_id` 恰好一行并依赖 IID 单位，不能直接套用 680 surface rows。未来有两条可选路线：实现并验证明确的 cluster-aware calibration/risk procedure，或者把 NLI 作为描述性次级评估、暂不声称有校准风险保证。不能只把 `group_id` 改名或在每组随意挑一行来伪装 IID。

### 新近 selective-risk 方法先例（Phase 154）

Salem et al. 的 [HG-CRC](https://arxiv.org/abs/2607.24562) 给出了按用户定义分层同时约束 selective risk 的方法先例：节点阈值、Bonferroni 同时控制、leaf-first fallback，并比较 split 与 residual/in-sample calibration。该文的形式保证仍基于 IID calibration examples + independent test point；它的 group hierarchy 是分层 membership，不是相关 pair/surface cluster 的稳健推断。因此可作为未来“是否需按 condition/POS 子组控制 precision risk”的 adapted baseline，但不能直接证明当前 680 surfaces 满足独立校准，也不构成 WordNet NLI baseline。完整假设和项目接口映射见Phase154与[日志](../sources/literature_screening_log_2026-10-08_hierarchical_group_risk_control.json)。

### 4. Verb grammar：第一轮 noun-only，verbs 保留为后续独立扩展

建议第一轮只纳入适用且模板经人工预审的 noun edges；58 条 verb edge 暂不生成正式候选。动词短语常含补语、粒子与论元结构，`To {child} is a more specific way to {parent}` 可能不自然或改变真值条件；noun 模板也要审查冠词、复数、multiword 与 mass noun。

这缩小第一轮可推广范围，但降低 hypothesis grammar 混淆。须在未来报告中明确结果只适用于 noun subset；verb 另行设计模板、做小规模独立自然度/语义预试后才加入。

## 盲化、标注与随机化建议

- 采用成对条件比较，但同一标注者不应连续看到同一 exact pair 的两种 premise，以减少记忆/对照泄漏；把 pair-condition 分派给不同标注者，并在 relation edge、POS、标注批次内平衡/随机化。
- 每个条件的 NLI 判断由两名标注者独立完成，先锁答案再做 adjudication；标注者对候选来自 OEWN hypernym 的身份盲化。source-support span 标注独立于 NLI 判断，允许多个支持 span/无法支持/歧义，并保留分歧记录。
- 记录标注者 ID、批次、呈现顺序、条件、盲化版本、停留/弃答（若采集）和 adjudication 轨迹。任何统计分析要反映同 target sense、edge、surface 的嵌套，以及连通组级数据拆分。
- 样本量和双标成本在 noun-only frame、标注协议、最小实际关心效应与 IAA 指标定好后作 power/precision 分析；680×2 条件是全量上界而不是必要样本量或充分 power 的证明。

## 对系统实现的影响

确认上述方案后才可建立新版本的数据契约。至少需要分别哈希 raw gloss 与 rendered premise、记录 renderer/condition 版本、保存 source-span 坐标、parent synset/relation-edge/surface identity、分开的 split-leakage group 与统计单位；同步升级 candidate freezer、manifest/sidecar validator、NLI exporter/evaluator 和 strict route。旧 `/0.1` record、manifest `/0.2`、export `/0.2` 必须保留并可回放。

此备忘录不批准 schema migration 或标注分发，也不证明该研究设计新颖/有效。必须先获得研究者对 estimand、样本范围、标注责任、登记与来源许可的确认；实施后再做针对性验证和功效/精度规划。

## Phase187：固定 release 候选总体的只读核定

新建的[OEWN hypernym candidate inventory builder](../src/analysis/build_oewn_hypernym_candidate_inventory.py)在 v3 锁定 target IDs 与 pinned OEWN 2025 Plus archive 上枚举直接普通 hypernym：400 个 target 中 310 个有直接 hypernym，共 322 条 edge、311 个 parent sense。所有 parent lemma 按 edge 展开得 680 个 edge-surface rows；parent-sense surface memberships 为 663（跨 sense unique 字符串 646）。child lemma surface 只独立记账，不与 parent 做笛卡尔积。此清单无 gloss、hypothesis、labels、splits 或 strata，不决定本备忘录中的研究单位、标注范围、NLI condition 或统计方案；也没有修复锁定 v3 的 1 条 POS 和 1 条 lemma-set mismatch。机器结果与限制见Phase187 深度报告和[replay audit](../sources/oewn_hypernym_candidate_inventory_audit_2026-10-08_phase187.json)。

## Phase188：候选表面政策的工作量敏感性

固定底表有 322 条 edge，其中 noun 264 条/507 parent surfaces，verb 58 条/173 surfaces；310 个有边 child senses 中，298 个有一条直接 parent edge，12 个有两条。按 Phase153 两个 NLI premise 条件和双标建议估算，若每 edge 选一个尚未指定的 child lemma surface，NLI 为全 POS 1,360 rows/2,720 判断，noun-only 1,014/2,028；若 child 的所有 surfaces 都与所有 parent surfaces 组合，则为 2,212/4,424 与 1,682/3,364。该差异意味着 child lemma policy 是实际协议选择，不能由实现默认值决定。情景计数不是 power、有效样本量或必要工作量。详见Phase188 深度报告及[aggregate audit](../sources/oewn_hypernym_candidate_workload_audit_2026-10-08_phase188.json)。
## Phase191：identity mismatch 对 Track A 候选面的影响

POS mismatch 不在任何 direct-hypernym edge 上，故当前 noun-only edge 数和 parent-surface 数不受影响。lemma mismatch 位于一条 noun edge；按 frame lemma 列表计算比按 pinned-release surface 少 1 个 child×parent combination。若协议取每 edge 一个 child surface，行数不因 lemma membership 数量而变；若取全部 child surfaces，则全 POS 情景是 1,105 vs 1,106 pair combinations（差异仅针对当前 mismatch）。现有来源记录中该 sense 有两个 lemma-list variants，无法由计数判断应采用哪一个研究语义。新候选 surface 按本备忘录既有的 pinned-release 口径，不回写锁定 v3 frame；在协议锁定前不渲染 hypothesis 或创建标注任务。证据见Phase191影响审计。

## Phase202：实施接口只读核对

静态代码核对表明现有 OEWN edge/surface inventory、claim-review pair manifest 与单义项 blind importer 是三个不同数据合同。即使它们的哈希/冻结模式可复用，也不能直接代表 relation-edge source-support gold 与逐输入条件 NLI。实施前仍需裁决 source-support 单位与 surface 汇总、exact-condition NLI、child/parent surface 范围、POS/template 和 statistical/calibration unit。此记录不批准 schema migration 或 candidate generation。接口字段对照见Phase202报告和[机器审计](../sources/track_a_implementation_compatibility_audit_2026-10-08_phase202.json)。
## Phase219：独立 Track A v1 设计草案

本备忘录的建议仍未被研究负责人裁决。Phase219 将其整理为完整的[Track A v1 设计草案](track_a_protocol_v1_draft.md)，补入**source-support 的 edge-population estimand**与 child-sense PSU 权重、condition-paired NLI、surface 嵌套和四人 balanced-incomplete-block 标注分配；NLI 条件差本身仍按本节建议采用 target-sense-equal 主估计量，并报告 edge-population sensitivity。Phase236 对齐了 v1 中一处曾把 NLI 主 estimand 写成 edge-population-weighted 的不一致，但没有改变待决状态，未生成 pairs、labels、splits 或 schema；Phase218 所列许可、签署与启动 gate 继续有效。详细 rationale、精度边界与机器设计记录见Phase219报告、Phase236一致性审计及[Phase219结构化记录](../sources/track_a_protocol_design_review_2026-10-08_phase219.json)。
