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
                                "source_version": "enwiktionary-2026-10-01",
                                "source_locator": "https://example.org/private/path?secret=do-not-print",
                                "source_ontology": "https://ontology.example/private/item",
                                "evidence_type": "definition_match",
                                "external_id": "private-sense-id",
                            },
                            {
                                "source": "Kaikki/Wiktextract relaxed definition-term fallback",
                                "source_version": "2026-10-01",
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
            self.assertEqual(targeted["version_shape"], {"date_like": 1})
            self.assertEqual(targeted["locator_host"], {"example.org": 1})
            self.assertEqual(targeted["evidence_type"], {"definition_match": 1})
            for secret in ("private definition text", "private-sense-id", "private/path", "secret=", "private-locator"):
                self.assertNotIn(secret, rendered)

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
