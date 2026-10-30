# OEWN 义项构造与依赖超图研究

本仓库研究词典义项定义中的联合依赖、替代分支及其来源，探索可复现的结构分析、逻辑构造、NLP 应用与概念发展问题。图中的可达性是形式结构结果，不自动等同自然语言蕴涵或学习效果。数据、候选与自动生成的公式需要独立语义核验。

## 研究方向

五条研究线的阶段、当前证据、门槛与决策权见[研究总控路线图](docs/research_program_roadmap_2026-10-30.md)；本轮可以执行的工作、依赖和 PR 状态见[五线执行队列](docs/research_execution_queue_2026-10-31.md)。T02 的关系字段、盲审协议和全图 `prep_phrase` 敏感性结果见[介词关系 schema 与盲审协议](docs/preposition_relation_schema_protocol.md)。T04 的 XPU 试点和误差/输入长度审计见[WSD 试点协议](docs/tiny_bert_wsd_pilot_protocol.md)；T05 的数据单位和许可 gate 见[数据可行性评估](https://github.com/yizhibanmashou/concept-graph-research/blob/codex/t05-data-feasibility/hypergraph_analysis_exploration/docs/t05_data_feasibility_2026-10-31.md)。结构、语义、模型表现和认知证据分开判定。

- **依赖超图与概念组合**：`src/analysis/` 与 `src/logic/` 是现有结构审计和形式验证代码；`outputs/` 保存实验结果；[研究计划](docs/research_tracks_2026-10-28.md)讨论介词和来源控制。介词 full-Horn 删除敏感性分析可用 `python -m src.analysis.preposition_horn_relaxation` 复跑，结果写到根 `report/`。

义项 A–D 输入草案可通过 `python -m src.analysis.sense_representation_audit --input outputs/sense_representation_sample_2026-10-29.json --out outputs/sense_audit_new.json` 检查共同目标、释义、依赖清单、成对边及联合分支。输入须先由 `sense_representation_pilot` 生成；输出须为新文件。JSON 字符数仅是序列化长度的描述，不是模型 token 数，不能证明相同输入预算或语义正确。

介词配对审查可先运行 `python -m src.analysis.structure_sampling_pilot --seed 17 --sample-size 5 --out outputs/sample_new.json`，再运行 `python -m src.analysis.preposition_paired_review --bundle ../OEWN --sample outputs/sample_new.json --pos prep --out outputs/paired_review_new.json`。导出按同一目标逐分支展示原依赖和删除后的依赖、空分支及非空分支碰撞，并留出人工审查字段。`--pos prep-and-phrase` 是另一个删除口径；两者须分别报告。源样本和冻结包默认不随 Git 提供，输出必须是新文件。该工具没有构造角色关系或判断语义正确性，也没有遮蔽干预条件；样本仅用于探索，不是确认性评测。
- **逻辑公式构造**：[ToLogic 支线](research/tologic/README.md)包含整理后的引擎、六例和 `want` 案例；原始 ZIP 与额外重跑输出不上传，公开发布前仍需完成权利审查。
- **交互词典**：同级目录 `../concept-dictionary/` 是交互原型，见其 README；与本目录一起属于工作区根部的 Git 仓库。
- **NLP 应用**：优先以 WSD 验证义项表示中的结构增益，反向词典作为后续任务。已完成全候选管线、SemCor 文档隔离内部开发试点和 tiny BERT 三种子 A–D 结果；当前未观察到完整分支相对 B 的增益，简单 MFS 基线更强。该试点规模小、同源且输入文本长度不平衡，不构成最终验证；测试分区未读取。后续必须使用新协议、新来源及长度/信息控制。

## 目录

| 路径 | 用途 |
| --- | --- |
| `src/`, `tests/` | 研究代码与测试 |
| `config/`, `docs/` | 数据路径、协议、方法及历史记录 |
| `research/tologic/` | 模型支线的说明、受限输入及复现输出 |
| `outputs/` | 各实验数据与复现产物，提交前须逐项审核 |
| `../report/` | 全项目报告入口 |
| `sources/`, `archive/` | 来源记录与历史代码 |

[当前项目总报告](../report/project_review_2026-10-29-current.md)；[概念组合汇报稿](../report/concept_combinations_2026-10-27.md)。旧版详尽导航保存在 `docs/historical_readme_2026-10-13.md`，其中可确认的相对链接已更新为当前路径。

## 运行与验证

需要 Python 3.10+；ToLogic 包要求 Python 3.11+。从仓库根目录进入本目录后运行：

```powershell
cd hypergraph_analysis_exploration
python -m unittest discover -s tests -v
python -m src.analysis.audit_frozen_bundle_all_files
```

2026-10-28 本机研究测试结果见根目录当前总报告；GitHub Actions 已配置但未在 GitHub 上运行。完整数据依赖上一级的冻结包，默认位置见 `config/project_config.json`；全包逐文件校验可用上述命令运行；详细约定参见 `docs/reproducible_development.md` 和 `docs/data_provenance.md`。

冻结包需自行提供：将 `OEWN/` 放在仓库根目录，使 `manifest.json`、`checksums.jsonl`、`graph/` 和 `indexes/` 直接位于该目录内。可先从仓库根目录检查两个元数据文件：

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath OEWN/manifest.json, OEWN/checksums.jsonl
```

本轮版本的两个摘要依次为 `126c8c5390efaff9ca1aaa1e12f7931ca90b802104ffaf57385d4b692c23605f` 和 `6800f0840858d4358a873dcec941c9c15ab85539b3c91f357c11444477040e6c`，也记录在 `config/frozen_bundle_integrity_lock.json`。之后运行上面的全包审计；它读取约 19 GB 文件，结果写入根 `report/`，可用 `--bundle` 和 `--output` 指定其他输入及输出。校验只能确认文件与清单一致，不能代替来源或许可审核。

## GitHub 发布边界

本项目已经连接到用户建立的私有仓库 `yizhibanmashou/concept-graph-research`，研究改动按主题分支和 PR 审阅。根目录 `docs/`、`report/`、`materials/` 和 `AGENTS.md` 按本机规则忽略；原始 OEWN 包、压缩包、儿童数据、原始语料、私有会议资料、模型权重和运行输出不得进入 Git。子项目中的公开协议和可复现脚本可以提交，但每次仍须检查许可、隐私、文件体积和 `git status --short --untracked-files=all`；`.gitignore` 不代替发布审查。仓库未授予代码许可证，不要将其称作已获开源授权。
