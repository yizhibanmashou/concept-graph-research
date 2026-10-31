import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.profile_t04_xpu_relation_aggregation import (
    _quantiles,
    _read_candidate_ids,
    _read_rules,
)


class T04XpuRelationProfileInputTests(unittest.TestCase):
    def test_reads_only_candidate_inventory_and_deduplicates(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "train.json"
            path.write_text(json.dumps([
                {"candidate_ids": ["b", "a", "b"], "label": "ignore", "context": "ignore"},
                {"candidate_ids": ["c"]},
            ]), encoding="utf-8")
            self.assertEqual(_read_candidate_ids(path), ["a", "b", "c"])

    def test_reads_only_requested_candidate_rules(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "rules.jsonl"
            path.write_text("\n".join(json.dumps(row) for row in [
                {"head": "wanted", "clauses": [["x"]]},
                {"head": "other", "clauses": [["private"]]},
            ]), encoding="utf-8")
            self.assertEqual(_read_rules(path, {"wanted"}), {"wanted": [["x"]]})

    def test_reports_nearest_rank_p90_and_empty_input(self):
        self.assertEqual(_quantiles([1, 2, 3, 4]), {
            "count": 4, "median": 2.5, "p90_nearest_rank": 4, "max": 4,
        })
        self.assertEqual(_quantiles([]), {
            "count": 0, "median": None, "p90_nearest_rank": None, "max": None,
        })


if __name__ == "__main__":
    unittest.main()
