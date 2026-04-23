import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import { useAgeAnalysis } from "../../../hooks/useAgeAnalysis";
import { useReferenciaEventos } from "../../../features/leads/shared";
import { useAuth } from "../../../store/auth";
import { LeadsAgeAnalysisPage } from "../../../features/leads/dashboard";
import { buildAgeAnalysisFixture } from "./ageAnalysisFixtures";

vi.mock("../../../store/auth", () => ({
  useAuth: vi.fn(),
}));

vi.mock("../../../hooks/useAgeAnalysis", () => ({
  useAgeAnalysis: vi.fn(),
}));

vi.mock("../../../features/leads/shared", () => ({
  useReferenciaEventos: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);
const mockedUseAgeAnalysis = vi.mocked(useAgeAnalysis);
const mockedUseReferenciaEventos = vi.mocked(useReferenciaEventos);

function buildHookState(overrides: Partial<ReturnType<typeof useAgeAnalysis>>) {
  return {
    data: null,
    isLoading: false,
    isRefreshing: false,
    error: null,
    lastSuccessfulAt: null,
    refetch: vi.fn(),
    ...overrides,
  };
}

function renderPage(initialEntry = "/dashboard/leads/analise-etaria") {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route path="/dashboard/leads/analise-etaria" element={<LeadsAgeAnalysisPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

function getRequiredCard(element: Element | null, message: string) {
  if (!(element instanceof HTMLElement)) {
    throw new Error(message);
  }

  return element;
}

describe("LeadsAgeAnalysisPage states", { timeout: 30000 }, () => {
  beforeEach(() => {
    mockedUseAuth.mockReturnValue({
      token: "token",
      user: { id: 1, email: "qa@npbb.com.br", tipo_usuario: "admin" },
      loading: false,
      refreshing: false,
      error: null,
      refresh: vi.fn(),
      login: vi.fn(),
      logout: vi.fn(),
    });
    mockedUseReferenciaEventos.mockReturnValue({
      eventOptions: [{ id: 1, nome: "Evento Alpha", data_inicio_prevista: null }],
      isLoadingEvents: false,
      eventsError: null,
    });
  });

  it("renders skeleton loaders while loading", async () => {
    mockedUseAgeAnalysis.mockReturnValue(buildHookState({ isLoading: true }));

    renderPage();

    expect(await screen.findAllByTestId("kpi-card-skeleton")).toHaveLength(8);
    expect(screen.getByTestId("chart-skeleton")).toBeInTheDocument();
    expect(screen.getByTestId("table-skeleton")).toBeInTheDocument();
  });

  it("keeps rendered content during refetch to avoid a loading flash", async () => {
    mockedUseAgeAnalysis.mockReturnValue(
      buildHookState({
        data: buildAgeAnalysisFixture(),
        isLoading: true,
      }),
    );

    renderPage();

    expect(await screen.findByText("Leads válidos")).toBeInTheDocument();
    expect(screen.queryByTestId("kpi-card-skeleton")).not.toBeInTheDocument();
    expect(screen.queryByTestId("chart-skeleton")).not.toBeInTheDocument();
    expect(screen.queryByTestId("table-skeleton")).not.toBeInTheDocument();
  });

  it("renders centered empty state", async () => {
    mockedUseAgeAnalysis.mockReturnValue(
      buildHookState({
        data: buildAgeAnalysisFixture({
        por_evento: [],
        consolidado: {
          ...buildAgeAnalysisFixture().consolidado,
          base_total: 0,
          leads_proponente: 0,
          leads_ativacao: 0,
          leads_canal_desconhecido: 0,
          clientes_bb_volume: null,
          clientes_bb_pct: null,
          nao_clientes_bb_volume: null,
          nao_clientes_bb_pct: null,
          bb_indefinido_volume: 0,
          faixas: {
            faixa_18_25: { volume: 0, pct: 0 },
            faixa_26_40: { volume: 0, pct: 0 },
            faixa_18_40: { volume: 0, pct: 0 },
            fora_18_40: { volume: 0, pct: 0 },
            sem_info_volume: 0,
            sem_info_pct_da_base: 0,
          },
          top_eventos: [],
          media_por_evento: 0,
          mediana_por_evento: 0,
          concentracao_top3_pct: 0,
        },
        confianca_consolidado: {
          ...buildAgeAnalysisFixture().confianca_consolidado,
          base_vinculos: 0,
          base_com_idade_volume: 0,
          base_bb_coberta_volume: 0,
        },
        qualidade_consolidado: {
          base_vinculos: 0,
          sem_cpf_volume: 0,
          sem_cpf_pct: 0,
          sem_data_nascimento_volume: 0,
          sem_data_nascimento_pct: 0,
          sem_nome_completo_volume: 0,
          sem_nome_completo_pct: 0,
        },
        qualidade_por_origem: [],
        insights: {
          resumo: ["Nenhum vinculo lead-evento encontrado para os filtros aplicados."],
          alertas: [],
          flags: [],
        },
      }),
    }),
    );

    renderPage();

    expect(await screen.findByText("Nenhum lead encontrado para os filtros aplicados")).toBeInTheDocument();
  });

  it("renders KPI cards with required consolidated metrics", async () => {
    mockedUseAgeAnalysis.mockReturnValue(buildHookState({ data: buildAgeAnalysisFixture() }));

    renderPage();

    const leadsValidosCard = getRequiredCard(
      (await screen.findByText("Leads válidos")).closest(".MuiCard-root"),
      "Leads validos card not found",
    );
    expect(within(leadsValidosCard).getByText(/10 \(100/)).toBeInTheDocument();

    const clientesCard = getRequiredCard(screen.getByText(/4 \(40,0%\)/).closest(".MuiCard-root"), "Clientes BB card not found");
    expect(within(clientesCard).getByText("Clientes BB")).toBeInTheDocument();
    expect(within(clientesCard).getByText(/4 \(40,0%\)/)).toBeInTheDocument();
    expect(within(clientesCard).getByText("Base BB coberta: 9")).toBeInTheDocument();
    expect(within(clientesCard).getByText("Cobertura BB")).toBeInTheDocument();
    expect(within(clientesCard).getByText("90.0%")).toBeInTheDocument();

    const faixaCard = getRequiredCard(screen.getByLabelText("Faixa etaria dominante"), "Faixa dominante card not found");
    expect(within(faixaCard).getByText("18–25")).toBeInTheDocument();

    const eventosCard = getRequiredCard(screen.getByText("Eventos").closest(".MuiCard-root"), "Eventos card not found");
    expect(within(eventosCard).getByText("1")).toBeInTheDocument();
  });

  it("shows error toast with retry action", async () => {
    const refetch = vi.fn();
    const user = userEvent.setup();
    mockedUseAgeAnalysis.mockReturnValue(
      buildHookState({
        error: "Nao foi possivel carregar a analise etaria.",
        refetch,
      }),
    );

    renderPage();

    expect(await screen.findByText("Nao foi possivel carregar a analise etaria.")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /tentar novamente/i }));
    expect(refetch).toHaveBeenCalledTimes(1);
  });

  it("shows and restores warning coverage banner after filters change", async () => {
    const user = userEvent.setup();
    const fixture = buildAgeAnalysisFixture({
      por_evento: [
        {
          ...buildAgeAnalysisFixture().por_evento[0],
          clientes_bb_volume: null,
          clientes_bb_pct: null,
          nao_clientes_bb_volume: null,
          nao_clientes_bb_pct: null,
          cobertura_bb_pct: 65,
        },
      ],
      consolidado: {
        ...buildAgeAnalysisFixture().consolidado,
        clientes_bb_volume: null,
        clientes_bb_pct: null,
        nao_clientes_bb_volume: null,
        nao_clientes_bb_pct: null,
        cobertura_bb_pct: 65,
      },
    });

    mockedUseAgeAnalysis.mockReturnValue(buildHookState({ data: fixture }));

    renderPage();

    expect(await screen.findByTestId("coverage-banner-warning-default")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /close/i }));
    expect(screen.queryByTestId("coverage-banner-warning-default")).not.toBeInTheDocument();

    const table = screen.getByRole("table", { name: /tabela de eventos da analise etaria/i });
    await user.click(within(table).getByText("Evento Alpha"));

    expect(await screen.findByTestId("coverage-banner-warning-default")).toBeInTheDocument();
  });

  it("renders danger coverage state and partial-data hints", async () => {
    mockedUseAgeAnalysis.mockReturnValue(
      buildHookState({
        data: buildAgeAnalysisFixture({
        por_evento: [
          {
            ...buildAgeAnalysisFixture().por_evento[0],
            clientes_bb_volume: null,
            clientes_bb_pct: null,
            nao_clientes_bb_volume: null,
            nao_clientes_bb_pct: null,
            cobertura_bb_pct: 12,
          },
        ],
        consolidado: {
          ...buildAgeAnalysisFixture().consolidado,
          clientes_bb_volume: null,
          clientes_bb_pct: null,
          nao_clientes_bb_volume: null,
          nao_clientes_bb_pct: null,
            cobertura_bb_pct: 12,
          },
        }),
      }),
    );

    renderPage();

    expect(await screen.findByTestId("coverage-banner-danger-default")).toBeInTheDocument();
    expect(await screen.findByTestId("coverage-banner-danger-compact")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Dados de vinculo BB indisponiveis neste recorte - realize o cruzamento com a base de dados do Banco.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "Dados de vinculo BB indisponiveis para este evento - realize o cruzamento com a base de dados do Banco.",
      ),
    ).toBeInTheDocument();
    expect(screen.getAllByText("(dados parciais)").length).toBeGreaterThan(0);
  });
});
