import unittest

from src.logic.source_clause_alignment_validator import validate_alignment, validate_dataset


def task_record():
    return {
        "schema_version": "source-clause-alignment-task/0.1",
        "task_id": "MAP-0001",
        "pos": "n",
        "lemmas": ["demo"],
        "raw_gloss": "a small bird",
        "effective_definition": "small bird",
        "parts": [
            {"part_id": "p1", "text": "small"},
            {"part_id": "p2", "text": "bird"},
        ],
        "source_logic": {"op": "AND", "args": [{"part_id": "p1"}, {"part_id": "p2"}]},
        "graph_clause": {
            "clause_index": 0,
            "literals": [
                {"literal_id": "l1", "lemmas": "small", "definition": "small concept"},
                {"literal_id": "l2", "lemmas": "bird", "definition": "bird concept"},
            ],
        },
    }


def annotation_record():
    return {
        "schema_version": "source-clause-alignment-return/0.1",
        "task_id": "MAP-0001",
        "annotator_id": "rater-a",
        "mappings": [
            {
                "literal_id": "l1",
                "status": "exact",
                "supporting_part_ids": ["p1"],
                "evidence_spans": [{"text_view": "raw_gloss", "start": 2, "end": 7}],
            },
            {
                "literal_id": "l2",
                "status": "exact",
                "supporting_part_ids": ["p2"],
                "evidence_spans": [{"text_view": "raw_gloss", "start": 8, "end": 12}],
            },
        ],
        "unmapped_part_ids": [],
        "notes": [],
    }


class SourceClauseAlignmentValidatorTests(unittest.TestCase):
    def test_accepts_complete_mapping_with_valid_gloss_spans(self):
        self.assertEqual(validate_alignment(task_record(), annotation_record()), [])
        self.assertEqual(validate_dataset([task_record()], [annotation_record()]), [])

    def test_rejects_missing_literals_unknown_parts_and_bad_offsets(self):
        annotation = annotation_record()
        annotation["mappings"].pop()
        annotation["mappings"][0]["supporting_part_ids"] = ["unknown-part"]
        annotation["mappings"][0]["evidence_spans"][0]["end"] = 100
        errors = validate_alignment(task_record(), annotation)
        self.assertTrue(any("every graph_clause literal" in error for error in errors))
        self.assertTrue(any("unknown part_id" in error for error in errors))
        self.assertTrue(any("selected text length" in error for error in errors))

    def test_requires_exact_unmapped_part_accounting_and_complete_task_returns(self):
        task = task_record()
        annotation = annotation_record()
        annotation["unmapped_part_ids"] = ["p2"]
        errors = validate_alignment(task, annotation)
        self.assertTrue(any("exactly the parts unused" in error for error in errors))

        annotation["unmapped_part_ids"] = []
        self.assertTrue(any("incomplete" in error for error in validate_dataset([task], [])))
        self.assertTrue(any("duplicate annotation" in error for error in validate_dataset([task], [annotation, annotation])))

    def test_rejects_fields_that_mix_mapping_with_uncontrolled_semantic_labels(self):
        annotation = annotation_record()
        annotation["entailment"] = "entailed"
        self.assertTrue(any("unsupported annotation field" in error for error in validate_alignment(task_record(), annotation)))

    def test_rejects_source_logic_leaves_that_do_not_match_declared_parts(self):
        task = task_record()
        task["source_logic"] = {"op": "OR", "args": [{"part_id": "p1"}, {"part_id": "missing"}]}
        self.assertTrue(any("known part IDs" in error for error in validate_alignment(task, annotation_record())))

    def test_rejects_duplicate_source_logic_part_references(self):
        task = task_record()
        task["source_logic"] = {"op": "AND", "args": [{"part_id": "p1"}, {"part_id": "p1"}]}
        self.assertTrue(any("each declared part exactly once" in error
                            for error in validate_alignment(task, annotation_record())))

    def test_rejects_evidence_span_from_unlisted_supporting_part(self):
        annotation = annotation_record()
        annotation["mappings"][0]["evidence_spans"] = [
            {"text_view": "part_text", "part_id": "p2", "start": 0, "end": 4},
            {"text_view": "raw_gloss", "start": 2, "end": 7},
        ]
        self.assertTrue(any("listed in supporting_part_ids" in error
                            for error in validate_alignment(task_record(), annotation)))


if __name__ == "__main__":
    unittest.main()
