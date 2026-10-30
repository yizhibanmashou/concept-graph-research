import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.audit_t02_targeted_source_metadata import summarize_bundle


class TargetedSourceMetadataTests(unittest.TestCase):
    def test_reports_categories_without_private_values(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle = Path(temp)
            rel = "sources/Synset/alternative_or_definition_wsd_frozen/item.json"
            payload = {
                "source_record": {
                    "alternative_definition_provenance": {
                        "source_evidence": [
                            {
                                "source": "Kaikki/Wiktextract targeted OEWN gap",
                                "source_version": "raw-sha256:" + "a" * 64,
                                "definition_text_sha256": "a" * 64,
                                "source_locator": "https://example.org/private/path?secret=do-not-print",
                                "source_ontology": "https://ontology.example/private/item",
                                "evidence_type": "definition_match",
                                "external_id": "private-sense-id",
                            },
                            {
                                "source": "Kaikki/Wiktextract relaxed definition-term fallback",
                                "source_version": "raw-sha256:" + "a" * 64,
                                "definition_text_sha256": "b" * 64,
                                "source_locator": "private-locator",
                                "evidence_type": "term_match",
                            },
                        ]
                    }
                },
                "definition": "private definition text",
            }
            path = bundle / rel
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(payload), encoding="utf-8")
            index = bundle / "indexes" / "source_records.jsonl"
            index.parent.mkdir()
            index.write_text(json.dumps({"path": rel}) + "\n", encoding="utf-8")

            report = summarize_bundle(bundle)
            rendered = json.dumps(report, ensure_ascii=False)

            self.assertEqual(report["summary"]["target_evidence_items"], 2)
            targeted = report["labels"]["Kaikki/Wiktextract targeted OEWN gap"]
            self.assertEqual(targeted["version_shape"], {"raw_sha256_fingerprint": 1})
            self.assertEqual(targeted["unique_source_version_fingerprints"], 1)
            self.assertEqual(targeted["definition_hash_valid"], 1)
            self.assertEqual(targeted["source_version_equals_definition_hash"], 1)
            self.assertTrue(report["target_labels_share_source_version_fingerprint"])
            self.assertEqual(targeted["locator_host"], {"example.org": 1})
            self.assertEqual(targeted["evidence_type"], {"definition_match": 1})
            for secret in ("private definition text", "private-sense-id", "private/path", "secret=", "private-locator", "a" * 64):
                self.assertNotIn(secret, rendered)

    def test_raw_sha256_fingerprint_does_not_imply_definition_hash_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle = Path(temp)
            rel = "sources/Synset/alternative_or_definition_wsd_frozen/item.json"
            payload = {"source_record": {"alternative_definition_provenance": {"source_evidence": [{
                "source": "Kaikki/Wiktextract relaxed definition-term fallback",
                "source_version": "raw-sha256:" + "b" * 64,
                "definition_text_sha256": "c" * 64,
            }]}}}
            path = bundle / rel
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(payload), encoding="utf-8")
            index = bundle / "indexes" / "source_records.jsonl"
            index.parent.mkdir()
            index.write_text(json.dumps({"path": rel}) + "\n", encoding="utf-8")

            report = summarize_bundle(bundle)
            fallback = report["labels"]["Kaikki/Wiktextract relaxed definition-term fallback"]

            self.assertEqual(fallback["source_version_equals_definition_hash"], 0)
            self.assertFalse(report["target_labels_share_source_version_fingerprint"])
            self.assertNotIn("b" * 64, json.dumps(report))

    def test_unlisted_sources_do_not_enter_target_counts(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle = Path(temp)
            rel = "sources/Synset/alternative_or_definition_wsd_frozen/item.json"
            path = bundle / rel
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"source_record": {"alternative_definition_provenance": {
                "source_evidence": [{"source": "Other source", "source_version": "v1.2.3"}]
            }}}), encoding="utf-8")
            index = bundle / "indexes" / "source_records.jsonl"
            index.parent.mkdir()
            index.write_text(json.dumps({"path": rel}) + "\n", encoding="utf-8")

            report = summarize_bundle(bundle)

            self.assertEqual(report["summary"]["target_evidence_items"], 0)
            self.assertEqual(sum(v["evidence_items"] for v in report["labels"].values()), 0)


if __name__ == "__main__":
    unittest.main()
