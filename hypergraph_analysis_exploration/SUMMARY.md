# Current Project Status (2026-10-12, Phase277)

Phase277 compared the 2026-09-30 senior-meeting assignment with current work. The initial graph-analysis task was followed; unsupported ordinary-graph interpretations have since been withdrawn. Reproducible AND/OR closure/witness audits align with understanding the supplied hypergraph, but the 100k-sense gloss-logicization milestone, adjudicated source-support gold, and real NLI/entailment evaluation remain incomplete. See [meeting alignment and briefing script](../report/project_review_2026-10-29-current.md).

Phase276 added an official full-text targeted review of ACL 2026 Lingua-Graph. It narrows broad novelty claims around shared explicit graphs and reusable local substructures; the paper's sentence-level representation/hostability task differs from this project's sense-bound gloss-to-Horn support and proof replay. The narrower project contribution remains unverified pending adjudicated gold and matched experiments. See [Phase276 briefing](../report/project_review_2026-10-29-current.md).

Phase275 audited the historical Phase1 claims and seven non-JSON outputs. The current 85-basis closure and selected/minimum-witness depth distribution are supported as structural properties of the pinned positive-Horn graph; the old cycle count, power-law regression, small-world claim, and “mutual definitions” interpretation are unsupported. Two legacy scripts now resolve the configured bundle and write within the project, but retain exploratory methods. Five PNGs expose source/sense identifiers and remain uncleared. See [Phase275 report](../report/research_progress_deep_review_2026-10-12_phase278.md).

Phase274 refreshed the local output release-surface inventory: 212 files, 22 text-key hits, 41 identity/provenance-key hits, and 53 Git-ignored artifacts. Four unignored text-key hits were shape-checked as integer metadata counts or an algorithm-description string. Phase275 manually reviewed the seven non-JSON artifacts; two figures expose source/sense IDs and the scripts remain exploratory, so neither content review nor path fixes clear them for publication. See the Phase274 report and [Phase275 follow-up](../report/research_progress_deep_review_2026-10-12_phase278.md).

Phase273 reconciled a stale `pending` status in the 2026-10-05 ACL candidate snapshot: APF had already been retained and targeted-screened in the 2026-10-06 log. This turn supplements its ranking-validation details and limits; it adds no candidate or unique paper. APF is cross-domain prior art for natural-language engineering requirements → executable optimization formulations, but does not address WordNet sense-bound gloss spans, typed Horn rules, or source-bound witness replay. No project experiment or model was run. See Phase273 report and the [prior screen](sources/literature_screening_log_2026-10-06_acl_formalization_2026.json) plus [supplemental log](sources/literature_screening_log_2026-10-08_apf_findings_acl2026_phase273.json).

Phase272 reran the full frozen hypergraph and minimum-depth witness audits into a fresh output directory. Both outputs are byte-identical to Phase213. The bundle lock, 110,425 witnesses, AND/OR closure, and minimum-depth certificates pass. Across 85 basis deletions, selected-witness descendants overestimate exact non-seed closure loss 66 times and match 19 times, reinforcing that exact deletion impact requires recomputing closure. This supports structural replay for the pinned bundle only; it does not establish gloss support, licensing, NLI results, or research effects. See [Phase272 report](../report/research_progress_deep_review_2026-10-12_phase278.md), [machine record](sources/frozen_graph_witness_replay_2026-10-08_phase272.json), and [outputs](outputs/phase272/).

Phase271 reran the synthetic gloss→OEWN bridge with validator 0.3: one resource query replayed, the two-row bridge passed, and the three success reports matched byte-for-byte in an independent repeat. Bad manifest pin, a missing unresolved candidate, and a query triple mismatch with matching report pins failed closed. The v3 input preflight still has 0 returns, no signed protocol, no external registration, and no distribution authorization. These runs establish synthetic software wiring only; no real gloss support, human gold, model result, or Track A effect was measured. See Phase271 report, [machine audit](sources/phase271_bridge_replay_audit_2026-10-08.json), and [outputs](outputs/phase271/).

Phase270 full-text screened ProofRank and clarified that formal correctness/replay and witness structure do not establish evidence-chain usability or explanation quality. The title appears in NeurIPS 2026 official Downloads/Poster pages, while arXiv v2 says accepted at the ICML 2026 AI for Math workshop; the relationship/track is unresolved. The refreshed index contains 2,058 records across 147 logs and 1,939 conservative clusters; the matrix crosswalk has 315 links / 300 targets, with 292 matched targets and 0 unmatched scholarly-reference candidates. These are traceability counts, not systematic-review coverage. No paper result was reproduced and no project tests/models were run. See Phase270 report, [screening log](sources/literature_screening_log_2026-10-08_proofrank_phase270.json), [audit](sources/phase270_proofrank_research_update_audit_2026-10-08.json), and [outputs](outputs/phase270/).

Phase269 upgraded the existing ACL Findings 2026 validity/plausibility paper from abstract-only to official full-text screening. Its 1,280 syllogisms use ten taxonomic term triples; the hypernym control reuses those triples, so this is a content-effect diagnostic neighbor, not WordNet gloss-span gold or a lexical generalization baseline. The refreshed index contains 2,057 records across 146 logs and 1,938 conservative clusters; 135 records are full-text screened. Matrix crosswalk: 314 link occurrences / 299 targets, 291 matched targets, and 0 unmatched scholarly-reference candidates. These are traceability counts, not review-coverage estimates. No paper result was reproduced. The [research-positioning memo](docs/research_positioning_and_prior_work.md) and [claim-evidence crosswalk](docs/research_claim_evidence_crosswalk_2026-10-08_phase204.md) now reflect Phase267–269 boundaries. See Phase269 report, [screening log](sources/literature_screening_log_2026-10-08_validity_plausibility_fulltext_phase269.json), [audit](sources/phase269_validity_plausibility_fulltext_audit_2026-10-08.json), and [outputs](outputs/phase269/).

Phase268 revalidated that the legacy claim-review `/0.1` schema/validator/exporter cannot represent Track A's separate raw-gloss and rendered-premise hashes/spans, edge-surface-condition keys, and independent panel provenance. Track A v1 remains a draft; no schema, candidate, labels, or splits were created. A new contract still depends on resolving estimand, population, POS/surface scope, panel and statistical-unit choices, plus rights/responsibility gates. See Phase268 report and [compatibility audit](sources/track_a_contract_compatibility_audit_2026-10-08_phase268.json).

Phase267 full-text screened a new close-work paper, *The Faithfulness Gap* / BPF / DriftBench (arXiv v1; author-attributed to an ICML 2026 workshop, not independently verified as an ICML main-conference paper). It directly rules out broad novelty claims around proof-validity vs. NL/formal faithfulness and contrastive drift probes. The remaining project hypothesis is narrower: release/sense-bound gloss-span support for typed directional Horn rules, connected to source-linked proof replay and lexical NLI on matched candidates. The paper reports 2,183 NL/Lean pairs and 89.6% controlled-split detection at 3% FPR; we did not reproduce these results. A review of the v1 formal argument found a missing probe-separation assumption in Proposition 4.2; Theorem 8.2's stated Occam derivation also needs repair, though a different Markov argument may support a similar bound under its strong uniform-witnessability assumption. Updated the log, nearest-work matrix, evaluation boundaries, and dedup/crosswalk; see Phase267 report, [screening log](sources/literature_screening_log_2026-10-08_faithfulness_gap_driftbench_phase267.json), [audit](sources/phase267_faithfulness_gap_research_update_audit_2026-10-08.json), and [outputs](outputs/phase267/).

Phase266 re-ran the locked v3 input preflight and replayed a bounded structural witness plus its ground Datalog bridge. All 21 preflight checks passed (400 frame items, 24 strata, 0 annotation returns); the protocol remains unsigned and external distribution unauthorized. The current witness replay passed with 3,596 nodes, 14,923 dependency edges, and 3,512 rules, and its report matched Phase148 byte-for-byte. This supports a replayable formal example only; it does not establish gloss-span semantic support, WSD correctness, open-world entailment, licensing, or method effectiveness. CodeGraph was already initialized and up-to-date, so no re-index occurred. See Phase266 report, [machine audit](sources/phase266_current_state_audit_2026-10-08.json), and [replay artifacts](outputs/phase266/).

Phase265 upgraded the existing ACL 2026 CoPE record from selected-section screening to targeted full-text screening; it is not a new paper inclusion. CoPE’s planner/solver-validity metric may not catch an unfaithful NL-to-formal encoding, which motivates separate measures for gloss-span support, typed logic/proof replay, and downstream utility. The refreshed index contains 2,055 records across 144 logs, grouped into 1,937 conservative clusters; the matrix has 313 link occurrences / 298 targets, with 290 targets matched and 0 unmatched scholarly-reference candidates. These are traceability/depth counts, not systematic-review coverage or novelty evidence. See Phase265 report, [screening addendum](sources/literature_screening_log_2026-10-08_acllong2026_cope_fulltext_phase265.json), [audit record](sources/phase265_research_update_audit_2026-10-08.json), and [outputs](outputs/phase265/).

Phase264 screened the NALOMA 2026 paper “Negation in Reasoning Traces: Interpretable Signals of Correctness and Provenance” and clarified that its provenance task concerns author/model attribution, not source lineage or proof-witness provenance. Its human annotation agreement was κ=.68 and LLM-human agreement κ=.37/.38; the authors treat automated labels as weak proxies. The new record raises the current index to 2,054 records / 1,937 conservative clusters across 143 logs. The current matrix has 313 external-link occurrences / 298 unique targets; 303 occurrences and 290 targets match logs, with 8 unmatched non-paper resources and 0 unmatched scholarly-reference candidates. This remains targeted literature work, not a systematic-search coverage or novelty claim. See Phase264 report, [screening record](sources/literature_screening_log_2026-10-08_naloma2026_negation_traces_phase264.json), [audit record](sources/phase264_research_update_audit_2026-10-08.json), and [derived outputs](outputs/phase264/).

Phase263 rebuilt the Phase250–252 literature dedup snapshots using the current CLI and the retained 137/138-log input sets. Historical summaries and cluster assignments match; full JSON differs only in the implementation hash and current extraction of DOI `10.1145/3770855.3817808` into P00200 (cluster and record fields). The old producer source is still missing, so this is a current-version reconstruction, not a recovery of that exact script. See Phase263 report, [machine comparison](sources/literature_log_legacy_output_replay_2026-10-08_phase263.json), and [reconstructed indexes](outputs/phase263/).

Current matrix crosswalk (Phase262) found 312 external-link occurrences / 297 unique targets: 302 occurrences and 289 targets match structured screening logs; the 8 unmatched targets are non-paper resources (5 project/code resources and 3 official WordNet documentation/data URLs), leaving 0 unmatched scholarly-reference candidates. This is bibliography traceability only, not systematic-search coverage. The current Phase256 literature dedup index replayed byte-for-byte from 142 logs. Phase250–252 outputs record an earlier implementation hash whose source script is absent from this uncommitted workspace; their historical replay claims remain documented, but exact producer reconstruction is not possible here. See Phase262 report, [crosswalk output](outputs/phase262/closest_work_log_crosswalk.json), and [source record](sources/closest_work_current_matrix_crosswalk_2026-10-08_phase262.json).

863 untracked, non-ignored paths / 271,109,408 bytes at capture, versus 812 / 240,093,564 bytes in Phase247. There are 805 unchanged hashes, 7 changed paths, 51 new paths, and no baseline paths missing. New paths remain unreviewed; 25 files matched a narrow restricted-context keyword screen, which is not a privacy, rights, or publication-clearance audit. No staging or commit occurred. See Phase261 report and [machine inventory](sources/repository_current_snapshot_inventory_2026-10-08_phase261.json).

The research goal remains active. Phase260 checked the WN30-lfs generation chain against the primary paper, the ISI LFToolkit page, the published artifact, and the final XML archive. A 32,613-byte compiled JAR is available (SHA-256 `bde5df2a…b57e0`), but current PATH has no Java runtime and the WN30-lfs-specific transformation rules, Charniak parse trees/config, GlossTag sense-assignment inputs, and per-synset logs were not located. The paper describes the resource pipeline, but the final archive is not a producer bundle, so no WN30-lfs reproduction or per-ID parse-failure attribution is claimed. LFToolkit documents partial output and potentially mislinked variables; this makes `partial/complete` processing labels unsuitable as semantic-quality gold without a resource-specific status mapping. See Phase260 report and [source record](sources/wn30_lfs_producer_reproducibility_2026-10-08_phase260.json).

The research goal remains active. Phase259 checked WN30-lfs source lineage and local XML schema against the primary paper and Princeton sense-index documentation. The paper identifies WordNet 3.0 glosses; the archive has 104,357 entries, 104,321 unique keys and 36 duplicate-key occurrences, but no entry offset or WordNet-release attribute. Its XML root `version="1.0"` is not a WordNet version. Since WordNet sense numbers/offsets vary by release and WN30-lfs does not use the release-independent WordNet `sense_key`, keep Phase257's strict 104,081/117,659 (88.4599%) identity coverage and leave 174 keys/13,578 absent IDs unresolved as to individual cause. The schema audit preserves no gloss/LF text; it makes no semantic or rights claim. See Phase259 report, [CLI](src/analysis/audit_wn30_lfs_source_schema.py), [output](outputs/phase259/wn30_lfs_source_schema.json), and [source record](sources/wn30_lfs_source_schema_2026-10-08_phase259.json).

The research goal remains active. Phase258 diagnosed the 174 WN30-lfs keys that failed Phase257's strict WordNet 3.0 identity join. Exact normalized-gloss matching found 23 unique same-lemma/POS candidates, 1 ambiguous same-lemma/POS case, 38 unique same-POS/different-lemma candidates, 38 cases with same lemma/POS but no exact gloss match, and 74 with no exact lemma/POS or gloss candidate. These are diagnostic candidates, not identity corrections; one apparent unique gloss match even conflicts with the keyed named entity. The strict 104,081/117,659 (88.4599%) coverage remains unchanged. The new CLI and output replay byte-for-byte, and the output does not copy gloss text. No reason for all unmatched cases, semantic LF result, matched baseline, or project effect is established. See Phase258 report, [diagnostic CLI](src/analysis/audit_wn30_lfs_unmapped_entries.py), [machine output](outputs/phase258/wn30_lfs_unmapped_diagnostic.json), and [source record](sources/wn30_lfs_unmapped_entry_diagnostic_2026-10-08_phase258.json).

Phase257 built a reproducible exact crosswalk from WN30-lfs `lemma#pos#sense_number` keys through Princeton WordNet 3.0 `index.sense` to the release's synset offsets. The 3.0 index and four data files agree on 117,659 synset IDs; WN30-lfs strictly maps 104,081 unique IDs (88.4599%), with 13,578 absent and no mapped IDs outside the release. That result establishes identity coverage, not LF semantics or license status. See Phase257 report and [crosswalk artifacts](outputs/phase257/).

Phase255 followed the Phase254 WordNet gloss→logic collision through XWN/ILF-WN/WN30-lfs and screened Rus 2004's logic-form evaluation. Its historical bibliography-index counts remain preserved below and in [Phase255 outputs](outputs/phase255/).

## Previous milestone: Phase254

The research goal remains active. Phase254 found and full-text screened a major direct historical collision: Moldovan & Rus (FLAIRS 2001) already transformed WordNet glosses into sense-tagged logic forms with argument structure and AND/OR encodings, and demonstrated QA use; their 81% figure is coverage against manually prepared LFTs, not semantic accuracy. Their ACL 2001 companion was verified at abstract/metadata depth and is not counted as an independent system. This withdraws any “first WordNet gloss→logic/AND-OR/QA” claim. The current `compile_annotations` path compiles human-supported structured claims into a restricted Horn/Datalog program and preserves provenance; it does not itself parse raw English glosses, and the checker does not validate gloss-to-rule semantic fidelity. The remaining source-span support, typed-rule and independently replayable witness direction is still a hypothesis pending exact baseline comparison and semantic gold. Phase254 also screened WSL and homonymy disambiguation papers to separate contextual sense-linking and coarse-grained sense identity from gloss-internal rule support. See Phase254 deep review, [architecture boundary record](sources/current_logic_pipeline_prior_art_boundary_phase254.json), [structured log](sources/literature_screening_log_2026-10-08_phase254_direct_prior_art.json), [matrix](docs/closest_work_comparison.md), and [Phase254 index/crosswalk](outputs/phase254/).

The research goal remains active. Phase253 screened five remaining unmatched scholarly references at full text, corrected the Word Ladders citation from the wrong ACL Anthology record `.18` to `.7`, and updated the closest-work matrix. The matrix now has 280/285 distinct targets linked to structured screening logs; all five unmatched targets are project/code resources. This is bibliography traceability, not search coverage. The updated index contains 2,042 records in 1,927 conservative clusters across 139 logs. See Phase253 deep review, [full-text addendum](sources/literature_screening_log_2026-10-08_phase253_fulltext_addendum.json), and [Phase253 index/crosswalk](outputs/phase253/closest_work_log_crosswalk.json).

Phase253 confirms major prior art for WordNet definition→graph→interpretable entailment (WordNetGraph), gloss-derived sense-level WordNet links (Gulbe et al.), fine-grained sentence provenance (TROVE), and programmatically verified FOL traces (FOL-Traces). Broad claims in these areas must be excluded. The still-unverified narrow hypothesis is sense/release-bound gloss-span support for directional typed Horn literals and independently replayable AND/OR source-bound witnesses. No semantic gold, matched baseline, paper-level effect, release clearance, or AAAI 2027 ownership boundary change is established.

The research goal remains active. Phase251 crosswalked 295 external-link occurrences (285 distinct targets) in the closest-work matrix to the Phase250 literature-log index. 273 distinct targets matched; 12 remain unmatched, including 7 scholarly citations and 5 project/repository links. One scholarly item has only a title-only `already_in_matrix` log record. This is traceability coverage, not literature-search coverage. See Phase251 report and [machine crosswalk](outputs/phase251/closest_work_log_crosswalk.json).

The research goal remains active. Phase250 indexed 2,036 titled records across 137 screening logs into 1,923 conservative bibliographic clusters; 88 clusters contain multiple log records, and 3 DOI/year conflicts remain for manual review. This is a navigation/dedup audit of iterative targeted screens, not an exhaustive literature denominator or systematic review. See Phase250 report, [index builder](src/analysis/audit_literature_log_deduplication.py), and the preserved [Phase251 baseline index](outputs/phase251/literature_log_dedup_index.json).

The research goal remains active. Phase249 full-text screened ACL 2026 SATQuest, a PySAT-verified CNF reasoning benchmark factorized by instance, task type, and presentation format. This narrows broad novelty claims around verifier-backed logical evaluation and controlled multi-format testing. SATQuest is limited to synthetic propositional CNF; it does not address WordNet senses, gloss-span support, typed Horn induction, or source-bound proof witnesses. Its 80-instance LLM-judge audit with 10% human checking is not lexical semantic gold. See Phase249 report and [screening log](sources/literature_screening_log_2026-10-08_satquest_acl2026_phase249.json).

The research goal remains active. Phase248 screened the 58 Phase247 sensitive-review paths: no personal-directory, email, or credential-assignment patterns were found; 21 files retain AAAI 2027/internal-boundary references and remain internal-only pending individual review/redaction. The lock file references an answer key that Git ignores; the fixture is synthetic. This supports a private snapshot review only; public-release and rights clearance remain open. No staging or commit occurred. See Phase248 report and [machine record](sources/repository_sensitive_path_review_2026-10-08_phase248.json).

The research goal remains active. Phase247 created a per-path SHA-256/size ledger for the initial Git candidate set: 812 files / 240,093,564 bytes. Initial handling classes identify 405 core project-file candidates, 200 research-record candidates, 58 sensitive-review paths (including 21 AAAI/internal-boundary keyword matches), 9 legacy files, 108 generated outputs, and 32 external/retrieval corpus snapshots. These are review categories, not an approved publication allowlist; no files were staged or committed. See Phase247 report and [machine record](sources/repository_initial_snapshot_review_2026-10-08_phase247.json).

The research goal remains active. Phase246 reran the Phase245 noun-slice genus diagnostic to an independent scratch path; its JSON was byte-identical to the saved Phase245 output (SHA-256 `18c2e335…53f500b`). This confirms repeatability on the current host and pinned inputs only, not cross-environment reproducibility or semantic correctness. Repository review also confirms that the initial Git snapshot still needs a per-path publication allowlist because source snapshots and large historical candidate corpora are mixed with code and reports. No files were staged or committed. See Phase246 report and [machine record](sources/track_a_genus_resource_replay_2026-10-08_phase246.json).

The research goal remains active. Phase245 measured the existing first-exact-noun-lemma genus heuristic on the 252 noun targets in the locked 400-item v3 frame. It produced a candidate for 247/252 definitions (98.0% coverage); against 264 direct noun-hypernym edges in the same OEWN release, pair precision/recall/F1 were 10.7%/36.7%/16.5%. These are same-release resource-alignment diagnostics, not semantic-support gold, independent validation, or matched model effectiveness. Track A choices remain pending. See Phase245 report and [machine record](sources/track_a_genus_resource_diagnostic_2026-10-08_phase245.json).

The research goal remains active. Phase244 rehashed every unique source payload referenced by the frozen sense index: all 115,235 payloads (18,734,636,389 bytes) match the frozen checksums, with zero duplicate path references and malformed index records. The new aggregate report is byte-identical to Phase210. This confirms current bundle byte consistency only; source rights remain not assessed and gloss semantics are unverified. See Phase244 report and [machine record](sources/source_payload_full_rehash_2026-10-08_phase244.json).

The research goal remains active. Phase240 full-text screened a NeurIPS 2025 method paper on APTP, an independent checker for binary activation-pattern proofs of DNN verification UNSAT. This narrows broad novelty claims around producer/checker separation and replayable proof artifacts. The paper does not address WordNet gloss support or source-only AND/OR Horn witnesses; its checker also relies on external MILP/LP solvers. Targeted screen only, with no runtime/schema changes or tests. See Phase240 report and [machine log](sources/literature_screening_log_2026-10-08_neurips2025_independent_proof_checking_phase240.json).

The research goal remains active. Phase239 adds a full-text ICLR 2026 neighbor, HiCEM: ImageNet concept labels derive from WordNet hypernym ancestors, and the paper studies hierarchical concept embeddings and interventions. This narrows broad novelty claims around WordNet-based hierarchical concepts, but does not cover natural-language gloss parsing, lexical source-span support, typed Horn rules, or proof replay. One other ICLR logic-representation paper is recorded at abstract-only depth because its official PDF could not be retrieved. This is a targeted screen, not a proceedings census. See Phase239 report and [machine log](sources/literature_screening_log_2026-10-08_iclr2026_hierarchical_concepts_wordnet_phase239.json).

The research goal remains active. Phase238 corrects Phase235's overly broad architecture claim: a strict single-sense/claim proof-NLI route now replays certificates, checks adjudicated supported rules and source-only facts, binds NLI premise/hypothesis hashes to the proof claim, optionally re-verifies frozen source payloads, and routes from hash-pinned exports after removing test gold. Track A still lacks an explicit relation-edge/surface/condition → annotation claim → candidate foreign-key chain; the exporter aliases `candidate_id` as `claim_id`, but the schema does not enforce that identity. This is a static interface audit only; no schema/code changes or tests were run. See Phase238 report and [machine record](sources/track_a_proof_nli_export_join_audit_2026-10-08_phase238.json).

The research goal remains active. Phase237 corrects a deduplication error: the LREC 2026 OEWN hyperbolic-hierarchy paper had already been full-text screened on 2026-10-05; this pass only adds that existing evidence to the closest-work matrix and rechecks official metadata. No new paper or candidate denominator was added. Phase236 reconciles a draft NLI estimand inconsistency without approving the protocol. Phase232's full-text LogicTree-RAG screen and Phase231's fixed-bundle sensitivity evidence continue to narrow broad novelty claims, while Phases229–230 remain limited to explicit structural interventions. Annotation is still unauthorized and Track A unlaunched; there is no adjudicated WordNet gloss-span→typed Horn source-support gold, matched effect evaluation, release clearance, or paper-level novelty evidence.

- [Phase219: Track A v1 design draft](docs/track_a_protocol_v1_draft.md)
- Phase219 deep review
- [Phase219 machine design record](sources/track_a_protocol_design_review_2026-10-08_phase219.json)
- Phase218: annotation and Track A launch-readiness audit
- [Phase218 machine audit record](sources/annotation_and_track_a_launch_readiness_audit_2026-10-08_phase218.json)
- Phase217: literature boundaries for faithfulness, validity, and plausibility
- [Phase217 machine screening log](sources/literature_screening_log_2026-10-08_faithfulness_validity_plausibility_phase217.json)
- Phase216: replayable minimum-depth alternative source map
- [Phase216 machine record](sources/minimum_depth_alternative_source_map_2026-10-08_phase216.json)
- Phase215: minimum-depth alternative source provenance audit
- [Phase215 machine record](sources/minimum_depth_alternative_source_audit_2026-10-08_phase215.json)
- Phase214: NLI calibration/proof-route contract review
- Phase213: frozen graph and witness replay
- [Current readiness audit](docs/research_readiness_audit.md)
- [Evaluation readiness matrix](docs/evaluation_readiness_matrix.md)

---

## Phase 182（2026-10-08）：COLM 2026 层次化机检证明近邻

核读 Goedel-Code-Prover：系统从 Lean 形式规格出发，以辅助引理分解、proof reconstruction 和 Lean kernel 检查形成层次化 code-proof 搜索；427 项上报告 62.0%，但与 pass@128 基线非 compute-matched。该先例排除把一般 proof tree / 层次化分解 / 机检证明作为宽泛新意；它不处理 WordNet gloss 转规则或 source-span 支持。本阶段仅单篇定向筛读，无项目运行、gold、effect 或 novelty 证据。见Phase182报告与[机器日志](sources/literature_screening_log_2026-10-08_colm2026_hierarchical_code_proof.json)。

## Phase 178（2026-10-08）：Horn 闭包空 body 语义修正

静态审阅发现通用 AND/OR `closure()` 遗漏空 body Horn 子句的空合取为真语义；已改为将对应 head 纳入初始传播队列。Phase175 冻结 bundle 中空子句数为 0，既有冻结图数字不受影响；其他调用方影响到 basis sensitivity 与 flattening ablation。未运行测试或复算 CLI，行为验证仍待后续。见Phase178报告。

## Phase 177（2026-10-08）：ACL/COLM 可执行逻辑形式与过程监督近邻

筛读 ACL Findings 2026 SELF-KBQA 与 COLM 2026 VPS 官方/作者全文。结构化 KB 子图引导可执行 logical-form generation、结构化过程 claim 的确定性验证均有近期先例；两者都不判断 WordNet gloss span 对方向性 typed Horn rule 的支持，也不提供 source-only witness replay。更新相关工作、最近工作表、研究定位和筛读协议；选篇筛查，不是 proceedings census/系统综述，无项目实验、gold、effect 或 novelty 结论。详见Phase177报告与[结构化日志](sources/literature_screening_log_2026-10-08_structural_kbqa_and_process_verification.json)。

## Phase 176（2026-10-08）：证明重放与 NLI 来源路由静态审计

CodeGraph 已初始化且索引最新。静态核对 NLI 导出、dev 校准、test gold 剥离、证明证书重放、实际规则/fact 来源绑定及其 IID/人工裁决边界；实现与文档基本相符。未运行测试、模型或人工标注；没有增加效果证据。见Phase176报告与[机器审计](sources/verified_reasoning_route_contract_audit_2026-10-08_phase176.json)。

## Phase 181（2026-10-08）：可复跑开发环境快照与当前发布 inventory 复核

新增 `src.analysis.audit_reproducibility_environment` 与当前机器快照，现可从仓库根目录复算维护 Python 源码 AST/import 状态、CI 静态矩阵、依赖声明、代码树/config/lock/workflow 哈希及外置 bundle 路径。当前 133 个 Python 文件 AST 无错误、无静态第三方导入；Ubuntu 3.10–3.13 与 Windows 3.10/3.13 只是配置矩阵。另运行只读 `verify_data_release_inventory`，inventory/本地 OEWN ZIP 哈希 CRC/bundle manifest 计数均一致，但项目状态仍为 `not_cleared_for_public_release`。未运行测试、CI、模型或语义实验；该快照不等于 bundle 全量 integrity/source-payload 重放。见Phase181报告与[机器快照](sources/reproducibility_environment_audit_current.json)。

## Phase 180（2026-10-08）：EMNLP 2026 论文题录可用性刷新

核对官方 conference site、main accepted-paper listing、CFP 与 ACL Anthology targeted results。EMNLP 将于 2026-10-24 至 10-29 举行；当前 official main-paper page 可访问但尚无可见论文题录，本轮 Anthology topic queries 也未获得可核对的 EMNLP 2026 proceedings 论文。覆盖状态保持 pending；未据搜索未命中推断不存在相关工作，也未新增论文/基线/新颖性判断。待正式题录公开后重筛。见Phase180报告与[机器日志](sources/literature_screening_log_2026-10-08_emnlp2026_availability_refresh.json)。

## Phase 179（2026-10-08）：basis 删除影响比较口径更正

复核 Phase175 的 85 条逐 basis 记录，发现旧的 53 高估/19 低估/13 相等比较把含被删根节点的 exact closure loss 与不含起点的 witness descendants 混算。全部 85 个 basis 均未被重推出，旧 19 个“低估”都只差被删根节点。统一排除根后为 66 高估、19 相等、0 低估；集合级核对中 0 个精确非根损失落在 descendants 之外，另有累计 98,573 个 descendant 场景-节点项在删除后仍可推出，印证未选 OR 替代分支造成高估。机器输出新增 exact non-seed loss / aligned difference / 集合差，保留原字段；Phase6 与 Phase175 输出均已重跑且完整性检查通过。未运行测试、模型或语义实验。见Phase179报告。

## Phase 175（2026-10-08）：冻结 AND/OR 图与 witness 当前复算

当前 frozen bundle 的 manifest/checksum/lock、完整 AND/OR closure、nodes↔heads、hyperedges↔rules 和 110,425/110,425 witness 结构证书全部通过。85 个 basis 单项删除均使精确 closure 下降。Phase175 初次对比的 13/85 相等统计后来发现含根口径不一致，已由Phase179更正为统一排除根后的 19/85 相等、66 高估、0 低估；删除影响仍需完整 AND/OR closure 重算。最小深度统计与 Phase14 机器结果逐字节一致，现有 selected witness 全部已在最小深度；这不证明 gloss 的自然语言蕴含或 basis 的全局最小性。Phase175 时未改源代码/schema/bundle/data，未运行测试/模型/实验/标注；Phase179 更新了比较实现和两份结构输出。详见Phase175报告、[冻结审计](outputs/phase175/frozen_hypergraph_current.json)与[最小 witness 审计](outputs/phase175/minimum_witness_current.json)。

## Phase 174（2026-10-08）：ACL Findings 的推理时 NL2FOL 纠偏

官方全文筛读 LSEG：逻辑保持输入变体、layer-wise hidden-state intervention 和内部熵触发已进入 ACL Findings 2026；其逻辑等价提升不能外推为 gloss-span source support。项目需区分形式等价、type/proof/witness validity 与 sense-bound source-span semantic support。它不是本项目 matched baseline；此为单篇 out-of-frame targeted discovery，不改 ACL v6 固定候选分母，不构成系统综述或 novelty proof。未跑模型/论文代码/项目测试。见Phase174报告与[结构化日志](sources/literature_screening_log_2026-10-08_lseg_nl2fol_findings_acl2026.json)。

## Phase 173（2026-10-08）：PMC OA 逐篇许可边界与交叉表更新

PMC 官方说明 Open Access Subset 中许可按文章变化，应以文章自身声明为准，且嵌入材料可能有独立版权。当前两个候选 payload 未绑定文章身份、source_version 或许可条款；登记来源族级规则不构成清权。rights log 为 18 个标签，exact-label 命中为 25/90 profiles、2,348/3,595 profile-payload 计数；仍有 65 个 profile/1,247 个计数未匹配，`release_clearance` 仍为 `not_assessed`。未改代码/schema/bundle/data；未跑测试、模型、实验或标注。见Phase173报告及[交叉表](outputs/phase173/source_rights_crosswalk_current.json)。

## Phase 172（2026-10-08）：Glottolog 5.3 官方证据与本地绑定核查

官方 Glottolog 页面列出 5.3 发行文件并声明 CC BY 4.0；候选 profile 的 3 个本地 payload 缺少 source_version/source_ontology，未与具体发行文件或哈希绑定。将来源家族级证据录入 rights log 后，exact-label 命中由 22/90 profiles（2,343/3,595 profile-payload 计数）增至 23/90（2,346/3,595），仍有 67 个 profile/1,249 个计数未匹配。总体 `release_clearance` 仍为 `not_assessed`，没有本地来源或 bundle 再分发许可结论。未改代码/schema/bundle，未跑测试、模型或实验。详见Phase172报告和[机器交叉表](outputs/phase172/source_rights_crosswalk_current.json)。

## Phase 171（2026-10-08）：来源权利 crosswalk 与 OEWN witness 现态复算

当前 rights log SHA 与旧 Phase52 输入不同，但 exact-label 命中维持 22/90 profiles、2,343/3,595 profile-payload 计数；仍有 68 profiles/1,252 计数未匹配，不能称为 license coverage。六条 OEWN release-matched payload 重放得 6/6 sense-index identity、11/11 clause-hyperedge join、6/6 witness source checksum；只有 2/6 selected witness documents 同时绑定候选 payload 与匹配 ILI/definition hash，另 2 仅在非选中 active clause、2 不在 active clause。结构性，不证明 gloss entailment 或 rights clearance。保留旧 Phase52/89 工件。详见报告。

## Phase 170（2026-10-08）：近期逻辑评测与语义公式距离

定向核读 CoNLL 2026 主会与 NALOMA 2026 workshop 官方全文：前者证明 verifier 选择和逻辑操作类别会影响评测结果，且需要把真正生成错误、off-LF-but-entailed 与验证器假阴性分开；后者用 Presburger 模型集合距离缓解字符串指标问题，但合成任务仍常丢量词。项目评测因此保留 parse/type、logical equivalence、exact-condition NLI、gloss span 人工支持和 source-only replay 多轴，并分析验证器分歧。两篇都不是 WordNet gloss-support matched baseline。选篇筛查，不是 proceedings census；未运行模型/实验/测试。见Phase170报告与[结构化日志](sources/literature_screening_log_2026-10-08_logic_evaluation_neighbors_phase170.json)。

## Phase 169（2026-10-08）：Track A 实施门槛与协议边界

结构审阅确认现有 400 项 source/gloss 标注锁与拟议的 relation-edge/surface gold + exact-condition NLI study 是不同协议；锁文件只保证输入字节/结构预检，未签 protocol、未外部注册、未授权分发。NLI exporter 的 manifest/hash 校验与 source bundle verifier 提供结构/来源字节完整性控制，但不证明许可、语义支持或校准保证。建议先解决精确来源使用权和研究者协议选择，再冻结独立 Track A frame/manifest；旧锁保持不动。CodeGraph 索引已可用、最新；Markdown 链接审计 0 问题。未改代码/schema/data，未跑测试/模型/标注。详见Phase169报告。

## Phase 168（2026-10-08）：匿名既有稿件归属与新研究定位更新

扫描当前文档与报告中的 AAAI 2027 提法，没有发现将匿名稿件的成果直接归给用户的表述；用户明确声明其不是本人成果。将一处旧报告“用户提供”改为“工作区中的匿名第三方稿件”，避免把材料提供与作者归属混淆。定位备忘录吸收 Phase166–167 的 ACL/AAAI 2026 先例；精确 gloss-span→typed Horn 支持及 source-only replay 仍无项目 gold/matched baseline，仍是假设。没有打开匿名 PDF，也未核验作者、投稿状态或使用许可。见Phase168报告与[更新后的定位备忘录](docs/research_positioning_and_prior_work.md)。

## Phase 167（2026-10-08）：定向筛读 AAAI 2026 四篇正式逻辑/autoformalization 近邻

已核读固定 ontology/gloss 下 NL→FOL + SMT equivalence 与 connective/quantifier perturbations、选择性 symbolic translation + backward reasoning、数学 autoformalization、statutory NL→Prolog execution/abstention。宽泛公式转换/solver 检查、选择性形式化/反向推理、可执行 Horn 系统不能独立作为新颖点；仍无 sense/release-bound gloss-span support gold 或 source-only proof matched baseline。三篇来自主技术轨，tax reasoning 为 special track；单 reviewer 选篇筛查，不是全目录综述。见Phase167报告和[结构化日志](sources/literature_screening_log_2026-10-08_aaai2026_formal_logic_neighbors.json)。未改项目代码/数据、未运行测试或实验。

## Phase 166：ACL v6 WordNet/gloss 2026 切片深筛

对 v6 `wordnet_gloss_lexical_relations` 家族九篇 2026 候选中仍为摘要级的四篇逐条升级/筛查：LKG Latin WSD 与 CEFR WordNet gloss alignment 两篇定向 PDF 章节筛读；UMLS/WordNet definition retrieval 与 Konkani WordNet 两篇摘要级。切片深度从 5 full + 4 abstract 变为 5 full + 2 targeted sections + 2 abstract，输出独立 v6 reconciliation。新证据收窄 gloss+WordNet hypernym LLM-WSD 和 gloss→sense label transfer 的宽泛新意；尚无 gloss-span→typed Horn entailment gold 或 source-only proof matched baseline。见Phase166报告、[结构化日志](sources/literature_screening_log_2026-10-08_acl2026_wordnet_slice_phase166.json)。

## Phase 165：ICLR 2026 formalization / proof DAG / verifier 补筛

四篇官方主会论文定向全文筛读：Mathesis（NL 数学问题→Lean 并以 LLM-assisted semantic scorer 及专家子集评估）、DExploration（Lean proof dependency DAG + topological traversal）、SCI-Verifier（专家标注答案等价）和 Variation in Verification（generator/verifier/difficulty 交互）。因此通用 NL→formal semantic assessment、proof DAG 和 answer-verification benchmark 不能单独支持新颖性；本项目 sense-bound gloss-span→typed AND/OR Horn support + source-only replay 仍是未验证假设。见Phase165报告及[筛读日志](sources/literature_screening_log_2026-10-08_iclr2026_formalization_verification.json)。
2026-10-07 Phase 107：多参考 scorer 核心 API 结果新增 scorer、claim canonicalizer、annotation validator、reference validator 的源码 SHA-256，另写入 Python implementation/version/platform；CLI 另绑定输入文件 hashes；当时 scorer version 升至 0.2。Phase 108 因输出 schema 修正将实现标识升至 0.3。能改善运行定位，但不等于依赖环境锁定或复现验证；未运行 CLI/测试。详见Phase 107。

2026-10-07 Phase 106：为多参考 gold scorer 加入 item-level macro P/R/F1，和现有 micro 分开报告；空 claim 对排除在 macro P/R/F1 外但保留在 exact-match 分母，并给出排除数。与单 reference 子集同步提供 micro/macro。未运行测试/CLI，操作性 estimand 未锁。详情见Phase 106。

2026-10-07 多参考 gloss annotation 原型（Phase 105）：新增 `gloss-analysis-reference/0.1` sidecar validator 与 alternative-aware scorer。每项预测按完整 alternatives 分别比对，不做 claims 并集；claim-set F1 的 best-alternative 聚合与 whole-analysis exact（claim multiset + canonical root AST + status）分开定义，另报告 single-reference 子集及 unresolved 数量。静态审查补上 split 一致性与畸形字段保护；未运行测试/CLI，没有 gold、协议锁或授权。详情见Phase 105。

2026-10-07 Phase 54 非规范来源字段审计：5,625 个 alternative/definition payload checksum 校验重扫；1,202 条非规范 source 字符串覆盖 1,199 个 profile payload 计数，安全 HTTP(S)/FTP host 提取为 0。1,079 个 profile payload 计数仅有 hash-shaped version 且无 download_url，继续标为 unresolved provenance。新审计输出不含 source 原值或 gloss。详见 Phase54。

2026-10-07 Phase 52 来源线索补录：GO `local_go-basic.obo_snapshot` 和 IUPAC Gold Book `v5_local_snapshot` 对应到官方资源/许可页面；分别缺 dated release+hash 与 term ID/revision，尚不能映射 payload。重算 crosswalk 为 22/90 画像、2,343/3,595 profile payload 计数命中。详细边界见 Phase52。

2026-10-07 Phase 51 来源官方证据补录：依据 OEWN 2025+ release/license、Wiktionary copyright 和 ChEBI about/licensing 页面，为三个聚合画像来源新增资源级证据与 payload 映射限制。精确 crosswalk 可定位画像组合由 17 升至 20（2,326→2,334 profile payload 计数）；这不是清权率。保留 Phase50 快照，新增 Phase51 重算与报告。

2026-10-07 Phase 50 来源画像—权利证据日志对账：从已冻结的 Phase 24 聚合画像和官方权利证据日志做 exact-label-only crosswalk。90 个画像组合、58 个来源标签、2,326/3,595 个跨 profile payload 计数命中相同标签；73 个画像组合尚无精确命中（别名未判）。新增 `src/analysis/reconcile_source_rights_coverage.py` 和本机忽略报告 `outputs/phase50/source_rights_crosswalk_audit.json`，记录输入/实现哈希，不读取 source payload。清权、逐版本 bytes 对齐未解决。详见 Phase 50 深度报告。

2026-10-06 v3 标注材料 text-free preflight 复核：执行 `python -m src.analysis.audit_annotation_preregistration_v3_inputs`，`integrity_pass=true`；400 条 frame、24 strata、400 条 blind batch/answer-key 覆盖、release crosscheck 与各锁定 SHA 均通过，回传文件数 0。锁内 `protocol_signed=false`、`distribution_authorized=false` 保持不变；该检查不构成许可审核或分发授权。已将状态记入 research readiness audit；未读取或输出 gloss/task/sense 内容。

2026-10-06 reviewed pipeline fact provenance 与测试释义绑定：复核发现 fact 虽可标记为 `source_assertion` 并带任意非空路径，但证书不记录其 sense/gloss 身份，可能让别的定义来源事实进入目标证明。source-only 输入现要求每个 source fact 声明 `source_sense_id` 和 `source_gloss_sha256`；Datalog 证书保存这些 bindings，独立 verifier 检查回放一致性，route 要求每个实际使用 fact 至少含一个与 test sense/premise gloss 哈希匹配的 source binding。pipeline 版本升至 `/6`；更新 logic 文档与 readiness 状态。binding 仍是调用方声明，尚不核验源文件内容。语法编译与 JSON/静态字段核对通过；未运行测试。

2026-10-06 组合 source-semantics gate 收紧与证据字段拆分：静态审查发现证明路由允许非目标 sense/gloss 的已审规则进入 proof；现在逐条要求所有实际使用规则均匹配 test prediction 的 sense ID 与 premise gloss SHA，同时至少一条用于规则绑定 test claim/hypothesis。source gate 还明确要求证书至少含一个 source assertion fact leaf，避免空 fact 集合的 vacuous truth。将 adjudicated/supported 规则状态、测试 gloss 来源一致性、facts source-only 与最终 gate pass 分开输出；更新逻辑验证/评测协议。模块 `py_compile`、筛读 JSON 解析和静态证据字段检查通过；未运行测试。现有回归用例尚未覆盖同 gloss 多规则通过及跨 gloss 规则拒绝，二者仍需回归验证。

2026-10-06 reviewed pipeline 防跨释义规则迁移：静态审查发现，组合路由此前只要求至少一条已用规则匹配 test claim，未约束其他被证明实际使用的规则来自同一 sense/gloss，可能把别的定义中已裁决规则带入证明。现要求每条实际使用规则均绑定到 test prediction 的 sense ID 与 premise gloss SHA；同一 gloss 内多条规则仍可组合，而跨 sense/跨释义规则拒绝通过 source-semantics gate。logic/method 文档已同步；未运行测试，需后续用回归用例核验。

2026-10-06 COLLIE-V 权利范围澄清：官方 LREC 2020 作者指南说明 proceedings 采用 CC BY-NC 4.0，与论文 PDF 页脚一致；ACL Anthology 的通用页脚描述 ACL materials，不能单独据此认定 ELRA 出版内容有许可冲突。仅澄清来源范围，不作法律意见；论文外的 COLLIE 资源、TRIPS ontology、代码与依赖仍需分别核验。详见筛读日志和逐项复现门槛。

2026-10-06 v3 增量筛读与优先全文复核：对 v3−v2 的 113 条候选完成逐条题名/摘要判断（新增决定 109：相邻 68、背景 33、排除 8；另复用既有深筛 4 条）；13 篇全文优先候选现已全部核读官方 PDF。结构性边界尤为关键：ACL 2026 EnoTab 已有显式 AND/OR Evidence Tree 与可观测 pruning/rollback；ACL 2025 LCDS 已组合领域逻辑约束、来源映射及专家复核；NAACL 2024 POLITICITE 已有人工多源证据片段及分级支持标注。其余全文还覆盖部分证据与充分性、跨段验证、NLI/证据评价与长上下文检索。它们不验证 WordNet sense-linked gloss→Horn support/proof replay，因此只支持收窄、尚不能证明本项目差异新颖或有效。本条记录当时的 v3 screened 对账为 416/1,747（53 全文、21 定向、190 摘要/元数据、152 深度未明、1,331 待筛；后续状态见下一条）；详情见[增量筛读日志](sources/literature_screening_log_2026-10-06_acl_expanded_delta.json)、[候选副本](sources/acl_anthology_candidates_2026-10-06_v3_screened.json)、[查询审计](sources/acl_query_expansion_audit_2026-10-06.json)。关键官方来源：[EnoTab](https://aclanthology.org/2026.acl-long.1102/)、[LCDS](https://aclanthology.org/2025.acl-demo.28/)与[POLITICITE](https://aclanthology.org/2024.naacl-long.216/)。未运行测试。
2026-10-06 ACL 2026 形式化主题增量筛查与定向全文章节复核：对 v3 中 `definition_to_formal_logic` 词族 24 条候选完成题名/摘要决定（相邻 13、背景 4、排除 7），再对 10 条优先项核读官方 PDF 中的方法、评测与局限章节；不称全文/附录穷尽复核。复核发现图式语义→FOL、NL→FOL+Z3、迭代 PDDL/Lean/Hoare 形式化及逻辑 prover 搜索均有跨域先例；这些系统的形式核验仍以已生成的中间表示/合同为条件，不能替代 gloss span→规则语义支持。精确 URL 对账现为 440/1,747（全文 53、定向 31、摘要/元数据 204、深度未明 152、待筛 1,307）。这不提供 WordNet matched baseline 或新颖性证据。逐篇范围见[结构化日志](sources/literature_screening_log_2026-10-06_acl_formalization_2026.json)。
2026-10-06 ACL 检索词族扩展并冻结 v3：在确定性 ACL Anthology 脚本新增 long-context evidence、multi-evidence selection、evidence evaluation/attribution 三词族；重下官方导出（未压缩 BibTeX 内容 hash 与 v2 相同），候选从 1,634 增至 1,747。逐 URL 对账为 307/1,747：全文 40、定向 21、元数据/摘要 94、深度未明 152、无日志匹配 1,440。扩展框检出并匹配 Logic Haystacks、ETS、Counting-Stars 与 TACL Ev2R；前三篇为全文记录，Ev2R 为摘要级记录。原 v1/v2 保持不变。候选哈希、词族计数、对账和限制见 [查询扩展审计](sources/acl_query_expansion_audit_2026-10-06.json)。这仍是关键词框，不是系统综述或召回率估计。

2026-10-06 顶会多证据检索补查：从官方 ACL Anthology 发现 ACL 2025 ETS、COLING 2025 Counting-Stars、TACL 2026 Ev2R；三篇都不在冻结关键词候选框，输入 SHA 不变。已全文核读前两篇、只按官方摘要记录 Ev2R。分别提取联合证据集搜索、位置/上下文长度与多证据干扰评测、reference alignment + verdict support 双轴指标设计启示；严格注明 reader reward/合成基准/摘要证据不等于 gloss-span semantic gold。记录于[结构化筛读日志](sources/literature_screening_log_2026-10-06_evidence_retrieval_supplement.json)。

2026-10-06 EACL 2026 Logic Haystacks 全文筛读：框外发现该文，冻结候选文件和历史对账计数不变。论文在最长 2,048 句的合成英语/FOL 前提中，用可证明不干扰的相似干扰项测试矛盾证据定位，并以证明加反事实删除提取必要且充分证据。将其记录为长上下文 evidence retrieval / distractor robustness 近邻；不涉及 WordNet gloss、sense 或 source-span 支持。候选关键词覆盖存在漏检，详见 [筛读日志](sources/literature_screening_log_2026-10-06_logic_haystacks.json)。

2026-10-06 EMNLP 2024 Unigram-FOL 全文筛读：核读声明式上下文敏感 grammar、英语/TPTP FOF 双 realization、FOL solver 标签、Vampire proofs、100K 生成数据及消融和局限。记录它对形式 compiler/reasoner synthetic stress-suite 的方法价值，同时明确未作新人工标注，不检查真实自然语言与公式的独立忠实度，也非 gloss-span gold。全文日志已加入相关工作、研究定位、最近工作比较、方法评测和检索协议。 ACL URL 对账更新至 v1 217/1,270、v2 303/1,634（全文深度 34/37；未明 152；v2 无日志匹配 1,331）。

2026-10-06 LREC-COLING 2024 Diff-Comb Explainer 全文筛读：核对 ILP/DBCS 解释子图选择、WorldTree split、超过 100K ConceptNet `is-a` 背景关系及答案准确率/解释 Precision@K/解释一致性/answer-explanation faithfulness 定义。其 faithfulness 不等于源句蕴含或 proof-certificate replay；解释选择只在 dev（test gold explanation 不公开）。作为证据图和指标分轴邻居写入文档，非 WordNet gloss baseline。ACL URL 对账更新为 v1 216/1,270、v2 302/1,634（全文深度 33/36，未明 152，无匹配 1,332）；无代码或数据复现，未运行测试。

2026-10-06 ACL 2024 NL→FOL 评测近邻全文补筛：核读 Yang et al. 的 MALLS/LogicLLaMA 正式 PDF。MALLS 有 28K GPT-4 生成句子级 NL–FOL 对；CFG 检查和人工错误样本分析支持过滤，1K 抽样由三名标注者逐项判断（六人标注池），Krippendorff α=.714；论文报告过滤后 correct 比例 92.8%。明确标为适配式方法基线邻居而非 WordNet gloss-span gold；MALLS 不检查事实性，样本无共享谓词/实体空间，数据许可为 CC BY-NC 4.0，未下载复用。修正 Princeton Annotated Gloss Corpus 官方链接为 `2019.gwc-1.48`。更新 related work、closest-work、research positioning、method/evaluation、检索协议和 README。精确 ACL URL 对账现为 v1 216/1,270、v2 301/1,634；深度未明仍 152，v2 无日志匹配 1,333。新筛读日志 JSON 与固定候选 source hash 已核验；未运行测试或模型复现。

2026-10-06 ACL 早期及 2023 WordNet/gloss 候选筛查：完成固定候选框 2016–2019 年待筛 82 条（1 direct、43 adjacent、35 background、3 exclude），定向核读 3 篇；完成 2023 年 12 条（0 direct、7 adjacent、4 background、1 exclude）。将候选框当前 URL 对账更新为 v1 215/1,270、v2 300/1,634；两版各有 152 条匹配但逐篇筛读深度未明，v2 仍有 1,334 条无日志匹配。详情、口径和边界见 docs/literature_search_protocol.md 与两份结构化筛读日志。单人定向筛查，不证明穷尽性、有效性或新颖性。

2026-10-06 ACL Anthology 2020 年 WordNet/gloss 族筛查：逐条完成 25 条摘要决定（2 direct、12 adjacent、4 background、7 exclude），并定向核读 COLLIE-V 与 BMEAUT 官方 PDF。确认 COLLIE-V 已从 WordNet gloss 导出含 AND/OR 结构的 entailment axioms，属于重大新颖性碰撞；BMEAUT 已实现 definition-graph lexical entailment，是必须加入的图基线候选。更新机器日志、相关工作、closest-work、检索协议和评测基线。项目差异及发表新颖性仍待共同 gold 上的实测，目标继续保持未完成。

2026-10-06 研究就绪度审计：核对冻结图结构、Phase 16 资源内 hypernym 证书、手工 AST→Horn/NLI 原型、400 项候选标注框、release lock、相关工作和 CI 配置，新增 docs/research_readiness_audit.md 并链接于 README。清楚区分结构/形式复算证据与 gloss-support gold、NLI 效果及新颖性证据；确认当前 preregistration lock 未签署、未授权分发，根目录无代码许可。审计文档内链和新筛读 JSON 解析通过；未运行测试套件或 CI。

2026-10-06 ICLR 2026 ProofBridge 全文补筛：记录其 proof-DAG-aware NL/Lean retrieval、SFT/repair、Lean type check 与基于参考 Lean theorem 的双向等价核验。pass@32 上 SC 为 62.70、TC 为 95.49，相较随机 few-shot Kimina-Prover-RL-1.7B 的 31.56/93.85；该语义指标以 reference NL→Lean 忠实为前提，因此不能替代原文到形式化的 source-faithfulness gold。补充结构化筛读日志、closest-work、related work、研究定位和方法评测，明确区分 formal validity、equivalence-to-reference 与 source-to-reference faithfulness。单篇定向筛查，未复现，不能支持项目新颖性或效果主张。

2026-10-06 EACL 2026 定义建模近邻补筛：从 ACL Anthology 官方 proceedings 搜索发现 LM-Lexicon，定向核读正式 PDF 的 WordNet/四个其他基准、训练切分、主结果、人评与局限。它研究 term/context→definition generation（含 1,775 个 WordNet test 项、3 seed 和 300 个 3D-EX 人评样本），没有评测给定 gloss→带 span 的方向性 Horn 规则或 proof replay；加入结构化筛读日志、closest-work matrix、related work 与检索协议。此主会先例收窄“WordNet definition modeling 尚未研究”的表述，但不构成本项目逻辑抽取匹配基线或有效性/新颖性证据。新增 JSON 可解析、项目内日志引用目标存在；未下载/复现模型、数据或运行测试。

2026-10-06 组合路由区分有效反模型：复核发现此前即使 pipeline 有精确的 `not_entailed_in_least_herbrand_model` 与有限 countermodel，route 仍把它压成 `abstain_missing_or_invalid_proof`。现 `route_pipeline_result` 独立重放 countermodel；NLI 阈值通过且反模型有效时返回 `not_entailed_in_supplied_program`，并在 evidence checks 标明重放结果；无校准/NLI 未过阈值仍保留原拒答优先级。逻辑验证与方法评测文档已同步，明示该状态只关于当前显式程序，不表示 gloss 矛盾或开放世界假命题。未运行测试；真实 gold 与语义有效性仍待验证。

2026-10-06 Datalog 未知结果进入 reviewed pipeline：保持 `datalog_checker.verify_query` 的严格异常契约；`run_pipeline` 现将求解阶段的格式错误/不支持 Datalog 输入编码为 `proof_result.status=unknown` 和稳定原因码，不再把异常外溢或误读为反模型。组合路由在 NLI 阈值通过但 proof 为 unknown 时返回 `abstain_unknown_proof_result`，并在 evidence checks 记录 proof 状态/原因；未校准或 NLI 未达阈值时保留原拒答原因。pipeline 版本升至 `/4`，同步更新逻辑与评测文档。源码 `py_compile` 与文档/版本引用静态检查通过；未运行测试，也未验证真实 WordNet gold 或语义有效性。

2026-10-05 Datalog 结果状态边界校正：核对 `datalog_checker` 与 reviewed pipeline 实现后确认，当前有限无函数正 Datalog 会完整计算 least Herbrand model，正/负状态分别附可回放证明或独立验证有限反模型；现无搜索预算和 `resource_limited` 返回态。格式错误/不支持输入目前抛 `ValueError`，尚未由 pipeline 统一映射为 `unknown`。修正 `docs/logic_verification.md` 与 `docs/method_and_evaluation.md`，将四态区分限定为未来跨片段/有界求解协议，避免误述为当前能力。仅文档静态复核，未运行测试。

2026-10-05 proof/NLI 相关工作补筛与候选框对账：从固定 ACL Anthology v2 的待筛项全文核读 LREC-COLING 2024 GFaiR 与 EMNLP 2024 RDTE/TREEWISE；GFaiR 在配对 FOL 上评估步骤级推导但搜索步数封顶，RDTE 提供 relevance/redundancy/factuality/sufficiency 序数 rubric，但其 context-dependent sufficiency 不是 gloss-span 支持，且论文的 1,000 总数与 267+775=1,042 分项冲突已保留。更新结构化日志、related work、closest-work、研究定位、方法评测、检索协议和 README；重跑精确 ACL URL 对账，v1 59/1,270（32 全文、13 定向、14 元数据/摘要），v2 144/1,634（34、17、93），v2 尚有 1,490 项无日志匹配。两项只收窄相关工作边界并启发区分 resource-limited 与 semantic unknown，不证明本项目有效性/新颖性；详见[结构化全文筛读日志](sources/literature_screening_log_2026-10-05_logic_proof_and_decompositional_nli.json)；未复现论文或运行测试。

2026-10-05 研究记录时间线纠正与独立 witness 重放复核：当前时钟与文件时间戳均显示这些新增筛读/对账记录于 2026-10-05 完成，原标为 2026-10-06；将 7 个机器日志文件及 17 处日期/链接引用统一改回 2026-10-05，ACL 候选表中的逐条筛读日志引用也同步更名。7 个 JSON 均可解析，候选表的 22 个不同日期化日志引用全部存在，项目文档/来源下无残余 2026-10-06 引用。重新独立回放 witness 与 Datalog bridge：3,596 nodes、14,923 dependency edges、3,512 ground rules，bundle integrity、节点集、边多重集和 Datalog 证书均通过。该复核只证明冻结包上的结构可用性，不证明 gloss 语义支持或开放世界蕴含；未运行测试套件。

2026-10-05 claim candidate manifest v0.2 与 split hygiene：检查实际 generator/validator 发现组合候选无法在冻结 manifest 表示 component IDs，且 group/sense 泄漏检查只覆盖 dev/test、未覆盖 train。新增可选 AND/OR composition descriptor（含各 component negated flag）、强制组合 formula hash、验证 component 存在及同组/sense/source/premise/split、拒绝循环；旧 manifest v0.1 仍可读，新 freezer 输出 v0.2，NLI export 保留组合类型。sidecar validator 与 freezer 现对 train/dev/test 全面执行 group/sense 隔离。更新 manifest schema、候选验证协议与评测文档。3 个 Python 模块 py_compile 和 schema JSON 解析通过；未运行测试，也未生成实际候选/gold。

2026-10-05 KDD 2026 组合逻辑基准适配协议细化：在候选验证协议新增 gloss 组合切片，固定原子 claim、组合 AST/hash、双人独立重裁决和 NLI/source-support/inference-basis 分轴标签；KDD 原论文先排除 baseline 原子错误的筛选另作 conditional subset，主集不按系统表现过滤，避免报告筛后容易样本造成的条件化偏差。明确 OR 是后续扩展、非 KDD v2 已验证切片。方法评测文档加入同候选比较、盲审与指标分轴要求。当前没有合格 gold/组合数据，该内容仍是待实现方案；未新增或运行测试。

2026-10-05 重要文献信息校正并完成全文筛读：此前按 ICLR 投稿题名将 Moreira et al. 记作未确认录用；arXiv v2 已更题并列出 KDD ’26 Proceedings Volume 2 与 DOI 10.1145/3770855.3817808，作者代码库亦标注 KDD 2026。全文/附录显示其已有 WordNet hierarchy、HyperLex、SNLI 和 LLM-elicited 600-pair 零样本 conjunction/negation 评测；软投影运算明确只是近似逻辑，WordNet 输入为 taxonomy links 而非 gloss。已修正相关工作、定位、状态记录，避免把同一 arXiv 作品重复计数。项目可检验差异收窄为 source-grounded gloss→typed Horn/span/proof replay，仍是假设，须做 matched evaluation；未复现模型或数据。

2026-10-05 最新近邻复核：ICLR 2026 正式论文 *The Lattice Representation Hypothesis of Large Language Models* 已在 WordNet 子层级测试概念 hierarchy 与 meet/join 的 embedding/FCA 表示，进一步排除“WordNet 逻辑组合未被研究”的宽泛说法。其属性标注由 GPT-4o 构造，未解析原 gloss、标注 source-span 或 replay Horn proof；分数不可迁移为本项目 source-support gold。已更新文献对照、定位和筛选日志；本轮是定向全文筛读，不是系统综述或 novelty proof。

2026-10-05 claim-review manifest 闭环：新增无文本、无 gold 的 claim-level manifest schema/生成器；sidecar validator 与 NLI 导出器现在要求 candidate 集合严格匹配由外部预注册/lock 固定 SHA-256 的 manifest，并核验 premise/hypothesis/formula hashes。原 v3 lock 只锁 sense 抽样、不含 claim hypothesis，故不改写为虚假的预注册状态。完整性 gate 通过仍为 400/400 抽样输入，但 0 份标注回传、方案未签署、无外部注册/分发授权；未创建真实 candidate pair 或 NLI gold。

2026-10-05 新增 Neural DTS (NALOMA 2026 workshop) 近邻：WordNet hypernym embedding 已用于 DTS proof search；最近工作边界进一步收窄至 source-anchored gloss rules、AND/OR 保真和独立来源证书。更新筛读日志、对照矩阵、评测基线与检索协议。

2026-10-05 标注 schema 更新至 `0.4-draft`，新增逐规则推理依据 `inference_basis` 并与 source-support 标签分开；旧记录仍兼容读取。仅做语法与链接静态检查，真实 gold、双标一致性及预注册仍未完成。

2026-10-05 跨顶会发现 ICLR 2025 LLM-TH 已组合 NLI entailment、typed hyperresolution 与证明搜索；已纳入先例矩阵并把项目差异收窄至待验证的 source-only/gloss-span/独立证书契约。
2026-10-05 新增 ACL 2026 主会 SLR 定向章节筛读：把它作为合成 Horn checker stress test 设计邻居，而非 gloss-support baseline；更新研究定位、比较矩阵、相关工作、筛查协议和机器日志。
2026-10-05 ACL source-grounded entailment 检索扩展及近邻复核：定向全文核读 PrefixNLI（ACL 2026）与 QASemConsistency（TACL 2026）发现 v1 1,270 条候选均未召回，遂增加 `source_grounded_entailment` 词族并保留 v1，生成 v2 1,634 条候选（新族预去重 404）；解压 BibTeX 内容 SHA-256 也纳入检索产物。v2 与逐篇筛读日志现精确匹配 141/1,634（全文 32、定向章节 16、摘要/元数据 93），剩余 1,493 条候选未匹配结构化日志。新增复核 FactCG、FactReasoner、NSF-CoT（PDF 定向章节），CiteEval、Self-Correcting RAG、Transform Retrieval（官方摘要），及 QC-NLI、HaluMap、RefNLI、Comprehensiveness Metrics（四篇官方 PDF 相关章节），另筛读两篇 NALOMA 逻辑 NLI/证明搜索工作。完成 2025–2026 两年 96 行、94 个去重题名/年份的逐篇标题/摘要初筛：已有筛读 11、优先全文候选 11、背景邻居 22、范围排除 50、重复别名 2。更新 closest-work matrix、related work、筛查协议和机器日志。该 ACL 单库词项框与单人筛查不估计领域召回率，也不构成最终综述纳入或新颖性证据。未复现模型或数据，未运行测试套件。

2026-10-05 proof 输入知识分区与规范化输入哈希：为回应 FoVer 全文显示的外部 common-knowledge 风险，在 Datalog fact schema 增加可重放 `knowledge_partition`（source_assertion/resource_fact/external_assumption/unclassified），证书 fact leaves 保存明确标签，独立 verifier 检查其与 replay program 一致。reviewed pipeline 增加 `knowledge_scope=all_inputs|source_only`：旧输入仍走 all_inputs；source_only 必须为每行明确标类，只纳入带 `source_documents` 的 source_assertion；结果摘要记录各类行数/过滤数量。组合 NLI→proof 路由进一步要求实际被用的所有 fact leaves 都仅为带来源文档的 source_assertion，否则 source semantic gate 不通过。更新逻辑验证说明、检索协议和方法评测边界，pipeline 版本升至 `/3`。source_only 与组合路由拒绝首尾去空白后为空的来源路径；输出新增 annotation records/problem 规范化 JSON SHA-256，直接 Python API 也能稳定标识内容，CLI 原始字节 SHA-256 继续独立保留。仅运行 pipeline 模块 `py_compile` 与差异静态检查；没有运行测试套件。该分区标签由输入方声明，机器回放不能证明标签正确或 source claim 语义成立；后续需有意构造回归样例并在人审 gold 上验证。

2026-10-05 TACL 2025 FoVer 全文筛读：全文核读 Pei et al., *FoVer: First-Order Logic Verification for Natural Language Reasoning*（TACL 13, 20 页）。FoVer 由 LLM 生成 Python/Z3 逻辑编码，再以 SMT 判定 True/False/Unknown；分别报告 executable rate、可执行样例准确率与总准确率。样本为 ProofWriter 200、FOLIO validation 203、REVEAL MuSiQue/StrategyQA 各 120。可选 LLM common-knowledge 在部分任务改善总准确率，但会引入前提冲突、降低执行率；作者承认公式生成仍有错误和 prompt 成本。该系统核查模型生成的公式，不验证公式/常识是否由输入原文支持。筛读时将 source_assertions / definition_axioms / external_assumptions 分区列为未来 artifact 要求；随后 `verified_reasoning_pipeline` 已实现事实 partition 标记、`source_only` 过滤、fact-leaf 证书回放与组合路由限制，但分区标签仍由调用方声明，且没有真实 gold 或独立语义审核。更新 formal_nli 筛读记录、相关工作、对照矩阵和 logic_verification 文档；ACL 候选框对账仍为 48/1,270 匹配，全文 30、定向章节 7、摘要/元数据 11、无匹配 1,222。未复现模型/数据，未运行测试。

2026-10-05 ACL 2025 隐含蕴含 NLI 全文筛读：核读 Havaldar et al., *Entailed Between the Lines*（17 页 ACL Long Paper）。INLI 把蕴含细分为 explicit/implied，额外推断可依赖逻辑、世界知识、语用或比喻；10k premise/40k hypothesis 来自四种对话/情境含意源，Gemini-Pro 参与构造。六位作者在校准讨论后对 200 条样例三人标注，Fleiss κ=.711、相对数据构造标签的多数一致率 .935；作者明确未全量人工审核并指出文化主观性/领域限制。项目已据此把 `inference_basis` 作为待版本化的次级标签方案，严格区分可推断性与 gloss-span 来源支持；INLI 不作本项目 gold 或匹配 baseline。更新 annotation protocol、method/evaluation、related work、comparison 与结构化日志；ACL 对账为 48/1,270 匹配，全文 29、定向章节 7、摘要/元数据 12、无日志匹配 1,222。未复现模型/数据，未运行测试。

2026-10-05 ACL 2025 FOL entailment 泛化全文筛读：核读 Zheng et al., *Enhancing Transformers for Generalizable First-Order Logical Entailment*（ACL Long Papers, 20 页）。其 KGQA benchmark 覆盖 55 种 EFO query types（23 seen、32 compositionally unseen）及 FB15k、FB15k-237、NELL995，并分开评估未见知识答案和未见 query type；TEGA 使用 logic-aware relative positional encoding 与 guided attention。该项启发将 sense/规则知识 held-out 与 AND/OR 组合泛化设为独立评测轴；但模型知识参数化于 KG、输出为实体排序，不生成 gloss-based rule、source-span support judgment 或 proof certificate，因此是评测设计近邻而非匹配方法基线。未复现代码/数据。更新 related_work、closest_work_comparison 和 formal_nli 筛读日志；ACL 固定候选框精确 URL 对账为 47/1,270 有匹配，全文 28、定向章节 7、摘要/元数据 12、无日志匹配 1,223。未运行测试。

# 项目摘要（2026-10-05）

2026-10-05 WordNet 多重 hypernym LLM 选择全文筛读：核读 Hristov (RANLP 2025 Student Research Workshop) 论文及其候选代码仓库。该研究对 1,339 个 PWN 3.0 多重 hypernym 义项，让四个 4-bit 模型在候选父 synset 中择一；对先前手工整理结果的 agreement 为 45.4%–55.0%，模型间一致更高。作者将模型共识用于人工整理优先级，并将进一步人审列为 future work；未报告 IAA。仓库无可见许可信息，未取用/复跑数据。更新相关工作、对照矩阵和筛读日志；ACL 候选深度对账为全文 27、定向章节 7、摘要/元数据 12（46/1,270 有日志匹配）。这一任务不包含 gloss→规则或证明，研究结果仅作关系清理邻居。

2026-10-05 近期义项对齐工作全文筛读：核读 Roussopoulou & Markantonatou (LT-EDI 2026) 13 页论文，确认其用原语言 lemma–definition–example、2,872,327 次 pairwise LLM 比较构建五语 sense alignment；人工核验只覆盖四组语言、每组 20 对且每组一名双语审阅者，因此 75%–100% 是单审阅者准确率，不是 IAA。公开仓库列代码 MIT、作者研究材料 CC BY-NC-SA 4.0、第三方许可分别适用，另链接大体量结果文件；未下载或复用数据。加入相关工作/结构化日志后重跑候选对账：全文 26、定向章节 7、摘要/元数据 13，共 46/1,270 有日志匹配。该工作只提供 sense/source identity 与有限人工核验邻居，不含 gloss-span gold 或逻辑证明；未运行测试。

2026-10-05 LREC 2026 层级迁移论文全文筛读：经官方 HTTP PDF 链接成功取回 *When Structure Matters* 的 18 页全文（SHA-256 记入机器日志），核读方法、数据/split、结果、局限及附录，并目视检查结果表。确认其“zero-shot”是 vocabulary-constrained：CWN 测试相关 English synsets 被保留在 OEWN 训练图中；作者承认不是严格 unseen-synset zero-shot。GPT-5-mini 自动对齐未经人工验证；测试图分支/深度和规模不平衡，作者称 CWN 优势只能视为上界。统计是单次训练末 10 个 checkpoint，不是独立 seed。作者声明发布数据/代码，但论文网页及 PDF 链接中没有找到发布 URL。重新运行 ACL 候选对账脚本后，筛读深度更新为全文 25、定向章节 7、摘要/元数据 14（共 46/1,270 匹配）。更新相关工作、筛读日志、候选状态与协议；未复现论文结果、未检查数据许可，也未运行测试。

2026-10-05 冻结 AND/OR 超图全量复算：使用当前 `frozen_hypergraph_audit.py` 输出到 `tmp/phase6_recheck/`，再次核验冻结包 integrity lock、basis Horn 闭包和全部 witness。110,425 heads、154,206 clauses、917,767 dependency literals、85 basis 与旧 phase6 report 的 observed 字段及逐 basis 删除敏感度完全相同；全量闭包覆盖、节点/规则/超边一致、无缺依赖/自依赖/空/重复子句、110,425 witness 全有效、最大深度 396。新版报告额外记录 pinned bundle 哈希和 9 项 integrity check，全部通过。`hypergraph_complexity_profile` 的复算输出 SHA-256 与既有产物逐字节一致（`8c7d2358d3792e4ebb514aa037b396ff06e1bfea550db0adaa59b0d15626674f2`）；单个 3,596 节点/14,923 边 witness 证书独立回放有效，bundle 六项锁定文件匹配。以上仍是固定冻结图上的结构证据，不验证 gloss 语义支持；全量脚本运行非单元测试，未运行测试套件。临时报告位于被忽略的 `tmp/phase6_recheck/`，未覆盖既有 baseline。
2026-10-05 Phase 16 复算与研究 gate 复核：在当前工作树重新运行 OEWN 2025 Plus 义项级 hypernym 闭包校验器，并用独立证书回放器核对 3 个示例 claim（1 direct、1 transitive、1 resource-relative not-in-closure）。回放 `valid=true`、3 claims、0 errors；taxonomy 为 120,564 synsets/93,395 direct hypernym edges。临时复算输出 SHA-256 与既有 phase16 产物逐字节一致：verification `0fb64b7600c7e51755dd7f137f018be88f47fa27acea2b8f4f41eecbebdef2d7`，replay `cf69ee6ebb03e26b0a12aef9c3955600f76ef9ac7a5963d07346e2f187a3bec8`。另外 text-free annotation preflight 的 integrity/schema 为 true（400/400 输入任务对齐），但 0 annotation returns、`protocol_signed=false`、`distribution_authorized=false`；数据发布 inventory 自检一致，发布状态仍 `not_cleared_for_public_release`。这些运行复核的是资源内 relation 与输入完整性，不是语义 gold、有效性或发布许可。未运行测试套件，也未分发任务。

2026-10-05 标注 claim—AST 子树—span 结构完整性：`annotation_validator` 现在要求 claim 公式子树中每个节点的完整 span 被该 claim 的 evidence span 并集无间隙覆盖，避免部分字符交叠被误当成完整引用。此检查只核验字符区间定位，不验证语义支持。更新了标注协议与组合验证边界说明；当前仅作语法/静态检查，未运行测试，也无人工回传可评估真实拒绝率。

2026-10-05 形式化鲁棒性相关工作补充：对 ACL 2026 CoPE（丰富自然语言约束下的 planner/formalizer）与 EACL 2026 LogiQAte（含 FOL 等价逻辑混淆）官方页面及论文相关章节作定向核查，加入比较矩阵；在评测方法中把变体构造、冻结输入、保持指标及 unknown 处理写成尚待实施的 stress-slice 方案。两者都不是 WordNet gloss→Horn/source-span 直接基线；项目尚无此类鲁棒性数据或实验。检索日志说明只筛两篇、无稳定完整命中集，不声称系统综述或新颖性审计。

2026-10-04 EMNLP proceedings 时点审计：按定义/WordNet/lexical relation/autoformalization/NLI 主题查询官方 ACL Anthology 未得到 EMNLP 2026 论文级记录；官方会议日期为 10 月 24–29 日，CFP 规定 accepted papers 报告后才进入 proceedings。新增[机器筛读日志](sources/literature_screening_log_2026-10-04_emnlp2026_status.json)，并在检索协议、相关工作综述和综合报告标记“会后复查”；无当前命中不解释为没有相关工作。JSON 与本地链接/空白检查通过；未运行测试。

2026-10-04 注释来源元数据校验与协议状态同步：`annotation_validator` 现在验证可选顶层 `provenance` 的对象类型；若提供 `source_records`，逐项要求非空路径和有效 SHA-256。此前 malformed provenance 可通过 validator，之后在 compiler/routing 的 `.get()` 处崩溃。更新标注协议，注明结构校验不确认路径存在或授权，并把 200 条 pilot 标为历史、400 条 v3 任务标为未分发候选。三个相关模块 `py_compile`、文档本地链接/空白检查通过；本轮未运行测试。

2026-10-04 规则库输入追溯：独立运行 `annotation_to_datalog` 时，编译 JSON 现记录原始 annotation JSONL 文件字节的 SHA-256；组合 reasoning pipeline 原有输入哈希保持不变。文档明确该哈希受空白和行序影响。源码语法、文档链接与空白检查通过；本轮未运行测试。

2026-10-04 项目首页状态同步：`README.md` 首页现把 200 条 pilot 明确标为早期 Phase 9 工作，并将 400 条/24 层任务框标为当前候选确认性设计；同时注明尚未分发/标注、不是 gold。首页本地链接与空白检查通过，消除摘要与后续 v3 状态记录的歧义。

2026-10-04 综合报告状态同步：更新 `../report/project_review_2026-10-29-current.md` 的日期与现状入口，将 200 条早期 pilot 明确标为历史阶段，并汇总 400 条/24 层候选确认性设计、截至 ACL/LREC 2026 的定向相关工作、NLI 阈值校正原型和仍未满足的标注/许可/版本映射/实验门槛。报告保留旧结构复算数据作为阶段审计，不把新工作表述成语义结果、系统综述或新颖性证明。报告内相对链接与尾随空白检查通过；本轮未运行测试。

2026-10-04 v3 标注研究预注册准备：新增独立方案草案，明确研究只估计人工标注状态/关系/支持标签的设计加权边际分布并测量标注一致性，不检验模型有效性；冻结 400 条/24 层样本定义、双人盲标、裁决顺序、非应答时停止推断、未校准区间的报告限制和实现版本要求。复核 frame、release cross-check、blind batch、manifest 与源 archive 六项 hash、400 行/400 个唯一 task ID及 schema 标签；目前没有标注回传。草案尚未签署或注册，人员、材料许可和持久注册信息仍未解决；不代表任务已分发或标注。见 [v3 预注册草案](docs/annotation_preregistration_draft_v3.md) 与[候选确认性抽样设计](docs/annotation_study_design_v3.md)。

2026-10-04 文献检索可复现性补充：OpenAlex title/abstract API 按 8 组 2024–2026 查询得到 45 个重叠命中，DOI/title-year 去重为 43 条；逐条纳排理由已存结构化日志，并补入 SymbCoT、乌克兰 WordNet 上下位关系抽取、E-prover 指导 NL→FOL 修正和 FOLDCoVe 四个不同层级的邻接方法。另将 ACL Findings 2026 NSF-CoT 的上下文推理忠实度审计纳入矩阵。该结果仅代表这 8 条 query 的单人候选筛选；API 元数据有缺项/日期占位，OpenAlex 也漏检 NSF-CoT；不构成系统综述、PRISMA 流程或新颖性证据。复跑命令和来源限制见[检索协议](docs/literature_search_protocol.md)及[机器筛选日志](sources/literature_screening_log_2026-10-04_openalex.json)。

2026-10-04 设计加权边际比例区间校准：按 v3 24 层设计，对均衡、中等、稀有、极稀有和层间异质五类合成比例，每类生成 5 个有限总体、各重抽 1,000 次；同时诊断 clipped Wald、logit 和 arcsine 区间。Wald 在 p≈0.01 和层间异质场景覆盖约 89%–90%；变换区间有所改善但各有偏离名义覆盖的情景，极稀有情景可报告率约 55%。分析器现将所报比例区间标注为未校准探索性区间并携带欠覆盖警告。模拟只检查指定合成分布，不代表真实人工比例；复算和各区间边界见 [v3 抽样设计](docs/annotation_study_design_v3.md)。

2026-10-04 设计加权 κ 区间模拟与压力测试：按 v3 真实 24 层设计，对五种合成有限总体各重抽 2,000 次，并比较 Taylor 与 delete-one jackknife Wald 区间。四个中等场景条件覆盖率为 94.3%–95.3%；稀疏边际/高一致性场景有 64.6% 样本无观察分歧，原始零宽区间欠覆盖。分析器现对零分歧结果抑制区间；剩余可报告区间条件覆盖率为 97.9%/99.7%，但可报告率仅 35.4%/34.9%。少于 10 个分歧时另附未经校准的操作性警告。还修正了 κ 对机会一致率的联合单元导数索引，并以非对称合成列联表锁定解析标准误。15 项聚焦测试通过。模拟不是人工标签证据；真实双标未回传。机器报告被 `.gitignore` 排除，复算与完整边界见 [v3 抽样设计](docs/annotation_study_design_v3.md)。

2026-10-04 候选确认性抽样框 v3：`annotation_sampling.py` 新增最小每层随机配额参数，保留旧默认策略并产出独立 400 条 frame：104,907 个冻结图目标节点、24 个 POS×释义长度×标点层、每层至少 2 条、无诊断富集。frame SHA-256=`ba17121d29b7c5140a897505a0a245b5964203f75d335e889cd7137bb2b0028d`；设计权重 2–291.25，Kish ESS≈380.6；二元总体比例在 p=.5 下的设计方差上界正态近似半宽约 5.01 个百分点。固定 OEWN 2025 Plus cross-check 为 raw 400/400 exact、effective 376/400 exact，已导出有 attribution 的本地 400 条盲标任务（visible fields 仅 task ID/POS/lemma/raw gloss）。这些是候选样本与任务包，不是 preregistration 或 gold；来源/发布许可审查仍待完成。复算命令、总体边界和 gate 见[候选确认性设计](docs/annotation_study_design_v3.md)；frame、blind batch、manifest 和答案键被 `.gitignore` 排除。

2026-10-04 一致性分析面板隔离与设计加权 κ：分析器按 `sampling_panel` 分开输出，拒绝同一 item 的 panel 错配；v3 完整双人随机 panel 支持经 frame/batch manifest 绑定校验后的加权名义 κ。区间为探索性 Taylor/Wald 近似；五场景压力测试揭示稀疏边际高一致性下严重欠覆盖，详见本文件首条。v2 的 160 个随机项有 9 个非普查 singleton 层，工具拒绝设计方差估计；诊断面板不作总体估计。AST/span/F1 与 bootstrap 仍是未加权探索性结果，且无真实双标回传。详见[标注协议](docs/annotation_protocol.md)与[v3 抽样设计](docs/annotation_study_design_v3.md)。

2026-10-04 形式化/NLI 基线分层：新增 ACL 2025 Entailment-Preserving FOL 与 Findings ACL 2025 Natural Logic tree 的官方记录核对，并将研究对照按词汇关系、NL→形式逻辑+prover、证明结构、选择性/NLI 一致性四层整理。matched evaluation 需共用同一裁决 sense/claim 集、切分与候选预算，分别统计 relation correctness、gloss-span support、proof replay、NLI gold accuracy、coverage 与成本。只做了摘要级定向筛读，没有完备数据库检索或匹配实验；不据此声称新颖性。见 [基线扫描日志](sources/literature_screening_log_2026-10-04_formal_nli.json)、[对照矩阵](docs/closest_work_comparison.md) 与[研究定位备忘录](docs/research_positioning_and_prior_work.md)。

2026-10-04 方向性 NLI 评测补充：全文核对 LREC 2026 PhrasIS 方向反转 coherence 研究并加入相关工作矩阵。新增的方法学约束是：未来 direct-NLI 与规则辅助 NLI 对照除分类准确率、校准及 coverage 外，需在有 gold 且方向可逆的 sense/claim 子集上测反向最小对一致性；coherence 必须与 gold correctness 并报，不能把“前后一致”当作语义正确。PhrasIS 的 7 类 phrase-pair 任务不是本项目 3 类 NLI 的直接基线；尚未有 WordNet gold，指标目前是实验设计建议。检索和全文边界见 [screening log](sources/literature_screening_log_2026-10-04_directional_nli.json)。

2026-10-04 研究定位更正：用户明确指出工作区 `AAAI2027.pdf` 是既有工作，不是用户成果；新论文需在此前工作基础上提出并验证独立增量。该匿名稿件本身标注禁止分发、引用或公开分享，因此仅作内部研究范围对照。新增 [既有稿件与新研究定位备忘录](docs/research_positioning_and_prior_work.md)，列明稿件已报告的贡献、与当前同计数冻结包的结构差异、可检验的新研究假设及许可/归属门槛。当前 Phase 21 只证明特定冻结快照上的结构压平损失，不构成语义有效性或新颖性结论。

2026-10-03 逻辑管线相关工作补读：全文核对 NL2Logic (Findings EACL 2026)、UFAL-CUNI SemEval-2026 Task 11 与 AAAI 2026 Hybrid KB reasoning。可迁移点分别是 AST→确定性生成、parser/prover 模块消融、符号 ontology 与 classifier 的组合语义；都不是 WordNet gloss source-support gold。尤其 NL2Logic 以 benchmark 下游 NLI accuracy 间接测公式语义，不能替代逐条 sense/span 人工裁决。已更新矩阵、方法评测与检索日志；仍为定向单人 scoping supplement，不报 PRISMA 或 novelty 结论。见 `sources/literature_screening_log_2026-10-03_logic_pipeline.json`。

2026-10-03 Phase 21 压平损失消融：同一 85 个 basis 下，规范 AND/OR 与普通依赖弧存在式可达性都覆盖 110,425 heads，因此整体覆盖无法区分；但 109,750 heads 的简单弧最短路严格短于 AND/OR 最小证明深度，深度中位数从 320 降至 2。把所有投影入邻居作为一个合取则仅覆盖 187 heads。结果显示普通图可能保留覆盖而抹掉证明层级/组合条件；只相对冻结编码成立，不是自然语言语义质量指标。复算见 [压平损失审计](docs/flattening_ablation.md) 和 `outputs/phase21/flattening_ablation.json`。

2026-10-03 相关工作方向收窄：重点核对 EMNLP 2025 SememeLP 与 ACL 2026 Structured Sememe Knowledge for Lexical Relation Mining。后者由定义预测 sememe inventory/tree，并在 WordNet 相关 lexical-relation 与 HyperLex graded entailment 任务评估；故“从释义抽取语义组件/树并预测上下位”不能作为宽泛 novelty claim。候选切口应收窄至有 sense/version/source-span 的有类型方向规则、显式 AND/OR、独立可重放 proof/unknown 证书及规则对 gloss 的语义支持 gold，且仍属未证实假设。已把论文加入对照矩阵、检索日志和 baseline 计划；搜索不穷尽、不报告 PRISMA 数字。详见 [相关工作](docs/related_work.md)、[对照矩阵](docs/closest_work_comparison.md) 和 [筛读日志](sources/literature_screening_log_2026-10-03_sememe_supplement.json)。

2026-10-03 多源文献审计：补查 ACL Anthology、AAAI OJS、Crossref、arXiv 与受限元数据库，并全文复核 AAAI 2026 *Towards a Common Framework for Autoformalization* 和 ACL 2026 Direct Dependency Retrieval。核心方法更新是先声明方向敏感的 gloss→rule 语义支持标准 E，再分别报告 span/ID integrity、well-formedness、编译保持、proof replay 和人工 faithfulness 等 V；ID 存在或 checker 通过都不能替代语义支持。API 限流、DBLP bot challenge、不可导出命中总数和单人筛选均如实记录；不报告 PRISMA、不据此宣称 novelty。详见[检索审计](docs/literature_review_audit_2026-10-03.md)和[机器日志](sources/literature_screening_log_2026-10-03_cross_database_audit.json)。

2026-10-03 source-part 定位辅助：新增 `src/analysis/suggest_source_part_spans.py`，在本地已有 291 条 source×clause 映射任务（696 个 part）中对照 raw/effective definition 生成精确子串偏移建议。raw 中 291 个唯一命中、405 个无命中；effective 中 292 个唯一命中、404 个无命中，无多重命中。输出只含 task/part ID、状态、偏移和哈希，不含释义文本。它不判断语义支持，也不替代人工 source-part→clause 映射。全量 sense 索引只有 parts 整数计数，没有 part 文本/ID/AND-OR 树，故不能据索引宣称全量逐项对齐。新增 6 项测试；当时本地全套 113 项测试和 compileall 通过。见[标注协议](docs/annotation_protocol.md)与[数据来源审查](docs/data_provenance.md)。

目前已对上游 OEWN frozen bundle 完成正 Horn AND/OR 结构审计：85 个基础项闭包覆盖 110,425 个 head；154,206 条 clause、917,767 个依赖 literal；缺失依赖、自依赖、空/重复子句均为 0；全部 110,425 个 witness 均通过 DAG 证书检查，包括 seed/basis 一致性、精确递归深度及无重复/缺失/多余记录。另有正 Datalog 证明证书检查器、保守 NLI evaluator/abstention 原型，以及标注 JSONL/AST/span/split 结构校验器；语义组件还未用 WordNet gold data 评测。详见 [审计报告](../report/project_review_2026-10-29-current.md)、[逻辑与 NLI 原型说明](docs/logic_verification.md)、[gold slice 标注协议](docs/annotation_protocol.md) 与 [复算 JSON](outputs/phase6/frozen_hypergraph_audit.json)。

结构分析补充：对每个非 basis head 的单条被选 witness clause 汇总依赖 DAG，得 664,732 条边（全部候选 clause 共 917,767 个 literal 引用）；selected-witness 依赖入度/父引用数 P90=7、最大 27,777，65,334 个节点不被其他被选 witness 引用。所有 85 个 basis 都被引用。该结构长尾为压力抽样提供候选维度，不是语义中心性或原语重要性。复算见 [selected-witness DAG 复用剖面](docs/selected_witness_dag_profile.md) 和 `outputs/phase6/hypergraph_complexity_profile.json`。

2026-10-03 witness 证据链进展：新增 `src/analysis/verify_witness_certificate.py`，可以脱离 DAG 导出器重新读取冻结 rules/witness/sense index，核验单个导出 JSON 的 graph semantic fingerprint、选中 AND clause、来源索引引用、依赖边多重集及拓扑/深度约束。现存 `oewn-00520548-n` 证书的 3,596 节点、14,923 条 literal 边通过独立重放；篡改指纹、子句、来源、边、深度或拓扑序的测试被拒绝。它仍只验证当前冻结编码下的结构可用性，不验证 raw gloss 是否语义支持该规则，也不取代全量审计、source-file hash 或许可证审查。运行说明见 [selected-witness DAG 复用剖面](docs/selected_witness_dag_profile.md)。

2026-10-03 可移植性修正：此前 `config/project_config.json` 的冻结包相对路径并未被核心脚本使用，多个入口各自硬编码同一目录。新增 `src/analysis/project_paths.py` 作为单一路径解析器，并令冻结图审计、索引审计、抽样、来源审计和 release cross-check 共用配置；相对路径按项目根目录解析，CLI 的 `--bundle` 仍可显式覆盖。相对/绝对配置、缺失/非法配置均有测试，模块与直接脚本入口已验证。当前全套 99 项测试通过。

2026-10-03 冻结版本例外审计：上游 manifest/replay/index 一致报告 110,424/110,425 heads exact replay。唯一例外 `ext_wikt_full_dd659c7fcb3b` 的 canonical replay singleton clause 与冻结图选定的 two-literal clause 不同；冻结包 README 明确保留 archived authoritative graph clause、不把额外分支自动并入图。新增 `src/analysis/audit_frozen_bundle_replay_exceptions.py` 和 phase8 JSON，将该例外与 manifest fingerprint、sense index、graph rule、witness 交叉核对；例外 head 自身的 depth-376 witness 与冻结图 clause 一致。报告强制区分来源重放差异与语义正确性，不擅自修改 frozen bundle。强制复跑 JSON hash 一致；当前全套 101 项测试通过。详见 [单例差异审计](docs/frozen_bundle_replay_exception.md)。

2026-10-03 工程化进展：新增 `.github/workflows/tests.yml`，配置六个 GitHub-hosted matrix 项（Ubuntu Python 3.10–3.13、Windows Python 3.10/3.13），仅运行 compileall 与标准库单测、不下载项目外数据。YAML 解析通过，本地 Python 3.13.9 下相同检查通过（101 tests）。本仓库当前没有 Git remote，因此尚无可观察的 GitHub Actions 运行结果；CI 仅是代码回归门，不代表全量数据或语义结论。范围见 [持续集成说明](docs/continuous_integration.md)。

NLI 阈值路径现明确分为两种：通用离线 evaluator 的观测阈值搜索与 Bonferroni-Wilson 界仅供探索性分析；组合在线路由改用预先固定的 101 点阈值网格、精确二项上尾检验与 Bonferroni 家族错误控制，并要求唯一 group_id（每个组一行）。校准对象记录 selector 版本和开发行规范化 SHA-256，二项尾部通过相对概率递推降低极端概率下溢风险。名义有限样本保证仍依赖冻结模型、IID 校准组及目标分布稳定；分组 ID 无法证明统计独立。dev/test 成对评估继续检查 sense/lemma-group/example 泄漏并在锁定 test 报告 gate precision/recall/coverage；此处无真实 NLI 模型预测或 WordNet gold。方法来源和限制见[风险控制筛读日志](sources/literature_screening_log_2026-10-04_risk_control.json)与[NLI 原型文档](docs/logic_verification.md)。

这只验证冻结依赖规则系统内部的结构可达性，不验证释义语义、形式逻辑忠实度或自然语言蕴含。论文稿与当前冻结包的 literal、深度和单删统计不一致，待上游对齐版本。历史 phase1–5 和外部 agent 结果是待复核探索，不是经验证的科学结论。

已补充摘要级的最接近工作对照矩阵和 gold slice 标注协议草案，并实现 JSONL 标注结构校验器。另对冻结包中的 OEWN namespace 构建了 200 条、不含 gloss 文本的可复算候选抽样框（160 条按 POS/长度/标点覆盖全部非空层的分层随机项 + 40 条结构诊断项），并完成对应 207 份 source JSON 的 hash/结构字段审计；这些都不是金标准，没有人工标注或模型精度含义。官方 2025 Plus 样本核对中 200/200 raw gloss 对齐，而有效释义只有 193/200 精确对齐，说明预处理变换必须单独做人审。现在已可导出经过版本、哈希和逐条释义匹配检查的 200 条盲标输入，答案键独立保管；task-ID 回填 adapter 可将单个标注者的 JSONL 返回合并为受校验的规范记录。**这些仍只是标注任务包与工具，不是 gold data**。抽样框和聚合结果分别见 `outputs/phase7/annotation_sampling_frame.jsonl`、`annotation_sampling_manifest.json` 和 `source_structure_audit.json`；盲标任务、答案键及署名清单见 `outputs/phase7/annotation_batch_2025_plus_blind.jsonl`、`annotation_batch_2025_plus_answer_key.json` 和 `annotation_batch_2025_plus_manifest.json`。参见 [相关工作](docs/related_work.md)、[逐项对照矩阵](docs/closest_work_comparison.md)、[标注协议草案](docs/annotation_protocol.md)、[数据来源审计](docs/data_provenance.md) 和 [检索协议](docs/literature_search_protocol.md)。

下一阶段优先级：核准候选项对应的精确 OEWN release 并确认混合来源许可 → 双人盲标候选样本、裁决并报告一致性 → 迭代稳定 schema/标注手册 → sense/释义 span/语义 AST/有类型规则 → 将数据接入独立 proof checker 和真实 NLI 模型 → lemma/sense 隔离评测与错误分型。

2026-10-03 进展：标注校验器增加 source gloss UTF-8 SHA-256 重算校验；受限 Horn 编译器拒绝低置信规则；新增标注→编译→有限正 Datalog query 的组合运行器，并输出可重放规则程序与 proof certificate。另增加 phase9 词面 genus 候选基线，在 200 条 2025 Plus pilot 上复算：160 条 random-stratified 子集中，99 个可评估名词目标有 96 个候选，其中 40 个至少有一个候选 sense 匹配 OEWN 直接 hypernym。它不是人工语义 gold，不能证明定义支持关系；具体限制和分母见 [Phase 9 报告](docs/phase9_gloss_genus_baseline.md)。

下一步工具进展：新增 `src/analysis/annotation_agreement.py`，按 item/source 对齐两份独立标注，计算 status/projection Cohen's κ、AST/公式方向/证据 span 一致性及固定 seed 的 paired-item bootstrap 95% 区间。只用合成样例测试，因尚无双人标注回传，不存在可报告的实际一致性系数。

2026-10-03 Phase 11：扩展 Phase 9 起始名词词面 heuristic 到 OEWN 2025 Plus 名词 synset 全量。84,909 个名词 synset 对应 84,910 条定义字符串；其中 77,173 条有直接 hypernym，候选覆盖 74,854/77,173（96.995%）；候选任一 sense 命中同一 release 的直接 hypernym 为 28,449/74,854（38.006%），覆盖全部可评估定义时为 28,449/77,173（36.864%）。这是弱 heuristic 的同资源结构 proxy，不是 sense-level precision、语义 gold 或冻结的 110,425-head 图评测。详见 [Phase 11 报告](docs/phase11_gloss_genus_release_baseline.md) 和[聚合 JSON](outputs/phase11/gloss_genus_release_baseline_2025_plus.json)。

2026-10-03 Phase 12：在 Phase 11 的相同首名词候选池上，新增不使用目标 hypernym 标签的词项上下文 TF-IDF cosine sense ranker。全量 77,173 个可评估定义中，13,528 个有唯一 top-1 决策（17.529% coverage），其中 5,843 个与 OEWN 同版本直接 hypernym 对齐（43.192% 的已决样本；7.571%/全量）。61,326 个候选实例因无上下文词重叠 abstain；对确有任一正确候选 sense 的池，top-1 retrieval 为 20.539%。强制重跑的聚合 JSON 哈希一致。结论是这个透明弱 baseline 覆盖低且信息有限，不是 gold WSD/语义蕴含准确率；详见 [Phase 12 报告](docs/phase12_gloss_sense_rank_baseline.md) 与[聚合结果](outputs/phase12/gloss_sense_rank_release_baseline_2025_plus.json)。

2026-10-03 文献工作：将 FormalScience (ACL 2026)、HBLR 与 DeepProofLog (AAAI 2026) 从摘要筛读升级为正式 PDF 全文核查，另读 Ancient Greek synset-selection 与 Open English NameNet 两篇 LREC 相关 workshop 全文。直接结论：形式系统编译有效不能代替源释义忠实度；选择性形式化/abstention 已有 AAAI 先例；证明证书复算与学习型证明搜索成本是不同评测量；词面首名词 baseline 需要同 gold slice 上的 taxonomy-aware sense ranking 与定义匹配对照。文献仍是单人定向 scoping review，OpenAlex/Semantic Scholar/DBLP 此次访问受限，不声称穷尽或 novelty audit。详见 [检索协议](docs/literature_search_protocol.md)、[全文筛读日志](sources/literature_screening_log_2026-10-03_fulltext.json) 和[逐项矩阵](docs/closest_work_comparison.md)。

2026-10-03 证明交叉检查：新增冻结 witness DAG → ground Datalog 的独立重放桥接器，实际重放 `oewn-00520548-n` 的 3,596 节点、14,923 条依赖边证书成功；证明节点和边多重集完全对齐。桥接范围仅为已选 clause 的结构性闭包，不判断 gloss 语义或其他 OR 分支。新增 3 项合成测试；当前全套 116 项测试和 compileall 通过。使用命令和限制见[逻辑验证说明](docs/logic_verification.md)。

2026-10-03 Phase 15 全量来源 payload 普查：读取全部 112,609 个活跃 source JSON（18,134,793,487 字节），每个文件的字节数与 SHA-256 均匹配冻结包 checksums manifest；110,425 条 sense-index 和全部 source logic tree 均完整扫描。108,727 个 source payload 的 DNF 分支数与归属 graph clause 数一致，但完整 WSD 分支 ID 多重集与图 literal ID 多重集完全一致的仅 3,123 个。以上是 source/logic/graph 结构映射计数，**不是**释义语义正确率、蕴含 soundness 或上下位精度。下一步应在许可明晰的小型双标 gold slice 上标注 source span→part→sense→literal 支持链。复算与边界见[Phase 15 报告](docs/full_source_payload_census.md)、[数据来源审查](docs/data_provenance.md)及 `outputs/phase15/full_source_payload_census.json`。
# 2026-10-04 单标注者边际比例

v3 完整随机 panel 的设计加权分析现逐位标注者输出分析状态、Horn 投影状态、规则关系 presence 和 semantic-support presence 的边际比例及分层 SRSWOR 方差。输出是独立标注者的描述分布，不是共识或裁决真值；使用截断正态 Wald 边际区间，尚未模拟稀有比例覆盖率。非普查零估计方差时抑制区间，全普查给精确点区间。聚焦测试覆盖层权重、方差、零方差与普查情形。真实双标注数据仍未回传。



2026-10-06 ACL 2026 逻辑推理近邻补筛：从固定 ACL Anthology v2 候选池按标题/摘要筛出三篇任务相关论文，并核读官方 PDF 的任务、方法、实验与限制：EACL Adaptive LLM-Symbolic Reasoning（自适应 LP/FOL/CSP/SMT 路由；形式化瓶颈及语义错误）、ACL OntGQA（Freebase 类型约束 KGQA）、Findings LoReFact（内容事实性与逻辑依赖评估）。更新结构化筛读日志、closest-work matrix、related work 和检索协议。它们分别约束 LLM+solver、类型约束图、逻辑依赖评估方面的宽泛新颖性说法，但不是 gloss→sense-linked Horn 规则与 provenance 回放的匹配基线；候选表 exact-URL 对账为 147/1,634，三条新增记录均标记为 targeted_sections_screened；JSON 与项目引用静态检查通过。该数只表示存在日志 URL 命中，不表示相关性纳入或系统综述召回率。此为有界筛查，不主张穷尽、项目效果或新颖性；未运行测试。
2026-10-06 ACL Findings FOVER 补筛：核读 ACL 2026 官方 PDF，记录 Kamoi et al. 的 FOVER（与 Pei et al. 2025 TACL FoVer 不同）：用 Z3/Isabelle 为形式逻辑与定理证明轨迹逐步标注并训练 PRM 的工作。其 solver 检查已形式化 premises/steps，不核验原始 gloss→formal premise 忠实度；据此将 source-support、逻辑有效性、proof replay、PRM 排序明确为分开的评测量。新增结构化筛读日志、closest-work matrix、related work、检索协议；候选表 exact-URL 对账更新为 148/1,634，FoVer 条目标记为 targeted_sections_screened。该数字仅是日志 URL 命中，不是纳入或召回率。此先例约束“首次形式验证推理步骤/自动 verifier 标签”说法，不是 WordNet gloss 或 AND/OR provenance 匹配基线；未复现数据/模型，未运行测试。
2026-10-06 Phase 16 输入契约收紧：代码检查发现 non-empty ID 验证后仍用原始字符串查询，因此带首尾空白的 child/ancestor ID 会被误报为资源缺失。验证器现拒绝 claim_id 和两个 synset ID 的首尾空白，不做静默规范化；同步更新 Phase 16 输入契约。仅做源码静态语法检查，未运行测试或全量 OEWN 重算；已有结果均绑定原输入哈希，行为变更需新输入/代码版本后复核。
2026-10-06 研究定位总表纳入 ACL Findings 2026 FOVER：将 TACL 2025 FoVer（自然语言到 FOL/Z3）与 Kamoi et al. 的 FOVER（形式轨迹→PRM 训练标签）明确分列；标明后者不验证原文到 premises 的忠实度，PRM ranking 不等于 proof replay。研究定位备忘录更新日期和语义形式化/prover 比较栏。静态检查内链目标存在；未运行测试。
2026-10-06 Phase 16 规范样例复算：在 hypernym ID 输入拒绝首尾空白的修正后，重新运行完整 OEWN 关系验证器和独立路径/Horn 证书回放。120,564 synsets、93,395 direct edges、图无环；3 claims 分别为 direct 1、transitive 1、release-local not-in-closure 1；回放 valid=true、0 errors。producer/replay SHA-256 与既有记录完全一致（0fb64b…def2d7 / cf69ee…a3bec8）；同步记录日期、结果和边界。此为规范输入上的结构/证书复算，不测试 malformed-ID 分支或语义精度；未运行测试套件。
2026-10-06 gloss 来源门槛落实到规则编译与组合路由：编译器升至 `/3`，schema `0.4-draft` 只允许非空、全由 lexical/paraphrastic 或 compositional/logical 组成的 `inference_basis` 编译；pipeline 升至 `/5`，proof-used claim 需绑定同一来源依据。外部世界知识、语用、比喻、unclear/unassessed 依据会拒绝编译。旧 schema 仍兼容编译读取，但不通过组合路由审查；测试夹具迁移到 schema 0.4。同步更新 annotation protocol、logic verification、method/evaluation。源码语法检查通过；未运行测试。没有真实标注 gold，门槛效度和标注一致性仍未知。

2026-10-06 近期相关工作补查新增一项直接 LLM baseline 候选：Greco et al. (Findings of EMNLP 2024) 已向 LLM 提供 WordNet 动词 synset gloss，评测方向性 lexical entailment；未做 gloss 有/无控制消融，也无规则来源 span 或 proof replay。NeurIPS 2024 KGD-L 另将 WordNet 定义与 hyponym descriptions 构成 CLIP 文本知识图用于目标检测器适配，属于图构建邻居而非词汇蕴含匹配基线。不得声称“WordNet gloss + LLM lexical entailment”或“WordNet gloss/hierarchy→显式下游图”宽泛新组合。已更新 related work、closest-work 矩阵/基线清单和定向筛读日志；一篇全文、一篇方法/消融定向核读，搜索仍非穷尽且不支持新颖性结论。

2026-10-06 文档可持续性维护：对仓库 47 个 Markdown 文件执行本地链接/标题锚点盘点，修复失效的文献日志相对路径、过期组合评测锚点、发布门槛锚点及存档文档路径；新增只读工具 `src.analysis.audit_markdown_links`，明确不检查外链。复跑报告 0 个本地链接问题，Python 语法编译通过；未运行测试套件。

# Goal continuation notes

2026-10-06 ambiguity-first semantic parsing 全文筛读：核读 Saparina & Lapata, *Disambiguate First, Parse Later*（Findings ACL 2025）。其在 AmbiQT/Ambrosia 先生成并补全自然语言解释，再逐项解析 SQL，报告 single/full interpretation coverage；作者指出错误可在多阶段间传播，不能过滤错误解释，且多解释增加计算。该先例排除“先消歧再形式化”和“多读法 coverage”作为单独 novelty，启示项目拆分候选 sense coverage、AST/Horn parsing、gloss-span support 与 proof replay；SQL execution equivalence 不迁移为 WordNet source support。新增[筛读日志](sources/literature_screening_log_2026-10-06_saparina_parse_later.json)，更新相关工作、逐项对照、method/evaluation、检索协议及 readiness。ACL v3 screened 更新为 443/1,747 日志匹配（全文 56、定向章节 31、摘要/元数据 204、深度未明 152；待筛 1,304），审计哈希同步。单篇定向筛读；未复现、未运行测试。

2026-10-06 严格 NLI 模型身份绑定：预测导出器升至 `claim-review-nli-export/0.2`，将统一声明的 model ID/revision 写入每条 dev/test 预测，manifest 保存两份输出 JSONL SHA-256，CLI 输出 manifest 自身哈希供外部锁定。新增 `route_pipeline_result_from_export`：要求外部固定 manifest hash，核对 manifest/schema、dev/test 文件 hash/行数/split/模型身份，从 test 文件按 ID 选行并先剥离 gold，再调用原 proof/NLI gate。底层兼容 `route_pipeline_result` 仍不核验模型身份，不应单独用于跨 split 校准结论；哈希也只绑定声明与字节，不证明实际推理服务运行了该 revision。pipeline 升至 `/10`，同步 logic verification、claim-evaluation protocol、method/evaluation 与 readiness。仅做 Python 语法编译和 Markdown 内链审计；未运行测试，未接模型或金标预测。

2026-10-06 NLI/proof route audit: source review confirmed `route_pipeline_result` recomputes the entailment threshold from supplied dev scores and binds test text hashes to the proof-used claim, but it receives no prediction manifest and does not enforce that dev and test scores share one NLI model ID/revision. The prediction exporter records model identity in its batch manifest, outside the routed rows. Updated logic verification and readiness audit to mark this as an explicit reproducibility/calibration limitation: a positive route's threshold interpretation currently depends on caller-preserved model-version consistency. No model data or gold is present; no tests run.

2026-10-06 公式一致性实现修订：审查发现双标 agreement analyzer 将量词绑定变量名直接纳入 AST signature，导致 alpha-equivalent 公式被计作结构分歧。现按词法作用域将绑定变量规范化为 de Bruijn 距离；自由变量、常量 ID 保留，精确 span 指标不变。分析器升至 `/9`，同步更新 annotation protocol 与 preregistration draft，说明这只衡量结构 alpha-equivalence，不等于逻辑等价或 gloss 忠实度。Python 语法编译通过、Markdown 内链审计 0 问题；未运行测试，也无真实双人标注数据可估计实际影响。

2026-10-06 FOL 指标全文筛读：核读 Thatikonda et al., *Assessing the Sensitivity and Alignment of FOL Closeness Metrics*（Findings EMNLP 2025）。FOLIO/MALLS 上的受控公式扰动显示量词、否定、AND/OR、谓词/变量改写对各指标影响不同；paper 的大样本排名对齐用 o3-mini judge，而人类仅参与 87 条的 judge 选择。因此将其用于设计 AST mutation diagnostics，不把自动公式分数或 LLM-judge 对齐当 gloss semantic-support gold。新增[机器筛读日志](sources/literature_screening_log_2026-10-06_fol_closeness_metrics.json)，更新对照矩阵、related work、method/evaluation、检索协议和 readiness audit。ACL v3 screened 当前为 442/1,747 日志匹配（全文 55、定向章节 31、摘要/元数据 204、深度未明 152；待筛 1,305），审计哈希已同步。JSON/哈希/计数及 Markdown 内链静态核验通过；未复现、未运行测试。该工作也不是 WordNet matched baseline，相关工作筛查仍未穷尽。

2026-10-06 Code4Logic 全文定向筛读：核读 Liu, *Few-Shot Natural Language to First-Order Logic Translation via Code Generation*（NAACL 2025 Long Papers）。其渐进式 Python 代码生成桥接 NL→FOL，并在 FOLIO/MALLS 及 LogicNLI、RuleTaker、VitaminC 报告论文自身指标；这些结果不等于 WordNet gloss source-support，且不可移作本项目成绩。将其作为已有 code-mediated NL→FOL + prover/downstream logic 先例写入结构化日志、related work、closest-work 对照与 method/evaluation；同步把 ACL v3 screened 快照精确日志匹配更新为 441/1,747（全文 54、定向章节 31、摘要/元数据 204、深度未明 152，待筛 1,306），更新衍生快照哈希。单篇定向筛读不构成系统综述或 novelty audit；未复现、未运行测试。

2026-10-06 reviewed source-fact path binding: source-only replay already bound fact atoms to adjudicated gloss claims and matching sense/gloss hashes, but a caller could label the fact with an unrelated non-empty `source_documents` path. The route now requires every referenced annotation to declare source-record paths, each reference to overlap the fact's paths, and every fact path to be represented among its referenced records. Bumped pipeline to `/9`; updated logic verification and readiness audit. `py_compile` and Markdown link audit passed; tests not run. This binds path labels to reviewed metadata only; it does not hash/read the external source files or verify their licensing.

2026-10-06 Phase 16 current-worktree spot replay: reran `python -m src.analysis.verify_oewn_hypernym_certificates` against the checked-in example claims/report and locally pinned OEWN release; result `valid=true`, 3 claims, 0 errors. This reconfirms only the recorded direct/transitive/absence cases and their release-relative certificate replay; it is not a semantic accuracy sample or gloss-entailment result. No output was overwritten and no tests were run.

2026-10-06 reviewed pipeline SHA-256 normalization: code audit found the canonical annotation validator accepts uppercase hexadecimal digests, but composed routing compared gloss and hypothesis digest strings case-sensitively, which could reject equivalent valid bindings. Added validated, case-insensitive digest equality for source/gloss and hypothesis checks; bumped pipeline to `/8`; updated readiness audit. Static Python compilation and Markdown link audit passed; no tests run. This improves input-contract consistency only and does not strengthen the claim that the model actually received the hashed text or that source files were independently verified.

2026-10-06 ACL 2026 结构证书近邻补查：全文核读 Li & Cao, *From Trajectories to Graphs*。其 interface-typed reasoning DAG、确定性 structural gate、接口证书和外部 verifier 与项目 witness/proof DAG 结构验证方法相邻；作者明确限定证书只保证可运行性，不保证语义正确。MATH L5 的 92.8% vs 41.2% 是论文自身的 verifier-runnable 指标，不可移作本项目成绩。更新独立筛读日志、closest-work comparison、related work 与 method/evaluation；收窄 novelty hypothesis：DAG/证书/gate 本身已有 ACL 主会先例，source-bound gloss claims 与可回放 entailment 仍需 matched gold 实证。仅一篇定向全文筛读，不是全 ACL 2026 系统筛查；未复现，未运行测试。

2026-10-06 SemEval 2026 Task 5 近邻筛读：核读 GuysLLM（NLI-finetuned DeBERTa graded regression）与 SemTechLab/HINTS（NLI-MPNet、target-span 特征、评分分布预测）。二者提供可适配的 graded sense-plausibility/NLI 方法候选，但输入任务不是 gloss 命题 source-support；目标词定位 span 不能当作来源证据 span，原论文成绩不可横比。已更新筛读日志、closest-work comparison、related work、method/evaluation 与 readiness audit。仅两篇定向全文筛读，未审全部 Task 5 系统论文、未适配或复现、未运行测试。

2026-10-06 annotation study design review using the experimental-design skill: clarify the estimand for weighted Cohen's kappa. With two fixed annotators, it describes that pair's agreement over the sampled item population and does not generalize to a population of annotators. Added preregistration gates for the 800 total item annotations, a frame-external workload/readability pilot, breaks/attrition, and task presentation order. The present exporter gives both annotators the same row order; the protocol now requires deciding whether a presentation layer will independently randomize order while keeping task IDs stable. Updated study design, preregistration draft, and readiness audit. No annotation materials were read or distributed; no tests run.

2026-10-06 source-fact evidence binding: close the source_only route gap that previously accepted caller-labeled facts without linking the fact atom to reviewed annotation content. `source_only` inputs now require `source_claim_refs` (`annotation_id`, `claim_id`, `formula_node_id`); the Datalog fact certificate preserves/replays those references. The composed route checks each used fact against an adjudicated, supported, medium/high-confidence gloss claim, requires gloss-grounded inference bases, matches the referenced atom predicate, and restricts grounding to the query target entity and matching sense/gloss binding. Updated [logic verification](docs/logic_verification.md) and [readiness audit](docs/research_readiness_audit.md); pipeline version is `/7`. This is a structural linkage, not independent verification of external source files or correctness of human judgments. `py_compile` passed and the Markdown link audit found 0 issues; tests were not run.

2026-10-06 Greco 直接 LLM baseline 适配协议细化：将 Findings EMNLP 2024 的 WordNet gloss + 有向动词 lexical-entailment 先例拆成资源设置复现诊断与项目人工 gold 的 matched Pair verification 两种视图；要求共同 sense/gloss/pair/split/预算，gloss 消融严格配对，few-shot 仅来自训练 lemma groups，并显式区分资源关系、NLI、semantic-support、span support 和 proof replay。更新[候选验证协议](docs/claim_verification_evaluation_protocol.md)。此为评测预案，不是已运行 baseline；无 gold、未获授权启动标注、未运行测试。

2026-10-06 ICLR 2026 autoformalization 邻近工作补查：官方全文筛读 CRAMF 与 Mathesis。CRAMF 将自然语言概念检索到 Mathlib formal definitions，再增强 Lean autoformalization，排除“检索定义作形式化 grounding”本身的宽泛创新说法；其编译/回译 LLM 指标不是 gloss support。Mathesis 用 LeanScorer 做分级 premise/conclusion 对齐，在 98 项三专家数学样本上报告 Fleiss κ=.7545、F1=.92；分数不是词典来源跨度或方向 gold。新增[结构化筛读日志](sources/literature_screening_log_2026-10-06_iclr26_autoformalization_neighbors.json)，更新 related work、closest-work、method/evaluation 与 readiness audit。全文定向筛查两篇，未复现、未审代码/数据许可、未运行测试。
2026-10-06 v3 双标呈现顺序工具化：在不改动 canonical blind batch（SHA-256 `dac533…97b6d5`）、答案键和原 lock 的前提下，新增双槽固定种子 presentation plan 与 schedule exporter；每个 slot 独立打乱稳定 `task_id` 并复用原任务字段，回传仍按 ID 对齐；输出目录加入 `.gitignore`。更新抽样设计、预注册草案、readiness 与项目结构。当前仅确认锁定输入哈希；未生成含 raw gloss 的呈现副本、未试标/分发、未改 `protocol_signed=false` / `distribution_authorized=false`，未运行测试。
2026-10-06 ICLR 检索协议补记：在 `docs/literature_search_protocol.md` 新增 CRAMF/Mathesis 补查的官方 proceedings 查询词族、正式会论文全文筛读范围与不可比性边界；明确没有全 ICLR 候选总数/去重框，不能称为系统检索或召回审计。与结构化筛读日志保持一致；未新增论文筛选或运行测试。
2026-10-07 Phase 55 COLM 2026 定向筛读：对官方 accepted-papers 列表中的三篇工作全文筛读组合 claim falsification、逻辑保持难例搜索、以及符号有效性/语义 grounding 分轨。结论：逐子句支持、组合反例、语义不变压力测试、verifier coverage/fallback 都应单独评估；泛化主张需收窄。非系统综述，无 matched evaluation 或 novelty conclusion，不改 ACL v3 计数。详见 Phase55。


## 2026-10-07 Phase 56：ACL 2026 NLI/逻辑筛查

在冻结候选框对 58 条 2026 NLI/逻辑论文完成题名/摘要筛读（26 邻近、2 背景、30 排除），定向核读五篇官方全文。固定 ACL v3 精确 URL 对账达到 623/1,747，待筛 1,124；这是日志覆盖状态，不是纳入相关工作数量。筛到的先例已收窄一般 NLI schema、来源跨度和规则图的新颖性表述；直接 gloss-source-support 匹配和效果仍未证实。详见Phase 56 报告及[筛读日志](sources/literature_screening_log_2026-10-07_acl2026_nli_logic.json)。


## 2026-10-07 Phase 57：ACL 2026 图/来源证据筛查

完成固定候选框中剩余 117 条图/规则/来源证据候选题名摘要筛读，并核读四篇官方全文。结合 Phase 56，2026 ACL 候选 295/295 均有精确日志匹配；全框总匹配 740/1,747，1,007 条仍待筛。新发现的 hypergraph retrieval 和 evidence graph 先例进一步收窄结构新颖性表述；source citation/span 本身仍不等于真实蕴含或忠实依赖。详见Phase 57和[机器日志](sources/literature_screening_log_2026-10-07_acl2026_graph_rule_provenance.json)。


## 2026-10-07 Phase 58：ACL 2025 WordNet/逻辑近邻

完成 ACL 2025 graph/rule 候选 133 条摘要筛查、十篇官方全文定向核读。LORex 已结合 WordNet taxonomy、概念定义和层级路径做 taxonomy parent expansion，应列为优先 baseline；Horn/tree rule refinement 和 KG graph-constrained reasoning 也已有先例。精确 URL 总匹配 873/1,747，仍有 874 条待筛；这不是系统综述或全文覆盖数字。详见Phase 58 报告与[结构化日志](sources/literature_screening_log_2026-10-07_acl2025_graph_rule_provenance.json)。

## Phase 59：ACL 2024 来源归因与 entailment 近邻

对固定候选中的 84 条 ACL 2024 `source_grounded_entailment` 待筛记录完成题名/摘要初筛（30 邻接、35 背景、19 排除），并对十篇优先论文作官方 PDF 定向章节核查。结论：答案归因、NLI 回溯、entailment tree 与 claim factuality 都有既有先例，不能单独作为创新点；WordNet sense/gloss span 绑定 typed AND/OR Horn rule 与独立 proof replay 仍是待检验假设。ACL 固定框 URL 对账为 957/1,747，尚有 790 条待筛。详见Phase 59 深度分析与[筛读日志](sources/literature_screening_log_2026-10-07_acl2024_source_grounded_entailment.json)。

## Phase 60：ACL 2024 逻辑证明与证据树近邻

对 ACL 2024 固定候选中剩余 36 条 NLI/逻辑/证明记录完成题名摘要筛查（16 邻接、8 背景、12 排除）及八篇定向全文章节核查。高优先方法参照包括 FRVA、WordNet 辅助 FOL model checking、Lean proof search 与来源归因系统；它们进一步收紧宽泛 novelty claims。ACL v3 URL 对账 993/1,747，仍有 754 条待筛。详见Phase 60 深度分析。

## Phase 61：ACL 2024 图规则与证据归因近邻

筛查 100 条剩余 2024 `graph_rule_provenance` 候选（36 邻接、33 背景、31 排除），并定向核对十篇全文。ClaimVer 已有 claim-span/KG 证据归因，TRACE 已有检索文本到图上推理链，复杂逻辑查询和 KG rules 也已有成熟先例。固定 ACL v3 对账 1,093/1,747，剩余 654。更窄的 glossary evidence span→typed AND/OR Horn support/replay 仍未验证。详见Phase 61 深度分析。

## Phase 62：ACL 2023 规则学习与 WordNet 符号校验近邻

对 31 条 ACL 2023 `definition_to_formal_logic` 候选完成筛查（15 邻接、13 背景、3 排除），九篇定向核读全文。发现文本 triple predicate 到 KG relation-path 的自监督规则学习，以及 WordNet–SUMO + FOL ATP 关系校验先例；source gloss-span→multi-premise Horn support 仍是未验证假设。固定 ACL v3 对账 1,124/1,747，623 待筛。详见Phase 62 报告。

## 2026-10-07 Phase 63：ACL 2023 WordNet gloss 与蕴含近邻

完成 ACL 2023 `source_grounded_entailment` 57 条候选的题名/摘要筛查（18 邻接、30 背景、9 排除）及十篇官方 PDF 定向章节核读。最直接近邻已用 WordNet sense gloss 辅助词汇替换，并以 mutual entailment 判断；所以“WordNet gloss + sense-aware lexical entailment”不能单独主张新颖。gloss-span→multi-premise Horn support、AND/OR provenance 和 independent replay 仍是假设。ACL v3 精确 URL 对账 1,181/1,747，566 无匹配。详见Phase 63 报告和[机器日志](sources/literature_screening_log_2026-10-07_acl2023_source_grounded_entailment.json)。

## 2026-10-07 Phase 64：ACL 2023 NL→逻辑、KG 规则与多证据近邻

对 ACL 2023 54 条 graph/rule/provenance 及 WiCE 多证据候选，共 55 条完成标题/摘要筛查（19 邻接、32 背景、4 排除）及十篇官方 PDF 定向核读。SPINDLE 已做 typed λ/proof parsing 与静态 checker；KG rules、规则增强、path quality、FactKG conjunction/negation、多证据 entailment 也有先例。ACL v3 URL 日志匹配 1,236/1,747。gloss-span→typed Horn support 和 replay 仍未由 gold/matched evaluation 证实。详见Phase 64 报告。

## 2026-10-07 Phase 65：ACL 2023 NLI、证明链与证据核验

筛查 ACL 2023 剩余 16 条 NLI/逻辑/证明候选（8 邻接、3 背景、5 排除），九篇官方 PDF 定向核读。PROVER 已做 commonsense-assisted 多步 NLI proof generation 和人工步骤核验；ReCEval 已做 reasoning-chain correctness/informativeness；SICCK 提供 hypernym/quantifier/negation 组合 NLI 压力切片。故“多步自然语言推理链”“链条打分”“证据检索+NLI”均不是充分新颖点。ACL v3 exact URL 对账 1,252/1,747；source-span→Horn replay 差异仍是假设。详见Phase 65 报告。

## 2026-10-07 Phase 66：ACL 2022 NL逻辑、Proof verifier 与释义近邻

目标性关键词切片筛查 20 篇 ACL Anthology 2022 候选（14 邻接、5 背景、1 排除），定向核读十篇官方 PDF。最重要的新边界是 NLProofS：它已有 supplied-fact proof tree、独立 trained verifier 和 search；Dual-(m)T5 已做 text→PL/FOL 并用于 NLI，CCG/Vampire 以及 verbalization+NLI 亦有先例。上述均不能证明原 gloss 支持每条 typed rule 或提供 source-only replay。固定 ACL v3 日志 URL match 1,272/1,747；这是 scoping 覆盖，不是系统综述。详见报告。

## Phase 67：ACL 2021 证明/Horn 近邻与实现边界

对 14 篇 2021 年 ACL Anthology 关键词候选完成题名/摘要筛查（6 邻接、6 背景、2 排除），定向核读六篇官方 PDF。Sumita 已有 natural-language prover subgoal + 用户临时词汇公理；RuleBERT、UniKER、WinoLogic 分别已有 soft Horn、definite Horn 与 solver-certified commonsense 先例。文件级实现审计确认项目现有人工审核→一元正 Datalog→证书 replay/NLI gate 原型，但 source-span validator 不判语义蕴含，typed predicate/argument signature 未实现；无 adjudicated gold/IAA/matched results。ACL URL 精确日志命中 1,286/1,747（文献覆盖账本，不是纳入数）。CodeGraph CLI/MCP 缺失导致本轮无法建索引。见Phase 67 深度报告及[结构化日志](sources/literature_screening_log_2026-10-07_acl2021_logic_proof.json)。

## Phase 68：显式类型签名下的 Datalog 校验原型

新增可选 `datalog-type-system/1` 检查，验证 sort hierarchy、predicate 参数签名、常量/规则变量 sort 和 subtype 兼容，并在 closure 与 proof/countermodel replay 路径上执行；pipeline 可携带版本化 type table。示例仅为 synthetic `Person <: Entity`，签名表由调用方提供，typed glossary rules 暂靠 rule-ID variable-sort side table，不能证明 gloss 蕴含或 WordNet 类型本体正确。py_compile 通过；没有运行测试或样例推理。详情见Phase 68 深度报告和[类型合同](docs/typed_datalog_contract.md)。

## Phase 69：类型环境哈希绑定

typed proof certificate 与 finite countermodel 现在携带 `type_system_sha256`，重放器要求与当前 versioned type table 精确一致；无类型化输入维持旧格式。py_compile 通过，但未运行 replay/tamper 测试，运行时行为仍待验证；哈希也不认证类型表来源或 gloss 语义。见Phase 69 报告。

## Phase 70：annotation 到 typed Horn 的变量 sort 传递

增加实验性 schema `0.5-draft`：每条 rule claim 显式声明其公式变量的 sort；validator 检查声明集合精确一致，compiler v4 将 sort 携带到每条规则且保留 gloss-grounded inference-basis gate。agreement analyzer v10 把 variable sort 纳入 claim 比较。旧 schema 0.2–0.4 继续可读；当前 v3 标注草案仍固定用 0.4。61 项聚焦测试通过；结论及语义限制见Phase 70 报告。

## Phase 71：typed Datalog 域与 artifact 篡改回放

新增 synthetic checker cases 并通过 10 项测试：Person 子类型 binding 成功、父类型但非子类型的常量不触发规则、typed certificate 缺失/错配 type hash 被拒、countermodel hash 改写和加入错 sort atom 被拒。它验证有限正 Datalog checker 的指定边界，不代表 WordNet 类型或 gloss 语义已验证。见Phase 71 报告。

## Phase 72：typed strict pipeline route 端到端检查

验证 0.5 claim sort 经 `run_pipeline` 进入 typed replay program；type table 被 proof 后改版时，strict route 拒绝旧 certificate；受限类型域下有效 countermodel 可产生程序范围 non-entailment route，而 countermodel hash 损坏则被降为拒答。pipeline 单测 12 项通过，五模块合并回归 66 项通过。所有场景为 synthetic，不是 WordNet 语义结果。见Phase 72 报告。

## Phase 73：OEWN 词汇类型来源审计

对固定 OEWN 2025 Plus 的 45 个 lexicographer files 和 120,564 synsets 做字节校验后的结构 profile：普通 `hypernym` 93,395 条，`instance_hypernym` 8,599 条；后者不在现有 Phase 16 verifier 覆盖范围内。官方把 lexfiles 说明为 POS+logical grouping，不是可直接视作 sort lattice 的 formal ontology。profile 复算哈希和受限输出见Phase 73 报告。

## Phase 74：Gloss Horn referent/type 契约草案

基于当前 `0.5-draft` 与 compiler v4 的一元共享变量边界，提出 `Referent` 根及不默认互斥的 `Entity`/`Eventuality` 候选域；POS 仅提示、不能自动定型，复杂类型转换和多元角色需拒绝或人工复核。新增[类型契约草案](docs/gloss_referent_type_contract.md)与阶段报告。Rademaker et al. GWC 2023 已做 WordNet gloss sense tagging→ERG predicate parsing，宽泛 semantic parsing 新颖性主张需排除；项目差异仍属待验证假设。

## Phase 75：Sort judgment provenance schema

新增实验性 `0.6-draft` 的 `variable_sort_judgments`，要求逐变量精确覆盖并记录 assigned/unresolved、sort、basis、理由和证据 span；unresolved 保留但 compiler v5 拒绝出规则。assigned provenance 被 compiler v5 带入 Horn rule，并由 agreement analyzer v12 输出独立 sort-judgment multiset micro P/R/F1 与 bootstrap 区间；证书篡改与 typed pipeline 端到端回放、0.5 兼容行为纳入测试。73 项包含审计、validator/compiler、Datalog、pipeline、agreement 的聚焦回归通过。尚无真实标注 IAA 或 semantic gold；当前 v3 仍固定 schema 0.4。见Phase 75 报告。

## Phase 76：OEWN instance_hypernym 资源内验证

新增独立的实例到类别关系 verifier，覆盖固定 release 的 8,599 条 `instance_hypernym`，与普通 `hypernym` 保持独立谓词；只通过显式 bridge/lifting rules 推到祖先类。新增独立 ZIP/JSON/图加载、SHA-256 manifest、DFS 闭包与证明规则 replay，检查路径、输入指纹和负例闭包；固定 release 两条正证书 replay 为 valid、0 errors。八模块 82 项目标回归及完整 220 项测试全部通过。尚无第三方实现交叉核对、人工 sense gold、gloss support 或 semantic accuracy 评估，不构成论文效果/新颖性证据。详见Phase 76 报告。

## Phase 77：instance_hypernym 分层压力集

新增固定种子 `20261007`、每层 40 条的 320-claim 压力集，覆盖 direct、class-lift 1-edge、class-lift 2+-edge、方向反转、同 POS 不可达、跨 POS、missing 与 self-pair 八层。固定 OEWN 运行 producer 后，独立 replay 对 320 项返回 valid、0 errors；固定重跑 claims SHA-256。全项目 222 项测试通过。该集合是 verifier 状态/路径压力回归，不是概率样本、语义 gold 或准确率估计；人工 sense-pair/source-support 评估仍待建立。详见[Phase 77 方法文档](docs/phase77_oewn_instance_hypernym_stress_frame.md)和深度报告。

## Phase 78：instance-to-class 人工审查候选设计

新增五层、每层 64 个的 320 个 text-free synset pair candidate IDs，direct/lift-depth 三个正类层具有可复算总体数；reverse 与 same-POS nonclosure 为独立 diagnostic 层。候选 ID 不泄露 strata，hidden key 与整个 `outputs/phase78/` 均 git-ignore；producer 和独立 replay 预检全部 320 pairs valid、0 errors。审查确认当前 0.4 单 sense schema 不适合 pair-level evidence，需要单独版本化 pair schema。标注 lock 仍是未签署/未授权；没有导出 gloss、外发或标注结果。详见[研究设计](docs/instance_relation_human_audit_design.md)和Phase 78 深度报告。

## Phase 79：pair-level 人工标注 schema 原型

新增独立 `wordnet-instance-relation-annotation/0.1-draft` validator，分别绑定两个 sense/gloss、方向、relation truth 与 strict gloss support、两个 span 坐标空间和裁决元数据；supported 记录和 gloss-only sense-relation 判断均要求两边 gloss 都有 evidence span，数据集校验同一 pair 的发布身份一致。测试只用 synthetic gloss，不读取 OEWN 文本。结构检查不判定语义正确性；pair validator 专项 8 项、全项目 232 项测试通过；标注协议仍未冻结、lock 仍未授权，无人工 gold/IAA/效果结果。详见Phase 79 报告。

## Phase 80：pair 标注手册与 rationale 字段

新增 pair 人工标注手册草案，分别定义 sense relation 与 strict two-gloss support 的任务、盲化、标签、span、裁决和分层报告建议，并列出签署前待决事项。pair validator 升为 0.2-draft，为两类判断分别保存必填 rationale。并提供 synthetic-only JSON fixture。专项 10 项、全项目 234 项测试通过。允许常识参与 sense relation、但 gloss support 只用两条 gloss，属于待审协议建议；当前无人工试标，授权 lock 不变。详见Phase 80。

## Phase 81：pair frame 精度与 estimand 审计

新增 text-free manifest 精度审计脚本。n=64 时三个正 strata 的最坏情形 pointwise 95% 正态半宽约 ±12.2pp；按已知人口权重的正向 closure total 约 ±9.3pp；相邻 lift 层差异约 ±17.3pp。same-POS challenge 明确为 source-macro 两阶段目标，不能解释成所有 nonclosure pairs 的简单 accuracy。计算为规划诊断而非 power/确认性区间。专项测试 3 项、全项目 237 项通过。见Phase 81。

## Phase 82：pair study 统计分析计划草案

新增未签署的 pair SAP 草案，定义推荐的 closure-positive support prevalence、分层/对比、source-macro challenge、`uncertain`/`unassessed`/nonresponse 处理、一致性/span 指标以及确认性 interval/multiplicity 冻结项。所有比率按“裁决标签 prevalence”解释，不宣称语义真值；CI 和 power 仍未冻结/未验证，授权 lock 不变。见Phase 82。

## Phase 83：有限总体 exact interval 原型

新增超几何反演区间：单层有限总体 binary proportion 使用等尾 exact interval，分层总体通过 Bonferroni simultaneous bounds 加权聚合，并对缺失标注给 worst-case bounds。N=2..8 穷举覆盖测试通过（4 项）；全项目 241 项测试通过。三层 `k=32` 仅合成示例的加权区间为 [0.3471, 0.6529]，说明保守区间比正态 planning margin 宽；非标注结果。SAP 仍未签署，方法待负责人审定。见Phase 83。

## Phase 84：SemEval 2026 形式/内容效应评测近邻

完成 SemEval-2026 Task 11 总览论文官方全文筛读。四类子任务分离形式有效性、语义合理性、语言迁移和无关前提干扰，且在 accuracy 之外报告 content effect。对本项目的 NLI 阶段，这是设计 plausibility/noise 压力项的依据；它不是 WordNet gloss-span support 或 proof replay 的匹配 baseline。没有复现论文结果，组合方案仍是假设。详见Phase 84 深度报告和[来源日志](sources/literature_screening_log_2026-10-07_semeval2026_task11_overview.json)。

## Phase 85：NLI 内容效应/干扰上下文评测草案

将 Phase 84 的形式/内容分离启示转为本项目独立的设计草案：盲法 plausibility 分层、经核准的匹配对和不改写 gloss/hash 的无关上下文诊断。方案区分 strict gloss-support 与 NLI 三分类 gold，限定干扰输入不能进入 source-only proof route；尚未实现、注册或获得标注授权。见Phase 85 深度报告与[评测草案](docs/nli_content_effect_evaluation_draft.md)。

## Phase 86：NLI 内容效应诊断工具原型

新增 `src/logic/nli_content_effect.py` 及 text-free sidecar 校验，覆盖匹配合理性对、同一 gloss/claim 的 source-only 与 distractor pair、模型版本、预测绑定和 split/group leakage；输出内容效应分层描述率、混淆矩阵、配对分数差及翻转率。该模块不校准阈值、不做推断、不进入 proof route。六项 synthetic-only tests 通过；NLI/route 聚焦回归 33 项、全项目 247 项通过。没有真实数据或效果结论。见Phase 86 报告。

## Phase 87：当前就绪状态与 Neural DTS 全文补核

将研究就绪度审计的顶部快照更新到 Phase 86，明确后续没有 ACL 固定框全局 reconciliation；Phase 58 数字仅保留为历史记录。复核人工标注 lock 仍未签署/授权且 annotator returns 为 0，并区分 247 项软件回归与缺失的自然语言 gold。补充记录 Neural DTS 已有的 WordNet hierarchy→DTS proof-search 先例与 max-over-candidate-senses 边界；它是 NALOMA workshop 近邻，不是新发现的顶会主会。见Phase 87 深度报告。

## Phase 88：OEWN 2025+ 来源记录与固定归档匹配

新增可复算审计，将固定发布 ZIP 与 inventory SHA-256 核对，并验证冻结 bundle 中六条 OEWN 2025+ 候选来源 payload 的 checksum；六组 `(ILI, definition_text_sha256)` 均在 73 个归档 JSON 成员中唯一匹配同一条记录。此进展不包含具体图规则 lineage 或全 bundle 清权，发布状态仍未授权。见Phase 88 报告。

## Phase 89：来源 payload 到图规则与 witness 的结构 lineage

六条 payload 均唯一连接到 sense index 与图 head；11/11 条规则子句匹配 hyperedge，六个 selected witness clause 均能回连规则/hyperedge。仅 4/6 active source-document 记录直接含候选 payload 路径，另两条连接到同一 sense 下其他 source record。此结果不证明释义语义支持或发布权利。见Phase 89 报告。

## Phase 90：selected witness 来源绑定精化

区分任意 active clause 来源与真正被 selected witness 采用的来源文档。六个 witness 来源文档 checksum 均核验通过，但只有 2/6 同时包含候选 payload 路径、匹配的 OEWN ILI/释义散列及定义文本 SHA-256；另两条候选只在非 witness 子句，另两条不在活动来源路径中。见Phase 90 报告。

## Phase 91：ACL Anthology 全局候选框对账

以固定 1,747 候选框对账 90 个日志，1,286 条存在精确 URL 匹配，461 条仍无任何全局匹配；明确全文 75、定向章节 134、元数据/摘要 851、深度不明 226。461 条均为 2016–2022，2022 年 130 条待筛。此统计不代表相关性纳入或系统综述完成。见Phase 91 报告。


### 研究进度：Phase 92 ACL 2022 候选筛读与近邻复核

完成 2022 年 130 条全局未匹配 ACL 候选的题名摘要筛读（22 邻近、2 背景、106 排除出核心综合），并对 4 篇官方论文做定向章节核读。总框复算为 1,416/1,747 URL 匹配、331 未匹配；2022 未匹配清零，剩余 331 条在 2016–2021。该统计与筛读不构成系统综述完成或 novelty 证据。见Phase 92 深度报告。


### Phase 93：ACL 2021 未匹配候选筛读与逻辑验证近邻

完成 2021 年 85 条未匹配候选筛读（26 邻近、2 背景、54 排除出当前核心综合、3 因缺摘要暂缓），对 4 篇官方论文定向核读。全框复算为 1,501/1,747 匹配、246 未匹配；剩余未匹配项在 2016–2020。见Phase 93 深度报告。


## Phase 94：ACL 2020 候选筛读与最近邻工作核读

完成 94 条未匹配候选筛读（29 邻近、3 背景、62 排除）和 6 篇官方 PDF 定向核读。最新固定候选框为 1,595/1,747 已有日志匹配、152 未匹配（均为 2016–2019）；深度分布全文 75、定向 148、摘要/元数据 1,143、旧深度未明 229。研究差异应聚焦 gloss-span 归因、typed rule 语义 gold 与独立 replay，并通过匹配 baseline 验证。详情见Phase 94 报告。


## Phase 95：ACL 2019 候选筛读与直接近邻

筛读 68 条未匹配候选（26 邻近、7 背景、35 排除），定向核读 4 篇官方 PDF。全框 1,663/1,747 URL 匹配，84 未匹配均在 2016–2018。Prokhorov et al. 的 textual-definition→hypernym path prediction 是直接先例；E3 结合程序性文本规则抽取与对话蕴含。研究差异应要求精确 gloss-span 归因、义项感知类型规则、source-only entailment 和可独立重放 witness 的联合 gold 验证。详情见Phase 95 报告。


## Phase 96：ACL 2018 形式化词义与证明近邻

完成 38 条筛读（18邻近、8背景、12排除）及6篇官方论文定向章节核读；固定框为1,701/1,747匹配、46待筛（2016–2017）。自然演绎证明获取短语关系、NL定义到OWL DL、WordNet ATP一致性审计、词汇资源+手写规则模板用于NLI均有直接先例。项目的新颖性尚未证明，候选差异需要落实到义项绑定、gloss span证据、typed Horn语义和独立replay的联合gold评测。见Phase96报告。


## Phase 97：ACL 2017 proof/lexical inference 先例

完成27条候选筛读（17邻近、7背景、3排除）及4篇官方PDF定向核读。全框1,728/1,747匹配，19待筛均在2016。按需词汇公理注入、自然语言tableau prover、proof-derived语义相似度以及自然语言解释到概念学习均有先例。可能贡献需在gloss来源、sense/span provenance、typed Horn与独立replay组合上验证。详情见Phase 97报告。


## Phase 98：ACL 固定候选框最后一批与审计结论

完成2016年19条候选筛读（10邻近、6背景、3排除）和5篇定向核读。冻结ACL v3的1,747个候选URL均至少命中一条日志；其中全文75、定向167、摘要/元数据1,276、旧日志深度不明229。URL覆盖不等于系统综述完成。形式ontology构建、WordNet资源交叉映射、KG+规则嵌入及textual entailment graph均已有近邻；项目差异仍须靠gloss span与可重放Horn规则的匹配实证验证。见Phase 98报告。

## Phase 102：gloss compiler 与 typed checker 边界

静态审计确认 compiler v5 仅支持共享变量的一元正谓词；通用 typed Datalog checker 可验证调用方签名下的程序，但不等价于从 gloss 自动构造/验证有类型 Horn。详见Phase 102 报告。

## Phase 103：lex-NLI structured explanation + prover 近邻

复核 AKBC 2026 接收论文的 362 项多参考 lex-NLI 人工 gold 和 LangPro 证明评测。文中证明覆盖增益有时由语义不可靠的词汇关系带来，强化了“proof replay 与来源语义支持分开评测”的设计要求。该研究使用 NLI 句对而非单条 WordNet gloss；本项目潜在差异只作为 gloss-span→typed rule→source replay 的待测假设。见Phase 103报告。

## Phase 104：annotation 多参考 gold 表示审计

`0.4-draft` 公式 OR 与整套合法替代分析不是同一种标注对象。Phase 104 定义签署前方案选择；Phase 105–106 实现未经运行验证的 sidecar validator/scorer 与 macro 指标原型，但选择/estimand 尚未冻结，现有 blind frame 和授权锁保持不变。见Phase 104、Phase 105、Phase 106。
# 2026-10-07 Phase 99 进展

已核读 BMEAUT 同研究线的 NLE 2023 期刊后续：可解释的词典定义图与路径式 lexical entailment 已有直接先例；项目窄化差异仍未验证。ACL 固定框 URL 对账为 1,747/1,747，但 229 条阅读深度不明，不能视为系统综述完成。见深度报告。

# 2026-10-07 Phase 100 进展

新增 BRISE-Plandok 方法邻接先例：UD→4lang 图 + 手写图模式 + 人工复核 gold，用于德语法规 formal-rule extraction。端到端全属性规则完全正确率 46%，但模式基于全标注集开发，且任务不是 WordNet gloss。该先例收窄宽泛新颖性主张，项目的 sense-bound source-support 仍缺 gold 和 matched experiment。详见报告。

# 2026-10-07 Phase 101 进展

ASAIL 2021 BRISE 原型已连接 4lang 图式规则抽取与 deontic prover；其 perfect 结果来自 6 句 toy set，不能作端到端性能证据。与 BRISE-Plandok 2025 合并为一个研究线。其先例进一步收窄“NL图规则+证明”宽主张；项目 glossary/source-support 差异未验证。见报告。

2026-10-07 Phase 108：发现评分 artifact 新增 macro 与源码/runtime 元数据后仍声明 schema `/0.1`，已将输出 schema 改为 `/0.2`、scorer 实现版本改为 `/0.3`，并在协议里区分输出 schema 与输入 sidecar schema。只做静态审查，未运行 CLI/测试。详见Phase 108。

2026-10-07 Phase 109：多参考 sidecar validator 原先允许 `complete` 与 `unresolved_candidates` 并存，可能使未决分析进入已裁决评分分母；现改为 complete 必须无未决候选，有任何未决分析则整项 unresolved，并将输入 schema 从 `/0.1` 升至 `/0.2`，scorer 实现标识升至 `/0.4`。同步标注协议/预注册草案；仅静态审查，未运行测试或 CLI。详见Phase 109。

2026-10-07 Phase 110：实现 `verify_gloss_oewn_relation_links`，核对 candidate row hash、source/gloss/sense、人工 genus mapping、raw OEWN pair 及 producer/replay hashes；replayer v3 增加 query 与 producer-report hash。仅静态审查，未运行 CLI/测试；没有人工 mapping 或 empirical result。详见Phase 110。

2026-10-07 Phase 111：按用户确认初始化 CodeGraph 并对 bridge 做结构审计。修正文档中把 sidecar 行称为 frozen candidate 的表述，明确 span 的语义由人工确认、validator 只核结构；同时拒绝全空白 span。尚未将 candidate manifest 外部 hash 接入 bridge，也未运行测试/CLI。详见Phase 111。

2026-10-07 Phase 112：bridge CLI 现在要求外部固定的 candidate-manifest SHA-256，并复用既有 validator 核对 sidecar 与清单一一对应；结果报告 schema/实现版本升至 `/0.2`。未运行 bridge/replay CLI、测试或数据验证。独立 bridge JSON Schema、真实 mapping 与经验评测仍未完成。详见Phase 112。

2026-10-07 Phase 113：新增 bridge link 与 validation report 的独立 JSON Schema，并强制 bridge candidate 集合等于 sidecar 全集，避免无映射候选掉出分母。仅静态审查，未运行 schema checker、测试或 bridge/replay CLI。端到端运行、真实 mapping 与评测仍未完成。详见Phase 113。

2026-10-07 Phase 114：通过 ACL Anthology/OpenReview 官方域定向检索与去重，SememeLRM、LREC 2026 adjective hypernym gold 和 Open English NameNet 均为已有记录；没有新增 direct baseline。ACL 2026 long-paper volume 列 2,223 篇论文，说明 1,747 行 ACL v3 是检索候选框而非全 ACL census。本轮不估计 recall 或 novelty。见Phase 114和[结构化日志](sources/literature_screening_log_2026-10-07_acl2026_lexical_relation_dedup.json)。

2026-10-07 Phase 115：定向筛读三篇 NeurIPS 2025 官方论文。miniF2F-Lean Revisited 提醒形式证明通过不能代替自然语言到形式目标的忠实度审计；HAR/CoPA 是分阶段自动形式化与 proof search 先例；Hierarchical Retrieval 使用 WordNet taxonomy，但不解析 gloss。未找到直接 gloss→Horn/span/replay matched baseline，不作新颖性主张。CodeGraph 状态正常，未运行测试/CLI/作者系统。见报告及[结构化筛读日志](sources/literature_screening_log_2026-10-07_neurips2025_autoformalization_wordnet.json)。
2026-10-07 Phase 116：ICLR 2026 定向筛读发现 ReForm 已在数学 autoformalization 中分离 compiler validity 与 semantic consistency，并构建专家标注/裁决 benchmark；法律 LLM 研究已提取 AND/OR phrase feature interactions。前者不是 WordNet gloss support，后者的 AND/OR 不等同 Horn 逻辑或 proof DAG。宽泛语义忠实度评测、AND/OR pattern 分析均不能单独作创新点。见报告和[日志](sources/literature_screening_log_2026-10-07_iclr2026_reflective_fidelity_and_andor_audit.json)。
2026-10-07 Phase 117：审计发现 Phase 19 source-lineage v1 未记录被实际使用的 `selected_basis_atoms.txt` hash，且入口未调用统一 frozen-bundle integrity lock。v2 已先验锁定 bundle、核 basis sidecar checksum，并记录 manifest/basis/lock、五个实现文件及 Python/platform 指纹。真实复算覆盖 110,340 条 selected clauses、110,382 个 payload/17.58GB，来源/identity/checksum 错误为 0；新增 Draft 2020-12 JSON Schema 并验证 v2 artifact 符合契约。只证明冻结结构来源链，不证明 gloss 语义支持；未运行项目测试。见报告、[结果](outputs/phase117/selected_witness_source_lineage.json)及[Schema](config/selected_witness_source_lineage.schema.json)。

2026-10-07 Phase 118：用当前 OEWN 2025 Plus verifier 重跑固定 360 项结构压力 claims，并由 `oewn-hypernym-path-replay/3` 独立回放；360/360 覆盖、160 个正路径、`valid=true`、0 errors。bridge 两份 JSON Schemas 通过 Draft 2020-12 meta-schema 检查。此证据只覆盖 taxonomy 路径与工件绑定，不是 gloss 语义 gold、准确率估计或 bridge 端到端结果。见深度报告、[producer](outputs/phase118/oewn_hypernym_stress_v1_verification_v2.json)和[replay](outputs/phase118/oewn_hypernym_stress_v1_replay_v3.json)。

2026-10-07 Phase 119：以两条明确标为非 WordNet 释义、非人工标注的 synthetic fixture 跑通候选 manifest→OEWN producer→replay v3→bridge validator，一个已裁决分支用于 wiring、一个 `unassessed` 分支保留在全候选分母。正确 manifest pin 得到 `valid=true`；错误 pin 和删去 unresolved bridge row 均 fail closed。四类 manifest/sidecar/bridge/report schema 均通过实例校验。此结果只验证 wiring/hash/分母契约，不验证语义 mapping、gold、IAA 或性能。见深度报告及[合成样例说明](examples/synthetic_gloss_oewn_bridge/README.md)。

## Phase 120：Findings of EMNLP 2025 推理/验证近邻筛查

对四篇官方论文做定向全文筛读，涵盖 formal proof benchmark、adaptive verification agent、principal knowledge grounding 和逻辑推理评价。结论：这些方向的宽泛方法已存在，不能单独作本项目创新点；但它们没有验证 WordNet sense/release-linked gloss spans 对 typed Horn rules 的逐项语义支持，也没有给出同任务的独立 source-only proof-replay baseline。四篇均未匹配冻结 ACL v3 候选框，不改 1,747 分母。EMNLP 2026 会议安排在 2026-10-24—29，晚于本轮截止日 2026-10-07。此轮不是 proceedings census，也不证明项目新颖或有效。详见Phase 120 报告和[机器日志](sources/literature_screening_log_2026-10-07_emnlp2025_reasoning_verification_grounding.json)。

## Phase 121：确认性标注包完整性重审

重跑 v3 annotation preregistration input preflight，21 项检查通过；400 个 blind task、答案键、release cross-check 与 24 strata 与锁定哈希相符。新 artifact 包含审计脚本/lock 指纹，见[结果](outputs/phase121/annotation_preregistration_v3_input_preflight.json)和深度报告。回传仍为 0；协议未签署、外部注册 ID 为空、分发未授权，所以这只证明本地材料完整，未生成 gold，也不允许声称开始标注。

## Phase 122：多参考 scorer / estimand 审计

静态核对确认 scorer 按 item 对预测与各完整可接受分析分别计分，取最高规则 claim F1 的 reference；不做 claim union，也不测 span/source semantic support。预注册需额外明确：裁决者必须在看模型预测前冻结 accepted alternatives；unresolved 项排除会使性能条件于裁决完成；macro 空/空排除使不同系统分母可能不同；当前 micro/macro 是无权重描述值，不可直接外推总体。单参考还是多参考 estimand 尚未选择，未改 scorer、未运行测试/CLI/预测。见Phase 122 报告。

## Phase 123：matched-baseline 评测就绪度矩阵

新增 [evaluation readiness matrix](docs/evaluation_readiness_matrix.md)，把 frozen structure、OEWN taxonomy replay、synthetic bridge、Pair verification、oracle prover、end-to-end 和人类 gold 分别按当前代码/工件与缺失 gate 对账。结论：结构性可复算和 taxonomy replay 有证据；bridge 仅 synthetic；三个模型评测轨道均无真实项目 gold-backed matched run。故项目是结构已审计、原型可运行但未经验验证；下一大缺口是获授权的人类来源标注和共同候选上的 matched experiment，不是再做一轮 synthetic wiring。详见Phase 123 报告。

## Phase 124：GCIDE 0.54 子来源结构复核

定向核读上游 GCIDE 0.54 README，确认它描述 1913 Webster、WordNet 1.5、志愿者等段落级混合来源，并允许一段定义有多个 `<source>` 标记。虽然 GNU 项目声明 GPL-3.0-or-later，冻结 evidence 尚未逐项绑定归档字节和子来源，也未追踪到规则/witness；1,573 payload-profile 与 1,580 evidence-object 计数口径尚不同。发布 clearance 不变。见Phase 124 报告。

## Phase 125：GCIDE 版本证据的受限 census

新增可复用审计器，仅扫描冻结索引中的 5,625 个目标 source payload，全部 checksum 通过。1,573 个唯一 payload 含 1,580 条 GCIDE evidence；其 `source_version=0.54` 且定义 SHA-256 格式均有效，计数差由多条 evidence 共存于 6 个 payload 解释。未对照官方 archive 字节、未恢复段落级子来源，也未追踪 graph rule/witness；release clearance 不变。详见[审计工件](outputs/phase125/gcide_source_evidence_census.json)和Phase 125 报告。

## Phase 126：GCIDE 官方归档定义哈希交叉审计

GNU 下载页 MD5 与本地 0.54 tar.gz 一致（归档 SHA-256 已固定；detached signature 未验）。受限复核 5,625 个冻结 payload checksums，扫描上游 179,781 个定义块；对 1,562 个不同冻结哈希，原始 `<def>` 内层字节命中 88 个，去标签并做 HTML 解码/NFC/空白归一化后命中 846 个（854 次归档出现）。另有 1,579/1,580 个 GCIDE evidence hash 精确等于同 payload 的 `synset.raw_definition` UTF-8 SHA-256。唯一异常哈希在归档中命中一个含 WordNet 来源标记的段落，提示混合来源审查线索，但不是独家归属判断。其余命中直接对应冻结 gloss 内容，但不判定唯一来源或语义支持；段落标记尚未连接 sense、rule/witness 或许可，发布状态不变。见[机器 artifact](outputs/phase126/gcide_archive_hash_crosswalk.json)和深度报告。

## Phase 127：GCIDE payload 到 graph/witness 的路径级 lineage

全量复核 5,625 个目标 payload checksums，将 1,573 个 GCIDE payload path 连接到 sense index、graph rule/hyperedge 与 selected witness。所有 payload 唯一对应 index identity；1,188 个路径出现在 active-clause 来源文档，886 个直接进入 selected-witness 来源文档，302 个仅在非选定活动子句，385 个无 active-clause 来源路径。1,570 个 graph heads 均有 rule/witness；40 个 seed，1,530 个非 seed witness clause 全部与 rule/hyperedge 对齐。Phase 126 唯一 WordNet-marker 异常 payload 在 385 个无来源路径项中，不进入 selected witness。路径 lineage 不代表 gloss-span 语义支持或许可清权。详见[机器 artifact](outputs/phase127/gcide_graph_lineage.json)及Phase 127 深度报告。

## Phase 128：selected-witness gloss hash 与归档子来源标记

在 886 个 selected-witness-linked GCIDE payload 中，506 个 gloss hash 于官方 0.54 归档按去标签/HTML/NFC/空白规范化匹配（502 个 distinct hashes，503 次归档出现）。46 个 payload 至少匹配到 WordNet marker 段落，433 个匹配到 Webster 1913 marker 段落，489 个匹配到任一非空 marker；这些来源类别可因同 hash 出现在多个段落而重叠。380 个 payload 在当前变换下未命中。此结果提供 selected-witness 路径上的 gloss—归档文本关联，但不证明 marker 独家归属、rule literal 语义支持或许可。见[机器 artifact](outputs/phase128/gcide_marker_witness_crosswalk.json)和深度报告。

## Phase 129：精确释义重复 split 防线

候选 freezer、manifest validator 与 standalone NLI dev/test evaluator 现检查精确 raw-premise UTF-8 SHA-256 不跨 train/dev/test；若独立 NLI 输入使用该 hash，则必须覆盖全部行。该规则跨资源、release、sense 生效，且不改变既有 schema。协议明确此检查不覆盖规范化变体或语义近重复。当前没有真实项目候选 manifest，因此只补齐工程门槛，没有测出数据泄漏或模型分数影响。代码语法及文档/配置一致性检查通过；未运行测试套件。见Phase 129 深度报告。

## Phase 130：2026 最新词汇解释与形式证明近邻复核

对 AKBC 2026 lex-NLI（已接收、workshop 尚未举行的 arXiv v1）和 ACL 2026 SememeLRM 的官方来源与全文任务边界作定向核对，并将其补入研究定位备忘录。前者已结合结构化 lexical explanation、多参考人工 gold 与 LangPro proof；后者已从定义构造 sememe tree 并评词汇关系/蕴含。它们排除了“结构化词汇解释+prover”及“定义→结构词汇语义→关系预测”的宽泛新颖性说法。可能的 sense/release-bound gloss-span→typed AND/OR Horn support + source-only proof 仍只是待测假设。此轮不是系统综述、复现或新颖性证明。见Phase 130 深度报告和[研究定位备忘录](docs/research_positioning_and_prior_work.md)。

## Phase 131：多参考 gold 的 source/sense identity 绑定

修正多参考 scorer 的身份校验：同一 sidecar item 的裁决记录必须共享来源/义项身份，prediction 也须与之匹配，避免相同释义字符串的跨义项/跨资源预测误计分。Scorer 标识升至 `/0.5`，schema 未变。完成静态语法与登记一致性检查；未运行测试，真实 gold 与预测仍缺。见Phase 131 深度报告。

## Phase 132：OEWN 400 项 blind batch 来源/署名 gate

核对锁定 preflight、批次 manifest 与官方 OEWN/Princeton 条款：400/400 raw gloss 与 pinned OEWN 2025 Plus 逐项匹配，manifest 记录双方署名、许可链接、修改说明和用途限制。锁仍为未签协议、未授权分发、0 个回传；本轮不授权外部标注或公开发布，也不覆盖混合来源冻结包。见Phase 132 深度报告和[发布门槛](docs/data_release_gate.md)。

## Phase 133：KR 2026 provenance prior 与近期 lexical/rule 工作去重

补入 KR 2026 Datalog why(-not)-provenance 直接先例，收窄 witness/support/provenance 的宽泛新颖性边界；重核 IJCAI NRI、LREC 2026 adjective hypernym gold 与 NALOMA Neural DTS，确认三者已在项目文档中，避免重复计数。Gloss-span 对 typed AND/OR Horn 的人工 source-support 与 source-only replay 仍是假设，无 gold/matched outcome。见Phase 133 深度报告。

## Phase 134：KR 2026 最小支持、FOL 解释与 proof-search 邻接筛查

官方目录主题补查新增 query relevance/minimal support、FOL 公式非等价解释、终止 proof-search 分解树、Lean chase 形式化等 prior-art 边界；均不是 gloss-span→typed Horn source-support 的匹配 baseline。证据仅至官方摘要层，不构成 KR 全目录 review。核心差异仍是未验证假设，无 gold/matched results。见Phase 134 深度报告。

## Phase 135：EACL 2026 WordNet gloss 与 lexical prediction prior

新增 EACL 主会 CAP 全文筛读：WordNet definition→term 与 word→hypernym prediction 均有先例；其条件于预答正确子集的 activation-pooling accuracy drop 不是全量准确率、source support 或形式证明。论文未入 ACL v3 候选框，检索词应增加 inverse definition modelling / definition-to-term。无项目 gold/matched result。见Phase 135 深度报告。

## Phase 136：ACL definition-conditioned lexical prediction 候选扩展

ACL 搜索器增加释义条件词汇预测词族，冻结 v3 不变，新建 v4 1,748 条；相对 v3 精确 ID join 新增 EACL 2026 CAP 一条、无删除。词族命中两篇，其中 Cho et al. 2020 已在旧框。v4 全部有 URL 日志，但深度为全文 76、定向 167、摘要/元数据 1,276、未明 229；不能将 URL 命中解释为全量筛读。详见Phase 136。

## Phase 137：固定 ACL 导出同源消融

生成器现支持固定压缩源离线重跑与 query-family exclusion。固定同一官方导出后，旧词族 1,747 IDs 与 v3 完全一致；加入释义条件词族得到 1,748，唯一新增 EACL 2026 Aljaafari et al.，无删除。原始压缩导出含年份窗口外、混合许可材料，仅保留本地复算。详见Phase 137。

## Phase 138：ACL 搜索器流式解析

逐条目解析固定 ACL 导出，释放全量解压文本与所有 BibTeX 记录中间副本。与 v5 候选框比，1,748 个 ID 和全部共同记录字段完全一致；源内容哈希、条目数、旧查询族计数和筛读深度分布均相同。运行中工作集样本约 69 MiB（历史旧流程观察样本约 966 MB；非受控峰值比较）。详见Phase 138。

## Phase 139：OEWN 全量名词 genus 基线复现核验

当前工作树对 OEWN 2025 Plus 全名词基线复算，53 个输入文件逐一与固定归档字节比对通过；结果 JSON 与 Phase 11 字节级一致。候选覆盖 96.995%，候选任一义项同版直接 hypernym 命中率 38.006%；两者都是同资源弱 proxy，不是语义 gold 或 sense-level precision。详见Phase 139。

## Phase 140：400 项标注批次与三轨适配审计

确认盲标返回形状可记录逐 gloss span 和方向规则支持，未来适用于 Track C 人工 reference；它不是 Track A pairwise NLI 数据，Track B 仍需固定 formal inputs。presentation 顺序/hash 回放通过，但 schema/protocol 未在 input lock 中固定，协议/分发未授权、零回传。详见Phase 140。

## Phase 141：Track A premise 目标上下文审计

发现 claim-review `/0.1` 强制模型 premise 等于 raw gloss，但没有 target lemma 输入或冻结的 hypothesis 模板，因而尚不能确认人审与 NLI 接收相同的 sense context。建议先审阅 lemma+POS+原文 gloss 的新版本 renderer 和 raw-gloss-only 消融，分别哈希两种输入，再生成 pair frame。见Phase 141。

## Phase 142：ACL 2026 分步 claim factuality 方法审查

补入 Ye et al. ACL 2026 的 claim 原子分解与显式 source-support 检查 prior；宽泛的结构化 prompt/分步事实核验不再适合作为新颖性主张。方法可作为未来同输入 Track A/Track C 适配 baseline，但不是 WordNet gloss 或 Horn 证明的匹配结果。未建候选对、未运行模型；项目 gold 与主估计量仍未冻结。详见Phase 142。

## Phase 143：source-only 推理与 NLI 路由静态审计

静态审计确认 source_only 的事实分区过滤、类型 fail-closed、proof/countermodel 独立回放、unknown 路由、source bundle 验证及 NLI export hash/group gate 都有代码实现；反模型解释严格限于所给有限程序。该结果不是运行时或语义正确性证据，且当前仍无项目 pair/gold/NLI export。详见Phase 143。

## Phase 144：Track A 输入身份复核

固定 OEWN release 对账确认 v3/400 的 sense ID 与 raw gloss 均为 400/400 匹配，但存在 1 个 POS 冲突和 1 个 target lemma set 不完整。保留 v3 原文件；未来 Track A 的 POS/完整 lemma 从 release record 重取。直接 hypernym 只作候选分层，parent 多 lemma hypothesis policy 尚未冻结，因此未生成 pair frame 或标签。见Phase 144 报告和[机器审计](outputs/phase144/annotation_frame_release_identity_audit.json)。

## Phase 145：父 lemma hypothesis surface 策略审计

322 条直接 hypernym edge 对应 311 个父 synset。按 release 全部父 lemma 逐词面生成候选共 680 行；单一词面/edge 为 322 行，但 lexical sort 不能解释为语义 canonical。全部表层变体应按 relation edge 关联并在该组内完成独立 pair 标签；宏观估计量需先声明 surface/edge 权重。草案 split 闭包为 279 组件、最大 26 行，仅作 renderer 冻结前的可行性信号。现 manifest/0.2 还缺 parent synset 与 edge provenance 字段，需新版本；无 pair、label、split 或 model run。详见Phase145。

## Phase 146：Track A context/hash/cluster 契约审计

现行 `/0.1` sidecar 与 NLI strict route 将 model premise hash 视为 raw source gloss hash，evidence span 也依 premise 字符位置；候选 manifest 缺 parent relation identity。680 个表层候选需要 edge 关联，但当前 `group_id` 一边控制 split 泄漏，一边作为一行/组的 dev 独立校准单位。新版本需拆 raw gloss/premise hashes、source spans、parent provenance、split grouping 与 calibration unit；strict export/route 和 content-effect evaluator 同步迁移。未改变旧 schema，未生成候选/标签，也未运行测试或模型。详细证据见Phase 146 报告。

## Phase 147：Track A pair contract 形成审议草案

将 Phase144–146 的输入、表层候选、双哈希、span、split/calibration 约束整合为[Track A pair contract 设计草案](docs/track_a_pair_contract_design_options.md)。建议区分 raw-gloss source support 与 condition-specific NLI relation gold，并把 edge/surface/统计单位分开；预估 680 surfaces × 2 contexts = 最多 1,360 pair-condition 行、双标最多 2,720 个判断。Verb hypothesis grammar 与 IID calibration 兼容性仍未解，尚未生成 pairs、labels、schema implementation 或模型结果。

## Phase 148：selected witness bridge 格式迁移审计

单目标结构证书（3,596 nodes、14,923 edges）、当前 checker 格式的 Datalog bridge（3,512 rules）与 Phase117 全量 source-lineage/bundle hash 绑定均通过。Phase6 历史 bridge 的 proof result 与当前 checker 不再逐对象相等，原因是当前证书节点增加了 `source_bindings` 与 `source_claim_refs`；其存储 summary、proof certificate、节点集和边多重集均保持通过。审计器将历史兼容性差异与当前可复算结果分开记录。该证据限于冻结图结构，不证明 gloss 语义支持或开放世界蕴含。见Phase 148 报告和[机器审计](outputs/phase148/witness_example_replay_audit.json)。

## Phase 149：ACL 2026 gloss 对照与 claim-support 先例补查

框外定向全文筛读新增 G-IdiomAlign 与 ReportLogic 两篇 ACL 2026 long papers。前者已做 Wiktionary gloss/no-gloss 对照，部分使用人工校准 embedding proxy；后者已用三专家多数判断评价研究报告级 evidence sufficiency/warrant/claim-support。由此将“gloss ablation”与一般人评 auditability 从宽泛新颖性候选中移除；项目窄化假设仍是 sense-bound gloss span→directional typed AND/OR Horn support 与 source-only proof replay 的联合 gold 评价，尚无效果或新颖性实证。两篇均未命中固定 ACL v3 候选框及旧日志，不改变 1,747 行分母。见Phase 149 报告与[结构化日志](sources/literature_screening_log_2026-10-08_acl2026_gloss_auditability_addendum.json)。


## Phase 150：COLM 2026 Q-CARE claim verifiability 邻接审查

官方接收目录确认 Q-CARE 为 COLM 2026 论文；定向核读确认其已做人标 atomic claim–retrieved chunk pairwise support benchmark（320 queries、7,907 claims、三人多数裁决），其自动 checker 是 LLM 判断而非逻辑证明。项目不再把一般 claim support/human verifiability 作为宽泛新意；sense-bound gloss-span→directional Horn literal support 与独立 proof replay 仍只是待证任务差异。Track A 合同四项选择未冻结，未生成候选或标签、未改 schema、未运行测试。证据见Phase 150 深度报告和[结构化筛读日志](sources/literature_screening_log_2026-10-08_colm2026_qcare_fulltext.json)。


## Phase 151：COLM 2026 grounded logic 与 judge 可靠性扩展筛读

按官方 COLM 接收目录的 targeted title terms 扩展 Q-CARE 后续筛查。全文核读 No Free Labels 与 LogicIF，摘要筛读 GraphWalker、GDP-RAG。新增核心边界：LLM correctness judge 依赖其求解能力与正确参考；code-executable gold + human-checked NL instruction fidelity 已有先例，但不能替代真实 gloss source-span support gold。两篇摘要级图/RAG 系统仅列邻接。无项目代码/数据复现、matched baseline、pair/label 或 schema migration；Track A 四项选择仍未冻结，项目效果/新颖性未证。详见Phase 151 深度报告与[结构化日志](sources/literature_screening_log_2026-10-08_colm2026_grounded_logic_addendum.json)。

## Phase 152：当前文献快照与 Track A 实现边界深度复核

重核用户更新后的 ACL v6：1,748/1,748 精确 URL 命中结构化筛读日志；Phase142 grounded-claim 论文仍属框外发现，LoReFact 与 OEWN 形容词 hypernym gold 已有筛读，避免重复。CodeGraph 当前索引健康（140 files / 2,466 nodes / 4,915 edges）；调用图确认旧 NLI 导出链路没有 contextual premise renderer。Phase147 的四项 pair contract 选择仍未决定，因此本轮不贸然创建 `/0.3` schema 或 pair。详见Phase152 深度报告。

## Phase 153：Track A 设计、estimand 与校准单位

将主问题建议收窄为 raw-gloss span 对 sense-bound relation edge/typed literal 的直接支持；exact-condition NLI 三分类另作上下文对照，不能替代 source-support gold。全部 parent lemma surfaces 作为 edge 内嵌套行；以 target sense 等权汇总上下文效应，split/区间按 lemma-sense-edge leakage component 处理。现行 IID NLI calibration gate 不适用于全部 surface rows；需要 cluster-aware calibration，或将其结果限为描述性。首轮建议 noun-only，并把 58 条 verb edges 留作独立模板预试。新增[裁决备忘录](docs/track_a_design_decision_memo.md)和Phase153报告；方案仍待研究者确认，没有生成数据或改 schema。

## Phase 154：分层 selective-risk prior 与校准契约复核

全文筛读 2026 arXiv HG-CRC：有预注册 group hierarchy、逐节点 Bonferroni risk control、leaf-first fallback 与 split calibration 先例，削弱一般 hierarchical LLM abstention 的宽泛新颖性；但形式保证假设 IID calibration examples，group membership 并不解决项目重复 surface/condition 的相关性。代码复核区分离线 Wilson exploratory selector 与固定网格 exact-binomial strict selector，并确认旧 exporter 用 `group_id` 同时承担 dev/test isolation 和 one-row calibration。新增[筛读日志](sources/literature_screening_log_2026-10-08_hierarchical_group_risk_control.json)及Phase154报告；未改代码、schema 或数据。

## Phase 155：多元 typed Horn 编译边界与目标变量缺口

静态审计确认 compiler v5 的 unary 限制来自目标 referent 识别惯例：schema 0.6 记录 variable sorts，却没有指定哪个变量代表目标义项。typed Datalog checker 已支持任意元数，因此应先定义显式 `target_variable` 的新增草案；充分方向可在每个 DNF 分支含目标变量时允许额外 body-only 变量，必要方向含非目标 head 变量则不满足普通安全 Datalog，应拒绝或另行定义存在规则语义。旧 schema、代码和冻结数据均未改。详见Phase155深度报告。

## Phase 156：显式目标变量 schema 0.7 与多元 Horn 编译器 v6

实现实验性 `0.7-draft` 校验、编译和 agreement 支持：新增必需的自由 `target_variable`；旧 schema 继续走一元共享变量路径。多元充分规则采用有界 DNF 并逐分支要求目标变量；必要方向若结论出现非目标变量则拒绝。编译 provenance 记录 schema/target，agreement v13 对齐目标字段。Python 语法编译与项目 JSON 静态检查通过；未运行测试、Datalog replay 或真实标注，不能据此声称语义正确或有效。详见Phase156报告。

## Phase 157：schema 0.7 到 source-only proof route 的多元事实绑定审计

静态调用链审计发现 source-only matcher 仍强制 gloss atom/fact/query 均为 unary，阻断 0.7 多元事实。本轮改为按 AST 变量/常量逐论元 ground-match、校验重复变量，并要求目标变量绑定等于 query target；旧 unary 路径保留，pipeline 升至 `/12`。blind v3 importer 仍固定输出 schema 0.4，0.7 尚无 blind return/import round-trip。仅 syntax-check，未运行 proof/source bundle/NLI route。详见Phase157报告。

2026-10-08 Phase159：定向筛读 ACL Industry Track T²（Lean 后继定理行为测试）、Findings ACL FoVer（形式 verifier 步骤监督、在 NLI 上评估 PRM）及 SemEval 2026 Task 11（控制 syllogism 的 plausibility/distractor/multilingual 条件）。据此明确 formal proof/replay、dependency behavior 与 WordNet gloss-to-rule semantic support 为不同评价轴；没有一项给出本项目的 matched baseline 或 gloss-span gold。单人三论文筛读，不是系统综述；未改冻结候选框、schema、图或数据。详见Phase159。

2026-10-08 Phase160：静态调用链审计确认 typed Datalog 的 proof/countermodel replay 会重新校验当前 type-system/signature hash；正向 route 证书回放失败时不通过。pipeline 新增 `invalid_typed_program` unknown 原因码，并在 route `evidence_checks` 暴露重算后的 typed validation，未提供 type table 明确为 `not_requested`；版本升至 `/13`。仅语法检查；未运行测试或真实 0.7/来源包回放。结论是诊断可审计性增强，未新增 soundness 或语义 gold 证据。详见Phase160。

## Phase 158：blind importer 的显式 canonical schema 选择

canonical importer 新增 `--canonical-schema-version` 与 API 参数，可选择 0.4–0.7；默认仍为 0.4，validator 对新 schema 字段作最终拒绝/通过门。锁定 v3 batch、manifest、answer key 均未改；尚未新增 schema-specific blind task/return UI 或材料，亦未运行 importer round-trip。详见Phase158报告。


## Phase 161：运行环境与外置 bundle 可复算性审计

对维护中的 132 个 Python 文件作 AST/import 静态扫描：无解析错误，未发现非标准库且非项目内的顶层导入；Python 3.10+ 标准库政策与声明 CI 矩阵相符。当前配置的仓库外 frozen bundle 路径及 manifest 存在，但没有执行 integrity replay，也没有运行 CI 或测试。结论仅支持核心代码环境轻量、外置数据路径可见；完整数据复现仍需另行核验 bundle 锁定字节。CodeGraph 初始化后状态正常且索引最新（140 files、2,466 nodes、4,915 edges）。详见Phase161报告和[机器快照](sources/reproducibility_environment_audit_2026-10-08_phase161.json)。


## Phase 162：外置冻结 bundle integrity lock 重放

对 project config 指向的 bundle 使用只读 integrity verifier：manifest semantic fingerprint 和 6 个锁定文件 SHA-256 均通过，错误数为 0。审计没有逐个读取 checksums sidecar 的全部来源 payload，因此不声称全量 source payload 当前完整性；也不涉及来源许可、gloss 语义、模型效果或新颖性。无测试、CI、模型或 proof route 运行。详见Phase162报告与[机器结果](outputs/phase162/frozen_bundle_integrity_replay.json)。


## Phase 163：来源 payload 全量完整性当前复算

2026-10-08 重新读取 sense index 引用的 115,235 个唯一 source-record payload，共 18,734,636,389 bytes；JSON 全部可解析，byte count 与 SHA-256 全部匹配 checksums sidecar，重复路径/畸形索引均为 0。聚合结果与 Phase23 留存报告的 SHA-256 完全相同（`9ff9ea44209fdb27e7967123ed9570f5a95ca236d6fc147ae955aa34f4d6dc2d`）。这确认 bundle 内部当前字节完整性，不建立上游权利、gloss 语义或论文有效性；`release_clearance` 仍为 `not_assessed`。详见Phase163报告和[机器结果](outputs/phase163/source_release_metadata_audit_current.json)。


## Phase 164：NeurIPS/ICML formal reasoning 与 verifier 补筛

对官方 NeurIPS 2025 与 PMLR ICML 2025/2026 proceedings 作定向候选检索，补充 APOLLO、Weaver、MuSLR、ICML 2026 formal problem-solving/proof-sketch/self-verification 与 ICML 2025 RULEBREAKERS；APOLLO/Weaver 核读全文相关章节，其余摘要级。形式证明修复、弱 verifier 聚合、自验证训练和 formal-rule benchmark 均已有先例；仍未发现本项目任务的 WordNet gloss-span→typed Horn matched gold。此为选择性补查，不是全量 proceedings census 或系统综述；未运行论文代码/项目实验。详情见Phase164和[机器日志](sources/literature_screening_log_2026-10-08_icml2026_neurips2025_formal_verification.json)。


## Phase 183 状态增量

COLM 2026 Quokka 提供了候选正确性与下游验证效用分轴、三态 verifier 与预算敏感 utility 的形式验证先例。该结果只收窄宽泛评价主张，不是 WordNet gloss 语义支持证据。项目 gold、matched baseline、效果与窄新颖性仍未证。详见Phase183深度复核。

## Phase 184 当前图结构证据

现态冻结超图与最小 witness-depth 两项审计均重放成功，输出与 Phase175 逐字节一致；110,425 个 selected witness 仍全部达到最小 grounded depth。该结果只支持当前正 Horn 表示可复算，不替代人工 gloss-span support gold 或来源许可。详见Phase184深度复核。

## Phase 220：混合来源权利证据覆盖审计

Phase24 的 90 个候选来源 profiles 中，25 个与现有权利日志精确标签匹配，65 个没有匹配；profile-payload 计数合计 3,595，不能解释为唯一记录数或清权数。最大未匹配部分为 22 个非规范/非标量 profile（1,199 个 profile-payload 计数）。报告将 MeSH 的 NLM 署名/时效要求与 OLS 聚合缓存的逐 ontology 版本绑定列为近期来源审计重点；整体公开状态保持 `not_cleared_for_public_release`，Track A 设计仍待裁决。见Phase220报告和[机器 crosswalk](sources/source_rights_coverage_audit_2026-10-08_phase220.json)。

## Phase 221：MeSH/OLS 上游记录身份与版本绑定

再次校验受限来源族的 5,625 个唯一 payload，checksum 全通过。新增审计发现 130 个 direct-MeSH/OLS-MeSH 共现 payload 可通过明确的 URI/namespace 尾部规范化形成相同标识符，并逐个在当前 NLM MeSH RDF API 得到 130/130 identifier echo 匹配；这是当前 ID 解析证据，不是 frozen cache 历史版本/字节 crosswalk。OLS 五个 namespace 的当前 version IRI 已采集，但本地 profile 仍只写 generic query-cache snapshot 且没有下载 URL。发布 clearance 不变，Track A gold/有效性/新颖性尚未证明。见Phase221深度报告、[机器审计](sources/mesh_ols_record_binding_audit_2026-10-08_phase221.json)和[审计器](src/analysis/audit_mesh_ols_record_binding.py)。

## Phase 222：来源 evidence 生产边界与前向捕获合同

当前 checkout 中未发现 `source_evidence` 写入端；命中均为消费者/审计工具，不能据此断言上游不存在 producer。新增未来采集用的捕获合同和 Draft 2020-12 JSON Schema：payload SHA-256 + evidence ordinal 定位本地对象，显式区分身份绑定、上游版本/bytes 绑定和权利审查。合同未接入 producer，不回填/修改冻结记录，`rights_clearance` 固定为 `not_assessed`。下一 gate 是找到原 producer 或建立 versioned acquisition component，并完成 schema validation 与端到端 replay。见Phase222报告、[合同](docs/source_evidence_capture_contract.md)和[schema](config/source_evidence_capture.schema.json)。

## Phase 223：外置冻结管线边界与捕获合同一致性

Frozen bundle 中仅有 `tools/read_graph.py`；recovered history 标注 `Wn2Lingua/KaikkiBasisHeldoutEvaluation`，但 producer hash 和其引用的源文件均不可得。保存的结构 replay 报告 154,206/154,206 clauses 有 source-DNF evidence、解析错误为 0，但 canonical replay 精确匹配 110,424/110,425 heads。结论是结构材料部分可复核，生成代码端到端复现未建立，gloss 语义支持也未证明。本轮发现并修复 Phase222 合同与 schema 不一致：新 schema 必须记录 producer、parser 与 normalizer 的实现 SHA-256。见Phase223报告、[机器审计](sources/source_producer_boundary_audit_2026-10-08_phase223.json)、[合同](docs/source_evidence_capture_contract.md)和[schema](config/source_evidence_capture.schema.json)。

## Phase 224：冻结 replay 单例差异现态复核

用既有冻结包例外审计器对当前外置 bundle 重跑，找到相同 1 个例外；semantic fingerprint、manifest/replay/index/rules 输入 SHA-256 和例外明细均与 Phase8 artifact 一致。`ext_wikt_full_dd659c7fcb3b` 的冻结 graph clause 与唯一 selected witness clause 匹配，depth=376，source-DNF evidence 标志为 true。此项确认冻结包内部例外声明现态稳定，不等同于上游 replay、witness 证明证书或 gloss 语义的独立验证；source payload 未打开。详见Phase224报告和[现态机器输出](outputs/phase224/frozen_bundle_replay_exceptions_current.json)。

## Phase 225：NeurIPS 2026 自动形式化与证明检索补筛

对官方 Downloads 索引新增四篇候选的定向全文章节审阅：教材到 Lean 大规模形式化、logic textbook theory-scale/LCS-Bench、global premise retrieval、Lean proof 多目标 refactoring。它们排除了若干宽泛创新主张，但均不提供 WordNet sense/release-bound gloss-span 对 typed Horn literal 支持的 matched baseline。官方 poster detail 页面未取到，track 仍标未核；目录为混合 event index，因此本轮不是系统综述。详见Phase225报告和[机器筛读日志](sources/literature_screening_log_2026-10-08_neurips2026_autoformalization_and_proof_graph_phase225.json)。

## Phase 226：资源关系、gloss、Horn 与 NLI 证据接口审计

静态核对确认 OEWN 路径验证和 single-sense proof/NLI route 是相互独立的组件：前者不能给出 gloss 语义判断，后者不能验证资源关系，也没有 `relation_edge_id`、parent-surface 和 condition-renderer 的共享 join。更新逻辑验证文档，列明各证据能证明什么与联合结果必须保留的独立状态。没有改动 verifier、数据、schema 或 Track A 草案；Track A 尚待裁决。见Phase226深度报告和[结构化审计](sources/evidence_layer_interface_audit_2026-10-08_phase226.json)。

## Phase 227：AND/OR basis 两两删除交互

新增 bit-mask 批量固定点算法，精确重算 85 个 basis 的 3,570 个两两删除场景。1,102 对存在单独删任一 basis 时仍可达、但联合删除后额外失活的 head；最大交互 `by-4`×`under-2` 为 3,700 个 head。全 pair 单调性检查通过；4 个情景直接 closure 对拍一致，第二路径复跑字节相同。交互是冻结图结构冗余，不是来源语义或语言学效应。见Phase227深度报告、[方法说明](docs/pairwise_basis_deletion_interactions.md)、[机器结果](outputs/phase227/pairwise_basis_deletion_interactions.json)及[审计记录](sources/pairwise_basis_deletion_audit_2026-10-08_phase227.json)。
## Phase 228：可靠性工程 pairwise interaction 先例审计

相关工作审计确认，JRI/JFI、故障树 gate-event 联合重要度、minimal cut sets 与 joint structural importance 均有先例。数学上，Phase227 的 21,878 个 pair×head 联合独有损失恰对应当前冻结图上 head-level 二元素最小删除割集；1,102/3,570 是包含至少一个此类 head 的 pair 数。不支持方法新颖、来源冗余或词义语义效果。方法页已更正为逐 head 检查全部 pair-world 位集合包含。见Phase228报告、[结构化文献日志](sources/literature_screening_log_2026-10-08_reliability_interactions_phase228.json)和[修正后方法页](docs/pairwise_basis_deletion_interactions.md)。

## Phase 229：basis source-record 身份与 payload lineage 审计

新增只读复算 CLI：85/85 basis IDs 一对一匹配 node 与 sense index；166/166 payload 的 sidecar 长度、SHA-256 与 sense/basis identity 通过；全图 154,206 个 clause 均有有效 source-index row，覆盖 154,356 条 source-document×clause 链接；主输出与另一输出路径复跑逐字节一致。来源身份链现已具备，剩余缺口是 source-document deletion 的规则干预语义和 gloss-span 语义支持，不应将 basis seed deletion 解释为来源文件删除。见Phase229报告、[CLI](src/analysis/basis_source_lineage_audit.py)、[结果](outputs/phase229/basis_source_lineage_audit.json)与[机器记录](sources/basis_source_lineage_audit_2026-10-08_phase229.json)。

## Phase 230：basis sense payload bundle deletion 对照

定义并复算两种明确干预：只删 basis seed；以及删除该 sense 的全部冻结 source-record payloads、撤回 seed 并禁用以该 sense 为 head 的规则。3,570 对的两种闭包损失集完全一致，额外损失为 0；7,140 个被删 basis-head/pair-world incidence 中 seed-only closure 均未重新推出对应 head。全部 seed-only 计数逐行匹配 Phase227，四个直接 closure 对拍通过，独立输出路径复跑字节一致。只适用于冻结 payload bundle，不是上游 WordNet 文档删除。见Phase230报告、[CLI](src/analysis/basis_payload_bundle_deletion_audit.py)、[结果](outputs/phase230/basis_payload_bundle_deletion_audit.json)与[机器记录](sources/basis_payload_bundle_deletion_audit_2026-10-08_phase230.json)。

## Phase 231：单个 basis source-record payload 删除敏感性

对 166 个 payload scenario 显式比较“任一登记来源仍在即可保留 clause”与“必须所有登记来源都在”的两种 bookkeeping 策略，并与 seed-only deletion 比较。两种策略在 110,425 个 head×166 个 scenario 上的 loss set 都与 seed-only 完全相同；22 个单 payload basis sense scenario 非零，最大损失 109,343 个 head；24 个直接 closure 对拍和独立路径复算通过。这只说明固定图与当前干预定义下的闭包不变，不证明 producer 多来源语义、来源独立性或上游 WordNet 文档删除效应。见Phase231报告、[CLI](src/analysis/basis_single_payload_deletion_audit.py)、[结果](outputs/phase231/basis_single_payload_deletion_audit.json)及[机器记录](sources/basis_single_payload_deletion_audit_2026-10-08_phase231.json)。

## Phase 232：NeurIPS 2026 LogicTree-RAG 近邻筛读

全文定向筛读 NeurIPS 2026 接收论文 LogicTree-RAG。它把 source-document spans 绑定到 hierarchical logic-tree generation，并用 GPT-5 judge + 20-case human audit 评估节点级 evidence support；另有三位专利从业者对 10 个文档作盲法人审。由此，通用“logic tree + 来源证据 + evidence-faithfulness 人审”不能作为宽泛新颖性主张。论文没有做 WordNet sense-specific gloss→typed AND/OR Horn support 或 proof replay；此范围差异仍不是新颖性证据。见Phase232报告、[结构化日志](sources/literature_screening_log_2026-10-08_logic_tree_rag_neurips2026_phase232.json)与[近邻对照](docs/closest_work_comparison.md)。

2026-10-08 Phase237：对账发现 LREC 2026 main *When Structure Matters* 早在 2026-10-05 已完成 18 页官方 PDF 全文筛读，但此前未列入 closest-work 表。本轮将既有证据补入矩阵，并重核 ACL/LREC 官方 venue 元数据；没有新增文献或候选分母。详见Phase237对账报告与[去重记录](sources/literature_screening_log_2026-10-08_lrec2026_wordnet_hyperbolic_phase237.json)。

## Phase 233：证明与 NLI 路线定向运行审计

运行 Datalog checker、annotation→Horn compiler、strict proof/NLI pipeline、NLI gate、OEWN hypernym verifier 与两类证书 replay 的 7 个定向测试模块。首次发现两条 schema 0.5/0.6 测试仍断言 compiler v5，而源码、协议和 readiness matrix 已统一为向后兼容 compiler v6；修正测试断言后 72 项全部通过。只更新了过期测试期望，没有改编译行为。该结果是合成/单元回归，不证明真实 gloss-span 支持、NLI 效果、授权或论文效度。详见Phase233深度报告和[评测 readiness matrix](docs/evaluation_readiness_matrix.md)。

## Phase 234：Track A 跨层身份字段传递审计

静态对照 OEWN resource inventory、hypernym verifier、claim-review `/0.1`、candidate manifest `/0.2`、NLI export `/0.2` 与 strict proof/NLI route。精化 Phase226 的“没有共享 edge ID”：上游 inventory 已生成绑定 release/child/parent 的确定性 `relation_edge_id`，并枚举 parent lemma surfaces；但这些身份未传入候选、导出和 strict route。record `/0.1` 还强制 premise hash 与 raw-gloss hash 相同，无法表达条件化 premise renderer。7 个实现文件的 SHA-256 对现态复算一致；未改代码/schema、未生成 pair 或 labels。研究选择与授权仍未冻结。见Phase234报告、[字段对照](docs/track_a_identity_field_crosswalk.md)和[机器审计](sources/track_a_identity_field_crosswalk_2026-10-08_phase234.json)。

2026-10-08 Phase235：CodeGraph 调用链审计确认 release identity audit、OEWN hypernym inventory 与 claim-review/NLI exporter 是分离路径；当前 inventory 的调用者为自身 CLI、identity-impact audit 与 workload audit，NLI exporter 不消费 relation-edge inventory。端到端 edge→surface→condition→proof/NLI join 尚不存在。未改代码/schema/frame/pairs/labels/protocol，未运行测试、模型或标注；不构成语义效果或新颖性证据。见Phase235报告与[机器记录](sources/track_a_candidate_flow_audit_2026-10-08_phase235.json)。

2026-10-08 Phase236：发现并修正 Track A v1 草案与 Phase153 备忘录的 NLI estimand 冲突。现在建议 NLI 条件差按 child target sense 抽样设计加权（target-sense-equal）为主，edge-population 加权作敏感性；gloss source-support 主结果仍为 edge-population 加权。此为未批准设计建议，没有生成 pairs/labels/splits/schema 或运行测试；协议签署、许可和 gold 仍未完成。见Phase236报告与[机器记录](sources/track_a_estimand_consistency_audit_2026-10-08_phase236.json)。

