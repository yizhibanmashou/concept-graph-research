# Phase 76：OEWN instance_hypernym 资源内校验

状态：固定发布包上的关系族 producer 与独立证书 replay 已运行；没有人工 gold 或语义准确率。

## 目的和依据

Phase 73 profile 出普通 `hypernym` 93,395 条，另有 `instance_hypernym` 8,599 条。旧 Phase 16 verifier 只验证普通类上位关系。Global WordNet schema 将 `instance_hypernym` 定义为实例所属的类，区别于表示更一般 concept 的 `hypernym`；Global WordNet documentation 对 instance relation 的说明还指出其实例端可为 proper-noun entity，目标为 common-noun class。[Global WordNet Schemas](https://globalwordnet.github.io/schemas/)、[Global WordNet relation documentation](https://globalwordnet.github.io/gwadoc/index.en.html)

## 实现

新增 `src/analysis/oewn_instance_hypernym_verifier.py`。加载器验证 release 解压文件与 pinned ZIP 字节一致，加载 synset 元数据，并把 direct `instance_hypernym` 与 direct `hypernym` 放在两个邻接表中；缺失端点、坏字段、重复边、跨 POS 均 fail closed。声明的规则只有：

1. `oewn_instance_hypernym(x,y) -> oewn_instance_of_class(x,y)`：将资源中的直接实例关系映射为 verifier 的结论谓词。
2. `oewn_instance_of_class(x,y) ∧ oewn_hypernym(y,z) -> oewn_instance_of_class(x,z)`：仅沿目标 class 的普通 `hypernym` 层级提升实例成员资格。

因此 `instance_hypernym` 本身没有被声明为可传递关系，ordinary class hierarchy 也没有与 instance facts 混同。每个正例带逐边 relation/source-file path 和含显式规则应用的 proof DAG。命令行输入是 `claim_id, instance_synset_id, class_synset_id` 三字段 JSONL，严格拒绝未知字段和重复 claim ID。来源语义依据为 Global WordNet 对 relation 的字段定义；“把 direct membership 沿 class ancestor 提升”是本 verifier 明确声明的推理规则，不能当作独立实证验证。

## 实际复算

运行 `python -m src.analysis.oewn_instance_hypernym_verifier config/instance_hypernym_claims.example.jsonl --output outputs/phase76/oewn_instance_hypernym_verification.json`，检查 45 个 taxonomy 文件与 pinned archive 的字节一致性。图含 120,564 synsets、8,599 direct instance-hypernym edges 和 93,395 ordinary class-hypernym edges。两条 opaque synset-ID fixture 分别得到 `direct_instance_membership` (1 edge) 与 `lifted_instance_class_membership` (1 instance edge + 5 class-hypernym edges)。claims SHA-256 为 `6e4172422b63d0c72c3b63ef1cb358216ed7a2743186064739ea9871746095be`；机器结果 SHA-256 为 `2bae8785f05e81711a6e5c9efa8e2b5752438f14414c4b75796003331db8fc14`。该 fixture 是状态 smoke test，不是抽样精度评估或人工验证。

新增 `src/analysis/replay_oewn_instance_hypernym_certificates.py`。replayer 独立读取 ZIP 成员及 taxonomy JSON、重算逐文件和 aggregate SHA-256、重建关系图，并用 DFS 检查 mixed-relation reachability；不调用 producer 的 graph loader、BFS 或 archive manifest helper。它逐边核对 relation kind、方向、端点、来源文件与 POS，再检查 rule schema、proof premises、root conclusion、status counts、claim/release fingerprints 和资源内 non-reachability。合成篡改测试覆盖关系类型、端点、source file、规则/前提、哈希、archive bytes、状态汇总与伪造的不可达。目标测试集 82 项通过，完整 `python -m unittest discover -s tests` 共 220 项全部通过。固定发布包两条正向证书 replay 为 `valid=true`、0 errors。

回放命令：

```powershell
python -m src.analysis.replay_oewn_instance_hypernym_certificates outputs/phase76/oewn_instance_hypernym_verification.json config/instance_hypernym_claims.example.jsonl --output outputs/phase76/oewn_instance_hypernym_replay.json
```

producer report SHA-256 为 `2bae8785f05e81711a6e5c9efa8e2b5752438f14414c4b75796003331db8fc14`；replay summary SHA-256 为 `3a1887217debabc55718bf483bf79fda2f5eec4f659e6a8346b7abb3159c9f34`。

## 解释范围与后续

- Positive status 表示固定 OEWN resource 中存在 direct instance edge 和可选 class-hypernym 路径；不是实际世界 membership、自然语言释义蕴含、sense disambiguation 或 NLI 结论。
- `not_in_instance_class_closure` 仅指当前有限发布图没有符合这两条规则的路径，不是语义反例。
- 两条样例没有提供 accuracy/coverage 估计，不可纳入 semantic gold 指标。
- 下一步应通过第三方交叉核对 release manifest 和证书格式，再通过 relation-specific human-checked sense pairs 评估。连接 gloss-span support 和 instance membership 时，仍需标注实例指称与 class 定义之间的语义边界。

本阶段不改变 Phase 16 的 hypernym 指标与结果，也不声称项目级创新性或论文有效性。
