import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { normalizeProfileHandle } from "./profile";

export interface AthleteHandleEntry {
  name: string;
  handle: string;
  status: string;
  notes: string;
}

function parseCsvLine(line: string): string[] {
  const out: string[] = [];
  let current = "";
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (inQuotes) {
      if (ch === '"') {
        if (line[i + 1] === '"') {
          current += '"';
          i++;
        } else {
          inQuotes = false;
        }
      } else {
        current += ch;
      }
      continue;
    }

    if (ch === '"') {
      inQuotes = true;
      continue;
    }
    if (ch === ",") {
      out.push(current);
      current = "";
      continue;
    }
    current += ch;
  }
  out.push(current);
  return out;
}

function parseCsv(content: string): string[][] {
  const rows: string[][] = [];
  const lines = content.split(/\r?\n/);
  for (const raw of lines) {
    if (!raw.trim()) continue;
    const line = rows.length === 0 ? raw.replace(/^\uFEFF/, "") : raw;
    rows.push(parseCsvLine(line));
  }
  return rows;
}

export function listAthleteHandles(rootDir: string): AthleteHandleEntry[] {
  const configPath = resolve(rootDir, "config", "instagram_handles.csv");
  if (!existsSync(configPath)) return [];

  let content = "";
  try {
    content = readFileSync(configPath, "utf8");
  } catch {
    return [];
  }

  const rows = parseCsv(content);
  if (!rows.length) return [];

  const header = rows[0].map((h) => h.trim().toLowerCase());
  const nameIdx = header.indexOf("name");
  const handleIdx = header.indexOf("handle");
  const statusIdx = header.indexOf("status");
  const notesIdx = header.indexOf("notes");
  if (nameIdx < 0 || handleIdx < 0) return [];

  const out: AthleteHandleEntry[] = [];
  for (let i = 1; i < rows.length; i++) {
    const row = rows[i];
    if (!row.length) continue;
    const handle = normalizeProfileHandle(row[handleIdx]);
    if (!handle) continue;
    out.push({
      name: (row[nameIdx] ?? "").trim(),
      handle,
      status: (row[statusIdx] ?? "").trim().toLowerCase(),
      notes: (row[notesIdx] ?? "").trim(),
    });
  }

  return out;
}

export function lookupAthleteName(handle: string | null, rootDir: string): string | null {
  const safeHandle = normalizeProfileHandle(handle);
  if (!safeHandle) return null;

  const compactHandle = (value: string): string => value.toLowerCase().replace(/[^a-z0-9]+/g, "");
  const exactMap = new Map<string, string>();
  const compactMap = new Map<string, string>();
  const compactCounts = new Map<string, number>();

  for (const athlete of listAthleteHandles(rootDir)) {
    const name = athlete.name.trim();
    if (!name) continue;
    exactMap.set(athlete.handle.toLowerCase(), name);
    const key = compactHandle(athlete.handle);
    if (!key) continue;
    compactCounts.set(key, (compactCounts.get(key) ?? 0) + 1);
    if (!compactMap.has(key)) compactMap.set(key, name);
  }

  const exact = exactMap.get(safeHandle.toLowerCase());
  if (exact) return exact;

  const compactKey = compactHandle(safeHandle);
  if (compactKey && compactCounts.get(compactKey) === 1) {
    return compactMap.get(compactKey) ?? null;
  }

  return null;
}
