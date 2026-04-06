import { existsSync } from "node:fs";
import { resolve } from "node:path";

export type ParsedArgs = Map<string, string | null>;

export function parseArgs(argv: string[]): ParsedArgs {
  const map = new Map<string, string | null>();
  for (let i = 0; i < argv.length; i++) {
    const raw = argv[i];
    if (!raw.startsWith("--")) continue;
    const trimmed = raw.slice(2);
    const eq = trimmed.indexOf("=");
    if (eq >= 0) {
      map.set(trimmed.slice(0, eq), trimmed.slice(eq + 1));
      continue;
    }
    const key = trimmed;
    const next = argv[i + 1];
    if (next && !next.startsWith("--")) {
      map.set(key, next);
      i++;
    } else {
      map.set(key, null);
    }
  }
  return map;
}

export function stringArg(value: string | null | undefined, fallback: string): string {
  const v = (value ?? "").trim();
  return v ? v : fallback;
}

export function parseIntArg(value: string | null | undefined, fallback: number, argName = "valor"): number {
  const raw = (value ?? "").trim();
  if (!raw) return fallback;
  const n = Number(raw);
  if (!Number.isFinite(n) || n <= 0 || !Number.isInteger(n)) {
    throw new Error(`Valor invalido em --${argName}: ${value}. Use inteiro > 0.`);
  }
  return n;
}

export function dateArg(value: string | null | undefined, argName = "date"): Date | null {
  if (!value) return null;
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) throw new Error(`Data invalida em --${argName}: ${value}`);
  return d;
}

export function boolArg(value: string | null | undefined): boolean {
  if (value == null) return false;
  const v = String(value).trim().toLowerCase();
  if (v === "" || v === "true" || v === "1" || v === "yes" || v === "y") return true;
  if (v === "false" || v === "0" || v === "no" || v === "n") return false;
  return true;
}

export function existingFileOrNull(path: string | null | undefined): string | null {
  const v = (path ?? "").trim();
  if (!v) return null;
  const candidate = resolve(v);
  return existsSync(candidate) ? candidate : null;
}

