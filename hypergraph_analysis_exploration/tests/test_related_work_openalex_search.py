import unittest

from src.analysis.search_related_work_openalex import merge_query_results, reconstruct_abstract


class RelatedWorkOpenAlexSearchTests(unittest.TestCase):
    def test_reconstructs_abstract_positions(self):
        self.assertEqual(
            reconstruct_abstract({"proof": [2], "A": [0], "replayable": [1]}),
            "A replayable proof",
        )
        self.assertIsNone(reconstruct_abstract(None))

    def test_merges_doi_variants_and_tracks_all_matching_queries(self):
        runs = [
            {"query_id": "q1", "results": [{
                "id": "https://openalex.org/W1", "doi": "https://doi.org/10.1234/ABC",
                "title": "A Study", "publication_date": "2026-01-01", "type": "conference-paper",
                "abstract_inverted_index": {"evidence": [0]},
                "primary_location": {"source": {"display_name": "ACL"}, "landing_page_url": "https://example.org/paper"},
                "authorships": [{"author": {"display_name": "Example Author"}}],
            }]},
            {"query_id": "q2", "results": [{
                "id": "https://openalex.org/W1", "doi": "https://doi.org/10.1234/abc",
                "title": "A Study", "publication_date": "2026-01-01", "type": "conference-paper",
                "abstract_inverted_index": {"evidence": [0]},
                "primary_location": {"source": {"display_name": "ACL"}},
                "authorships": [],
            }]},
        ]
        merged = merge_query_results(runs)
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["matched_queries"], ["q1", "q2"])
        self.assertEqual(merged[0]["abstract"], "evidence")

    def test_falls_back_to_normalized_title_and_year_without_doi(self):
        runs = [
            {"query_id": "q1", "results": [{"title": "A–Study", "publication_date": "2026-01-01"}]},
            {"query_id": "q2", "results": [{"title": "a study", "publication_date": "2026-02-01"}]},
        ]
        merged = merge_query_results(runs)
        self.assertEqual(len(merged), 1)


if __name__ == "__main__":
    unittest.main()
