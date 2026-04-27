import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";

import MapeamentoPage from "../leads/MapeamentoPage";
import { listAgencias } from "../../services/agencias";
import { createEvento } from "../../services/eventos/core";
import { ApiError } from "../../services/http";
import { reconcileLeadMappingTimeout } from "../../services/leads_mapping_recovery";
import { useAuth } from "../../store/auth";
import {
  getLeadBatchColunas,
  type LeadBatch,
  listReferenciaEventos,
  mapearLeadBatch,
} from "../../services/leads_import";

vi.mock("../../store/auth", () => ({ useAuth: vi.fn() }));
vi.mock("../../services/agencias", () => ({ listAgencias: vi.fn() }));
vi.mock("../../services/leads_import", () => ({
  getLeadBatchColunas: vi.fn(),
  listReferenciaEventos: vi.fn(),
  mapearLeadBatch: vi.fn(),
}));
vi.mock("../../services/leads_mapping_recovery", () => ({
  reconcileLeadMappingTimeout: vi.fn(),
}));
vi.mock("../../services/eventos/core", () => ({
  createEvento: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);
const mockedListAgencias = vi.mocked(listAgencias);
const mockedGetLeadBatchColunas = vi.mocked(getLeadBatchColunas);
const mockedListReferenciaEventos = vi.mocked(listReferenciaEventos);
const mockedMapearLeadBatch = vi.mocked(mapearLeadBatch);
const mockedCreateEvento = vi.mocked(createEvento);
const mockedReconcileLeadMappingTimeout = vi.mocked(reconcileLeadMappingTimeout);
const EVENTOS_LOAD_ERROR = "Nao foi possivel carregar os eventos. Tente recarregar a pagina.";

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

function renderMapeamentoPage(element = <MapeamentoPage />) {
  return render(
    <MemoryRouter initialEntries={["/leads/mapeamento?batch_id=10"]}>
      <Routes>
        <Route path="/leads/mapeamento" element={element} />
        <Route path="/leads/pipeline" element={<PipelineProbe />} />
      </Routes>
    </MemoryRouter>,
  );
}

async function selectEventoAndConfirm() {
  const user = userEvent.setup();

  await user.click(await screen.findByPlaceholderText("Selecione ou pesquise o evento..."));
  await user.click(await screen.findByRole("option", { name: /Evento Teste/i }));
  await user.click(screen.getByRole("button", { name: "Confirmar Mapeamento" }));
}

describe("MapeamentoPage", { timeout: 30000 }, () => {
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
    mockedListAgencias.mockResolvedValue([
      { id: 10, nome: "Agencia Alpha", dominio: "alpha.com.br" },
    ]);
    mockedGetLeadBatchColunas.mockResolvedValue({
      batch_id: 10,
      colunas: [
        {
          coluna_original: "Nome",
          campo_sugerido: "nome",
          confianca: "exact_match",
        },
      ],
    });
    mockedListReferenciaEventos.mockResolvedValue([
      { id: 42, nome: "Evento Teste", data_inicio_prevista: "2099-01-01" },
    ]);
    mockedReconcileLeadMappingTimeout.mockReset();
  });

  it("renders with minimal route and auth context", async () => {
    renderMapeamentoPage();

    expect(screen.getByText("Mapeamento de Colunas")).toBeInTheDocument();
    expect(await screen.findByText("Nome")).toBeInTheDocument();
    expect(mockedGetLeadBatchColunas).toHaveBeenCalledWith("token-123", 10);
    expect(mockedListReferenciaEventos).toHaveBeenCalledWith("token-123");
  });

  it("shows the reference event dropdown after events load successfully", async () => {
    renderMapeamentoPage();

    const user = userEvent.setup();
    await user.click(await screen.findByPlaceholderText("Selecione ou pesquise o evento..."));

    expect(await screen.findByRole("option", { name: /Evento Teste/i })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: /\+ Criar evento rapidamente/i })).toBeInTheDocument();
  });

  it("creates an ad-hoc event from the mapping flow and uses it on confirmation", async () => {
    mockedCreateEvento.mockResolvedValue({
      id: 77,
      nome: "Evento Ad Hoc",
      cidade: "Sao Paulo",
      estado: "SP",
      concorrencia: false,
      data_inicio_prevista: "2099-02-01",
      data_fim_prevista: "2099-02-03",
      data_inicio_realizada: null,
      data_fim_realizada: null,
      descricao: null,
      investimento: null,
      publico_projetado: null,
      publico_realizado: null,
      agencia_id: 10,
      diretoria_id: null,
      gestor_id: null,
      tipo_id: null,
      subtipo_id: null,
      tag_ids: [],
      territorio_ids: [],
      status_id: 1,
      created_at: "2026-04-16T10:00:00",
      updated_at: "2026-04-16T10:00:00",
    });
    mockedMapearLeadBatch.mockResolvedValue({
      batch_id: 10,
      silver_count: 1,
      stage: "silver",
    });

    renderMapeamentoPage();

    const user = userEvent.setup();
    await user.click(await screen.findByPlaceholderText("Selecione ou pesquise o evento..."));
    await user.click(await screen.findByRole("option", { name: /\+ Criar evento rapidamente/i }));

    const dialog = await screen.findByRole("dialog");
    await user.type(within(dialog).getByLabelText(/nome do evento/i), "Evento Ad Hoc");
    fireEvent.change(within(dialog).getByLabelText(/data de inicio/i), {
      target: { value: "2099-02-01" },
    });
    fireEvent.change(within(dialog).getByLabelText(/data de fim/i), {
      target: { value: "2099-02-03" },
    });
    await user.type(within(dialog).getByLabelText(/cidade/i), "Sao Paulo");
    await user.click(within(dialog).getByRole("combobox", { name: /estado/i }));
    await user.click(await screen.findByRole("option", { name: "SP" }));
    await user.click(within(dialog).getByRole("combobox", { name: /agencia responsavel/i }));
    await user.click(await screen.findByRole("option", { name: "Agencia Alpha" }));
    await user.click(within(dialog).getByRole("button", { name: "Salvar" }));

    await waitFor(() => {
      expect(mockedCreateEvento).toHaveBeenCalledWith("token-123", {
        nome: "Evento Ad Hoc",
        data_inicio_prevista: "2099-02-01",
        data_fim_prevista: "2099-02-03",
        cidade: "Sao Paulo",
        estado: "SP",
        agencia_id: 10,
        concorrencia: false,
        criar_ativacao_padrao_bb: true,
      });
    });
    await waitFor(() => {
      expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: "Confirmar Mapeamento" }));

    await waitFor(() => {
      expect(mockedMapearLeadBatch).toHaveBeenCalledWith("token-123", 10, {
        evento_id: 77,
        mapeamento: { Nome: "nome" },
      });
    });
  });

  it("lists extended lead fields in the canonical mapping dropdown", async () => {
    renderMapeamentoPage();

    const user = userEvent.setup();
    await screen.findByText("Nome");

    const comboboxes = screen.getAllByRole("combobox");
    await user.click(comboboxes[comboboxes.length - 1]);

    expect(await screen.findByRole("option", { name: "sobrenome" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "genero" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "is_cliente_bb" })).toBeInTheDocument();
  });

  it("keeps event-owned fields available in the canonical mapping dropdown without fixed event", async () => {
    mockedGetLeadBatchColunas.mockResolvedValue({
      batch_id: 10,
      colunas: [
        {
          coluna_original: "Nome",
          campo_sugerido: "nome",
          confianca: "exact_match",
        },
      ],
    });

    renderMapeamentoPage();

    const user = userEvent.setup();
    await screen.findByText("Nome");

    const comboboxes = screen.getAllByRole("combobox");
    await user.click(comboboxes[comboboxes.length - 1]);

    expect(await screen.findByRole("option", { name: "evento" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "tipo_evento" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "local" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "data_evento" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "cidade" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "estado" })).toBeInTheDocument();
  });

  it("shows an error alert when reference events fail to load", async () => {
    mockedListReferenciaEventos.mockRejectedValue(new Error("network error"));

    renderMapeamentoPage();

    expect(await screen.findByRole("alert")).toHaveTextContent(EVENTOS_LOAD_ERROR);
    expect(mockedListReferenciaEventos).toHaveBeenCalledWith("token-123");
  });

  it("navigates to the pipeline route with the confirmation response batch id", async () => {
    mockedMapearLeadBatch.mockResolvedValue({
      batch_id: 10,
      silver_count: 1,
      stage: "silver",
    });

    renderMapeamentoPage();
    await selectEventoAndConfirm();

    await waitFor(() => {
      expect(mockedMapearLeadBatch).toHaveBeenCalledWith("token-123", 10, {
        evento_id: 42,
        mapeamento: { Nome: "nome" },
      });
    });
    expect(await screen.findByText("Pipeline route ?batch_id=10")).toBeInTheDocument();
  });

  it("confirms with fixed event and skips loading reference events", async () => {
    mockedMapearLeadBatch.mockResolvedValue({
      batch_id: 10,
      silver_count: 1,
      stage: "silver",
    });

    renderMapeamentoPage(<MapeamentoPage batchId={10} fixedEventoId={42} />);

    expect(await screen.findByText("Nome")).toBeInTheDocument();
    expect(screen.queryByPlaceholderText("Selecione ou pesquise o evento...")).not.toBeInTheDocument();
    expect(mockedListReferenciaEventos).not.toHaveBeenCalled();

    await userEvent.setup().click(screen.getByRole("button", { name: "Confirmar Mapeamento" }));

    await waitFor(() => {
      expect(mockedMapearLeadBatch).toHaveBeenCalledWith("token-123", 10, {
        evento_id: 42,
        mapeamento: { Nome: "nome" },
      });
    });
  });

  it("confirms enrichment-only mapping without loading reference events", async () => {
    mockedMapearLeadBatch.mockResolvedValue({
      batch_id: 10,
      silver_count: 1,
      stage: "silver",
    });

    renderMapeamentoPage(<MapeamentoPage batchId={10} enrichmentOnly />);

    expect(await screen.findByText("Nome")).toBeInTheDocument();
    expect(screen.queryByPlaceholderText("Selecione ou pesquise o evento...")).not.toBeInTheDocument();
    expect(
      screen.getByText(/Este lote foi enviado para enriquecimento sem evento/i),
    ).toBeInTheDocument();
    expect(mockedListReferenciaEventos).not.toHaveBeenCalled();

    await userEvent.setup().click(screen.getByRole("button", { name: "Confirmar Mapeamento" }));

    await waitFor(() => {
      expect(mockedMapearLeadBatch).toHaveBeenCalledWith("token-123", 10, {
        evento_id: null,
        mapeamento: { Nome: "nome" },
      });
    });
  });

  it("recovers automatically after timeout when the backend already promoted the batch to silver", async () => {
    mockedMapearLeadBatch.mockRejectedValue(
      new ApiError({
        message: "Tempo limite da requisicao excedido.",
        status: 0,
        detail: "TIMEOUT",
        code: "TIMEOUT",
        method: "POST",
        url: "/leads/batches/10/mapear",
      }),
    );
    mockedReconcileLeadMappingTimeout.mockResolvedValue({
      status: "mapped",
      batches: [createBatchStatus(10, "silver")],
    });

    renderMapeamentoPage();
    await selectEventoAndConfirm();

    await waitFor(() => {
      expect(mockedReconcileLeadMappingTimeout).toHaveBeenCalledWith("token-123", [10]);
    });
    expect(await screen.findByText("Pipeline route ?batch_id=10")).toBeInTheDocument();
  });

  it("hides event-owned fields and sanitizes derived suggestions when batch has fixed event", async () => {
    mockedGetLeadBatchColunas.mockResolvedValue({
      batch_id: 10,
      colunas: [
        {
          coluna_original: "Nome",
          campo_sugerido: "nome",
          confianca: "exact_match",
        },
        {
          coluna_original: "Evento",
          campo_sugerido: "evento",
          confianca: "exact_match",
        },
        {
          coluna_original: "Tipo",
          campo_sugerido: "tipo_evento",
          confianca: "exact_match",
        },
        {
          coluna_original: "Data",
          campo_sugerido: "data_evento",
          confianca: "exact_match",
        },
        {
          coluna_original: "Local",
          campo_sugerido: "local",
          confianca: "exact_match",
        },
      ],
    });
    mockedMapearLeadBatch.mockResolvedValue({
      batch_id: 10,
      silver_count: 1,
      stage: "silver",
    });

    renderMapeamentoPage(<MapeamentoPage batchId={10} fixedEventoId={42} />);

    expect(await screen.findByText("Nome")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Com evento fixo, evento, tipo_evento, local e data_evento serao derivados automaticamente do cadastro do evento selecionado. Nao e necessario mapea-los no arquivo.",
      ),
    ).toBeInTheDocument();
    expect(screen.queryByPlaceholderText("Selecione ou pesquise o evento...")).not.toBeInTheDocument();
    expect(mockedListReferenciaEventos).not.toHaveBeenCalled();

    const eventoRow = screen.getByText("Evento").closest("tr");
    expect(eventoRow).not.toBeNull();
    expect(within(eventoRow as HTMLElement).getByText(/Derivado do evento/)).toBeInTheDocument();

    const user = userEvent.setup();

    const nomeRow = screen.getByText("Nome").closest("tr");
    expect(nomeRow).not.toBeNull();
    await user.click(within(nomeRow as HTMLElement).getByRole("combobox"));

    await waitFor(() => {
      expect(screen.queryByRole("option", { name: "evento" })).not.toBeInTheDocument();
      expect(screen.queryByRole("option", { name: "tipo_evento" })).not.toBeInTheDocument();
      expect(screen.queryByRole("option", { name: "local" })).not.toBeInTheDocument();
      expect(screen.queryByRole("option", { name: "data_evento" })).not.toBeInTheDocument();
      expect(screen.getByRole("option", { name: "cidade" })).toBeInTheDocument();
      expect(screen.getByRole("option", { name: "estado" })).toBeInTheDocument();
    });

    await user.keyboard("{Escape}");
    await user.click(screen.getByRole("button", { name: "Confirmar Mapeamento" }));

    await waitFor(() => {
      expect(mockedMapearLeadBatch).toHaveBeenCalledWith("token-123", 10, {
        evento_id: 42,
        mapeamento: { Nome: "nome" },
      });
    });
  });

  it("shows an explicit error instead of navigating when confirmation omits batch id", async () => {
    mockedMapearLeadBatch.mockResolvedValue({
      silver_count: 1,
      stage: "silver",
    } as Awaited<ReturnType<typeof mapearLeadBatch>>);

    renderMapeamentoPage();
    await selectEventoAndConfirm();

    expect(
      await screen.findByText(/Resposta de confirmacao nao retornou batch_id\./),
    ).toBeInTheDocument();
    expect(screen.queryByText(/Pipeline route \?batch_id=/)).not.toBeInTheDocument();
  });
});
