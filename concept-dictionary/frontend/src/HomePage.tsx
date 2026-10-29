import type { Dispatch, SetStateAction } from "react";
import {
  Search,
  X,
  ArrowRight,
  ArrowUpRight,
  Info,
  BookOpen,
} from "lucide-react";
import { label, type Sense, type Health, type RecentPath } from "./types";

type Props = {
  query: string;
  setQuery: (value: string) => void;
  results: Sense[];
  setResults: (value: Sense[]) => void;
  activeResult: number;
  setActiveResult: Dispatch<SetStateAction<number>>;
  searching: boolean;
  setSearching: (value: boolean) => void;
  health: Health | null;
  recent: RecentPath[];
  choose: (sense: Sense) => void;
  chooseExample: (
    id: string,
    expanded: string[],
    choices: Record<string, number>,
  ) => Promise<void>;
  resume: (item: RecentPath) => Promise<void>;
};
export function HomePage({
  query,
  setQuery,
  results,
  setResults,
  activeResult,
  setActiveResult,
  searching,
  setSearching,
  health,
  recent,
  choose,
  chooseExample,
  resume,
}: Props) {
  return (
    <div className="home page">
      <div className="hero-layout">
        <div className="hero-intro">
          <div className="eyebrow">
            <span className="tiny-spark">✦</span> 一座可以探索的概念词典
          </div>
          <h1>
            从一个问题开始，
            <br />
            <span>找到理解的路径。</span>
          </h1>
          <p className="hero-copy">
            输入一个想理解的词。从你熟悉的概念出发，
            <br />
            逐步展开它的定义，直到看清每一步。
          </p>
          <div className="search-wrap">
            <Search size={22} />
            <input
              role="combobox"
              aria-label="搜索英文概念"
              aria-autocomplete="list"
              aria-expanded={Boolean(query && results.length)}
              aria-controls="sense-results"
              aria-activedescendant={
                activeResult >= 0 ? `sense-option-${activeResult}` : undefined
              }
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setResults([]);
                setSearching(Boolean(e.target.value.trim()));
              }}
              onKeyDown={(e) => {
                if (e.key === "ArrowDown" && results.length) {
                  e.preventDefault();
                  setActiveResult((i) => Math.min(i + 1, results.length - 1));
                }
                if (e.key === "ArrowUp" && results.length) {
                  e.preventDefault();
                  setActiveResult((i) => Math.max(i - 1, 0));
                }
                if (
                  e.key === "Enter" &&
                  activeResult >= 0 &&
                  results[activeResult]
                ) {
                  e.preventDefault();
                  choose(results[activeResult]);
                }
                if (e.key === "Escape") {
                  setQuery("");
                  setResults([]);
                  setActiveResult(-1);
                }
              }}
              placeholder="搜索英文词语，例如 square"
            />
            <span className="search-key">SEARCH</span>
            {query && (
              <button
                className="clear"
                onClick={() => setQuery("")}
                aria-label="清除搜索"
              >
                <X size={16} />
              </button>
            )}
            {query && (
              <div
                id="sense-results"
                role="listbox"
                aria-label="搜索到的义项"
                className="search-results"
              >
                {searching ? (
                  <div className="search-empty">正在搜索…</div>
                ) : results.length ? (
                  results.map((s, i) => (
                    <button
                      role="option"
                      aria-selected={i === activeResult}
                      id={`sense-option-${i}`}
                      key={s.id}
                      className={i === activeResult ? "keyboard-active" : ""}
                      onMouseEnter={() => setActiveResult(i)}
                      onClick={() => choose(s)}
                    >
                      <span>
                        <b>{label(s)}</b>
                        <small>
                          {s.pos} · {s.definition}
                        </small>
                      </span>
                      <ArrowUpRight size={16} />
                    </button>
                  ))
                ) : (
                  <div className="search-empty">
                    没有找到匹配的义项，试试其他英文词形。
                  </div>
                )}
              </div>
            )}
          </div>
          <div className="hint">
            试试搜索 <button onClick={() => setQuery("square")}>square</button>
            <button onClick={() => setQuery("book")}>book</button>
            <button onClick={() => setQuery("light")}>light</button>
          </div>
          <div className="hero-meta">
            <span>
              <i />
              本地词典
            </span>
            <span>
              {health ? health.head_count.toLocaleString() : "…"} 个义项
            </span>
            <span>保留来源与分支</span>
          </div>
        </div>
        <div
          className="constellation"
          aria-label="square 与 rectangle 的局部图谱示意"
        >
          <div className="constellation-top">
            <span>PATH PREVIEW</span>
            <span>图谱节选</span>
          </div>
          <div className="orbit orbit-one" />
          <div className="orbit orbit-two" />
          <div className="orbit orbit-three" />
          <svg
            className="constellation-lines"
            viewBox="0 0 440 340"
            aria-hidden="true"
          >
            <path d="M217 155 Q157 116 97 107 M217 155 Q275 112 334 89 M217 155 Q280 188 345 229 M217 155 Q170 216 115 251" />
          </svg>
          <span className="star star-a" />
          <span className="star star-b" />
          <span className="star star-c" />
          <span className="star star-d" />
          <div className="orbit-node primary-node">
            <span className="orbit-dot" />
            <b>square</b>
            <small>目标义项</small>
          </div>
          <div className="orbit-node node-a">
            <span className="orbit-dot" />
            <b>rectangle</b>
            <small>联合前提之一</small>
          </div>
          <div className="orbit-node node-b">
            <span className="orbit-dot" />
            <b>equal</b>
            <small>联合前提之一</small>
          </div>
          <div className="orbit-node node-c">
            <span className="orbit-dot" />
            <b>angle</b>
            <small>联合前提之一</small>
          </div>
          <div className="orbit-node node-d">
            <span className="orbit-dot" />
            <b>plane</b>
            <small>联合前提之一</small>
          </div>
          <button
            className="visual-action"
            onClick={() =>
              chooseExample("oewn-13901273-n", ["oewn-13901273-n"], {})
            }
          >
            打开完整路径 <ArrowRight size={14} />
          </button>
          <span className="visual-caption">展示部分依赖 · 义项映射待审核</span>
        </div>
      </div>
      <div className="home-lower">
        {recent.length > 0 && (
          <div className="recent-section">
            <div className="section-heading">
              <div>
                <span className="section-kicker">CONTINUE EXPLORING</span>
                <h2>继续上次的探索</h2>
              </div>
            </div>
            <div className="recent-list">
              {recent.slice(0, 3).map((item) => (
                <button key={item.target} onClick={() => resume(item)}>
                  <BookOpen size={16} />
                  <span>
                    <b>{item.name}</b>
                    <small>恢复上次选择的分支</small>
                  </span>
                  <ArrowRight size={15} />
                </button>
              ))}
            </div>
          </div>
        )}
        <div className="examples">
          <div className="section-heading">
            <div>
              <span className="section-kicker">START EXPLORING</span>
              <h2>从一条路径开始</h2>
            </div>
          </div>
          <div className="example-grid">
            <button
              onClick={() =>
                chooseExample("oewn-13901273-n", ["oewn-13901273-n"], {})
              }
            >
              <b>square</b>
              <span>多前提的几何义项</span>
              <ArrowRight size={15} />
            </button>
            <button onClick={() => chooseExample("about-1", ["about-1"], {})}>
              <b>about</b>
              <span>多分支与外部资源</span>
              <ArrowRight size={15} />
            </button>
            <button
              onClick={() =>
                chooseExample("in-5", ["in-5", "oewn-04937655-n"], {
                  "in-5": 0,
                  "oewn-04937655-n": 0,
                })
              }
            >
              <b>in → form → in</b>
              <span>查看循环阻塞</span>
              <ArrowRight size={15} />
            </button>
          </div>
          <p>案例已核对图结构与来源映射；语义尚未独立审核。</p>
        </div>
        <div className="dataset-note">
          <Info size={16} />
          <span>
            基于本地冻结词典数据 ·{" "}
            {health
              ? `${health.head_count.toLocaleString()} 个义项 · ${health.clause_count.toLocaleString()} 条定义分支`
              : "正在连接数据"}
            。路径的结构可追溯，语义审核状态请查看依据。
          </span>
        </div>
      </div>
    </div>
  );
}
