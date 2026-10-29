# 全量活跃来源 payload 结构普查

状态：已扫描冻结包索引所引用的全部活跃 source JSON，并逐文件核对包内 checksums 清单。此报告是 source/logic/graph 的结构追踪，不是语义正确率。

## 输入完整性与范围

- sense index 共 110,425 条记录，与 manifest 计数一致；图规则 SHA-256 与 manifest 一致。
- 112,609 个活跃 source payload、共 18,134,793,487 字节，逐文件 SHA-256 和字节数均与 `checksums.jsonl` 一致；活跃 clause-source link 共 154,356 条，畸形 active link 为 0。
- 所有 112,609 个活跃 payload 均为可解析 UTF-8 JSON；全部 logic tree 均在审计器的 DNF 分支/深度限制内成功解析。
- 每个 payload 的 part ID 唯一；112,597/112,609 个 payload 的逻辑叶子 ID 集合与 parts ID 集合一致。
- 3,898/112,609 个 active payload 的 raw gloss 与 effective definition 字符串不同，必须区分来源释义与加工释义。

## 分支与图 clause 的结构追踪

- 108,727/112,609 个 active source payload 的 DNF 分支数与被索引归属的 graph clause 数相等，3,882 个不等。条数相等仅是必要的结构线索，不说明分支内容对应正确。
- 112,383/112,609 个 source payload 的各 part 都有非空 WSD sense ID 结果。
- 在逐 part WSD ID 完整的前提下，只有 3,123/112,609 个 payload 的 WSD 分支 ID 集合多重集与归属 graph clause literal ID 集合完全相同。
- 154,356 个 source-clause 归属对中，150,599 个 graph clause literal 集合是至少一个完整 WSD 分支 ID 并集的子集；4,887 个归属对与至少一个分支并集完全相同。

以上是集合/分支级结构相等与包含关系，不验证 WSD 义项是否正确、词句 span 是否支持 literal、AND/OR 方向是否忠实，更不验证 Horn rule 对 gloss 的蕴含。WSD 合并也可能把非逻辑贡献词带入分支集合；图构建还可能有筛选、归一化或扩展。不可将 3,123/112,609 当成“映射准确率”，也不能把剩余集合差异都判为错误。

该结果把主要工程缺口从“是否有 source payload/logic tree”推进到“part、WSD 与 graph literal 的内容映射是否有证据支持”。下一步应在许可证可用的小型、sense-disjoint slice 上人工标注 source span→part→WSD sense→graph literal 及必要/充分方向，双人独立后裁决；再分别衡量映射保真、规则语义支持、proof replay 和 NLI。不得从此结构 census 直接训练或宣称全量可靠。

## 复算

```powershell
python -m src.analysis.full_source_payload_census
python -m unittest tests.test_full_source_payload_census -v
```

默认输出 `outputs/phase15/full_source_payload_census.json`，含图/index/checksum 清单哈希、payload 顺序 digest 和聚合计数，不含 raw gloss、sense identity、文件路径或 WSD/graph ID。替换既有报告须传 `--force`。默认单个源文件读取上限为 16 MiB；超限时应先审查异常而不是自动放宽限制。
