# Phase 17：局部最小深度 witness 的 basis 支持包络

状态：已在冻结正 Horn 依赖超图复算；这是规则结构诊断，不是语义重要性或语言学结论。

## 问题与精确定义

冻结图对每个 head 保存 OR 个候选 clause，每个 clause 的 dependency 是 AND。Phase 14 已报告可达到 head 最小 grounded depth 的 clause 数量，但尚未描述不同最浅 clause 选择在递归展开后共同/分别依赖哪些 basis。

本 Phase 对每个 head 汇总两个 basis mask：

- **possible support**：至少存在一条 witness 选择配置使该 basis atom 出现在递归依赖中。
- **certain support**：在本分析定义的 witness 家族中，每一种递归选择配置都必须出现该 basis atom。

这里的 witness 家族严格定义为：每个非 basis head 都选择一条达到**该 head 自身最小 grounded depth** 的 clause，并递归地对所有依赖作相同选择。对于单条 AND clause，possible 是各依赖 possible mask 的并集，certain 是各依赖 certain mask 的并集；对于 OR 候选，possible 是各 clause mask 的并集，certain 是各 clause certain mask 的交集。所有选择都按冻结的有向 AND/OR clause 表示传播，没有投影为普通边。

## 结果

输入 graph rules SHA-256：`c07dd37342ab399244a091501a21ada9e2f9f706efb1dc34d6b8ebc16a8a0a53`。

- 110,425 个 head、154,206 条 clause、917,767 个 dependency literal、85 个 basis。
- 每个 head possible basis 数中位数 81，P90 85，最小 1；certain basis 数中位数 81，P90 85，最小 0。
- 汇总的 head–basis possible 对为 8,704,714；certain 对为 8,658,401；2 个 head 在该 witness 家族里没有任何单一 basis atom 属于所有递归选择。
- 对 85 个 basis 按其 possible 支持 head 数统计，分布中位数 108,410、最小 21,790、最大 109,942；按 certain 支持 head 数统计，中位数 108,260、最小 21,323、最大 109,940。basis 名称不输出。

结果由 `outputs/phase17/minimum_witness_basis_support.json` 生成。支持集合的定义、图指纹及输出边界由程序一并写入 JSON。

## 重要限制

这不是**所有全局最小高度证明树**的集合。若某个 body 中一项依赖决定根深度，而另一项依赖可以用更深但仍不超过根深度上限的子证明，本 Phase 仍排除该非自身最小深度子证明。因此，“certain/possible”只对以上明确规定的递归局部最小 clause 家族成立。后续 Phase 18 已补充全局最小高度的有界证明家族统计；两种指标不可混称。

mask 成员是冻结图标记的 85 个结构 basis，不证明其为 semantic primes、因果重要节点或 gloss 规则来源。结构支持范围与 gloss-span 支持、WordNet sense 正确性、外部事实真值均不同。`certain=0` 也不代表不可推出；只表示此处不存在一个共同的必现 basis atom。

## 复算与验证

在项目根目录运行：

```powershell
python -m src.analysis.minimum_witness_basis_support
python -m unittest tests.test_minimum_witness_audit -v
```

默认报告为 `outputs/phase17/minimum_witness_basis_support.json`；覆盖已有输出须显式传 `--force`。单元测试以 AND/OR、空 clause、循环 grounding 合成例验证行为，并在 20 个固定随机种子的小型 DAG 超图上将 bit-mask 结果与逐一枚举递归局部最小 witness 的参考算法对拍。测试证明实现符合上述集合定义，不验证 WordNet 语义。

全局最小高度证明家族及两种口径差异见[Phase 18 报告](global_minimum_witness_basis_support.md)。
