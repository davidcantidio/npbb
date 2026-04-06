import { join } from "node:path";

export function sanitizeHandle(value: string | null | undefined): string | null {
  const trimmed = String(value ?? "").trim().replace(/^@+/, "");
  if (!trimmed) return null;
  const safe = trimmed.replace(/[^a-z0-9._-]+/gi, "_").replace(/^_+|_+$/g, "");
  return safe ? safe.toLowerCase() : null;
}

export function sanitizeLabel(value: string | null | undefined): string | null {
  const trimmed = String(value ?? "").trim();
  if (!trimmed) return null;
  const safe = trimmed.replace(/[^a-z0-9._-]+/gi, "_").replace(/^_+|_+$/g, "");
  return safe ? safe.toLowerCase() : null;
}

export function outputFileName(base: string, ext: string, handle?: string | null): string {
  const safeHandle = sanitizeHandle(handle);
  const suffix = safeHandle ? `_${safeHandle}` : "";
  return `${base}${suffix}.${ext}`;
}

export function outputPostsFileName(name: string | null | undefined, handle: string | null | undefined, ext: string): string {
  const safeName = sanitizeLabel(name);
  const safeHandle = sanitizeHandle(handle);
  const parts = [safeName, safeHandle, "posts"].filter(Boolean);
  return `${parts.join("_")}.${ext}`;
}

export function outputPath(outDir: string, base: string, ext: string, handle?: string | null): string {
  return join(outDir, outputFileName(base, ext, handle));
}

export function outputPostsPath(outDir: string, name: string | null | undefined, handle: string | null | undefined, ext: string): string {
  return join(outDir, outputPostsFileName(name, handle, ext));
}
