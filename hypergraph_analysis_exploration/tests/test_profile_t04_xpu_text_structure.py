import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.profile_t04_xpu_text_structure import (
    pad_token_batch,
    read_graph,
    read_train_candidate_ids,
)


class ProfileT04XpuTextStructureTests(unittest.TestCase):
    def test_reads_only_candidate_ids_and_deduplicates_for_encoding(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "train.json"
            path.write_text(json.dumps([
                {"candidate_ids": ["b", "a"], "label": "not-read"},
                {"candidate_ids": ["a", "c"], "context": "not-read"},
            ]), encoding="utf-8")
            ids, occurrences = read_train_candidate_ids(path)
        self.assertEqual(ids, ["a", "b", "c"])
        self.assertEqual(occurrences, 4)

    def test_pads_ids_and_masks_without_changing_content(self):
        ids, masks = pad_token_batch([[101, 12, 102], [101, 102]], pad_id=0)
        self.assertEqual(ids, [[101, 12, 102], [101, 102, 0]])
        self.assertEqual(masks, [[1, 1, 1], [1, 1, 0]])

    def test_loads_dependency_glosses_as_well_as_train_target_glosses(self):
        with tempfile.TemporaryDirectory() as tmp:
            nodes = Path(tmp) / "nodes.tsv"
            rules = Path(tmp) / "rules.jsonl"
            nodes.write_text(
                "synset_id\tdefinition\nhead\ttarget gloss\ndep\tdependency gloss\n",
                encoding="utf-8",
            )
            rules.write_text(json.dumps({"head": "head", "clauses": [["dep"]]}) + "\n",
                             encoding="utf-8")
            glosses, branches = read_graph(nodes, rules, {"head"})
        self.assertEqual(glosses, {"head": "target gloss", "dep": "dependency gloss"})
        self.assertEqual(branches, {"head": [["dep"]]})

    def test_rejects_empty_sequences(self):
        with self.assertRaises(ValueError):
            pad_token_batch([[101, 102], []])


if __name__ == "__main__":
    unittest.main()
