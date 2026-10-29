import { describe, expect, it } from "vitest";
import { decodeSession, encodeSession, validSession } from "./api";
import { loadRecent, MAX_RECENT, rememberPath } from "./recentPaths";
import { visibleFrontier } from "./frontier";
import type { Session } from "./types";

const session: Session = {
  version: 1,
  fingerprint: "v1",
  target: "a",
  known: ["b"],
  expanded: ["a"],
  choices: { a: 1 },
};

describe("解释卡片", () => {
  it("preserves Unicode and a large known set during URL round trip", () => {
    const input = {
      ...session,
      target: "概念",
      known: Array.from({ length: 5000 }, (_, index) => `sense-${index}`),
    };
    expect(decodeSession(encodeSession(input))).toEqual(input);
  });
  it("rejects incompatible versions and malformed choices", () => {
    expect(validSession(session, "v1")).toBe(true);
    expect(validSession(session, "v2")).toBe(false);
    expect(validSession({ ...session, choices: { a: -1 } }, "v1")).toBe(false);
  });
});

describe("最近探索", () => {
  it("restores per-target branch selection without duplicating entries", () => {
    const first = rememberPath([], session, "alpha");
    const updated = rememberPath(
      first,
      { ...session, choices: { a: 2 } },
      "alpha",
    );
    expect(updated).toHaveLength(1);
    expect(loadRecent(JSON.stringify(updated), "v1")[0].choices.a).toBe(2);
    expect(loadRecent(JSON.stringify(updated), "other")).toEqual([]);
  });
  it("limits entries and tolerates malformed storage", () => {
    let recent = rememberPath([], session, "a");
    for (let i = 0; i < 25; i++)
      recent = rememberPath(
        recent,
        { ...session, target: `item-${i}` },
        `item ${i}`,
      );
    expect(recent).toHaveLength(MAX_RECENT);
    expect(loadRecent("not json", "v1")).toEqual([]);
  });
});

describe("当前展开中的待处理概念", () => {
  it("counts unique unresolved nodes and excludes known nodes", () => {
    const common = {
      lemmas: "",
      pos: "n",
      definition: "",
      known: false,
      reachable: false,
    };
    const item = { ...common, id: "a", status: "collapsed" };
    expect(
      visibleFrontier({
        ...common,
        id: "root",
        status: "expanded",
        children: [
          item,
          item,
          { ...common, id: "b", status: "known", known: true },
        ],
      }),
    ).toBe(1);
  });
});
