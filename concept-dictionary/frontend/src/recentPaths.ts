import type { RecentPath, Session } from "./types";

export const RECENT_KEY = "concept-dictionary-recent-v1";
export const MAX_RECENT = 20;

export function loadRecent(
  raw: string | null,
  fingerprint: string,
): RecentPath[] {
  try {
    const value: unknown = JSON.parse(raw || "[]");
    if (!Array.isArray(value)) return [];
    return value
      .filter(
        (entry): entry is RecentPath =>
          !!entry &&
          typeof entry === "object" &&
          entry.fingerprint === fingerprint &&
          typeof entry.target === "string" &&
          typeof entry.name === "string" &&
          Array.isArray(entry.expanded) &&
          entry.expanded.every((x: unknown) => typeof x === "string") &&
          !!entry.choices &&
          typeof entry.choices === "object" &&
          !Array.isArray(entry.choices) &&
          Object.values(entry.choices).every(
            (x) => Number.isInteger(x) && (x as number) >= 0,
          ),
      )
      .slice(0, MAX_RECENT);
  } catch {
    return [];
  }
}

export function rememberPath(
  recent: RecentPath[],
  session: Session,
  name: string,
): RecentPath[] {
  if (!session.target) return recent;
  const entry = {
    target: session.target,
    name,
    expanded: [...session.expanded],
    choices: { ...session.choices },
    fingerprint: session.fingerprint,
  };
  return [
    entry,
    ...recent.filter((item) => item.target !== entry.target),
  ].slice(0, MAX_RECENT);
}
