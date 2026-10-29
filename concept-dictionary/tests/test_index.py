import hashlib
import json
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from backend import data


class IndexTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        (self.root/'graph').mkdir()
        (self.root/'indexes').mkdir()
        files={
            'graph/nodes.tsv': 'synset_id\tlemmas\tpos\tdefinition\tsource_root\tclause_count\tis_basis\tis_cycle_candidate\nA\talpha / aleph\tn\tfirst\tlocal\t1\tFalse\tFalse\nB\tbeta\tn\tsecond\tlocal\t0\tTrue\tFalse\n',
            'graph/hypergraph_rules.jsonl': json.dumps({'head':'A','clauses':[['B']]})+'\n'+json.dumps({'head':'B','clauses':[]})+'\n',
            'indexes/senses.jsonl': '\n'.join(json.dumps({'identity':x,'lemmas':l,'source_records':[],'active_clause_sources':[]}) for x,l in [('A','alpha / aleph'),('B','beta')])+'\n',
        }
        records=[]
        for name,content in files.items():
            raw=content.encode('utf-8');(self.root/name).write_bytes(raw)
            records.append({'path':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
        (self.root/'checksums.jsonl').write_text('\n'.join(map(json.dumps,records))+'\n',encoding='utf-8')
        digest=next(x['sha256'] for x in records if x['path']=='graph/hypergraph_rules.jsonl')
        (self.root/'manifest.json').write_text(json.dumps({'semantic_fingerprint_sha256':'fixture','graph_sha256':digest,'graph_version':'test','head_count':2,'clause_count':1}),encoding='utf-8')
        self.bundle=patch.object(data,'BUNDLE',self.root);self.bundle.start()
        self.db=patch.object(data,'DB',self.root/'out'/'graph.sqlite3');self.db.start()

    def tearDown(self):
        self.db.stop();self.bundle.stop();self.tmp.cleanup()

    def test_index_and_independent_lemma_search(self):
        data.ensure_index()
        with closing(data.connect()) as db:
            self.assertEqual(db.execute("SELECT sense_id FROM lemma_index WHERE lemma='aleph'").fetchone()[0],'A')
            self.assertEqual(db.execute('SELECT count(*) FROM clauses').fetchone()[0],1)

    def test_corrupt_input_does_not_replace_existing_index(self):
        data.ensure_index()
        before=data.DB.read_bytes()
        (self.root/'indexes/senses.jsonl').write_text('corrupted',encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError,'校验失败'):
            data.ensure_index()
        with self.assertRaisesRegex(RuntimeError,'校验失败'):
            data.ensure_index(force=True)
        self.assertEqual(data.DB.read_bytes(),before)

    def test_changed_input_with_updated_checksum_requires_rebuild(self):
        data.ensure_index()
        path=self.root/'graph/nodes.tsv'
        raw=path.read_bytes().replace(b'first',b'FIRST')
        path.write_bytes(raw)
        checksums=[json.loads(line) for line in (self.root/'checksums.jsonl').read_text(encoding='utf-8').splitlines()]
        for item in checksums:
            if item['path']=='graph/nodes.tsv':
                item['sha256']=hashlib.sha256(raw).hexdigest()
                item['bytes']=len(raw)
        (self.root/'checksums.jsonl').write_text('\n'.join(map(json.dumps,checksums))+'\n',encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError,'索引版本或数据指纹不匹配'):
            data.ensure_index()

if __name__ == '__main__': unittest.main()
