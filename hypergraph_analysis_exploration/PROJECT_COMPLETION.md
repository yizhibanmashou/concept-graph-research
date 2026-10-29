# Current Project Status (2026-10-12, Phase277)

> CI note (2026-10-29): this is a historical snapshot. Its subproject workflow is inactive in the current repository; the equivalent research matrix is now configured in the [root workflow](../.github/workflows/checks.yml), but has not run on GitHub. See the [current CI scope](docs/continuous_integration.md).

Phase277 mapped the 2026-09-30 meeting direction to current evidence: initial dependency-graph exploration is aligned, while validated gloss-to-logic production at 100k-sense scale and real reasoning/NLI evaluation remain uncompleted. Prior ordinary-graph findings are retained as exploratory history with unsupported interpretations withdrawn. See [Phase277 meeting alignment](../report/project_review_2026-10-29-current.md).

Phase276 screened ACL 2026 Lingua-Graph against the project. This strengthens the prior-art boundary around reusable explicit graph representations, while leaving the narrower WordNet gloss-span→typed Horn support and replayable lexical inference hypothesis unverified. No gold, matched evaluation, or paper-level novelty evidence was added. See [Phase276 briefing](../report/project_review_2026-10-29-current.md).

Phase275 reviewed the Phase1 exploration outputs and legacy methods. Phase272 supports complete closure of 110,425 heads from 85 basis atoms and a selected/minimum witness depth ≥301 for 69,052 heads (62.53%; max 396), strictly as properties of the pinned positive-Horn graph. The 49,435 cycle count has no preserved detector; the old binned log-log regression is not a power-law test; the undirected pairwise projection clustering result does not establish small-world structure or semantic communities. Legacy scripts now use project configuration/relative outputs, but their metrics remain exploratory. The five historical charts show IDs and are not rights-cleared. See [Phase275 report](../report/research_progress_deep_review_2026-10-12_phase278.md).

Phase274 rescanned the current output surface: 212 files, 22 text-key hits, 41 identity/provenance-key hits, and 53 Git-ignored files. The four unignored text-key hits were shape-checked as integer metadata counts or an algorithm description. Phase275 manually reviewed the seven non-JSON artifacts; source/sense identifiers remain visible in two figures, and path fixes do not validate the scripts' exploratory methods. This is not per-file legal clearance; `release_clearance` remains `not_cleared_for_public_release`. The inventory is a local ignored artifact at `sources/output_release_surface_audit_2026-10-08_phase274.json`. See Phase274 report and [Phase275 report](../report/research_progress_deep_review_2026-10-12_phase278.md).

Phase273 reconciled a stale pending status for the Findings ACL 2026 APF paper in the 2026-10-05 candidate snapshot; the 2026-10-06 screening log had already retained and targeted-screened it as adjacent prior art. This phase adds a supplemental record of ranking-validation details and evaluation limits, not a new candidate or unique paper. APF narrows broad NL→executable-formalization claims but does not establish or disprove the project's sense-bound gloss-span→typed-Horn research hypothesis. No project experiment or model was run. See the Phase273 report, [prior screen](sources/literature_screening_log_2026-10-06_acl_formalization_2026.json), and [supplemental record](sources/literature_screening_log_2026-10-08_apf_findings_acl2026_phase273.json).

Phase272 reran the complete frozen hypergraph and minimum-depth witness audits into fresh outputs. Both JSON files are byte-identical to Phase213; the pinned integrity lock, closure, all 110,425 witnesses, and minimum-depth certificates pass. Selected-witness descendants overestimate exact non-seed AND/OR closure loss in 66/85 basis deletions, match in 19/85, and never underestimate. This reinforces that deletion analysis must recompute full closure. The replay supports structural reproducibility for the pinned bundle, not gloss semantic support, licensing, NLI performance, or research effects. See [Phase272 report](../report/research_progress_deep_review_2026-10-12_phase278.md), [machine record](sources/frozen_graph_witness_replay_2026-10-08_phase272.json), and [outputs](outputs/phase272/).

Phase271 reran the synthetic gloss→OEWN bridge with validator 0.3: one resource query replayed, the two-row bridge passed, and the three success reports matched byte-for-byte in an independent repeat. Bad manifest pin, a missing unresolved candidate, and a query triple mismatch with matching report pins failed closed. The v3 input preflight still has 0 returns, no signed protocol, no external registration, and no distribution authorization. These runs establish synthetic software wiring only; no real gloss support, human gold, model result, or Track A effect was measured. See Phase271 report, [machine audit](sources/phase271_bridge_replay_audit_2026-10-08.json), and [outputs](outputs/phase271/).

Phase270 full-text screened ProofRank and clarified that formal correctness/replay and witness structure do not establish evidence-chain usability or explanation quality. The title appears in NeurIPS 2026 official Downloads/Poster pages, while arXiv v2 says accepted at the ICML 2026 AI for Math workshop; the relationship/track is unresolved. The refreshed index contains 2,058 records across 147 logs and 1,939 conservative clusters; the matrix crosswalk has 315 links / 300 targets, with 292 matched targets and 0 unmatched scholarly-reference candidates. These are traceability counts, not systematic-review coverage. No paper result was reproduced. See Phase270 report, [screening log](sources/literature_screening_log_2026-10-08_proofrank_phase270.json), [audit](sources/phase270_proofrank_research_update_audit_2026-10-08.json), and [outputs](outputs/phase270/).

Phase269 upgraded the existing ACL Findings 2026 validity/plausibility paper from abstract-only to official full-text screening. The paper's 1,280 syllogisms use ten taxonomic term triples; its hypernym control reuses those triples, so this is a content-effect diagnostic neighbor rather than WordNet gloss-span gold or a lexical generalization baseline. The refreshed index contains 2,057 records across 146 logs and 1,938 conservative clusters; 135 records are full-text screened. The current matrix crosswalk has 314 link occurrences / 299 targets, 291 matched targets, and 0 unmatched scholarly-reference candidates. These are traceability counts, not systematic-review coverage. No paper result was reproduced. See Phase269 report, [screening log](sources/literature_screening_log_2026-10-08_validity_plausibility_fulltext_phase269.json), [audit](sources/phase269_validity_plausibility_fulltext_audit_2026-10-08.json), and [outputs](outputs/phase269/).

Phase268 confirmed that the legacy claim-review `/0.1` contract cannot represent Track A's separate raw-gloss/rendered-premise hashes and spans, edge-surface-condition identity, and independent panel provenance. Track A v1 remains a draft; no schema, candidate, labels, or splits were created. See Phase268 report and [compatibility audit](sources/track_a_contract_compatibility_audit_2026-10-08_phase268.json).

Phase265 upgraded the already-recorded ACL 2026 CoPE paper to a targeted full-text review. Its authors note that plan validity can fail to expose an unfaithful natural-language-to-formal encoding, so this project must keep gloss-span support, typed logic/proof replay, and downstream query utility as distinct outcomes. This was a depth upgrade, not a new paper inclusion. The current index has 2,055 records / 1,937 conservative clusters across 144 logs. The matrix has 313 external-link occurrences / 298 targets; 303 occurrences and 290 targets match structured logs, with 8 unmatched non-paper resources and 0 unmatched scholarly references. These are bibliography traceability statistics, not systematic-search coverage or novelty evidence. See Phase265 report, [screening addendum](sources/literature_screening_log_2026-10-08_acllong2026_cope_fulltext_phase265.json), [audit record](sources/phase265_research_update_audit_2026-10-08.json), and [derived outputs](outputs/phase265/).

Phase264 added a targeted full-text screen of Hammerla & Mehler (NALOMA 2026). The paper's “provenance” is human-versus-LLM/model attribution, distinct from this project's external source lineage, gloss-span semantic support, and proof-witness provenance. Human-human agreement is reported at κ=.68; LLM-human agreement is κ=.37/.38, and the authors treat automated labels as weak proxies. After adding one log, the current index contains 2,054 records / 1,937 conservative clusters across 143 logs. The updated matrix contains 313 link occurrences / 298 distinct targets; 290 targets and 303 occurrences match logs, with 8 unmatched non-paper resources and 0 unmatched scholarly references. These are bibliographic traceability counts, not systematic-review coverage or novelty evidence. See Phase264 report, [screening log](sources/literature_screening_log_2026-10-08_naloma2026_negation_traces_phase264.json), [audit record](sources/phase264_research_update_audit_2026-10-08.json), and [derived outputs](outputs/phase264/).

Phase263 rebuilt the Phase250–252 literature dedup snapshots using the current CLI and the retained 137/138-log input sets. Historical summaries and cluster assignments match; full JSON differs only in the implementation hash and current extraction of DOI `10.1145/3770855.3817808` into P00200 (cluster and record fields). The old producer source is still missing, so this is a current-version reconstruction, not a recovery of that exact script. See Phase263 report, [machine comparison](sources/literature_log_legacy_output_replay_2026-10-08_phase263.json), and [reconstructed indexes](outputs/phase263/).

Current matrix crosswalk (Phase262) found 312 external-link occurrences / 297 unique targets: 302 occurrences and 289 targets match structured screening logs; the 8 unmatched targets are non-paper resources (5 project/code resources and 3 official WordNet documentation/data URLs), leaving 0 unmatched scholarly-reference candidates. This is bibliography traceability only, not systematic-search coverage. The current Phase256 literature dedup index replayed byte-for-byte from 142 logs. Phase250–252 outputs record an earlier implementation hash whose source script is absent from this uncommitted workspace; their historical replay claims remain documented, but exact producer reconstruction is not possible here. See Phase262 report, [crosswalk output](outputs/phase262/closest_work_log_crosswalk.json), and [source record](sources/closest_work_current_matrix_crosswalk_2026-10-08_phase262.json).

863 untracked, non-ignored paths / 271,109,408 bytes at capture, versus 812 / 240,093,564 bytes in Phase247. There are 805 unchanged hashes, 7 changed paths, 51 new paths, and no baseline paths missing. New paths remain unreviewed; 25 files matched a narrow restricted-context keyword screen, which is not a privacy, rights, or publication-clearance audit. No staging or commit occurred. See Phase261 report and [machine inventory](sources/repository_current_snapshot_inventory_2026-10-08_phase261.json).

Phase260 found the generic compiled LFToolkit JAR but not the complete WN30-lfs producer bundle. The JAR requires parse-tree XML and separate transformation rules; WN30-lfs's published archive only contains final XML, and the paper also names Charniak parsing and WordNet GlossTag sense assignment. The local host has no Java runtime, so the JAR was inventoried but not run. No full rerun or missing-ID cause is established. LFToolkit's documented partial processing may emit LF with incorrectly linked variables; therefore WN30-lfs `partial/complete` counts cannot substitute for semantic correctness labels absent a documented resource-specific mapping. See Phase260 report and [machine record](sources/wn30_lfs_producer_reproducibility_2026-10-08_phase260.json).

Phase259 verified the WN30-lfs source and key boundary. The primary ILF-WN paper describes it as a WordNet 3.0 logical-form resource and shows lemma/POS/sense-number keys. The official archive contains one XML file with 104,357 entries, 104,321 unique keys, 36 repeated-key occurrences, and no entry-level synset-offset or WordNet-release attribute. Princeton documentation says WordNet sense numbers and offsets vary by release, whereas `sense_key` is the stable lookup form; WN30-lfs uses another key format. Therefore Phase257's exact-release crosswalk remains authoritative: 104,081/117,659 (88.4599%); 174 unresolved keys and 13,578 missing IDs remain unattributed individually. See Phase259 report and [schema audit](outputs/phase259/wn30_lfs_source_schema.json). Semantic validity and separate resource rights remain unverified.

Phase258 diagnosed the 174 WN30-lfs entries not resolved by Phase257's strict WordNet 3.0 key join. Normalized exact-gloss matching yields 23 unique same-lemma/POS candidates, 1 ambiguous same-lemma/POS case, 38 unique same-POS candidates with another lemma, 38 same-lemma/POS entries with no exact gloss match, and 74 entries with neither an exact lemma/POS nor gloss candidate. A wrong named-entity candidate demonstrates that even a unique exact gloss match must not be automatically promoted to an identity mapping. The strict coverage numerator remains 104,081/117,659 (88.4599%). A reproducible diagnostic CLI and output preserve all 174 keys, candidate offsets and normalization flags without storing gloss text; independent replay is byte-identical. No cause is established for the remaining keys, and LF fidelity remains untested. See Phase258 report, [CLI](src/analysis/audit_wn30_lfs_unmapped_entries.py), [output](outputs/phase258/wn30_lfs_unmapped_diagnostic.json), and [source record](sources/wn30_lfs_unmapped_entry_diagnostic_2026-10-08_phase258.json).

Phase257 completed a strict WordNet 3.0 identity crosswalk for WN30-lfs. WordNet's `index.sense` (206,941 rows; 117,659 unique `(POS, offset)` IDs) matches the four release data files exactly. WN30-lfs has 104,357 entries; 104,081 unique IDs map exactly (88.4599%), 13,578 are absent, 0 mapped IDs are outside the release, and 174 entry keys remain unresolved without fuzzy matching. The report also separates 102 entries beyond one-per-offset, 36 repeated exact keys, and 45 mixed `partial/complete` offset statuses. A reusable CLI and full missing-ID audit output were created; independent scratch replay was byte-identical. This establishes ID coverage only, not LF semantics, parse-failure causes, or WN30-lfs rights. See Phase257 report, [CLI](src/analysis/audit_wn30_lfs_synset_crosswalk.py), [output](outputs/phase257/wn30_lfs_synset_crosswalk.json), and [source record](sources/wn30_lfs_synset_crosswalk_2026-10-08_phase257.json).

Phase256 corrects the XWN evidence-depth statement in Phase255: targeted sections of the six-page author report were screened. The report's pilot and evidence focus on preprocessing/WSD, not a complete LF evaluation. The official Princeton WN30-lfs ZIP was retrieved and its XML parsed: 104,357 entries, all with gloss and LF; 52,743 `partial`, 51,614 `complete`, and 28,872 sub-LF elements across 13,565 entries. The 88.69% ratio to ILF-WN's cited 117,659-synset total is a count ratio only; no offset crosswalk validates coverage. The archive contains no README/license file, so redistribution rights remain unresolved. Published 2012/2015 XWN LF consistency audits report parser-defined disconnected-variable rates of 54.05% and 23.82% after automatic correction; the latter is evaluated using the same parser. They establish prior art for structural consistency checking/correction, not independent gloss-semantic fidelity. The Phase256 index has 2,053 records in 1,936 conservative clusters across 143 logs; the matrix crosswalk matches 288/294 distinct targets and all six unmatched targets are nonpaper resources. Both outputs replayed byte-for-byte and local Markdown link audit found zero issues. The remaining source-span→directional typed rule→independent source-bound replay contribution is still an unvalidated hypothesis: no adjudicated gold, matched baseline, project effect, or LFToolkit reproduction exists. See Phase256 report, [machine log](sources/literature_screening_log_2026-10-08_phase256_xwn_wn30_resource_reaudit.json), and [updated closest-work matrix](docs/closest_work_comparison.md).

Phase255's literature index and crosswalk remain historical artifacts: 141 logs, 2,050 records, 1,934 conservative clusters, 286/291 matrix targets matched, and byte-identical replay. See Phase255 report and [machine outputs](outputs/phase255/).

Latest related-work screen: Phase254 deep review, [structured log](sources/literature_screening_log_2026-10-08_phase254_direct_prior_art.json), and [closest-work matrix](docs/closest_work_comparison.md). A major direct historical collision is now documented: Moldovan & Rus (FLAIRS 2001) already transform WordNet glosses into sense-tagged logic forms with argument structure and AND/OR encodings and demonstrate QA use. Their 81% result is coverage on 400 manually prepared LFTs, not semantic accuracy. The ACL 2001 companion is abstract/metadata-only pending version comparison. Claims of first WordNet gloss logicization, AND/OR representation, or QA use are withdrawn. Static inspection shows the current `compile_annotations` path starts from human-supported structured claims and produces restricted Horn/Datalog rules with provenance; it does not parse raw English glosses, and proof checking does not establish gloss fidelity ([architecture record](sources/current_logic_pipeline_prior_art_boundary_phase254.json)). WSL 2024 and homonymy 2024 are recorded as upstream span/sense and coarse-granularity neighbors. Any remaining source-span support / typed rule / replayable witness novelty is an unvalidated hypothesis; no semantic gold, matched 2001 baseline, paper-level effect, release clearance, or AAAI 2027 authorship boundary change is established.

Latest related-work screen: Phase253 report, [structured full-text addendum](sources/literature_screening_log_2026-10-08_phase253_fulltext_addendum.json), and [updated closest-work matrix](docs/closest_work_comparison.md). Phase253 full-text screened TROVE, Gulbe et al., Word Ladders, FOL-Traces, and WordNetGraph. It corrected the Word Ladders record URL and narrowed novelty claims around gloss-derived WordNet links, definition graphs for interpretable entailment, fine-grained sentence provenance, and verified FOL traces. Current matrix-to-log crosswalk matches 280/285 distinct external targets; the five unmatched targets are project/code resources, and no scholarly references remain unmatched. This is traceability, not evidence of search completeness or semantic novelty. The narrow gloss-span→typed Horn support and source-bound proof replay hypothesis remains unvalidated; no gold, matched baseline, or paper-level result exists.

Latest closest-work traceability audit: Phase253 report, [crosswalk CLI](src/analysis/audit_closest_work_log_crosswalk.py), and [machine result](outputs/phase253/closest_work_log_crosswalk.json). Of 285 distinct external targets in matrix table rows, 280 match structured screening logs; no scholarly citation remains unmatched, and 5 code/project resources remain unmatched. This is log traceability only, not literature coverage.

Latest cross-log literature audit: Phase250 report, [deduplication CLI](src/analysis/audit_literature_log_deduplication.py), and [machine index](outputs/phase250/literature_log_dedup_index.json). It links 2,036 titled records across 137 targeted-screen logs into 1,923 conservative clusters; this does not define an exhaustive candidate denominator or establish a systematic review.

Latest related-work update: Phase249 report and [screening log](sources/literature_screening_log_2026-10-08_satquest_acl2026_phase249.json). ACL 2026 SATQuest narrows generic verifier-backed logical-evaluation novelty; its propositional CNF tasks do not supply WordNet gloss-span semantic support labels or source-bound proof witnesses.

Latest sensitive-path screen: Phase248 report and [machine record](sources/repository_sensitive_path_review_2026-10-08_phase248.json). The 58 flagged paths have no detected personal-path, email, or credential-assignment patterns. Twenty-one internal AAAI-boundary references remain internal-only; the referenced annotation answer key is ignored by Git. This is not publication clearance.

Latest initial-snapshot review: Phase247 report and [machine record](sources/repository_initial_snapshot_review_2026-10-08_phase247.json). Every one of the 812 then-untracked candidate paths has a recorded size/hash and a proposed handling class. Content review and publication allowlist approval remain incomplete; no staging or commit occurred.

Latest deterministic replay: Phase246 report and [machine record](sources/track_a_genus_resource_replay_2026-10-08_phase246.json). The Phase245 genus resource-alignment JSON was reproduced byte-for-byte at a separate scratch path on the current host. Cross-environment reproduction and semantic validation remain open. Git still has no tracked baseline; a publication allowlist is needed before creating the initial snapshot.

Latest Track A preparation diagnostic: Phase245 report and [machine record](sources/track_a_genus_resource_diagnostic_2026-10-08_phase245.json). The 252 noun targets in the mixed-POS locked v3 frame have 98.0% candidate coverage; same-release direct-hypernym resource pair P/R/F1 are 10.7%/36.7%/16.5%. This is a resource-alignment proxy, not gloss semantic gold or a model result. Track A protocol decisions and authorization remain pending.

Latest full source-payload rehash: Phase244 report and [machine record](sources/source_payload_full_rehash_2026-10-08_phase244.json). All 115,235 unique payloads referenced by the frozen sense index match checksums over 18.73 GB; the aggregate report is byte-identical to Phase210. This is byte-integrity evidence only, not source authenticity, semantic support, or release clearance; release clearance remains not assessed.

Latest frozen graph current replay: Phase243 report and [machine record](sources/frozen_graph_witness_replay_2026-10-08_phase243.json). The current bundle's graph and minimum-depth witness reports match saved Phase213 artifacts byte-for-byte; the replay-exception consistency report matches Phase224 byte-for-byte. This supports pinned-bundle structural reproducibility only; the Phase243 exception audit did not open source payloads or establish semantic support, rights clearance, or NLI/model results.

Latest clean-environment and snapshot audit: Phase242 report and [machine record](sources/git_initial_snapshot_inventory_2026-10-08_phase242.json). The initial Git snapshot candidate set contains 800 untracked files/240,040,154 bytes and needs content-reviewed per-path selection. The current host's configured external bundle/core graph files exist; source imports are statically standard-library/local only and CI is configured, but no CI/tests or payload integrity replay ran.

Latest repository-readiness audit: Phase241 report and [machine record](sources/repository_baseline_hygiene_audit_2026-10-08_phase241.json). The Git repository currently has no commits or tracked files; root `tmp/` contains 337 files (392,751,359 bytes), including external archives. Local index/cache/temp paths are now ignored, but no initial snapshot was created and this is not release clearance.

Latest related-work screen: Phase240 report and [machine log](sources/literature_screening_log_2026-10-08_neurips2025_independent_proof_checking_phase240.json). APTP, a NeurIPS 2025 independent checker for DNN branch-and-bound UNSAT proof trees, narrows broad novelty claims around producer/checker separation and replayable proof artifacts. Its proof object differs from this project's source-only AND/OR Horn witness and provides no gloss-span semantic support. Phase239's ICLR 2026 HiCEM screen remains in the history below. Targeted screens only, not proceedings censuses or novelty proofs.

Latest proof/NLI interface audit: Phase238 report and [machine record](sources/track_a_proof_nli_export_join_audit_2026-10-08_phase238.json). Current code composes a single-sense proof/NLI route with certificate replay, adjudicated claim binding, premise/hypothesis hash matching, optional frozen-payload verification, pinned NLI exports, and test-gold removal. The Track A relation-edge/surface/condition join remains incomplete: candidate contracts lack annotation claim foreign keys, while the exporter aliases `candidate_id` as `claim_id`. This corrects Phase235's too-broad statement that no proof/NLI join exists. Static audit only; no tests or schema changes.

Latest deletion-unit comparison: Phase231 report, [CLI](src/analysis/basis_single_payload_deletion_audit.py), and [machine result](outputs/phase231/basis_single_payload_deletion_audit.json).

Latest executable-route verification: Phase233 report. Seven targeted test modules passed (72 tests) after two stale annotation compiler-version assertions were updated from v5 to the current backward-compatible v6. This is synthetic/unit regression evidence; the goal remains active with no real gloss-span gold, matched research effect estimate, source clearance, or paper-level novelty evidence.

Latest identity-interface audit: Phase234 report, [field crosswalk](docs/track_a_identity_field_crosswalk.md), and [machine record](sources/track_a_identity_field_crosswalk_2026-10-08_phase234.json). The upstream OEWN inventory has release-bound edge IDs; those IDs and parent-surface/renderer identity are not carried into current claim-review/NLI/proof contracts. No Track A schema was migrated.

Latest call-flow audit: Phase235 report and [machine record](sources/track_a_candidate_flow_audit_2026-10-08_phase235.json). CodeGraph confirms that the release identity audit, hypernym inventory, and claim-review/NLI exporter remain separate paths; current inventory callers are audit/workload CLIs, and the exporter does not consume relation-edge inventory. No end-to-end edge→surface→condition→proof/NLI join exists in the indexed Python flow. No runtime code or schema changed.

Latest design-consistency audit: Phase236 report and [machine record](sources/track_a_estimand_consistency_audit_2026-10-08_phase236.json). It reconciles the NLI condition-difference estimand in the v1 draft with Phase153: target-sense-equal is recommended for NLI, edge-population weighting remains a sensitivity, while source-support remains edge-population weighted. This is a draft recommendation only; the protocol remains unapproved.

Latest literature reconciliation: Phase237 report and [dedup log](sources/literature_screening_log_2026-10-08_lrec2026_wordnet_hyperbolic_phase237.json). It corrects a false new-discovery classification: the LREC 2026 paper was already full-text screened on 2026-10-05; this pass only adds that existing evidence to the closest-work matrix and rechecks official metadata. No new inclusion or candidate denominator change. Broader literature review remains targeted and incomplete.

The goal remains active. Phase231 compares deleting one of 166 basis source-record payloads under permissive (“any source remains”) and strict (“all listed sources required”) clause-retention policies with seed-only deletion. Both policies produce exactly the same loss sets across every head×scenario; 22 scenarios have nonzero loss, with a maximum of 109,343 heads, and 24 direct closure checks plus a byte-identical replay pass. This is a sensitivity result under explicit bookkeeping policies, not validated producer semantics or upstream WordNet document deletion. Phase230 had already established the same equality for 3,570 whole-bundle pair interventions. Phase229 adds a deterministic basis source-lineage CLI: 85/85 basis identities match nodes and sense index, and 166/166 source payloads pass sidecar size, SHA-256, and sense-identity checks; an independent output-path replay is byte-identical. It also confirms all 154,206 graph clauses have an active source-index row (154,356 source-document×clause links). This establishes identity and byte lineage only, not gloss support, licensing, or source-deletion semantics. Phase228 literature screening confirms established pair/multi-component importance and interaction work in reliability engineering and fault-tree analysis; pairwise interaction itself is not a defensible novelty claim. Formally, Phase227's 21,878 joint-only pair×head losses equal size-2 inclusion-minimal deletion cut-set associations for head reachability in the pinned graph; 1,102/3,570 pairs contain at least one such head. These are not source-redundancy or semantic-effect estimates. Phase226 documents that OEWN resource-path replay and single-sense proof/NLI routing are separate evidence paths without a relation-edge join contract. Phase225's targeted NeurIPS supplement narrowed broad novelty claims. Phase219's Track A v1 study design remains unconfirmed and generated no pairs, labels, or schema. Existing evidence supports reproducible structural audits of the pinned AND/OR Horn bundle, provenance coverage across minimum-depth alternatives, and auditable single-sense proof/NLI routing under stated assumptions. There is still no authorized gloss-span semantic gold, matched research effect estimate, release clearance, or paper-level novelty evidence. The goal remains active.
The goal remains active. Phase232 adds an accepted NeurIPS 2026 neighbor, LogicTree-RAG, which combines hierarchical logic-tree generation, source evidence spans, node-level evidence-support evaluation, and human audit. General claims about these components are now clearly prior art; only the sense-specific WordNet gloss→typed AND/OR Horn support and proof-replay task distinction remains as an untested hypothesis. Phase231 compares deleting one of 166 basis source-record payloads under permissive (“any source remains”) and strict (“all listed sources required”) clause-retention policies with seed-only deletion. Both policies produce exactly the same loss sets across every head×scenario; 22 scenarios have nonzero loss, with a maximum of 109,343 heads, and 24 direct closure checks plus a byte-identical replay pass. This is a sensitivity result under explicit bookkeeping policies, not validated producer semantics or upstream WordNet document deletion. Phase230 had already established the same equality for 3,570 whole-bundle pair interventions. Phase229 adds a deterministic basis source-lineage CLI: 85/85 basis identities match nodes and sense index, and 166/166 source payloads pass sidecar size, SHA-256, and sense-identity checks; an independent output-path replay is byte-identical. It also confirms all 154,206 graph clauses have an active source-index row (154,356 source-document×clause links). This establishes identity and byte lineage only, not gloss support, licensing, or source-deletion semantics. Phase228 literature screening confirms established pair/multi-component importance and interaction work in reliability engineering and fault-tree analysis; pairwise interaction itself is not a defensible novelty claim. Formally, Phase227's 21,878 joint-only pair×head losses equal size-2 inclusion-minimal deletion cut-set associations for head reachability in the pinned graph; 1,102/3,570 pairs contain at least one such head. These are not source-redundancy or semantic-effect estimates. Phase226 documents that OEWN resource-path replay and single-sense proof/NLI routing are separate evidence paths without a relation-edge join contract. Phase225's targeted NeurIPS supplement narrowed broad novelty claims. Phase219's Track A v1 study design remains unconfirmed and generated no pairs, labels, or schema. Existing evidence supports reproducible structural audits of the pinned AND/OR Horn bundle, provenance coverage across minimum-depth alternatives, and auditable single-sense proof/NLI routing under stated assumptions. There is still no authorized gloss-span semantic gold, matched research effect estimate, release clearance, or paper-level novelty evidence. The goal remains active.

Latest basis lineage audit: Phase229 report, [CLI](src/analysis/basis_source_lineage_audit.py), and [machine result](outputs/phase229/basis_source_lineage_audit.json). Latest novelty-boundary update: Phase228 report and [screening log](sources/literature_screening_log_2026-10-08_reliability_interactions_phase228.json). Latest structural sensitivity analysis: Phase227 report, [method](docs/pairwise_basis_deletion_interactions.md), and [machine result](outputs/phase227/pairwise_basis_deletion_interactions.json). Latest evidence-interface audit: Phase226 report and [machine record](sources/evidence_layer_interface_audit_2026-10-08_phase226.json). Latest design draft: [Phase219 Track A v1 protocol](docs/track_a_protocol_v1_draft.md), deep review, and [machine record](sources/track_a_protocol_design_review_2026-10-08_phase219.json). Latest launchability audit: Phase218 report and [machine record](sources/annotation_and_track_a_launch_readiness_audit_2026-10-08_phase218.json). Latest literature supplement: Phase225 report and [machine screening log](sources/literature_screening_log_2026-10-08_neurips2026_autoformalization_and_proof_graph_phase225.json). Latest provenance replay: Phase216 report, [machine record](sources/minimum_depth_alternative_source_map_2026-10-08_phase216.json), and [source map](outputs/phase216/minimum_depth_alternative_source_map.jsonl).

---

## Phase 230：冻结 sense payload-bundle deletion 对照

在 3,570 个 pair scenarios 上比较 seed-only deletion 与删除整个 basis sense payload bundle（撤回 seed，并禁用该 head 的全部规则）。loss sets 全部相同；seed-only 场景中 7,140 个被删除 head/pair incidence 均未重新推出。所有行与 Phase227 对账、4 个直接 closure 核对和独立路径确定性复跑通过。该结论限于冻结 package payload，不表示 upstream source-document deletion。见Phase230报告、[实现](src/analysis/basis_payload_bundle_deletion_audit.py)、[输出](outputs/phase230/basis_payload_bundle_deletion_audit.json)及[机器记录](sources/basis_payload_bundle_deletion_audit_2026-10-08_phase230.json)。

## Phase 229：basis 来源身份链复算

新增只读 CLI 对 85 个 basis ID、166 个 source payload 与 checksum/identity 做逐项核验，另确认 154,206 个 graph clauses 都有有效 active-source index row、154,356 条 source-document×clause links；双路径复算字节一致。此证据补齐来源 identity/byte lineage，但不证明 gloss 语义支持、许可或 source deletion semantics。详见Phase229报告、[实现](src/analysis/basis_source_lineage_audit.py)和[机器结果](outputs/phase229/basis_source_lineage_audit.json)。

## Phase 228：可靠性/故障树交互先例审计

定向摘要筛读发现 pair/multi-component JRI/JFI、gate-event joint importance、minimal cut-set importance 与 joint structural importance 先例。因此 pairwise interaction 本身不是可靠的新颖性主张；Phase227 仅是冻结图上的确定性 closure-loss 观察。未做公式级匹配比较、模型或测试。见Phase228报告和[机器日志](sources/literature_screening_log_2026-10-08_reliability_interactions_phase228.json)。

2026-10-08 Phase 182 current status：COLM 2026 Goedel-Code-Prover 全文核读并确认层次化 proof decomposition、constructive reconstruction 和 Lean-kernel checked proof 属于近期方法先例；任务从已形式化 Lean 规格开始，未覆盖自然语言→规则或 gloss-span support。单篇筛读，未跑项目代码/模型/语义实验；没有新增效果或新颖性证据。见Phase182报告与[结构化日志](sources/literature_screening_log_2026-10-08_colm2026_hierarchical_code_proof.json)。

2026-10-08 Phase 181 current status：已增加可重跑的只读开发环境审计命令，当前 133 个维护 Python 文件 AST 解析无错误、未发现静态第三方导入，CI 矩阵被记录为静态配置；configured bundle 和 manifest 存在。`verify_data_release_inventory` 当前一致、OEWN 本地 archive hashes/CRC 与 bundle manifest 计数匹配，但项目仍 `not_cleared_for_public_release`。本阶段未运行测试、CI、模型或语义实验；完整数据 integrity/source-record payload replay 需独立检查。见Phase181报告与[机器快照](sources/reproducibility_environment_audit_current.json)。

2026-10-08 Phase 180 literature status：EMNLP 2026 官方 accepted-main-papers 页在 2026-10-08 尚无可见 paper-level 题录，会议日期为 10-24 至 10-29；related-work coverage 保持 pending，待公开题录/proceedings 后重筛，不据搜索未命中声称缺少相关工作。详见Phase180报告。

2026-10-08 Phase 179 current status：Phase175 的 witness descendants 比较曾把含被删根节点的精确 closure loss 与不含起点的 descendants 混算。逐 basis 复核后统一排除根：66/85 高估、19/85 相等、0/85 低估；85 个 basis 删除均未重推出 seed。新增逐集合审计确认 0 个精确非根损失节点落在 descendants 之外，跨删除场景累计 98,573 个 descendant 场景-节点项仍可由完整 closure 推出。Phase6 和 Phase175 冻结超图输出已重算，bundle lock、manifest/checksum、closure、hyperedge/rule、nodes/head 和 110,425 条 selected witness 结构检查全部通过。差异来自未选 OR 替代推导造成的高估；删除影响仍须 AND/OR closure 重算。只支持固定正 Horn 图内结构结论，不证明 gloss entailment 或全局最小 basis。更新代码和报告；未运行测试、模型、语义实验或标注。见Phase179报告与Phase175报告。

2026-10-08 Phase 174 current status：官方 ACL Findings 2026 全文筛读 LSEG，登记 NL2FOL 推理时隐藏状态纠偏和公式等价评测先例；明确不能外推为 WordNet gloss-span 支持，且不是 matched baseline。固定 ACL v6 denominator 不变；单篇 out-of-frame review，不是系统综述或新颖性证明。无项目代码/schema/data 修改；未跑测试/模型/实验/标注。详见Phase174报告。

2026-10-08 Phase 173 current status：PMC 官方说明 OA Subset 的许可按文章变化，且需检查嵌入内容及获取渠道边界。当前两个候选 payload 未绑定文章身份或许可条款，rights log 只登记来源族规则；总 `release_clearance` 仍为 `not_assessed`。rights log 18 个标签，exact-label 命中 25/90 profiles、2,348/3,595 计数。无代码/schema/bundle/data 修改；未跑测试、模型、实验或标注。详见Phase173报告。

2026-10-08 Phase 172 current status：补记 Glottolog 5.3 官方下载与 CC BY 4.0 声明；本地 3 个 candidate payload 的版本字段缺失，未绑定发行文件或哈希。rights log 17 个标签，exact-label 命中为 23/90 profiles、2,346/3,595 profile-payload 计数；总体 `release_clearance` 仍为 `not_assessed`。无代码/schema/bundle/data 修改；未跑测试、模型、实验或标注。详见Phase172报告。

2026-10-08 Phase 171 current status：以当前 rights log 和冻结 bundle 重算来源 crosswalk 与六条 OEWN graph lineage。精确标签命中维持 22/90 profiles（输入 evidence 有更新）；6/6 payload identity 与 11/11 clause-hyperedge 对齐成立，但只有 2/6 selected witness 文档同时含精确候选路径和匹配 OEWN ILI/hash。结构证据不代表 source semantics 或许可通过。无代码/schema/data 修改，未跑测试/模型/标注。详见Phase171报告。

2026-10-08 Phase 170 current status：新增两篇官方全文定向筛读（CoNLL 2026 main、NALOMA 2026 workshop），分别约束 verifier reliability/operation-aware evaluation 与 semantics-aware formula metrics 的解释范围；本项目 source-span support 仍需独立人工 gold。无代码、schema 或数据变更；未跑模型、实验、测试或标注。见Phase170报告。

2026-10-08 Phase 169 current status：CodeGraph 索引已初始化且最新。区分既有 400 项 preregistration 输入锁与拟议的 Track A relation-edge/surface + exact-condition NLI study；前者仅保证字节/结构预检，不能视作后者的协议批准或分发授权。建议先解决精确来源使用权及协议选择，再另建候选框/manifest。Markdown 链接审计 0 问题；未改代码/schema/data，未运行测试/模型/标注。详见Phase169报告。

2026-10-08 Phase 168 current status：全局文本审计未发现把匿名 AAAI 2027 稿件成果归给用户；将旧报告的“用户提供”改成“工作区中的匿名第三方稿件”，并把 ACL/AAAI 2026 先例更新到 prior-work 定位备忘录。没有打开或复制受限 PDF；没有独立核验作者、投稿状态或许可。详见Phase168报告。

2026-10-08 Phase 167 current status：对 AAAI 2026 官方论文集作四篇定向全文筛读，三篇主技术轨、一篇 AI for Social Impact special track。新增本体抽取 vs. 固定 signature 下公式转换、SMT 等价与逻辑扰动评测、selective translation/backward reasoning、数学 autoformalization、法条到 Prolog 执行/拒答等近邻；这些宽泛方法不能作为独立创新。仍需直接建立 gloss-span→typed Horn 支持 gold 与 source-only proof replay 的 matched evaluation。此轮不越过 Track A 决策 gate，未改代码/数据、未运行测试或实验。见Phase167报告与[筛读日志](sources/literature_screening_log_2026-10-08_aaai2026_formal_logic_neighbors.json)。

2026-10-08 Phase 166 current status：对 ACL v6 的 2026 `wordnet_gloss_lexical_relations` 九篇候选切片做筛读升级，先前 5 篇全文/4 篇摘要更新为 5 篇全文、2 篇定向章节、2 篇摘要；原始 v6 不覆盖，另输出 exact-URL reconciliation。发现 LREC 2026 已有 WordNet hypernym + gloss-conditioned contextual WSD，以及 LLM WordNet gloss-to-sense label transfer；后一工作无人工 spot-check，不能以 downstream F1 代替 direct semantic gold。目标中的 gloss-span→directional typed Horn support + source-only replay 仍未证实。单 reviewer slice，不是系统综述；无项目代码/数据/测试/实验改动。见Phase166报告、[筛读日志](sources/literature_screening_log_2026-10-08_acl2026_wordnet_slice_phase166.json)和[深度快照](sources/acl_anthology_candidates_2026-10-08_v6_reconciled_phase166.json)。

2026-10-08 Phase 165 current status：定向核读 ICLR 2026 主会 Mathesis、DExploration、SCI-Verifier 与 Variation in Verification 四篇官方论文。NL→formal semantic assessment、proof-dependency DAG/topological traversal、专家标注 answer verifier benchmark 与 generator/difficulty-conditioned verification 均已有近期主会先例；项目差异仍仅是 sense/release-bound gloss-span→directional typed AND/OR Horn source support + source-only replay 假设，未有 gold/matched baseline/效果证据。本轮未改代码/数据、未跑测试/实验；单 reviewer targeted screen，不是 ICLR 全量综述。详情见Phase165报告和[结构化日志](sources/literature_screening_log_2026-10-08_iclr2026_formalization_verification.json)。
2026-10-08 Phase 164 current status：补查官方 ICML 2026 PMLR 306（2026-09-29 发布）与 NeurIPS 2025/ICML 2025 相关工作，筛选 7 篇、其中 2 篇定向全文、5 篇摘要级；去重保留既有文献条目，未新增项目代码或实验结果。方法边界进一步确认：proof repair、learned/weakly aggregated verifiers、rule-grounded benchmark 与 formal-versus-plausibility 均已有先例；sense-bound WordNet gloss-span→typed AND/OR Horn support 与 source-only replay 仍无本项目 gold/matched evidence。不是 proceedings 全量筛查或系统综述；APOLLO 书目作者字段冲突待核。详见Phase164报告和[结构化日志](sources/literature_screening_log_2026-10-08_icml2026_neurips2025_formal_verification.json)。

2026-10-08 Phase 163 current status：当前配置 bundle 中 sense index 引用的 115,235 个唯一来源 payload（18,734,636,389 bytes）已逐个解析并与 checksums.jsonl 的 byte count/SHA-256 匹配；畸形索引记录和重复路径均为 0。当前聚合输出 SHA-256 与留存 Phase23 结果完全一致（9ff9ea44209fdb27e7967123ed9570f5a95ca236d6fc147ae955aa34f4d6dc2d）。这只证明被 sense index 引用的 payload 与本地冻结 checksum 相符；source-level rights 仍为 not_assessed，不证明上游真实性或 gloss/图规则语义。Phase162 六个 bundle lock 文件也均匹配；CodeGraph 索引最新。详见Phase163报告和[当前机器结果](outputs/phase163/source_release_metadata_audit_current.json)。

2026-10-08 Phase 160 current status：pipeline `/13` 现在对 invalid typed program 提供 `unknown / invalid_typed_program` 原因，并在 strict route 暴露从 replay program 重算的 type-validation 报告；这是可审计性改进，不是语义有效性或 soundness 新证据。Phase 159 最新定向筛读显示近期形式验证/NLI 先例仍未提供 WordNet gloss-span→typed-Horn matched gold。0.7 仍是静态实验路径，Track A 设计、授权标注与真实 gold 未完成。详情见Phase 160和Phase 159。

2026-10-08 Phase 156 进展：新增实验性 annotation schema 0.7 的显式 target variable 校验、compiler v6 多元正 Horn 受限投影与 agreement v13 对齐，更新方法/类型/proof/source-only 契约。仅通过 Python syntax compilation 和配置 JSON 解析；未运行测试、Datalog replay 或真实标注，故行为正确性与 gloss 语义有效性仍待验证。前序 Phase 58 文献筛查详见Phase 58；本轮具体边界见Phase 156。

# 研究就绪度与论文主张审计

**状态快照：2026-10-07（Phase 58）。** 本页把当前可查证的工程/结构产物与尚不能支撑论文主张的证据分开。它用于下一阶段排序，不是已完成的论文审稿、系统综述、法律意见或发表许可。

本快照的整体阶段判断见阶段性深度分析报告、Phase 32 深度分析及Phase 33 深度分析。Phase 28 增加 `route_pipeline_batch_from_export` 编排接口，但项目仍无真实 annotation returns、校准 NLI gold 或端到端匹配评测；新增 API 不改变下表的实证状态。Phase 32 完成固定 v3 中 2024 `definition_to_formal_logic` 词族日志覆盖，Phase 33 又对两篇 2026 formal NLI/proof-tree 候选作官方 PDF 定向筛读。当前全局 exact-URL 对账为 565/1,747，待题名/摘要筛查 1,182；深度计数为全文 56、定向章节 52、摘要/元数据 305、未明 152。详情见[Phase 33 日志](sources/literature_screening_log_2026-10-06_acl2026_proof_and_formal_nli.json)及[Phase 33 reconciliation](sources/acl_screening_reconciliation_2026-10-06_phase33.json)。

Phase 35 静态范围审计确认现有 compiler 仍是一元正 Horn/Datalog 原型；Phase 36 增补两篇 ICML 2026 摘要级跨会场背景工作，未改变 ACL v3 reconciliation 或实证缺口。详情见Phase 35与Phase 36。

工程与语义证据边界按当前实现进一步列在[Source-only 证据链契约](docs/source_only_evidence_contract.md)及Phase 34 静态审计报告：certificate replay、source payload hash/sense/gloss match 和 AST span coverage 各支持窄的结构/身份声明，不能替代人工 gloss-support gold、权利/归属审查或匹配实验。

Phase 39 重核发布 inventory 与本机 OEWN/frozen bundle 一致性，并确认 source-level release clearance 仍未评估、annotation protocol/distribution authorization 未满足；详见Phase 39。Phase 40 在 IJCAI 2026 官方 proceedings 中定向筛读两篇：VANESSA 已组合 textual entailment、符号推理和 proof tree；NRI 已展示 proposition-level DNF induction。它们降低宽泛 pipeline 与规则归纳 novelty claim 的可信度，但不是 glossary source-support baseline，也不改变无人工 gloss-support gold、无 matched evaluation、无发布授权的实证状态；详见Phase 40和[结构化日志](sources/literature_screening_log_2026-10-06_ijcai2026_logic_neighbors.json)。

Phase 41 静态复查确认 source-record verifier 已把 annotation path/hash 声明与冻结包锁、sense index、payload bytes/checksum 和精确 gloss 字段绑定；失败诊断日志早于当前测试文件修改，因此当前回归用例状态未知，本轮没有运行测试。该 verifier 仍不证明上游 release/许可、规则语义支持或人类裁决正确，详见Phase 41。Phase 42 对 IJCAI 2026 官方 proceedings 做了全目录标题级补筛，没有发现 VANESSA/NRI 之外显眼标题命中；这不构成全摘要/全文审查或新颖性证据，详见Phase 42及[筛查记录](sources/ijcai2026_title_screen_audit_2026-10-07.json)。

截至本次状态复核，`config/annotation_preregistration_v3_lock.json` 仍记为 `protocol_signed=false`、`external_preregistration_id=null`、`distribution_authorized=false`，标注回传文件为 0。这里只核对 lock 字段和回传文件名数量，没有运行 text-free preflight；blind task/answer key 继续限于本地内部使用，不能据此启动外部分发或正式标注。

Phase 43 更新了 GCIDE 0.54 与 MeSH 2026 的官方版本/复用条款页面证据，未完成 payload-to-release bytes 绑定、来源内容第三方材料审查或具体发布方案判断；不改变 `release_clearance=not_assessed`。详见Phase 43与[来源证据 JSON](sources/source_release_rights_evidence_2026-10-06.json)。

Phase 44 查明 NCI 专用 NCIt 条款页声明 CC BY 4.0，并记录商标限制与官方发布格式/版本信息。OLS 聚合记录仍未映射到精确 NCIt release、序列化和字节，故不改变 `release_clearance=not_assessed`。详见Phase 44。

Phase 45 定向核读 ACL 2026 RGCWM，确认通用规则依赖图、规则状态和结构传播已有强主会邻居，进一步收窄 novelty framing。该工作不提供 WordNet gloss-span semantic gold 或可重放的 source-only Horn proof；本项目剩余差异仍是假设，需系统检索和 matched gold 实验验证。详见Phase 45。

Phase 47 修正了评测协议中过时的 schema 描述：NLI 三分类已进入独立 `claim-review-record/0.1` sidecar，canonical annotation `0.4-draft` 仍存独立的 gloss-support 标签。字段合同现在与现有 schema/exporter 一致；仍无真实标签回传或标注授权，详见Phase 47。

Phase 48 对冻结 source-record 索引的 115,235 行作字段集合聚合，确认索引层没有显式 provider/release/version/format/license 字段。此结果不能外推到索引指向的 payload；OLS/NCIt 版本绑定与 `release_clearance` 仍未解决。详见Phase 48。

Phase 49 将主要研究假设明确为同一人工 source-support gold、隔离切分和相同预算下的风险—覆盖增量比较，并为结构保留和证据/回放辅助写出可证伪的次要假设。当前无 gold、无 matched 结果，所有假设仍未验证；数值判据需在合法 pilot 后、test 标签揭示前预注册。详见Phase 49与[评测协议](docs/claim_verification_evaluation_protocol.md#可证伪的研究假设与判据预注册前草案)。

Phase 50 把 Phase 24 的 90 个 aggregate source profiles 与权利证据日志按 source label 精确交叉；17 个 profile 组合、2,326 个 profile payload 计数有同标签日志项，73 个组合仍是字面未命中（其中可能包含别名）。此结果只是 crosswalk 可定位性，不是清权比例。Phase 23 的 payload 字段扫描和 Phase 48 的 index 字段扫描范围不同：payload 有来源/版本线索，索引本身仍无这些身份字段。具体 release/bytes 映射和兼容性未解决。详见Phase 50。

Phase 51 基于当前官方页面，为 OEWN 2025+、English Wiktionary 和 ChEBI 三个明确画像标签补入资源家族证据，crosswalk 变为 20/90 个 profile 组合、2,334/3,595 个跨 profile payload 计数可精确定位。页面级 terms 仍未绑定到候选 payload 的具体 bytes/entry/release；其他来源别名未审，不能解释为清权覆盖。详见Phase 51。

Phase 52 对 `local_go-basic.obo_snapshot` 和 `v5_local_snapshot` 补查 GO/IUPAC 官方版本与许可说明；更新 crosswalk 为 22/90 个画像组合、2,343/3,595 个 profile payload 计数精确匹配。具体 GO 日期 release、IUPAC term identity/revision 和 payload bytes 仍未绑定；清权状态不变。详见Phase 52。

Phase 54 对 Phase 24 最大的非规范来源画像簇做字段形状与 host 抽取，确认 1,202 条非规范 `source` 值均为字符串，受控 URL parser 未恢复 host；其中 1,079 个 profile payload 计数只有 hash-shaped version 且无 `download_url`。这不足以判断字符串内实际内容，故整体仍 unresolved；不对外分发或套用来源许可。详见Phase 54。

Phase 55 对 COLM 2026 官方 accepted-papers 列表中三篇近期方法邻居做定向全文筛读：组合式 claim falsification、logic-preserving difficulty search、以及 symbolic validity/semantic grounding 分轨。它们进一步限制了宽泛贡献表述，并提示需加入组合 hard negatives、语义保持压力测试及 verifier coverage/fallback 报告。筛读不改变 ACL v3 计数，也不构成 matched evaluation、新颖性判断或系统综述；项目依然没有可授权的 gloss-support gold 或匹配实验。详见Phase 55及[筛读日志](sources/literature_screening_log_2026-10-07_colm2026_compositional_verification.json)。

## 按研究目标核对

### 核心假设判定门

| 假设 | 当前可查证证据 | 下一项必要证据 | 失败/不可判定解释 |
|---|---|---|---|
| H1 source-only 端到端路线在相同覆盖/风险下优于预先指定基线 | 有三轨道协议、route/proof replay 工程和候选标注设计；无回传标注、semantic-support gold 或 matched baseline 结果 | 许可与归属清理；协议/候选 manifest 锁；盲标裁决；同候选、同预算、group-disjoint 的强基线比较 | 有足够精度而未达到预注册主效应判据，则收窄/撤回增量主张；gold、权利或比较不齐则保持不可判定 |
| H2 保留 AND/OR 能改善整体规则/方向判断 | 固定快照有结构消融；只证明该图中的结构/深度差异，无 gloss gold | 在裁决 claim 上与预定义压平基线比较 exact formula、方向错误和 unsupported entailment | 仅 replay 或结构计数差异不支持语义收益；无人工 gold 则不能识别 |
| H3 span/回放帮助人工审计 | 有 span/schema/独立 replay 接口设计；无盲化人审对照 | 盲化带/不带证据界面的审阅实验，报告定位耗时、错误接受及标签一致性 | 只证 verifier replay 成功不代表审阅体验或判断更好 |

| 目标层 | 当前可查证证据 | 状态 | 仍缺的关键证据 |
|---|---|---|---|
| 审计冻结超图、AND/OR 结构与 witness DAG | [冻结包审计](outputs/phase6/frozen_hypergraph_audit.json)、[最小深度审计](docs/minimum_witness_audit.md)、[basis 支持包络](docs/global_minimum_witness_basis_support.md)、[来源链审计](docs/selected_witness_source_lineage.md)、[压平消融](docs/flattening_ablation.md) | 对锁定快照的结构属性、所选 witness 及来源引用已有多项可重算分析；这些对象不是语义 gold | 需逐项固定数据版本与上游归属映射；需要 source-span→规则语义支持人审后，才可讨论图规则是否忠实于释义 |
| 关系/上下位校验 | [Phase 16 示例](outputs/phase16/oewn_hypernym_verification.json)、[360 项分层 stress producer](outputs/phase16/oewn_hypernym_stress_v1_verification.json)及[独立回放](outputs/phase16/oewn_hypernym_stress_v1_replay.json)绑定 OEWN 2025 Plus（120,564 synsets、93,395 direct hypernym edges） | 示例与确定性 stress frame 已覆盖 direct/transitive path、反向、同 POS 前向不可达、跨 POS、缺失义项和 self-link；stress report 独立 replay `valid=true`、0 errors | stress frame 是 verifier 分支/路径深度压力集，不是概率样本或关系准确率估计；缺少人工 sense-relation 和 gloss-span directional-support gold；资源闭包外不等于语义反例 |
| Gloss→形式规则 | [annotation schema/protocol](docs/annotation_protocol.md)、[受限 Horn compiler](docs/logic_verification.md#标注-ast-datalog-受限编译器)和 [compiler 实现](src/logic/annotation_to_datalog.py) | 人工提交的 AST 可经 schema 校验后编译为限定正 Datalog；编译拒绝条件已包含支持标签、置信度、方向及 schema 0.4 的 `inference_basis` | 尚无经人审并双标的 WordNet 形式化 gold；尚无从自然语言 gloss 自动生成 AST/变量/作用域/有类型规则的已验证端到端系统；编译可执行不证明规则忠实 |
| 蕴含/证明与 NLI | [reviewed pipeline](src/logic/verified_reasoning_pipeline.py)、[Datalog checker](src/logic/datalog_checker.py)、[source-record verifier](src/logic/source_record_verifier.py)、[NLI 评估协议](docs/logic_verification.md) | 有限正 Datalog 证明/反模型回放、fact 与规则到 test sense/gloss 的哈希绑定、NLI 校准及拒答接口已实现；source facts 需绑定到同 sense/gloss、已裁决且 supported 的 gloss atom；fact source paths 与引用标注的 source-record paths 交叉核对；certificate replay 核对 claim refs；Phase 26 verifier 已接入组合路由并可复用 bundle context；Phase 28 增加 `route_pipeline_batch_from_export`，统一编排逐条严格路由并摘要输入 hash；compiler `/3`、pipeline `/11` | 尚无真实 annotation returns 可实际复核；上游确切发行版、许可、来源标签真实性与人类裁决正确性仍未独立核验；无真实冻结模型预测、人工 gold、同切分 matched baseline；strict export 的 manifest SHA 仍须外部固定且模型运行真实性仍需审计；批量 API 当前逐项重验 dev/test 文件，未测性能；无论文级性能结论 |
| 人工确认性标注 | [v3 抽样框/设计](docs/annotation_study_design_v3.md)、[预注册草案](docs/annotation_preregistration_draft_v3.md)、`config/annotation_preregistration_v3_lock.json` | 400 条、24 层候选任务框；raw gloss 与 OEWN 2025 Plus cross-check 为 400/400，effective definition 精确匹配为 376/400。2026-10-06 重跑 text-free preflight：integrity pass，输入哈希、frame/manifest、400 项覆盖与 24 strata 全部通过，尚无回传；这些仍是候选材料而非标注结果。当前 κ 目标限于两位固定标注者 pair | 当前 lock 明示 `protocol_signed=false` 与 `distribution_authorized=false`；preflight 虽通过仍不授权外发。无双人回传、裁决或一致性系数。800 次预定 item-level 标注的负担未试标；任务顺序问题已在设计/代码层推进：版本化 SHA-256 计数器 Fisher–Yates plan/exporter 已生成 2 个本地 draft preview views（400 项/槽）；manifest SHA-256 `e8709e907a1950aad989f69978f20cb45ef94bcabe7b6205c4e1072b9e821222`，并绑定算法/生成器源码 hash。它们未锁入 preregistration，且不是 frame 外工作量试标；尚无外部呈现或 slot—annotator 受限映射。还需完成人工协议审阅、固定版本哈希、来源许可/归属审核、标注者/裁决者安排及明确的分发授权 |
| 相关工作与新颖性 | [相关工作综述底稿](docs/related_work.md)、[逐项对照](docs/closest_work_comparison.md)、[检索协议](docs/literature_search_protocol.md)、[v3 查询扩展审计](sources/acl_query_expansion_audit_2026-10-06.json)、结构化筛读日志 | 已覆盖多轮 ACL Anthology/其他官方来源检索及 2026 近期邻近工作；2026-10-06 全文核读 COLLIE-V/BMEAUT，并筛查固定 ACL 候选库 2016–2019（82 条）、2021–2022 与 2023 切片，发现定义语义角色、definition-augmented NLI、释义数据增强和关系获取等先例；新增核读 Greco et al. (Findings EMNLP 2024)，其 WordNet gloss-conditioned 方向性 lexical-entailment 任务应作为直接 LLM baseline 候选；NeurIPS 2024 KGD-L 将 WordNet definitions/hyponyms 编为用于检测适配的语言知识图，作为跨域图构建先例；新增筛读 SemEval 2026 Task 5 的 GuysLLM 与 SemTechLab/HINTS，纳入 graded sense-plausibility 的 NLI/span 特征候选，但任务不是 gloss source-support；全文定向筛读 NAACL 2025 Code4Logic，确认 code-mediated NL→FOL 与 prover/downstream logic 已有先例；全文定向筛读 Findings EMNLP 2025 FOL Closeness Metrics，纳入受控公式扰动和 metric sensitivity 设计，同时明确其 LLM-judge 对齐不是 source-support gold；全文定向筛读 Findings ACL 2025 Disambiguate First, Parse Later，确认 ambiguity-first interpretation coverage 与分阶段 semantic parsing 已有先例；另全文筛读 ACL 2026 contract-checked reasoning DAG，排除 DAG+结构 gate+证书作为充分创新点；新增 ICLR 2026 CRAMF 与 Mathesis 两篇全文定向筛读，确认定义检索增强 autoformalization 及形式检查/语义评估/证明分层已有数学领域先例 | 目前仍是定向 scoping；ACL v3 关键词候选框扩展为 1,747 条；Phase 29 新日志 reconciliation 后有 447 条精确 URL 日志匹配（56 全文、35 定向章节、204 摘要/元数据、152 深度未明），另 1,300 条待题名/摘要筛查；基线 v3 audit 的 443/1,304 是 Phase 29 前快照，当前重算见 [reconciliation 记录](sources/acl_screening_reconciliation_2026-10-06_phase29.json)；其中新增 ACL 2026 形式化主题切片 24 条题名/摘要决定，10 条做了官方 PDF 定向章节复核，均非全文/附录穷尽阅读。新增词族追回 Logic Haystacks、ETS、Counting-Stars 等已知漏检项，但不构成召回率证据。2016–2019 的 78 条保留记录中，3 篇做了针对性全文核读，其余 75 篇只有题名/摘要筛查；2023 的 11 条保留记录均只有摘要筛查；另有未匹配候选与跨库空白。COLLIE-V induction、BMEAUT matched adaptation、Greco-style direct-LLM matched evaluation 与 SemEval-style graded plausibility adaptation 均未运行，未形成共同 gold 上的 baseline；缺少完整跨库、可复现纳排与最终 novelty audit；未证明研究假设新颖 |
| 开源与可复算 | [CI 工作流](.github/workflows/tests.yml)、[CI 说明](docs/continuous_integration.md)、[发布门槛](docs/data_release_gate.md)、[来源元数据审计](outputs/phase23/source_release_metadata_audit.json) | CI 配置在 Ubuntu 上覆盖 Python 3.10–3.13，在 Windows 上覆盖 3.10 和 3.13；phase 23 报告冻结包来源 payload 完整性锁有效且 source-level rights 未评估 | 本快照没有 CI 运行结果；当前不执行测试套件。仓库无项目代码许可；冻结包、任务/答案键和带身份的结果不能因哈希正确或上游某个版本开放而默认公开 |
| 新论文归属及增量 | [定位备忘录](docs/research_positioning_and_prior_work.md) | 已明确 AAAI 2027 匿名稿不是用户成果，仅作为内部 prior-work 对照 | 需取得可使用既有稿件/数据的授权和版本对照；新贡献须由独立问题、同数据基线与人工 gold 支撑，不能把既有结构审计重新包装为新论文贡献 |

### 2026-10-06 ICLR 2026 ProofFlow 增量

定向筛读 [ProofFlow](https://proceedings.iclr.cc/paper_files/paper/2026/hash/5fce5198dbf92d5ff45f74504431e2ff-Abstract-Conference.html) 后，相关工作状态增加一项已核官方全文的方法近邻：proof-step dependency DAG、结构约束消融、syntactic/semantic/structural composite score 及人工核验 benchmark 均已有数学 autoformalization 先例。因此任何“依赖 DAG + 形式化忠实度验证”宽泛主张必须降级或改写为对象明确的研究假设。它与本项目 gloss-derived AND/OR Horn 及 source-span semantics 不同，但这只是任务边界，不是已证新颖性；须共同 gold 与 matched experiments 验证差异价值。筛读记录：[结构化日志](sources/literature_screening_log_2026-10-06_proofflow_iclr2026.json)，[逐项对照表](docs/closest_work_comparison.md)。本增量不改变无独立 WordNet source-support gold、无 matched baseline、无已证新颖性及未清权的总体结论。

## 发表前的依赖顺序

1. **先冻结合法来源和归属边界**：确认既有材料可用于内部研究的范围，逐来源评估 release/version/license/attribution；在明确授权前不向外部标注者发送任务或答案键。
2. **完成协议审阅和预注册锁定**：审定 `inference_basis` 标签、判例、source-span 规则、双标/裁决流程、拒答和偏离处理；再固定 schema、validator、抽样框、盲标包与分析器哈希并签署/注册。
3. **取得有效独立标注与裁决**：分别保存两位标注者原始记录和裁决记录；验证完整回收，不对无效/非应答样本静默删项；报告各标签分布、设计权重、适用的区间、协议偏离与一致性。
4. **锁定 matched baselines 后评测**：同一 sense/lemma/source split、候选和预算上比较资源标签、词面、sememe/定义模型、直接 NLI、LLM 逻辑化与规则/proof 路线；分开报告关系正确、gloss-span support、逻辑/类型正确、proof replay、NLI 指标、拒答/覆盖与成本。
5. **更新系统检索并审查贡献独立性**：用最近候选池和专业数据库补完定向筛读，保留逐篇排除理由；逐项对照 AAAI 2027 既有主张和公开方法。若没有 gold、直接对照和归属证据，论文中的效果/新颖性只能写成假设，不能写成结论。
6. **发布前进行独立干净环境复算**：在不含本地忽略缓存/私有冻结包的 checkout 上复算可发布结果，逐文件复核代码许可、数据许可、归属和输出提取风险；只有实际 CI 与复算日志通过后才报告发布就绪。

## 当前最关键的断点

结构分析和证明对象已有较多固定快照上的工程验证；最限制下一步论文证据的不是再加一条图指标，而是：**获准且可审计的 sense-linked gloss 标注 → 独立 source-support gold → matched baseline 与错误分析。** 在这个证据链建立前，项目可以报告资源相对结构结果、接口边界和研究假设，不能声称从 WordNet 定义学到了有效知识、改善了蕴含/上下位判断，或已经找到新颖贡献。

2026-10-06 Findings ACL 2026 框外补查：官方全文筛读 Qiu et al., *Pause or Fabricate?*。GRIL 的缺前提检测和 pause/clarify 训练是一般推理边界控制先例；不能替代 WordNet gloss-span support、NLI gold 或 source-only proof/countermodel。论文在冻结 ACL v3 候选框外，通过 ACL Anthology 定向检索发现；不修改 1,747 候选框计数或召回结论。研究边界与全文/附录筛读范围见 [补充综合](docs/latest_related_work_addendum_2026-10-06.md) 和 [结构化日志](sources/literature_screening_log_2026-10-06_gril_findings_acl2026.json)。
### Findings ACL 2026 SLKD 增量

Bi et al. 的 [SLKD](https://aclanthology.org/2026.findings-acl.436/) 以 LLM 逻辑分解、AND/OR/NOT 操作符数与嵌套深度构造自然语言推理样例的密度 proxy，并用于逻辑基准上的 SFT/RL 训练样本选择。它是逻辑结构复杂度/拓扑评分的近期先例；作者明确指出分解噪声、有限模型族与跨域适用性限制。对本项目的审计结论是：冻结 hypergraph 的 depth/OR/AND 统计只描述给定图结构，不能单独当作 gloss support、语义难度或创新证据。论文不在冻结 ACL v3 候选框，筛读记录见[机器日志](sources/literature_screening_log_2026-10-06_slkd_findings_acl2026.json)与[补充综述](docs/latest_related_work_addendum_2026-10-06.md)。


当前形式化实现范围补记（Phase 35）：annotation compiler v3 仍是共享单变量的一元正 Horn/Datalog 原型，validator 没有 predicate-signature/argument-sort type checker；checker 的 arity consistency 不是类型检查。故文献定位中“typed AND/OR Horn”仍是未来研究假设。类型扩展门槛和分层评测要求见[Source-only 证据链契约第 5 节](docs/source_only_evidence_contract.md#5-已有与待完成的-typed-horn-能力)。
2026-10-06 Phase 36 跨会场补查新增两篇 ICML 2026 摘要级背景工作（attention 图谱式推理验证；形式验证驱动代码生成）。它们不构成 WordNet gloss source-support 直接基线，未改变 ACL v3 计数或本审计对人工 gold、许可和 matched evaluation 缺口的判断。详见阶段报告和[筛查日志](sources/literature_screening_log_2026-10-06_icml2026_verification_supplement.json)。



Phase 37 跨会场工作进一步区分模型内部 reasoning topology 与 KG prior/path constraint 两种路线；它们都没有提供 WordNet gloss-span source-support gold 或 source-only replayable Horn proof。Phase 38 则把资源关系 verifier 从 3 条 smoke claim 扩展为 360 项九层 deterministic stress frame，修复 replay 暴露的 self-link `child_pos` 缺失，并获得 `valid=true`、0 errors 的独立重放。两轮都不改变 ACL 候选对账，也不弥补当前 semantic gold/许可/matched-baseline 缺口。详情见Phase 37 报告、Phase 38 报告及[Phase 38 机器记录](outputs/phase16/oewn_hypernym_stress_v1_manifest.json)。




Phase 56 对冻结 ACL 2026 NLI/逻辑候选子集的 58 条完成题名/摘要筛读，26 邻近、2 背景、30 排除；对 CARENLI、Ghost Context、FactAppeal、COMPACT、SciClaimEval 五篇官方全文作定向章节核读。精确 URL 日志匹配从 565/1,747 增至 623/1,747，待筛 1,124；此计数是日志覆盖而非相关工作纳入或系统综述数字。全框仍有 1,124 条无精确匹配，本轮未解决新颖性、source-support gold、许可或 matched baseline 缺口。详见Phase 56和[逐条日志](sources/literature_screening_log_2026-10-07_acl2026_nli_logic.json)。


Phase 57 完成 2026 年 `graph_rule_provenance` 剩余 117 条题名/摘要筛查，定向核读四篇官方全文；结合 Phase 56 的 58 条 NLI/逻辑候选，本 ACL Anthology 2026 固定候选框 295/295 均有精确 URL 日志匹配。全框总匹配 740/1,747、待筛 1,007；深度为全文 65、定向章节 52、摘要/元数据 471、先前未明 152。URL 匹配不是相关工作纳入数或系统综述完成。超图检索、graph evidence retrieval、citation 和 span annotation 均已有先例，但都不能替代 sense-linked gloss support gold 或可重放证明；核心新颖性/效能仍未证实。见Phase 57 报告。


Phase 58 对 2025 年 graph/rule/provenance 余下 133 条逐篇题名摘要筛查，定向核读十篇官方论文。发现 LORex（ACL Findings 2025）直接在 WordNet taxonomy 上结合节点定义和层级路径做父节点扩展，应列为优先 taxonomy baseline；FOL/Horn tree-rule refinement 和 graph-constrained logical parsing 也有先例。当前全框 exact-URL 命中 873/1,747，待筛 874；2025、2026 年均全量 URL 匹配，但匹配不表示全文阅读或相关工作纳入。新颖性、source-support gold、许可和 matched comparison 均未解决。见Phase 58。

### 文献调研进度：Phase 59

- ACL 2024 固定候选 `source_grounded_entailment` 待筛切片 84/84 完成题名/摘要判断，10 篇官方 PDF 做了定向章节核查；新增逐条机器日志与 Phase 59 报告。
- 该阶段收紧来源归因、NLI factuality、entailment-tree、claim extraction 的宽泛创新主张；未证明更窄的 gloss-span→typed AND/OR Horn support 与 replay 任务新颖或有效。
- v3 candidate frame 精确 URL 对账 957/1,747，余 790 条待筛；日志匹配数不等于相关论文纳入数。研究目标继续进行。

### 文献调研进度：Phase 60

- ACL 2024 NLI/逻辑/证明词族剩余 36 条完成题名/摘要筛查，八篇官方 PDF 作了定向章节核查。FRVA、WordNet-assisted model checking、Lean proof validation 与 claim/source attribution 收紧了宽泛 novelty claims。
- 新增筛查日志、对照矩阵、就绪度边界和 Phase 60 报告。更窄的 gloss-span Horn support 和 replay 仍需人工 gold 与 matched evaluation。
- ACL v3 现有 URL 精确匹配为 993/1,747，尚 754 条待筛；goal 未完成。

### 文献调研进度：Phase 61

- ACL 2024 剩余 100 条 graph/rule/provenance 候选完成单人题名摘要筛查，十篇官方 PDF 定向核查。ClaimVer、TRACE、复杂 KG 逻辑查询、KG rule embedding 与图遍历解释扩大了相关工作边界。
- 已更新 related work、closest-work matrix、literature protocol、readiness audit、摘要/首页和 Phase 61 深度报告。source definition span 支撑 typed AND/OR rules 与 proof replay 仍是假设。
- ACL v3 URL 对账 1,093/1,747，654 待筛；目标继续进行。

### 文献调研进度：Phase 62

- 2023 年 definition-to-formal-logic 待筛 31 条已完成标题/摘要判断，九篇官方 PDF 作定向核读。发现 self-supervised text-to-KG rule mapping 与 WordNet–SUMO/FOL ATP 近邻，已更新相关工作、对照矩阵、就绪度审计和 Phase 62 报告。
- gloss 原句到多前提 Horn 规则的来源支持是否与既有关系映射实质不同，仍待 gold 与匹配实验。
- ACL v3 对账 1,124/1,747，623 pending；研究 goal 继续进行。

### 文献调研进度：Phase 63

- ACL 2023 `source_grounded_entailment` 的 57 条待筛候选完成标题/摘要判断，10 篇官方 PDF 做定向章节核读；筛查为 18 邻接、30 背景、9 排除。
- 发现 WordNet sense gloss + mutual entailment 已用于词汇替换，故宽泛的 gloss/WordNet/sense-aware entailment novelty 不成立为单独主张；更窄的 gloss-span→Horn support 与 replay 尚无 gold/匹配实验。
- ACL v3 精确 URL 对账 1,181/1,747，566 条无匹配；覆盖计数不是系统综述或 relevance inclusion。goal 继续进行。

### 文献调研进度：Phase 64

- ACL 2023 graph/rule/provenance 54 条及 WiCE 多证据 1 条，共 55 条完成标题/摘要筛读，十篇官方 PDF 定向核读；19 邻接、32 背景、4 排除。
- SPINDLE 的 typed λ/proof checker、图规则学习/扩增、path spuriousness、FactKG 和 WiCE/RoMQA 已收录对照；宽泛 NL→logic、规则、证明路径和多证据贡献需收窄。
- ACL v3 精确 URL 日志匹配 1,236/1,747，511 无匹配。source-supported WordNet Horn proof 的新颖性/有效性仍未证实，goal 继续。

### 文献调研进度：Phase 65

- ACL 2023 NLI/逻辑/证明剩余 16 条候选完成筛查，九篇官方 PDF 定向核读；8 邻接、3 背景、5 排除。
- PROVER、ReCEval、SICCK、CCG parser 与 FEVER retrieval 收入验证路线对照；NLI proof chain 和 chain scoring 不能代替 source-span 支持或 formal replay。
- ACL v3 精确 URL 匹配 1,252/1,747，495 条待匹配。真实 gloss-support gold、IAA 和 matched results 仍缺，goal 继续。

### 文献调研进度：Phase 66

- ACL 2022 直接关键词切片 20 篇完成标题摘要筛查，10 篇官方 PDF 定向核读；14 邻接、5 背景、1 排除。
- NLProofS、Dual-(m)T5、CCG+Vampire、ZS4IE 等已加入证明/NLI对照；学习 verifier 不等于 Horn certificate replay。
- ACL v3 exact URL 日志匹配为 1,272/1,747。WordNet gloss-span semantic gold、IAA、matched performance 尚缺；goal 继续。

### 文献调研进度：Phase 67

- ACL Anthology 2021 direct-keyword 切片 14 篇完成题名/摘要筛查（6 邻接、6 背景、2 排除），6 篇官方 PDF 做定向核读。Sumita 的 interactive theorem-prover NLI、RuleBERT soft Horn、UniKER definite Horn、WinoLogic Z3 knowledge validation 已收紧宽泛创新说法。
- 文件级实现审计确认已有人工审核→受限 unary positive Datalog→证书重放/NLI 路由骨架；source-span validator 只验证结构与偏移，不判断语义蕴含；predicate argument typing 未实现。
- ACL v3 精确 URL 日志匹配 1,286/1,747，深度全文 75、定向 134、元数据/摘要 851、先前深度未明 226；461 条仍待筛。文献框为单人 scoping，不能支持召回或新颖性结论。CodeGraph 初始化因当前环境缺少 CLI/MCP 工具未能执行；未运行测试，未运行系统代码。goal 继续。
- 详见Phase 67 报告和[结构化日志](sources/literature_screening_log_2026-10-07_acl2021_logic_proof.json)。

### 工程进度：Phase 68 typed Datalog 原型

新增版本化显式 sort/signature checker，并接入 closure、proof/countermodel replay 与 reviewed-gloss pipeline 的可选 type table。未选择/绑定正式 WordNet 类型本体；canonical annotation/compiler 仍需 rule-ID side table 传变量 sort。py_compile 通过，没有执行测试或样例推理，所以没有运行时效果结论。它不验证人工规则对 gloss 的语义支持，source-support gold/IAA 与 matched baseline 仍缺。详见Phase 68及[接口合同](docs/typed_datalog_contract.md)。

### 工程进度：Phase 69 类型环境哈希绑定

针对 typed Datalog artifact 未携带类型环境 hash 的审计问题，certificate/countermodel 现在都绑定 `type_system_sha256`，replay 要求精确匹配。仅 py_compile 通过；未运行示例、replay 或 tampering tests，不能声称运行时行为已验证，也不证明 type table 或 gloss 语义正确。详见Phase 69 报告。

### 工程进度：Phase 70 annotation 到 typed Horn 的变量 sort 传递

实验性 annotation schema 0.5 让每条 rule claim 显式携带覆盖公式变量的 sort 声明，compiler v4 将其写入派生 Horn rule，agreement analyzer v10 将其纳入 claim 比较；0.2–0.4 保持兼容，当前 v3 标注方案仍使用 0.4。61 项 annotation/compiler/Datalog/pipeline/agreement 聚焦测试通过。类型仍由调用方声明，未绑定权威 lexical ontology，也不证明 gloss 语义支持或研究有效性。详见Phase 70。

### 工程进度：Phase 71 typed Datalog replay 边界

新增 3 组 typed checker 行为用例，单测 10 项通过：子类型域 binding、typed certificate hash 缺失/类型表版本变化、countermodel hash 变化及错 sort atom 注入拒绝。证据限于 synthetic finite Datalog；WordNet 类型来源、释义支持、NLI 和论文有效性仍未验证。详见Phase 71。

### 工程进度：Phase 72 typed strict pipeline route

新增端到端 regression：0.5 variable sort 经 pipeline 入 typed program；proof 后更换 type table 会让 route 拒绝旧 certificate；有限反模型在 hash 完好时可输出“supplied program 内不蕴含”，篡改 hash 后转为拒答。pipeline 单测 12 项、五模块合并测试 66 项通过。结果仅限 synthetic finite Datalog，不证明开放世界假命题、WordNet 类型或 gloss 语义。详见Phase 72。

### 研究进度：Phase 73 OEWN type inventory 来源审计

新增可复算、无 gloss 输出的 OEWN 2025 Plus inventory auditor。Pinned archive 上 profile 到 120,564 synsets、45 lexicographer files、93,395 ordinary hypernym edges 和另 8,599 instance_hypernym edges；profile 重算与机器产物一致，2 项合成测试及包含 Phase 70–72 的 68 项聚焦回归全部通过。官方 lexname 只是句法类别/逻辑分组，不能未经验证转成 sort lattice；instance relation 也与 class hypernym 分开。该审计不定义 glossary 变量的语义域或证明类型 gold。详见Phase 73。

### 研究进度：Phase 74 gloss referent/type 契约草案

将 lexical sense、unary Horn 变量 referent 与 sort 分层；为当前片段提出 `Referent` 根和实验性 `Entity`/`Eventuality` 域，并明确 POS 不是类型证据、instance relation 不自动转换为成员事实、复杂多元语义留在片段外。定向核对 GWC 2023 WordNet Gloss Corpus→ERG predicate parsing，收窄宽泛 semantic parsing 新颖性主张。新增设计文档但未改 schema/compiler，也未新增测试；类型选择仍是假设，需 challenge annotation、双标一致性与 matched evaluation。详见Phase 74。

### 研究进度：Phase 75 sort judgment provenance 链

实验性 schema 0.6 记录逐变量的类型 status/sort/basis/rationale/evidence span，unresolved 判断不编译；compiler v5 保留 assigned judgment 与 review status 到 rule provenance；agreement analyzer v12 输出独立的 sort-judgment multiset micro P/R/F1 和 bootstrap 区间。73 项聚焦回归通过，包括 typed pipeline 端到端证书重放、provenance tampering 和旧 schema 兼容。实现只验证数据链路完整性，不证明 sort 选择的语义正确性。当前 v3 仍使用 0.4，真实 gold/IAA/matched 语义评测未完成。详见Phase 75。

### 研究进度：Phase 76 instance_hypernym relation adapter

固定 OEWN release 中 8,599 条实例类边现由单独 verifier 加载，class `hypernym` 不与实例谓词混合；规则显式展示如何把 direct membership 沿 class hierarchy 提升。新增独立 ZIP/JSON/图 loader、SHA-256 manifest、DFS 闭包和 Horn proof replay，producer 两条正证书 valid、0 errors；篡改拒绝测试通过。目标 82 项与完整 220 项项目测试通过。尚无第三方实现交叉核对、人工 sense gold、gloss-support/NLI matched evaluation；本结果不是论文效果或新颖性证据。详见Phase 76。

### 研究进度：Phase 77 instance_hypernym stress frame

新增 320 条固定种子结构压力集，八层分别测试直接实例关系、1/2+ 层 class lifting、关系方向反转、同 POS 资源内不可达、跨 POS、synthetic missing 和 self-pair。producer 六类状态分布与 strata 对应，独立 replay 全部 320 条 valid、0 errors。它只能说明固定资源和构造输入下的程序分支/路径行为，不能当作 semantic accuracy 或 NLI 评估。全项目 222 项测试通过；人工 sense gold 与 matched semantic evaluation 未完成。详见Phase 77。

### 研究进度：Phase 78 relation pair 人工审查设计

在现有双标锁 `distribution_authorized=false` 下，只生成本地 text-free、320 项、五层候选 ID 与单独隐藏 key；未读取或导出 gloss、未分发。producer/replayer 预检通过。研究设计分开 sense relation truth 与 strict two-gloss support，并确认当前 single-sense annotation 0.4 不适用于跨 sense pair，需要独立 pair schema/validator。样本数尚非功效设计，人工 gold/协议/许可/注册均未就绪。详见Phase 78。


### 研究进度：Phase 79 pair-level annotation schema draft

新增独立 0.1-draft pair schema validator，覆盖双 sense/source binding、独立 gloss hash 与 span 空间、sense relation 与 gloss support 双标签、状态约束、标注重复与发布漂移。`supported` 与 `gloss_only` relation judgment 均要求两条 gloss 各有 span，且仅是结构要求。当前只有 synthetic fixture 测试，没有 OEWN gloss、人工标注或语义判断；未授权 lock 不变。schema 尚待手册审查和试标，不能据此报告效果或 novelty。专项测试 8 项、全项目回归 232 项通过。详见Phase 79。


### 研究进度：Phase 80 pair 标注手册草案

新增 pair-level 标注手册工作稿，将 sense relation 与 strict two-gloss support 的信息边界、标签、blind procedure、裁决与分层报告分开，并列出许可、no 标准、试标、estimand 等签署前决策。pair schema 升至 0.2-draft，为两种 judgment 各存 rationale。手册尚未经负责人签署或试标；“允许常识判断 relation、禁止在线检索”目前是建议，lock 仍未授权。并加入 synthetic-only JSON fixture。专项测试 10 项、全项目回归 234 项通过。见Phase 80。


### 研究进度：Phase 81 pair frame 精度审计

基于 text-free manifest 计算分层二元比例最坏情形规划精度：n=64 的单层半宽约 ±12.2pp，closure-positive 按 population weights 汇总约 ±9.3pp，层间对比约 ±17.3pp。当前样本数不是功效设计。same-POS challenge 按 source 等权、source 内 target 均匀的宏平均解释，不能宣传成均匀 pair 总体。新增纯 aggregate audit 脚本和 3 项 synthetic tests；全项目 237 项通过。见Phase 81。


### 研究进度：Phase 82 pair study 统计分析计划草案

新增 pair SAP 草案：推荐 closure-positive strict-gloss-support label prevalence 为 primary，按 population size 加权；分开报告层间率/差异、sense-relation human reference 和 challenge strata；把 uncertain 与 missing 分开，列出最坏界限和冻结前的 CI/multiplicity 决策。文件明确它不是 preregistration，也不把 adjudicated labels 当作真值。标注授权仍未获得。见Phase 82。


### 研究进度：Phase 83 exact finite-population intervals

新增超几何反演单层区间与 Bonferroni 分层 simultaneous bounds，支持加权 closure-positive prevalence、差值界限与 missingness worst-case bounds。小总体 `N≤8` 对所有抽样/成功数穷举验证 nominal coverage，4 项测试通过；全项目 241 项通过。有限样本区间较宽，方案尚未签署；这不提供 semantic gold 或 effect evidence。见Phase 83。

### 研究进度：Phase 84 SemEval 2026 逻辑内容效应近邻

定向核读 SemEval-2026 Task 11 官方总览论文，记录其形式有效性/内容合理性分离、四种语言与无关 premise 条件、content-effect 评测。该工作启发 NLI/释义解析阶段设置 plausibility 与干扰上下文压力测试，但不是 WordNet gloss-span support、Horn proof provenance 的匹配 baseline。没有独立复现或效果结果；跨模块组合价值仍属研究假设。见Phase 84 深度分析。

### 研究进度：Phase 85 NLI 内容效应与干扰上下文方案

审读现有 NLI 三分类校准接口及 strict source-only proof route，新增独立的未冻结诊断评测草案：plausibility strata、人工核准匹配对、无关上下文条件、数据隔离和估计量边界。它不是实现、注册或实证结果；未触碰 annotation lock。见Phase 85 报告。

### 研究进度：Phase 86 NLI 内容效应诊断 evaluator

实现 text-free sidecar validator 与独立 descriptive evaluator；支持 plausibility strata、matched contrast、irrelevant-context pair，检查模型版本/预测配对/hash 与 split group，并输出混淆矩阵、FNR/FPR、内容差值及翻转率。原型不接入校准或严格证明路由，不计算置信区间，也未使用真实 annotation/model 数据。六项 synthetic 测试、NLI/route 33 项聚焦回归及全项目 247 项测试通过。见Phase 86 深度报告。

### 研究进度：Phase 87 当前就绪度重审

刷新研究就绪度审计顶部状态，区分固定超图/逻辑代码的结构验证与语义 gold、权利清查、matched results 的缺口；确认 Phase 58 后没有固定 ACL 1,747 候选框全局 reconciliation，旧总数不能继续当作当前覆盖统计。对已记录的 Neural DTS 官方全文补充 sense aggregation 的方法边界；不把已知 workshop 论文记为新顶会发现。详见Phase 87 报告。

### 研究进度：Phase 88 OEWN 2025+ 发布记录绑定

增加隐私过滤的可复算审计，验证冻结候选 payload checksum、本机固定 OEWN 2025+ ZIP 的 inventory SHA-256，并将六条 source evidence 的 ILI 与释义散列联合匹配到归档中的唯一记录。它尚未追踪图规则 lineage，也未评估整体许可兼容或授权；`release_clearance` 保持 `not_assessed`。见Phase 88 报告。

### 研究进度：Phase 89 OEWN 来源记录图级结构 lineage

将六条候选 payload 的 sense identity 与六个冻结图 head 精确连接；11 条子句与 hyperedge 对应，六个 selected witness clause 与规则/hyperedge 一致。4/6 有直接 active source-document path 记录，2/6 只能连到同一 sense 下其他 source record。结构验证不等于 gloss 语义证据，许可状态仍未清权。见Phase 89 报告。

### 研究进度：Phase 90 selected witness 来源文档精化

按每个 head 的 selected witness clause 重新核对 active source documents，并验证六个来源文件 checksum。只有 2/6 selected documents 同时保留候选 payload path、相同 OEWN ILI/定义散列及同一释义的精确文本散列；其余候选分为非 witness 子句专属两条及无 active source path 两条。不得将更宽的 4/6 active-path 计数当作 selected witness attribution。见Phase 90 报告。

### 研究进度：Phase 91 ACL Anthology 全局对账

对官方 2016–2026 ACL 候选固定框的 1,747 条记录及当前 90 个结构化文献日志做精确 URL reconciliation：1,286 条至少一条日志匹配，461 条无全局日志匹配；显式全文 75、定向章节 134、元数据/摘要 851、深度未明 226。全局匹配不是词族级覆盖、相关性决定或系统综述完成。见Phase 91 报告。


### 研究进度：Phase 92 ACL 2022 候选筛读与近邻复核

完成 2022 年 130 条全局未匹配 ACL 候选的题名摘要筛读（22 邻近、2 背景、106 排除出核心综合），并对 4 篇官方论文做定向章节核读。总框复算为 1,416/1,747 URL 匹配、331 未匹配；2022 未匹配清零，剩余 331 条在 2016–2021。该统计与筛读不构成系统综述完成或 novelty 证据。见Phase 92 深度报告。


### Phase 93：ACL 2021 未匹配候选筛读与逻辑验证近邻

完成 2021 年 85 条未匹配候选筛读（26 邻近、2 背景、54 排除出当前核心综合、3 因缺摘要暂缓），对 4 篇官方论文定向核读。全框复算为 1,501/1,747 匹配、246 未匹配；剩余未匹配项在 2016–2020。见Phase 93 深度报告。


### 研究进度：Phase 94 ACL 2020 候选筛读与创新边界更新

筛读 94 条此前未匹配的 ACL 2020 候选（29 邻近、3 背景、62 排除），定向核读六篇官方论文相关章节。全框为 1,595/1,747 匹配、152 未匹配，剩余均在 2016–2019。逻辑学习词汇关系、形容词 DL 形式化、WikiNLI、proof graph 约束和细粒度 source support 均有先例；项目主张须收窄到 gloss 片段证据、typed Horn 语义正确性和独立 witness replay，并做匹配评测。此阶段不代表系统综述完成或新颖性确认。见Phase 94 深度报告。


### 研究进度：Phase 95 ACL 2019 候选与定义路径近邻审计

完成 68 条未匹配候选筛读（26 邻近、7 背景、35 排除），对 4 篇官方论文定向核读。全框为 1,663/1,747 URL 匹配，84 待筛项均在 2016–2018。Prokhorov et al. 已从文本定义预测本体 hypernym 路径，E3 已联合来源规则提取与 entailment；因此不能宽泛声称首次定义到图路径或自然语言规则抽取。候选贡献须经 span 级来源、typed Horn gold、独立 replay 和匹配 baseline 实证。见Phase 95 深度报告。


### 研究进度：Phase 96 ACL 2018 形式化与WordNet验证先例

筛读38条未匹配候选（18邻近、8背景、12排除），对6篇官方PDF做定向核读。全框为1,701/1,747匹配，46未匹配在2016–2017。已确认自然演绎短语关系学习、自然语言定义到OWL DL、WordNet/SUMO自动定理证明审计、词汇资源引导的NLI规则模板等直接先例；不能声称这些组件本身首次。当前研究差异仍是假设，需用sense-linked span标注、typed Horn gold、独立replay和matched baselines证明。见Phase 96深度报告。


### 研究进度：Phase 97 ACL 2017 逻辑与词汇推理先例

筛读27条未匹配候选（17邻近、7背景、3排除），对4篇官方论文定向核读。全框为1,728/1,747 URL匹配，余19条均在2016年。已确认证明失败驱动的词汇公理注入、自然语言tableau theorem prover、proof-derived语义相似度和自然语言解释概念学习等先例。当前研究新颖性仍未证实，需聚焦义项绑定gloss span、source-entailment和独立Horn witness replay并开展匹配评测。见Phase 97报告。


### 研究进度：Phase 98 ACL 固定候选框审计完成

完成2016年最后19条候选筛读（10邻近、6背景、3排除），对5篇官方论文定向核读。冻结候选框1,747/1,747 URL均有日志匹配，pending=0；仍有229条旧日志深度不明。此结果不说明全ACL召回或系统综述完备。领域ontology/glossary、WordNet跨资源formal ontology、KG逻辑规则联合建模及文本蕴含图已有先例。研究新颖性未证实，下一步扩展到ACL外引用网络，并测试sense-linked gloss-span→typed Horn→independent replay假设。见Phase 98报告。
# Phase 99 状态补充（2026-10-07）

固定 ACL v3 候选框已完成 URL→日志匹配（1,747/1,747）；仍有 229 条旧日志筛读深度未明，且 1,276 条仅有摘要/元数据证据，因此文献综述不视为完成。ACL 框外新增 4lang/BMEAUT 期刊后续全文筛读：宽泛的“首次可解释定义图蕴含”不成立。研究 goal 仍待跨库引文追踪、合法可用的 sense-linked gloss gold、双人 source-support 标注、匹配 baseline 与独立复算。详见Phase 99 深度报告。

# Phase 100 状态补充（2026-10-07）

新增 BRISE-Plandok 近邻复核：4lang 图模式辅助从法规文本抽取 formal rules，并用双标/专家复核 gold 评测。排除“首次图式规则抽取/首次 gold 评测”宽泛主张；该工作不涉及 WordNet gloss。研究 goal 未完成，需以共同 gloss-sense gold 测试窄化差异。见Phase 100 报告。

# Phase 101 状态补充（2026-10-07）

确认 ASAIL 2021 BRISE 论文已做 semantic graph→formal rule→theorem prover；完整抽取完美结果仅来自 6 句 toy set，并非全系统量化结果。与 BRISE-Plandok 2025 视为一个研究线。项目仍需验证 WordNet gloss/source-span/Horn 语义假设，不能用 prover 通过代替 source fidelity。见Phase 101 报告。

# Phase 102–103 状态补充（2026-10-07）

Phase 102 区分了受限 gloss compiler 与 caller-signature typed Datalog checker：形式重放不等于 gloss entailment。Phase 103 复核新接收的 AKBC 2026 lex-NLI 工作，发现结构化词汇 explanation、多人 gold 和 prover 已有强邻接先例；且 prover proof coverage 可能由语义不可靠的关系提高。现阶段新颖性只保留为 sense/release-linked gloss-span support 与独立 Horn/witness replay 的研究假设，仍缺双人 gloss gold、IAA 和 matched experiment。见Phase 102与Phase 103。

# Phase 104 状态补充（2026-10-07）

静态检查发现当前 `0.4-draft` 未表示互斥的整套有效分析；语义 OR、合法分析 alternatives 和未解决歧义现已在协议草案中区分。签署确认性方案前，需选单一裁决 reference 或多参考 sidecar；Phase 105 已提供后者的 validator/scorer 原型，但没有运行验证或锁定 estimand/hash，且未改现有 400 项输入锁、签署与分发状态。见Phase 104和Phase 105。

# Phase 105 状态补充（2026-10-07）

新增 `gloss-analysis-reference/0.1` validator 和 alternative-aware scorer 原型。它对每项完整 reference alternatives 独立评分，使用 claim-set F1 选择 best admissible alternative，并把 canonical root AST 与分析状态纳入整体 exact match。仅静态审阅，未运行测试/CLI；无真实 gold、研究者协议审阅、代码/schema hash lock 或标注授权。该实现不改变 Phase 104 指出的确认性 estimand 选择需求。

# Phase 106 状态补充（2026-10-07）

新增 alternative-aware macro P/R/F1，与 claim-volume-weighted micro 并报。Macro 的分母仅含至少一侧存在 rule claims 的已评分项目；空/空项计入 exact match 但不进入 macro P/R/F1，并报告数量。估计量尚未运行验证或预注册锁定，详见Phase 106。

# Phase 107 状态补充（2026-10-07）

Scorer 核心 API 新增 scorer/canonicalizer/validator 源码 SHA-256 和基本 Python runtime 指纹输出，CLI 另记录输入文件哈希；Phase 108 将结果 schema 升至 `/0.2`、scorer 实现版本升至 `/0.3`，以标识新增输出契约。该记录可帮助区分源码/Python 版本不同的运行，但没有固定完整依赖环境或进程执行映像，也未通过 CLI 验证；不能等同于完整可复现运行。详见Phase 107和Phase 108。

Phase 109 收紧 sidecar 状态契约：`complete` 项不能带 unresolved candidate；未决候选仍存在时，整项不得进入 completed-gold 评分分母。输入 schema 升至 `/0.2`，scorer 标识升至 `/0.4`。该 fail-closed 语义尚待研究者/标注流程审阅，且只做静态检查，未运行测试或 CLI。详见Phase 109。

Phase 110 实现 `verify_gloss_oewn_relation_links.py`，按 candidate-row hash、source sense/gloss、人工 genus mapping、release pair 和 report hashes 核验跨文件链接；hypernym replayer v3 输出 query 与 producer-report hashes。只做静态审查，未运行 CLI/测试；bridge schema/协议未锁、人工 mapping 和经验评测缺失。旧 replay v2 artifacts 不可用于新 bridge，须重新生成。详见Phase 110和[评测协议](docs/claim_verification_evaluation_protocol.md)。

Phase 111 按用户确认建立 CodeGraph 索引并静态审计 bridge。修正 protocol 中关于 frozen candidate/span 语义校验的过度表述，validator 现在拒绝全空白 genus span。审计确认仍缺 candidate manifest 外部哈希联锁、独立 JSON Schema、人工 mapping、全链路运行和实证评估；本阶段未运行测试或 CLI。详见Phase 111。

Phase 112 将 candidate manifest 及外部 SHA-256 pin 接入 bridge，复用 `validate_against_candidate_manifest` 核验 sidecar 与 text-free manifest 完整一致，并在 validation output 中保留 manifest 指纹。报告 schema 和 validator 实现标识升至 `/0.2`。只做静态审查，未运行 bridge/replay CLI、测试或数据验证；独立 bridge JSON Schema、真实映射和发表级实证仍未完成。详见Phase 112。

Phase 113 为 bridge link 和 validation report 增加独立 JSON Schema，并要求 bridge row 覆盖全部 claim-review candidates，避免 unresolved mapping 被排除出 denominator。仅静态检查，未运行 JSON Schema validator、项目测试或 bridge/replay CLI。语义 mapping、端到端复算、授权、gold 和发表级评估仍缺失。详见Phase 113。

Phase 114 对 ACL Anthology 2026 lexical-relation 候选做官方来源去重，确认新命中条目已在相关工作矩阵中；并核对 ACL 官方 long-paper 页面有 2,223 篇，避免把项目 1,747 行 query-derived 跨年候选框误称为全 ACL census。本轮没有发现 direct baseline，也不构成系统综述或新颖性证明。详见Phase 114。

### Phase 115：NeurIPS 2025 形式化忠实度与 WordNet 层级

官方 proceedings 定向筛读新增 HAR/CoPA、miniF2F-Lean Revisited 和 Hierarchical Retrieval。方法学结论是把 formal proof validity 与 source-to-formal fidelity 分开；WordNet retrieval 论文使用 synset hierarchy，不是 gloss reasoning。筛查不是 proceedings-wide systematic review，也没有证明项目新颖性或效果。总体缺口仍是 source-support gold、IAA、matched baseline、bridge 端到端运行和干净环境复算。详见Phase 115和[结构化日志](sources/literature_screening_log_2026-10-07_neurips2025_autoformalization_wordnet.json)。
### Phase 116：ICLR 2026 semantic-fidelity 与 AND/OR interaction 邻近工作

ReForm 已有数学 formalization 的 semantic consistency 专家 benchmark 和双标/裁决先例；法律模型研究已有数值 AND/OR phrase interactions 与专家 relevance audit。项目不能将宽泛语义忠实度评估、AND/OR pattern 解释单独当作贡献。与 WordNet gloss、逐 claim 支持跨度、source-only typed Horn 与可重放 witness 的差异仍未在共同 gold 上验证。此轮只是两篇定向全文筛查；不是 ICLR 全量综述，也未运行复现。详见Phase 116与[结构化日志](sources/literature_screening_log_2026-10-07_iclr2026_reflective_fidelity_and_andor_audit.json)。
### Phase 117：Selected-witness source-lineage 复算加固

Phase 19 的 lineage v1 未记录其依赖的 `selected_basis_atoms.txt` hash，也未统一验证 frozen-bundle integrity lock。现在 v2 运行前检查锁定 bundle，单独核验 basis 与 checksums sidecar，并将全部输入 hashes、五个实现文件 hashes、Python/platform 写入聚合报告。对完整冻结包重跑后，110,340 个 selected clauses 的来源链和 110,382 个 payload 校验全部通过，checksum/identity 错误为 0；artifact 另通过独立 [Draft 2020-12 JSON Schema](config/selected_witness_source_lineage.schema.json) 校验。此结论仅限来源文件结构与身份一致，不表示 gloss 语义蕴含、sense 选择或 license clearance。详见Phase 117 报告、[v2 artifact](outputs/phase117/selected_witness_source_lineage.json)和[审计说明](docs/selected_witness_source_lineage.md)。

### Phase 118：OEWN hypernym replay v3 运行复核

在锁定的 OEWN 2025 Plus release 上，当前 producer 对历史固定 360 项 stress frame 完整重算；producer 报告的状态分布与预设分层一致。独立 replay v3 覆盖 360 项，160 个正路径重放成功，`valid=true`、0 errors；bridge schemas 的 Draft 2020-12 meta-schema 检查通过。此运行只证明 taxonomy release 内关系路径与报告/claims 指纹可重放，不是准确率估计或 gloss 语义支持结果。由于缺少获授权、裁决过的 genus mapping 与锁定 manifest，gloss bridge 尚未端到端运行。详见Phase 118 报告、[producer](outputs/phase118/oewn_hypernym_stress_v1_verification_v2.json)和[replay v3](outputs/phase118/oewn_hypernym_stress_v1_replay_v3.json)。

### Phase 119：synthetic gloss–OEWN bridge wiring

两条清晰标记为 synthetic、且 NLI/source-support 均为 unassessed 的 sentinel fixture 贯通 candidate manifest freezer、OEWN producer、replay v3 与 bridge validator；一个 unresolved mapping 保留在完整候选分母中。manifest 正确 pin 时 validation report valid；全零错误 pin 和缺失 unresolved bridge row 均被拒绝。candidate manifest、claim-review、bridge link 和 success/failure validation-report artifact 均通过 JSON Schema 实例检查。此工程性证据不是真实 gloss mapping、人工 adjudication、性能样本或语义 gold；真实 bridge 及授权/双人裁决数据仍未完成。详见Phase 119 报告和[合成 fixture](examples/synthetic_gloss_oewn_bridge/README.md)。

### Phase 120：EMNLP 2025 reasoning/verification 文献筛查

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

GNU 下载页公布 MD5 与本地 0.54 tar.gz 一致，归档 SHA-256 与 179,781 个上游 `<def>` 块数均记录在机器 artifact。受限重验 5,625 个冻结 payload checksums 后，对 1,562 个不同 evidence 定义哈希作三种明确规范化交叉比对：原始字节命中 88 个，标签剥离与文本规范化命中 846 个。再对账同 payload 的字符串字段发现，1,579/1,580 条 evidence hash 精确等于 `synset.raw_definition` 的 UTF-8 SHA-256；余下 1 条未与同 payload 任一字符串匹配，但在归档中命中一个恢复出 WordNet 标记的段落。这提供具体混合子来源审查线索，不等于唯一来源或法律裁定。大多数归档匹配绑定当前冻结 gloss 字符串，但不能证明上游 sense、语义支持或图规则/witness 使用。GPG 签名未验证，段落来源标签由正则探索恢复且不是逐项权利裁决；项目发布状态仍未清权。见[Phase 126 artifact](outputs/phase126/gcide_archive_hash_crosswalk.json)与深度报告。

## Phase 127：GCIDE payload 到 graph/witness 的路径级 lineage

全量复核 5,625 个目标 payload checksums，将 1,573 个 GCIDE payload path 连接到 sense index、graph rule/hyperedge 与 selected witness。所有 payload 唯一对应 index identity；1,188 个路径出现在 active-clause 来源文档，886 个直接进入 selected-witness 来源文档，302 个仅在非选定活动子句，385 个无 active-clause 来源路径。1,570 个 graph heads 均有 rule/witness；40 个 seed，1,530 个非 seed witness clause 全部与 rule/hyperedge 对齐。Phase 126 唯一 WordNet-marker 异常 payload 在 385 个无来源路径项中，不进入 selected witness。路径 lineage 不代表 gloss-span 语义支持或许可清权。见[Phase 127 artifact](outputs/phase127/gcide_graph_lineage.json)及深度报告。

## Phase 128：selected-witness gloss hash 与归档子来源标记

在 886 个 selected-witness-linked GCIDE payload 中，506 个 gloss hash 于官方 0.54 归档按去标签/HTML/NFC/空白规范化匹配（502 个 distinct hashes，503 次归档出现）。46 个 payload 至少匹配到 WordNet marker 段落，433 个匹配到 Webster 1913 marker 段落，489 个匹配到任一非空 marker；这些来源类别可因同 hash 出现在多个段落而重叠。380 个 payload 在当前变换下未命中。此结果提供 selected-witness 路径上的 gloss—归档文本关联，但不证明 marker 独家归属、rule literal 语义支持或许可。见[Phase 128 artifact](outputs/phase128/gcide_marker_witness_crosswalk.json)和深度报告。

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

## Phase 134：KR 2026 最小支持与形式证明邻接 prior

KR 2026 有限主题筛查补出 database minimal-support relevance、FOL non-equivalence explanations、rule-based terminating proof certificates 与 Lean chase formalization。它们收窄宽泛支持/解释/证书新颖性，但没有 gloss-span source support gold 或同任务对照。筛读依据官方目录和摘要，不是全会议系统综述。见Phase 134。

## Phase 135：EACL 2026 WordNet gloss / lexical prediction prior

官方 25 页全文确认 WordNet inverse definition modelling 与 hypernym prediction 的近期 EACL 主会先例，并厘清两者输入不同（gloss→term 与 word→hypernym）；CAP 分数仅为干预前答对样本上的条件鲁棒性指标。论文缺席冻结 ACL v3 候选，已据此补充检索词与任务匹配 baseline 建议。核心 gloss-span→typed Horn support 仍未验证。见Phase 135 深度报告。

## Phase 136：ACL definition-conditioned lexical prediction 候选扩展

搜索器新增独立释义条件 lexical prediction 词族，生成官方导出可追溯的 v4 候选与精确 URL 对账副本；冻结 v3 未改。v4 对 v3 ID 差分为新增 EACL 2026 一篇、无删除；Cho et al. 2020 为旧框重召回。v4 有 1,748 条日志 URL 命中，但 229 条筛读深度未明，不表示全量筛读。见Phase 136。

## Phase 137：固定 ACL 导出同源消融

为解决 Phase 136 的导出哈希不同问题，固定官方 ACL export 并实现离线重跑与 query-family exclusion。在同一输入字节上基线与新词族差 1 条候选（EACL 2026），旧词族候选集合完全复现冻结 v3。完整 export 仅作本地复算，因包含窗口外混合许可材料不公开再分发。见Phase 137。

## Phase 138：ACL 搜索器流式解析

改用逐行解压及逐 BibTeX 条目处理。固定快照复算与 v5 在 1,748 个候选 ID 和全部共同记录字段上完全一致，解压哈希、条目数、旧查询族命中数及筛读深度计数保持一致。运行中工作集样本约 69 MiB，历史整文件流程样本约 966 MB；该观察不是受控峰值内存基准。见Phase 138。

## Phase 139：OEWN 全量名词 genus 基线复现核验

以当前工作树重跑固定 OEWN 2025 Plus release 的名词 genus 词面基线，53 个实际读取的 entries/noun JSON 均与 pinned ZIP 字节匹配。输出与 Phase 11 聚合结果逐字节一致。它确认确定性复算稳定，不证明 sense 选择、释义语义支持、蕴含有效性或系统优势；真实 gold 和授权标注 gate 仍未满足。见Phase 139。

## Phase 140：400 项标注批次与三轨适配审计

只读审计确认 v3/400 可为 Track C 收集带 span 的 gloss/rule 人工参考，但不覆盖 Track A 的 claim-pair NLI；Track B 还需独立固定形式程序、事实与 query。双 presentation 排序复算有效，answer key 未进入任务包；其 protocol/schema 版本尚未在 input lock 中固定，且仍未签协议、未授权分发、0 回传。见Phase 140。

## Phase 141：Track A premise 目标上下文审计

对当前 pair schemas 与 NLI exporter 的审查发现：premise 必须等于 raw gloss，source 未显式绑定 lemma，hypothesis rendering 尚未冻结。因此 Track A 的目标词义上下文以及 human/model input parity 仍未定义。建议在生成 pair frame 前由研究者审阅版本化的 lemma+POS+gloss renderer 与 raw-gloss-only paired ablation；原 `/0.1` hash 契约保持不变。无项目候选或结果。见Phase 141。

## Phase 142：ACL 2026 分步 grounded-claim factuality prior

官方全文定向筛读发现，复合 claim 分解以及逐步检查主客体、描述、关系和推断是否受来源支持已有 ACL 主会先例。该文是后续可适配的 prompt baseline，不是 WordNet/gloss-span/typed-Horn 匹配基线；其事实性分数和 token 效率不可移植为项目结论。项目仍无 Track A pair frame、裁决 gold 或模型结果。见Phase 142 深度报告。

## Phase 143：source-only 推理路由契约审计

CodeGraph 与代码静态检查确认，source-only 只将明确 source assertions 纳入程序；typed validation、proof/countermodel replay、unknown、reviewed-span binding、source bundle hash 校验和 NLI export split/hash gate 已在路由中分离实现。反模型仅是有限程序内不蕴含，不是自然语言否定。没有在本轮运行程序或测试，也没有真实 gold 或模型结果；项目仍需完成授权、标注回收、pair 输入冻结和匹配评估。见Phase 143 报告。

## Phase 144：Track A 候选输入 release identity audit

v3/400 的 400 个 target sense ID 与 raw gloss 均通过 pinned OEWN release 对账，但 1 个 frame/source POS 不一致，另 1 个目标 lemma 集遗漏 release lemma。根因为旧 frame 的 POS 来自冻结 graph、lemmas 来自首条匹配 source record。当前 batch 保持不可变；任何新 pair frame 必须从 pinned release 按 sense ID 获取 POS 和全部 lemmas。311 个 direct parent 中 172 个有多 lemma，hypothesis 的 parent 表面策略仍未冻结；未生成 claim pair/gold/model result。详见Phase 144 报告。

## Phase 144：Track A 候选输入一致性审计

对锁定的 400 项 blind batch 与固定 OEWN 2025 Plus release 作身份字段核查。400 个 sense ID 与 raw gloss cross-check 均匹配；发现 1 项 POS 冲突及 1 项 target lemma set 不完整。新增只输出计数/标识符的可复算审计程序与机器报告。结论：保留 v3 字节，新的 Track A frame 必须从 release sense record 重取 POS/完整 lemmas；parent 多 lemma hypothesis policy 仍未冻结，不生成 pair/gold。此阶段不改变 0 回传、未授权分发和无效能结论状态。报告：`reports/research_progress_deep_review_2026-10-08_phase144.md`；程序：`src/analysis/audit_annotation_frame_release_identity.py`；机器结果：`outputs/phase144/annotation_frame_release_identity_audit.json`；输入摘要：`sources/track_a_pair_frame_input_inventory_2026-10-08_phase144.json`。

## Phase 145：Track A hypothesis 表层与分组设计审计

可复算核算了父 synset 多 lemma 的候选扩张：322 条资源 edge 展开成 680 个不同的 target-sense/surface claim；177 条 edge 有多 lemma。一个 lexicographic lemma/edge 虽将数量压回 322，却没有语义 canonicality。建议考虑 all-surface 候选并按 resource edge 成组，按 edge 汇总前先冻结 estimand/权重；新 manifest 需保留 parent synset/relation provenance。草案 leakage closure 279 个组件、最大 26 行，最终 split 要待 premise renderer 锁定后重算。本阶段没有生成 pair/labels，也未运行模型。详见Phase145。

## Phase 146：Track A contextual premise 契约影响审计

源码静态追踪发现 `/0.1` sidecar、候选 manifest `/0.2`、NLI export `/0.2` 与 source-only strict route 共用“premise 即 raw gloss”的 hash 不变量；当前 span 坐标、模型 export 与 proof source binding 都依赖它。现有 `group_id` 又同时用于 split 泄漏隔离和 calibration 独立单位，不能容纳 edge 下多个 lemma surface/context 行。需采用新版本拆分 source-gloss/rendered-premise hash、raw-gloss evidence spans、parent relation provenance、split component 与 statistical unit，并协调 validator/freezer/exporter/content-effect/gate/strict route。具体 condition gold 与 cluster calibration 仍待研究设计审议。本阶段仅为静态审计，无新代码运行、标注数据或效能主张。见Phase 146。

## Phase 147：Track A pair contract 设计选项

形成一个待审议的、未冻结的数据契约方案：target-context primary 与 gloss-only ablation 成对；parent lemma surface 独立作为 hypothesis；raw-gloss `semantic_support`、exact-context NLI 三分类及 resource relation 分开；拆 relation-edge、split-leakage group 和 statistical/calibration unit。按现有输入最多会有 1,360 pair-condition 行，双人标注可达 2,720 judgments。当前 NLI certified gate 的 one-row-per-IID-group 要求以及 verb hypothesis 语法均尚无适配实现。本阶段仅完成设计稿，未生成实验数据或结果。见[Phase147 设计稿](docs/track_a_pair_contract_design_options.md)。

## Phase 148：selected-witness bridge 版本漂移与当前重放

冻结目标 `oewn-00520548-n` 的结构证书和当前 checker 版本 bridge 通过复核：3,596 节点、14,923 条依赖边、3,512 条 ground Datalog rules。历史 Phase6 bridge 创建时验证通过，但 proof-result 当前重算对象因 checker 增加 `source_bindings` 与 `source_claim_refs` 而不再逐字段相等；历史 proof certificate 仍能验证，节点和边多重集匹配。新增审计器同时记录历史漂移和当前格式重放，避免把历史序列化差异误写成当前结构失败。该结论不涉及自然语言语义支持或新颖性。见Phase 148 报告。

## Phase 149：ACL 2026 gloss-conditioned 与逻辑审计工作补查

对两篇官方 ACL 2026 long papers 做框外定向筛读。G-IdiomAlign 已采用 gloss/no-gloss 对照与 embedding proxy；ReportLogic 已有专家人评的 report-level evidence sufficiency、warrant 和 claim-support rubric。因此不再把 gloss ablation 或一般 human-rated auditability 当作独立创新。固定 ACL v3 候选框未变；项目的 sense-bound source-span-to-typed-Horn-support 和 source-only replay 仍只是待验证假设，没有 matched baseline 或项目效果证据。筛读及边界见Phase 149 报告。


## Phase 150：COLM 2026 Q-CARE claim verifiability 邻接审查

官方接收目录确认 Q-CARE 为 COLM 2026 论文；定向核读确认其已做人标 atomic claim–retrieved chunk pairwise support benchmark（320 queries、7,907 claims、三人多数裁决），其自动 checker 是 LLM 判断而非逻辑证明。项目不再把一般 claim support/human verifiability 作为宽泛新意；sense-bound gloss-span→directional Horn literal support 与独立 proof replay 仍只是待证任务差异。Track A 合同四项选择未冻结，未生成候选或标签、未改 schema、未运行测试。证据见Phase 150 深度报告和[结构化筛读日志](sources/literature_screening_log_2026-10-08_colm2026_qcare_fulltext.json)。


## Phase 151：COLM 2026 grounded logic 与 judge 可靠性扩展筛读

按官方 COLM 接收目录的 targeted title terms 扩展 Q-CARE 后续筛查。全文核读 No Free Labels 与 LogicIF，摘要筛读 GraphWalker、GDP-RAG。新增核心边界：LLM correctness judge 依赖其求解能力与正确参考；code-executable gold + human-checked NL instruction fidelity 已有先例，但不能替代真实 gloss source-span support gold。两篇摘要级图/RAG 系统仅列邻接。无项目代码/数据复现、matched baseline、pair/label 或 schema migration；Track A 四项选择仍未冻结，项目效果/新颖性未证。详见Phase 151 深度报告与[结构化日志](sources/literature_screening_log_2026-10-08_colm2026_grounded_logic_addendum.json)。

## Phase 152：文献快照与 Track A 实现边界复核

当前 ACL v6 固定快照为 1,748 条，结构化日志 URL 命中 1,748；Phase142 的 `2026.acl-long.1468` 不在该候选框，LoReFact 和 LREC 2026 OEWN adjectival hypernym 资源则已有全文筛读。CodeGraph 初始化成功且索引最新（140 files、2,466 nodes、4,915 edges）。当前 NLI export/validator 调用图没有 contextual premise renderer；Track A 的语义 gold、context NLI gold、surface/edge/statistical unit 和 verb grammar 选择仍未冻结。为避免擅自改变研究 estimand，本阶段未改代码/schema、未生成 pair/label/split；无测试或模型运行。项目仍无真实 gloss-support gold、matched baseline、许可清权或有效性/新颖性证据。详情见Phase152 深度报告。

## Phase 153：Track A 研究设计裁决建议

在标注前把四项未决选择连到 estimand 和嵌套/校准结构：推荐以 raw-gloss span→relation edge/typed literal 支持作为主问题，把两种 exact premise 的 NLI gold 分开且列为次级上下文对照；全部 lemma surfaces 嵌套于 edge，target-sense 等权汇总并按 leakage component 作依赖区间；现有 IID calibration gate 不能直接服务全 surface frame，需 cluster-aware procedure 或降格为描述性结果；第一轮 noun-only，58 条 verb edges 独立预试。方案仍待研究者确认；未改代码/schema、未造候选和标注数据。见[设计备忘录](docs/track_a_design_decision_memo.md)与Phase153报告。

## Phase 154：分层 selective-risk 方法先例与校准 gate 假设审计

定向全文筛读 HG-CRC（arXiv 2026 preprint）：其层级化 simultaneous selective-risk control、Bonferroni node correction、leaf-first fallback 是新的相关方法先例；论文的严格 split variant 假设 IID calibration rows，层级 group membership 不是依赖 surface rows 的 cluster adjustment。项目代码复核确认离线 Wilson selector 是 exploratory，而 strict route 使用 fixed 101-grid exact-binomial/Bonferroni，并要求每个 dev `group_id` 一行；exporter/strict route 仍把 `group_id` 同时当作 split 与 calibration unit。不得靠重命名或分层 membership 掩盖多 surface/condition 依赖。未变更代码/schema/数据。详见[筛读日志](sources/literature_screening_log_2026-10-08_hierarchical_group_risk_control.json)、Phase154报告。

## Phase 155：多元 typed Horn 与显式目标变量缺口

静态审计确认 compiler v5 只支持共享单变量的一元正谓词，0.6 schema 虽保留 sort judgments 但未声明目标变量；必要/充分方向的多元安全性不同，不能直接扩大旧编译路径。此阶段只形成设计依据，未改代码或数据；已由 Phase156 实验性实现承接。见Phase155。

## Phase 156：schema 0.7 与多元 Horn compiler v6

实验性 `0.7-draft` 增加显式 `target_variable` 和 sort judgments；compiler v6 对正必要规则和充分方向 bounded DNF 分别实施目标变量安全约束，agreement analyzer 对齐 0.7。仅语法/配置静态检查；没有 runtime compiler 边界回放或真实 gold，0.7 未进入当前 v3 任务协议。详见Phase156。

## Phase 157：多元 source-only fact grounding 静态修复

source-only matcher 从一元限制扩至多元事实，并按 AST 变量/常量逐位 grounding、检查重复变量一致性和目标变量到 query target 的绑定；旧 unary 路径保留。pipeline 당시升至 `/12`。仅语法检查，没有 proof/countermodel/source-bundle 运行回放。详见Phase157。

## Phase 158：blind importer schema-version 选择

canonical importer 可选择 0.4–0.7 输出 schema，默认保持 0.4，最终仍由 canonical validator 拦截字段缺失。该变化没有生成 0.7 专属任务、呈现/回收材料或更新锁定 v3 batch。仅语法检查，未做 importer round-trip。详见Phase158。

## Phase 159：形式正确性、verifier 监督与内容效应先例

定向筛读 ACL Industry Track 的 T²、Findings ACL 的 FoVer 和 SemEval 2026 Task 11，分别记录 Lean 下游行为测试、verifier 产生 PRM 步骤监督并在 NLI 上评估、以及控制 syllogism plausibility/distractor/multilingual 的先例。它们都没有提供 WordNet gloss-span→typed Horn matched gold 或 baseline；单人三论文筛读，不是系统综述。详见Phase159。

## Phase 160：typed route 诊断可审计性

源码调用链显示 typed proof/countermodel replay 已对当前签名表做验证和哈希绑定；本阶段未发现无效 type table 可通过 replay 的证据。改进仅限输出：invalid typed program 在 pipeline 以 `unknown / invalid_typed_program` 报告，strict route 重算并呈现 typed validation，未提供 type system 时明确标为 `not_requested`；pipeline 版本升至 `/13`。只做语法和静态产物检查，未运行测试或真实 0.7 回放，不增加 soundness 或语义 gold 证据。详见Phase160。




## Phase 183 增量状态（2026-10-08）

已定向核读 COLM 2026 Quokka 并记录正式题名/预印本题名沿革、verifier correctness 与 downstream utility 的分离、unknown 状态和资源预算敏感结果。此项只更新相关工作与评测约束，不改变研究数据、schema、代码或 gold。核心研究目标尚未完成：仍需权利清晰、可审定的 sense/release-bound gloss-span gold、匹配基线、来源绑定 proof replay 的独立验证与论文级结果。见Phase183报告。

## Phase 184 增量状态（2026-10-08）

已在当前工作区重新运行冻结图与 minimum-depth witness 审计，输出与 Phase175 对应产物逐字节一致。图完整性与结构证书状态稳定；研究目标仍未完成，因为形式闭包/证书不证明 gloss 语义支持或来源许可，人工 source-support gold 与匹配语义基线仍缺。详见Phase184报告。

## Phase 223：外置 producer 代码边界与捕获 schema 修订

外置冻结 bundle 只含 graph reader；recovered-history 给出 `Wn2Lingua/KaikkiBasisHeldoutEvaluation` 管线描述，但不含 producer 实现 SHA，且记录引用的原始/准备输入均不在当前机器。结构报告显示 154,206/154,206 clauses 有 source-DNF evidence，parse errors 为 0，canonical replay 精确匹配 110,424/110,425 heads。因此结构证据可部分复核，原始生成程序和全量 canonical replay 不能声称已复现；也无 gloss semantic gold 或 clearance 新证据。同步发现并修复 Phase222 合同与 schema 的字段缺口：前向 schema 现在要求 producer、parser、normalizer 的实现哈希，并要求 validator 启用 `format` assertions。详见Phase223 报告、[机器审计](sources/source_producer_boundary_audit_2026-10-08_phase223.json)和[捕获合同](docs/source_evidence_capture_contract.md)。

## Phase 224：冻结 replay 单例差异现态复核

用既有冻结包例外审计器对当前外置 bundle 重跑，找到相同 1 个例外；semantic fingerprint、manifest/replay/index/rules 输入 SHA-256 和例外明细均与 Phase8 artifact 一致。`ext_wikt_full_dd659c7fcb3b` 的冻结 graph clause 与唯一 selected witness clause 匹配，depth=376，source-DNF evidence 标志为 true。此项确认冻结包内部例外声明现态稳定，不等同于上游 replay、witness 证明证书或 gloss 语义的独立验证；source payload 未打开。详见Phase224报告和[现态机器输出](outputs/phase224/frozen_bundle_replay_exceptions_current.json)。

## Phase 225：NeurIPS 2026 自动形式化与证明检索补筛

对官方 Downloads 索引新增四篇候选的定向全文章节审阅：教材到 Lean 大规模形式化、logic textbook theory-scale/LCS-Bench、global premise retrieval、Lean proof 多目标 refactoring。它们排除了若干宽泛创新主张，但均不提供 WordNet sense/release-bound gloss-span 对 typed Horn literal 支持的 matched baseline。官方 poster detail 页面未取到，track 仍标未核；目录为混合 event index，因此本轮不是系统综述。详见Phase225报告和[机器筛读日志](sources/literature_screening_log_2026-10-08_neurips2026_autoformalization_and_proof_graph_phase225.json)。

## Phase 226：relation-edge 跨层证据接口现态审计

OEWN resource verifier 与 proof/NLI strict route 各自具有局部可回放性，但没有共享 edge identity 或统一关联合同。已在[逻辑验证文档](docs/logic_verification.md)增加四类证据的证明范围、禁止互相替代的规则及未来 join 的最低身份字段。此为静态架构审计，没有语义实验；不改代码/schema，不代表 Track A 获准或已冻结。见Phase226报告与[机器记录](sources/evidence_layer_interface_audit_2026-10-08_phase226.json)。

## Phase 227：冻结 AND/OR 图的两两 basis deletion audit

新增 pairwise sensitivity analyzer 和方法说明，对 3,570 个 basis pair 使用批量位掩码传播重算精确闭包。1,102 对的 joint-only loss 非零，最大 pair 额外失活 3,700 个 head；全 pair 单调性、4 个直接 closure 核对和第二路径字节复跑通过。报告强调其只反映固定正 Horn 图的结构交互，不能解释为 gloss/source 语义。见Phase227深度报告、[实现](src/analysis/pairwise_basis_deletion_audit.py)、[方法文档](docs/pairwise_basis_deletion_interactions.md)、[机器结果](outputs/phase227/pairwise_basis_deletion_interactions.json)及[审计记录](sources/pairwise_basis_deletion_audit_2026-10-08_phase227.json)。

