# 知径 GitHub Pages 演示

这是使用自编概念和解释的静态交互演示，不依赖 OEWN、Python 后端或网络 API。打开 `index.html` 即可使用；已知状态仅保留在当前页面会话中。它不代表完整词典或经过语义审核的研究数据。

## 发布

仓库根目录的 `.github/workflows/concept-demo-pages.yml` 在 `main` 上本目录或工作流变更时构建并部署，也支持手动运行。将该变更按项目流程提交到主题分支，经 PR 审阅并合并；在 GitHub 仓库 Settings → Pages 中将 Source 设为 GitHub Actions。工作流只上传 `concept-dictionary/pages-demo`，不会上传本地数据包。实际网址以部署结果为准。

若仓库已有 Pages 站点，启用前需核对现有发布配置：该工作流会部署到同一个仓库站点并替换其现有内容。
