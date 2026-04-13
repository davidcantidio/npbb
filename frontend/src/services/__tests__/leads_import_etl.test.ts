import { afterEach, describe, expect, it, vi } from "vitest";

import { commitLeadImportEtl, previewLeadImportEtl } from "../leads_import";

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

describe("leads_import ETL service", () => {
  it("previewLeadImportEtl returns the backend contract without client-side remapping", async () => {
    const fetchMock = mockFetchSequence([
      {
        ok: true,
        status: 200,
        statusText: "OK",
        text: () =>
          Promise.resolve(
            JSON.stringify({
              status: "previewed",
              session_token: "session-123",
              total_rows: 4,
              valid_rows: 3,
              invalid_rows: 1,
              dq_report: [
                {
                  check_name: "dq.preview.rejected_rows",
                  severity: "error",
                  affected_rows: 1,
                  sample: [{ row_number: 2 }],
                },
              ],
            }),
          ),
      },
    ]);

    const file = new File(["xlsx"], "leads.xlsx");
    const result = await previewLeadImportEtl("token-123", file, 42, true);

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringMatching(/\/leads\/import\/etl\/preview$/),
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({ Authorization: "Bearer token-123" }),
      }),
    );
    expect(result).toEqual({
      status: "previewed",
      session_token: "session-123",
      total_rows: 4,
      valid_rows: 3,
      invalid_rows: 1,
      dq_report: [
        {
          check_name: "dq.preview.rejected_rows",
          severity: "error",
          affected_rows: 1,
          sample: [{ row_number: 2 }],
        },
      ],
    });
  });

  it("previewLeadImportEtl sends optional header fallback fields", async () => {
    const fetchMock = mockFetchSequence([
      {
        ok: true,
        status: 200,
        statusText: "OK",
        text: () =>
          Promise.resolve(
            JSON.stringify({
              status: "cpf_column_required",
              message: "Selecione CPF",
              header_row: 2,
              required_fields: ["cpf"],
              columns: [{ column_index: 2, column_letter: "B", source_value: "Documento" }],
            }),
          ),
      },
    ]);

    const file = new File(["xlsx"], "leads.xlsx");
    const result = await previewLeadImportEtl("token-123", file, 42, false, {
      headerRow: 2,
      fieldAliases: { cpf: { column_index: 2, source_value: "Documento" } },
    });

    const form = fetchMock.mock.calls[0][1].body as FormData;
    expect(form.get("header_row")).toBe("2");
    expect(form.get("field_aliases_json")).toBe(JSON.stringify({ cpf: { column_index: 2, source_value: "Documento" } }));
    expect(result.status).toBe("cpf_column_required");
  });

  it("commitLeadImportEtl posts the public payload and returns the backend contract unchanged", async () => {
    const fetchMock = mockFetchSequence([
      {
        ok: true,
        status: 200,
        statusText: "OK",
        text: () =>
          Promise.resolve(
            JSON.stringify({
              session_token: "session-123",
              total_rows: 4,
              valid_rows: 3,
              invalid_rows: 1,
              created: 2,
              updated: 1,
              skipped: 0,
              errors: 0,
              strict: false,
              status: "committed",
              dq_report: [
                {
                  check_name: "dq.preview.duplicates",
                  severity: "warning",
                  affected_rows: 2,
                  sample: [{ dedupe_key: "abc" }],
                },
              ],
            }),
          ),
      },
    ]);

    const result = await commitLeadImportEtl("token-123", "session-123", 42, true);

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringMatching(/\/leads\/import\/etl\/commit$/),
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({
          Authorization: "Bearer token-123",
          "Content-Type": "application/json",
        }),
        body: JSON.stringify({
          session_token: "session-123",
          evento_id: 42,
          force_warnings: true,
        }),
      }),
    );
    expect(result.status).toBe("committed");
    expect(result.dq_report[0].check_name).toBe("dq.preview.duplicates");
  });
});
