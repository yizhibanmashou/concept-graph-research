import type { Tree } from "./types";

/** Count unresolved nodes in the displayed tree, without claiming mastery. */
export function visibleFrontier(tree: Tree): number {
  const pending = new Set<string>();
  const visit = (node: Tree) => {
    if (node.known) return;
    if (
      ["collapsed", "cycle", "missing", "no_definition", "limit"].includes(
        node.status,
      )
    ) {
      pending.add(node.id);
      return;
    }
    node.children?.forEach(visit);
  };
  visit(tree);
  return pending.size;
}
