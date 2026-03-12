import { defineConfig } from "@playwright/test";

import {
  API_PORT,
  API_URL,
  BACKEND_BIND_HOST,
  E2E_DB_PATH,
  FRONTEND_BIND_HOST,
  FRONTEND_PORT,
  FRONTEND_URL,
} from "./e2e/support/test-urls";

export default defineConfig({
  testDir: "./e2e",
  testMatch: [
    "*.smoke.spec.ts",
    "issue-f2-01-003*.spec.ts",
    "issue-f3-01-002*.spec.ts",
    "issue-f3-02-001*.spec.ts",
    "issue-f3-02-002*.spec.ts",
  ],
  timeout: 30_000,
  expect: {
    timeout: 10_000,
  },
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  outputDir: "test-results/playwright/artifacts",
  reporter: [
    ["list"],
    ["html", { open: "never", outputFolder: "playwright-report" }],
    ["junit", { outputFile: "test-results/playwright/junit.xml" }],
  ],
  use: {
    baseURL: FRONTEND_URL,
    trace: "on-first-retry",
    video: "retain-on-failure",
    screenshot: "only-on-failure",
    browserName: "chromium",
  },
  webServer: [
    {
      command: "node ./e2e/support/backend-server.mjs",
      cwd: ".",
      env: {
        ...process.env,
        NPBB_E2E_API_URL: API_URL,
        NPBB_E2E_FRONTEND_URL: FRONTEND_URL,
        NPBB_E2E_DB_PATH: E2E_DB_PATH,
      },
      url: `http://${BACKEND_BIND_HOST}:${API_PORT}/health`,
      timeout: 120_000,
      reuseExistingServer: false,
    },
    {
      command: `npm run dev -- --host ${FRONTEND_BIND_HOST} --port ${FRONTEND_PORT} --strictPort`,
      cwd: ".",
      env: {
        ...process.env,
        VITE_API_BASE_URL: API_URL,
      },
      url: FRONTEND_URL,
      timeout: 120_000,
      reuseExistingServer: false,
    },
  ],
});
