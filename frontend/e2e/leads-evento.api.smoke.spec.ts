import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { expect, test } from "@playwright/test";

import { authHeaders, createApiContext, loginViaApi } from "./support/auth-helpers";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const csvTemplatePath = path.join(__dirname, "fixtures", "leads-import-smoke.csv");

type CatalogItem = { id: number; nome: string };

async function buildCsvBuffer(eventName: string): Promise<Buffer> {
  const template = await readFile(csvTemplatePath, "utf8");
  return Buffer.from(template.replace(/__EVENTO_NOME__/g, eventName), "utf8");
}

test("runs the legacy evento/leads smoke through Playwright API", async () => {
  const api = await createApiContext();
  let eventId: number | null = null;
  let headers: Record<string, string> | null = null;

  try {
    const login = await loginViaApi(api);
    headers = authHeaders(login.access_token);

    const statusesResponse = await api.get("/evento/all/status-evento", { headers });
    expect(statusesResponse.status()).toBe(200);
    const statuses = (await statusesResponse.json()) as CatalogItem[];
    const plannedStatus = statuses.find((item) => item.nome === "Planejado") ?? statuses[0];
    expect(plannedStatus).toBeTruthy();

    const diretoriasResponse = await api.get("/evento/all/diretorias", { headers });
    expect(diretoriasResponse.status()).toBe(200);
    const diretorias = (await diretoriasResponse.json()) as CatalogItem[];
    const dipes = diretorias.find((item) => item.nome === "DIPES") ?? diretorias[0];
    expect(dipes).toBeTruthy();

    const eventName = `SMOKE-EVENTO-${Date.now()}`;
    const createEventResponse = await api.post("/evento/", {
      headers: {
        ...headers,
        "Content-Type": "application/json",
      },
      data: {
        nome: eventName,
        descricao: "Evento temporario para smoke Playwright",
        cidade: "Sao Paulo",
        estado: "SP",
        diretoria_id: dipes.id,
        status_id: plannedStatus.id,
        data_inicio_prevista: "2026-03-10",
        data_fim_prevista: "2026-03-12",
        concorrencia: false,
      },
    });
    expect(createEventResponse.status()).toBe(201);
    const createdEvent = (await createEventResponse.json()) as { id: number; nome: string };
    eventId = createdEvent.id;

    const fileBuffer = await buildCsvBuffer(eventName);
    const previewResponse = await api.post("/leads/import/preview", {
      headers,
      multipart: {
        file: {
          name: "leads-import-smoke.csv",
          mimeType: "text/csv",
          buffer: fileBuffer,
        },
        sample_rows: "10",
      },
    });
    expect(previewResponse.status()).toBe(200);
    const previewBody = (await previewResponse.json()) as {
      headers: string[];
      suggestions: Array<{ coluna: string; campo: string | null }>;
    };
    expect(previewBody.headers).toEqual(["nome", "email", "cpf", "evento_nome"]);

    const mappings = [
      { coluna: "nome", campo: "nome" },
      { coluna: "email", campo: "email" },
      { coluna: "cpf", campo: "cpf" },
      { coluna: "evento_nome", campo: "evento_nome" },
    ];

    const validateResponse = await api.post("/leads/import/validate", {
      headers: {
        ...headers,
        "Content-Type": "application/json",
      },
      data: mappings,
    });
    expect(validateResponse.status()).toBe(200);
    expect(await validateResponse.json()).toEqual({ ok: true });

    const importResponse = await api.post("/leads/import", {
      headers,
      multipart: {
        file: {
          name: "leads-import-smoke.csv",
          mimeType: "text/csv",
          buffer: fileBuffer,
        },
        mappings_json: JSON.stringify(mappings),
      },
    });
    expect(importResponse.status()).toBe(200);
    const importBody = (await importResponse.json()) as {
      filename: string;
      created: number;
      updated: number;
      skipped: number;
    };
    expect(importBody.filename).toBe("leads-import-smoke.csv");
    expect(importBody.created).toBeGreaterThanOrEqual(1);
    expect(importBody.updated).toBe(0);
    expect(importBody.skipped).toBe(0);
  } finally {
    if (headers && eventId !== null) {
      await api.delete(`/evento/${eventId}`, {
        headers,
        failOnStatusCode: false,
      });
    }
    await api.dispose();
  }
});
