import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const BASE_URL = (process.env.NPBB_BASE_URL || "http://localhost:8000").replace(/\/$/, "");
const EMAIL = process.env.NPBB_TEST_EMAIL;
const PASSWORD = process.env.NPBB_TEST_PASSWORD;
const TIMEOUT_MS = Number(process.env.NPBB_SMOKE_TIMEOUT_MS || 20000);

if (!EMAIL || !PASSWORD) {
  console.error("Defina NPBB_TEST_EMAIL e NPBB_TEST_PASSWORD para rodar o smoke.");
  process.exit(1);
}

function buildUrl(pathname) {
  return `${BASE_URL}${pathname.startsWith("/") ? pathname : `/${pathname}`}`;
}

async function request(pathname, { method = "GET", token, headers, body } = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const response = await fetch(buildUrl(pathname), {
      method,
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(headers || {}),
      },
      body,
      signal: controller.signal,
    });

    const text = await response.text();
    const data = text
      ? (() => {
          try {
            return JSON.parse(text);
          } catch {
            return text;
          }
        })()
      : null;

    return {
      ok: response.ok,
      status: response.status,
      data,
    };
  } finally {
    clearTimeout(timeout);
  }
}

function toIsoDate(daysFromNow = 7) {
  const date = new Date();
  date.setDate(date.getDate() + daysFromNow);
  return date.toISOString().slice(0, 10);
}

async function main() {
  const timestamp = Date.now();
  const report = {
    generated_at: new Date().toISOString(),
    base_url: BASE_URL,
    steps: [],
  };

  let token;
  let tempEventId = null;
  const eventName = `SMOKE-EVENTO-${timestamp}`;

  try {
    const loginResult = await request("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: EMAIL, password: PASSWORD }),
    });
    report.steps.push({ step: "login", status: loginResult.status });
    if (!loginResult.ok || !loginResult.data?.access_token) {
      throw new Error(`Falha no login (${loginResult.status}).`);
    }
    token = loginResult.data.access_token;

    const createEventResult = await request("/evento/", {
      method: "POST",
      token,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        nome: eventName,
        cidade: "Brasilia",
        estado: "DF",
        concorrencia: false,
        data_inicio_prevista: toIsoDate(7),
      }),
    });
    report.steps.push({ step: "create_event", status: createEventResult.status });
    if (!createEventResult.ok || !createEventResult.data?.id) {
      throw new Error(`Falha ao criar evento temporario (${createEventResult.status}).`);
    }
    tempEventId = Number(createEventResult.data.id);

    const csvContent = [
      "Email;CPF;Nome;Evento",
      `smoke.${timestamp}@example.com;12345678901;Smoke Lead;${eventName}`,
    ].join("\n");
    const csvBlob = new Blob([csvContent], { type: "text/csv" });
    const filename = `smoke-leads-${timestamp}.csv`;

    const previewForm = new FormData();
    previewForm.append("file", csvBlob, filename);
    previewForm.append("sample_rows", "5");

    const previewResult = await request("/leads/import/preview", {
      method: "POST",
      token,
      body: previewForm,
    });
    report.steps.push({
      step: "preview",
      status: previewResult.status,
      headers: previewResult.data?.headers || [],
    });
    if (!previewResult.ok) {
      throw new Error(`Falha no preview (${previewResult.status}).`);
    }

    const mappings = [
      { coluna: "Email", campo: "email", confianca: 1 },
      { coluna: "CPF", campo: "cpf", confianca: 1 },
      { coluna: "Nome", campo: "nome", confianca: 1 },
      { coluna: "Evento", campo: "evento_nome", confianca: 1 },
    ];

    const validateResult = await request("/leads/import/validate", {
      method: "POST",
      token,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(mappings),
    });
    report.steps.push({
      step: "validate",
      status: validateResult.status,
      ok: validateResult.data?.ok ?? null,
    });
    if (!validateResult.ok) {
      throw new Error(`Falha na validacao (${validateResult.status}).`);
    }

    const importForm = new FormData();
    importForm.append("file", csvBlob, filename);
    importForm.append("mappings_json", JSON.stringify(mappings));

    const importResult = await request("/leads/import", {
      method: "POST",
      token,
      body: importForm,
    });
    report.steps.push({
      step: "import",
      status: importResult.status,
      result: importResult.data,
    });
    if (!importResult.ok) {
      throw new Error(`Falha no import (${importResult.status}).`);
    }

    console.log("Smoke evento/leads concluido com sucesso.");
    console.log(`Evento temporario: ${tempEventId}`);
    console.log(`Import resultado: ${JSON.stringify(importResult.data)}`);
  } catch (error) {
    report.error = error instanceof Error ? error.message : String(error);
    console.error("Smoke evento/leads falhou:", report.error);
    process.exitCode = 1;
  } finally {
    if (token && tempEventId) {
      const cleanupResult = await request(`/evento/${tempEventId}`, {
        method: "DELETE",
        token,
      });
      report.steps.push({
        step: "cleanup_event",
        status: cleanupResult.status,
      });
    }

    const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
    const reportDir = path.join(rootDir, "reports", "smoke-evento-leads");
    await fs.mkdir(reportDir, { recursive: true });
    const reportPath = path.join(reportDir, `${new Date().toISOString().replace(/[:.]/g, "-")}.json`);
    await fs.writeFile(reportPath, JSON.stringify(report, null, 2), "utf8");
    console.log(`Relatorio salvo em ${path.relative(rootDir, reportPath)}`);
  }
}

main();
