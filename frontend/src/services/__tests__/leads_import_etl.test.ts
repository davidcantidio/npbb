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

  it("previewLeadImportEtl sends sheet_name and max_scan_rows when provided", async () => {
    const fetchMock = mockFetchSequence([
      {
        ok: true,
        status: 200,
        statusText: "OK",
        text: () =>
          Promise.resolve(
            JSON.stringify({
              status: "previewed",
              session_token: "s1",
              total_rows: 1,
              valid_rows: 1,
              invalid_rows: 0,
              dq_report: [],
              sheet_name: "Dados",
              available_sheets: ["Indice", "Dados"],
            }),
          ),
      },
    ]);

    const file = new File(["xlsx"], "leads.xlsx");
    const result = await previewLeadImportEtl("token-123", file, 99, false, {
      sheetName: "Dados",
      maxScanRows: 120,
    });

    const form = fetchMock.mock.calls[0][1].body as FormData;
    expect(form.get("sheet_name")).toBe("Dados");
    expect(form.get("max_scan_rows")).toBe("120");
    expect(result.status).toBe("previewed");
    if (result.status === "previewed") {
      expect(result.sheet_name).toBe("Dados");
      expect(result.available_sheets).toEqual(["Indice", "Dados"]);
    }
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
              persistence_failures: [],
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
    expect(result.persistence_failures).toEqual([]);
  });

  it("commitLeadImportEtl preserves partial_failure responses for retry handling", async () => {
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
              created: 1,
              updated: 1,
              skipped: 1,
              errors: 1,
              strict: false,
              status: "partial_failure",
              persistence_failures: [{ row_number: 7, reason: "db timeout" }],
              dq_report: [],
            }),
          ),
      },
    ]);

    const result = await commitLeadImportEtl("token-123", "session-123", 42, true);

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(result.status).toBe("partial_failure");
    expect(result.persistence_failures).toEqual([{ row_number: 7, reason: "db timeout" }]);
  });
});
