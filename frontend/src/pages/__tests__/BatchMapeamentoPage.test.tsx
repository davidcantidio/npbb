import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";

import BatchMapeamentoPage from "../leads/BatchMapeamentoPage";
import { ApiError } from "../../services/http";
import type { LeadBatch } from "../../services/leads_import";
import { reconcileLeadMappingTimeout } from "../../services/leads_mapping_recovery";
import { useAuth } from "../../store/auth";
import { getLeadBatchColunasBatch, mapearLeadBatches } from "../../services/leads_import";

vi.mock("../../store/auth", () => ({ useAuth: vi.fn() }));
vi.mock("../../services/leads_import", () => ({
  getLeadBatchColunasBatch: vi.fn(),
  mapearLeadBatches: vi.fn(),
}));
vi.mock("../../services/leads_mapping_recovery", () => ({
  reconcileLeadMappingTimeout: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);
const mockedGetLeadBatchColunasBatch = vi.mocked(getLeadBatchColunasBatch);
const mockedMapearLeadBatches = vi.mocked(mapearLeadBatches);
const mockedReconcileLeadMappingTimeout = vi.mocked(reconcileLeadMappingTimeout);

function createBatchStatus(batchId: number, stage: LeadBatch["stage"]): LeadBatch {
  return {
    id: batchId,
    enviado_por: 1,
    plataforma_origem: "email",
    data_envio: "2026-04-19T10:00:00Z",
    data_upload: "2026-04-19T10:00:00Z",
    nome_arquivo_original: `batch-${batchId}.csv`,
    stage,
    evento_id: 42,
    origem_lote: "proponente",
    enrichment_only: false,
    tipo_lead_proponente: "entrada_evento",
    ativacao_id: null,
    pipeline_status: "pending",
    pipeline_progress: null,
    pipeline_report: null,
    created_at: "2026-04-19T10:00:00Z",
    gold_pipeline_stale_after_seconds: null,
    gold_pipeline_progress_is_stale: null,
  };
}

function PipelineProbe() {
  const location = useLocation();
  return <div>{`Pipeline route ${location.search}`}</div>;
}

function LocationProbe() {
  const location = useLocation();
  return <div>{`Location route ${location.pathname}${location.search}`}</div>;
}

function renderBatchMapeamentoPage(element = <BatchMapeamentoPage batchIds={[70, 71]} primaryBatchId={70} />) {
  return render(
    <MemoryRouter initialEntries={["/leads/importar?step=mapping&batch_id=70&context=batch"]}>
      <Routes>
        <Route
          path="/leads/importar"
          element={
            <>
              {element}
              <LocationProbe />
            </>
          }
        />
        <Route path="/leads/pipeline" element={<PipelineProbe />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("BatchMapeamentoPage", () => {
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
    mockedGetLeadBatchColunasBatch.mockResolvedValue({
      batch_ids: [70, 71],
      primary_batch_id: 70,
      aggregation_rule:
        "trim + lowercase + remover acentos + colapsar espacos internos; preserva pontuacao e separadores como _ e -",
      warnings: ["O batch reune arquivos de eventos diferentes."],
      blockers: [],
      blocked_batch_ids: [],
      colunas: [
        {
          chave_agregada: "cpf",
          nome_exibicao: "CPF",
          variantes: ["CPF", "cpf"],
          aparece_em_arquivos: 2,
          campo_sugerido: "cpf",
          confianca: "exact_match",
          warnings: [],
          ocorrencias: [
            {
              batch_id: 70,
              file_name: "batch-a.csv",
              coluna_original: "CPF",
              amostras: ["12345678901"],
              campo_sugerido: "cpf",
              confianca: "exact_match",
              evento_id: 42,
              plataforma_origem: "email",
            },
            {
              batch_id: 71,
              file_name: "batch-b.csv",
              coluna_original: "cpf",
              amostras: ["98765432100"],
              campo_sugerido: "cpf",
              confianca: "exact_match",
              evento_id: 43,
              plataforma_origem: "manual",
            },
          ],
        },
        {
          chave_agregada: "data",
          nome_exibicao: "Data",
          variantes: ["Data"],
          aparece_em_arquivos: 1,
          campo_sugerido: null,
          confianca: "none",
          warnings: ["Sugestoes automaticas divergentes entre os arquivos."],
          ocorrencias: [
            {
              batch_id: 70,
              file_name: "batch-a.csv",
              coluna_original: "Data",
              amostras: ["01/02/1990"],
              campo_sugerido: null,
              confianca: "none",
              evento_id: 42,
              plataforma_origem: "email",
            },
          ],
        },
      ],
    });
    mockedReconcileLeadMappingTimeout.mockReset();
  });

  it("renders aggregated coverage, variants and warnings", async () => {
    renderBatchMapeamentoPage();

    expect(await screen.findByText("Mapeamento Unificado do Batch")).toBeInTheDocument();
    expect(mockedGetLeadBatchColunasBatch).toHaveBeenCalledWith("token-123", [70, 71]);
    expect(screen.getByText(/Regra de agregacao de colunas:/i)).toBeInTheDocument();
    expect(screen.getByText("O batch reune arquivos de eventos diferentes.")).toBeInTheDocument();
    expect(screen.getByText("Presente em 2 arquivo(s).")).toBeInTheDocument();
    expect(screen.getByText("Variantes: CPF, cpf")).toBeInTheDocument();
    expect(screen.getAllByText("batch-a.csv").length).toBeGreaterThan(0);
    expect(screen.getAllByText("batch-b.csv").length).toBeGreaterThan(0);
    expect(screen.getByText("Sugestoes automaticas divergentes entre os arquivos.")).toBeInTheDocument();
  });

  it("confirms the aggregated mapping once and exposes the result to the parent", async () => {
    mockedMapearLeadBatches.mockResolvedValue({
      batch_ids: [70, 71],
      primary_batch_id: 70,
      total_silver_count: 4,
      results: [
        { batch_id: 70, silver_count: 2, stage: "silver" },
        { batch_id: 71, silver_count: 2, stage: "silver" },
      ],
      stage: "silver",
    });
    const onMapped = vi.fn();

    renderBatchMapeamentoPage(
      <BatchMapeamentoPage batchIds={[70, 71]} primaryBatchId={70} onMapped={onMapped} />,
    );

    const user = userEvent.setup();
    await screen.findByText("CPF");

    await user.click(screen.getByRole("button", { name: "Concluir mapeamento do batch" }));

    await waitFor(() => {
      expect(mockedMapearLeadBatches).toHaveBeenCalledWith("token-123", {
        batch_ids: [70, 71],
        mapeamento: {
          cpf: "cpf",
        },
      });
    });
    expect(onMapped).toHaveBeenCalledWith(
      expect.objectContaining({
        primary_batch_id: 70,
        batch_ids: [70, 71],
      }),
    );
  });

  it("blocks confirmation when the backend reports blockers", async () => {
    mockedGetLeadBatchColunasBatch.mockResolvedValue({
      batch_ids: [70],
      primary_batch_id: 70,
      aggregation_rule: "regra",
      warnings: [],
      blockers: ["Lote #70 nao possui evento de referencia salvo."],
      blocked_batch_ids: [70],
      colunas: [],
    });

    renderBatchMapeamentoPage(<BatchMapeamentoPage batchIds={[70]} primaryBatchId={70} />);
    const user = userEvent.setup();

    expect(await screen.findByText("Lote #70 nao possui evento de referencia salvo.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Concluir mapeamento do batch" })).toBeDisabled();
    await user.click(screen.getByRole("button", { name: "Abrir lote #70 por arquivo" }));
    expect(
      await screen.findByText("Location route /leads/importar?step=mapping&batch_id=70&context=batch&mapping_mode=single"),
    ).toBeInTheDocument();
    expect(mockedMapearLeadBatches).not.toHaveBeenCalled();
  });

  it("recovers automatically after timeout when all batches reach silver or gold", async () => {
    mockedMapearLeadBatches.mockRejectedValue(
      new ApiError({
        message: "Tempo limite da requisicao excedido.",
        status: 0,
        detail: "TIMEOUT",
        code: "TIMEOUT",
        method: "POST",
        url: "/leads/batches/mapear",
      }),
    );
    mockedReconcileLeadMappingTimeout.mockResolvedValue({
      status: "mapped",
      batches: [createBatchStatus(70, "silver"), createBatchStatus(71, "gold")],
    });

    const onMapped = vi.fn();
    renderBatchMapeamentoPage(
      <BatchMapeamentoPage batchIds={[70, 71]} primaryBatchId={70} onMapped={onMapped} />,
    );

    const user = userEvent.setup();
    await screen.findByText("CPF");

    await user.click(screen.getByRole("button", { name: "Concluir mapeamento do batch" }));

    await waitFor(() => {
      expect(mockedReconcileLeadMappingTimeout).toHaveBeenCalledWith("token-123", [70, 71]);
    });
    await waitFor(() => {
      expect(onMapped).toHaveBeenCalledWith(
        expect.objectContaining({
          primary_batch_id: 70,
          batch_ids: [70, 71],
        }),
      );
    });
  });

  it("keeps the page on mapping when timeout recovery expires and batches stay bronze", async () => {
    mockedMapearLeadBatches.mockRejectedValue(
      new ApiError({
        message: "Tempo limite da requisicao excedido.",
        status: 0,
        detail: "TIMEOUT",
        code: "TIMEOUT",
        method: "POST",
        url: "/leads/batches/mapear",
      }),
    );
    mockedReconcileLeadMappingTimeout.mockResolvedValue({
      status: "pending",
      batches: [createBatchStatus(70, "bronze"), createBatchStatus(71, "bronze")],
    });

    const onMapped = vi.fn();
    renderBatchMapeamentoPage(
      <BatchMapeamentoPage batchIds={[70, 71]} primaryBatchId={70} onMapped={onMapped} />,
    );

    const user = userEvent.setup();
    await screen.findByText("CPF");
    await user.click(screen.getByRole("button", { name: "Concluir mapeamento do batch" }));

    expect(await screen.findByText(/backend ainda nao confirmou todos os lotes como mapeados/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Reverificar status do batch/i })).toBeInTheDocument();
    expect(onMapped).not.toHaveBeenCalled();
    expect(screen.queryByText(/Pipeline route/i)).not.toBeInTheDocument();
  });
});
