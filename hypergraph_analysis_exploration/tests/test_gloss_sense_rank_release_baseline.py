import unittest

from src.analysis.gloss_sense_rank_release_baseline import (
    build_idf,
    evaluate_synsets,
    rank_candidate_senses,
)
from src.analysis.gloss_genus_baseline import find_first_noun_candidate


class GlossSenseRankReleaseBaselineTests(unittest.TestCase):
    def test_context_gloss_similarity_ranks_matching_sense_without_hypernym_input(self):
        records = [
            {
                "synset_id": "target-n",
                "lexname": "noun.artifact",
                "definitions": ["a company that accepts deposits from customers"],
                "members": ["target"],
                "hypernyms": ["financial-n"],
            },
            {
                "synset_id": "financial-n",
                "lexname": "noun.group",
                "definitions": ["an organization that accepts deposits from customers and lends money"],
                "members": ["company", "financial institution"],
                "hypernyms": ["entity-n"],
            },
            {
                "synset_id": "military-n",
                "lexname": "noun.group",
                "definitions": ["a group of soldiers organized for a military operation"],
                "members": ["company"],
                "hypernyms": ["group-n"],
            },
        ]
        index = build_noun_lemma_index_from_records(records)
        candidate = find_first_noun_candidate(records[0]["definitions"][0], records[0]["members"], index)
        idf, token_sets = build_idf(records)

        ranking = rank_candidate_senses(
            records[0]["definitions"][0], records[0]["members"], candidate, idf, token_sets,
        )

        self.assertEqual(candidate["lemma"], "company")
        self.assertEqual(ranking["decision"], "selected_unique_top_sense")
        self.assertEqual(ranking["selected_synset_id"], "financial-n")
        self.assertGreater(ranking["ranked_senses"][0]["score"], ranking["ranked_senses"][1]["score"])

    def test_equal_top_scores_abstain_instead_of_using_id_tie_break(self):
        records = [
            {"synset_id": "target-n", "lexname": "x", "definitions": ["a company with deposits"],
             "members": ["target"], "hypernyms": ["sense-a"]},
            {"synset_id": "sense-a", "lexname": "x", "definitions": ["a business with deposits"],
             "members": ["company"], "hypernyms": []},
            {"synset_id": "sense-b", "lexname": "x", "definitions": ["a business with deposits"],
             "members": ["company"], "hypernyms": []},
        ]
        candidate = {"lemma": "company", "span": {"start": 2, "end": 9},
                     "candidate_synset_ids": ["sense-a", "sense-b"]}
        idf, token_sets = build_idf(records)

        ranking = rank_candidate_senses(
            records[0]["definitions"][0], records[0]["members"], candidate, idf, token_sets,
        )

        self.assertEqual(ranking["decision"], "abstain_tied_top_score")
        self.assertIsNone(ranking["selected_synset_id"])
        self.assertEqual(ranking["top_tie_size"], 2)

    def test_no_overlap_abstains_and_does_not_claim_false(self):
        records = [
            {"synset_id": "target-n", "lexname": "x", "definitions": ["a company of blue"],
             "members": ["target"], "hypernyms": ["sense-a"]},
            {"synset_id": "sense-a", "lexname": "x", "definitions": ["red objects gather"],
             "members": ["company"], "hypernyms": []},
        ]
        candidate = {"lemma": "company", "span": {"start": 2, "end": 9},
                     "candidate_synset_ids": ["sense-a"]}
        idf, token_sets = build_idf(records)

        ranking = rank_candidate_senses(
            records[0]["definitions"][0], records[0]["members"], candidate, idf, token_sets,
        )

        self.assertEqual(ranking["decision"], "abstain_no_context_overlap")
        self.assertIsNone(ranking["selected_synset_id"])

    def test_aggregate_evaluation_reports_selective_metrics_only(self):
        records = [
            {"synset_id": "target-n", "lexname": "noun.artifact", "definitions": ["a company that accepts deposits"],
             "members": ["target"], "hypernyms": ["financial-n"]},
            {"synset_id": "financial-n", "lexname": "noun.group", "definitions": ["an organization that accepts deposits"],
             "members": ["company"], "hypernyms": []},
            {"synset_id": "root-n", "lexname": "noun.entity", "definitions": ["something that exists"],
             "members": ["root"], "hypernyms": []},
        ]

        result = evaluate_synsets(records, build_noun_lemma_index_from_records(records))

        self.assertEqual(result["definition_instance_count"], 3)
        self.assertEqual(result["definition_instances_without_direct_hypernym"], 2)
        self.assertFalse(result["source_gloss_text_emitted"])
        self.assertFalse(result["per_definition_results_emitted"])
        self.assertNotIn("per_definition", result)
        self.assertIn("unique_top1_match_rate_among_decisions", result["overall"])
        self.assertIn("3", result["overall"]["top_k_retrieval"])


def build_noun_lemma_index_from_records(records):
    """Construct an index fixture from test records without touching the release."""
    index = {}
    for record in records:
        for member in record["members"]:
            index.setdefault(member.casefold(), set()).add(record["synset_id"])
    return {lemma: sorted(ids) for lemma, ids in index.items()}


if __name__ == "__main__":
    unittest.main()
