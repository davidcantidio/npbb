import { afterEach, describe, expect, it, vi } from "vitest";

import { getAgeAnalysis } from "../dashboard_age_analysis";
import { fetchWithAuth, handleApiResponse } from "../http";

vi.mock("../http", () => ({
  fetchWithAuth: vi.fn(),
  handleApiResponse: vi.fn(),
}));

const mockedFetchWithAuth = vi.mocked(fetchWithAuth);
const mockedHandleApiResponse = vi.mocked(handleApiResponse);

afterEach(() => {
  vi.clearAllMocks();
});

describe("dashboard_age_analysis service", () => {
  it("calls the age analysis endpoint with explicit timeout and no retries", async () => {
    const payload = { por_evento: [], consolidado: { base_total: 0 } };
    mockedFetchWithAuth.mockResolvedValueOnce({} as Response);
    mockedHandleApiResponse.mockResolvedValueOnce(payload as never);

    const response = await getAgeAnalysis("token-123", {
      evento_id: 4,
      data_inicio: "2026-01-01",
      data_fim: "2026-01-31",
    });

    expect(mockedFetchWithAuth).toHaveBeenCalledWith(
      "/dashboard/leads/analise-etaria?evento_id=4&data_inicio=2026-01-01&data_fim=2026-01-31",
      {
        token: "token-123",
        timeoutMs: 120_000,
        retries: 0,
      },
    );
    expect(response).toBe(payload);
  });

  it("omits the query string when no filters are provided", async () => {
    mockedFetchWithAuth.mockResolvedValueOnce({} as Response);
    mockedHandleApiResponse.mockResolvedValueOnce({} as never);

    await getAgeAnalysis("token-123");

    expect(mockedFetchWithAuth).toHaveBeenCalledWith("/dashboard/leads/analise-etaria", {
      token: "token-123",
      timeoutMs: 120_000,
      retries: 0,
    });
  });
});
