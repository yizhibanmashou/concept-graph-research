"""Read-only import of the frozen graph into a disposable SQLite index."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BUNDLE = ROOT.parent / 'OEWN'
BUNDLE = Path(os.environ.get('CONCEPT_BUNDLE', DEFAULT_BUNDLE)).resolve()
DB = ROOT / 'data' / 'graph.sqlite3'
SCHEMA = '5'


def manifest():
    path = BUNDLE / 'manifest.json'
    if not path.is_file():
        raise RuntimeError(f'未找到冻结数据包：{path}。请设置 CONCEPT_BUNDLE 指向数据包目录。')
    return json.loads(path.read_text(encoding='utf-8'))


def rows(path):
    with path.open(encoding='utf-8-sig') as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def connect():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db


def verify_index_inputs(m):
    required = {'graph/hypergraph_rules.jsonl', 'graph/nodes.tsv', 'indexes/senses.jsonl'}
    checksums = {row['path']: row for row in rows(BUNDLE / 'checksums.jsonl') if row['path'] in required}
    if set(checksums) != required or checksums['graph/hypergraph_rules.jsonl']['sha256'] != m['graph_sha256']:
        raise RuntimeError('冻结数据的文件清单不完整或与 manifest 不一致，未建立索引。')
    for name in sorted(required):
        file = BUNDLE / name
        if not file.is_file():
            raise RuntimeError(f'冻结数据文件缺失：{name}；请检查数据包。')
        digest = hashlib.sha256()
        with file.open('rb') as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b''):
                digest.update(chunk)
        if file.stat().st_size != checksums[name]['bytes'] or digest.hexdigest() != checksums[name]['sha256']:
            raise RuntimeError(f'冻结数据文件校验失败：{name}；未建立索引。')
    return {name: checksums[name]['sha256'] for name in required}


def ensure_index(force=False):
    m = manifest()
    expected = m['semantic_fingerprint_sha256']
    # The source may change after an index was built. Do not serve a stale
    # index under an unchanged manifest fingerprint.
    input_hashes = verify_index_inputs(m)
    if DB.is_file() and not force:
        try:
            with closing(connect()) as db:
                meta = dict(db.execute('SELECT key,value FROM meta'))
                if (meta.get('fingerprint') == expected and meta.get('schema') == SCHEMA
                    and all(meta.get('input:' + name) == digest for name, digest in input_hashes.items())):
                    return m
        except sqlite3.DatabaseError:
            pass
        raise RuntimeError('本地索引版本或数据指纹不匹配，请运行 python -m backend.index --rebuild。')
    graph = BUNDLE / 'graph' / 'hypergraph_rules.jsonl'
    DB.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix='graph-building-', suffix='.sqlite3', dir=DB.parent)
    os.close(fd)
    temp = Path(temp_name)
    print('首次启动：正在建立本地索引，请稍候……', flush=True)
    db = None
    try:
        db = sqlite3.connect(temp)
        db.executescript('''
          PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF;
          CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT);
          CREATE TABLE senses(id TEXT PRIMARY KEY, lemmas TEXT, pos TEXT, definition TEXT, basis INTEGER, records TEXT, sources TEXT);
          CREATE TABLE clauses(head TEXT, idx INTEGER, body TEXT, PRIMARY KEY(head,idx));
          CREATE TABLE lemma_index(lemma TEXT, sense_id TEXT);
        ''')
        with (BUNDLE / 'graph' / 'nodes.tsv').open(encoding='utf-8-sig', newline='') as f:
            batch=[]
            for row in csv.DictReader(f, delimiter='\t'):
                batch.append((row['synset_id'],row['lemmas'],row['pos'],row['definition'],int(row['is_basis'].lower()=='true'),'[]','[]'))
            db.executemany('INSERT INTO senses VALUES(?,?,?,?,?,?,?)', batch)
        identities = {row[0] for row in batch}
        lemma_rows=[]
        indexed_identities=set()
        for row in rows(BUNDLE / 'indexes' / 'senses.jsonl'):
            if row['identity'] not in identities or row['identity'] in indexed_identities:
                raise RuntimeError(f'来源索引义项缺失或重复：{row["identity"]}')
            indexed_identities.add(row['identity'])
            db.execute('UPDATE senses SET records=?,sources=? WHERE id=?', (json.dumps(row.get('source_records',[]),ensure_ascii=False),json.dumps(row.get('active_clause_sources',[]),ensure_ascii=False),row['identity']))
            labels = row.get('lemmas') or ''
            if isinstance(labels, list):
                labels = ';'.join(labels)
            for label in re.split(r'\s*/\s*|;', labels):
                if label.strip(): lemma_rows.append((label.strip().lower(),row['identity']))
        db.executemany('INSERT INTO lemma_index VALUES(?,?)',lemma_rows)
        if indexed_identities != identities:
            raise RuntimeError('来源索引未覆盖全部义项。')
        batch=[]
        graph_heads=set()
        for row in rows(graph):
            if row['head'] not in identities or row['head'] in graph_heads:
                raise RuntimeError(f'规则头节点缺失或重复：{row["head"]}')
            graph_heads.add(row['head'])
            for i, body in enumerate(row['clauses']):
                if any(dependency not in identities for dependency in body):
                    raise RuntimeError(f'规则包含不存在的前提：{row["head"]}')
                batch.append((row['head'],i,json.dumps(body,ensure_ascii=False)))
        if graph_heads != identities:
            raise RuntimeError('规则头节点未覆盖全部义项。')
        db.executemany('INSERT INTO clauses VALUES(?,?,?)',batch)
        db.executemany('INSERT INTO meta VALUES(?,?)',[('fingerprint',expected),('schema',SCHEMA),('graph_version',m['graph_version'])] + [('input:' + name, digest) for name,digest in input_hashes.items()])
        db.executescript('CREATE INDEX lemma_search ON lemma_index(lemma); CREATE INDEX clauses_head ON clauses(head);')
        db.commit()
        counts = db.execute('SELECT (SELECT count(*) FROM senses), (SELECT count(*) FROM clauses)').fetchone()
        db.close()
        db = None
        if counts != (m['head_count'],m['clause_count']):
            raise RuntimeError(f'索引数量与清单不一致：{counts}')
        temp.replace(DB)
    finally:
        if db is not None:
            db.close()
        if temp.exists(): temp.unlink()
    print('索引已完成。', flush=True)
    return m


class Graph:
    def __init__(self):
        self.clauses = {}
        self.names = {}
        with closing(connect()) as db:
            for r in db.execute('SELECT id,lemmas,pos,definition,basis FROM senses'):
                self.names[r['id']] = {'id':r['id'],'lemmas':r['lemmas'],'pos':r['pos'],'definition':r['definition'],'basis':bool(r['basis'])}
            for r in db.execute('SELECT head,idx,body FROM clauses ORDER BY head,idx'):
                self.clauses.setdefault(r['head'],[]).append(json.loads(r['body']))

    def node(self, identity):
        item = self.names.get(identity)
        if not item: return None
        with closing(connect()) as db:
            row = db.execute('SELECT records,sources FROM senses WHERE id=?',(identity,)).fetchone()
        records, sources = json.loads(row['records']), json.loads(row['sources'])
        alternatives=[]
        for i, body in enumerate(self.clauses.get(identity, [])):
            documents = next((x.get('source_documents',[]) for x in sources if x.get('clause_index') == i),[])
            alternatives.append({'index':i,'body':body,'sources':documents,'source_available':bool(documents) and all((BUNDLE / p).is_file() for p in documents)})
        return {**item, 'records':records, 'alternatives':alternatives}
