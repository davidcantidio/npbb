import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { act, render, waitFor } from "@testing-library/react";
import { useEffect } from "react";

import { useAgeAnalysis } from "../useAgeAnalysis";
import { getAgeAnalysis } from "../../services/dashboard_age_analysis";
import { useAuth } from "../../store/auth";
import type { AgeAnalysisFiltersQuery } from "../../types/dashboard";
import { buildAgeAnalysisFixture } from "../../pages/dashboard/__tests__/ageAnalysisFixtures";

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
    const response = buildAgeAnalysisFixture();
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

    mockedGetAgeAnalysis.mockResolvedValue(buildAgeAnalysisFixture());

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

  it("refetches with normalized filters, preserves cached data and exposes the new error", async () => {
    const response = buildAgeAnalysisFixture();
    mockedGetAgeAnalysis
      .mockResolvedValueOnce(response)
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
      expect(latestState()?.data).toEqual(response);
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
      expect(latestState()?.data).toEqual(response);
      expect(latestState()?.error).toBe("timeout");
    });

    expect(mockedGetAgeAnalysis).toHaveBeenNthCalledWith(2, "token-123", {
      evento_id: 99,
    });
  });
});
