# 贡献指南

感谢参与义项构造、依赖超图和知径项目。请先在对应支线目录阅读 README 和研究文档；不要把探索性结构直接表述为语义真值、逻辑蕴涵或认知规律。

## 修改前

- 保持修改范围聚焦于对应支线，避免重写原始冻结资源或上游模型包。
- 不提交个人聊天记录、会议记录、凭据、私人路径、原始数据包或未审核的数据导出。
- OEWN 冻结数据和原始 ZIP 由 `.gitignore` 排除；整理后的 ToLogic 引擎与六例、`want` 案例纳入私有仓库。对外公开前应核实许可、署名、隐私与体积。
- 结果应记录命令、输入版本/摘要、候选或样本范围、随机种子（若适用）和限制；不要用同一批数据反复调参后称为独立评测。

## 本地检查

研究代码：

```powershell
cd hypergraph_analysis_exploration
python -m compileall -q src tests
python -m unittest discover -s tests -v
```

知径：

```powershell
cd concept-dictionary
python -m unittest discover -s tests -v
cd frontend
npm ci
npm test
npm run format:check
npm run build
```

知径和图数据驱动研究需要本机准备 OEWN 冻结包；ToLogic 整理版引擎和案例随仓库提供，参见各支线 README。GitHub Actions 只验证配置中列出的代码检查，不代表被忽略的数据实验已经复跑。

本机工作区的 `docs/github_workflow.md` 记录首次上传、分支、Pull Request 和实验记录的具体步骤；该文件仅保留本地。

2026-10-29 在仅包含未忽略文件的 Windows 临时副本中，两套 Python 测试以及前端 `npm ci`、测试、格式检查和构建均通过；这不代表 GitHub Actions 在线运行或 Linux 环境已通过。

## 研究结果

区分程序/数据完整性检查、人工构造样例、探索性冒烟和独立基准。公开的模型比较须保证相同候选集、数据划分、输入长度与调参条件，说明义项映射覆盖率和数据许可，并隔离测试标签。报告失败案例及资源覆盖边界，不只报告单一汇总指标。

提交前请检查 `git status --short` 和 `git diff --check`，确认没有本机数据、缓存或敏感内容进入提交。
