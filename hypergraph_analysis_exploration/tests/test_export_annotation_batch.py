import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.export_annotation_batch import build_batch, write_batch_outputs


class ExportAnnotationBatchTests(unittest.TestCase):
    def _fixture(self, root: Path):
        bundle = root / "bundle"
        release = root / "release"
        bundle.mkdir()
        release.mkdir()
        candidates = [
            ("oewn-00000001-n", "a small bird", ["bird"], "random_stratified"),
            ("oewn-00000002-n", "a flying creature", ["flyer"], "diagnostic_not_for_population_estimates"),
        ]
        frame_rows = []
        release_records = {}
        source_rows = []
        for sense_id, gloss, lemmas, panel in candidates:
            source_name = f"{sense_id}.json"
            source_path = bundle / source_name
            source_path.write_text(json.dumps({
                "synset": {"synset_id": sense_id, "raw_definition": gloss, "lemmas": lemmas},
            }), encoding="utf-8")
            source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
            frame_rows.append({
                "sense_id": sense_id,
                "item_id": f"graph:{sense_id}",
                "lemmas": lemmas,
                "pos": "n",
                "panel": panel,
                "stratum": "hidden-stratum",
                "random_seed": 99,
                "structural_features": {
                    "clause_count": 3,
                    "max_clause_width": 5,
                    "selected_witness_depth": 12,
                    "selected_witness_width": 2,
                    "selected_witness_fanout": 7,
                },
                "source_records": [{"path": source_name, "sha256": source_hash}],
            })
            source_rows.append({
                "sense_id": sense_id,
                "raw_gloss_exact_match": True,
                "raw_gloss_normalized_match": True,
                "effective_gloss_exact_match": panel == "random_stratified",
                "effective_gloss_normalized_match": panel == "random_stratified",
                "source_record_comparisons": [{
                    "source_payload_sha256": source_hash,
                    "source_raw_gloss_present": True,
                    "source_raw_gloss_length_codepoints": len(gloss),
                    "source_effective_gloss_present": True,
                    "source_effective_gloss_length_codepoints": len(gloss),
                    "raw_gloss_exact_match": True,
                    "raw_gloss_normalized_match": True,
                    "effective_gloss_exact_match": panel == "random_stratified",
                    "effective_gloss_normalized_match": panel == "random_stratified",
                    "raw_equals_effective": True,
                }],
            })
            release_records[sense_id.removeprefix("oewn-")] = {"definition": gloss}
        frame = root / "frame.jsonl"
        frame.write_text("".join(json.dumps(row) + "\n" for row in frame_rows), encoding="utf-8")
        (release / "noun.fixture.json").write_text(json.dumps(release_records), encoding="utf-8")
        crosscheck = root / "crosscheck.json"
        crosscheck.write_text(json.dumps({
            "release_name": "Open English WordNet 2025 Plus",
            "release_date": "2025-12-31",
            "official_download_uri": "https://en-word.net/static/english-wordnet-2025-plus-json.zip",
            "release_archive_sha256": "8832b8fa26a14c0ba8c99bb1ef8db6f9e122a6d9193b65ca9e0ef572580fee7e",
            "frame_sha256": hashlib.sha256(frame.read_bytes()).hexdigest(),
            "raw_gloss_text_emitted": False,
            "candidate_sense_count": len(candidates),
            "overall": {
                "sense_count": len(candidates),
                "official_release_synset_found": len(candidates),
                "exact_raw_gloss_match": len(candidates),
            },
            "per_sense": source_rows,
        }), encoding="utf-8")
        return frame, bundle, release, crosscheck

    def test_blinded_batch_is_deterministic_and_separates_answer_key(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = self._fixture(Path(directory))
            batch, key, manifest = build_batch(*paths)
            repeated_batch, repeated_key, _ = build_batch(*paths)
            self.assertEqual(batch, repeated_batch)
            self.assertEqual(key, repeated_key)
            self.assertEqual(len(batch), 2)
            self.assertEqual({row["task_id"] for row in batch}, {row["task_id"] for row in key})
            self.assertEqual(set(batch[0]), {"task_id", "pos", "lemmas", "gloss"})
            self.assertNotIn("sense_id", json.dumps(batch))
            self.assertNotIn("stratum", json.dumps(batch))
            self.assertNotIn("source_records", json.dumps(batch))
            self.assertNotIn("selected_witness_depth", json.dumps(batch))
            self.assertNotIn("selected_witness_fanout", json.dumps(batch))
            self.assertEqual(key[0]["graph_structural_features"]["selected_witness_depth"], 12)
            self.assertEqual(key[0]["graph_structural_features"]["selected_witness_fanout"], 7)
            self.assertEqual(key[0]["release_comparison"]["source_record_details_status"], "present")
            self.assertIn("source_record_details", json.dumps(key[0]["release_comparison"]))
            self.assertNotIn("release_comparison", json.dumps(batch))
            self.assertIn("release_comparison", manifest["withheld_from_annotators"])
            self.assertIn("CC BY 4.0", manifest["license"])
            self.assertIn("Princeton", manifest["copyright_notice"])
            self.assertIn("retained verbatim", manifest["modification_notice"])
            self.assertEqual(len({row["sense_id"] for row in key}), 2)

    def test_rejects_crosscheck_for_a_different_frame(self):
        with tempfile.TemporaryDirectory() as directory:
            frame, bundle, release, crosscheck = self._fixture(Path(directory))
            with frame.open("a", encoding="utf-8") as stream:
                stream.write("\n")
            with self.assertRaisesRegex(ValueError, "different annotation frame"):
                build_batch(frame, bundle, release, crosscheck)

    def test_rejects_source_text_that_does_not_match_official_release(self):
        with tempfile.TemporaryDirectory() as directory:
            frame, bundle, release, crosscheck = self._fixture(Path(directory))
            source = bundle / "oewn-00000001-n.json"
            source_doc = json.loads(source.read_text(encoding="utf-8"))
            source_doc["synset"]["raw_definition"] = "modified text"
            source.write_text(json.dumps(source_doc), encoding="utf-8")
            frame_rows = [json.loads(line) for line in frame.read_text(encoding="utf-8").splitlines()]
            frame_rows[0]["source_records"][0]["sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
            frame.write_text("".join(json.dumps(row) + "\n" for row in frame_rows), encoding="utf-8")
            report = json.loads(crosscheck.read_text(encoding="utf-8"))
            report["frame_sha256"] = hashlib.sha256(frame.read_bytes()).hexdigest()
            crosscheck.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "raw gloss does not match"):
                build_batch(frame, bundle, release, crosscheck)

    def test_rejects_source_release_evidence_for_a_different_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            frame, bundle, release, crosscheck = self._fixture(Path(directory))
            report = json.loads(crosscheck.read_text(encoding="utf-8"))
            report["per_sense"][0]["source_record_comparisons"][0]["source_payload_sha256"] = "0" * 64
            crosscheck.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "source release comparisons do not match frame records"):
                build_batch(frame, bundle, release, crosscheck)

    def test_written_hashes_match_files_on_disk(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = self._fixture(root)
            batch, key, manifest = build_batch(*paths)
            batch_path = root / "out" / "batch.jsonl"
            key_path = root / "out" / "answer-key.json"
            manifest_path = root / "out" / "manifest.json"
            written_manifest = write_batch_outputs(batch, key, manifest, batch_path, key_path, manifest_path)
            self.assertEqual(written_manifest["batch_sha256"], hashlib.sha256(batch_path.read_bytes()).hexdigest())
            self.assertEqual(written_manifest["answer_key_sha256"], hashlib.sha256(key_path.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
