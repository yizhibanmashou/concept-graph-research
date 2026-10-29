# 六个真实义项的逻辑公式枚举与复现说明

这份资料供合作者复现 ToLogicV3 的六个单用法实验。问题是：给定义、固定 WSD、argumentation、类型明确的依赖用法 LHS，以及有限的结构规则，能否在不预先指定正确作用域的情况下完整枚举，并找到已确认的最终公式。

本包保存了一次完整运行的 **455 条候选**。六个已确认公式全部出现，原候选 ID 与完整 AST 精确匹配；每组候选集合也与单独实现的有限构造算法一致。包内同时附有程序、源数据、实际输入和正确公式，可离线核验及重新运行。

## 先运行这两条命令

解压后进入包含 `bundle.py` 的目录。需要 **Python 3.11 或以上版本**；只使用标准库，无需 pip 安装、API 密钥或网络服务。

核验文件完整性、原有455条结果、静态合法性、正确公式及独立候选集合：

```console
python -B -X utf8 bundle.py verify
```

从头枚举全部六个例子，输出到一个新的空目录，再核对结果：

```console
python -B -X utf8 bundle.py replay --out rerun
```

也可只重跑一个例子：

```console
python -B -X utf8 bundle.py replay --case impermissible --out rerun_impermissible
```

`--out` 必须是不存在或为空的目录。命令不覆盖包内保存的结果。成功时最后显示 `status: PASS`；全量运行的 `total_candidates` 应为455。重跑报告另存为输出目录下的 `verification.json`。

若要提交自行准备的输入，使用独立枚举入口。它没有预置答案或候选数，仍要求符合包内输入契约：

```console
python -B -X utf8 enumerate_one.py --input my_input.json --out my_candidates
```

建议将新输入放在原资料包之外；`bundle.py verify` 会检查归档输入未被改动。

## 六个用法和预期结果

这里的“正确公式”指本项目在当前明确用法和接口下已确认的目标表达；本轮检查它是否由枚举器生成。

| 例子 | 固定义项 | 本次定义 | 候选数 | 正确式行号 |
|---|---|---|---:|---:|
| bear | oewn-02636952-v | have | 130 | 20 |
| life | oewn-10280403-n | a living person | 2 | 2 |
| hand in hand | oewn-00246625-r | together，合作义 | 3 | 2 |
| all along | oewn-00068615-r | all the time，p0用法 | 20 | 1 |
| immobility | oewn-04783538-n | the quality of not moving | 122 | 36 |
| impermissible | oewn-01765698-a | not permitted | 178 | 17 |

行号均从1开始，指每个例子的 `results/candidates.jsonl`。完整 ID 和已选公式见 `expected/selection.json`、`expected/formula.json`，不必靠行号识别。

```text
Bear(e) ∧ Agent(e,s) ∧ Theme(e,h)
  ↔ Have(e) ∧ Agent(e,s) ∧ Theme(e,h)

Life(x) ↔ Alive(x) ∧ Person(x)

HandInHand(e) ↔ Together(e)

AllAlong(e)
  ↔ All_Time^World(e)(λr:Time.Time(r), λt:Time.Happen(e,t))

Immobility(q:E)
  ↔ Quality(q) ∧ ∃h:E [Of(q,h) ∧ Nom[not moving](h)]

Impermissible(b:E)
  ↔ Not(∃r:V [Permit(r) ∧ Agent(r,ImplicitSubj(r)) ∧ Theme(r,b)])
```

E 表示实体，V 表示事件／状态，Time 表示时间。`World:V→World` 是单值函数；只有已知用法具有 World 槽时才能使用。`Not` 和 `All` 在作者公式中都是具体来源词的用法调用，不是枚举器任意增加的否定或全称量词。

## 输入到底提供了什么

每个 `input.json` 包含原定义的精确 occurrence、固定词义身份、A/B 句、参数短语位置、目标参数和 LHS、依赖用法的完整 LHS，以及名词见证或事件许可。**没有提供 basis RHS。** `use` 实例化的是整个依赖 LHS，不能把它理解成丢掉 Agent/Theme 后的裸词汇谓词。

举例：permit 的被动用法 LHS 是 `Permit(r) ∧ Agent(r,ImplicitSubj(r)) ∧ Theme(r,b)`，其中 r:V、b:E；move 的事件用法保留 `Move(e) ∧ Agent(e,s)`；Of 使用二元实体接口 `Of(q:E,h:E)`。完整接口按例保存在 `basis_usages.json`，全包索引在 `BASIS_USAGE_INDEX.json`。

参数短语不产生附加词汇条件。hand in hand 和 all along 是事件修饰用法，只接收 e；原句主语保留在来源与上下文记录中，不自动加进副词接口。Life 的谓语名词短语作用于已有 x，冠词 a 不把 x 存在量化掉。Immobility 的 q 保持开放，h 是经名词化许可的内部指称；Impermissible 的行为指称 b 是 E，只有许可事件 r 是内部 V。

## 作用域如何保持开放

本轮没有把已选 RHS 或 binding_plan 送入搜索器。正确公式放在 `expected/`，重跑命令完成搜索后才读取它们作比较。

原 Impermissible 输入有 `within` 字段，提前将事件闭包限定在 not 的命题槽里。本轮在副本中删除这一字段，保留事件来源、所有权和类型，完整枚举其合法作用域。原接受输入仍在 `accepted_input.json`，差异见 `audit/scope_audit.json`。

实际生成的范围如下：

- All along：Time 位于 S 和位于 P 各10条，正确方向和反向方向都在列表中。`scope_templates` 只给局部变量和类型，没有决定 S/P 分配。
- Immobility：Nom 内部否定和外层 Not 都被生成，∃h 与外层否定的不同相对位置也被枚举。`negation_occurrence_ids` 给 Nom 内部附着提供许可，不强制采用该附着。
- Impermissible：`Not(∃r …)` 16条，存在绑定外包且内部含 Not 的候选146条，不含 Not 的候选16条，共178条。

已确认的 Nom 构式有固定内部展开模板：名词指称 h 描述完整动词事件用法；否定名词化在内部事件存在闭包之外施加 Not。模板内部规则不被重新发明。作者层枚举 Nom 与其他来源词的组合和附着，Nom 的内部事件不会进入外层事件池。展开说明保存在 `docs/immobility_nom_expansion.json`。

## 为什么能穷尽

输入提供有限的词汇 occurrence、已知具体用法、参数类型、性质槽、名词见证许可和事件许可。每个来源 occurrence 至多消费一次；新增结构原子由可见同型参数组成，同一关系及实参身份的原子至多选一次。函数／命题作用域只能来自已知用法槽，存在绑定只能来自已声明许可。

枚举器遍历这些有限选择及合法作用域放置，规范化同一区域的 AND，不跨 Not、All、Nom 或存在绑定随意搬动条件。默认无候选上限、beam、Top-k 或语义评分剪枝。只有搜索实际结束才标记 `COMPLETE`。

这个覆盖保证针对给定的有限构造语言。输入的类型、接口和构式必须能表达目标式。本包验证的正是六个明确例子在此语言内的实际包含性，不把455条局部结果称为任意自然语言公式的形式化完备性证明。

## 文件怎么对应

```text
bundle.py                       离线核验及完整重跑入口
enumerate_one.py                任意合规输入JSON的完整枚举入口
engine/src/tologic_v3/           枚举核心与必要运行模块的原样副本
engine/config/                  白名单 Nom 事件闭包及策略
engine/specification/           AST 数据契约与枚举规则
engine/sources/basis_ids.json    冻结的85个basis身份
cases/<例子>/
  source/cleaned.json            完整清洗记录 含词位 参数 A/B WSD Lingua
  source/v3_source.json          V3原始导入记录 含raw_wsd
  source/upstream_original.json  更早的原始上游记录 原样保存
  source/lingua_graphs.json       从cleaned中提取的全部已有图及来源
  source/provenance_map.json     原路径到包内相对路径的映射与哈希
  input.json                    本轮实际枚举输入
  accepted_input.json            已接受输入 含可能被本轮放开的约束
  basis_usages.json              此例用到的LHS接口
  results/candidates.jsonl       全部候选 每行一条
  results/input.json             运行输入快照
  results/report.json            COMPLETE及搜索统计
  expected/formula.json          已确认正确公式的完整AST
  expected/selection.json        candidate_id 行号和可读公式
  expected/matched_candidate.json 实际命中的原候选行
audit/                          原核验记录 原独立构造脚本及本轮输入差异
INDEX.json                      六项索引
MANIFEST.json                   所有包内资料的SHA256与文件大小
```

原始来源文件内保留的本机绝对路径是追溯信息；运行入口使用包内相对路径，不访问原工作区。`provenance_map.json` 给出它们的包内位置。上游原始记录可能含历史分析或公式字段，这些字段只供追溯，不参与当前枚举，也不作为 V3 依赖授权。

All along 保存了完整词典记录及两个原 argumentation，但本次只枚举已指定的 `all the time` 用法。旧来源缺少 all 的最终 WSD，故输入明确记录项目已给定的 all 接口假设；它不冒充冻结85成员，不改写原 WSD。Immobility 的旧冠词对齐 warning 也在原记录中保留。

## 建议合作者检查的内容

先运行 `verify`，再运行 `replay`，确认六组数量和正确公式匹配。随后重点查看 all along 的第1与第11条、immobility 中 Nom 内外否定、impermissible 中 Not/∃r 的内外顺序；这些例子显示作用域是在候选空间中探索后选出的。

若新增例子，请先确定该用法的目标参数、固定 WSD、依赖 LHS 和合法见证来源；无法确定的合法作用域应保持开放。改变接口或构式后，应重新枚举并重新核对正确式，不能继续沿用旧候选 ID。

当前工作阶段是 LHS-only 组合研究。静态通过说明符合构造规则，正确式的包含性由精确匹配确认；basis RHS 的语义实现和正式发布属于后续工作。本包不需要运行模型服务来复现以上结果。
