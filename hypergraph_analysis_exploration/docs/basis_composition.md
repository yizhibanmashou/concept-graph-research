# 冻结包 basis 构成审计

状态：已对当前交付冻结包复算；只描述包中被标记为结构种子的 85 个节点，不给出语义原语或认知基础词结论。

## 结果

| 维度 | 计数 |
|---|---:|
| POS：名词 `n` | 37 |
| POS：动词 `v` | 23 |
| POS：形容词 `a` | 8 |
| POS：副词 `r` | 3 |
| POS：卫星形容词 `s` | 1 |
| POS：介词 `prep` | 13 |
| OEWN 命名空间 | 72 |
| 非 OEWN 命名空间 | 13 |

按冻结包 `source_root` 聚合：`fully_parsed_glosstag_plausible_wsd` 46、`ready_for_lingua_glosstag_plausible_wsd` 25、`nonstandard_definition_wsd_success_merged` 13、`standard_definition_wsd_external` 1。85 个 basis ID 均唯一，并在 `nodes.tsv` 中恰有一条对应记录，且 `is_basis=true` 与 `selected_basis_atoms.txt` 一致。

此构成显示该种子集合混有多个词性和来源处理类别，且包含 13 个介词类、非 OEWN 命名空间节点。它是**结构 basis**，不等同于 Natural Semantic Metalanguage 原语、sememe inventory 或其他语言学语义原语；统计不能证明 85 个节点全局最小，也不能证明从这些节点得到的定义依赖具有真值条件语义。

Phase229 对所有 basis 节点额外核对了 `nodes.tsv`→sense index→source-record→payload identity/checksum 链：85/85 identity 和定义元数据匹配，166/166 source payload 的大小、SHA-256 与 sense identity 全部通过。该映射补足的是来源身份和字节级 lineage；它没有把 basis atom deletion 变成 source-document deletion，也不证明任何 gloss span 支持规则。详见Phase229 深度报告、[机器记录](../sources/basis_source_lineage_audit_2026-10-08_phase229.json)和[聚合输出](../outputs/phase229/basis_source_lineage_audit.json)。

## 复算

```powershell
python -m src.analysis.basis_composition_audit
python -m unittest tests.test_basis_composition_audit -v
```

聚合结果保存在 `outputs/phase6/basis_composition_audit.json`。报告保存 basis 文件、节点表和图规则的 SHA-256，不写出 basis ID、释义或完整外部路径。需要覆盖现有报告时显式添加 `--force`；`--output` 必须指向项目目录内。输入冻结包只读。
