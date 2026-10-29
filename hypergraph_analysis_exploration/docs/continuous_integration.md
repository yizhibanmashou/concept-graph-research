# 持续集成检查范围

整个项目以工作区根目录为 Git 仓库。当前拟用的工作流是[根目录 checks.yml](../../.github/workflows/checks.yml)：超图任务配置 Ubuntu 上 Python 3.10–3.13，以及 Windows 上 Python 3.10 和 3.13；知径任务配置 Ubuntu、Python 3.12 和 Node.js 22。两个子目录各保留一份旧 workflow，但它们不位于当前仓库根目录的 workflow 位置，不会自动运行。GitHub 从仓库根目录发现工作流，见[官方说明](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows)。这些矩阵配置尚未在 GitHub 上运行。

超图任务执行：

```sh
python -m compileall -q src tests
python -m unittest discover -s tests -v
```

本地可执行相同检查。`project_config.json` 的默认 bundle 路径即使在 CI 中不存在，纯单元测试也应可运行；依赖真实 bundle 的全量结构复算是独立、受版本/许可约束的本地检查，不属于此工作流。

知径任务安装 Python 依赖后执行后端单元测试，并在前端执行 `npm ci`、测试、格式检查和构建。工作流不下载 OEWN 冻结包或 ToLogic 原始案例；本机干净副本验证结果见[项目总报告](../../report/project_review_2026-10-29-current.md)。

补充本地检查：Windows 临时副本上，Python 3.10.20、3.11.15、3.12.13 各通过 272 项研究测试。该副本当时已放入 ToLogic 案例，但未放入 OEWN 冻结包；此检查不等同于 GitHub 矩阵结果。

CI 通过只说明受测代码能编译且当前合成/单元测试通过。它不证明外部冻结数据可获取或许可完备，不执行 110,425-head 数据复算，不验证 WordNet gloss 到逻辑规则的语义忠实度、蕴含 soundness 或 NLI 性能。发布候选仍需依据[数据来源审查](data_provenance.md)、[冻结包审计](../../report/project_review_2026-10-29-current.md)及各阶段复算结果单独验收。
