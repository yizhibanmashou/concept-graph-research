import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.gloss_genus_baseline import evaluate_batch, find_first_noun_candidate, load_direct_hypernyms


class GlossGenusBaselineTests(unittest.TestCase):
    def test_first_exact_noun_match_preserves_source_span(self):
        candidate = find_first_noun_candidate(
            "a small bird that sings",
            ["songbird"],
            {"bird": ["bird.n.01"], "small bird": ["small-bird.n.01"]},
        )
        self.assertEqual(candidate["lemma"], "small bird")
        self.assertEqual(candidate["span"], {"start": 2, "end": 12})
        self.assertEqual(candidate["candidate_sense_count"], 1)

    def test_target_lemma_is_not_reused_as_its_own_candidate(self):
        candidate = find_first_noun_candidate("the animal is a dog", ["animal"], {"animal": ["animal.n.01"], "dog": ["dog.n.01"]})
        self.assertEqual(candidate["lemma"], "dog")

    def test_indefinite_pronoun_definitions_abstain(self):
        self.assertIsNone(find_first_noun_candidate("someone who studies birds", [], {"someone": ["someone.n.01"], "bird": ["bird.n.01"]}))

    def test_match_is_only_a_resource_relative_direct_hypernym_proxy(self):
        batch = [{"task_id": "T1", "pos": "n", "lemmas": ["sparrow"], "gloss": "a bird with a short bill"}]
        answer = [{"task_id": "T1", "sense_id": "sparrow.n.01", "panel": "random"}]
        result = evaluate_batch(batch, answer, {"bird": ["bird.n.01"]}, {"sparrow.n.01": ["bird.n.01", "organism.n.01"]})
        summary = result["overall"]
        self.assertEqual(summary["candidate_coverage"], 1.0)
        self.assertEqual(summary["direct_hypernym_match_rate_among_candidates"], 1.0)
        self.assertEqual(result["per_task"][0]["status"], "candidate_matches_direct_hypernym")
        self.assertIn("not semantic gold", result["evaluation_target"])

    def test_release_namespace_prefix_is_mapped_to_official_synset_key(self):
        with tempfile.TemporaryDirectory() as directory:
            release = Path(directory)
            (release / "noun.test.json").write_text(
                json.dumps({"00000001-n": {"hypernym": ["00000002-n"]}}),
                encoding="utf-8",
            )
            self.assertEqual(
                load_direct_hypernyms(release, {"oewn-00000001-n"}),
                {"oewn-00000001-n": ["00000002-n"]},
            )

    def test_targets_without_hypernyms_are_excluded_from_match_denominator(self):
        batch = [
            {"task_id": "T1", "pos": "n", "lemmas": ["sparrow"], "gloss": "a bird"},
            {"task_id": "T2", "pos": "n", "lemmas": ["root"], "gloss": "a root"},
        ]
        answer = [
            {"task_id": "T1", "sense_id": "sparrow.n.01", "panel": "random"},
            {"task_id": "T2", "sense_id": "root.n.01", "panel": "random"},
        ]
        result = evaluate_batch(
            batch,
            answer,
            {"bird": ["bird.n.01"]},
            {"sparrow.n.01": ["bird.n.01"], "root.n.01": []},
        )
        self.assertEqual(result["overall"]["eligible_noun_targets_with_direct_hypernym"], 1)
        self.assertEqual(result["overall"]["direct_hypernym_match_rate_over_eligible"], 1.0)
        self.assertEqual(result["per_task"][1]["status"], "target_has_no_direct_hypernym")


if __name__ == "__main__":
    unittest.main()
