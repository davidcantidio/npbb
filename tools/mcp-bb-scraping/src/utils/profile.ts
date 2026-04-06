const IG_BLOCKLIST = new Set(["p", "reel", "explore", "accounts", "stories", "about", "legal"]);
const X_BLOCKLIST = new Set(["home", "i", "intent", "search", "settings", "compose", "explore"]);
const TIKTOK_BLOCKLIST = new Set(["discover", "tag", "login", "signup", "upload", "embed", "music", "foryou"]);

export function normalizeProfileHandle(raw: string | null | undefined): string | null {
  const trimmed = (raw ?? "").trim();
  if (!trimmed) return null;

  const noAt = stripAt(trimmed);
  if (!noAt) return null;

  const urlCandidate = toUrlCandidate(noAt);
  if (urlCandidate) return extractHandleFromProfileUrl(urlCandidate);

  const slashIndex = noAt.indexOf("/");
  const handle = slashIndex >= 0 ? noAt.slice(0, slashIndex) : noAt;
  return handle || null;
}

export function buildInstagramProfileUrl(handle: string): string {
  const cleaned = stripAt(handle);
  return `https://www.instagram.com/${cleaned}/`;
}

export function buildXProfileUrl(handle: string): string {
  const cleaned = stripAt(handle);
  return `https://x.com/${cleaned}`;
}

export function buildTikTokProfileUrl(handle: string): string {
  const cleaned = stripAt(handle);
  return `https://www.tiktok.com/@${cleaned}`;
}

export function extractHandleFromProfileUrl(url: string): string | null {
  const parsed = safeParseUrl(url);
  if (!parsed) return null;

  const host = parsed.hostname.toLowerCase();
  if (isInstagramHost(host)) return extractHandleFromPath(parsed.pathname, IG_BLOCKLIST);
  if (isXHost(host)) return extractHandleFromPath(parsed.pathname, X_BLOCKLIST);
  if (isTikTokHost(host)) return extractHandleFromPath(parsed.pathname, TIKTOK_BLOCKLIST);

  return null;
}

export function extractInstagramProfileHandle(url: string): string | null {
  const parsed = safeParseUrl(url);
  if (!parsed || !isInstagramHost(parsed.hostname.toLowerCase())) return null;
  return extractHandleFromPath(parsed.pathname, IG_BLOCKLIST);
}

function extractHandleFromPath(pathname: string, blocklist: Set<string>): string | null {
  const parts = pathname.split("/").filter(Boolean);
  if (!parts.length) return null;
  const candidate = stripAt(parts[0]);
  if (!candidate) return null;
  if (blocklist.has(candidate.toLowerCase())) return null;
  return candidate;
}

function stripAt(value: string): string {
  return value.replace(/^@+/, "").trim();
}

function toUrlCandidate(value: string): string | null {
  if (/^https?:\/\//i.test(value)) return value;
  const lower = value.toLowerCase();
  if (lower.includes("instagram.com") || lower.includes("tiktok.com") || lower.includes("x.com") || lower.includes("twitter.com")) {
    return `https://${value}`;
  }
  return null;
}

function safeParseUrl(value: string): URL | null {
  try {
    return new URL(value);
  } catch {
    return null;
  }
}

function isInstagramHost(host: string): boolean {
  return host === "instagram.com" || host.endsWith(".instagram.com");
}

function isXHost(host: string): boolean {
  return host === "x.com" || host.endsWith(".x.com") || host === "twitter.com" || host.endsWith(".twitter.com");
}

function isTikTokHost(host: string): boolean {
  return host === "tiktok.com" || host.endsWith(".tiktok.com");
}
