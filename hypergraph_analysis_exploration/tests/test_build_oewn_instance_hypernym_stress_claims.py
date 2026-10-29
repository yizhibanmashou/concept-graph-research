import unittest

from src.analysis.build_oewn_instance_hypernym_stress_claims import build_claims


class OewnInstanceHypernymStressFrameTests(unittest.TestCase):
    def setUp(self):
        self.nodes = {
            "i1": {"pos": "n", "source_file": "noun.test.json"},
            "c1": {"pos": "n", "source_file": "noun.test.json"},
            "i2": {"pos": "n", "source_file": "noun.test.json"},
            "c2": {"pos": "n", "source_file": "noun.test.json"},
            "middle": {"pos": "n", "source_file": "noun.test.json"},
            "root": {"pos": "n", "source_file": "noun.test.json"},
            "other1": {"pos": "n", "source_file": "noun.test.json"},
            "other2": {"pos": "n", "source_file": "noun.test.json"},
            "verb1": {"pos": "v", "source_file": "verb.test.json"},
            "verb2": {"pos": "v", "source_file": "verb.test.json"},
        }
        self.instance_parents = {
            "i1": ("c1",), "c1": (), "i2": ("c2",), "c2": (),
            "middle": (), "root": (), "other1": (), "other2": (), "verb1": (), "verb2": (),
        }
        self.class_parents = {
            "i1": (), "c1": ("middle",), "i2": (), "c2": ("middle",),
            "middle": ("root",), "root": (), "other1": (), "other2": (), "verb1": (), "verb2": (),
        }

    def test_builds_exact_deterministic_strata_without_duplicate_pairs(self):
        first, counts = build_claims(self.nodes, self.instance_parents, self.class_parents, per_stratum=2)
        second, second_counts = build_claims(self.nodes, self.instance_parents, self.class_parents, per_stratum=2)
        self.assertEqual(first, second)
        self.assertEqual(counts, second_counts)
        self.assertEqual(len(first), 16)
        self.assertEqual(set(counts.values()), {2})
        self.assertEqual(len({(row["instance_synset_id"], row["class_synset_id"]) for row in first}), 16)
        by_prefix = {}
        for claim in first:
            by_prefix.setdefault(claim["claim_id"].split("/")[0], []).append(claim)
        self.assertEqual(len(by_prefix), 8)
        self.assertEqual(len([row for row in by_prefix["missing_synset"]
                              if row["instance_synset_id"].startswith("__missing_")]), 2)

    def test_rejects_zero_sample_size(self):
        with self.assertRaisesRegex(ValueError, "per_stratum must be positive"):
            build_claims(self.nodes, self.instance_parents, self.class_parents, per_stratum=0)


if __name__ == "__main__":
    unittest.main()
