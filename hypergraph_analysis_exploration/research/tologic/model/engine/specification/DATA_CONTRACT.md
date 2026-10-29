# V3 数据契约

实现共享字段见根目录 [IMPLEMENTATION_CONTRACT.md](../IMPLEMENTATION_CONTRACT.md)。规则以 [RULES.md](RULES.md) 为准。

`sources/items/<synset_id>.json` 保存 `v3.source/1`：原文 definition、lemmas、冻结 basis 身份、occurrences、evidence、provenance；附 `raw_wsd` 保留旧 WSD 原始记录。occurrence 的 start/end 是 definition 原文的 Python Unicode 字符区间，左闭右开。无法证明该区间时不猜测；写入 blocking_issues。

原文中的 a/an/the 可以建立 `kind: article`、`synset_id: @syntax:a` 或 `@syntax:the` 的语法定位记录；它们不是补造的词义，也绝不是 callable provider。all 必须使用已有固定 WSD 身份。允许确定性坐标规范化：表面词精确匹配、大小写/Unicode 规范化、已记录 lemma 的唯一匹配、旧定义分支在原文中的唯一顺序投影。仅在已有分支出现完全一致 token 时，允许固定 lemma 的规则 -ing 词形桥接。全部保留原始表面词/lemma/part_id/对齐方法，不运行新的 WSD、广义词形猜测，不使用 B 句坐标或有歧义的重复匹配。

basis 的依赖 WSD 分支冲突不阻止其内部 primitive 实现起步，但冲突跨度的全部候选必须从可调用 occurrences 禁用，保留 disabled_dependency_occurrences 与 raw_wsd，不能默选第一条。相同问题在非 basis 仍是阻塞；原文缺失或目标身份冲突无论是否 basis 都是阻塞。

`sources/basis_ids.json` 冻结 85 身份；`sources/comparison_521_ids.json` 仅用于比较。`sources/manifest.json` 记录导入原始文件与规范化 source 的哈希。历史公式、注册表签名、等价验收状态和 argumentation 不作为新来源认证导入。

usage inventory 包含 coverage、usages；每个 usage 单独保存 evidence、sentence_a、sentence_b、argumentation、parameters、target_arguments、occurrence_ids、determiners、voice、reductions、witnesses。reductions 记录用法约化，不要求构造不同公式。

usage.parameter_spans 可选，每项为 `{sentence:"sentence_a"|"sentence_b",start,end,text,parameter,source_occurrence_ids?:[],reason?:string}`。坐标是对应 A/B 句的精确字符区间。parameter 必须是已声明外部参数；有 source_occurrence_ids 时，这些 source 定位必须完整、连续地对应同一短语。标记后的词汇定位不再参与谓词枚举，但来源 WSD 不修改。没有关联 source IDs 的造句支撑词只被记录为参数文本，不删除任何定义词。

the 的 drop/share 除外部参数外，也可保留由显式 scope_id 绑定的局部名词参数，例如 all 的范围 lambda 中的 time(r)。这是量词用法原本的绑定，不是 the 引入存在量词。

determiners 中 a 的 `action: parameter` 必须指定已有外部参数；a 的 `action: exists` 则必须对应内部 witness。a/the 的 head_occurrence_id 指向实际名词定位，the 的 share/drop 都保留 parameter，share 与 antecedent 必须是同一参数。all 仅在 basis 内允许 action: basis_definition；非 basis 必须 provider。完整 source 的每个独立 a/an/the/all 均须恰好出现于 determiners 或可选 determiner_exclusions:[{occurrence_id,reason}] 中一次；不能只靠不加入 occurrence_ids 避开检查。排除理由必须非空且由独立 usage verifier 审查，排除的定位不能又被词汇调用使用。

binding_plan 为 `{"lexical":[{"occurrence_id":"...","usage_id":"...","bindings":{"提供方参数名":"当前外部参数或见证名"}}],"structural":{"lhs":[{"name":"Agent","arguments":["e","s"]}],"rhs":[]}}`。被动隐式主体实参写为 `{"implicit_subject":"e"}`。左右结构承诺分别描述，rhs 承诺可由实例化 provider 的完整 LHS 实现。完整 AST 与类型语法见 [AST.md](AST.md)。

词汇 binding 的值还可为 `{"world_of":"e"}`，但只对应 provider 的 World 类型槽，e 必须是可见 V 参数。World 不加入 structural.lhs/rhs 的命题承诺列表，不被当作额外词汇 occurrence。

单用法枚举的事件集合由实际可见的 V 参数确定，包括动词 occurrence 许可的内部 V 见证及性质槽的局部 V 参数。名词见证不能引入 V，Nom 的内部事件不参与外层枚举。`enumeration.structural_budgets` 为可选的非负总上限，缺省由不同类型实参原子数决定；`verb_occurrence_ids` 与 `event_structure_licenses` 是旧输入注记，不再供应次数。固定关系及实参绑定身份的作者原子至多一次，候选 `resource_counts.available_structural_atoms` 记录当前可选原子数。详见 [枚举契约](ENUMERATION.md)。

formula candidate 绑定 synset_id/usage_id，复制认证参数，提供 lhs/rhs AST。只有 basis 的 primitives 可非空。`use` 必须提供 occurrence_id、provider_hash、具体 usage_id 和按序实参。结构符号只来自单独白名单。

仅接口枚举模式新增 `usage.syntax:{sentence,tokens,provenance}`，tokens 包含 index、原句 start/end/text、pos、dependency、head，定义词另有精确 occurrence_id。未知的支撑词句法须标为未知，不补造。`analyze_nominalizations` 检查所有已映射动词；`derive_nominalization_sites` 可从明确名词位置、唯一具体用法和其唯一 V 目标槽导出构式声明，显式参与者须提供 capture 对应。

`enumeration.nominalizations` 每项为 `{nominalization_id,head_occurrence_id,usage_id,event_parameter,abstract_parameters,captures,negation_occurrence_ids,reason}`。动词用法的每个参数必须且只能属于主事件、内部抽象角色或外部 capture 三类之一。syntax 必须支持该名词化及其 not 附着；额外定义词补语／修饰语未经组合不能丢掉，未支持情况明确报错。构式 hash 包括完整用法接口、句法证据与 Nom 规则 hash。

`enumeration.noun_licenses` 支持 `origin:"nominalization"`，occurrence_id 指向已确认名词化的动词，type 必须 E，最多一个新见证。对应作者 `exists` 使用相同 origin。源 WSD/POS 保持动词，许可来自构式而非 POS 改写。

作者 Nom AST：`{op:"nom",synset_id,usage_id,interface_hash,occurrence_id,nominalization_id,construction_hash,negation_occurrence_ids,args}`。args 第一项为名词指称，后续为保持开放的 captures。`expand_nominalizations` 输出独立 `v3.nominalization-expansion/1` 编译产物，其中 `op:nom_internal` 的 NominalRef/Holds 不可反向作为作者 AST 提交。可实例化完整 verb LHS 展示角色，或保留完整 use 等待将来 basis RHS 展开；不补造缺失 RHS。

当前 Nom 接入的是 LHS-only symbolic 枚举路径，使用显式构式绑定；尚未接入生产式完整 binding_plan 输入或发布认证。输出的 proposed plan 不构成生产证书。

同一 symbolic 枚举路径新增 `enumeration.event_bindings`。新事件项为 `{occurrence_id,usage_id,event_parameter,mode:"existential",name,required?:boolean,within?:{occurrence_id,usage_id,parameter},reason}`。类型固定 V，origin 固定 verb_event，每个 occurrence 至多一项。required 缺省 false 表示词汇可以不选；词汇一旦选中，其事件绑定必须同时出现。

已有事件使用 `{occurrence_id,usage_id,event_parameter,mode:"reuse",parameter,scope_id?:string,owner_occurrence_id?:string,reason}`。无额外字段时 parameter 指外部 V；scope_id 指已提供 lambda 的 V 参数；owner_occurrence_id 指另一个普通动词 occurrence 的唯一新事件。两种局部来源不能同时指定。变量名受捕获检查，既有词汇绑定不能被覆盖。

within 精确指定存在绑定者所处的词汇参数槽；不能指 Nom 内部，槽类型必须是 Prop 或返回 Prop 的函数。候选静态门独立核对作用域、所属调用、主事件实参及复用来源，不能仅凭搜索器生成就默认通过。存在节点沿用 `{op:"exists",variables:[{name,type:"V"}],body,origin:"verb_event",occurrence_id}`，未增加语义原子。

事件许可依赖 usage.syntax 的肯定动词证据，先排除 Nom 和纯助动词／系词支撑项。普通动词的屈折词面可显式提供 `source_alignment:"recorded_lemma_match"`，仅当已有 token lemma 与源词面／stored_lemma 一致时接受，不执行新的词形猜测或 WSD。report.event_binding_hashes 绑定规则、接口和句法来源；event_ownership 显示主事件槽归属。当前和 Nom 一样用于 LHS-only 枚举，不自动进入生产发布。

判定状态区分 source blocked、usage blocked/rejected/unresolved、formula hard-gate failure、semantic rejection/unresolved、完整认证和发布。局部错误不变成 accepted，不把模型输出中的 decision 直接当作发布命令。
