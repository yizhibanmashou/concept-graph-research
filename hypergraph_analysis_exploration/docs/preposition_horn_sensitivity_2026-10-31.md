# 全图介词 Horn 依赖删除敏感性（2026-10-31）

## 问题与边界

本轮检查从冻结 OEWN 依赖超图中删除 POS=`prep` 的依赖字面量后，AND/OR 可达结构发生什么变化；并依用户指定将 POS=`prep_phrase` 纳入单独的敏感性条件。这个操作是**结构反事实**：删除前提会放宽剩余规则，不能解释成原释义语义错误、语义保真或逻辑蕴涵。

两种条件都保留目标头、未删除的依赖字面量和 OR 替代分支。若删除后某替代分支变空，则主报告采用保守口径把这个新空分支删除，避免将其视为无前提事实。原图中本来为空的分支（若存在）不会由此处理新造。最小派生深度是图结构量，不是人的理解难度或习得时间。

## 冻结输入与执行

- 超图：110,425 个头节点；basis 85 个（以 bundle manifest / graph 输入为准）。
- 冻结语义指纹：`6a26db5de732d90e7eb1ae700eec5c6f34e9c28fa83f35d2eb616c6abb8d4e41`。
- `nodes.tsv` SHA-256：`9bde0367d0ba1f62f7f4810b05693a82f1dcb32767c2fe7f0e88055991e23bd1`。
- `hypergraph_rules.jsonl` SHA-256：`c07dd37342ab399244a091501a21ada9e2f9f706efb1dc34d6b8ebc16a8a0a53`。
- 每次运行都先调用冻结 bundle 完整性校验。脚本：`src/analysis/preposition_horn_relaxation.py`。

```powershell
python -m src.analysis.preposition_horn_relaxation --bundle ../OEWN --pos prep --out outputs/t02_prep_horn_relaxation_v2_20261031.json
python -m src.analysis.preposition_horn_relaxation --bundle ../OEWN --pos prep-and-phrase --out outputs/t02_prep_phrase_horn_relaxation_v2_20261031.json
python -m unittest tests.test_preposition_horn_relaxation
```

本轮 5 项 T02 单元测试通过；`py_compile` 通过。完整 JSON 只在本机被 `.gitignore` 忽略的 `outputs/` 中保存。

## 结果

| 删除条件 | 移除字面量 | 有移除的 AND 子句 | 删除后新增空分支 | 保守口径可达头 | 不可达头 | 可达子集原深度中位数 → 新深度中位数 |
|---|---:|---:|---:|---:|---:|---:|
| 仅 `prep`（主分析） | 207,753 | 122,501 | 623 | 3,887 | 106,538（96.48%） | 320 → 7（子集内） |
| `prep` + `prep_phrase`（敏感性） | 208,100 | 122,594 | 638 | 3,938 | 106,487（96.43%） | 320 → 7（子集内） |

注意第一种条件的“原深度 320”是仅对删除后仍可达的 3,887 个头计算；全图原始深度中位数为 320。第二条件删除后可达 3,938 个头，其原深度中位数也是 320。两组的删除后可达子集并不相同，不能用 7 对 7 推断条件等价。把 `prep_phrase` 加入删除集合后，额外移除 347 个字面量、触及 93 个 AND 子句，保守可达头净增 51 个；这只量化结构敏感性。

## 解释

删除介词依赖导致约 96% 的头不可由当前规则从 basis 推导，说明这些依赖并非可随意去掉的“装饰边”。少数幸存目标的深度显著降低，来自规则条件被移除后的过度放宽，不能称为结构优化成功。`prep_phrase` 的增量相对小但非零；应保留为独立敏感性结果，不能并入主口径。

本实验没有对介词词义分类，没有确认其 direction / path / participant-role / negation 等类型，也没有说明依赖中的 prep 是否都表达同一种语义。已批准的窄关系类别、ordered arguments、极性与 unresolved 方案仍需要来源版本可追溯和独立人工证据。Kaikki/Wiktextract payload 当前的 source fingerprint 无法绑定到具体上游版本，许可也未确认；因此正式定义保真双盲审查及来源家族推断仍不能启动。既有 40 条仅用于试标。

## 后续门槛

1. 继续核对来源 evidence 的原始 payload、版本与许可；在 crosswalk 完成前不导出释义标注包。
2. 先以合成记录验证 `source / prep_delete / boundary_preserve / typed_relation` 四条件的转换不变量；未知类型保持 unresolved。
3. 只有满足来源和抽样协议后，才用目标等权、目标内分支比例汇总做定义保真盲审；报告方向/论元、否定范围、遗漏/添加与整体判断。
4. 可达性、深度和碰撞统计始终单列为结构描述，不能替代保真度或 NLP/认知效果。
