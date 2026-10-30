import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.audit_preposition_source_provenance import summarize_bundle


class PrepositionSourceProvenanceAuditTests(unittest.TestCase):
    def test_aggregates_scoped_records_without_emitting_raw_content_or_locators(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle = Path(temp)
            (bundle / "indexes").mkdir()
            source_dir = bundle / "sources/Synset/alternative_or_definition_wsd_frozen"
            other_dir = bundle / "sources/Synset/other_pipeline"
            source_dir.mkdir(parents=True)
            other_dir.mkdir(parents=True)
            records = [
                {
                    "source_record": {
                        "alternative_definition_provenance": {
                            "source_evidence": [{
                                "source": "fixture-dictionary",
                                "source_version": "v1",
                                "source_locator": "secret-locator",
                                "download_url": "https://example.invalid/private",
                                "definition_text_sha256": "a" * 64,
                                "definition": "must not appear",
                            }]
                        }
                    },
                    "definition": {"text": "must not appear either"},
                },
                {"source_record": {"alternative_definition_provenance": {}}},
            ]
            paths = []
            for index, payload in enumerate(records):
                rel = f"sources/Synset/alternative_or_definition_wsd_frozen/record-{index}.json"
                (bundle / rel).write_text(json.dumps(payload), encoding="utf-8")
                paths.append(rel)
            other_rel = "sources/Synset/other_pipeline/record.json"
            (bundle / other_rel).write_text("{}", encoding="utf-8")
            paths.append(other_rel)
            (bundle / "indexes/source_records.jsonl").write_text(
                "\n".join(json.dumps({"path": rel}) for rel in paths) + "\n", encoding="utf-8"
            )

            result = summarize_bundle(bundle)

        self.assertEqual(result["summary"]["indexed_records"], 2)
        self.assertEqual(result["summary"]["payloads_read"], 2)
        self.assertEqual(result["summary"]["records_with_source_evidence"], 1)
        self.assertEqual(result["summary"]["records_without_evidence_list"], 1)
        self.assertEqual(result["summary"]["evidence_items"], 1)
        self.assertEqual(result["summary"]["unique_exact_source_labels"], 1)
        self.assertEqual(result["summary"]["records_with_license_field_in_evidence"], 0)
        self.assertEqual(len(result["inputs_sha256"]["source_records_index"]), 64)
        self.assertEqual(len(result["inputs_sha256"]["scoped_payload_set"]), 64)
        rendered = json.dumps(result, ensure_ascii=False)
        for forbidden in ("secret-locator", "example.invalid", "must not appear"):
            self.assertNotIn(forbidden, rendered)

    def test_reports_missing_payload_as_error_without_exposing_path(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle = Path(temp)
            (bundle / "indexes").mkdir()
            (bundle / "indexes/source_records.jsonl").write_text(
                json.dumps({"path": "sources/Synset/alternative_or_definition_wsd_frozen/missing.json"}) + "\n",
                encoding="utf-8",
            )
            result = summarize_bundle(bundle)

        self.assertEqual(result["summary"]["payload_errors"], 1)
        self.assertNotIn("missing.json", json.dumps(result))


if __name__ == "__main__":
    unittest.main()
