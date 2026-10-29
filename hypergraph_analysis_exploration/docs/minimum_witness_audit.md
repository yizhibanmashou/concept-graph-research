# 最小推导深度 witness 基线

状态：已对冻结正 Horn 依赖超图复算；本报告描述图结构上的最小 grounded derivation depth，不描述自然语言语义。

## 定义与算法

把每个冻结规则视为 OR-of-AND Horn 子句 `h ← d1 ∧ ... ∧ dk`。basis atom 深度为 0；选择一条子句时，head 的推导深度为 `1 + max(depth(dependency))`。对每个 head 在所有可用候选子句中取最小值。实现按依赖项完成事件推进子句，并用优先队列按非递减深度结算节点；没有 basis 支撑的循环不能自行建立推导。

对相同最小深度存在多条规则时，证书构造器使用依赖 ID 元组的字典序最小子句。这样可以确定性地生成一份可重放 witness DAG；此 tie-break 不评价证据质量。

## 冻结包结果

输入 graph SHA-256：`c07dd37342ab399244a091501a21ada9e2f9f706efb1dc34d6b8ebc16a8a0a53`。

- 110,425 个 head、154,206 条 clause、917,767 个依赖 literal、85 个 basis atom 均有 grounded derivation。
- 最小推导深度中位数 320、P90 379、最大 396。
- 110,340 个非 basis head 中，最小深度 clause 数中位数为 1，P90 为 2，最大为 21。
- 现有 selected witness 的 110,425/110,425 个 head 都已达到各自最小推导深度；深度 slack 全为 0。即现有证书在此定义下已是最浅，不支持以“压缩 witness 深度”为当前优化目标。
- 原 selected-witness DAG 有 664,732 条依赖边；字典序规范化的最小深度 DAG 有 669,414 条边。相同最小深度不保证边数或证据质量最优。
- 原 witness 与新构造的最小深度 witness 均通过结构证书重放验证。

这些结果只证明相对于冻结规则和选定 basis 的图内最小层数。它不等价于最少规则数、最短证明文件、最小计算成本、语义最简推理或释义到规则的忠实性。

## 复算

```powershell
python -m src.analysis.minimum_witness_audit
python -m unittest tests.test_minimum_witness_audit -v
```

默认报告为 `outputs/phase14/minimum_witness_audit.json`。输出只含聚合统计、哈希和限制，不含 sense ID 或原始文本；替换既有报告需要 `--force`。

## 2026-10-08 Phase175：冻结图当前复算

用既有 CLI 生成[当前审计](../outputs/phase175/minimum_witness_current.json)：110,425 个 head 全部可从 85 个 basis atom grounded；154,206 clauses/917,767 dependency literals。最小深度中位数 320、P90 379、最大 396。现有 selected witness 的 110,425 个 head 全部是最浅 witness；新生成的 minimum-depth witness 也全部通过结构重放。当前 JSON 与 Phase14 报告逐字节一致（SHA-256 `0879dac51e1a604f474935be8fc65588ebabecaa3a291a9860fd4eb6005f9dba`）。此为已编码规则内的可复算结构证据，不表示 semantic entailment、最短 token/运行成本或 gloss source fidelity。完整双路检查与 basis 删除分析见Phase175报告。
