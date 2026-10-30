import unittest
from research.tologic.without_interface_audit import audit


class WithoutAuditTests(unittest.TestCase):
    def test_counts_and_occurrence_validation(self):
        source = {'source': {'synset_id': 'w'}, 'usage': {'occurrence_ids': ['o']},
                  'interfaces': {'without::lack': {'parameters': [{'name': n} for n in ('e', 's', 'h')]}}}
        def candidate(i, lexical, used, rhs):
            return {'candidate_id': str(i), 'formula': {'synset_id': 'w', 'rhs': rhs},
                    'binding_plan': {'lexical': lexical}, 'used_occurrence_ids': used}
        call = {'occurrence_id': 'o', 'bindings': {'e': 'e', 's': 's', 'h': 'h'}}
        rhs = {'op': 'use', 'occurrence_id': 'o', 'synset_id': 'without', 'usage_id': 'lack',
               'args': [{'var': x} for x in ('e', 's', 'h')]}
        rows = [candidate(1, [call], ['o'], rhs), candidate(2, [], [], {'op': 'struct'})]
        result = audit(source, rows)
        self.assertEqual((result['same_named_binding'], result['without_not_called'],
                          result['no_call_and_no_explicit_negation_operator']), (1, 1, 1))
        with self.assertRaises(ValueError):
            audit(source, rows + [rows[0]])
        rhs['args'][1]['var'] = 'h'
        with self.assertRaises(ValueError):
            audit(source, rows)


if __name__ == '__main__':
    unittest.main()
