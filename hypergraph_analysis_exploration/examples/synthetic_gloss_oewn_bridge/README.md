# Synthetic gloss–OEWN bridge wiring fixture

**Every file in this directory is synthetic engineering data. It contains no WordNet gloss and no human annotation. Do not use it as lexical evidence, semantic gold, or an accuracy sample.**

The first candidate's `sense_id` and query pair reuse one real OEWN edge only so the verifier can demonstrate the byte-bound producer → replay v3 → bridge route. The second candidate has an `unassessed` genus mapping and no resource query. Both premises are the literal sentinel `SYNTHETIC FIXTURE ONLY - NOT A WORDNET GLOSS`; `adjudicator_id` is `SYNTHETIC_FIXTURE_NOT_HUMAN`. The first bridge row's `adjudicated` status is a required synthetic input state, not a claim that a person performed adjudication.

## Captured result

- `validation_report.json`: both synthetic candidates pass exact manifest/sidecar/bridge denominator checks. One resource query passes candidate hash, release, query, producer-report, and replay-report bindings as `direct_hypernym`; the second unresolved candidate remains in the output denominator with `resource_relation_status: null`.
- `validation_report_bad_pin.json`: the same run with an all-zero candidate-manifest pin fails closed with a manifest hash mismatch.
- `validation_report_missing_candidate.json`: omitting the unassessed row fails the exact bridge-candidate denominator check.
- `candidate_manifest.json` SHA-256 (the explicit fixture pin): `2bb658ae721ea50aa8c2d1d2376b7dff2959987f9f9af88e428ec0869f93e7df`.
- Both `claim_review.jsonl` rows remain NLI-unassessed and semantic-support-unassessed. The resource result does not upgrade either label.

## Phase271: validator 0.3 replay

The historical Phase119 reports above were produced with validator 0.2. Phase271 reran the synthetic producer → independent replay v3 → bridge validator 0.3 in [`outputs/phase271/synthetic_bridge_replay/`](../../outputs/phase271/synthetic_bridge_replay/) and repeated the run in a second output directory. The verifier, replay, and bridge report SHA-256 values matched byte-for-byte across the two runs. The current bridge output retains both rows (`adjudicated` synthetic mapping → `direct_hypernym`; `unassessed` → `null`). A bad external manifest pin and an omitted unresolved candidate each failed closed. A third control changed the query pair, generated a matching producer/replay and updated report pins, then confirmed the bridge still rejects the mismatch between the query row and bridge row; its artifacts are under [`outputs/phase271/query_row_mismatch/`](../../outputs/phase271/query_row_mismatch/). See the Phase271 deep review and [machine audit](../../sources/phase271_bridge_replay_audit_2026-10-08.json).

## Reproduce producer → replay → bridge

Run from the project root. Outputs go to a fresh temporary directory so the captured fixture remains unchanged:

```powershell
$runDir = "tmp/phase119_synthetic_bridge_run"
New-Item -ItemType Directory -Path $runDir

python -m src.analysis.oewn_hypernym_verifier `
  examples/synthetic_gloss_oewn_bridge/queries.jsonl `
  --output "$runDir/verifier_report.json"

python -m src.analysis.verify_oewn_hypernym_certificates `
  "$runDir/verifier_report.json" `
  examples/synthetic_gloss_oewn_bridge/queries.jsonl `
  --output "$runDir/replay_v3.json"

python -m src.analysis.verify_gloss_oewn_relation_links `
  examples/synthetic_gloss_oewn_bridge/links.jsonl `
  examples/synthetic_gloss_oewn_bridge/claim_review.jsonl `
  examples/synthetic_gloss_oewn_bridge/candidate_manifest.json `
  --candidate-manifest-sha256 2bb658ae721ea50aa8c2d1d2376b7dff2959987f9f9af88e428ec0869f93e7df `
  --expected-release-name "Open English WordNet 2025 Plus" `
  --expected-release-archive-sha256 8832b8fa26a14c0ba8c99bb1ef8db6f9e122a6d9193b65ca9e0ef572580fee7e `
  --queries examples/synthetic_gloss_oewn_bridge/queries.jsonl `
  --verifier-report "$runDir/verifier_report.json" `
  --replay-report "$runDir/replay_v3.json" `
  --output "$runDir/validation_report.json"
```

The default local OEWN release directory/archive must be available under `tmp/oewn-2025-plus-json/` and `tmp/oewn-2025-plus-json.zip`. The manifest pin above is only a fixture pin. A real study needs an independently fixed candidate-manifest hash and authorized, blind-reviewed mapping inputs. This fixture validates software wiring and fail-closed hash binding only; it does not establish that any gloss supports any relation.
