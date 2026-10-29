import {
  Compass,
  Search,
  X,
  ArrowRight,
  Sparkles,
  CircleHelp,
} from "lucide-react";
import { label, type Sense, type ExploreResult } from "./types";

type Props = {
  count: number;
  added: Sense | null;
  setAdded: (value: Sense | null) => void;
  busy: boolean;
  explore: ExploreResult | null;
  filter: string;
  setFilter: (value: string) => void;
  addQuery: string;
  setAddQuery: (value: string) => void;
  addResults: Sense[];
  setAddResults: (value: Sense[]) => void;
  choose: (sense: Sense) => void;
  goHome: () => void;
};
export function ExplorePage({
  count,
  added,
  setAdded,
  busy,
  explore,
  filter,
  setFilter,
  addQuery,
  setAddQuery,
  addResults,
  setAddResults,
  choose,
  goHome,
}: Props) {
  return (
    <div className="page explore-page">
      <span className="section-kicker">EXPLORE WHAT'S POSSIBLE</span>
      <h1>已知的，还能带你去哪？</h1>
      <p className="lead">
        从你标记的概念出发，查看当前图中可以完整展开的目标。
      </p>
      <div className="explore-layout">
        <div className="explore-main">
          <div className="metric-row">
            <div>
              <span>当前已知</span>
              <strong>{count}</strong>
              <small>由你主动确认</small>
            </div>
            <div>
              <span>{added ? "新增后增加" : "可展开目标"}</span>
              <strong>
                {busy ? "…" : (explore?.total.toLocaleString() ?? "—")}
              </strong>
              <small>按完整定义前提计算</small>
            </div>
          </div>
          <div className="result-heading">
            <div>
              <h2>
                {added
                  ? `加入 ${label(added)} 后新增的目标`
                  : "当前可展开的目标"}
              </h2>
              <p>从任意可用分支计算图中可达；不代表已经理解或推荐学习顺序。</p>
            </div>
            <input
              className="filter"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              placeholder="筛选结果"
              aria-label="筛选结果"
            />
          </div>
          {busy ? (
            <div className="empty-state">正在计算完整前提…</div>
          ) : explore?.items.length ? (
            <div className="explore-results">
              {explore.items.map((s) => (
                <button key={s.id} onClick={() => choose(s)}>
                  <div>
                    <b>{label(s)}</b>
                    <small>
                      {s.pos} · {s.definition}
                    </small>
                  </div>
                  <ArrowRight size={16} />
                </button>
              ))}
              {explore.truncated && (
                <div className="results-note">
                  显示前 50 条，共 {explore.matched.toLocaleString()}{" "}
                  条匹配；可输入词形继续筛选。
                </div>
              )}
            </div>
          ) : (
            <div className="empty-state">
              <Compass size={26} />
              <b>还没有可展示的目标</b>
              <span>
                {count
                  ? "试试加入其他概念或清除筛选条件。"
                  : "先在解释中标记你已经理解的概念。"}
              </span>
              <button className="button secondary" onClick={goHome}>
                去搜索概念 <ArrowRight size={15} />
              </button>
            </div>
          )}
        </div>
        <aside className="experiment-card">
          <span className="experiment-icon">
            <Sparkles size={19} />
          </span>
          <h3>试试加入一个概念</h3>
          <p>比较加入前后的可达目标，观察这个概念可能带来的变化。</p>
          {added ? (
            <div className="added">
              <span>
                {label(added)}
                <small>{added.id}</small>
              </span>
              <button onClick={() => setAdded(null)} aria-label="移除试算概念">
                <X size={15} />
              </button>
            </div>
          ) : (
            <div className="add-search">
              <Search size={16} />
              <input
                value={addQuery}
                onChange={(e) => setAddQuery(e.target.value)}
                placeholder="搜索英文概念"
              />
              {addResults.length > 0 && (
                <div className="add-results">
                  {addResults.slice(0, 8).map((s) => (
                    <button
                      key={s.id}
                      onClick={() => {
                        setAdded(s);
                        setAddQuery("");
                        setAddResults([]);
                      }}
                    >
                      <b>{label(s)}</b>
                      <small>{s.definition}</small>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
          <div className="experiment-note">
            <CircleHelp size={15} />
            这是一次假设计算，不会自动把它标记为你已理解。
          </div>
        </aside>
      </div>
    </div>
  );
}
