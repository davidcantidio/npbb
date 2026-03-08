import { defineConfig } from "@playwright/test";

function resolvePort(url: URL): number {
  if (url.port) {
    return Number(url.port);
  }

  return url.protocol === "https:" ? 443 : 80;
}

const BASE_URL = process.env.NPBB_LANDING_THEME_BASE_URL ?? "http://127.0.0.1:5173";
const API_URL = process.env.NPBB_LANDING_THEME_API_URL ?? "http://127.0.0.1:8000";
const baseUrl = new URL(BASE_URL);

export default defineConfig({
  testDir: "./e2e",
  testMatch: "issue-f3-01-001-theme-validation.spec.ts",
  timeout: 30_000,
  expect: {
    timeout: 10_000,
  },
  fullyParallel: false,
  workers: 1,
  retries: 0,
  outputDir: "test-results/playwright/phase-f3",
  reporter: [["list"]],
  use: {
    baseURL: BASE_URL,
    trace: "retain-on-failure",
    video: "retain-on-failure",
    screenshot: "only-on-failure",
    browserName: "chromium",
  },
  webServer: [
    {
      command: `npm run dev -- --host ${baseUrl.hostname} --port ${resolvePort(baseUrl)} --strictPort`,
      cwd: ".",
      env: {
        ...process.env,
        VITE_API_BASE_URL: API_URL,
      },
      url: BASE_URL,
      timeout: 120_000,
      reuseExistingServer: true,
    },
  ],
});
