# Phase 16：OEWN 义项级有向 hypernym 闭包校验

状态：资源内关系校验器已实现并在 OEWN 2025 Plus 发布包上运行示例。它是 sense-ID 级关系验证基线，不是 gloss 解析器、语义 gold 评估或 NLI 实验。

## 定义与结果

输入是一行一个显式候选：

```json
{"claim_id":"candidate-1","child_synset_id":"00034778-n","ancestor_synset_id":"00030657-n"}
```

方向固定为 child→hypernym ancestor。校验器读取 noun/verb/adj/adv synset JSON 的直接 `hypernym` 边，以有向 BFS 检查闭包，并为正例输出确定性最短证明路径。每个正结果还包含显式 Horn proof DAG：direct `hypernym(child,parent)` 边是带源文件的 ground facts，多跳结论通过 `H(x,y) ∧ H(y,z) → H(x,z)` 规则逐步派生。传递律是公开写出的推理假设，不声称由自然语言释义归纳得到。a/s 被视为同一个 adjective POS 家族；原始 POS 仍记录在节点元数据中。缺失 synset、跨 POS、self-link、资源内不可达和正例分别得到不同状态。对不可达候选也查反方向路径，但不把 resource-relative 未连通称为自然语言矛盾。

实际读取了 OEWN 2025 Plus 的 45 个 POS synset 文件，共 120,564 个 synset 和 93,395 条直接 hypernym 边。加载器确认所有边端点都存在，且边两端属于同一 POS 家族。另以 Kahn 算法检查有向图：全图无环，未处理节点数为 0。每个已解压输入文件都与发布 ZIP 内同名文件做 SHA-256 字节比对。

对示例输入 `config/hypernym_claims.example.jsonl` 的实际运行：1 条直接关系成功、1 条二跳传递关系成功、1 条在该版本 taxonomy 中未找到。前两条均输出逐边 synset ID 与来源文件路径。此三条是工具 smoke test，不是精度估计，也不证明资源关系符合人类直觉或释义逻辑。

### 可复算的资源级分层压力集

为覆盖只有 3 条示例时未碰到的结果状态，新增 `src/analysis/build_oewn_hypernym_stress_claims.py`，按固定种子 `20261006` 从当前锁定的 OEWN 发布图确定性生成 9 层、每层 40 条的本地 stress frame：direct、最短 2/3/≥4 跳、直接边反向、同 POS 前向不可达、跨 POS、synthetic missing ID、自指，共 360 条。此设计是状态分支/路径深度检查，不是概率抽样或 semantic accuracy benchmark；`same_pos_nonforward_closure` 和方向反转都只表达资源图状态。

固定 release archive SHA-256 `8832b8fa26a14c0ba8c99bb1ef8db6f9e122a6d9193b65ca9e0ef572580fee7e`，仍为 120,564 synsets、93,395 direct edges。producer 输出 40 direct、120 transitive、80 `not_in_hypernym_closure`、40 `unsupported_cross_pos`、40 missing-synset、40 self-link。每条方向反转样本都有反方向 resource path；非闭包不解释为自然语言否定。初次独立 replay 揭露原 producer 的 self-link 结果缺 `child_pos`，随后补齐该字段；修复后的 360 项 report 独立 replay 为 `valid=true`、0 errors。该修复不影响既有三条 smoke 输入/输出。

复算命令（所有输出都留在被忽略的 `outputs/phase16/`，不外发）：

```powershell
python -m src.analysis.build_oewn_hypernym_stress_claims
python -m src.analysis.oewn_hypernym_verifier outputs/phase16/oewn_hypernym_stress_v1_claims.jsonl --output outputs/phase16/oewn_hypernym_stress_v1_verification.json
python -m src.analysis.verify_oewn_hypernym_certificates outputs/phase16/oewn_hypernym_stress_v1_verification.json outputs/phase16/oewn_hypernym_stress_v1_claims.jsonl --output outputs/phase16/oewn_hypernym_stress_v1_replay.json
```

输入与产物 manifest、分层摘要及 SHA-256 见[`claims`](../outputs/phase16/oewn_hypernym_stress_v1_claims.jsonl)、[`manifest`](../outputs/phase16/oewn_hypernym_stress_v1_manifest.json)、[`producer report`](../outputs/phase16/oewn_hypernym_stress_v1_verification.json)、[`independent replay`](../outputs/phase16/oewn_hypernym_stress_v1_replay.json)。claim frame SHA-256 `462d281a7c0b705acb5e06566b20f517974c6bd03b5197b7ee9c7a8810486a33`；manifest SHA-256 `b06567948807dd94c15373b68a33a72465fa70f4fac14067e5a873c486af72cf`；producer report SHA-256 `d565e6df07787fe237130a1368efed9dbe3bc59069f0c483457adb82f463c882`；replay SHA-256 `7501b257f0269634eaa376a52d029ca22c8a6ae33ac13da16c07befefc1234d5`。manifest 绑定 generator、producer verifier 与 replay verifier 的版本和源码 SHA-256；生成器拒绝重复 directed synset pairs 与重复 claim IDs。新的 stress frame 不替代人工 sense-relation/gloss-support gold，也不升级为 NLI 或开世界反例评测。

机器可读结果：[`outputs/phase16/oewn_hypernym_verification.json`](../outputs/phase16/oewn_hypernym_verification.json)。结果记录 release archive SHA-256、45 个输入文件的 aggregate fingerprint、输入候选 SHA-256、节点/边计数、全图无环审计、图路径和逻辑证书；不会复制 gloss/example 文本。v2 同版本输入重复运行后输出 SHA-256 为 `0fb64b7600c7e51755dd7f137f018be88f47fa27acea2b8f4f41eecbebdef2d7`，结果字节一致。

## 独立逻辑证书回放

生成器与回放器分开运行。回放器在相同的固定 release/候选输入上检查 report fingerprints、全部 claim 覆盖、status 汇总、图无环结论和每条正向边；证明路径必须方向连续、起终点正确、边确实出现在该 child 的直接 `hypernym` 列表中，且来源文件与 child synset 文件一致。它独立核对 Horn transitivity rule schema、每个 rule application 的前提 ID、结论 atom、proof root 和直接事实来源；并以从目标反向搜索得到的最短距离检查路径长度，不依赖生成器的正向 BFS。对 `not_in_hypernym_closure` 则重新从 child 穷举可达闭包，确认目标确实不可达；这仍是有限资源的相对结论。

```powershell
python -m src.analysis.verify_oewn_hypernym_certificates outputs/phase16/oewn_hypernym_verification.json config/hypernym_claims.example.jsonl --output outputs/phase16/oewn_hypernym_replay.json
```

完整 OEWN 实际运行返回 3 个 claim、2 条正向路径/逻辑证书回放、0 个错误，结果为[`回放摘要`](../outputs/phase16/oewn_hypernym_replay.json)（SHA-256 `cf69ee6ebb03e26b0a12aef9c3955600f76ef9ac7a5963d07346e2f187a3bec8`）。2026-10-06 在输入契约收紧后再次运行：报告和回放摘要均保持上述 SHA-256；120,564 个 synset、93,395 条直接边，拓扑审计无环；正向状态仍为 1 direct / 1 transitive，资源内未达仍为 1，独立回放 valid=true、0 errors。此复算确认规范样例与证书稳定，不覆盖 malformed-ID 拒绝路径，也不是语义精度验证。篡改边端点、来源文件、非最短路径、Horn 前提、transitivity rule schema、release/claim 哈希、状态汇总或闭包不可达声明的合成测试均应失败。这里的“独立”指路径与逻辑 proof replay 算法和 producer 分离；loader 仍共用同一 JSON schema 约定，因此发布前还应做实现多样性审计或第三方交叉核对。

### Phase 73 relation coverage 补充

同一 pinned release 结构审计发现 93,395 条 `hypernym` 之外另有 8,599 条 `instance_hypernym`。本 verifier 有意只把普通 `hypernym` 作为 `oewn_hypernym` 输入，没有消费 instance relation；该输出不能解释为完整 WordNet 上位/实例关系闭包。两类边的语义不同，扩展验证时应使用独立关系谓词、明确规则与单独计分。lexicographer file 计数与跨文件边统计详见Phase 73。

## 复算

```powershell
python -m src.analysis.oewn_hypernym_verifier config/hypernym_claims.example.jsonl --output outputs/phase16/oewn_hypernym_verification.json
```

输出已存在时需显式添加 `--force`。输入格式拒绝未知字段、空批次、重复 claim ID、ID 首尾空白和坏 JSON；ID 不会在查询时静默规范化。synset 文件集与 ZIP 内清单不同、文件哈希不符、重复 synset ID、坏 POS、重复边、缺失端点或跨 POS 边均 fail closed。

## 解释限制与下一步

- `direct_hypernym` / `transitive_hypernym` 表示在固定发布版 OEWN relation graph 中存在可重放路径；它是该资源所编码事实的证明，不是独立的语义证明。
- `not_in_hypernym_closure` 仅表示有限 release graph 中无有向路径，开放世界下不能据此判“不是上位词”或“释义不蕴含”。
- 适配器要求调用者已经提供 child 与 ancestor synset IDs；它不提供义项消歧，不解析释义，也不做词汇候选生成。
- 只有在独立 sense/source 标注 gold 上测出 sense grounding、方向准确率、覆盖率与人工裁决一致性后，才能把这个资源关系接口纳入定义自举系统评估。下一步将其与人工 gloss-span / AST 规则映射层连接，并保留“资源 taxonomy relation”与“source-supported entailment”两个不同标签。

合成测试覆盖直接/传递路径、最短性、反向路径、不可达、缺失 ID、跨 POS、a/s 兼容、输入完整性与证书篡改拒绝。全量项目测试和 compileall 结果记录在当前项目状态文档中。

### Phase 110 bridge-link 对接说明

`src.analysis.verify_oewn_hypernym_certificates` 当前输出版本已升至 `oewn-hypernym-path-replay/3`：在 `/2` 路径/闭包回放摘要上增加 query JSONL 字节 SHA-256 和 producer report 字节 SHA-256，供 gloss bridge validator 对接。本文上文列出的 replay v2 哈希属于历史运行快照；使用 [`verify_gloss_oewn_relation_links.py`](../src/analysis/verify_gloss_oewn_relation_links.py) 前，须按文中命令重新生成 producer 和 replay v3 artifacts。Phase 110 当时未运行新版；Phase 118 已在固定压力集上复算并独立 replay。此运行证据不改变资源关系与自然语言释义之间的解释边界。

### Phase 118 runtime replay

Phase 118 已在固定 OEWN 2025 Plus release 上重算 360 条历史 stress claims，并生成独立的 [producer v2 report](../outputs/phase118/oewn_hypernym_stress_v1_verification_v2.json) 与 [replay v3 report](../outputs/phase118/oewn_hypernym_stress_v1_replay_v3.json)。Replay 覆盖 360/360 claims，160 个正路径重放成功，`valid=true`、0 errors。复算命令和 hash/边界说明见Phase 118 深度报告。这仍是 taxonomy 图内关系证书验证，不验证 gloss 的语义支持，也没有运行 gloss bridge。
