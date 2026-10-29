# 两两 basis 删除交互审计

状态：已在当前冻结正 Horn AND/OR 图上复算。结论仅针对已锁定图与当前 basis，不是词义语义、来源忠实度或删除原始来源文件的影响估计。

## 定义

令 `B` 为冻结图中的 basis，`C(S)` 为以 seed 集合 `S` 求出的完整最小正 Horn 闭包。对两个不同 basis atoms `a,b`：

- 单删损失：`L(a)=Heads \ C(B\{a})`；
- 联合删除损失：`L(a,b)=Heads \ C(B\{a,b})`；
- 单删损失并集：`L(a) ∪ L(b)`；
- **联合独有损失**：`L(a,b) \ (L(a) ∪ L(b))`。

联合独有损失中的 head 在删 `a` 或删 `b` 任一个场景下都仍可推出，但两者同时删除时失去完整 AND/OR 闭包支持。这是图内 OR 替代的联合脆弱性指标。由于删更多 seed 不会增加闭包，`L(a) ∪ L(b) ⊆ L(a,b)`；实现对每个 head 检查所有 pair-world 的位集合包含关系，而非只比较集合基数，当前全量违规数为 0。

在完整 basis closure 已成立的前提下，`h ∈ L(a,b) \ (L(a) ∪ L(b))` 等价于 `{a,b}` 是使 head `h` 不可达的 inclusion-minimal 二元素删除集：删两个会失活，删任一单项仍可达。因此该集合也可称作 head-level size-2 minimal deletion cut sets。这里的“cut set”只描述冻结 Horn 图中 seed 对 head 可达性的结构性质，不表示概率故障事件或真实 source documents。

## 实现与复算

`src/analysis/pairwise_basis_deletion_audit.py` 将所有 `choose(|B|,2)` 个删除场景打包成 Python 整数位掩码，并按依赖事件传播各场景的 Horn 闭包。AND 子句只在同一个场景内所有 premise bits 均成立时触发；每个节点的 bit-mask closure loss 再与 85 个单删闭包的 bitset 交集计算联合独有损失。输出前会核对冻结包 integrity lock、完整 basis closure，并用直接 closure 重新计算固定边界/中位及最大交互场景。

```powershell
python -m src.analysis.pairwise_basis_deletion_audit --output outputs/phase227/pairwise_basis_deletion_interactions.json
```

默认不覆盖既有输出；需要重建时指定新输出路径，或在明确确认后使用 `--force`。机器结果保留每个 basis pair 的精确闭包损失、单删并集、联合独有损失与对应比例，并记录 bundle、graph rules、basis hashes 及直接核对结果。

## 当前冻结图结果

当前 basis 为 85 个 atoms，共 3,570 个 pair 场景。1,102 对有非零联合独有损失，2,468 对为零；所有 pair 删除都有非零总闭包损失。联合独有损失总计 21,878 个“场景×head”项（不是互异 head 数）；最大 pair 为 `by-4` 与 `under-2`，在该场景新增损失 3,700 个 head，单删损失并集为 102,893，联合删除精确损失为 106,593。

这说明该冻结图存在可量化的二阶冗余交互，单 basis 敏感度不能完整描述多来源共同支撑的结构。但该统计不证明这些 basis atoms 的 gloss 语义独立/冗余，也不能把 basis atom 解释成真实可删除的 source document；后者需要 atom→rule→source 的可靠身份映射与干预对象定义。该交互也不等同于全局最小 basis 或 k-resilience，且不对三项及更高阶删除作结论。

Phase230 比较了 seed-only deletion 与删除同 sense 的全部冻结 source-record payload bundle（同步撤回该 seed 并禁用以该 sense 为 head 的所有 clauses）。3,570 个 pair 的 loss sets 完全一致：被删除的 basis head 在 seed-only 场景中本来就没有被重新推出，因此再移除其 head rules 不改变任何闭包。该结果仅针对冻结包级的整 sense bundle 干预，不推广到上游文档或单 payload 删除。详见Phase230报告、[方法实现](../src/analysis/basis_payload_bundle_deletion_audit.py)和[机器结果](../outputs/phase230/basis_payload_bundle_deletion_audit.json)。
