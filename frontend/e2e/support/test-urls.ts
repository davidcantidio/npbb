import path from "node:path";
import { tmpdir } from "node:os";

function resolvePort(url: URL): number {
  if (url.port) {
    return Number(url.port);
  }
  return url.protocol === "https:" ? 443 : 80;
}

export const API_URL = process.env.NPBB_E2E_API_URL ?? "http://localhost:8000";
export const FRONTEND_URL = process.env.NPBB_E2E_FRONTEND_URL ?? "http://localhost:4173";
export const BACKEND_BIND_HOST = process.env.NPBB_E2E_BACKEND_BIND_HOST ?? "127.0.0.1";
export const FRONTEND_BIND_HOST = process.env.NPBB_E2E_FRONTEND_BIND_HOST ?? "127.0.0.1";
export const E2E_DB_PATH = process.env.NPBB_E2E_DB_PATH ?? path.join(tmpdir(), "npbb_playwright_smoke.db");

export const API_PORT = resolvePort(new URL(API_URL));
export const FRONTEND_PORT = resolvePort(new URL(FRONTEND_URL));
