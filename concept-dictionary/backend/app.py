from __future__ import annotations

from contextlib import asynccontextmanager, closing
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .data import BUNDLE, ROOT, Graph, connect, ensure_index
from .reasoning import closure, rank_alternatives

graph: Graph
info: dict[str, Any]


@asynccontextmanager
async def lifespan(app):
    global graph, info
    info=ensure_index()
    graph=Graph()
    yield


app = FastAPI(title='Concept Dictionary', lifespan=lifespan)


class State(BaseModel):
    known: list[str] = Field(default_factory=list, max_length=5000)


class Explain(State):
    target: str
    expanded: list[str] = Field(default_factory=list, max_length=300)
    choices: dict[str,int] = Field(default_factory=dict, max_length=300)


class Explore(State):
    added: str | None = None
    query: str = ''


class SessionData(Explain):
    version: int
    fingerprint: str


def valid_known(known):
    unknown=sorted(set(known)-graph.names.keys())
    if unknown: raise HTTPException(400, f'存在未知义项：{unknown[:5]}')
    return frozenset(known)


@lru_cache(maxsize=3)
def costs_for(known):
    return closure(graph.clauses,known)


@lru_cache(maxsize=3)
def costs_for_choices(known, choices):
    # Explicit selections constrain reachability; otherwise a cyclic selected
    # branch might be credited with a different, unselected escape branch.
    rules = dict(graph.clauses)
    for identity, index in choices:
        alternatives = rules.get(identity, [])
        if 0 <= index < len(alternatives):
            rules[identity] = [alternatives[index]]
    return closure(rules, known)


@app.get('/api/health')
def health():
    return {'ready':True,'fingerprint':info['semantic_fingerprint_sha256'], 'graph_version':info['graph_version'], 'head_count':info['head_count'], 'clause_count':info['clause_count']}


@app.get('/api/search')
def search(q: str = '', limit: int = 30):
    q=q.strip().lower()
    if not q: return []
    # Escape SQL LIKE metacharacters; an exact/prefix query is fast with the index.
    q=q.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')
    limit=max(1,min(limit,100))
    with closing(connect()) as db:
        rows=db.execute("""SELECT DISTINCT s.id,s.lemmas,s.pos,s.definition FROM lemma_index l JOIN senses s ON s.id=l.sense_id
                           WHERE l.lemma LIKE ? ESCAPE '\\' ORDER BY CASE WHEN l.lemma=? THEN 0 ELSE 1 END,l.lemma,s.id LIMIT ?""",(q+'%',q,limit)).fetchall()
    return [dict(row) for row in rows]


@app.get('/api/node/{identity}')
def node(identity: str):
    value=graph.node(identity)
    if not value: raise HTTPException(404,'未找到该义项')
    return value


@app.post('/api/known')
def known_concepts(state: State):
    known=valid_known(state.known)
    return [graph.names[x] for x in sorted(known,key=lambda x:(graph.names[x]['lemmas'].lower(),x))]


@app.post('/api/session/validate')
def validate_session(state: SessionData):
    if state.version != 1 or state.fingerprint != info['semantic_fingerprint_sha256']:
        raise HTTPException(400, '解释卡片的数据版本不匹配。')
    valid_known(state.known)
    if state.target and state.target not in graph.names:
        raise HTTPException(400, '解释卡片中的目标义项不存在。')
    if any(identity not in graph.names for identity in state.expanded):
        raise HTTPException(400, '解释卡片包含不存在的展开义项。')
    for identity, index in state.choices.items():
        if identity not in graph.names or index < 0 or index >= len(graph.clauses.get(identity, [])):
            raise HTTPException(400, '解释卡片包含不存在的定义分支。')
    return {'valid': True}


@app.post('/api/explain')
def explain(state: Explain):
    if state.target not in graph.names: raise HTTPException(404,'目标义项不存在')
    known=valid_known(state.known)
    choices=tuple(sorted((identity,index) for identity,index in state.choices.items() if identity in graph.clauses and 0 <= index < len(graph.clauses[identity])))
    costs=costs_for_choices(known, choices) if choices else costs_for(known)
    expanded=set(state.expanded) | {state.target}
    budget=[300]
    def build(identity, path):
        item=graph.names.get(identity)
        if not item: return {'id':identity,'missing_node':True,'status':'missing'}
        base={**item,'known':identity in known,'reachable':identity in costs}
        if identity in known: return {**base,'status':'known'}
        if identity in path: return {**base,'status':'cycle'}
        if identity not in expanded: return {**base,'status':'collapsed'}
        budget[0]-=1
        if budget[0]<0: return {**base,'status':'limit'}
        full=graph.node(identity)
        alternatives=full['alternatives']
        ranks=rank_alternatives([x['body'] for x in alternatives],costs)
        if not ranks: return {**base,'status':'no_definition','alternatives':[]}
        chosen=state.choices.get(identity,ranks[0]['index'])
        if not isinstance(chosen,int) or chosen<0 or chosen>=len(alternatives): chosen=ranks[0]['index']
        rank_map={r['index']:r for r in ranks}
        for alternative in alternatives:
            alternative.update(rank_map[alternative['index']])
        body=alternatives[chosen]['body']
        return {**base,'status':'expanded','selected':chosen,'alternatives':alternatives,
                'children':[build(dep,path | {identity}) for dep in body]}
    return {'target':state.target,'known_count':len(known),'tree':build(state.target,set()),'fingerprint':info['semantic_fingerprint_sha256']}


@app.post('/api/explore')
def explore(state: Explore):
    known=valid_known(state.known)
    base=costs_for(known)
    after=base
    if state.added:
        if state.added not in graph.names: raise HTTPException(404,'新增义项不存在')
        after=costs_for(known | {state.added})
    # Counts include graph heads only, and exclude user-known concepts.
    candidates=set(after) & graph.names.keys() - set(known)
    if state.added: candidates -= set(base); candidates.discard(state.added)
    query=state.query.strip().lower()
    filtered=[x for x in candidates if not query or query in graph.names[x]['lemmas'].lower()]
    filtered.sort(key=lambda x:(after[x],graph.names[x]['lemmas'].lower(),x))
    return {'total':len(candidates),'matched':len(filtered),'items':[graph.names[x] | {'cost':after[x]} for x in filtered[:50]],'truncated':len(filtered)>50,'added':state.added}


dist=ROOT/'frontend'/'dist'
if dist.is_dir():
    app.mount('/assets', StaticFiles(directory=dist/'assets'), name='assets')
    @app.get('/')
    def index(): return FileResponse(dist/'index.html')
