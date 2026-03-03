import { spawn, spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "../../..");
const backendDir = path.join(repoRoot, "backend");

const apiUrl = new URL(process.env.NPBB_E2E_API_URL ?? "http://localhost:8000");
const frontendUrl = new URL(process.env.NPBB_E2E_FRONTEND_URL ?? "http://localhost:4173");
const frontendBindHost = process.env.NPBB_E2E_FRONTEND_BIND_HOST ?? "127.0.0.1";
const dbPath = process.env.NPBB_E2E_DB_PATH ?? path.join(process.env.TMPDIR ?? "/tmp", "npbb_playwright_smoke.db");
const pythonBin = process.env.PYTHON_BIN ?? "python3";

const uvicornHost = process.env.NPBB_E2E_BACKEND_BIND_HOST ?? "127.0.0.1";
const uvicornPort = apiUrl.port || (apiUrl.protocol === "https:" ? "443" : "80");
const frontendOrigin = process.env.NPBB_E2E_FRONTEND_ORIGIN ?? `${frontendUrl.origin},http://${frontendBindHost}:${frontendUrl.port || "4173"}`;

const env = {
  ...process.env,
  DATABASE_URL: `sqlite:///${dbPath}`,
  SECRET_KEY: "e2e-secret-key",
  FRONTEND_ORIGIN: frontendOrigin,
  ENV: "development",
  COOKIE_SECURE: "false",
  USER_REGISTRATION_MODE: "invite",
  USER_REGISTRATION_INVITE_TOKEN: "invite-secret",
  USER_REGISTRATION_RATE_LIMIT_MAX: "1",
  USER_REGISTRATION_RATE_LIMIT_WINDOW_SEC: "600",
  FORGOT_PASSWORD_RATE_LIMIT_MAX: "2",
  FORGOT_PASSWORD_RATE_LIMIT_WINDOW_SEC: "600",
  PYTHONPATH: [repoRoot, backendDir, process.env.PYTHONPATH].filter(Boolean).join(path.delimiter),
  PYTHONUNBUFFERED: "1",
};

if (fs.existsSync(dbPath)) {
  fs.rmSync(dbPath, { force: true });
}

const seedResult = spawnSync(pythonBin, ["scripts/seed_playwright_smoke.py"], {
  cwd: backendDir,
  env,
  stdio: "inherit",
});

if (seedResult.status !== 0) {
  process.exit(seedResult.status ?? 1);
}

const backend = spawn(
  pythonBin,
  ["-m", "uvicorn", "app.main:app", "--host", uvicornHost, "--port", uvicornPort],
  {
    cwd: backendDir,
    env,
    stdio: "inherit",
  },
);

let shuttingDown = false;

function shutdown(signal) {
  if (shuttingDown) {
    return;
  }
  shuttingDown = true;
  if (!backend.killed) {
    backend.kill(signal);
    setTimeout(() => {
      if (!backend.killed) {
        backend.kill("SIGKILL");
      }
    }, 5_000).unref();
  }
}

process.on("SIGINT", () => shutdown("SIGINT"));
process.on("SIGTERM", () => shutdown("SIGTERM"));
process.on("exit", () => shutdown("SIGTERM"));

backend.on("exit", (code, signal) => {
  if (signal) {
    process.exit(1);
    return;
  }
  process.exit(code ?? 0);
});
