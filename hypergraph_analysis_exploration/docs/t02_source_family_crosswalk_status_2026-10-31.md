# T02 来源家族 crosswalk：标签级核验状态

审查日期：2026-10-31
证据范围：冻结包 `alternative_or_definition_wsd_frozen` 路径中 5,625 条已索引记录、3,645 个 `source_evidence` 项、82 种原始来源标签，以及本机权利日志的确定性标签对账。
用途：决定 T02 能否建立来源分层抽样框；不是法律意见，也不是语义保真结果。

## 结论

目前只能做**标签级来源排查**，尚未建立能支持独立来源家族评测的逐记录 crosswalk。82 种标签中，最高频的若干项在公开来源上能找到提供方或资源说明，但本地冻结记录通常没有足够证据把每条记录绑定到特定上游字节快照、发行版、许可证和署名要求。标签匹配权利日志只表示找到了相关日志行，不代表记录级来源或再分发权限已核清。

因此当前 T02 可以继续做不输出原始定义的结构分析、元数据追溯和匿名聚合；**不能**把标签直接当成独立 source family，不能做来源家族 bootstrap/holdout，也不能据此释放正式盲审包。分支结构变化与定义保真仍是并列的研究结果；这份文档只报告来源可追溯性。

## 高占比标签核对

| 冻结包自报标签 | evidence 项 / 记录数 | 已能确认的上游背景 | 本地记录级状态 | 解除 unresolved 所需证据 |
|---|---:|---|---|---|
| `GCIDE 0.54` | 1,580 / 1,573 | GNU GCIDE 项目说明其版本及 GPL 条款；项目文字同时包含来源异质的历史词典材料。 | 权利日志有提供方声明，但明确未核实版本与 payload 对齐。 | 冻结生成器/清单对 0.54 发行包的绑定、记录级标识/散列对应、适用条款与署名/派生义务核对。 |
| `Kaikki/Wiktextract targeted OEWN gap` | 881 / 878 | Kaikki 的 raw-data 页面提供 Wiktionary 原始抽取；Wiktionary 说明贡献者文本许可，并提示外部材料可能另有条款。 | 未匹配本地权利日志。标签对应的 881 个 evidence 项有 `raw-sha256` 形态摘要，但哈希对象未识别，且不能绑定到某个 Kaikki/Wiktionary dump。 | 生成端对摘要对象的定义、上游 dump/commit/条目标识映射、第三方来源识别及逐项许可。 |
| `MeSH 2026 descriptors` | 356 / 356 | NLM 提供 MeSH 下载和使用条款；条款要求说明所用版本或数据时效。 | 权利日志记有提供方重用条款，但未指派标准许可证；“2026”标签尚不足以证明每条记录与指定发行文件一致。 | 原始下载/文件哈希、版本字段到记录的映射、NLM 条款快照及输出/署名方式复核。 |
| `EMBL-EBI OLS` | 275 / 235 | OLS 是多个生物医学 ontology 的发现与服务入口，不是单一 ontology 或统一许可证。 | 权利日志明确要求按 ontology 与确切快照分别解析。 | 每条 evidence 映射到具体 ontology、版本/发行快照和上游 license；OLS API 返回值不能替代 ontology 本身的授权。 |
| `Kaikki/Wiktextract relaxed definition-term fallback` | 201 / 201 | 同 Kaikki/Wiktionary。 | 未匹配本地权利日志；来源快照 unresolved。 | 同 targeted gap；另须确认 fallback 所用关系/文本在该资源中的来源性质。 |
| `GBIF Species Match API / GBIF Backbone Taxonomy` | 66 / 66 | GBIF 数据使用协议要求保留记录所有权标识、引用数据发布者，并遵守每个发布者选择的许可；GBIF 是服务/发布基础设施，不是所有数据的统一权利人。 | 未匹配本地权利日志。 | API 请求/响应或离线快照、backbone 发行版、dataset/publisher/ownership 标识、DOI 与逐数据集许可。 |
| `Wikidata` | 59 / 59 | 项目公开结构化数据有其项目级复用信息，但具体冻结记录仍须绑定数据命名空间及 dump。 | 权利日志状态是“以结构化数据 namespace 与 exact dump 对齐为条件”；当前未核实这两项。 | 记录级 Wikidata item/namespace 身份、dump 日期/校验和、实际抽取字段及署名要求。 |

上表中的计数为 `source_evidence` 项 / 含该标签的 source record 数，不是目标义项数，也不是互斥来源家族数。同一记录可含多个 evidence 项；多种标签也可能指向同一上游资源。计数来自被忽略的本地聚合文件 `outputs/t02_source_label_rights_reconciliation_20261031_v2.json`，输入哈希及复算命令记录在 [`preposition_relation_schema_protocol.md`](preposition_relation_schema_protocol.md) 的来源审计小节。

## 公开页面能证明什么、不能证明什么

- GNU GCIDE 项目页可证明其项目说明中的版本/许可线索，但不能证明冻结包中的某个 `source_evidence` 已由该确切发布包生成。见 [GCIDE 项目与许可说明](https://github.com/gitGNU/gnu_gcide)。
- [Kaikki raw-data 页面](https://kaikki.org/dictionary/rawdata.html)描述当前提供的原始抽取，不会反向绑定冻结包中未注明日期的本地记录。 [Wiktionary copyrights](https://en.wiktionary.org/wiki/Wiktionary:Copyrights)还提醒外部材料可能有单独条款。
- [NLM MeSH 使用条款](https://www.nlm.nih.gov/databases/download/terms_and_conditions_mesh.html)要求产品标出版本或说明数据可能不是最新；[MeSH 下载页](https://www.nlm.nih.gov/databases/download/mesh.html)说明当前下载入口与格式变化。它们不能替代本地文件和记录版本的核验。
- [OLS 说明页](https://www.ebi.ac.uk/ols4/about)将其定义为多 ontology 服务；[OLS 下载页](https://www.ebi.ac.uk/ols4/downloads)提供服务快照。仍须逐 ontology 查版本及权利。
- [GBIF Data User Agreement](https://www.gbif.org/terms/data-user)要求保留权属标识、引用发布者、遵守发布者所选许可，明确 GBIF 不拥有或托管所有记录的权利。
- [OEWN 2025 release](https://github.com/globalwordnet/english-wordnet/releases/tag/2025-edition)及 [OEWN license](https://github.com/globalwordnet/english-wordnet/blob/main/LICENSE.md)能支撑匹配发布版释义文本的署名/许可路径，但不能自动覆盖混合冻结 payload、被改写文本或超图构造规则。

## 可执行 crosswalk 规格与状态

下一版记录以 `source occurrence` 为最小单位，按下列字段分层；字段缺失要保留缺失状态，不可由标签猜填：

1. **内部链接**：目标、图规则/OR 分支、payload checksum、source evidence ordinal。内部 ID 和 locator 仅留在受控本机数据，不进入 Git 文档或公共结果。
2. **来源身份**：原始 provider、资源名称、条目/记录 ID、source family、各字段证据来源。可验证到 provider 但无法验证资源家族时，分别记录，不合并成一个“已确认”状态。
3. **版本身份**：发行版/commit/dump、生成日期、归档哈希、摘要算法及被摘要对象。只有摘要格式正确而无对象定义时标 `version_unresolved`。
4. **权利状态**：适用 license/条款版本、署名文本、再分发/改编条件及来源 URL；状态只允许 `evidence_found_unverified`、`record_bound`、`cleared_for_scope`、`restricted`、`unresolved`。`cleared_for_scope` 必须由具备授权判断职责的人确认，不能由代码自动赋值。
5. **家族与抽样资格**：source family 判定理由、与规则开发样本的隔离关系、允许的分析范围、排除原因。不能证明独立来源的记录归 `family_unresolved`，不进入 family holdout。

**互斥版本/身份失败标签**：`exact_release_match`、`normalized_only`、`different`、`missing_identity`、`source_unresolved`、`rights_unresolved`。身份、版本和权利是不同维度，最终状态须保留三者，不能把单一互斥标签误当成全部审查结论。

**下一工作门**：先用本机受控生成记录追溯 top-volume 标签的源快照及生成代码；只输出每家族覆盖目标数、分支数、版本绑定率、权利状态计数及输入哈希。若这些本机生成映射或发布许可不存在，应把类别保持 `unresolved`，停止确认性语义样本设计，并向负责人汇报实际可用总体，不用公开网页声明代填。

## 复现与边界

从 `hypergraph_analysis_exploration/` 运行（输出文件须是不存在的新路径）：

```powershell
python -m src.analysis.audit_preposition_source_provenance --bundle ../OEWN --out outputs/t02_source_provenance_audit_20261031_v4.json
python -m src.analysis.reconcile_t02_source_label_rights --audit outputs/t02_source_provenance_audit_20261031_v4.json --rights-log sources/source_release_rights_evidence_2026-10-06.json --out outputs/t02_source_label_rights_reconciliation_20261031_v4.json
python -m unittest tests.test_audit_preposition_source_provenance tests.test_reconcile_t02_source_label_rights -v
```

这些命令只做聚合审计与精确/规范化标签 join；它们不形成逐记录 crosswalk，也不清权、不标注语义、不产生独立来源家族抽样框。输出会写入 ignored 本机目录，禁止把原始 payload 或这些输出整体加入 Git。
