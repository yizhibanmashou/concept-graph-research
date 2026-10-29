# 冻结图 selected-witness DAG 复用剖面

状态：全量结构描述已复算。它补充 AND/OR clause 与 witness 深度剖面，单独统计冻结包为每个 head 选取的一条 witness 子句形成的有向无环依赖图。该分析只说明结构引用/复用，不给节点赋予语言学重要性，也不检验 gloss 的语义忠实度。

## 结果

固定图规则 SHA-256 为 `c07dd37342ab399244a091501a21ada9e2f9f706efb1dc34d6b8ebc16a8a0a53`。全量 110,425 个 witness 仍通过现有结构证书校验。将每个非 basis head 的选定 witness 中每个依赖记为一条有向边后：

| 结构量 | 结果 |
|---|---:|
| selected-witness DAG 依赖边数 | 664,732 |
| 全部候选子句的 literal 引用数 | 917,767 |
| 选定 witness 边 / 全部 literal 引用 | 72.429% |
| 节点被多少其他选定 witness 引用（p90 / 最大） | 7 / 27,777 |
| 从未被其他选定 witness 引用的节点 | 65,334 / 110,425（59.17%）|
| 至少被引用一次的 basis 原语 | 85 / 85 |

引用数高度偏斜：所有 basis 都进入所选证书 DAG，但部分浅层节点被大量其他 witness 共用。按被依赖节点的 witness 深度分层：

| 节点深度 | 节点数 | 被引用节点数 | 引用次数中位数 / p90 / 最大 |
|---|---:|---:|---:|
| 0（basis） | 85 | 85 | 182 / 857 / 27,777 |
| 1–5 | 1,026 | 610 | 1 / 52 / 11,182 |
| 6–25 | 564 | 363 | 2 / 54 / 9,070 |
| 26–100 | 4,966 | 2,895 | 1 / 36 / 6,219 |
| 101–300 | 34,732 | 16,553 | 0 / 11 / 8,096 |
| 301+ | 69,052 | 24,585 | 0 / 4 / 1,797 |

所选 witness 仅选每个 head 的一个 OR 分支，所以 664,732 条边不能与 917,767 条候选规则 literal 当作同一张图的边数；它们的比值只说明选定证书相对全规则编码包含多少 literal 引用。反过来，DAG 中节点的“被引用次数”表示多少其他选定 witness 依赖该节点，不是概念中心性、语义重要性、证明贡献或 WordNet taxonomy degree。

## 复算与验证

实现仍集中于 `src/analysis/hypergraph_complexity_profile.py`，输出为 `outputs/phase6/hypergraph_complexity_profile.json` 的 `selected_witness_dag` 字段：

```powershell
python -m src.analysis.hypergraph_complexity_profile --output outputs/phase6/hypergraph_complexity_profile.json --force
```

以项目根目录运行 `python -m unittest tests.test_hypergraph_complexity_profile -v` 可验证合成 AND/OR 图的边数、复用次数及深度分层。全量输出 SHA-256：`8c7d2358d3792e4ebb514aa037b396ff06e1bfea550db0adaa59b0d15626674f2`。该摘要沿用 phase6 的机器可读结果，原有结构 profile 字段保持不变。

单个导出的 witness JSON 现在也有独立重放器：`src/analysis/verify_witness_certificate.py` 不调用导出函数，而是重新读取冻结规则、witness 和 sense 索引，核对 manifest semantic fingerprint、目标可达节点集合、所选 clause index、source-document 引用、边多重集、严格递增深度及 dependency-before-head 拓扑顺序。复核现存示例的命令为：

```powershell
python -m src.analysis.verify_witness_certificate outputs/phase6/witness_oewn-00520548-n.json
```

截至 2026-10-03，该示例在冻结包上通过：3,596 节点、14,923 条 witness literal 边、0 项结构错误。篡改图版本指纹、clause、来源引用、edge、depth 或拓扑顺序的合成测试均应失败。该检查只认证相对于当前冻结 bundle 的结构性证书；source-document 指针和定义语义仍需独立数据哈希/许可审计与人工 source-faithfulness 标注，不能据此称为 gloss entailment 证明。

## 对研究设计的作用与边界

- 全规则 clause 引用与所选 witness DAG 复用必须分开报告：前者跨越所有 OR 候选，后者是单 witness 证书中的实际 AND 依赖。
- 后续人工标注/压力测试可以同时控制 witness 深度、witness AND 宽度、head 的 OR 候选数，以及被引用次数分位；这有助于覆盖浅/深层与高复用/低复用结构。
- 高 fanout 只能作为抽样维度，不能推断高 fanout 节点是语义核心。若要评估逻辑证明的压力，仍需测量具体 query 的证书展开大小、重放时间、分支数量与资源用量；单张全局 DAG 的引用分布不能替代 query 级成本。
- witness DAG 结构正确性不证明生成该 witness 的原始定义/解析是正确的。源 span→定义 part→graph literal 的人工映射，以及独立 proof replay 和语义评测仍未完成。

## 2026-10-08 Phase175：当前 witness 家族复算

重放当前 frozen bundle 后，原 selected-witness DAG 仍有 664,732 条边，85/85 个 basis 均被引用，零引用 head 为 65,334；最小深度 witness 使用字典序 clause tie-break，形成 669,414 条边。二者 head depth 一致，但边数不同，说明最小高度 tie-break 不是 DAG 边数最小化，也不评价证据质量。冻结结构证书 110,425/110,425 有效。

Phase175 曾把包含被删 basis 本身的精确 closure loss 与不包含起点的 descendants 直接比较，得到 13 相等/53 高估/19 低估。Phase179 核对逐 basis 行后改为一致排除根节点：19/85 相等、66/85 高估、0/85 低估。差值 -1 的原 19 行全部只差被删根节点；全部 85 个根都未被重新推出。新增集合级审计显示，85 次删除累计有 0 个精确非根损失节点落在 witness descendants 之外；累计 98,573 个 descendant 场景-节点项在删除后仍可由完整 AND/OR closure 推出（66 个 seed 场景至少出现一次）。合法的 selected witness 使任何失去精确支持的非根节点都位于所选 witness descendants 中；高估来自被删节点可由未选 OR 替代子句重新推出。故 descendants 是删除影响的结构上界诊断，不是完整 AND/OR closure 重算的替代品。机器记录同时保留根包含旧指标和新增非根同口径指标。见Phase179更正报告、[Phase175 frozen audit](../outputs/phase175/frozen_hypergraph_current.json)、[minimum-depth audit](../outputs/phase175/minimum_witness_current.json)和Phase175原报告。

## Phase 184 当前复算

现态重跑冻结图和最小深度审计后，两份 JSON 分别与 Phase175 对应产物逐字节一致。85 个 basis atom、110,425 heads、154,206 clauses、917,767 dependency literals 未漂移；锁、闭包、节点/超边对账和全部 witness 验证均通过。selected witness 仍全部达到最小 grounded depth（median 320、P90 379、max 396），但最小深度不等于最少依赖边或最优来源证据。详见Phase184报告和[现态机器产物](../outputs/phase184/frozen_hypergraph_current.json)、[最小深度产物](../outputs/phase184/minimum_witness_current.json)。
