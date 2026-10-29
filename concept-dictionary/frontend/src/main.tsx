import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { createRoot } from "react-dom/client";
import {
  BookOpen,
  Search,
  Network,
  Compass,
  Settings2,
  ChevronRight,
  X,
  Check,
  Info,
  Download,
  Upload,
  Share2,
  Layers,
} from "lucide-react";
import "./style.css";
import "./settings.css";
import { api, post, encodeSession, decodeSession, validSession } from "./api";
import {
  label,
  themes,
  type Session,
  type Sense,
  type Tree,
  type Source,
  type Health,
  type ExploreResult,
  type Theme,
  type TextSize,
  type RecentPath,
} from "./types";
import { Explanation, PathTree } from "./Explanation";
import { SettingsPage } from "./SettingsPage";
import { Drawer } from "./Drawer";
import { HomePage } from "./HomePage";
import { ExplorePage } from "./ExplorePage";
import { loadRecent, rememberPath, RECENT_KEY } from "./recentPaths";
import { visibleFrontier } from "./frontier";

const storage = "concept-dictionary-session-v1";
const empty: Session = {
  version: 1,
  fingerprint: "",
  target: "",
  known: [],
  expanded: [],
  choices: {},
};

function App() {
  const [health, setHealth] = useState<Health | null>(null),
    [session, setSession] = useState<Session>(empty),
    [tree, setTree] = useState<Tree | null>(null),
    [source, setSource] = useState<Source | null>(null);
  const [recent, setRecent] = useState<RecentPath[]>([]),
    [recentReady, setRecentReady] = useState(false);
  const [view, setView] = useState<"home" | "explain" | "explore" | "settings">(
      "home",
    ),
    [theme, setTheme] = useState<Theme>(
      () => (localStorage.getItem("concept-theme") as Theme) || "default",
    );
  const [textSize, setTextSize] = useState<TextSize>(
    () => (localStorage.getItem("concept-text-size") as TextSize) || "medium",
  );
  const [reduceMotion, setReduceMotion] = useState(
    () => localStorage.getItem("concept-reduce-motion") === "true",
  );
  const [defaultGraph, setDefaultGraph] = useState(
    () => localStorage.getItem("concept-default-graph") !== "false",
  );
  const [query, setQuery] = useState(""),
    [results, setResults] = useState<Sense[]>([]),
    [activeResult, setActiveResult] = useState(-1),
    [searching, setSearching] = useState(false),
    [error, setError] = useState(""),
    [notice, setNotice] = useState("");
  const [graphOpen, setGraphOpen] = useState(
      () => localStorage.getItem("concept-default-graph") !== "false",
    ),
    [sourceOpen, setSourceOpen] = useState(false),
    [knownOpen, setKnownOpen] = useState(false),
    [knownItems, setKnownItems] = useState<Sense[]>([]),
    [busy, setBusy] = useState(false);
  const [explore, setExplore] = useState<ExploreResult | null>(null),
    [added, setAdded] = useState<Sense | null>(null),
    [addQuery, setAddQuery] = useState(""),
    [addResults, setAddResults] = useState<Sense[]>([]),
    [filter, setFilter] = useState("");
  const upload = useRef<HTMLInputElement>(null);
  const canPersist = useRef(true);
  const update = useCallback((part: Partial<Session>) => {
    canPersist.current = true;
    setSession((s) => ({ ...s, ...part }));
  }, []);
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("concept-theme", theme);
  }, [theme]);
  useEffect(() => {
    document.documentElement.dataset.textSize = textSize;
    localStorage.setItem("concept-text-size", textSize);
  }, [textSize]);
  useEffect(() => {
    document.documentElement.dataset.reduceMotion = String(reduceMotion);
    localStorage.setItem("concept-reduce-motion", String(reduceMotion));
  }, [reduceMotion]);
  useEffect(() => {
    localStorage.setItem("concept-default-graph", String(defaultGraph));
  }, [defaultGraph]);
  useEffect(() => {
    api<Health>("/api/health")
      .then(async (h) => {
        setHealth(h);
        let saved: Session | null = null;
        try {
          const hash = location.hash.startsWith("#s=")
            ? decodeSession(location.hash.slice(3))
            : null;
          saved = hash || JSON.parse(localStorage.getItem(storage) || "null");
          if (saved && !validSession(saved, h.fingerprint))
            throw new Error("保存的路径格式或数据版本不匹配。");
          if (saved) await post("/api/session/validate", saved);
        } catch (e) {
          canPersist.current = false;
          setNotice(
            e instanceof Error
              ? `${e.message} 当前状态未导入，原本地记录保留。`
              : "无法读取保存的路径。",
          );
          saved = null;
        }
        if (saved) {
          setSession(saved);
          if (saved.target) setView("explain");
          if (location.hash.startsWith("#s="))
            history.replaceState(null, "", location.pathname + location.search);
        } else setSession({ ...empty, fingerprint: h.fingerprint });
      })
      .catch((e) => setError(`无法连接本地数据服务：${e.message}`));
  }, []);
  useEffect(() => {
    if (
      canPersist.current &&
      health &&
      session.fingerprint === health.fingerprint
    )
      localStorage.setItem(storage, JSON.stringify(session));
  }, [session, health]);
  useEffect(() => {
    if (health) {
      setRecent(
        loadRecent(
          localStorage.getItem(`${RECENT_KEY}:${health.fingerprint}`),
          health.fingerprint,
        ),
      );
      setRecentReady(true);
    }
  }, [health]);
  useEffect(() => {
    if (recentReady && health)
      localStorage.setItem(
        `${RECENT_KEY}:${health.fingerprint}`,
        JSON.stringify(recent),
      );
  }, [recent, recentReady, health]);
  useEffect(() => {
    if (
      recentReady &&
      tree &&
      tree.id === session.target &&
      session.fingerprint
    )
      setRecent((items) => rememberPath(items, session, label(tree)));
  }, [recentReady, tree, session]);
  useEffect(() => {
    if (query.trim().length < 1) {
      setResults([]);
      setSearching(false);
      return;
    }
    const c = new AbortController();
    let current = true;
    const timer = setTimeout(() => {
      setSearching(true);
      api<Sense[]>("/api/search?q=" + encodeURIComponent(query), {
        signal: c.signal,
      })
        .then((data) => {
          if (current) {
            setResults(data);
            setActiveResult(-1);
          }
        })
        .catch((e) => {
          if (current && e.name !== "AbortError") setError(e.message);
        })
        .finally(() => {
          if (current) setSearching(false);
        });
    }, 200);
    return () => {
      current = false;
      clearTimeout(timer);
      c.abort();
    };
  }, [query]);
  useEffect(() => {
    if (activeResult >= 0)
      document
        .getElementById(`sense-option-${activeResult}`)
        ?.scrollIntoView({ block: "nearest" });
  }, [activeResult]);
  useEffect(() => {
    if (!session.target || view !== "explain") return;
    let active = true;
    setBusy(true);
    post<{ tree: Tree }>("/api/explain", session)
      .then((r) => {
        if (active) setTree(r.tree);
      })
      .catch((e) => {
        if (active) setError(e.message);
      })
      .finally(() => {
        if (active) setBusy(false);
      });
    return () => {
      active = false;
    };
  }, [session, view]);
  useEffect(() => {
    if (view !== "explore") return;
    let active = true;
    setBusy(true);
    post<ExploreResult>("/api/explore", {
      known: session.known,
      added: added?.id || null,
      query: filter,
    })
      .then((r) => {
        if (active) setExplore(r);
      })
      .catch((e) => {
        if (active) setError(e.message);
      })
      .finally(() => {
        if (active) setBusy(false);
      });
    return () => {
      active = false;
    };
  }, [view, session.known, added, filter]);
  useEffect(() => {
    if (!addQuery.trim()) {
      setAddResults([]);
      return;
    }
    const t = setTimeout(
      () =>
        api<Sense[]>("/api/search?q=" + encodeURIComponent(addQuery))
          .then(setAddResults)
          .catch((e) => setError(e.message)),
      250,
    );
    return () => clearTimeout(t);
  }, [addQuery]);
  useEffect(() => {
    if (knownOpen)
      post<Sense[]>("/api/known", { known: session.known })
        .then(setKnownItems)
        .catch((e) => setError(e.message));
  }, [knownOpen, session.known]);
  const choose = (s: Sense) => {
    update({ target: s.id, expanded: [s.id], choices: {} });
    setGraphOpen(defaultGraph);
    setQuery("");
    setResults([]);
    setTree(null);
    setView("explain");
    setSourceOpen(false);
  };
  const chooseExample = async (
    id: string,
    expanded: string[],
    choices: Record<string, number>,
  ) => {
    try {
      await api<Source>("/api/node/" + encodeURIComponent(id));
      update({ target: id, expanded, choices });
      setGraphOpen(defaultGraph);
      setTree(null);
      setView("explain");
      setSourceOpen(false);
    } catch (e) {
      setError(String(e));
    }
  };
  const resume = async (item: RecentPath) => {
    const next = {
      ...session,
      target: item.target,
      expanded: item.expanded,
      choices: item.choices,
    };
    try {
      await post("/api/session/validate", next);
      update(next);
      setGraphOpen(defaultGraph);
      setTree(null);
      setView("explain");
    } catch (e) {
      setError(e instanceof Error ? e.message : "无法恢复这条路径。");
    }
  };
  const toggleKnown = (id: string) => {
    canPersist.current = true;
    setSession((s) => ({
      ...s,
      known: s.known.includes(id)
        ? s.known.filter((x) => x !== id)
        : [...s.known, id],
    }));
  };
  const toggleExpand = (id: string) => {
    canPersist.current = true;
    setSession((s) => ({
      ...s,
      expanded: s.expanded.includes(id)
        ? s.expanded.filter((x) => x !== id)
        : [...s.expanded, id],
    }));
  };
  const seeSource = async (id: string) => {
    try {
      setSource(await api<Source>("/api/node/" + encodeURIComponent(id)));
      setSourceOpen(true);
    } catch (e) {
      setError(String(e));
    }
  };
  const restore = async (s: Session) => {
    if (!health || !validSession(s, health.fingerprint)) {
      setError("文件格式无效，或文件与当前数据版本不一致。");
      return;
    }
    try {
      await post("/api/session/validate", s);
      canPersist.current = true;
      setSession(s);
      setView(s.target ? "explain" : "home");
      setNotice("已恢复解释路径和已知概念。");
    } catch (e) {
      setError(e instanceof Error ? e.message : "无法验证解释卡片。");
    }
  };
  const exportSession = () => {
    const blob = new Blob([JSON.stringify(session, null, 2)], {
        type: "application/json",
      }),
      url = URL.createObjectURL(blob),
      a = document.createElement("a");
    a.href = url;
    a.download = "concept-path.json";
    a.click();
    URL.revokeObjectURL(url);
  };
  const share = async () => {
    try {
      const url =
        location.origin + location.pathname + "#s=" + encodeSession(session);
      if (url.length > 8000) {
        setError("路径太长，无法可靠生成链接；请使用导出文件分享。");
        return;
      }
      await navigator.clipboard.writeText(url);
      setNotice("本机链接已复制；在相同数据版本的本地实例中打开。");
    } catch {
      setError("复制失败，可使用导出文件分享路径。");
    }
  };
  const importFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    try {
      const f = e.target.files?.[0];
      if (f) {
        if (f.size > 1024 * 1024)
          throw new Error("解释卡片超过 1 MB，请选择较小的文件。");
        await restore(JSON.parse(await f.text()));
      }
    } catch (e) {
      setError(
        e instanceof SyntaxError
          ? "无法读取解释卡片，请选择有效的 JSON 文件。"
          : e instanceof Error
            ? e.message
            : "无法读取解释卡片。",
      );
    }
    e.target.value = "";
  };
  const count = useMemo(() => session.known.length, [session.known]);
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <button className="brand" onClick={() => setView("home")}>
          <span className="brand-mark">
            <Layers size={20} />
          </span>
          <span>
            <b>知径</b>
            <small>CONCEPT PATH</small>
          </span>
        </button>
        <div className="sidebar-label">工作空间</div>
        <nav>
          <button
            className={view === "home" ? "active" : ""}
            onClick={() => setView("home")}
          >
            <Search size={17} />
            发现概念
          </button>
          <button
            className={view === "explain" ? "active" : ""}
            onClick={() =>
              session.target ? setView("explain") : setView("home")
            }
          >
            <BookOpen size={17} />
            我的解释
          </button>
          <button
            className={view === "explore" ? "active" : ""}
            onClick={() => setView("explore")}
          >
            <Compass size={17} />
            探索可能
          </button>
          <button
            className={
              "mobile-settings " + (view === "settings" ? "active" : "")
            }
            aria-label="设置"
            onClick={() => setView("settings")}
          >
            <Settings2 size={17} />
            设置
          </button>
        </nav>
        {recent.length > 0 && (
          <div className="sidebar-history">
            <div className="sidebar-label">最近探索</div>
            {recent.slice(0, 4).map((item) => (
              <button
                key={item.target}
                title={item.name}
                onClick={() => resume(item)}
              >
                <BookOpen size={14} />
                <span>{item.name}</span>
              </button>
            ))}
          </div>
        )}
        <div className="sidebar-bottom">
          <button className="known-summary" onClick={() => setKnownOpen(true)}>
            <span className="known-icon">
              <Check size={16} />
            </span>
            <div>
              <b>{count} 个已知概念</b>
              <small>查看和管理</small>
            </div>
          </button>
          <button
            className={
              "settings-button " + (view === "settings" ? "active" : "")
            }
            onClick={() => setView("settings")}
          >
            <Settings2 size={17} />
            设置 <ChevronRight size={15} />
          </button>
        </div>
      </aside>
      <main className="main">
        <header className="topbar">
          <div className="breadcrumb">
            知识探索 <span>/</span>{" "}
            {view === "home"
              ? "发现概念"
              : view === "explain"
                ? "我的解释"
                : view === "explore"
                  ? "探索可能"
                  : "设置"}
          </div>
          <div className="top-actions">
            <span className="status-dot" />
            <span className="connection-label">
              {health ? "本地数据" : "连接中"}
            </span>
            <button
              className="mobile-known icon-button"
              aria-label="管理已知概念"
              onClick={() => setKnownOpen(true)}
            >
              <Check size={16} />
            </button>
            <label className="mobile-theme">
              <span>主题</span>
              <select
                aria-label="选择主题"
                value={theme}
                onChange={(e) => setTheme(e.target.value as Theme)}
              >
                {themes.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.label}
                  </option>
                ))}
              </select>
            </label>
            <button
              className="icon-button"
              aria-label="导入解释卡片"
              title="导入解释卡片"
              onClick={() => upload.current?.click()}
            >
              <Upload size={17} />
            </button>
            <input
              ref={upload}
              type="file"
              accept="application/json,.json"
              hidden
              onChange={importFile}
            />
          </div>
        </header>
        {error && (
          <div className="alert error" role="alert">
            {error}
            <button onClick={() => setError("")}>
              <X size={16} />
            </button>
          </div>
        )}
        {notice && (
          <div className="alert" role="status">
            {notice}
            <button onClick={() => setNotice("")}>
              <X size={16} />
            </button>
          </div>
        )}
        {view === "home" && (
          <HomePage
            query={query}
            setQuery={setQuery}
            results={results}
            setResults={setResults}
            activeResult={activeResult}
            setActiveResult={setActiveResult}
            searching={searching}
            setSearching={setSearching}
            health={health}
            recent={recent}
            choose={choose}
            chooseExample={chooseExample}
            resume={resume}
          />
        )}
        {view === "explain" && (
          <div className="workspace page">
            <div className="workspace-title">
              <div>
                <span className="section-kicker">YOUR EXPLANATION</span>
                <h1>沿着解释，一步步理解</h1>
                <p>已理解的概念会成为起点。点击一个概念，决定下一步。</p>
              </div>
              <div className="workspace-actions">
                <button
                  className={
                    "button secondary " + (graphOpen ? "selected" : "")
                  }
                  onClick={() => setGraphOpen(!graphOpen)}
                >
                  <Network size={16} />
                  路径图
                </button>
                <button className="button secondary" onClick={share}>
                  <Share2 size={16} />
                  分享
                </button>
                <button className="button secondary" onClick={exportSession}>
                  <Download size={16} />
                  导出
                </button>
              </div>
            </div>
            {busy && !tree && <div className="loading">正在计算解释路径…</div>}
            {tree && (
              <div className={"workspace-grid " + (!graphOpen ? "single" : "")}>
                <div className="reading-column">
                  <div className="reading-head">
                    <span>当前解释 · {visibleFrontier(tree)} 个待处理</span>
                    <span aria-live="polite">
                      {busy ? "正在更新路径… · " : ""}
                      {count} 个已知概念
                    </span>
                  </div>
                  <Explanation
                    node={tree}
                    depth={0}
                    path="root"
                    onKnown={toggleKnown}
                    onExpand={toggleExpand}
                    onChoice={(id, index) => {
                      canPersist.current = true;
                      setSession((s) => ({
                        ...s,
                        choices: { ...s.choices, [id]: index },
                      }));
                    }}
                    onSource={seeSource}
                  />
                  <div className="reading-foot">
                    <Info size={15} />
                    “可展开”表示当前图中存在从已知概念出发的结构路径，并不表示已经掌握。
                  </div>
                </div>
                {graphOpen && (
                  <aside className="path-panel">
                    <div className="panel-header">
                      <div>
                        <span className="section-kicker">PATH VIEW</span>
                        <h3>当前路径</h3>
                      </div>
                      <button
                        className="icon-button"
                        aria-label="关闭路径图"
                        onClick={() => setGraphOpen(false)}
                      >
                        <X size={16} />
                      </button>
                    </div>
                    <p>
                      同一组里的前提需要一起满足；不同分支可在解释卡片切换。
                    </p>
                    <PathTree
                      node={tree}
                      path="root"
                      onLocate={(id) =>
                        document.getElementById("node-" + id)?.scrollIntoView({
                          behavior: reduceMotion ? "auto" : "smooth",
                          block: "center",
                        })
                      }
                    />
                    <div className="legend">
                      <span>
                        <i className="known" />
                        已标记理解
                      </span>
                      <span>
                        <i className="unresolved" />
                        尚待处理
                      </span>
                    </div>
                  </aside>
                )}
              </div>
            )}
          </div>
        )}
        {view === "explore" && (
          <ExplorePage
            count={count}
            added={added}
            setAdded={setAdded}
            busy={busy}
            explore={explore}
            filter={filter}
            setFilter={setFilter}
            addQuery={addQuery}
            setAddQuery={setAddQuery}
            addResults={addResults}
            setAddResults={setAddResults}
            choose={choose}
            goHome={() => setView("home")}
          />
        )}
        {view === "settings" && (
          <SettingsPage
            health={health}
            theme={theme}
            setTheme={setTheme}
            textSize={textSize}
            setTextSize={setTextSize}
            reduceMotion={reduceMotion}
            setReduceMotion={setReduceMotion}
            defaultGraph={defaultGraph}
            setDefaultGraph={setDefaultGraph}
            knownCount={count}
            recentCount={recent.length}
            onClearRecent={() => {
              if (
                window.confirm(
                  "确定清除最近探索记录？当前解释和已知概念会保留。",
                )
              ) {
                setRecent([]);
                setNotice("最近探索记录已清除。");
              }
            }}
            openKnown={() => setKnownOpen(true)}
            onImport={() => upload.current?.click()}
            onExport={exportSession}
            onReset={() => {
              if (
                window.confirm(
                  "确定重置当前目标、已知概念和展开记录？建议先导出需要保留的解释卡片。",
                )
              ) {
                canPersist.current = true;
                setSession({
                  ...empty,
                  fingerprint: health?.fingerprint || "",
                });
                setTree(null);
                setNotice("学习状态已重置。");
              }
            }}
          />
        )}
        <footer>
          <span>知径 · 概念解释探索</span>
          <span>
            本地研究原型 <span className="footer-separator">/</span>{" "}
            解释路径保留来源
          </span>
        </footer>
      </main>
      {sourceOpen && source && (
        <Drawer
          titleId="source-drawer-title"
          onClose={() => setSourceOpen(false)}
        >
          <div className="panel-header">
            <div>
              <span className="section-kicker">SOURCE & EVIDENCE</span>
              <h2 id="source-drawer-title">查看依据</h2>
            </div>
            <button
              className="icon-button"
              aria-label="关闭依据"
              onClick={() => setSourceOpen(false)}
            >
              <X size={19} />
            </button>
          </div>
          <h3>{label(source)}</h3>
          <p className="sense-id">
            {source.id} · {source.pos}
          </p>
          <div className="source-block">
            <span>冻结快照释义</span>
            <p>{source.definition || "当前没有可显示的原始释义。"}</p>
          </div>
          <div className="source-block">
            <span>审核状态</span>
            <p>来源与图结构可追溯；目前没有可展示的独立语义审核结论。</p>
          </div>
          <div className="source-block">
            <span>分支与来源映射</span>
            {source.alternatives.map((a) => (
              <div className="source-record" key={a.index}>
                <b>分支 {a.index + 1}</b>
                <p>{a.body.join(" + ") || "无前提"}</p>
                {a.sources.map((p) => (
                  <code key={p}>
                    {p}
                    <br />
                  </code>
                ))}
                {!a.source_available && <small>来源文件不可用。</small>}
              </div>
            ))}
          </div>
          <div className="source-block">
            <span>来源记录</span>
            {source.records.length ? (
              source.records.map((r, i) => (
                <div className="source-record" key={i}>
                  <code>{r.path}</code>
                  <p>
                    {r.raw_definition ||
                      r.effective_definition ||
                      "来源记录未提供定义文本。"}
                  </p>
                  <small>
                    原记录状态：{r.status || "未记录"}，不等同语义审核。
                  </small>
                </div>
              ))
            ) : (
              <p>未找到来源记录。</p>
            )}
          </div>
          <div className="source-block">
            <span>版本指纹</span>
            <code className="fingerprint">{health?.fingerprint}</code>
          </div>
        </Drawer>
      )}
      {knownOpen && (
        <Drawer
          titleId="known-drawer-title"
          onClose={() => setKnownOpen(false)}
        >
          <div className="panel-header">
            <div>
              <span className="section-kicker">YOUR KNOWLEDGE</span>
              <h2 id="known-drawer-title">已知概念</h2>
            </div>
            <button
              className="icon-button"
              aria-label="关闭已知概念"
              onClick={() => setKnownOpen(false)}
            >
              <X size={19} />
            </button>
          </div>
          <p className="sense-id">这些义项由你主动标记，可以随时撤销。</p>
          {knownItems.length ? (
            knownItems.map((item) => (
              <div className="source-record" key={item.id}>
                <b>{label(item)}</b>
                <p>{item.definition}</p>
                <small>{item.id}</small>
                <button
                  className="known-remove"
                  onClick={() => toggleKnown(item.id)}
                >
                  撤销已理解
                </button>
              </div>
            ))
          ) : (
            <p className="sense-id">尚未标记任何已知概念。</p>
          )}
        </Drawer>
      )}
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
