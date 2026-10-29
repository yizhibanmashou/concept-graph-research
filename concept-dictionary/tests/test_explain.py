import unittest
import backend.app as service
from fastapi import HTTPException


class TinyGraph:
    def __init__(self):
        self.clauses={'t':[['a','b'],['c']], 'c':[['t']], 'a':[], 'b':[]}
        self.names={x:{'id':x,'lemmas':x,'pos':'n','definition':x,'basis':False} for x in self.clauses}
    def node(self, identity):
        return self.names[identity] | {'records':[], 'alternatives':[{'index':i,'body':b,'sources':[],'source_available':False} for i,b in enumerate(self.clauses[identity])]}


class ExplanationTests(unittest.TestCase):
    def setUp(self):
        self.old_graph=getattr(service,'graph',None)
        self.old_info=getattr(service,'info',None)
        service.graph=TinyGraph()
        service.info={'semantic_fingerprint_sha256':'test'}
        service.costs_for.cache_clear()
        service.costs_for_choices.cache_clear()
    def tearDown(self):
        service.graph=self.old_graph
        service.info=self.old_info
        service.costs_for.cache_clear()
        service.costs_for_choices.cache_clear()
    def test_selected_cycle_is_visible(self):
        state=service.Explain(target='t',known=[],expanded=['t','c'],choices={'t':1,'c':0})
        tree=service.explain(state)['tree']
        self.assertEqual(tree['selected'],1)
        self.assertEqual(tree['children'][0]['children'][0]['status'],'cycle')
    def test_known_prerequisites_complete_one_branch(self):
        state=service.Explain(target='t',known=['a','b'],expanded=['t'])
        tree=service.explain(state)['tree']
        self.assertEqual(tree['selected'],0)
        self.assertTrue(tree['alternatives'][0]['complete'])
        self.assertEqual([child['status'] for child in tree['children']],['known','known'])

    def test_selected_cycle_cannot_borrow_unselected_escape(self):
        state=service.Explain(target='t',known=['a','b'],expanded=['t','c'],choices={'t':1,'c':0})
        tree=service.explain(state)['tree']
        self.assertFalse(tree['reachable'])
        self.assertFalse(tree['alternatives'][1]['complete'])
        self.assertEqual(tree['children'][0]['children'][0]['status'],'cycle')
    def test_explore_counts_new_targets_not_new_seed(self):
        data=service.explore(service.Explore(known=['a'],added='b'))
        self.assertEqual(data['total'],2) # t, and c through t
        self.assertEqual({x['id'] for x in data['items']},{'t','c'})

    def test_session_validation_accepts_valid_path(self):
        state=service.SessionData(version=1,fingerprint='test',target='t',known=['a'],expanded=['t'],choices={'t':1})
        self.assertTrue(service.validate_session(state)['valid'])

    def test_session_validation_rejects_wrong_version_and_invalid_branch(self):
        for change in ({'fingerprint':'other'}, {'choices':{'t':9}}, {'known':['unknown']}, {'expanded':['unknown']}):
            payload={'version':1,'fingerprint':'test','target':'t','known':[],'expanded':['t'],'choices':{}}
            payload.update(change)
            with self.subTest(change=change), self.assertRaises(HTTPException):
                service.validate_session(service.SessionData(**payload))

if __name__ == '__main__': unittest.main()
