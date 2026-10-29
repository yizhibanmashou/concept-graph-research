# 单用法公式穷尽枚举

枚举器在给定 definition、固定 WSD、一个用法的结构化 argumentation 和依赖用法完整公式后，生成全部符合下述有限构造契约的候选。另有显式的仅 LHS 研究模式，用于 basis RHS 尚未构造时的接口组合试跑。它不调用模型、不重新 WSD、不读取旧 basis 公式，也不要求先发布 V3 的 85 basis。

**正确公式满足本契约和输入中的固定约束时，完成的枚举必定包含它的规范代表。** 这是候选集的覆盖承诺，不是把所有候选判为正确。输入错误或暂不支持的类型会报错；中断、异常或显式限额不会伪称已经完整枚举。

## 运行

从 [redacted-local-path] 执行：

```powershell
python -B -X utf8 Synset/ToLogicV3/run.py enumerate --input Synset/ToLogicV3/examples/enumeration/not_scope.json --out Synset/ToLogicV3/staging/enumeration_runs/not_scope_01
```

输出目录必须不存在或为空。默认没有候选数量上限、beam、Top-k 或自动超时。仅作预览时可以明确指定 `--max-candidates 10`；若还有候选，报告为 PARTIAL，不能作为完整结果。恰好在限额处穷尽时仍可证明 COMPLETE。

Python 接口位于 src/tologic_v3/enumeration.py：

```python
prepared = prepare_request(request, project=project_path)
report = enumerate_request(request, output_dir, project=project_path)
```

结果文件：

- input.json：完整输入快照，含所给依赖公式。
- candidates.jsonl：每行一个候选，含标准 V3 formula、候选 binding_plan、单用法 inventory、来源资源计数及可读公式。
- report.json：输入摘要、候选数量、搜索计数、complete/exhausted 和终止状态。

只有搜索生成器实际穷尽后才写 `status=COMPLETE, complete=true, exhausted=true`。运行中报告为 RUNNING 且 complete=false；正常可捕获的中断记 INTERRUPTED；执行异常记 ERROR。JSONL 逐候选写出，不把全部公式放入一个大数组。去重摘要和搜索状态仍占用内存，有限不等于适合任意规模一次穷尽。

## 输入

顶层 schema_version 为 `v3.enumeration-input/1`，主要字段如下：

| 字段 | 内容 |
|---|---|
| source | 原有 V3 source：synset_id、definition、occurrences 的字符位置与固定 synset、is_basis=false、来源说明 |
| usage | 一个 V3 用法：argumentation、A/B、parameters、target_arguments、occurrence_ids、determiners、witnesses、voice、evidence、reductions |
| providers | 按 `synset_id::usage_id` 索引的已给定 provider；必须含 parameters、完整 lhs/rhs、primitives、is_basis；可有原有 bundle_hash 和 round |
| enumeration | 可选的结构化约束：词汇使用次数、已确定实参、名词见证许可、结构预算、LHS 角色、固定作用域槽映射 |

自然语言 argumentation 会保留供人和模型审查，脚本不会假装能可靠地把任意英语／中文论证自动变成硬约束。有限参数表和已确定的关系应使用 V3 的结构化字段；没有确定的选择保持开放并穷尽。七个可以直接运行的完整手写 JSON 见 examples/enumeration，不需要先生成模型回复或正式 provider 注册表。

Provider 是本次给定的语义假设。其公式会检查完整 AST、变量和类型，已有内部 not/forall/primitive 保持原样；外层枚举始终调用 `use`，不把展开后的符号重新拿来排列。传递依赖若仍以 use 出现，也必须在输入中提供，且其 hash、先后关系一致。给定的 bundle_hash 被原样保留；缺省时生成输入快照摘要，均不自动产生认证。

### 仅 LHS 的 basis 接口研究模式

使用 `schema_version: "v3.enumeration-interfaces-input/1"`，将 `providers` 换成 `interfaces`；source、usage、enumeration 保持相同契约。命令仍为 `run.py enumerate --input ... --out ...`，由 schema 明确选择模式。

每个 `synset_id::usage_id` 接口包含 `synset_id`、`usage_id`、有类型和角色说明的 `parameters`、完整 `lhs`、`rhs_status:"pending"`，可附 `description`、`evidence`。冻结 Basis85 身份写 `is_basis:true`。LHS 由一个 target 和所需白名单结构组成，必须保留所有参数。禁止放入 rhs、primitives、bundle_hash；程序不会补造占位 RHS。按接口身份、参数、LHS 及被动 voice 生成并校验独立 `interface_hash`。

用户明确提供、但旧数据漏记身份的词汇算子，可在本研究模式用顶层 `interface_assumptions:[{synset_id,occurrence_ids,reason,authorization}]` 逐定位记录。例如本会话已给定的 all 用法不在冻结85中，接口必须如实写 `is_basis:false`，来源定位保留 `frozen_synset_id:null`，不修改冻结来源或成员集合。假设须对应输入中该身份的全部确切 occurrence，来源说明计入接口哈希及报告；不可声明成正式 basis，也不能覆盖已声明的不同冻结身份。标准完整公式 schema 不接受这个研究字段。

候选为 `v3.interface-formula-candidate/1`，use 携带 `interface_hash`。调用实例化完整 LHS，角色和参数共享不丢失；只做 LHS 替换，不展开 basis RHS。`interface_gate` 检查类型、词汇来源、次数、外部参数和允许结构；完整 V3 gate 标记 `NOT_RUN_REQUIRES_CERTIFIED_FORMULAS`。`COMPLETE` 仍只表示有限搜索实际穷尽，产物 `publishable:false`，不会进入 provider 注册表。独立语义审查可在给定接口假设下选出符合作用法的公式，不代表 basis RHS 已经构造或认证。

真实第一层示例见 [三项试跑](../staging/first_layer_simple_trials_20261014/README.md)：bear、life、hand in hand 当前共 135 条候选，全部候选集合与独立的小规模穷举一致。hand in hand 已按用户修正，仅使用事件参数 e，together 的接口为 Together(e)，原句主语留在上下文记录中。各输入刻意不固定词汇绑定，正确绑定由枚举产生后再选择。

带作用域的真实例子见 [作用域试跑](../staging/scope_trials_20261014/README.md)：all along 的范围／性质槽、immobility 的性质内否定、impermissible 的被动性质否定。仍只提供 LHS，没有把量词或否定作为非 basis 可任意添加的 AST 操作。

### 已确定与未确定的绑定

没有 `usage.binding_plan` 时，各活动 occurrence 默认最多一次、可以不用，符合“至多出现定义次数”的规则；`enumeration.lexical` 可以明确要求某词必须使用或固定部分实参：

```json
{
  "lexical": [
    {"occurrence_id": "rel-1", "min_calls": 1, "max_calls": 1,
     "usage_ids": ["u"], "bindings": {"left": "x"}}
  ],
  "structural_budgets": {"Agent": 0, "Theme": 0, "Happen": 0}
}
```

这只固定 left=x，其他参数仍穷尽同型且可见的选择。次数只能是 0 或 1；同一词义在 definition 出现多次时，由不同 occurrence 分别提供资源，而不是复用同一个 occurrence。

若输入已有 `usage.binding_plan`，它被视为冻结的完整调用计划：列出的调用必须实现，用法和已给定的实参不能改变；未列出的直接调用不会新增。每个输出附上与自身作用域匹配的完整候选计划，但不会把该计划冒充新的独立认证。若只想固定一部分条件，请用 enumeration.lexical.bindings，而不要伪装为完整认证计划。

存在的固定 lambda scope 模板会被穷尽地匹配到类型相容的用法参数槽。可以用 `slot_scopes` 提供确定的映射，键为 `occurrence_id::usage_id::parameter_name`，值为 binding_plan.scopes 中的 scope_id。all 的限制性质槽和核作用域槽分开处理，不能只通过一个算子排列顺序代替。

仅需给局部变量及限定词头声明作用域、又不想冻结调用和结构位置时，可以使用 `enumeration.scope_templates`，格式与 `binding_plan.scopes` 相同。如果二者都给出则必须一致。模板只能由既有词汇用法的同型函数槽实现，不添加自由 lambda 或量词。比如 all the time 的 the 可指向 `time_scope` 中的 r，而 `time_scope` 究竟接 S 还是 P 仍开放枚举；这不要求先把正确的 Happen 正文写进 binding_plan。

### 名词见证

动词名词化增加了通用 Nom 资源。详见 [Nom 规则](RULES.md#41-动词名词化-nom) 与 [真实试跑](../staging/scope_trials_20261014/revisions/nominalized_verb/README.md)。先根据提供的句法分析识别，而非按 -ing 字面替换；`derive_nominalization_sites` 从已知完整动词用法导出事件／角色绑定。动词仍保留其冻结 WSD 身份。

Nom 的作者形式是一个带 E 指称槽的原子宏，内部事件／角色不加入外层可见变量集合，不增加外层 Agent/Theme 候选。名词化 occurrence 可通过 `noun_licenses` 的 `origin:nominalization` 许可一个外层 E 存在见证。语法明确附着的 not 可选择位于 Nom 内或由普通词汇调用在外层组合；资源选择器按消耗的原始 occurrence 去重，不能在两处重复使用同一个 not。所有选择仍有限，默认无截断。

NominalRef/Holds 只在展开时生成；它们不在普通结构关系白名单中，作者或 provider 不能将其声明为 primitive。完整动词用法通过 `exists e F` 进入 Nom 模板，not 位于该内部存在量化之外。类型门和来源门只判定静态合法性，语义选择仍另行进行。

`usage.witnesses` 中已经确定的内部见证必须保留。a 的 action=exists 必须指明真实名词头并提供对应见证；action=parameter 仍使用外部参数。the 只保留原分析中的共享／去冠词决定。

新的可选裸不可数名词见证通过以下有限许可列出：

```json
{
  "noun_licenses": [
    {"occurrence_id": "water-1", "origin": "bare_mass",
     "name": "y", "type": "E", "required": false,
     "reason": "本用法允许内部水量见证，外部容器 x 仍是参数。"}
  ]
}
```

每个名词出现位置最多一个许可；不得把外部参数或已有局部参数改成见证。a 许可还需 article_occurrence_id，与用法中的冠词分析一致。选中见证时，名词调用必须实际接收这个见证，不能只生成 ∃y.Rel(x,y) 而漏掉作为许可证依据的 Noun(y)。

裸不可数名词的作者 AST 使用既有 V3 `origin=definition_internal`，精确来源保留在输入 noun_licenses；不能利用该兼容字段引入任意“内部原因”变量。名词见证的完整清单属于输入 argumentation，枚举器不根据词面猜测可数性。新增量词数受这个清单和名词出现次数双重限制，不统计 provider 固定公式内部的量词。

### 事件集合、结构原子和左侧

先选择词汇用法、获准见证及其作用域，再收集每个区域实际可见的参数。V 事件可以来自 LHS 外部参数、普通动词 occurrence 许可的内部事件，或给定用法性质槽绑定的局部 V 参数。名词见证不得引入 V，Nom 的内部事件不暴露给外层。新事件必须有动词来源，不能为填补类型缺口凭空制造；已有事件也不能重复量化。

在同一可见区域内建立有限原子集合：Agent 使用 V×E，Theme 使用 V×(E∪V)，Happen 使用 V×Time。被动用法还可有 Agent(e,ImplicitSubj(e))。枚举原子子集以及每个原子的合法作用域位置；一份候选的作者 RHS 中，固定关系和实参身份的同一个原子至多选一次。因而 Agent(e,h1) 与 Agent(e,h2) 可以同时出现，Happen(e,t1) 与 Happen(e,t2) 也可以同时出现。不会添加角色单值性或事件只在一个时刻发生的公理。

普通动词内部事件由 enumeration.event_bindings 许可，不能借用 noun_licenses。先排除 Nom，再核对源动词、具体接口和 V 主事件槽。每个 occurrence 只许可一个新事件；动词调用与事件绑定共同选择。已有外部／lambda／共享事件用 reuse。within 可限定闭包所在的词汇参数槽；没有 within 时作用域仍穷尽枚举。Nom 的内部 e 不进入外层变量池。

真实例子见 [普通动词事件闭包](../staging/scope_trials_20261014/revisions/verb_event_closure/README.md)：Impermissible(b:E) 在明确 not 作用域后有16条候选；移除该约束的对照有178条，正确式都在其中。Nom 回归的122条候选 ID 完全未变。

实参身份包括绑定者：不同 lambda 各自绑定的同名 t 是不同参数；外部 e、h 被传入不同命题区域仍是同一参数，同一个 Agent(e,h) 只能选择其中一个位置。候选记录的 resource_counts.available_structural_atoms 给出当前作用域配置下可选择的不同原子数量，structures 给出实际选中的数量。World(e) 是可重复的函数实参，不适用命题原子的一次选择限制。

`structural_budgets` 现在只是可选的显式总上限：0 禁用该关系，省略则遍历实际原子集合的全部子集。写入比原子数更大的上限也不能制造重复原子。`verb_occurrence_ids` 和 `event_structure_licenses` 仅为旧输入兼容保留并检查其记录格式，不再增加或限制结构预算。all along 的外部 e 和局部 t 已足以提供 Happen(e,t)，不需要额外事件许可。

被动仅允许 Agent(e,ImplicitSubj(e))；两处事件一致，不生成其他独立 ImplicitSubj 用法。Theme 保持 E/V 区别，Happen 接收 V 和 Time。

LHS 是输入用法已有的目标及角色模式，固定而不枚举。使用 binding_plan.structural.lhs，或 enumeration.lhs_structures；没有角色时使用 target(target_arguments)。全部外部参数必须保留在该 LHS。预算针对枚举器在 RHS 新编写的结构调用，不重复计算输入固定 LHS 或 provider 宏内部原有的角色条件。

## 枚举的准确语言

外层可生成 `use`、允许的 `struct`、获准 `exists` 和 AND。not、all、or 等只能作为 definition 中真实词汇调用，其含义由给定用法提供；没有自由生成 native not/or/forall/eq 的入口。

普通实参从有限的可见同型变量中选择。Prop 参数可直接接收已有 Prop 变量，或接收一个生成的命题区域。性质参数可直接接收同型函数变量，或生成接口规定形状的 lambda；lambda 只用于填已有用法槽位，不随意包装公式。区域内已有 Prop 参数可作为合取项，同一参数在同一区域的重复用一次规范代表。

目前支持 E、V、Time、World、Prop，以及最外层返回 Prop 的谓词函数参数，例如 E→Prop、V×E→Prop、(E→Prop)→Prop。其 lambda 参数类型可为更高阶已知类型。需要生成返回非 Prop 的函数参数、任意函数应用、未列出的语义原语等输入会明确报 unsupported，不以一个缩水候选集返回 COMPLETE。World:V→World 是明确批准的参数项，不是任意函数合成入口。固定 provider 内部已有的其他构造仍可被检查和保留；枚举器不重新合成其内部实现。

参数化函数若需要执行，须由给定的 provider 用法公式实现；作者层没有可无限使用的 apply 构造。此限制对应当前讨论的“固定词汇调用＋有限绑定／作用域＋AND”语言，不是通用高阶项合成器。

每个区域非空，没有凭空的 truth/空合取。AND 按同区域展平排序，并检查二元等价计数不超过作者谓词调用数量。不跨 not/all/exists 搬运条件，不以有限模型上的偶然相同作语义去重。来源标记不同的同形公式可以保留为不同候选，例如两个 not occurrence 的嵌套次序。

### 世界参数与参数占位短语

当被调用的定义词汇用法有 World 类型实参，枚举器可填入一个可见 World 变量，或任一可见事件的 `World(e)` 项。没有这种槽就不生成该项。它是单值函数项，可在多个槽重复，不计作词汇／动词／结构谓词资源；有限世界槽与有限事件变量仍保证组合有限。固定绑定写作 `{"world_of":"e"}`。World 返回 World 而不是 Prop，不能独立放入 AND。

世界作用域来自给定 provider 的 `at_world(w,phi)`，不作为非 basis 新增构造。它在世界 w 解释完整 phi，含在该处应用的性质 lambda；不能仅给 All 加一个未使用的 w 参数。

usage.parameter_spans 明确区分占位文本和定义内容。每项记录句子 A/B、精确 start/end/text、对应外部 parameter，并可关联 source_occurrence_ids。关联词不再要求 provider 或生成词汇调用，外部变量仍保留。例如被标记的 the object 只提供 h:E，不产生 Object(h)。未标记的 time 不因也是名词就被删除。

`examples/enumeration/want_parameter.json` 验证 `Target(e) AND Theme(e,h) ↔ want(e,h)`，不产生 Agent、Object 或存在量词。旧 want_the.json 被保留为明确包含 Object 条件的对照例，不能用它代表用户标记为参数的情形。

`examples/enumeration/all_along.json` 使用真实义项 oewn-00068615-r 的 p0 原文 all the time。冻结来源缺少 all 的最终 WSD，因此 All 依赖明确标记为用户给定假设；time 沿用该分支已有的 oewn-00028468-n。此测试不修改冻结源，也不声称覆盖原完整定义的另一个分支。作用域开放时产生 S/P 两种匹配；固定 slot_scopes 后保留用户给定公式一项。the 在这里使用 time_scope 中的局部 r，不创建外部时间或额外量词。

## 完备性理由

任取满足输入契约的正确公式 F：

1. 将其同区域 AND 展平排序、局部变量按来源槽位统一命名。得到等价的规范代表；不改变源 occurrence、语义作用域或外部参数。
2. F 中每个 use 对应一个来源资源及一个已知用法；每个新增 exists 对应一个名词许可。先移去结构原子叶节点，得到由词汇调用和见证绑定构成、允许暂时为空的有限作用域骨架。引擎遍历其资源选择、用法选择和全部无环放置。
3. 每个 Prop／函数实参，要么是现有变量，要么由其接口规定的子公式／lambda 实现。引擎遍历这两类模式及固定 scope 模板的所有相容匹配。
4. 骨架决定每个区域的可见参数及绑定身份。F 中每个新增结构原子都属于对应有限类型实参积；引擎遍历这些原子的全部子集及每个原子的合法区域位置，同时遵守显式预算。同一原子不能重复，但不同绑定者的同名参数仍是不同选择。补入结构原子及 Prop 叶后再检查区域非空和参数覆盖。
5. F 满足类型、来源、作用域和输入固定条件，所以不会被相应硬剪枝排除。因此它的规范代表必然到达输出。

有限词汇节点、槽位和见证先决定有限作用域与变量，再决定有限的结构原子集合，保证搜索结束。生成器不做语义评分删减，不依据原 V3 gate 的额外规则删除候选。故实际穷尽时，同时得到有限性与该语言内的覆盖保证。

该保证以输入依赖公式和结构化 argumentation 正确且完整为前提。源数据或约束自相矛盾时会报输入错误，或得到零个满足约束的候选；后者应检查输入及枚举覆盖，不应直接解释为词义无法表达。模型对候选的语义选择仍需后续独立 verifier。

## 与现有 V3 流水线的衔接

每个候选输出标准 formula 字段 synset_id、usage_id、parameters、lhs、rhs、primitives=[]。同时提供 inventory 与完整 binding_plan，便于单用法核验；标记 `PROPOSED_SINGLE_USAGE_NOT_CERTIFIED`，其 coverage 只指本次输入的单个用法，不宣称穷尽该义项的全部自然语言用法。

现有 validate_formula 的结果记录在每行 v3_gate 中，作为兼容性诊断，不作为未经证明的筛除条件。这防止旧门禁的差异破坏新枚举的覆盖承诺。下一步可由模型只选择 candidate_id，再把原始完整候选送独立 verifier；本命令不发布任何结果。

## 验证

七个手写例子的完整运行结果在 staging/enumeration_examples/run_20261013。对应候选数为 not 3、双 not 2、关系绑定 2、want/the 1、all/a 4、裸不可数名词 1、被动/Happen 1，均实际穷尽并通过现有 V3 硬门。all/a 保留两个目标量词读法以及尚未由输入排除的两种名词附着，不假装额外语义筛选已经完成。

除逐例检查外，引擎测试还用一个独立的递归 AST 构造器作对照：两个 not occurrence、开放 P/Q、AND 预算 2，两种独立算法生成的 50 个公式集合完全相同。这是局部软件覆盖测试；上面的编码论证给出整个契约的完备性理由，不把测试数量称为形式化证明。

```powershell
python -B -X utf8 Synset/ToLogicV3/run.py self-test
```
