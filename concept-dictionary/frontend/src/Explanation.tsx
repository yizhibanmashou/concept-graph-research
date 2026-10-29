import {
  BookOpen,
  Check,
  Plus,
  PanelRight,
  ArrowUpRight,
  ArrowRight,
  ChevronRight,
} from "lucide-react";
import { label, type Tree } from "./types";

export function Explanation({
  node,
  depth,
  path,
  onKnown,
  onExpand,
  onChoice,
  onSource,
}: {
  node: Tree;
  depth: number;
  path: string;
  onKnown: (id: string) => void;
  onExpand: (id: string) => void;
  onChoice: (id: string, n: number) => void;
  onSource: (id: string) => void;
}) {
  const selected = node.alternatives?.find((a) => a.index === node.selected);
  return (
    <div
      id={"node-" + path}
      className={"explanation-node depth-" + Math.min(depth, 2)}
    >
      <div className="concept-title">
        <div className="concept-title-left">
          <span className={"concept-badge " + (node.known ? "understood" : "")}>
            {node.known ? (
              <Check size={14} />
            ) : depth === 0 ? (
              <BookOpen size={15} />
            ) : (
              <span>{depth}</span>
            )}
          </span>
          <div>
            <div className="concept-label">
              {depth === 0 ? "目标概念" : "定义前提"}{" "}
              <span>· {node.pos || "义项"}</span>
            </div>
            <h2>{label(node)}</h2>
          </div>
        </div>
        <div className="concept-actions">
          <button
            className={"known-button " + (node.known ? "is-known" : "")}
            onClick={() => onKnown(node.id)}
          >
            {node.known ? (
              <>
                <Check size={14} />
                已理解
              </>
            ) : (
              <>
                <Plus size={14} />
                我懂
              </>
            )}
          </button>
          <button
            className="icon-button"
            aria-label="查看依据"
            title="查看依据"
            onClick={() => onSource(node.id)}
          >
            <PanelRight size={17} />
          </button>
        </div>
      </div>
      <p className="definition">
        {node.definition || "暂无可显示的原始释义。"}
      </p>
      <div className="concept-meta">
        <span>{node.id}</span>
        <button onClick={() => onSource(node.id)}>
          查看来源 <ArrowUpRight size={13} />
        </button>
      </div>
      {(node.pos === "prep" || node.pos === "prep_phrase") && (
        <div className="status-message warning">
          这是介词依赖节点，可能引入广泛关联，也可能表达方向或否定；请结合来源判断。
        </div>
      )}
      {node.status === "cycle" && (
        <div className="status-message warning">
          这条展开再次引用了当前路径中的概念，形成循环。请换分支或标记你理解的概念。
        </div>
      )}
      {node.status === "missing" && (
        <div className="status-message warning">当前数据中未找到这个前提。</div>
      )}
      {node.status === "no_definition" && (
        <div className="status-message warning">
          当前数据没有可展开的定义分支。
        </div>
      )}
      {node.status === "limit" && (
        <div className="status-message warning">
          当前展示达到节点上限，请折叠部分路径后继续。
        </div>
      )}
      {node.status === "collapsed" && !node.known && (
        <button className="expand-button" onClick={() => onExpand(node.id)}>
          <Plus size={15} />
          解释这个概念 <ArrowRight size={14} />
        </button>
      )}
      {node.status === "expanded" && (
        <>
          <div className="branch-header">
            <div>
              <span className="section-kicker">DEFINITION PATH</span>
              <h3>图谱记录的联合前提</h3>
            </div>
            <div className="branch-actions">
              {depth > 0 && (
                <button onClick={() => onExpand(node.id)}>收起</button>
              )}
              {node.alternatives && node.alternatives.length > 1 && (
                <label>
                  切换分支{" "}
                  <select
                    value={node.selected}
                    onChange={(e) => onChoice(node.id, Number(e.target.value))}
                    aria-label="切换定义分支"
                  >
                    {node.alternatives.map((a) => (
                      <option key={a.index} value={a.index}>
                        分支 {a.index + 1} ·{" "}
                        {a.index !== node.selected
                          ? "切换后重算"
                          : a.complete
                            ? "可完整展开"
                            : `尚缺 ${a.missing.length} 项`}
                      </option>
                    ))}
                  </select>
                </label>
              )}
            </div>
          </div>
          <div className="branch-note">
            同一分支里的前提需要一起考虑（AND）；不同分支是替代的构造路径（OR）。{" "}
            {selected?.complete
              ? "根据当前已知概念，这条分支可以在图中完整展开。"
              : `这条分支仍有 ${selected?.missing.length || 0} 个前提无法从当前已知集合完整展开。`}{" "}
            {node.alternatives && node.alternatives.length > 1
              ? "系统默认优先选择可展开、展开量较小的分支；切换后重新计算。"
              : ""}{" "}
            图谱依赖与词义对应关系尚待语义审核。
          </div>
          {selected && !selected.source_available && (
            <div className="status-message warning">
              该分支的部分来源文件不可用。
            </div>
          )}
          <div className="children">
            {node.children?.map((child, i) => (
              <Explanation
                key={child.id + "-" + i}
                node={child}
                depth={depth + 1}
                path={`${path}-${i}`}
                onKnown={onKnown}
                onExpand={onExpand}
                onChoice={onChoice}
                onSource={onSource}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
export function PathTree({
  node,
  path,
  onLocate,
}: {
  node: Tree;
  path: string;
  onLocate: (id: string) => void;
}) {
  return (
    <div className="path-branch">
      <button className="path-node" onClick={() => onLocate(path)}>
        <span
          className={
            "path-dot " +
            (node.known
              ? "known"
              : node.status === "cycle" || !node.reachable
                ? "unresolved"
                : "")
          }
        />
        <span>
          {label(node)}
          <small>
            {node.pos === "prep" || node.pos === "prep_phrase"
              ? "介词依赖 · "
              : ""}
            {node.known
              ? "已标记理解"
              : node.status === "cycle"
                ? "循环引用"
                : node.status === "expanded"
                  ? "当前展开"
                  : node.reachable
                    ? "可展开"
                    : "尚待处理"}
          </small>
        </span>
        <ChevronRight size={14} />
      </button>
      {node.children && (
        <div className="path-children">
          <span className="and-tag">
            {node.alternatives &&
            node.alternatives.length > 1 &&
            node.selected !== undefined
              ? `分支 ${node.selected + 1} · `
              : ""}
            AND · 全部前提
          </span>
          {node.children.map((n, i) => (
            <PathTree
              key={n.id + "-" + i}
              node={n}
              path={`${path}-${i}`}
              onLocate={onLocate}
            />
          ))}
        </div>
      )}
    </div>
  );
}
