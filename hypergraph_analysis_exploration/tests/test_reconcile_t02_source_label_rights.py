import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.reconcile_t02_source_label_rights import normalize_label, reconcile


class T02SourceRightsReconciliationTests(unittest.TestCase):
    def test_normalizes_only_case_underscores_and_whitespace(self):
        self.assertEqual(normalize_label(" MeSH_2026   descriptors "), "mesh 2026 descriptors")
        self.assertNotEqual(normalize_label("GCIDE 0.54"), normalize_label("GCIDE 0.55"))

    def test_reconciles_unique_ambiguous_and_unmatched_labels_without_legal_claims(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            audit_path = root / "audit.json"
            rights_path = root / "rights.json"
            audit_path.write_text(json.dumps({
                "private_definition_fixture": "must not be emitted",
                "declared_source_labels": [
                {"source_label_exact": "GCIDE 0.54", "evidence_items": 10, "record_count": 8},
                {"source_label_exact": "Alias", "evidence_items": 3, "record_count": 3},
                {"source_label_exact": "unlisted", "evidence_items": 2, "record_count": 2},
            ]}), encoding="utf-8")
            rights_path.write_text(json.dumps({"sources": [
                {"source_label": "GCIDE_0.54", "license_status": "alignment_unverified",
                 "official_license_evidence": "private rights evidence prose"},
                {"source_label": "Alias", "license_status": "status_a"},
                {"source_label": "ALIAS", "license_status": "status_b"},
            ]}), encoding="utf-8")
            result = reconcile(audit_path, rights_path)

        self.assertEqual(result["summary"], {
            "source_profiles": 3,
            "evidence_items": 15,
            "unique_normalized_matches": 1,
            "matched_evidence_items": 10,
            "ambiguous_profiles": 1,
            "ambiguous_evidence_items": 3,
            "unmatched_profiles": 1,
            "unmatched_evidence_items": 2,
        })
        rendered = json.dumps(result, ensure_ascii=False)
        self.assertNotIn("secret-locator", rendered)
        self.assertNotIn("must not be emitted", rendered)
        self.assertNotIn("private rights evidence prose", rendered)
        self.assertIn("does not establish upstream identity", result["limitations"])
        self.assertEqual(len(result["inputs_sha256"]["t02_source_audit"]), 64)


if __name__ == "__main__":
    unittest.main()
