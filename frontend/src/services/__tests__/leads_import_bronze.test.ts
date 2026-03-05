import { afterEach, describe, expect, it, vi } from "vitest";
import { createLeadBatch, getLeadBatchPreview } from "../leads_import";

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
              pipeline_status: "pending",
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
});
