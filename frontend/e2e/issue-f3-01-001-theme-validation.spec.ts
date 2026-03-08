import { expect, test } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import type { TemplateKey } from "../src/components/landing/__tests__/landingFixtures";
import {
  EXPECTED_TEMPLATE_GRADIENTS,
  EXPECTED_TEMPLATE_OVERLAY_VARIANTS,
  TEMPLATE_KEYS,
} from "../src/components/landing/__tests__/landingFixtures";

const TEST_FILE_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(TEST_FILE_DIR, "../..");
const ARTIFACT_ROOT = path.resolve(REPO_ROOT, "artifacts/phase-f3");
const SCREENSHOT_DIR = path.resolve(ARTIFACT_ROOT, "screenshots");
const EVIDENCE_DIR = path.resolve(ARTIFACT_ROOT, "evidence");
const RESULT_JSON_PATH = path.resolve(EVIDENCE_DIR, "issue-f3-01-001-results.json");

const API_URL = process.env.NPBB_LANDING_THEME_API_URL ?? "http://127.0.0.1:8000";
const BASE_URL = process.env.NPBB_LANDING_THEME_BASE_URL ?? "http://127.0.0.1:5173";
const EVENT_ID = Number(process.env.NPBB_LANDING_THEME_EVENT_ID ?? "1");

const BREAKPOINTS = [
  { label: "mobile", width: 375, height: 812 },
  { label: "tablet", width: 768, height: 1024 },
  { label: "desktop", width: 1280, height: 900 },
] as const;

type BreakpointLabel = (typeof BREAKPOINTS)[number]["label"];

type ScenarioResult = {
  template: TemplateKey;
  breakpoint: BreakpointLabel;
  viewport: { width: number; height: number };
  status: "PASS" | "FAIL";
  screenshot_path: string;
  template_category: string | null;
  overlay_variant: string | null;
  expected_overlay_variant: string;
  background_image: string;
  expected_background_image: string;
  viewport_gap_free: boolean;
  external_image_requests: string[];
  errors: string[];
  duration_ms: number;
};

const results: ScenarioResult[] = [];
const apiOrigin = new URL(API_URL).origin;
const baseOrigin = new URL(BASE_URL).origin;

function ensureArtifactDirs() {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  fs.mkdirSync(EVIDENCE_DIR, { recursive: true });
}

async function normalizeGradient(page: import("@playwright/test").Page, gradient: string) {
  return page.evaluate((value) => {
    const node = document.createElement("div");
    node.style.background = value;
    document.body.appendChild(node);
    const backgroundImage = getComputedStyle(node).backgroundImage;
    node.remove();
    return backgroundImage;
  }, gradient);
}

test.beforeAll(async () => {
  ensureArtifactDirs();

  const healthResponse = await fetch(`${API_URL}/health`);
  expect(healthResponse.ok).toBeTruthy();

  const landingResponse = await fetch(`${API_URL}/eventos/${EVENT_ID}/landing`);
  expect(landingResponse.ok).toBeTruthy();
});

test.afterAll(() => {
  const payload = {
    issue_id: "ISSUE-F3-01-001",
    generated_at: new Date().toISOString(),
    source_mode: "backend-real",
    api_url: API_URL,
    base_url: BASE_URL,
    event_id: EVENT_ID,
    total_scenarios: results.length,
    passed_scenarios: results.filter((item) => item.status === "PASS").length,
    failed_scenarios: results.filter((item) => item.status === "FAIL").length,
    results,
  };

  fs.writeFileSync(RESULT_JSON_PATH, `${JSON.stringify(payload, null, 2)}\n`);
});

for (const templateKey of TEMPLATE_KEYS) {
  for (const breakpoint of BREAKPOINTS) {
    test(`${templateKey} @ ${breakpoint.label}`, async ({ page }) => {
      const startedAt = Date.now();
      const screenshotPath = path.resolve(SCREENSHOT_DIR, `${templateKey}_${breakpoint.label}.png`);
      const relativeScreenshotPath = path.relative(REPO_ROOT, screenshotPath);
      const externalImageRequests: string[] = [];
      const scenario: ScenarioResult = {
        template: templateKey,
        breakpoint: breakpoint.label,
        viewport: { width: breakpoint.width, height: breakpoint.height },
        status: "FAIL",
        screenshot_path: relativeScreenshotPath,
        template_category: null,
        overlay_variant: null,
        expected_overlay_variant: EXPECTED_TEMPLATE_OVERLAY_VARIANTS[templateKey],
        background_image: "",
        expected_background_image: "",
        viewport_gap_free: false,
        external_image_requests: externalImageRequests,
        errors: [],
        duration_ms: 0,
      };

      page.on("request", (request) => {
        if (request.resourceType() !== "image") {
          return;
        }

        const url = request.url();
        if (url.startsWith("data:") || url.startsWith("blob:")) {
          return;
        }

        try {
          const origin = new URL(url).origin;
          if (origin === apiOrigin || origin === baseOrigin) {
            return;
          }
        } catch {
          externalImageRequests.push(url);
          return;
        }

        externalImageRequests.push(url);
      });

      await page.route(`**/eventos/${EVENT_ID}/landing*`, async (route) => {
        if (route.request().method() !== "GET") {
          await route.continue();
          return;
        }

          const nextUrl = new URL(route.request().url());
          nextUrl.searchParams.set("template_override", templateKey);
          await route.continue({ url: nextUrl.toString() });
        });

      try {
        await page.setViewportSize({ width: breakpoint.width, height: breakpoint.height });
        await page.goto(`/landing/eventos/${EVENT_ID}`);
        await page.waitForSelector("[data-testid='form-card-paper']", { timeout: 10_000 });

        const backgroundLayer = page.getByTestId("full-page-background-layer");
        const overlayLayer = page.getByTestId("full-page-overlay-layer");

        scenario.template_category = await backgroundLayer.getAttribute("data-template-category");
        scenario.overlay_variant = await overlayLayer.getAttribute("data-overlay-variant");
        scenario.background_image = await backgroundLayer.evaluate((element) => getComputedStyle(element).backgroundImage);
        scenario.expected_background_image = await normalizeGradient(page, EXPECTED_TEMPLATE_GRADIENTS[templateKey]);

        const coverage = await backgroundLayer.evaluate((element) => {
          const rect = element.getBoundingClientRect();
          return {
            left: rect.left,
            top: rect.top,
            width: rect.width,
            height: rect.height,
            viewportWidth: window.innerWidth,
            viewportHeight: window.innerHeight,
          };
        });

        scenario.viewport_gap_free =
          coverage.left === 0 &&
          coverage.top === 0 &&
          Math.abs(coverage.width - coverage.viewportWidth) <= 1 &&
          coverage.height >= coverage.viewportHeight - 1;

        expect(scenario.template_category).toBe(templateKey);
        expect(scenario.overlay_variant).toBe(EXPECTED_TEMPLATE_OVERLAY_VARIANTS[templateKey]);
        expect(scenario.background_image).toBe(scenario.expected_background_image);
        expect(scenario.viewport_gap_free).toBe(true);
        expect(externalImageRequests).toHaveLength(0);

        await page.screenshot({
          path: screenshotPath,
          fullPage: true,
        });

        scenario.status = "PASS";
      } catch (error) {
        scenario.errors.push(error instanceof Error ? error.message : String(error));
        throw error;
      } finally {
        scenario.duration_ms = Date.now() - startedAt;
        results.push(scenario);
      }
    });
  }
}
