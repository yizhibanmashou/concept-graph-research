import type { Session } from "./types";

export async function api<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init);
  if (!response.ok) {
    let reason = response.statusText;
    try {
      const error = await response.json();
      reason =
        typeof error.detail === "string" ? error.detail : "请求格式不正确";
    } catch {
      /* Keep the HTTP status when the response is not JSON. */
    }
    throw new Error(reason);
  }
  return response.json();
}

export function post<T>(url: string, body: unknown): Promise<T> {
  return api<T>(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export function encodeSession(session: Session): string {
  const bytes = new TextEncoder().encode(JSON.stringify(session));
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary)
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

export function decodeSession(raw: string): Session {
  const binary = atob(raw.replace(/-/g, "+").replace(/_/g, "/"));
  return JSON.parse(
    new TextDecoder().decode(Uint8Array.from(binary, (c) => c.charCodeAt(0))),
  ) as Session;
}

export function validSession(session: Session, fingerprint: string): boolean {
  return (
    !!session &&
    session.version === 1 &&
    session.fingerprint === fingerprint &&
    typeof session.target === "string" &&
    Array.isArray(session.known) &&
    session.known.every((x) => typeof x === "string") &&
    Array.isArray(session.expanded) &&
    session.expanded.every((x) => typeof x === "string") &&
    !!session.choices &&
    !Array.isArray(session.choices) &&
    typeof session.choices === "object" &&
    Object.values(session.choices).every((x) => Number.isInteger(x) && x >= 0)
  );
}
