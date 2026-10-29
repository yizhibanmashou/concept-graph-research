# ToLogicV3 规则 v1

本规范、`config/policy.json` 与 `config/structural_relations.json` 是 V3 的规则来源。历史 V2 的 skill、注册表、接口、公式与 PASS 均不是 V3 的语义授权。V3 只读取历史来源，不修改 V2。

## 1. 定义、词义与用法

85 basis 是冻结的起始身份集合；它们的旧公式需要重新构造和验证。want 对应的 basis 身份是 `oewn-01829179-v`，其内部允许引入经过说明的模态表达。不能把 want 的 basis 身份泛化为每个同形词的身份。

同一 synset 可以有多种用法。用法不是新 synset，也不是 definition 的某一个 OR 分支。每种用法必须完整覆盖适用于它的定义条件，并有独立的 argumentation、句子 A、句子 B、外部参数与公式。不同用法可能约化为同一公式，这是正常现象，不判为冲突，也不强制为模式添加不等式。

收集“所有用法”指穷尽冻结来源证据支持的用法范围，必须说明覆盖依据；不是任意生成无限多句子。缺乏证据的用法不认证。不按词性预置目标接口；接口从用法和 definition 的实际组合推导，随后冻结。

## 2. WSD 已完成

输入中的 WSD 身份不可由 usage agent 或 formula agent 重新选择、修正或补造。来源证据包括 definition 原文、已有 WSD、例句和框架。例句提供用法证据，不能为 definition 增加新的词汇条件。为 A/B 造句添加的名字、person 等支撑词同样不得偷偷变成依赖。

basis 内部可直接构造 primitive，因此历史依赖 WSD 的分支冲突可保留为 warning；冲突位置的全部依赖候选须禁用，不选任一身份。非 basis 的相同冲突仍阻塞。basis 的原定义或目标身份本身有问题时仍不得继续。

非 basis 的每个直接 `use` 都必须对应 definition 中的具体 occurrence，且 synset 与固定 WSD 相同。源文件只有 B 句 token 坐标时，不能冒充 definition 坐标。缺失或不明确的来源对齐应 BLOCKED；这不等于重新进行 WSD。

## 3. 允许的结构与底层语义

唯一公共结构白名单位于 [structural_relations.json](../config/structural_relations.json)。当前有 Agent、Theme、Happen、被动语态 ImplicitSubj，以及用户明确批准的 World 参数函数。

- `Agent(V,E) -> Prop` 表示主语侧参与者，不强加有意性。
- `Theme(V,E|V) -> Prop` 接收不同类型的实体或事件，不允许 E/V 隐式转换。其他补语类型不能自行加入白名单。
- `Happen(e:V,t:Time)` 表示事件在该时刻处于发生状态。出现一个 V 变量或角色关系不自动推出 Happen。
- `ImplicitSubj(V) -> E` 仅用于被动用法的 `Agent(e,ImplicitSubj(e))`，两处 e 必须相同。显式出现的外部主语不得替换成它。
- `World(V) -> World` 是单值函数，给出事件所对应的世界。只可向 definition 内给定词汇用法的 World 类型槽传参，不作为命题独立合取。同一 World(e) 可在多个世界槽重复使用，不消耗词汇／动词出现次数或新增命题结构预算。

不继承 V2 的角色功能性或存在性公理，不强制所有词性都套用一个事件角色模板。用法中实际需要的角色不得遗漏。

结构枚举先确定已声明外部参数、已知用法局部槽及按动词 occurrence 许可的内部 V 事件，再按可见同型实参组成 Agent、Theme、Happen 原子。名词见证不能引入 V；Nom 的指称为 E，其内部事件不参与外层枚举。一个事件可以有多个施事、受事和发生时刻；限制是同一作者 RHS 中固定关系及实参身份的原子至多选一次，不是每个事件只能有一次该关系。绑定者不同的同名局部变量保持区别；LHS 和 provider 固定内部公式不占新增原子预算。具体有限枚举契约见 [ENUMERATION.md](ENUMERATION.md)。

给定 basis 公式可用 `at_world(w,phi)` 表示在世界 w 下解释完整 phi；性质 lambda 的正文在应用处的世界上下文求值。非 basis 只能经已知词汇用法间接获得它，不能自行添加一个世界作用域操作。世界参数必须确实决定公式的求值环境，不能只是没有作用的标签。

连接词、变量、相等、量词和 lambda 属于逻辑语法，但不能借此绕过词汇约束。时间、概率、空间、程度、模态等其他语义符号只允许 basis 内部引入；必须声明类型、意义和来源依据。非 basis 禁止直接调用这些符号，也禁止手工添加 RESULT、PURPOSE、CONTENT、投影、阈值或字面量。

外部通过已经认证的 basis/非 basis 用法间接获得这些语义。递归展开中出现底层符号合法的前提，是调用链可追溯到该符号的 basis 定义。白名单限制直接编写的词汇调用，不要求传递展开后的每个词都出现在最外层 definition。

## 4. 外部参数与限定词

用法所需的外部实体、事件、时间或开放性质必须先列为用法参数，保留在完整 LHS 与 RHS 中。禁止把缺失的外部角色“修好”为存在量化；禁止通过改名、局部 lambda 或量词掩盖对外部参数的捕获、删除或替换。

参数变量保留，不代表为参数造句时使用的占位词也要逻辑化。用法用 `parameter_spans` 标记 A/B 的精确参数短语；明确关联到该短语的 source occurrences 只作参数来源，不再调用其词汇公式或要求其 provider。例如被标记为 h:E 的 “the object” 不产生 Object(h) 或 the，而 h 仍通过 Theme(e,h) 等用法位置传递。未标记的定义内容不能因此被删除；all the time 中作为量化范围的 time 仍是词汇条件。

- **a/an**：按存在量词处理真正的内部见证（`action: exists`）。每个见证必须在经验证的 inventory.witnesses 中单独声明来源和原因。若所指实体是用法所需的外部输入，记录 `action: parameter` 并指向已声明参数，不能被量化掉。
- **the**：先检查同一句子中的共指名词。存在共指时共享同一参数；不存在共指时只删除冠词进行分析，名词内容、原有角色和外部参数均保留。the 本身不授权存在量词。
- 当名词已由 all 等用法的局部性质参数绑定，the 可指向显式 scope_id 中的局部名词变量，而不强行增加外部参数。整段本来就是参数占位短语时，按 parameter_spans 的来源标记处理。
- **all**：通过它对应的固定词义及已认证用法公式表达。非 basis 不把它改写为手工 `forall`。basis 内部可使用 `action: basis_definition` 实现量词，all 自身也不要求递归调用尚未建立的自己。定义对所有外部参数的元层闭包，与 RHS 中的词汇量词不同。

非 basis 的内部存在见证必须有 definition/冠词的具体来源，不能以“闭合自由变量”为理由引入。经下述构式识别的动词名词化也可许可一个 E 类型的内部名词指称。没有 all 的合法 provider 时，记录依赖阻塞。

每个用法必须逐项处理整个 source 中的独立 a/an/the/all；不适用该用法的项写入 determiner_exclusions 并说明理由，由独立用法 verifier 检查。不能仅把 occurrence 从用法列表删掉来躲开规则；同一个限定词不能重复处理、同时处理和排除，排除项也不能又被公式调用。

### 4.1 动词名词化 Nom

用户明确批准的通用规则单独保存于 `config/nominalization.json`。词义仍为原动词 synset，名词化属于具体用法／构式，不补造名词 WSD。先逐个检查已对齐动词的句法位置；介词的名词性补语、名词性主语／宾语等证据与动名词形态共同许可 Nom。不能仅凭 -ing 后缀判定。进行时助动词链保持动词用法，定语／状语分词不自动名词化，歧义或不支持的复杂结构需明确核查。

作者 RHS 只可编写 `Nom[完整动词用法](h)`，AST 为 `op:nom`，携带固定 occurrence、usage、构式 hash 和实参。不得直接写 NominalRef/Holds，也不得把它们声明成普通 basis primitive；两者仅用于编译器生成的 Nom 展开产物。完整动词 LHS 中的 Agent/Theme 等角色不能丢失。

若完整动词用法为 F(e,roles,captures)，固定展开模板为：

```text
NominalRef(h) AND forall roles
  (Holds(h,roles) IFF exists e F(e,roles,captures))
```

名词化短语中的 not 按其来源词汇调用作用于 `exists e F` 之外，再放入同一模板；不能写成 `exists e Not(F)`。本版不额外引入世界和时间维度。roles 是构式内部尚未填入的形式角色槽；已经由 A/B 传入的 captures 保持开放，不能量化、替换或隐藏。展开中的事件量化与角色抽象来自固定模板，不是作者层新增自由量词。

每个已确认的名词化动词 occurrence 最多许可一个 E 类型见证 h，以 `origin:nominalization` 记录。选用该见证时必须实际出现对应 `Nom[...](h)`，不能只量化 h 而遗漏名词条件。该名词见证许可不适用于普通有限动词或被动分词；普通事件须使用 4.2 的独立许可，不能借用 Nom。外部目标 LHS 仍从 argumentation 先行冻结。

not 在 Nom 内部或外部均占同一个来源 occurrence，不能重复消费。Nom 内部的完整 verb use 同样占用原动词 occurrence。每个构式只有一个已声明模板，没有任意套叠 Nom 或自由创建抽象词汇原子的入口。

### 4.2 普通动词的事件闭包

规则单独保存在 `config/event_closure.json`。每个活动 definition 动词 occurrence 的已知具体用法可声明 `event_bindings`：复用已有事件，或为其主事件槽许可一个内部 V 存在见证。主事件槽必须是完整 LHS 的 target 上的 V 参数；不能因为 Theme 等补语需要 V 就任意制造事件。纯语法辅助成分不能独立提供许可。

名词化识别优先：同一 occurrence 只要被识别或登记为 Nom，就不得同时声明普通事件绑定，无论复用还是新量化。同一 synset 的不同 occurrence 可以分别作普通动词和名词化。普通名词的 a/bare-mass 见证也不再允许 V，以免绕过动词来源规则。

每个主事件槽至多新增一个 `origin:verb_event` 见证。见证与所属具体动词调用同时出现，必须填入其主事件槽并由同一绑定者约束；只量化事件而省略所属动词不合法。词汇调用未选中时不额外创建它的事件。此许可不增加实体参与者，不量化或替换外部参数，不推导 Happen。

已有外部事件、已提供 lambda 事件或另一动词 occurrence 已许可且明确共享的事件，用 `mode:reuse`，不能再生成第二个存在量词。Nom 的内部事件不向外暴露，也不能被其他 occurrence 复用。事件归属和作用域先由具体用法声明，禁止根据枚举结果扩充目标接口。

存在量词的许可与作用域分开检查。可用 `within` 指定绑定者必须位于某个已知词汇调用的 Prop／性质参数槽内；没有该约束时，枚举所有类型、可见性和所有权合法的作用域。以被动用法为例，名词短语 The behavior 传入 b:E，permit 引入 r:V，闭包在 not 的命题槽内：

```text
Impermissible(b:E)
IFF Not(exists r:V [Permit(r) AND Agent(r,ImplicitSubj(r)) AND Theme(r,b)])
```

存在量化位于否定之内，不是全句对许可事件存在的肯定断言。新增事件见证数量受源动词 occurrence 的主事件槽数量约束；角色结构原子仍按可见变量对计算，二者不是同一预算。

## 5. 两套独立 agent–verifier

第一套：usage agent 收集用法、逐项 argumentation、构造 A/B、列参数/限定词/内部见证；usage verifier 独立检查覆盖、论证、参数、限定词和固定 WSD。不得把旧 argumentation 的 PASS 当作本次通过。

每个用法必须先给出 binding_plan：definition occurrence 的哪一种用法接收哪些外部参数/内部见证，LHS/RHS 各自要求哪些结构关系。两侧分别声明，不强制所有定义变换共用同一个事件角色模式。该计划经第一套 verifier 认证后，第二套不得任意换参或把已有参与者换成隐式主语。a/the 还要明确 head_occurrence_id：它限定哪个名词、名词实际调用接收哪个参数。单独保留 `x=x` 不算外部参数的有意义传递。

第二套：formula agent 对每种通过的用法分别排列组合已发布用法，构造完整 LHS ↔ RHS；先运行本地硬门，只有硬门通过才交 formula verifier 独立判断两个方向的语义等价。硬门通过仅代表可表达且符合静态约束，不代表语义等价。

verifier 使用新的独立请求，不共享生成者的聊天上下文。审查同一份冻结 source、inventory、候选和提供方快照。只有所有必需检查为 true 且决定为 ACCEPT，才形成有效认证。REJECT/UNRESOLVED 不发布；有界修复保存每次记录。

## 6. 调用、发布与逐圈扩展

`use(synset,usage,bindings)` 是编译器调用记录，不是新的逻辑谓词。它实例化提供方的完整 LHS，保留全部角色、类型、作用域和共享参数；展开时使用该用法认证的 RHS。不能裸调用依赖的目标谓词，再自行拼接任意角色。

一条候选只能读取上一冻结快照中的提供方。第 0 圈构建 basis；下一圈只使用已经发布的用法。没有完整认证公式就没有公开接口，源码队列和 staging 中的身份不构成 provider。

首版按 synset 包原子发布：本次声明的所有用法都通过后，生成公式包和派生注册表。缺失公式、缺失用法、来源不全或未切断的循环只记录阻塞，不创建无公式接口，不自动扩充 basis。

原 521 项仅是冻结比较集合，不预先保证是 V3 第一圈。每次发布绑定 source、basis、规则、结构、用法、公式、提供方版本和独立审查执行记录的哈希；变更后旧认证不能继续沿用。demo/replay 的成功不得进入 production。

## 7. 当前能力边界

本实现验证的是显式 AST、调用来源和绑定，不声称通过静态检查即可证明自然语言语义正确，也不声称模型的 EQUIV 审查构成 Lean 证明。量词、模态和 Happen 的具体理论由 basis 的新公式逐步明确。命题内容当前采用 Prop；更加细致的命题同一性、内涵和态度语境解释留作后续专门处理。
