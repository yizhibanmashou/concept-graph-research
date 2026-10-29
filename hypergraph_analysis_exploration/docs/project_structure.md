# 项目目录结构

本文按当前仓库实际布局描述；phase 1–5 内容是历史探索，未纳入核心 API。

```text
config/       项目与数据包路径配置及版本化的标注/claim-review schema 草案
docs/         方法、评测、逻辑原型、相关工作、数据发布门槛和检索记录；`source_only_evidence_contract.md` 汇总证据链可声明边界（含 figures/ 概念框架示意图及依赖投影 SCC 审计）
.github/     不下载受限数据的 Python 跨版本编译/单元测试工作流
outputs/      按 phase 分目录保存可复算 JSON、查询结果和历史产物
reports/      审计报告、阶段工作记录与历史报告
archive/      phase 1–5 普通图探索源码/原规划只读归档；历史产物仍保留
src/analysis/ 冻结 Horn 图审计、basis 构成/复杂度剖面、依赖投影 SCC、最小 witness 深度审计、全量 source payload 普查、replay exception 审计、witness 查询与独立证书重放、抽样、来源审计与 Phase 50 权利日志 crosswalk、phase9/11 词面候选与 phase12 sense-ranking baseline、双标注一致性分析、claim-review manifest 冻结与 NLI 分数连接/导出，以及按 task ID 独立随机化盲标呈现顺序的工具
src/logic/    正 Datalog 证明证书、组合证明运行器、可选签名表类型校验、NLI 评估/拒答、canonical annotation 与 claim-review sidecar 校验原型
sources/      机器可读数据来源、发布清单与文献筛读记录
tests/        核心逻辑语义、证书验证、NLI 路由、词面/sense-ranking baseline 和闭包测试
tmp/          被 Git 忽略的本机复算输入缓存（当前含 OEWN 2025/2025 Plus）；同时可暂存短期脚本/中间输出，须区分缓存与可清理产物，见 `tmp/README.md`
```

`config/project_config.json` 的 `phases` 索引对应项目阶段记录；近期阶段索引项链接阶段报告和主要机器产物。新增阶段后需同步该索引、`PROJECT_COMPLETION.md`、`SUMMARY.md` 与 README 导航。Phase 67 的 ACL 2021 定向筛读日志、reconciled candidate frame 和深度报告均已加入索引；Phase 68–75 的 typed Datalog checker、synthetic example、证书哈希绑定、annotation sort 传递与来源记录、strict replay 测试、OEWN type-inventory auditor、gloss referent/type 契约草案和阶段报告也已加入。

当前 `src/` 不再放置 phase 1–5 的普通图投影探索程序。它们及其仅供旧脚本使用的 `DataLoader`、`Visualizer` 和报告生成器已保留在 `archive/legacy_phase1_5/src/`；归档代码依赖旧导入路径和第三方库，未经维护，不承诺直接可运行。原始 phase-2 规划在 `archive/legacy_phase1_5/docs/phase2_plan_original.md`，活跃文档 `docs/phase2_plan.md` 仅作旧链接转向说明。

当前 phase8 包含全量 sense-index 结构与 active source-clause lineage census、基于 phase7 frame 的 source part/WSD 追踪，以及 291 条本地映射任务。汇总结果在 `outputs/phase8/full_source_index_audit.json`、`outputs/phase8/source_clause_alignment_audit.json`；带文本的任务与 answer key 被 `.gitignore` 排除，不得在完成许可审查前公开。全量 census 验证的是 source path/clause 的索引覆盖，不是 part-to-literal 语义对应。冻结上游 bundle 仍在项目外，只读访问。

Phase 13 在 `outputs/phase13/dependency_projection_scc.json` 保存所有备选 Horn clause 的简单依赖弧投影 SCC 结构指标；AND 超边语义被投影丢弃，因此必须与 selected-witness DAG 的无环证书分开解释。

Phase 14 在 `outputs/phase14/minimum_witness_audit.json` 对每个 head 求相对于冻结 basis 的最小 grounded 推导深度，并比较原 witness 深度及规范化 witness DAG；这是 Horn 图结构审计，不是语义蕴含分析。

Phase 15 在 `outputs/phase15/full_source_payload_census.json` 扫描全部活跃来源 payload 并逐一比对冻结 checksums；输出 part/logic/WSD ID 与 graph clause 的聚合结构对齐量，不输出释义、identity 或路径，也不作语义正确性判断。

## 维护约定

- 项目已初始化本地 Git，但当前没有首个提交或远端；首次提交前先审阅全部未跟踪源码/报告，并确认 `.gitignore` 排除了许可未清、含 gloss 的映射任务和受限 answer key。
- 核心代码与探索代码分开；短期实验脚本可放项目内 `tmp/`，验证后将必要实现迁入 `src/`，并为固定结果添加可复跑命令和测试。该目录也可能保存被 Git 忽略的本机复算输入；清理前先检查 `tmp/README.md` 与数据来源文档，不能仅因目录名而删除输入缓存。
- 可复现产物写入 `outputs/phaseN/`；先检查已有文件、哈希和 manifest，不静默覆盖冻结输入或人工材料。
- 外置 frozen bundle 只读。配置中的相对路径应以项目根目录为锚点；导出结果记录 bundle manifest、输入哈希和脚本/规则版本。
- `config/project_config.json` 是 frozen bundle 默认路径的单一配置源；路径解析由 `src/analysis/project_paths.py` 统一处理。命令行 `--bundle` 只覆盖单次运行，不回写配置。
- 文档必须区分已复现事实、实验假设、历史未验证产物与待办。结构可达性不得写成自然语言蕴含，有限 Datalog 原型不得描述成完整一阶逻辑证明器。
- 发布前确认数据、WordNet 派生资源、来源材料及投稿稿的许可证/公开权限；不要将未获许可内容复制进公开仓库。
- `sources/data_release_inventory.json` 与 `docs/data_release_gate.md` 是当前发布状态依据；在权利人未选定代码许可、冻结包未完成逐来源审查、输出未完成逐文件检查前，不得将仓库标为 fully cleared/public data release。
