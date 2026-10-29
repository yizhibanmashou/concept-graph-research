import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.suggest_source_part_spans import suggest_spans


class SuggestSourcePartSpansTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tasks_path = Path(self.temp_dir.name) / "tasks.jsonl"

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_tasks(self, tasks):
        self.tasks_path.write_text(
            "".join(json.dumps(task, ensure_ascii=False) + "\n" for task in tasks),
            encoding="utf-8",
        )

    def _task(self, *, raw="a cat", effective="a cat", parts=None):
        return {
            "task_id": "task-1",
            "raw_gloss": raw,
            "effective_definition": effective,
            "parts": parts if parts is not None else [{"part_id": "p1", "text": "cat"}],
        }

    def test_reports_unique_matches_and_excludes_source_text(self):
        self._write_tasks([self._task()])
        result = suggest_spans(self.tasks_path)
        row = result["rows"][0]
        self.assertEqual(row["task_id"], "task-1")
        self.assertEqual(row["part_suggestions"][0]["raw_gloss"], {
            "status": "unique_exact_substring", "spans": [{"start": 2, "end": 5}],
        })
        self.assertEqual(row["part_suggestions"][0]["effective_definition"]["status"],
                         "unique_exact_substring")
        self.assertNotIn("cat", json.dumps(row))
        self.assertFalse(result["manifest"]["output_contains_gloss_or_part_text"])

    def test_preserves_overlapping_matches_as_ambiguous(self):
        self._write_tasks([self._task(raw="aaaa", effective="aaaa",
                                      parts=[{"part_id": "p1", "text": "aa"}])])
        suggestion = suggest_spans(self.tasks_path)["rows"][0]["part_suggestions"][0]
        self.assertEqual(suggestion["raw_gloss"], {
            "status": "multiple_exact_substrings",
            "spans": [{"start": 0, "end": 2}, {"start": 1, "end": 3},
                      {"start": 2, "end": 4}],
        })

    def test_reports_no_match_without_guessing(self):
        self._write_tasks([self._task(raw="animal", effective="animal",
                                      parts=[{"part_id": "p1", "text": "feline"}])])
        suggestion = suggest_spans(self.tasks_path)["rows"][0]["part_suggestions"][0]
        self.assertEqual(suggestion["raw_gloss"], {
            "status": "no_exact_substring", "spans": [],
        })

    def test_offsets_are_python_unicode_code_points(self):
        self._write_tasks([self._task(raw="猫🐈a", effective="猫🐈a",
                                      parts=[{"part_id": "p1", "text": "🐈"}])])
        suggestion = suggest_spans(self.tasks_path)["rows"][0]["part_suggestions"][0]
        self.assertEqual(suggestion["raw_gloss"]["spans"], [{"start": 1, "end": 2}])

    def test_rejects_duplicate_task_and_part_ids(self):
        with self.subTest("duplicate task"):
            self._write_tasks([self._task(), self._task()])
            with self.assertRaisesRegex(ValueError, "duplicate task_id"):
                suggest_spans(self.tasks_path)
        with self.subTest("duplicate part"):
            self._write_tasks([self._task(parts=[{"part_id": "p1", "text": "a"},
                                                {"part_id": "p1", "text": "cat"}])])
            with self.assertRaisesRegex(ValueError, "duplicate part_id"):
                suggest_spans(self.tasks_path)

    def test_rejects_empty_or_malformed_task_content(self):
        for task in (self._task(parts=[]), self._task(parts=[{"part_id": "p1", "text": ""}])):
            with self.subTest(task=task):
                self._write_tasks([task])
                with self.assertRaises(ValueError):
                    suggest_spans(self.tasks_path)


if __name__ == "__main__":
    unittest.main()
