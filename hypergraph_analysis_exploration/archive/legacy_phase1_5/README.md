# 历史探索材料（只读归档）

本目录保留早期 phase 1–5 普通图投影分析脚本、其私有辅助模块，以及原始 phase-2 规划稿。它们是探索记录，不属于当前核心 API；不应被误认为经过当前 Horn AND/OR 结构语义复核或人工语义评测的结果。

归档内容保持原文/原代码，不在此维护。早期运行所需的 NetworkX、python-louvain、Pandas、Matplotlib/Seaborn 等依赖和旧式导入路径未整理为受支持的可复跑环境。历史 JSON、报告与可视化仍保留在 `outputs/phase1`、`outputs/phase2`–`phase5` 及 `reports/` 对应目录中；新结果应走当前 `src/analysis` 核心工具并写清输入指纹与复跑命令。

已从 `src/` 移入的文件：

- `src/analysis/community_detection.py`
- `src/analysis/path_analysis.py`
- `src/analysis/cycle_analysis.py`
- `src/analysis/hub_analysis.py`
- `src/analysis/report_generator.py`
- `src/utils/data_loader.py`
- `src/visualization/visualizer.py`

原规划稿保存在 `docs/phase2_plan_original.md`。普通图分析历史结论及其限制见 `../report/project_review_2026-10-29-current.md`。
