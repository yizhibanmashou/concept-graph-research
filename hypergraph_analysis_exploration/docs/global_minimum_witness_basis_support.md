# Phase 18：全局最小高度证明的 basis 支持包络

状态：已在冻结正 Horn 依赖超图上复算。该指标按有界证明树精确定义，对当前编码图完备；它仍然只是图结构诊断，不是语义重要性或语言学结论。

## 定义

对每个根 head `h`，先计算最小 grounded 推导高度 `d(h)`。统计其所有高度不超过 `d(h)` 的证明树；因为 `d(h)` 是最小高度，这些根证明的高度恰为 `d(h)`。递归展开时，每经过一条规则边，剩余预算减一；只保留所有依赖都能在剩余预算内推出的 AND 子句。basis fact 可作为高度 0 的叶子；若预算允许，冻结图中以 basis head 为头的规则也保留为另一种证明。因而即使一个依赖有更浅证明，只要较深的替代证明仍在根的预算内，也不会被漏掉。

在每个有界状态 `(head, budget)` 上，AND 子句的 possible support 是依赖 possible mask 的并集、certain support 是依赖 certain mask 的并集；head 的可用规则（及 basis 叶子）是 OR 备选，possible 跨备选取并、certain 跨备选取交。预算每步严格减少，因此即使原图有环，此有界递归仍终止。状态按需 memoize，而非枚举指数级证明树。

## 冻结图结果

输入 graph rules SHA-256：`c07dd37342ab399244a091501a21ada9e2f9f706efb1dc34d6b8ebc16a8a0a53`。

- 110,425 个 head、154,206 条 clause、917,767 个 dependency literal、85 个 basis；85 个 basis head 都各自也有规则子句（共 258 条）。
- 全局家族共访问 1,799,569 个 `(head, budget)` 状态；本机单次实测约 20 秒，默认状态上限 5,000,000（耗时不是性能承诺）。
- possible head–basis 对 8,910,531；certain 对 8,650,575；2 个 head 没有一个 basis atom 在所有证明中必现。
- 每个 head 的 possible basis 数中位数 84、P90 85、最小 1；certain 中位数 81、P90 85、最小 0。

相较 Phase 17 的递归局部最小家族，possible 对增加 205,817，certain 对减少 7,826。该方向符合“扩大证明家族时 possible 不减、certain 不增”的集合性质。两种口径的差异不是结果矛盾：Phase 17 要求每个节点都用自身最浅子证明；本 Phase 允许在全局根高度预算内的 slack 子证明，并将 basis 事实和其规则推导视作 OR 备选。全局值应作为“所有全局最小高度证明”问题的主指标，Phase 17 作为更窄的局部最小对照保留。

### 结构分层

报告另外按根最小推导深度、head 的 OR 子句数、最大 AND 子句宽度分层；每层包括 possible 新增对、certain 消失对、发生变化的 head 占比及每 head 平均变化。各维度单独分层且互不嵌套，分层求和均与全图差异严格一致。当前有两个值得进一步检验的结构观察：

- 深度 101–300 的 34,732 个 head 平均新增 2.89 个 possible basis 对，约 97.3% 的 head 至少新增一对；该层贡献全图 100,431/205,817 个 possible 新增对。深度 301+ 的绝对变化也很大（92,028 个 possible 对新增、5,891 个 certain 对消失），但每 head possible 新增为 1.33。
- 最大 AND 宽度 2–3 的节点平均新增 2.22 个 possible 对；宽度 8+ 节点平均新增 1.31。该模式提示“结构宽度越高，slack 支持变化越大”并不成立，值得用于分层抽样而非直接推断语义难度。

这些是冻结图中读出差异的描述统计，不是独立样本假设检验，也不说明定义复杂度或语义不确定性；宽度/深度之间的相关性尚未控制。机器报告保留所有层级聚合值，以便后续预注册的样本设计和复算。

完整分布、校验标志及不含 basis ID/来源路径/释义文本的机器报告见 `outputs/phase18/global_minimum_witness_basis_support.json`。

## 解释边界

精确性只相对于冻结图及上述证明树定义：它说明当前 OR-of-AND Horn 图在该高度界下的结构 basis 支持，不说明规则语义正确、sense 对齐正确、释义蕴含成立，也不证明 85 个 seed 是普适 semantic primes。图中某条规则被证明系统使用，只能推出“相对于输入图可推出”，不能代替对自然语言来源的验证。支持 mask 也不是完整的 why-provenance 多项式或开放世界解释。

## 复算与验证

在项目根目录运行：

```powershell
python -m src.analysis.global_minimum_witness_basis_support
python -m unittest tests.test_minimum_witness_audit -v
```

默认写入 `outputs/phase18/global_minimum_witness_basis_support.json`；已有输出需传 `--force` 才覆盖。可用 `--max-states` 调低/调高 memo 状态上限。单测包括 slack 子证明反例、basis 叶子与规则备选，以及 12 个固定随机 DAG 超图与显式枚举证明树的差分对拍；它验证计算定义，不验证 WordNet 语义。
