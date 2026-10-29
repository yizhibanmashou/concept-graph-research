import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.export_annotation_batch import build_batch, write_batch_outputs
from src.analysis.import_annotation_returns import build_canonical_records, write_records


class ImportAnnotationReturnsTests(unittest.TestCase):
    def _fixture(self, root: Path):
        bundle = root / "bundle"
        release = root / "release"
        bundle.mkdir()
        release.mkdir()
        sense_id = "oewn-00000001-n"
        gloss = "a small bird"
        source = bundle / "source.json"
        source.write_text(json.dumps({
            "synset": {"synset_id": sense_id, "raw_definition": gloss},
        }), encoding="utf-8")
        source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        frame = root / "frame.jsonl"
        frame.write_text(json.dumps({
            "sense_id": sense_id,
            "item_id": "frozen-graph:oewn-00000001-n",
            "lemmas": ["bird"],
            "pos": "n",
            "panel": "random_stratified",
            "stratum": "hidden",
            "random_seed": 7,
            "structural_features": {"selected_witness_depth": 23, "selected_witness_fanout": 4},
            "source_records": [{"path": "source.json", "sha256": source_hash}],
        }) + "\n", encoding="utf-8")
        (release / "noun.fixture.json").write_text(json.dumps({
            "00000001-n": {"definition": gloss},
        }), encoding="utf-8")
        crosscheck = root / "crosscheck.json"
        crosscheck.write_text(json.dumps({
            "release_name": "Open English WordNet 2025 Plus",
            "release_date": "2025-12-31",
            "official_download_uri": "https://en-word.net/static/english-wordnet-2025-plus-json.zip",
            "release_archive_sha256": "8832b8fa26a14c0ba8c99bb1ef8db6f9e122a6d9193b65ca9e0ef572580fee7e",
            "frame_sha256": hashlib.sha256(frame.read_bytes()).hexdigest(),
            "raw_gloss_text_emitted": False,
            "candidate_sense_count": 1,
            "overall": {"sense_count": 1, "official_release_synset_found": 1, "exact_raw_gloss_match": 1},
            "per_sense": [{
                "sense_id": sense_id,
                "raw_gloss_exact_match": True,
                "raw_gloss_normalized_match": True,
                "effective_gloss_exact_match": False,
                "effective_gloss_normalized_match": False,
                "source_record_comparisons": [{
                    "source_payload_sha256": source_hash,
                    "source_raw_gloss_present": True,
                    "source_raw_gloss_length_codepoints": len(gloss),
                    "source_effective_gloss_present": True,
                    "source_effective_gloss_length_codepoints": 0,
                    "raw_gloss_exact_match": True,
                    "raw_gloss_normalized_match": True,
                    "effective_gloss_exact_match": False,
                    "effective_gloss_normalized_match": False,
                    "raw_equals_effective": False,
                }],
            }],
        }), encoding="utf-8")
        batch, key, manifest = build_batch(frame, bundle, release, crosscheck)
        batch_path = root / "blind.jsonl"
        key_path = root / "key.json"
        manifest_path = root / "manifest.json"
        write_batch_outputs(batch, key, manifest, batch_path, key_path, manifest_path)
        return batch_path, key_path, manifest_path, root

    @staticmethod
    def _return(task_id: str, status: str = "needs_review"):
        return {
            "task_id": task_id,
            "annotator_id": "rater-a",
            "analysis": {
                "status": status,
                "nodes": [{
                    "id": "unknown-1",
                    "kind": "unknown",
                    "reason": "insufficient information for a stable parse",
                    "span": {"start": 0, "end": len("a small bird")},
                }],
                "root_node_ids": ["unknown-1"],
                "rule_claims": [],
                "horn_projection": {"status": "not_attempted", "rule_ids": [], "omissions": []},
            },
            "notes": [],
        }

    def test_import_round_trip_restores_identity_and_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            batch_path, key_path, manifest_path, root = self._fixture(Path(directory))
            batch = [json.loads(line) for line in batch_path.read_text(encoding="utf-8").splitlines()]
            returned = root / "returned.jsonl"
            returned.write_text(json.dumps(self._return(batch[0]["task_id"])) + "\n", encoding="utf-8")

            records = build_canonical_records(returned, batch_path, key_path, manifest_path)

            self.assertEqual(len(records), 1)
            record = records[0]
            self.assertEqual(record["sense"]["synset_id"], "oewn-00000001-n")
            self.assertEqual(record["sense"]["gloss"], "a small bird")
            self.assertEqual(record["annotation"]["adjudication_status"], "independent")
            self.assertEqual(record["split"], "unassigned")
            self.assertEqual(record["provenance"]["sampling_panel"], "random_stratified")
            self.assertEqual(record["provenance"]["graph_structural_features"], {
                "selected_witness_depth": 23,
                "selected_witness_fanout": 4,
            })
            self.assertEqual(
                record["provenance"]["release_comparison"]["source_record_details"][0]
                ["effective_gloss_exact_match"],
                False,
            )

    def test_rejects_duplicate_unknown_or_missing_tasks(self):
        with tempfile.TemporaryDirectory() as directory:
            batch_path, key_path, manifest_path, root = self._fixture(Path(directory))
            task_id = json.loads(batch_path.read_text(encoding="utf-8").splitlines()[0])["task_id"]
            returned = root / "returned.jsonl"
            row = self._return(task_id)
            returned.write_text(json.dumps(row) + "\n" + json.dumps(row) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate returned task_id"):
                build_canonical_records(returned, batch_path, key_path, manifest_path)

            returned.write_text(json.dumps(self._return("WN-9999")) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unknown task_id"):
                build_canonical_records(returned, batch_path, key_path, manifest_path)

            returned.write_text("", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "return JSONL is empty"):
                build_canonical_records(returned, batch_path, key_path, manifest_path)

    def test_rejects_manifest_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            batch_path, key_path, manifest_path, root = self._fixture(Path(directory))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["batch_sha256"] = "0" * 64
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            returned = root / "returned.jsonl"
            task_id = json.loads(batch_path.read_text(encoding="utf-8").splitlines()[0])["task_id"]
            returned.write_text(json.dumps(self._return(task_id)) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "blind batch hash"):
                build_canonical_records(returned, batch_path, key_path, manifest_path)

    def test_write_records_is_hashable_and_refuses_implicit_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            batch_path, key_path, manifest_path, root = self._fixture(Path(directory))
            task_id = json.loads(batch_path.read_text(encoding="utf-8").splitlines()[0])["task_id"]
            returned = root / "returned.jsonl"
            returned.write_text(json.dumps(self._return(task_id)) + "\n", encoding="utf-8")
            records = build_canonical_records(returned, batch_path, key_path, manifest_path)
            output = root / "canonical.jsonl"
            digest = write_records(records, output)
            self.assertEqual(digest, hashlib.sha256(output.read_bytes()).hexdigest())
            with self.assertRaises(FileExistsError):
                write_records(records, output)


if __name__ == "__main__":
    unittest.main()
