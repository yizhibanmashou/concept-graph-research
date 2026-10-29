export type Sense = {
  id: string;
  lemmas: string;
  pos: string;
  definition: string;
  basis?: boolean;
};
export type Alternative = {
  index: number;
  body: string[];
  sources: string[];
  source_available: boolean;
  complete: boolean;
  missing: string[];
  cost: number;
};
export type Tree = Sense & {
  known: boolean;
  reachable: boolean;
  status: string;
  selected?: number;
  alternatives?: Alternative[];
  children?: Tree[];
  missing_node?: boolean;
};
export type Source = Sense & {
  records: {
    path: string;
    raw_definition?: string;
    effective_definition?: string;
    status?: string;
  }[];
  alternatives: Alternative[];
};
export type Session = {
  version: number;
  fingerprint: string;
  target: string;
  known: string[];
  expanded: string[];
  choices: Record<string, number>;
};
export type Health = {
  fingerprint: string;
  graph_version: string;
  head_count: number;
  clause_count: number;
  ready: boolean;
};
export type ExploreResult = {
  total: number;
  matched: number;
  items: (Sense & { cost: number })[];
  truncated: boolean;
  added: string | null;
};
export type Theme = "default" | "cream" | "dark" | "glass";
export type TextSize = "small" | "medium" | "large";
export type RecentPath = {
  target: string;
  name: string;
  expanded: string[];
  choices: Record<string, number>;
  fingerprint: string;
};

export const themes: { id: Theme; label: string; description: string }[] = [
  { id: "default", label: "默认", description: "纯白与蓝色" },
  { id: "cream", label: "暖色", description: "暖白与陶土色" },
  { id: "dark", label: "深色", description: "暖黑与陶土色" },
  { id: "glass", label: "玻璃", description: "深紫色玻璃质感" },
];

export const label = (sense: Sense) => sense.lemmas || sense.id;
