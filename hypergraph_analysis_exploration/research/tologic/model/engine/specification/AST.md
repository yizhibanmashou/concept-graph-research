# V3 JSON AST v1

所有节点必须是 JSON 对象。不要返回 V2 的 `call`、`predicate`、`equiv`、`op:var` 或自然语言公式文本。

## 类型与外部参数

基础类型为字符串 `E`、`V`、`Time`、`World`、`Prop`，互不隐式转换。函数类型为 `{"arrow":[参数类型,...,返回类型]}`，例如 `{"arrow":["E","Prop"]}`。外部参数记录为 `{"name":"s","type":"E","role":"主体"}`。参数按 inventory 中顺序保留；公式参数与认证 inventory 必须完全相同。

## 节点

```json
{"var":"s"}
{"op":"target","args":[{"var":"e"}]}
{"op":"struct","name":"Agent","args":[{"var":"e"},{"var":"s"}]}
{"op":"struct","name":"Theme","args":[{"var":"e"},{"var":"h"}]}
{"op":"struct","name":"Happen","args":[{"var":"e"},{"var":"t"}]}
{"op":"struct","name":"World","args":[{"var":"e"}]}
{"op":"struct","name":"ImplicitSubj","args":[{"var":"e"}]}
{"op":"use","synset_id":"exact-provider-id","usage_id":"certified-usage-id","provider_hash":"exact-bundle-hash","occurrence_id":"source-occurrence-id","args":[{"var":"e"},{"var":"s"}]}
{"op":"primitive","name":"declared-basis-symbol","args":[{"var":"e"}]}
{"op":"and","args":[FORMULA,FORMULA]}
{"op":"or","args":[FORMULA,FORMULA]}
{"op":"not","body":FORMULA}
{"op":"implies","left":FORMULA,"right":FORMULA}
{"op":"iff","left":FORMULA,"right":FORMULA}
{"op":"eq","left":TERM,"right":TERM}
{"op":"exists","variables":[{"name":"x","type":"E"}],"body":FORMULA,"origin":"a","occurrence_id":"source-article-occurrence"}
{"op":"forall","variables":[{"name":"x","type":"E"}],"body":FORMULA}
{"op":"lambda","parameters":[{"name":"z","type":"E"}],"body":FORMULA}
{"op":"apply","function":FUNCTION,"args":[TERM]}
```

以上 FORMULA/TERM/FUNCTION 是说明占位符，实际输出必须是对应的嵌套 JSON 节点。

`target` 只指当前义项，且只允许出现于 LHS 一次。LHS 是该 target 与完整角色模式的正合取；target 的 args 恰好对应认证用法的 target_arguments。所有外部参数须由该完整模式表达，RHS 中不得删除或局部绑定这些参数。

接口确实没有开放参数的封闭命题用法可以有 parameters=[]、target_arguments=[] 和 `{"op":"target","args":[]}`。它仍须有完整认证公式，不是无公式的零元接口。量词与 lambda 的局部绑定变量列表不得为空。

`use.args` 按提供方完整 parameters 顺序实例化，包括提供方需要的所有外部角色和开放性质。它实例化整条用法，不是手工调用一个裸谓词。不得改 provider_hash、绕过 occurrence_id 或只传目标核心参数。

`ImplicitSubj` 只能作为被动用法中 `Agent(e,ImplicitSubj(e))` 的第二实参。Theme 目前只接 E 或 V；其他类型不得自行添加。

`World(e)` 返回 World 类型，仅可放在给定 `use` 调用的 World 类型参数位置。同一项可重复出现，不增加命题结构数量。它不能作为 AND 的一项，也不能填充 E/V/Time 槽。绑定计划用 `{"world_of":"e"}` 指明此项。

给定 basis 公式内部可使用 `{"op":"at_world","world":{"var":"w"},"body":FORMULA}`。它表示在指定世界解释整个公式，包括在该区域应用的性质 lambda 正文；非 basis 作者不能直接创建 at_world。All 的通用类型参数在本次调用前实例化，例如 All_Time(w,S,P)，其固定 RHS 为 at_world(w,forall t:Time [S(t) implies P(t)])。

有局部绑定时，lambda 可以带 scope_id，并在 binding_plan.scopes 中记录 `{scope_id,parent_scope,kind:"lambda",variables:[...]}`。调用或结构行的 scope_id 指向可见的父 scope；已有世界项的事件变量同样受这个可见性约束。

非 basis 不得使用 primitive、原生 forall、数字或文本常量。exists 的 origin 只能为 a 或 definition_internal，且变量、类型、来源 occurrence 必须在已认证 witnesses 中。外部参数不可被 exists/forall/lambda 捕获。lambda 仅抽象真正局部的新参数；函数参数并不授权新增语义符号。

basis 可声明 `primitives:[{"name":"...","argument_types":[TYPE,...],"return_type":TYPE,"meaning":"...","source_evidence":"..."}]`，然后在自身公式使用；零元 primitive 可表达需要的常量。每个声明必须有意义及基础定义来源，不能仅为使硬门通过而命名。

## 公式候选

```json
{
  "synset_id":"请求指定的身份",
  "usage_id":"请求指定的用法",
  "parameters":[],
  "lhs":{},
  "rhs":{},
  "primitives":[],
  "notes":"构造说明"
}
```

空数组/对象只是字段布局示意，真实候选需要完整内容。非 basis 的 primitives 必须为空。候选不能替换 source 或 inventory，不能自行提供认证。语义等价由独立 verifier 判断。
