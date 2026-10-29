# 全候选依赖弧投影的强连通分量审计

状态：已对冻结包复算；这是**依赖图简单弧投影**的结构审计，不是 Horn 超图语义验证。

## 定义与实现

对每条候选 Horn 子句 `h ← d1 ∧ ... ∧ dk`，构造依赖指向 head 的简单弧 `di → h`。不同 OR 子句中重复出现的同一 `(dependency, head)` 对在投影图中只计一条唯一弧，同时单独报告重复投影弧数。对该有向图用迭代 Kosaraju 算法计算 SCC；使用压缩邻接数组避免递归深度限制。

这个投影会丢失超边中 AND 条件的组合语义。因而投影 SCC 只表示在所有备选依赖关系合并后互相可达，不等价于存在循环 Horn 推导、自然语言定义循环、无效规则或语义矛盾。OR 候选规则的自然语言有效性也没有在本审计中验证。

另单独检查冻结包为每个 head 选中的 witness：选中依赖的 proof depth 必须严格小于 head 的 proof depth。该性质说明所选 witness 关系无环，但全候选投影的 SCC 可因未选 OR 备选弧而包含循环；两者并不冲突。

## 冻结包结果

输入 `hypergraph_rules.jsonl` SHA-256：`c07dd37342ab399244a091501a21ada9e2f9f706efb1dc34d6b8ebc16a8a0a53`。

- 110,425 个节点、917,767 个依赖 literal；投影后 744,947 条唯一有向弧，172,820 次依赖 literal 是同一 head 的另一条候选 clause 中已出现过的投影弧。
- 简单弧图有 95,751 个 SCC，其中 949 个为循环分量（分量大小至少 2）；总计 15,623 个节点在循环分量中，最大分量 13,168 个节点。自环数为 0。
- 选中 witness 有 664,732 条依赖边；逐边均满足依赖深度小于 head 的 proof depth。部分 witness 边落在“全候选投影”的循环 SCC 内，不表示 witness 自身成环：被选边的 proof depth 仍严格递增。
- witness 记录通过已有的结构验证器，110,425 条无无效 witness。

结果只描述当前冻结规则版本。大型 SCC 不能直接解释为高语义中心性、错误知识或词义社区；若用于后续样本分层，需与 gloss 长度、POS、义项歧义、source 映射和人工语义标签分开分析，避免把投影 SCC 当作真实语义复杂度代理。

## 复算

在项目根目录执行：

```powershell
python -m src.analysis.dependency_projection_scc
python -m unittest tests.test_dependency_projection_scc -v
```

默认结果写入 `outputs/phase13/dependency_projection_scc.json`。报告只包含聚合结构指标、图文件哈希和边界说明，不输出 sense ID、lemma、gloss 或 source path。替换已存在报告须显式传 `--force`；自定义 `--output` 仍必须位于项目目录内。
