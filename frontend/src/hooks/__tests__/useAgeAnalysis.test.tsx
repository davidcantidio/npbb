import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { act, render, waitFor } from "@testing-library/react";
import { useEffect } from "react";

import { useAgeAnalysis } from "../useAgeAnalysis";
import { getAgeAnalysis } from "../../services/dashboard_age_analysis";
import { useAuth } from "../../store/auth";
import type { AgeAnalysisFiltersQuery, AgeAnalysisResponse } from "../../types/dashboard";

vi.mock("../../store/auth", () => ({
  useAuth: vi.fn(),
}));

vi.mock("../../services/dashboard_age_analysis", () => ({
  getAgeAnalysis: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);
const mockedGetAgeAnalysis = vi.mocked(getAgeAnalysis);

type HookState = ReturnType<typeof useAgeAnalysis>;

function HookStateObserver({
  filters,
  onState,
}: {
  filters: AgeAnalysisFiltersQuery;
  onState: (state: HookState) => void;
}) {
  const state = useAgeAnalysis(filters);

  useEffect(() => {
    onState(state);
  }, [onState, state]);

  return null;
}

function buildFixture(overrides: Partial<AgeAnalysisResponse> = {}): AgeAnalysisResponse {
  return {
    version: 1,
    generated_at: "2026-03-07T12:00:00Z",
    filters: {
      data_inicio: null,
      data_fim: null,
      evento_id: null,
    },
    por_evento: [
      {
        evento_id: 1,
        evento_nome: "Evento Alpha",
        cidade: "Sao Paulo",
        estado: "SP",
        base_leads: 10,
        clientes_bb_volume: 4,
        clientes_bb_pct: 40,
        cobertura_bb_pct: 90,
        faixa_dominante: "faixa_18_25",
        faixas: {
          faixa_18_25: { volume: 5, pct: 50 },
          faixa_26_40: { volume: 3, pct: 30 },
          fora_18_40: { volume: 2, pct: 20 },
          sem_info_volume: 0,
          sem_info_pct_da_base: 0,
        },
      },
    ],
    consolidado: {
      base_total: 10,
      clientes_bb_volume: 4,
      clientes_bb_pct: 40,
      cobertura_bb_pct: 90,
      faixas: {
        faixa_18_25: { volume: 5, pct: 50 },
        faixa_26_40: { volume: 3, pct: 30 },
        fora_18_40: { volume: 2, pct: 20 },
        sem_info_volume: 0,
        sem_info_pct_da_base: 0,
      },
      top_eventos: [
        {
          evento_id: 1,
          evento_nome: "Evento Alpha",
          base_leads: 10,
          faixa_dominante: "faixa_18_25",
        },
      ],
      media_por_evento: 10,
      mediana_por_evento: 10,
      concentracao_top3_pct: 100,
    },
    ...overrides,
  };
}

describe("useAgeAnalysis", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedUseAuth.mockReturnValue({
      token: "token-123",
      user: { id: 1, email: "qa@npbb.com.br", tipo_usuario: "admin" },
      loading: false,
      refreshing: false,
      error: null,
      refresh: vi.fn(),
      login: vi.fn(),
      logout: vi.fn(),
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("fetches age analysis payload with normalized filters and returns loading, data and error states", async () => {
    const filters: AgeAnalysisFiltersQuery = {
      evento_id: 42,
      data_inicio: "2026-01-01",
      data_fim: "",
    };
    const response = buildFixture();
    mockedGetAgeAnalysis.mockResolvedValue(response);

    const states: HookState[] = [];

    render(<HookStateObserver filters={filters} onState={(state) => states.push(state)} />);

    const latestState = () => states[states.length - 1];

    await waitFor(() => {
      expect(latestState()?.isLoading).toBe(true);
    });
    await waitFor(() => {
      expect(latestState()?.isLoading).toBe(false);
    });

    expect(latestState()?.data).toEqual(response);
    expect(latestState()?.error).toBeNull();
    expect(mockedGetAgeAnalysis).toHaveBeenCalledTimes(1);
    expect(mockedGetAgeAnalysis).toHaveBeenCalledWith("token-123", {
      evento_id: 42,
      data_inicio: "2026-01-01",
    });
  });

  it("sets authentication error without invoking API when token is unavailable", async () => {
    mockedUseAuth.mockReturnValue({
      token: null,
      user: null,
      loading: false,
      refreshing: false,
      error: null,
      refresh: vi.fn(),
      login: vi.fn(),
      logout: vi.fn(),
    });

    mockedGetAgeAnalysis.mockResolvedValue(buildFixture());

    const states: HookState[] = [];
    render(<HookStateObserver filters={{}} onState={(state) => states.push(state)} />);

    const latestState = () => states[states.length - 1];

    await waitFor(() => {
      expect(latestState()?.isLoading).toBe(false);
    });

    expect(latestState()?.error).toBe("Usuario nao autenticado.");
    expect(latestState()?.data).toBeNull();
    expect(mockedGetAgeAnalysis).not.toHaveBeenCalled();
  });

  it("maps request errors into hook error state and clears data", async () => {
    mockedGetAgeAnalysis.mockRejectedValue(new Error("network-failed"));

    const states: HookState[] = [];
    render(<HookStateObserver filters={{}} onState={(state) => states.push(state)} />);

    const latestState = () => states[states.length - 1];

    await waitFor(() => {
      expect(latestState()?.isLoading).toBe(false);
    });

    expect(latestState()?.data).toBeNull();
    expect(latestState()?.error).toBe("network-failed");
  });

  it("refetches with normalized filters and resets data on subsequent failures", async () => {
    mockedGetAgeAnalysis
      .mockResolvedValueOnce(buildFixture())
      .mockRejectedValueOnce(new Error("timeout"));

    const states: HookState[] = [];

    render(
      <HookStateObserver
        filters={{
          evento_id: 99,
          data_inicio: "",
          data_fim: "",
        }}
        onState={(state) => states.push(state)}
      />,
    );

    const latestState = () => states[states.length - 1];

    await waitFor(() => {
      expect(latestState()?.isLoading).toBe(false);
      expect(latestState()?.data).toEqual(buildFixture());
    });

    expect(mockedGetAgeAnalysis).toHaveBeenCalledTimes(1);
    expect(mockedGetAgeAnalysis).toHaveBeenCalledWith("token-123", {
      evento_id: 99,
    });

    await act(async () => {
      await latestState()?.refetch();
    });

    await waitFor(() => {
      expect(mockedGetAgeAnalysis).toHaveBeenCalledTimes(2);
      expect(latestState()?.isLoading).toBe(false);
      expect(latestState()?.data).toBeNull();
      expect(latestState()?.error).toBe("timeout");
    });

    expect(mockedGetAgeAnalysis).toHaveBeenNthCalledWith(2, "token-123", {
      evento_id: 99,
    });
  });
});
