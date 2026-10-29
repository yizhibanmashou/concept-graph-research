# 义项构造、依赖超图与知径

围绕 OEWN 义项定义，研究联合依赖、概念组合、逻辑公式候选与交互式解释。工作区根目录是整个项目的 Git 仓库。

## 支线入口

- [超图分析与研究方法](hypergraph_analysis_exploration/README.md)：构造依赖、概念组合、来源审计与介词截断试验。
- [ToLogic 公式枚举与排序试验](hypergraph_analysis_exploration/research/tologic/README.md)：六个确认例子和额外 `want` 案例。
- [知径交互词典](concept-dictionary/README.md)：本地可运行的概念路径原型。
- 本机 `report/` 保存阶段报告，`docs/progress.html` 展示各支线进度；这两个目录不随 Git 上传。
- `OEWN/`：本机只读冻结数据包，直接打开即可看到 `graph/`、`indexes/` 和清单。Git 默认忽略数据包，公开发布前须核对许可。

## 初步试验

介词路径截断、ToLogic 排序、义项表示、反向词典和 WSD 试点结果及其局限记录在本机当前总报告中。图数据相关试验使用本机忽略的数据；这些试点不构成标准独立基准成绩。反向词典目前只有 BM25 词面检索；报告包含 `lend`/`borrow` 角色方向的成对失败例，不能当成正式 benchmark。

在 `hypergraph_analysis_exploration/` 内，还可运行以下实验性词面基线：

```powershell
python -m src.analysis.reverse_dictionary_pilot --query "a person who is alive"
python -m src.analysis.wsd_pilot --lemma bank --pos n --context "She deposited money at a financial institution"
python -m src.analysis.witness_reuse_pilot --out ../report/reuse_new.json
python -m src.analysis.preposition_horn_relaxation
python -m src.analysis.structure_sampling_pilot --seed 17 --sample-size 5 --out outputs/structure_sampling_example.json
python -m src.analysis.audit_frozen_bundle_all_files
python -m src.analysis.audit_wn30_oewn_sense_key_crosswalk --wordnet-tar tmp/phase256_inputs/WordNet-3.0.tar.gz --oewn-zip tmp/oewn-2025-plus-json.zip --lfs-zip tmp/phase256_inputs/wn30-lfs.zip --output ../report/wn30_oewn_2025_sense_key_crosswalk_2026-10-28.json
```

这些仅是冒烟试验，不构成独立评测。介词全图试验分别报告保留空子句（会引入无条件事实）和丢弃新空子句（会造成大量节点不可达）两种敏感性口径，均不作为语义改写效果。ToLogic 的整理版引擎和案例随项目提供，原始 ZIP 和本地重跑输出不上传；运行与校验步骤见支线 README。没有 OEWN 冻结包时，依赖完整图的试验不能复跑。

复用实验除冻结包外还需要有序根节点清单：默认读取 `hypergraph_analysis_exploration/outputs/experiment_2026_10_13/evaluation_root_ids.txt`，该目录被 Git 忽略。报告使用的 3,000 行清单 SHA-256 为 `60144fbf086d385c8c1046c908c8f2d9ded9583c5c16b1392d215d728b18cb5d`；缺少它时可通过 `--roots` 指定自己的义项 ID 文件，但结果不能与原报告直接视为同一实验。WordNet 映射命令还需要自行准备示例路径下的三个源档案，干净克隆不会包含它们。

结构分层抽样命令只生成待审查的候选 ID，不生成语义标签或训练／测试划分；重复运行请使用新的输出文件。种子固定时结果仍依赖输入规则的顺序，输出记录了输入摘要。

知径安装、构建和启动方法见其 README；需要 Python 与 Node.js。超图标准库测试使用 `python -m unittest discover -s tests -v`（在 `hypergraph_analysis_exploration/` 运行）。截至 2026-10-29 的本机复核结果见本机当前总报告；GitHub Actions 尚未运行。

截图中的研究方向与初步方案见 [研究分析](hypergraph_analysis_exploration/docs/screenshot_research_analysis_2026-10-28.md)。

## GitHub 准备

协作与本地验证要求见 [贡献指南](.github/CONTRIBUTING.md)，首次上传、分支和 PR 操作记录在本机 `docs/github_workflow.md`。根 `.gitignore` 排除根目录的 `docs/`、`report/`、`materials/`、`AGENTS.md`、OEWN 冻结包、原始 ZIP 和结果缓存；整理后的 ToLogic 引擎与案例纳入仓库。忽略数据意味着图数据驱动试验无法在干净克隆上直接复跑。仍须在公开发布前审查版权、隐私、体积和许可。尚未指定代码许可证；配置不代表 CI 已通过。

历史文档中有大量链接指向被忽略的 `hypergraph_analysis_exploration/sources/` 和 `outputs/`，普通克隆中这些链接将失效。本机存在这些目标不表示公开仓库包含它们。发布前需要确认哪些证据可以公开，并为可公开材料提供获取方式；当前清单和统计见总报告。
