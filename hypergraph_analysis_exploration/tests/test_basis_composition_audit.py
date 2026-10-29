import csv
import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.basis_composition_audit import audit_basis_composition


class BasisCompositionAuditTests(unittest.TestCase):
    def test_reports_aggregate_metadata_without_emitting_basis_ids(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir)
            graph = bundle / "graph"
            graph.mkdir()
            (bundle / "manifest.json").write_text(json.dumps({"graph_sha256": "a" * 64}))
            (graph / "selected_basis_atoms.txt").write_text("oewn-1-n\nprep-1\n")
            with (graph / "nodes.tsv").open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(
                    stream,
                    fieldnames=["synset_id", "lemmas", "pos", "definition", "source_root", "is_basis"],
                    delimiter="\t",
                )
                writer.writeheader()
                writer.writerows([
                    {"synset_id": "oewn-1-n", "lemmas": "bird", "pos": "n", "definition": "a bird", "source_root": "parsed", "is_basis": "True"},
                    {"synset_id": "prep-1", "lemmas": "above", "pos": "prep", "definition": "above", "source_root": "external", "is_basis": "True"},
                ])

            report = audit_basis_composition(bundle)

        self.assertEqual(report["basis_count"], 2)
        self.assertEqual(report["pos_counts"], {"n": 1, "prep": 1})
        self.assertEqual(report["source_root_counts"], {"external": 1, "parsed": 1})
        self.assertEqual(report["id_namespace_counts"], {"non_oewn": 1, "oewn": 1})
        self.assertTrue(report["integrity_checks"]["node_basis_flags_agree"])
        serialized = json.dumps(report)
        self.assertNotIn("oewn-1-n", serialized)
        self.assertNotIn("a bird", serialized)

    def test_rejects_basis_file_that_disagrees_with_node_flags(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir)
            graph = bundle / "graph"
            graph.mkdir()
            (bundle / "manifest.json").write_text(json.dumps({"graph_sha256": "a" * 64}))
            (graph / "selected_basis_atoms.txt").write_text("seed\n")
            (graph / "nodes.tsv").write_text(
                "synset_id\tpos\tsource_root\tis_basis\nseed\tn\tparsed\tFalse\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "disagrees"):
                audit_basis_composition(bundle)


if __name__ == "__main__":
    unittest.main()
