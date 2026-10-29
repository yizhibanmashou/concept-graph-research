# ToLogicV3 六义项枚举资料包

请先阅读 [给合作者的说明文档](COLLABORATOR_GUIDE.md)。

包内包含枚举脚本与必要依赖、六个义项的原始来源和 Lingua 图、当前 basis 用法 LHS、455条完整候选，以及六条已确认正确公式。

Python 3.11及以上，只需标准库，在本目录运行：

```console
python -B -X utf8 bundle.py verify
python -B -X utf8 bundle.py replay --out rerun
```

预期候选数：bear 130、life 2、hand in hand 3、all along 20、immobility 122、impermissible 178。两条命令完成后均应显示 PASS。输出目录必须是新的空目录。

输入与源记录中的历史绝对路径仅供追溯，不是运行依赖。包内未提供 basis RHS，也不需要联网或API服务。


## 项目整理说明

此目录整合用户提供的六例与 want 案例；历史本机绝对路径已替换为 `[redacted-local-path]`，并重新计算清单及六例输入摘要。原始压缩包独立保存在原位置，不随 Git 上传；整理后的清单不表示与原包逐字节相同。`cases/want_lack/` 是额外案例，不是六例 gold。
