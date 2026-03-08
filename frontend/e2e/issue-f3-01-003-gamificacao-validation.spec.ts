import { expect, test } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import type { TemplateKey } from "../src/components/landing/__tests__/landingFixtures";
import { TEMPLATE_KEYS } from "../src/components/landing/__tests__/landingFixtures";

const TEST_FILE_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(TEST_FILE_DIR, "../..");
const ARTIFACT_ROOT = path.resolve(REPO_ROOT, "artifacts/phase-f3");
const SCREENSHOT_DIR = path.resolve(ARTIFACT_ROOT, "screenshots");
const EVIDENCE_DIR = path.resolve(ARTIFACT_ROOT, "evidence");
const RESULT_JSON_PATH = path.resolve(EVIDENCE_DIR, "issue-f3-01-003-results.json");
const FIXTURE_JSON_PATH = path.resolve(EVIDENCE_DIR, "issue-f3-01-003-fixtures.json");

const API_URL = process.env.NPBB_LANDING_THEME_API_URL ?? "http://127.0.0.1:8000";
const BASE_URL = process.env.NPBB_LANDING_THEME_BASE_URL ?? "http://127.0.0.1:5173";

const BREAKPOINTS = [
  { label: "mobile", width: 375, height: 812 },
  { label: "tablet", width: 768, height: 1024 },
  { label: "desktop", width: 1280, height: 900 },
] as const;

type BreakpointLabel = (typeof BREAKPOINTS)[number]["label"];

type GamificacaoFixture = {
  template_key: string;
  template_category: string | null;
  evento_id: number;
  ativacao_id: number;
  gamificacao_id?: number | null;
};

type FixturePayload = {
  issue_id: string;
  generated_at: string;
  fixtures: GamificacaoFixture[];
};

type ScenarioResult = {
  template: TemplateKey;
  breakpoint: BreakpointLabel;
  viewport: { width: number; height: number };
  status: "PASS" | "FAIL";
  screenshot_path: string;
  fixture: {
    evento_id: number;
    ativacao_id: number;
    gamificacao_id: number | null;
  };
  template_category: string | null;
  overlay_variant: string | null;
  background_image: string;
  theme_visible: boolean;
  position_ok: boolean;
  form_cleared_after_reset: boolean;
  state_sequence: {
    initial: "PRESENTING";
    after_submit: "ACTIVE";
    after_complete: "COMPLETED";
    after_reset: "PRESENTING";
  };
  external_image_requests: string[];
  errors: string[];
  duration_ms: number;
};

type FixtureRegistry = Map<TemplateKey, GamificacaoFixture>;

const results: ScenarioResult[] = [];

function ensureArtifactDirs() {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  fs.mkdirSync(EVIDENCE_DIR, { recursive: true });
}

function loadFixtures(): FixtureRegistry {
  if (!fs.existsSync(FIXTURE_JSON_PATH)) {
    throw new Error(`Fixture file missing: ${FIXTURE_JSON_PATH}`);
  }

  const raw = fs.readFileSync(FIXTURE_JSON_PATH, "utf-8");
  const parsed = JSON.parse(raw) as FixturePayload;

  if (!Array.isArray(parsed?.fixtures)) {
    throw new Error("Invalid fixture payload: 'fixtures' missing");
  }

  const registry: FixtureRegistry = new Map();
  for (const row of parsed.fixtures) {
    const templateKey = row.template_key?.trim();
    if (!templateKey || !TEMPLATE_KEYS.includes(templateKey as TemplateKey)) {
      continue;
    }

    if (!Number.isFinite(row.ativacao_id) || row.ativacao_id <= 0) {
      continue;
    }

    registry.set(templateKey as TemplateKey, {
      template_key: templateKey,
      template_category: row.template_category ?? null,
      evento_id: row.evento_id,
      ativacao_id: row.ativacao_id,
      gamificacao_id: row.gamificacao_id ?? null,
    });
  }

  return registry;
}

const fixtures = loadFixtures();
const TEST_MATRIX = TEMPLATE_KEYS.filter((templateKey) => fixtures.has(templateKey));

if (TEST_MATRIX.length !== TEMPLATE_KEYS.length) {
  const missing = TEMPLATE_KEYS.filter((templateKey) => !fixtures.has(templateKey));
  throw new Error(
    `Fixture incompleta em issue-f3-01-003-fixtures.json. Templates faltantes: ${missing.join(", ")}`,
  );
}

function formatEmail(seed: number, template: TemplateKey, breakpoint: BreakpointLabel) {
  const safeTemplate = template.replace(/_/g, "-");
  return `f3-${safeTemplate}-${breakpoint}-${seed}@qa.npbb.example`;
}

async function getBackgroundInfo(page: import("@playwright/test").Page) {
  const backgroundLayer = page.getByTestId("full-page-background-layer");
  const overlayLayer = page.getByTestId("full-page-overlay-layer");

  const templateCategory = await backgroundLayer.getAttribute("data-template-category");
  const overlayVariant = await overlayLayer.getAttribute("data-overlay-variant");
  const backgroundImage = await backgroundLayer.evaluate(
    (element) => window.getComputedStyle(element).backgroundImage,
  );

  return { templateCategory, overlayVariant, backgroundImage };
}

function isBelow(
  topCandidate: { x: number; y: number; height: number } | null,
  topReference: { x: number; y: number; height: number } | null,
) {
  if (!topCandidate || !topReference) return false;
  return topCandidate.y >= topReference.y + topReference.height - 1;
}

function recordFailure(scenario: ScenarioResult, error: unknown) {
  const message = error instanceof Error ? error.message : String(error);
  scenario.errors.push(message);
  scenario.status = "FAIL";
}

test.beforeAll(async () => {
  ensureArtifactDirs();

  const healthResponse = await fetch(`${API_URL}/health`);
  expect(healthResponse.ok).toBeTruthy();
});

test.afterAll(() => {
  const payload = {
    issue_id: "ISSUE-F3-01-003",
    generated_at: new Date().toISOString(),
    source_mode: "backend-real",
    api_url: API_URL,
    base_url: BASE_URL,
    total_scenarios: results.length,
    passed_scenarios: results.filter((item) => item.status === "PASS").length,
    failed_scenarios: results.filter((item) => item.status === "FAIL").length,
    results,
  };

  fs.writeFileSync(RESULT_JSON_PATH, `${JSON.stringify(payload, null, 2)}\n`);
});

for (const templateKey of TEST_MATRIX) {
  for (const breakpoint of BREAKPOINTS) {
    test(`ISSUE-F3-01-003 | ${templateKey} | ${breakpoint.label}`, async ({ page }) => {
      const startedAt = Date.now();
      const fixture = fixtures.get(templateKey);
      if (!fixture) {
        throw new Error(`Sem fixture para template: ${templateKey}`);
      }

      const screenshotPath = path.resolve(
        SCREENSHOT_DIR,
        `issue-f3-01-003-${templateKey}_${breakpoint.label}.png`,
      );
      const relativeScreenshotPath = path.relative(REPO_ROOT, screenshotPath);
      const externalImageRequests: string[] = [];
      const scenario: ScenarioResult = {
        template: templateKey,
        breakpoint: breakpoint.label,
        viewport: { width: breakpoint.width, height: breakpoint.height },
        status: "FAIL",
        screenshot_path: relativeScreenshotPath,
        fixture: {
          evento_id: fixture.evento_id,
          ativacao_id: fixture.ativacao_id,
          gamificacao_id: fixture.gamificacao_id ?? null,
        },
        template_category: null,
        overlay_variant: null,
        background_image: "",
        theme_visible: false,
        position_ok: false,
        form_cleared_after_reset: false,
        state_sequence: {
          initial: "PRESENTING",
          after_submit: "ACTIVE",
          after_complete: "COMPLETED",
          after_reset: "PRESENTING",
        },
        external_image_requests: externalImageRequests,
        errors: [],
        duration_ms: 0,
      };

      const landingRequest = page.waitForRequest(
        (request) => request.method() === "GET" && /\/landing\/ativacoes\//.test(request.url()),
      );
      page.on("request", (request) => {
        if (request.resourceType() !== "image") return;
        if (request.url().startsWith("data:") || request.url().startsWith("blob:")) return;
        try {
          const origin = new URL(request.url()).origin;
          const apiOrigin = new URL(API_URL).origin;
          const baseOrigin = new URL(BASE_URL).origin;
          if (origin === apiOrigin || origin === baseOrigin) return;
        } catch {
          externalImageRequests.push(request.url());
          return;
        }

        externalImageRequests.push(request.url());
      });

      try {
        await page.setViewportSize({ width: breakpoint.width, height: breakpoint.height });
        await page.goto(`/landing/ativacoes/${fixture.ativacao_id}`);
        await landingRequest;

        await page.waitForSelector("[data-testid='form-card-paper']", { timeout: 12_000 });
        await page.waitForSelector("[data-testid='landing-gamificacao-section']", { timeout: 12_000 });

        const formCardContainer = page.getByTestId("form-card-paper");
        const gamificacaoSection = page.getByTestId("landing-gamificacao-section");
        const presentButton = page.getByRole("button", { name: /^Quero participar$/i });

        const initialLayout = await Promise.all([
          formCardContainer.boundingBox(),
          gamificacaoSection.boundingBox(),
        ]);
        scenario.position_ok = isBelow(initialLayout[1], initialLayout[0]);

        const backgroundInfo = await getBackgroundInfo(page);
        scenario.template_category = backgroundInfo.templateCategory;
        scenario.overlay_variant = backgroundInfo.overlayVariant;
        scenario.background_image = backgroundInfo.backgroundImage;
        scenario.theme_visible = backgroundInfo.backgroundImage !== "none";

        await expect(presentButton).toBeVisible();
        await expect(presentButton).toBeDisabled();

        const formCardPaper = page.getByTestId("form-card-paper");
        const submitButton = formCardPaper.locator("button").first();
        const nameField = formCardPaper.getByRole("textbox", { name: /^Nome/i });
        const emailField = formCardPaper.getByRole("textbox", { name: /^Email/i });
        const consentCheckbox = page.getByRole("checkbox");
        const email = formatEmail(Date.now(), templateKey, breakpoint.label);

        await nameField.fill("QA F3");
        await emailField.fill(email);
        await consentCheckbox.check();
        await submitButton.click();

        await expect(page.getByText("Cadastro concluido")).toBeVisible({ timeout: 10_000 });
        await expect(presentButton).toBeEnabled();

        const activeButton = page.getByRole("button", { name: /^Conclui$/i });
        await expect(activeButton).toBeVisible();
        await activeButton.click();

        const resetButton = page.getByRole("button", { name: /^Nova pessoa$/i });
        await expect(resetButton).toBeVisible({ timeout: 10_000 });
        await expect(page.getByText("Parabens!")).toBeVisible();
        await resetButton.click();

        await expect(presentButton).toBeDisabled();
        await expect(page.getByText("Cadastro concluido")).toBeHidden({ timeout: 10_000 });

        await expect(nameField).toHaveValue("");
        await expect(emailField).toHaveValue("");

        scenario.form_cleared_after_reset = true;

        await page.screenshot({ path: screenshotPath, fullPage: true });
        scenario.status = "PASS";
      } catch (error) {
        recordFailure(scenario, error);
        throw error;
      } finally {
        scenario.duration_ms = Date.now() - startedAt;
        results.push(scenario);
      }
    });
  }
}
