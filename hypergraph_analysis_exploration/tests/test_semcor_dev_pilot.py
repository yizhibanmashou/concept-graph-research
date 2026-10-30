import unittest
from collections import Counter
from io import BytesIO
from zipfile import ZipFile
from src.analysis.semcor_dev_pilot import (build_index, mapped_target, norm, observed_key, pos_class,
                                           ranked_gloss, ranked_mfs, sentence_records, sentences)


class SemcorDevPilotTests(unittest.TestCase):
    def test_adjective_candidates_and_strict_mapping(self):
        rows = [{'synset_id': 'oewn-a', 'lemmas': 'good', 'pos': 'a', 'definition': 'pleasant'},
                {'synset_id': 'oewn-b', 'lemmas': 'good', 'pos': 's', 'definition': 'healthy'}]
        index = build_index(rows)
        self.assertEqual(set(index['good', 'a']), {'oewn-a', 'oewn-b'})
        self.assertEqual(pos_class('s'), 'a')
        self.assertEqual(norm('Ice_Cream'), 'ice cream')
        self.assertEqual(mapped_target('key', {'key': {'a'}}, {r['synset_id']: r for r in rows}), ('oewn-a', None))

    def test_baselines_deterministic_and_no_gold_input(self):
        rows = {'x': {'synset_id': 'x', 'lemmas': 'bank', 'definition': 'money'},
                'y': {'synset_id': 'y', 'lemmas': 'bank', 'definition': 'river'}}
        self.assertEqual(ranked_mfs(rows, Counter({'y': 2})), 'y')
        self.assertEqual(ranked_mfs(rows, Counter()), 'x')
        self.assertEqual(ranked_gloss(rows, 'the river flows'), 'y')
        self.assertEqual(ranked_gloss(rows, 'unmatched'), 'x')

    def test_target_is_derived_from_surface_and_observed_pos(self):
        morph = lambda surface, pos: 'run' if surface == 'running' and pos == 'v' else None
        self.assertEqual(observed_key('running', 'VBG', morph), ('run', 'v'))
        self.assertEqual(observed_key('Unknown_Name', 'NNP', morph), ('unknown name', 'n'))
        self.assertIsNone(observed_key('and', 'CC', morph))

    def test_sentence_records_preserves_xml_word_positions_and_legacy_view(self):
        payload = b'<corpus><s><wf>early</wf><punc>,</punc><wf wnsn="1" lexsn="x">pivot</wf><wf>late</wf></s></corpus>'
        memory = BytesIO()
        with ZipFile(memory, 'w') as archive:
            archive.writestr('semcor/sample.xml', payload)
        memory.seek(0)
        with ZipFile(memory) as archive:
            records = list(sentence_records(archive, 'sample.xml'))
            legacy = list(sentences(archive, 'sample.xml'))
        self.assertEqual(records[0][1], ['early', ',', 'pivot', 'late'])
        self.assertEqual([(position, word.text) for position, word in records[0][2]], [(2, 'pivot')])
        self.assertEqual(legacy[0][0], 'early , pivot late')
        self.assertEqual([word.text for word in legacy[0][1]], ['pivot'])
