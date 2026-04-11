import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import PipelineStatusPage from "../leads/PipelineStatusPage";
import { useAuth } from "../../store/auth";
import {
  executarPipeline,
  getLeadBatch,
  type LeadBatch,
  type PipelineReport,
} from "../../services/leads_import";

vi.mock("../../store/auth", () => ({ useAuth: vi.fn() }));
vi.mock("../../services/leads_import", () => ({
  executarPipeline: vi.fn(),
  getLeadBatch: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);
const mockedExecutarPipeline = vi.mocked(executarPipeline);
const mockedGetLeadBatch = vi.mocked(getLeadBatch);

const basePipelineReport: PipelineReport = {
  lote_id: "10",
  run_timestamp: "2026-03-09T12:30:00",
  totals: {
    raw_rows: 4,
    valid_rows: 3,
    discarded_rows: 1,
  },
  quality_metrics: {
    cpf_invalid_discarded: 1,
    telefone_invalid: 0,
    data_evento_invalid: 0,
    data_nascimento_invalid: 0,
    duplicidades_cpf_evento: 0,
    cidade_fora_mapeamento: 0,
  },
  gate: {
    status: "PASS",
    decision: "promote",
    fail_reasons: [],
    warnings: [],
  },
};

function createBatch(overrides: Partial<LeadBatch> = {}): LeadBatch {
  return {
    id: 10,
    enviado_por: 1,
    plataforma_origem: "email",
    data_envio: "2026-03-09T00:00:00",
    data_upload: "2026-03-09T12:00:00",
    nome_arquivo_original: "leads.csv",
    stage: "gold",
    evento_id: 42,
    pipeline_status: "pass",
    pipeline_report: basePipelineReport,
    created_at: "2026-03-09T12:00:00",
    ...overrides,
  };
}

function renderPipelineStatusPage() {
  return render(
    <MemoryRouter initialEntries={["/leads/pipeline?batch_id=10"]}>
      <Routes>
        <Route path="/leads/pipeline" element={<PipelineStatusPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("PipelineStatusPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedUseAuth.mockReturnValue({
      token: "token-123",
      user: { id: 1, email: "demo@npbb.com.br", tipo_usuario: "admin", agencia_id: null },
      loading: false,
      refreshing: false,
      error: null,
      refresh: vi.fn(),
      login: vi.fn(),
      logout: vi.fn(),
    });
    mockedExecutarPipeline.mockResolvedValue({ batch_id: 10, status: "queued" });
    mockedGetLeadBatch.mockResolvedValue(
      createBatch({
        stage: "silver",
        pipeline_status: "pending",
        pipeline_report: null,
      }),
    );
  });

  it("renders with minimal route and auth context", async () => {
    renderPipelineStatusPage();

    expect(await screen.findByText(/Pipeline Gold/)).toBeInTheDocument();
    expect(screen.getByText("leads.csv")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Executar Pipeline" })).toBeInTheDocument();
    expect(mockedGetLeadBatch).toHaveBeenCalledWith("token-123", 10);
  });

  it("shows pipeline state when getLeadBatch returns a valid batch", async () => {
    mockedGetLeadBatch.mockResolvedValue(createBatch());

    renderPipelineStatusPage();

    expect(await screen.findByText(/Pipeline Gold/)).toBeInTheDocument();
    expect(screen.getByText("leads.csv")).toBeInTheDocument();
    expect(screen.getByText("email")).toBeInTheDocument();
    expect(screen.getByText("GOLD")).toBeInTheDocument();
    expect(screen.getByText("Aprovado")).toBeInTheDocument();
    expect(screen.getByText("3 leads promovidos para Gold")).toBeInTheDocument();
  });

  it("shows warning feedback when the pipeline passes with warnings", async () => {
    const warningReport: PipelineReport = {
      ...basePipelineReport,
      quality_metrics: {
        ...basePipelineReport.quality_metrics,
        telefone_invalid: 1,
      },
      gate: {
        ...basePipelineReport.gate,
        status: "PASS_WITH_WARNINGS",
        warnings: ["Telefone invalido"],
      },
    };
    mockedGetLeadBatch.mockResolvedValue(
      createBatch({
        pipeline_status: "pass_with_warnings",
        pipeline_report: warningReport,
      }),
    );

    renderPipelineStatusPage();

    expect(await screen.findByText("Aprovado c/ avisos")).toBeInTheDocument();
    expect(screen.getByText("Avisos:")).toBeInTheDocument();
    expect(screen.getByText("Telefone invalido")).toBeInTheDocument();
    expect(screen.getByText(/PASS WITH WARNINGS/)).toBeInTheDocument();
  });
});
