import { afterEach, describe, expect, it, vi } from "vitest";
import {
  createLeadBatch,
  createLeadBatchIntake,
  getLeadBatchPreview,
  getLeadImportMetadataHint,
  normalizeLeadImportHintDateInput,
} from "../leads_import";

type FetchResponse = {
  ok: boolean;
  status: number;
  statusText: string;
  text: () => Promise<string>;
};

function mockFetchSequence(responses: FetchResponse[]) {
  const fetchMock = vi.fn().mockImplementation(() => {
    const next = responses.shift();
    if (!next) {
      return Promise.reject(new Error("No more mocked responses"));
    }
    return Promise.resolve(next);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("leads_import Bronze service", () => {
  it("createLeadBatch posts multipart payload and returns backend contract", async () => {
    const fetchMock = mockFetchSequence([
      {
        ok: true,
        status: 201,
        statusText: "Created",
        text: () =>
          Promise.resolve(
            JSON.stringify({
              id: 10,
              enviado_por: 2,
              plataforma_origem: "email",
              data_envio: "2026-03-05T00:00:00",
              data_upload: "2026-03-05T12:00:00",
              nome_arquivo_original: "leads.csv",
              stage: "bronze",
              evento_id: null,
              origem_lote: "proponente",
              enrichment_only: false,
              tipo_lead_proponente: null,
              ativacao_id: null,
              pipeline_status: "pending",
              pipeline_progress: null,
              created_at: "2026-03-05T12:00:00",
            }),
          ),
      },
    ]);

    const file = new File(["nome,email"], "leads.csv", { type: "text/csv" });
    const result = await createLeadBatch("token-123", {
      quem_enviou: "analista@npbb.com.br",
      plataforma_origem: "email",
      data_envio: "2026-03-05",
      file,
    });

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringMatching(/\/leads\/batches$/),
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({ Authorization: "Bearer token-123" }),
        body: expect.any(FormData),
      }),
    );
    expect(result.id).toBe(10);
    expect(result.stage).toBe("bronze");
  });

  it("createLeadBatch includes evento_id in FormData when provided", async () => {
    const fetchMock = mockFetchSequence([
      {
        ok: true,
        status: 201,
        statusText: "Created",
        text: () =>
          Promise.resolve(
            JSON.stringify({
              id: 11,
              enviado_por: 2,
              plataforma_origem: "email",
              data_envio: "2026-03-05T00:00:00",
              data_upload: "2026-03-05T12:00:00",
              nome_arquivo_original: "leads.csv",
              stage: "bronze",
              evento_id: 7,
              origem_lote: "proponente",
              enrichment_only: false,
              tipo_lead_proponente: null,
              ativacao_id: null,
              pipeline_status: "pending",
              pipeline_progress: null,
              created_at: "2026-03-05T12:00:00",
            }),
          ),
      },
    ]);

    const file = new File(["nome,email"], "leads.csv", { type: "text/csv" });
    await createLeadBatch("token-123", {
      plataforma_origem: "email",
      data_envio: "2026-03-05",
      evento_id: 7,
      origem_lote: "ativacao",
      ativacao_id: 3,
      file,
    });

    const init = fetchMock.mock.calls[0][1] as RequestInit;
    const body = init.body as FormData;
    expect(body.get("evento_id")).toBe("7");
    expect(body.get("origem_lote")).toBe("ativacao");
    expect(body.get("ativacao_id")).toBe("3");
  });

  it("createLeadBatch includes enrichment_only in FormData when enabled", async () => {
    const fetchMock = mockFetchSequence([
      {
        ok: true,
        status: 201,
        statusText: "Created",
        text: () =>
          Promise.resolve(
            JSON.stringify({
              id: 12,
              enviado_por: 2,
              plataforma_origem: "email",
              data_envio: "2026-03-05T00:00:00",
              data_upload: "2026-03-05T12:00:00",
              nome_arquivo_original: "leads.csv",
              stage: "bronze",
              evento_id: null,
              origem_lote: null,
              enrichment_only: true,
              tipo_lead_proponente: "entrada_evento",
              ativacao_id: null,
              pipeline_status: "pending",
              pipeline_progress: null,
              created_at: "2026-03-05T12:00:00",
            }),
          ),
      },
    ]);

    const file = new File(["nome,email"], "leads.csv", { type: "text/csv" });
    await createLeadBatch("token-123", {
      plataforma_origem: "email",
      data_envio: "2026-03-05",
      origem_lote: "proponente",
      enrichment_only: true,
      tipo_lead_proponente: "entrada_evento",
      file,
    });

    const init = fetchMock.mock.calls[0][1] as RequestInit;
    const body = init.body as FormData;
    expect(body.get("enrichment_only")).toBe("true");
    expect(body.get("evento_id")).toBeNull();
  });

  it("createLeadBatchIntake omits origem_lote when enrichment_only uses optional classification", async () => {
    const fetchMock = mockFetchSequence([
      {
        ok: true,
        status: 201,
        statusText: "Created",
        text: () =>
          Promise.resolve(
            JSON.stringify({
              items: [
                {
                  client_row_id: "row-1",
                  batch: {
                    id: 13,
                    enviado_por: 2,
                    plataforma_origem: "email",
                    data_envio: "2026-03-05T00:00:00",
                    data_upload: "2026-03-05T12:00:00",
                    nome_arquivo_original: "leads.csv",
                    stage: "bronze",
                    evento_id: null,
                    origem_lote: null,
                    enrichment_only: true,
                    tipo_lead_proponente: "entrada_evento",
                    ativacao_id: null,
                    pipeline_status: "pending",
                    pipeline_progress: null,
                    pipeline_report: null,
                    created_at: "2026-03-05T12:00:00",
                  },
                  preview: {
                    headers: ["nome", "email"],
                    rows: [["Maria", "maria@npbb.com.br"]],
                    total_rows: 1,
                  },
                  hint_applied: null,
                },
              ],
            }),
          ),
      },
    ]);

    const file = new File(["nome,email"], "leads.csv", { type: "text/csv" });
    await createLeadBatchIntake("token-123", {
      items: [
        {
          client_row_id: "row-1",
          plataforma_origem: "email",
          data_envio: "2026-03-05",
          enrichment_only: true,
          tipo_lead_proponente: "entrada_evento",
          file,
        },
      ],
    });

    const init = fetchMock.mock.calls[0][1] as RequestInit;
    const body = init.body as FormData;
    const manifestRaw = body.get("manifest_json");
    expect(typeof manifestRaw).toBe("string");
    const manifest = JSON.parse(String(manifestRaw));
    expect(manifest.items).toEqual([
      expect.objectContaining({
        client_row_id: "row-1",
        enrichment_only: true,
        tipo_lead_proponente: "entrada_evento",
      }),
    ]);
    expect(manifest.items[0]).not.toHaveProperty("evento_id");
    expect(manifest.items[0]).not.toHaveProperty("ativacao_id");
    expect(manifest.items[0]).not.toHaveProperty("origem_lote");
  });

  it("createLeadBatchIntake omits origem_lote and tipo when enrichment_only uses nao informar", async () => {
    const fetchMock = mockFetchSequence([
      {
        ok: true,
        status: 201,
        statusText: "Created",
        text: () =>
          Promise.resolve(
            JSON.stringify({
              items: [
                {
                  client_row_id: "row-1",
                  batch: {
                    id: 14,
                    enviado_por: 2,
                    plataforma_origem: "email",
                    data_envio: "2026-03-05T00:00:00",
                    data_upload: "2026-03-05T12:00:00",
                    nome_arquivo_original: "leads.csv",
                    stage: "bronze",
                    evento_id: null,
                    origem_lote: null,
                    enrichment_only: true,
                    tipo_lead_proponente: null,
                    ativacao_id: null,
                    pipeline_status: "pending",
                    pipeline_progress: null,
                    pipeline_report: null,
                    created_at: "2026-03-05T12:00:00",
                  },
                  preview: {
                    headers: ["nome", "email"],
                    rows: [["Maria", "maria@npbb.com.br"]],
                    total_rows: 1,
                  },
                  hint_applied: null,
                },
              ],
            }),
          ),
      },
    ]);

    const file = new File(["nome,email"], "leads.csv", { type: "text/csv" });
    await createLeadBatchIntake("token-123", {
      items: [
        {
          client_row_id: "row-1",
          plataforma_origem: "email",
          data_envio: "2026-03-05",
          enrichment_only: true,
          file,
        },
      ],
    });

    const init = fetchMock.mock.calls[0][1] as RequestInit;
    const body = init.body as FormData;
    const manifestRaw = body.get("manifest_json");
    expect(typeof manifestRaw).toBe("string");
    const manifest = JSON.parse(String(manifestRaw));
    expect(manifest.items[0]).toMatchObject({
      client_row_id: "row-1",
      enrichment_only: true,
    });
    expect(manifest.items[0]).not.toHaveProperty("evento_id");
    expect(manifest.items[0]).not.toHaveProperty("ativacao_id");
    expect(manifest.items[0]).not.toHaveProperty("origem_lote");
    expect(manifest.items[0]).not.toHaveProperty("tipo_lead_proponente");
  });

  it("getLeadBatchPreview fetches sample contract unchanged", async () => {
    const fetchMock = mockFetchSequence([
      {
        ok: true,
        status: 200,
        statusText: "OK",
        text: () =>
          Promise.resolve(
            JSON.stringify({
              headers: ["nome", "email"],
              rows: [["Maria", "maria@npbb.com.br"]],
              total_rows: 1,
            }),
          ),
      },
    ]);

    const result = await getLeadBatchPreview("token-123", 10);

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringMatching(/\/leads\/batches\/10\/preview$/),
      expect.objectContaining({
        method: "GET",
        headers: expect.objectContaining({ Authorization: "Bearer token-123" }),
      }),
    );
    expect(result).toEqual({
      headers: ["nome", "email"],
      rows: [["Maria", "maria@npbb.com.br"]],
      total_rows: 1,
    });
  });

  it("getLeadImportMetadataHint returns null on 204", async () => {
    const fetchMock = mockFetchSequence([
      {
        ok: true,
        status: 204,
        statusText: "No Content",
        text: () => Promise.resolve(""),
      },
    ]);

    const result = await getLeadImportMetadataHint("token-123", "a".repeat(64));

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringMatching(/\/leads\/batches\/import-hint\?arquivo_sha256=/),
      expect.objectContaining({
        method: "GET",
        headers: expect.objectContaining({ Authorization: "Bearer token-123" }),
      }),
    );
    expect(result).toBeNull();
  });

  it("normalizeLeadImportHintDateInput keeps yyyy-mm-dd for date inputs", () => {
    expect(normalizeLeadImportHintDateInput("2026-03-05T12:30:00")).toBe("2026-03-05");
    expect(normalizeLeadImportHintDateInput("2026-03-05")).toBe("2026-03-05");
    expect(normalizeLeadImportHintDateInput("")).toBe("");
  });
});
