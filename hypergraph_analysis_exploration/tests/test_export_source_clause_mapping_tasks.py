import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.export_annotation_batch import RELEASE_ARCHIVE_SHA256, RELEASE_DATE, RELEASE_NAME
from src.analysis.export_source_clause_mapping_tasks import build_tasks


class ExportSourceClauseMappingTasksTests(unittest.TestCase):
    def _fixture(self, root: Path):
        bundle = root / "bundle"
        (bundle / "graph").mkdir(parents=True)
        (bundle / "indexes").mkdir()
        source_relative = "sources/candidate.json"
        source_path = bundle / source_relative
        source_path.parent.mkdir()
        source = {
            "synset": {"synset_id": "oewn-private-sense", "raw_definition": "a small bird"},
            "definition": {
                "definition": "small bird",
                "parts": [{"part_id": "src-part-a", "text": "small"}, {"part_id": "src-part-b", "text": "bird"}],
                "logic": {"op": "OR", "args": [
                    {"op": "ATOM", "part_id": "src-part-a"},
                    {"op": "ATOM", "part_id": "src-part-b"},
                ]},
            },
        }
        source_bytes = json.dumps(source).encode("utf-8")
        source_path.write_bytes(source_bytes)
        sense_id = "oewn-private-sense"
        rules_path = bundle / "graph" / "hypergraph_rules.jsonl"
        rules_path.write_text(json.dumps({
            "head": sense_id,
            "clauses": [["oewn-private-literal-a"], ["oewn-private-literal-b"]],
        }) + "\n", encoding="utf-8")
        graph_hash = hashlib.sha256(rules_path.read_bytes()).hexdigest()
        (bundle / "manifest.json").write_text(json.dumps({"graph_sha256": graph_hash}), encoding="utf-8")
        (bundle / "indexes" / "senses.jsonl").write_text(json.dumps({
            "identity": sense_id,
            "active_clause_sources": [
                {"clause_index": 0, "source_documents": [source_relative]},
                {"clause_index": 1, "source_documents": [source_relative]},
            ],
        }) + "\n", encoding="utf-8")
        (bundle / "graph" / "nodes.tsv").write_text(
            "synset_id\tlemmas\tpos\tdefinition\tsource_root\tclause_count\tis_basis\tis_cycle_candidate\n"
            "oewn-private-literal-a\tsmall\ta\tsmall concept\troot\t1\tFalse\tFalse\n"
            "oewn-private-literal-b\tbird\tn\tbird concept\troot\t1\tFalse\tFalse\n",
            encoding="utf-8",
        )
        frame_path = root / "frame.jsonl"
        frame_path.write_text(json.dumps({
            "sense_id": sense_id,
            "pos": "n",
            "lemmas": ["demo"],
            "panel": "diagnostic_not_for_population_estimates",
            "random_seed": 31,
            "source_records": [{"path": source_relative, "sha256": hashlib.sha256(source_bytes).hexdigest()}],
        }) + "\n", encoding="utf-8")
        release_batch_path = root / "release_batch.jsonl"
        release_batch_path.write_text(json.dumps({"task_id": "WN-0001", "gloss": "a small bird"}) + "\n", encoding="utf-8")
        release_key_path = root / "release_key.json"
        release_key_path.write_text(json.dumps([{"task_id": "WN-0001", "sense_id": sense_id}]), encoding="utf-8")
        release_manifest_path = root / "release_manifest.json"
        release_manifest_path.write_text(json.dumps({
            "batch_version": "oewn-blind-annotation-batch/1",
            "candidate_count": 1,
            "source_release": RELEASE_NAME,
            "source_release_date": RELEASE_DATE,
            "source_release_archive_sha256": RELEASE_ARCHIVE_SHA256,
            "frame_sha256": hashlib.sha256(frame_path.read_bytes()).hexdigest(),
            "batch_sha256": hashlib.sha256(release_batch_path.read_bytes()).hexdigest(),
            "answer_key_sha256": hashlib.sha256(release_key_path.read_bytes()).hexdigest(),
        }), encoding="utf-8")
        return frame_path, bundle, release_batch_path, release_key_path, release_manifest_path

    def test_exports_anonymized_active_clause_tasks_deterministically(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self._fixture(Path(directory))
            tasks, key, manifest = build_tasks(*args)
            repeated_tasks, repeated_key, _ = build_tasks(*args)
            self.assertEqual(tasks, repeated_tasks)
            self.assertEqual(key, repeated_key)
            self.assertEqual(len(tasks), 2)
            self.assertEqual(manifest["active_source_record_count"], 1)
            self.assertEqual(manifest["active_sources_excluded_for_nonmatching_official_raw_gloss"], 0)
            serialized = json.dumps(tasks)
            for hidden in ("oewn-private-sense", "oewn-private-literal", "sources/candidate.json", "diagnostic_not_for_population_estimates"):
                self.assertNotIn(hidden, serialized)
            self.assertEqual({row["task_id"] for row in tasks}, {row["task_id"] for row in key})
            self.assertEqual(tasks[0]["schema_version"], "source-clause-alignment-task/0.1")
            self.assertIn("internal only", manifest["distribution_status"])

    def test_rejects_hash_or_release_provenance_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            args = list(self._fixture(Path(directory)))
            manifest_path = args[-1]
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["batch_sha256"] = "0" * 64
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "blind-batch hash"):
                build_tasks(*args)


if __name__ == "__main__":
    unittest.main()
