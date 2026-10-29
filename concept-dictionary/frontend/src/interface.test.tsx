// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { Drawer } from "./Drawer";
import { SettingsPage } from "./SettingsPage";
import { Explanation, PathTree } from "./Explanation";

afterEach(cleanup);

describe("设置与键盘操作", () => {
  it("explains AND/OR and warns about preposition phrases", () => {
    render(
      <Explanation
        path="root"
        depth={0}
        onKnown={vi.fn()}
        onExpand={vi.fn()}
        onChoice={vi.fn()}
        onSource={vi.fn()}
        node={{
          id: "phrase",
          lemmas: "because of",
          pos: "prep_phrase",
          definition: "on account of",
          known: false,
          reachable: true,
          status: "expanded",
          selected: 0,
          alternatives: [
            {
              index: 0,
              body: [],
              sources: [],
              source_available: true,
              complete: true,
              missing: [],
              cost: 0,
            },
          ],
          children: [],
        }}
      />,
    );
    expect(screen.getByText(/可能表达方向或否定/)).toBeTruthy();
    expect(screen.getByText(/不同分支是替代的构造路径/)).toBeTruthy();
  });
  it("identifies prepositions and the selected alternative in the path view", () => {
    const locate = vi.fn();
    const child = {
      id: "in-6",
      lemmas: "in",
      pos: "prep",
      definition: "",
      known: false,
      reachable: false,
      status: "collapsed",
    };
    render(
      <PathTree
        path="root"
        onLocate={locate}
        node={{
          id: "root",
          lemmas: "target",
          pos: "n",
          definition: "",
          known: false,
          reachable: false,
          status: "expanded",
          selected: 1,
          alternatives: [
            {
              index: 0,
              body: [],
              sources: [],
              source_available: false,
              complete: false,
              missing: [],
              cost: 0,
            },
            {
              index: 1,
              body: ["in-6"],
              sources: [],
              source_available: false,
              complete: false,
              missing: ["in-6"],
              cost: 0,
            },
          ],
          children: [child],
        }}
      />,
    );
    expect(screen.getByText(/分支 2 · AND/)).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: /介词依赖/ }));
    expect(locate).toHaveBeenCalledWith("root-0");
  });
  it("exposes meaningful settings and updates the selected preference", () => {
    const setTheme = vi.fn();
    const setDefaultGraph = vi.fn();
    render(
      <SettingsPage
        health={{
          ready: true,
          fingerprint: "1234567890abcdef",
          graph_version: "v",
          head_count: 2,
          clause_count: 3,
        }}
        theme="default"
        setTheme={setTheme}
        textSize="medium"
        setTextSize={vi.fn()}
        reduceMotion={false}
        setReduceMotion={vi.fn()}
        defaultGraph={true}
        setDefaultGraph={setDefaultGraph}
        knownCount={1}
        recentCount={2}
        onClearRecent={vi.fn()}
        openKnown={vi.fn()}
        onImport={vi.fn()}
        onExport={vi.fn()}
        onReset={vi.fn()}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: /暖色/ }));
    fireEvent.click(screen.getByRole("switch", { name: "默认显示路径图" }));
    expect(setTheme).toHaveBeenCalledWith("cream");
    expect(setDefaultGraph).toHaveBeenCalledWith(false);
    expect(screen.getByText("本地数据已连接")).toBeTruthy();
  });

  it("focuses the drawer and closes it with Escape", () => {
    const close = vi.fn();
    render(
      <Drawer titleId="dialog-title" onClose={close}>
        <h2 id="dialog-title">依据</h2>
        <button>关闭</button>
      </Drawer>,
    );
    expect(screen.getByRole("dialog", { name: "依据" })).toBeTruthy();
    expect(document.activeElement).toBe(
      screen.getByRole("button", { name: "关闭" }),
    );
    fireEvent.keyDown(document, { key: "Escape" });
    expect(close).toHaveBeenCalledOnce();
  });
});
