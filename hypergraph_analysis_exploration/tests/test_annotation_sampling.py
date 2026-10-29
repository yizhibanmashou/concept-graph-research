import hashlib
import json
import random
import tempfile
import unittest
from pathlib import Path

from src.analysis.annotation_sampling import _apportion, _choose_diagnostic_panel, build_frame, write_frame_outputs


GRAPH_VERSION = "alternative_or_definition_wsd_complete_hypergraph_after_basis85_law_complete_or"


class AnnotationSamplingTests(unittest.TestCase):
    def test_apportion_preserves_total_and_respects_capacities(self):
        allocation = _apportion(5, {"a": 1, "b": 10, "c": 10})
        self.assertEqual(sum(allocation.values()), 5)
        self.assertLessEqual(allocation["a"], 1)
        self.assertEqual(allocation, _apportion(5, {"a": 1, "b": 10, "c": 10}))

    def test_apportion_covers_each_nonempty_stratum_when_feasible(self):
        allocation = _apportion(4, {"rare_a": 1, "rare_b": 2, "large": 20, "empty": 0})
        self.assertEqual(sum(allocation.values()), 4)
        self.assertGreater(allocation["rare_a"], 0)
        self.assertGreater(allocation["rare_b"], 0)
        self.assertEqual(allocation["empty"], 0)

    def test_diagnostic_panel_separates_or_width_and_depth_cases(self):
        population = []
        for index in range(30):
            population.append({
                "sense_id": str(index),
                "has_alternative_clauses": index < 15,
                "max_clause_width": 20 if 15 <= index < 22 else 1,
                "selected_witness_depth": 100 if index >= 22 else 1,
            })
        selected, threshold = _choose_diagnostic_panel(population, set(), 10, random.Random(9))
        self.assertEqual(len(selected), 10)
        self.assertEqual(threshold, {"max_clause_width_p90": 20, "selected_witness_depth_p90": 100})
        self.assertEqual(sum(row["diagnostic_reason"] == "multiple_OR_clauses" for row in selected), 4)
        self.assertEqual(sum(row["diagnostic_reason"].startswith("high_max_clause_width") for row in selected), 3)
        self.assertEqual(sum(row["diagnostic_reason"].startswith("high_selected_witness_depth") for row in selected), 3)
        self.assertEqual(len({row["sense_id"] for row in selected}), len(selected))

    def test_frame_is_reproducible_and_contains_no_gloss_text(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory)
            (bundle / "graph").mkdir()
            (bundle / "indexes").mkdir()
            (bundle / "sources" / "Synset").mkdir(parents=True)
            (bundle / "manifest.json").write_text(json.dumps({
                "graph_version": GRAPH_VERSION,
                "graph_sha256": "b" * 64,
                "semantic_fingerprint_sha256": "c" * 64,
                "head_count": 3,
                "clause_count": 3,
            }), encoding="utf-8")
            (bundle / "graph" / "nodes.tsv").write_text(
                "synset_id\tlemmas\tpos\tdefinition\tsource_root\tclause_count\tis_basis\tis_cycle_candidate\n"
                "oewn-00000001-n\tone\tn\ta gloss alpha\tsource-a\t1\tFalse\tFalse\n"
                "oewn-00000002-n\ttwo\tn\ta gloss beta\tsource-b\t1\tFalse\tFalse\n"
                "oewn-00000003-v\tthree\tv\ta gloss gamma\tsource-c\t1\tFalse\tFalse\n"
                "ext-00000004-n\tfour\tn\texternal gloss\texternal\t1\tFalse\tFalse\n",
                encoding="utf-8",
            )
            ids = ["oewn-00000001-n", "oewn-00000002-n", "oewn-00000003-v"]
            (bundle / "graph" / "hypergraph_rules.jsonl").write_text("".join(
                json.dumps({"head": sense_id, "clauses": [["basis"]]}) + "\n" for sense_id in ids
            ), encoding="utf-8")
            (bundle / "graph" / "coverage_witnesses.jsonl").write_text("".join(
                json.dumps({"head": sense_id, "is_seed": False, "proof_depth": index + 1,
                            "witness_clause": ["basis"]}) + "\n"
                for index, sense_id in enumerate(ids)
            ), encoding="utf-8")
            index_rows = []
            for index, sense_id in enumerate(ids):
                relative = f"sources/Synset/{sense_id}.json"
                (bundle / relative).write_text(json.dumps({"source": index}), encoding="utf-8")
                lemma = ["one", "two", "three"][index]
                index_rows.append({
                    "identity": sense_id,
                    "lemmas": lemma,
                    "source_records": [{"identity": sense_id, "lemmas": [lemma], "path": relative}],
                })
            (bundle / "indexes" / "senses.jsonl").write_text("".join(
                json.dumps(row) + "\n" for row in index_rows
            ), encoding="utf-8")

            frame_a, summary_a = build_frame(bundle, random_size=2, diagnostic_size=0, seed=7)
            frame_b, summary_b = build_frame(bundle, random_size=2, diagnostic_size=0, seed=7)
            self.assertEqual(frame_a, frame_b)
            self.assertEqual(summary_a, summary_b)
            self.assertEqual(len(frame_a), 2)
            self.assertIn("random_panel_strata", summary_a)
            self.assertFalse(frame_a[0]["annotator_visible"])
            self.assertEqual(summary_a["sampling_policy_version"], "oewn-annotation-candidate/2")
            self.assertEqual(frame_a[0]["frame_version"], "oewn-annotation-candidate/2")
            self.assertEqual(frame_a[0]["structural_features"]["selected_witness_width"], 1)
            self.assertIn("selected_witness_depth", frame_a[0]["structural_features"])
            self.assertIn("selected_witness_fanout", frame_a[0]["structural_features"])
            serialized = json.dumps(frame_a)
            for gloss in ("a gloss alpha", "a gloss beta", "a gloss gamma"):
                self.assertNotIn(gloss, serialized)
            self.assertTrue(all(row["license_review"].startswith("pending") for row in frame_a))
            frame_path = bundle / "candidate-frame.jsonl"
            manifest_path = bundle / "candidate-manifest.json"
            written_summary = write_frame_outputs(frame_a, summary_a, frame_path, manifest_path)
            self.assertEqual(written_summary["candidate_count"], len(frame_a))
            self.assertEqual(
                written_summary["frame_sha256"],
                hashlib.sha256(frame_path.read_bytes()).hexdigest(),
            )
            self.assertEqual(json.loads(manifest_path.read_text(encoding="utf-8")), written_summary)


if __name__ == "__main__":
    unittest.main()
