import { act, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import PipelineStatusPage from "../leads/PipelineStatusPage";
import { ApiError } from "../../services/http";
import { useAuth } from "../../store/auth";
import {
  executarPipeline,
  getApiReadiness,
  getLeadBatch,
  type LeadBatch,
  type PipelineReport,
} from "../../services/leads_import";

vi.mock("../../store/auth", () => ({ useAuth: vi.fn() }));
vi.mock("../../services/leads_import", () => ({
  executarPipeline: vi.fn(),
  getApiReadiness: vi.fn(),
  getLeadBatch: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);
const mockedExecutarPipeline = vi.mocked(executarPipeline);
const mockedGetApiReadiness = vi.mocked(getApiReadiness);
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
    data_nascimento_missing: 0,
    duplicidades_cpf_evento: 0,
    cidade_fora_mapeamento: 0,
    localidade_invalida: 0,
    localidade_nao_resolvida: 0,
    localidade_fora_brasil: 0,
    localidade_cidade_uf_inconsistente: 0,
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
    origem_lote: "proponente",
    enrichment_only: false,
    tipo_lead_proponente: "entrada_evento",
    ativacao_id: null,
    pipeline_status: "pass",
    pipeline_progress: null,
    pipeline_report: basePipelineReport,
    created_at: "2026-03-09T12:00:00",
    ...overrides,
  };
}

function renderPipelineStatusPage(element = <PipelineStatusPage />) {
  return render(
    <MemoryRouter initialEntries={["/leads/pipeline?batch_id=10"]}>
      <Routes>
        <Route path="/leads/pipeline" element={element} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("PipelineStatusPage", () => {
  beforeEach(() => {
    mockedUseAuth.mockReset();
    mockedExecutarPipeline.mockReset();
    mockedGetApiReadiness.mockReset();
    mockedGetLeadBatch.mockReset();
    vi.spyOn(console, "info").mockImplementation(() => undefined);
    vi.spyOn(console, "warn").mockImplementation(() => undefined);
    vi.spyOn(console, "error").mockImplementation(() => undefined);
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
    mockedGetApiReadiness.mockResolvedValue({ status: "ready" });
    mockedGetLeadBatch.mockResolvedValue(
      createBatch({
        stage: "silver",
        pipeline_status: "pending",
        pipeline_progress: null,
        pipeline_report: null,
      }),
    );
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it("renders with minimal route and auth context", async () => {
    renderPipelineStatusPage();

    expect(await screen.findByText(/Pipeline Gold/)).toBeInTheDocument();
    expect(screen.getByText("leads.csv")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Executar Pipeline" })).toBeInTheDocument();
    expect(mockedGetLeadBatch).toHaveBeenCalledWith("token-123", 10);
  }, 10000);

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

  it("calls onBatchLoaded with the fetched batch when the status request succeeds", async () => {
    const onBatchLoaded = vi.fn();
    const fetchedBatch = createBatch();
    mockedGetLeadBatch.mockResolvedValue(fetchedBatch);

    renderPipelineStatusPage(<PipelineStatusPage onBatchLoaded={onBatchLoaded} />);

    expect(await screen.findByText(/Pipeline Gold/)).toBeInTheDocument();
    expect(onBatchLoaded).toHaveBeenCalledWith(fetchedBatch);
  });

  it("does not poll for a silver batch that is still pending without pipeline_progress", async () => {
    mockedGetLeadBatch.mockResolvedValue(
      createBatch({
        stage: "silver",
        pipeline_status: "pending",
        pipeline_progress: null,
        pipeline_report: null,
      }),
    );

    renderPipelineStatusPage();

    expect(await screen.findByRole("button", { name: "Executar Pipeline" })).toBeInTheDocument();
    expect(mockedGetLeadBatch).toHaveBeenCalledTimes(1);

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 1800));
    });

    expect(mockedGetLeadBatch).toHaveBeenCalledTimes(1);
  }, 10000);

  it("shows determinate progress and keeps polling while pipeline_progress is active", async () => {
    mockedGetLeadBatch.mockResolvedValue(
      createBatch({
        stage: "silver",
        pipeline_status: "pending",
        pipeline_progress: {
          step: "normalize_rows",
          label: "Normalizando campos (CPF, datas, telefone, local…)",
          pct: 40,
          updated_at: "2026-04-14T12:34:56.789Z",
        },
        pipeline_report: null,
      }),
    );

    renderPipelineStatusPage();

    expect(
      await screen.findByText("Normalizando campos (CPF, datas, telefone, local…)")
    ).toBeInTheDocument();
    expect(screen.getByText("40%")).toBeInTheDocument();

    const progressbar = screen.getByRole("progressbar", {
      name: "Progresso da pipeline",
    });
    expect(progressbar).toHaveAttribute("aria-valuenow", "40");

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 1800));
    });

    expect(mockedGetLeadBatch).toHaveBeenCalledTimes(2);
  }, 10000);

  it("backs off polling after 120s when step and pct stay unchanged", async () => {
    vi.useFakeTimers();
    mockedGetLeadBatch.mockResolvedValue(
      createBatch({
        stage: "silver",
        pipeline_status: "pending",
        pipeline_progress: {
          step: "normalize_rows",
          label: "Normalizando campos",
          pct: 40,
          updated_at: "2026-04-14T12:34:56.789Z",
        },
        pipeline_report: null,
      }),
    );

    renderPipelineStatusPage();

    await act(async () => {
      await Promise.resolve();
    });
    expect(screen.getByText("Normalizando campos")).toBeInTheDocument();
    expect(mockedGetLeadBatch).toHaveBeenCalledTimes(1);

    await act(async () => {
      await vi.advanceTimersByTimeAsync(120_000);
    });
    const callsBeforeSlowPoll = mockedGetLeadBatch.mock.calls.length;
    expect(callsBeforeSlowPoll).toBeGreaterThan(1);

    await act(async () => {
      await vi.advanceTimersByTimeAsync(4_499);
    });
    expect(mockedGetLeadBatch).toHaveBeenCalledTimes(callsBeforeSlowPoll);

    await act(async () => {
      await vi.advanceTimersByTimeAsync(1);
    });
    expect(mockedGetLeadBatch).toHaveBeenCalledTimes(callsBeforeSlowPoll + 1);
  }, 10000);

  it("does not start overlapping polling requests when a status request is still running", async () => {
    let resolveSecondRequest: ((value: LeadBatch) => void) | undefined;
    mockedGetLeadBatch
      .mockResolvedValueOnce(
        createBatch({
          stage: "silver",
          pipeline_status: "pending",
          pipeline_progress: {
            step: "normalize_rows",
            label: "Normalizando campos",
            pct: 40,
            updated_at: "2026-04-14T12:34:56.789Z",
          },
          pipeline_report: null,
        }),
      )
      .mockImplementationOnce(
        () =>
          new Promise<LeadBatch>((resolve) => {
            resolveSecondRequest = resolve;
          }),
      );

    renderPipelineStatusPage();

    expect(await screen.findByText("Normalizando campos")).toBeInTheDocument();

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 1800));
    });
    expect(mockedGetLeadBatch).toHaveBeenCalledTimes(2);

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 1800));
    });
    expect(mockedGetLeadBatch).toHaveBeenCalledTimes(2);

    await act(async () => {
      resolveSecondRequest?.(
        createBatch({
          stage: "gold",
          pipeline_status: "pass",
          pipeline_progress: null,
        }),
      );
      await Promise.resolve();
    });
  }, 10000);

  it("keeps polling after a transient timeout while pipeline progress is active", async () => {
    mockedGetLeadBatch
      .mockResolvedValueOnce(
        createBatch({
          stage: "silver",
          pipeline_status: "pending",
          pipeline_progress: {
            step: "normalize_rows",
            label: "Normalizando campos",
            pct: 40,
            updated_at: "2026-04-14T12:34:56.789Z",
          },
          pipeline_report: null,
        }),
      )
      .mockRejectedValueOnce(
        new ApiError({
          message: "Tempo limite da requisicao excedido.",
          status: 0,
          detail: "TIMEOUT",
          code: "TIMEOUT",
          method: "GET",
          url: "/leads/batches/10",
        }),
      )
      .mockResolvedValueOnce(
        createBatch({
          stage: "gold",
          pipeline_status: "pass",
          pipeline_progress: null,
        }),
      );

    renderPipelineStatusPage();

    expect(await screen.findByText("Normalizando campos")).toBeInTheDocument();

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 1800));
    });

    expect(
      await screen.findByText(/Falha temporaria ao consultar o lote #10 \(timeout, tentativa 1\)/i),
    ).toBeInTheDocument();

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 1800));
    });

    expect(await screen.findByText("3 leads promovidos para Gold")).toBeInTheDocument();
    expect(mockedGetLeadBatch).toHaveBeenCalledTimes(3);
  }, 10000);

  it("escalates the notice after three consecutive transient polling failures", async () => {
    mockedGetLeadBatch
      .mockResolvedValueOnce(
        createBatch({
          stage: "silver",
          pipeline_status: "pending",
          pipeline_progress: {
            step: "insert_leads",
            label: "Inserindo leads Gold no banco (20/100)",
            pct: 20,
            updated_at: "2026-04-14T12:34:56.789Z",
          },
          pipeline_report: null,
        }),
      )
      .mockRejectedValueOnce(
        new ApiError({
          message: "Tempo limite da requisicao excedido.",
          status: 0,
          detail: "TIMEOUT",
          code: "TIMEOUT",
          method: "GET",
          url: "/leads/batches/10",
        }),
      )
      .mockRejectedValueOnce(
        new ApiError({
          message: "Falha de rede ao comunicar com a API.",
          status: 0,
          detail: "NETWORK_ERROR",
          code: "NETWORK_ERROR",
          method: "GET",
          url: "/leads/batches/10",
        }),
      )
      .mockRejectedValueOnce(
        new ApiError({
          message: "Tempo limite da requisicao excedido.",
          status: 0,
          detail: "TIMEOUT",
          code: "TIMEOUT",
          method: "GET",
          url: "/leads/batches/10",
        }),
      );

    renderPipelineStatusPage();

    expect(await screen.findByText(/Inserindo leads Gold no banco \(20\/100\)/)).toBeInTheDocument();

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 1800));
    });
    expect(await screen.findByText(/tentativa 1/i)).toBeInTheDocument();

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 1800));
    });
    expect(await screen.findByText(/tentativa 2/i)).toBeInTheDocument();

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 1800));
    });

    expect(await screen.findByText(/3 tentativas consecutivas/i)).toBeInTheDocument();
    expect(screen.getByText(/Ultima atualizacao do backend: 2026-04-14T12:34:56.789Z/i)).toBeInTheDocument();
    expect(mockedGetLeadBatch).toHaveBeenCalledTimes(4);
  }, 10000);

  it("shows an explicit stall warning when pipeline progress stops updating for too long", async () => {
    vi.useFakeTimers();

    mockedGetLeadBatch.mockResolvedValue(
      createBatch({
        stage: "silver",
        pipeline_status: "pending",
        pipeline_progress: {
          step: "insert_leads",
          label: "Inserindo leads Gold no banco (20/100)",
          pct: 20,
          updated_at: "2026-04-14T12:34:56.789Z",
        },
        pipeline_report: null,
      }),
    );

    renderPipelineStatusPage();

    await act(async () => {
      await Promise.resolve();
    });
    expect(screen.getByText(/Inserindo leads Gold no banco \(20\/100\)/)).toBeInTheDocument();

    await act(async () => {
      await vi.advanceTimersByTimeAsync(60_000);
    });

    expect(screen.getByText(/Processo lento ou possivelmente travado no lote #10/i)).toBeInTheDocument();
    expect(screen.getByText(/step=insert_leads/i)).toBeInTheDocument();
    expect(screen.getByText(/Ultima atualizacao do backend: 2026-04-14T12:34:56.789Z/i)).toBeInTheDocument();
  }, 10000);

  it("treats server-marked stale progress as recoverable and keeps the retry action visible", async () => {
    mockedGetLeadBatch.mockResolvedValue(
      createBatch({
        stage: "silver",
        pipeline_status: "pending",
        pipeline_progress: {
          step: "normalize_rows",
          label: "Normalizando campos (CPF, datas, telefone, local…)",
          pct: 40,
          updated_at: "2026-04-14T12:34:56.789Z",
        },
        pipeline_report: null,
        gold_pipeline_progress_is_stale: true,
        gold_pipeline_stale_after_seconds: 420,
      }),
    );

    renderPipelineStatusPage();

    expect(await screen.findByText(/Provavel execucao orfa apos reinicio ou deploy/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Retomar Pipeline" })).toBeInTheDocument();
    expect(screen.queryByText(/Atualizando automaticamente/i)).not.toBeInTheDocument();

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 1_800));
    });

    expect(mockedGetLeadBatch).toHaveBeenCalledTimes(1);
  }, 10000);

  it("shows indeterminate progress when pct is null", async () => {
    mockedGetLeadBatch.mockResolvedValue(
      createBatch({
        stage: "silver",
        pipeline_status: "pending",
        pipeline_progress: {
          step: "source_adapt",
          label: "Lendo e adaptando arquivos de origem",
          pct: null,
          updated_at: "2026-04-14T12:34:56.789Z",
        },
        pipeline_report: null,
      }),
    );

    renderPipelineStatusPage();

    expect(await screen.findByText("Lendo e adaptando arquivos de origem")).toBeInTheDocument();
    const progressbar = screen.getByRole("progressbar", {
      name: "Progresso da pipeline",
    });
    expect(progressbar).not.toHaveAttribute("aria-valuenow");
  });

  it("lists source row numbers in quality metrics when invalid_records are present", async () => {
    const reportWithRows: PipelineReport = {
      ...basePipelineReport,
      quality_metrics: {
        ...basePipelineReport.quality_metrics,
        cpf_invalid_discarded: 2,
      },
      invalid_records: [
        {
          source_file: "leads.xlsx",
          source_sheet: "Participantes",
          source_row: 3,
          motivo_rejeicao: "CPF_INVALIDO",
        },
        {
          source_file: "leads.xlsx",
          source_sheet: "Participantes",
          source_row: 10,
          motivo_rejeicao: "CPF_INVALIDO",
        },
      ],
    };
    mockedGetLeadBatch.mockResolvedValue(
      createBatch({ pipeline_report: reportWithRows }),
    );

    renderPipelineStatusPage();

    const summaryLabel = await screen.findByText(/Linhas no ficheiro original/i);
    const summary = summaryLabel.parentElement;
    expect(summary).not.toBeNull();
    expect(summary).toHaveTextContent("leads.xlsx");
    expect(summary).toHaveTextContent("Participantes");
    expect(summary).toHaveTextContent("3");
    expect(summary).toHaveTextContent("10");
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

  it("shows an internal-error alert when the batch failed without pipeline_report", async () => {
    mockedGetLeadBatch.mockResolvedValue(
      createBatch({
        stage: "silver",
        pipeline_status: "fail",
        pipeline_report: null,
      }),
    );

    renderPipelineStatusPage();

    expect(await screen.findByText("Reprovado")).toBeInTheDocument();
    expect(
      screen.getByText(/falhou antes de gerar o relatorio desta execucao/i),
    ).toBeInTheDocument();
  });

  it("hides event-date invalid metric when batch is anchored on evento_id", async () => {
    const reportWithEventDateInvalid: PipelineReport = {
      ...basePipelineReport,
      quality_metrics: {
        ...basePipelineReport.quality_metrics,
        data_evento_invalid: 2,
      },
      invalid_records: [
        {
          source_file: "leads.xlsx",
          source_sheet: "Planilha",
          source_row: 3,
          motivo_rejeicao: "DATA_EVENTO_INVALIDA",
        },
      ],
    };
    mockedGetLeadBatch.mockResolvedValue(
      createBatch({
        evento_id: 42,
        pipeline_report: reportWithEventDateInvalid,
      }),
    );

    renderPipelineStatusPage();

    expect(await screen.findByText(/Pipeline Gold/)).toBeInTheDocument();
    expect(screen.queryByText(/Datas de evento/i)).not.toBeInTheDocument();
  });

  it("relabels lead locality metrics and hides city-out-of-mapping when batch is anchored on evento_id", async () => {
    const reportWithAnchoredLocality: PipelineReport = {
      ...basePipelineReport,
      quality_metrics: {
        ...basePipelineReport.quality_metrics,
        cidade_fora_mapeamento: 2,
        localidade_invalida: 1,
        localidade_nao_resolvida: 1,
        localidade_fora_brasil: 1,
        localidade_cidade_uf_inconsistente: 1,
      },
      localidade_controle: [
        {
          source_file: "silver_input.csv",
          source_sheet: "",
          source_row: 2,
          issue: "cidade_uf_mismatch",
          raw_cidade: "Sao Paulo",
          raw_estado: "RJ",
          raw_local: "",
        },
      ],
      cidade_fora_mapeamento_controle: [
        {
          source_file: "silver_input.csv",
          source_sheet: "",
          source_row: 2,
        },
      ],
    };
    mockedGetLeadBatch.mockResolvedValue(
      createBatch({
        evento_id: 42,
        pipeline_report: reportWithAnchoredLocality,
      }),
    );

    renderPipelineStatusPage();

    expect(await screen.findByText(/Pipeline Gold/)).toBeInTheDocument();
    expect(screen.queryByText("Cidade fora do mapeamento")).not.toBeInTheDocument();
    expect(screen.queryByText("Localidades inválidas")).not.toBeInTheDocument();
    expect(screen.queryByText("Localidades não resolvidas")).not.toBeInTheDocument();
    expect(screen.queryByText("Localidades fora do Brasil")).not.toBeInTheDocument();
    expect(screen.queryByText("Cidade/UF inconsistentes")).not.toBeInTheDocument();
    expect(screen.getByText("Cidade/UF do lead inválidos")).toBeInTheDocument();
    expect(screen.getByText("Cidade/UF do lead não resolvidos")).toBeInTheDocument();
    expect(screen.getByText("Cidade/UF do lead fora do Brasil")).toBeInTheDocument();
    expect(screen.getByText("Cidade/UF do lead inconsistentes")).toBeInTheDocument();
  });

  it("keeps event-date invalid metric visible for legacy batches without evento_id", async () => {
    const reportWithEventDateInvalid: PipelineReport = {
      ...basePipelineReport,
      quality_metrics: {
        ...basePipelineReport.quality_metrics,
        data_evento_invalid: 2,
      },
      invalid_records: [
        {
          source_file: "leads.xlsx",
          source_sheet: "Planilha",
          source_row: 3,
          motivo_rejeicao: "DATA_EVENTO_INVALIDA",
        },
      ],
    };
    mockedGetLeadBatch.mockResolvedValue(
      createBatch({
        evento_id: null,
        pipeline_report: reportWithEventDateInvalid,
      }),
    );

    renderPipelineStatusPage();

    expect(await screen.findByText(/Pipeline Gold/)).toBeInTheDocument();
    expect(screen.getByText(/Datas de evento/i)).toBeInTheDocument();
  });

  it("keeps generic locality labels visible for legacy batches without evento_id", async () => {
    const reportWithGenericLocality: PipelineReport = {
      ...basePipelineReport,
      quality_metrics: {
        ...basePipelineReport.quality_metrics,
        cidade_fora_mapeamento: 1,
        localidade_invalida: 1,
        localidade_nao_resolvida: 1,
        localidade_fora_brasil: 1,
        localidade_cidade_uf_inconsistente: 1,
      },
    };
    mockedGetLeadBatch.mockResolvedValue(
      createBatch({
        evento_id: null,
        pipeline_report: reportWithGenericLocality,
      }),
    );

    renderPipelineStatusPage();

    expect(await screen.findByText(/Pipeline Gold/)).toBeInTheDocument();
    expect(screen.getByText("Cidade fora do mapeamento")).toBeInTheDocument();
    expect(screen.getByText("Localidades inválidas")).toBeInTheDocument();
    expect(screen.getByText("Localidades não resolvidas")).toBeInTheDocument();
    expect(screen.getByText("Localidades fora do Brasil")).toBeInTheDocument();
    expect(screen.getByText("Cidade/UF inconsistentes")).toBeInTheDocument();
  });
});
