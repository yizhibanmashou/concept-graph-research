# Phase 77：OEWN instance_hypernym 分层压力集

状态：固定种子、固定 release 的 320 条状态/路径压力集已生成；producer 与独立 replay 全部通过。该集合不是语义 gold 或精度样本。

## 设计

Phase 76 的两条示例只能证明直接路径和一种提升路径可运行。本阶段沿用项目已有 stress-frame 惯例，为 instance-to-class adapter 生成八个互斥 strata，每层 40 条：direct instance relation、提升 1 条 class-hypernym edge、提升至少 2 条 class-hypernym edges、direct instance pair 方向反转、同 POS 但当前规则下不可达、跨 POS、synthetic missing synset、自指。随机种子为 `20261007`，每层固定采样 40。manifest 记录 Python 版本、随机生成器、generator/producer/replayer 版本与源码哈希、pinned release 指纹和 claims SHA-256。

这些是结构和状态分支测试。`direction_reversed` 与 `same_pos_nonclosure` 仅表示有限 OEWN 关系图在声明规则下不可达；cross-POS 是 verifier unsupported 状态；missing ID 是 synthetic sentinel。所有输出只写 synset IDs 和结构字段，不含 gloss、example、lemma 或词形文本。

## 实际复算

固定 OEWN 2025 Plus 上，generator 枚举到足够候选并输出 320 条 claims。producer 返回 40 条 direct membership、80 条 lifted membership、80 条资源内未达、40 条 self-pair、40 条 missing、40 条 cross-POS。独立 replay 对 320 条全部验证，`valid=true`、0 errors。将 generator 用 `--force` 重跑后，claims SHA-256 与首次相同，为 `50df77be79c1dab882bb549feab0495fbac5d4daa41aea02029510832093b62e`。

| 文件 | SHA-256 |
|---|---|
| claims | `50df77be79c1dab882bb549feab0495fbac5d4daa41aea02029510832093b62e` |
| manifest | `5395b1693c9cc129558e58203b9c0a51309850a6ca1b7fd951ffba59b8c90cd2` |
| producer report | `c1c0fabca2d33a103164eb331e04f3284952b9f10a4ee66b06d7c3f25fdd2cd6` |
| independent replay | `ea4a919067aed426791f7723895fb4e94640a1951b6c80467f4af7bb98dace65` |

## 复算命令

```powershell
python -m src.analysis.build_oewn_instance_hypernym_stress_claims
python -m src.analysis.oewn_instance_hypernym_verifier outputs/phase77/oewn_instance_hypernym_stress_v1_claims.jsonl --output outputs/phase77/oewn_instance_hypernym_stress_v1_verification.json
python -m src.analysis.replay_oewn_instance_hypernym_certificates outputs/phase77/oewn_instance_hypernym_stress_v1_verification.json outputs/phase77/oewn_instance_hypernym_stress_v1_claims.jsonl --output outputs/phase77/oewn_instance_hypernym_stress_v1_replay.json
```

现存输出时 producer 拒绝覆盖；若明确要重建，generator 用 `--force`，producer 用 `--force`。replayer 写入新的输出路径。

## 解释边界与下一步

320 项全部通过证明程序在这些受控输入和固定 release 上对预期结构状态保持一致。由于样本由图算法直接构造，不能估计 human sense accuracy、source-gloss entailment precision/recall、NLI performance、现实世界 membership 或外部泛化。下一步应形成 relation-specific 人工核验 pair，并比较 direct-only、class-lift depth 与 human judgments；在项目的人工双标授权流程完成之前，本阶段不生成/分发含 gloss 的人工标注材料。
