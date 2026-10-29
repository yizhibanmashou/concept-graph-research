# 复用计算的顺序敏感性试点

`witness_reuse_orders` 固定同一组目标、深度和缓存容量，对多个种子随机排列目标后逐一模拟 LRU，记录每种顺序的状态计算次数、命中、驱逐与汇总范围。重复的顺序是同一目标集的配对计算，并非独立人群，也没有计时。

在超图项目目录，使用本机冻结包和不随 Git 提供的根节点清单：

```powershell
python -m src.analysis.witness_reuse_orders --bundle ../OEWN --roots outputs/experiment_2026_10_13/evaluation_root_ids.txt --depth 4 --capacities 0 256 4096 --seeds 11 17 23 31 47 --out outputs/reuse_orders_new.json
```

输出必须是新文件。结果记录输入摘要、种子、容量、每次模拟和最小/中位/最大计算状态数；容量单位是 `(节点 ID, 剩余深度)` 键。仅使用 selected witness，不能推断不同定义分支的结果；计算量变化既不是语义正确性，也不是人类学习证据。不能把这五个顺序当作独立采样的词义或参与者。
