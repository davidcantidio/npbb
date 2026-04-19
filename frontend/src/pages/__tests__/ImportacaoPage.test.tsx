import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes, useLocation, useNavigate } from "react-router-dom";

import { ApiError } from "../../services/http";
import {
  computeFileSha256Hex,
  commitLeadImportEtl,
  createLeadBatch,
  getLeadBatch,
  getLeadBatchPreview,
  getLeadImportMetadataHint,
  listReferenciaEventos,
  previewLeadImportEtl,
} from "../../services/leads_import";
import { listAgencias } from "../../services/agencias";
import { createEvento, updateEvento } from "../../services/eventos/core";
import { createEventoAtivacao, listEventoAtivacoes } from "../../services/eventos/workflow";
import { useAuth } from "../../store/auth";
import { getLocalDateInputValue } from "../../utils/date";
import ImportacaoPage from "../leads/ImportacaoPage";

vi.mock("../leads/MapeamentoPage", () => ({
  default: ({
    batchId,
    fixedEventoId,
    onCancel,
    onMapped,
    cancelLabel,
  }: {
    batchId?: number;
    fixedEventoId?: number | null;
    onCancel?: () => void;
    onMapped?: (result: { batch_id: number; silver_count: number; stage: string }) => void;
    cancelLabel?: string;
  }) => (
    <div>
      <div>{`Mapeamento shell ${batchId ?? 0}`}</div>
      <div>{fixedEventoId != null ? `Evento fixo shell ${fixedEventoId}` : "Evento editavel shell"}</div>
      <button type="button" onClick={() => onCancel?.()}>
        {cancelLabel ?? "Cancelar shell mapeamento"}
      </button>
      <button
        type="button"
        onClick={() =>
          onMapped?.({
            batch_id: batchId ?? 0,
            silver_count: 3,
            stage: "silver",
          })
        }
      >
        Concluir shell mapeamento
      </button>
    </div>
  ),
}));

vi.mock("../leads/BatchMapeamentoPage", () => ({
  default: ({
    batchIds,
    primaryBatchId,
    onCancel,
    onMapped,
    cancelLabel,
  }: {
    batchIds?: number[];
    primaryBatchId?: number | null;
    onCancel?: () => void;
    onMapped?: (result: {
      batch_ids: number[];
      primary_batch_id: number;
      total_silver_count: number;
      results: Array<{ batch_id: number; silver_count: number; stage: string }>;
      stage: string;
    }) => void;
    cancelLabel?: string;
  }) => {
    const navigate = useNavigate();
    const resolvedBatchIds = batchIds ?? [];
    const resolvedPrimaryBatchId = primaryBatchId ?? resolvedBatchIds[0] ?? 0;

    return (
      <div>
        <div>{`Mapeamento batch shell ${resolvedBatchIds.join(",")}`}</div>
        <div>{`Batch primario shell ${resolvedPrimaryBatchId}`}</div>
        <button type="button" onClick={() => onCancel?.()}>
          {cancelLabel ?? "Cancelar shell batch mapeamento"}
        </button>
        <button
          type="button"
          onClick={() =>
            navigate(
              `/leads/importar?step=mapping&batch_id=${resolvedPrimaryBatchId}&context=batch&mapping_mode=single`,
            )
          }
        >
          Fallback shell batch mapeamento
        </button>
        <button
          type="button"
          onClick={() =>
            onMapped?.({
              batch_ids: resolvedBatchIds,
              primary_batch_id: resolvedPrimaryBatchId,
              total_silver_count: resolvedBatchIds.length * 3,
              results: resolvedBatchIds.map((batchId) => ({
                batch_id: batchId,
                silver_count: 3,
                stage: "silver",
              })),
              stage: "silver",
            })
          }
        >
          Concluir shell batch mapeamento
        </button>
      </div>
    );
  },
}));

vi.mock("../leads/PipelineStatusPage", () => ({
  default: ({
    batchId,
    onNewImport,
    onBack,
    backLabel,
    onBatchLoaded,
  }: {
    batchId?: number;
    onNewImport?: () => void;
    onBack?: () => void;
    backLabel?: string;
    onBatchLoaded?: (batch: { id: number; stage: string; pipeline_status: string }) => void;
  }) => (
    <div>
      <div>{`Pipeline shell ${batchId ?? 0}`}</div>
      {onBack ? (
        <button type="button" onClick={() => onBack()}>
          {backLabel ?? "Voltar"}
        </button>
      ) : null}
      {onNewImport ? (
        <button type="button" onClick={() => onNewImport()}>
          Nova importacao shell
        </button>
      ) : null}
      {onBatchLoaded ? (
        <button
          type="button"
          onClick={() =>
            onBatchLoaded({
              id: batchId ?? 0,
              stage: "gold",
              pipeline_status: "pass",
            })
          }
        >
          Sincronizar lote shell
        </button>
      ) : null}
    </div>
  ),
}));

vi.mock("../../store/auth", () => ({ useAuth: vi.fn() }));
vi.mock("../../services/agencias", () => ({ listAgencias: vi.fn() }));
vi.mock("../../services/leads_import", () => ({
  DEFAULT_ACTIVATION_IMPORT_BLOCK_REASON:
    "Vincule uma agencia ao evento antes de importar leads de ativacao.",
  LEAD_IMPORT_ETL_MAX_SCAN_ROWS_CAP: 500,
  computeFileSha256Hex: vi.fn(),
  commitLeadImportEtl: vi.fn(),
  createLeadBatch: vi.fn(),
  getActivationImportBlockReason: (evento?: { activation_import_block_reason?: string | null }) =>
    evento?.activation_import_block_reason ?? null,
  getLeadBatch: vi.fn(),
  getLeadBatchPreview: vi.fn(),
  getLeadImportMetadataHint: vi.fn(),
  listReferenciaEventos: vi.fn(),
  normalizeLeadImportHintDateInput: (value?: string | null) => (value ? String(value).slice(0, 10) : ""),
  previewLeadImportEtl: vi.fn(),
  supportsActivationImport: (evento?: { supports_activation_import?: boolean }) =>
    evento?.supports_activation_import ?? true,
}));
vi.mock("../../services/eventos/workflow", () => ({
  listEventoAtivacoes: vi.fn(),
  createEventoAtivacao: vi.fn(),
}));
vi.mock("../../services/eventos/core", () => ({
  createEvento: vi.fn(),
  updateEvento: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);
const mockedListAgencias = vi.mocked(listAgencias);
const mockedComputeFileSha256Hex = vi.mocked(computeFileSha256Hex);
const mockedCommitLeadImportEtl = vi.mocked(commitLeadImportEtl);
const mockedCreateLeadBatch = vi.mocked(createLeadBatch);
const mockedGetLeadBatch = vi.mocked(getLeadBatch);
const mockedGetLeadBatchPreview = vi.mocked(getLeadBatchPreview);
const mockedGetLeadImportMetadataHint = vi.mocked(getLeadImportMetadataHint);
const mockedListReferenciaEventos = vi.mocked(listReferenciaEventos);
const mockedPreviewLeadImportEtl = vi.mocked(previewLeadImportEtl);
const mockedListEventoAtivacoes = vi.mocked(listEventoAtivacoes);
const mockedCreateEventoAtivacao = vi.mocked(createEventoAtivacao);
const mockedCreateEvento = vi.mocked(createEvento);
const mockedUpdateEvento = vi.mocked(updateEvento);

function LocationProbe() {
  const location = useLocation();
  return <div data-testid="location">{`${location.pathname}${location.search}`}</div>;
}

function ImportacaoHarness() {
  return (
    <>
      <ImportacaoPage />
      <LocationProbe />
    </>
  );
}

function renderImportacaoPage(initialEntry = "/leads/importar") {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route path="/leads/importar" element={<ImportacaoHarness />} />
      </Routes>
    </MemoryRouter>,
  );
}

function createCsvFile() {
  return new File(["nome,email\nAlice,alice@npbb.com.br"], "leads.csv", {
    type: "text/csv",
  });
}

function createXlsxFile() {
  return new File(["xlsx"], "leads.xlsx", {
    type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  });
}

function createDeferred<T>() {
  let resolve!: (value: T | PromiseLike<T>) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((nextResolve, nextReject) => {
    resolve = nextResolve;
    reject = nextReject;
  });
  return { promise, resolve, reject };
}

function bronzeBatchBase() {
  return {
    origem_lote: "proponente" as const,
    tipo_lead_proponente: "entrada_evento",
    ativacao_id: null as number | null,
    pipeline_progress: null as null,
  };
}

function createEventoReadBase(overrides: Record<string, unknown> = {}) {
  return {
    id: 42,
    nome: "Evento ETL",
    cidade: "Sao Paulo",
    estado: "SP",
    concorrencia: false,
    data_inicio_prevista: "2099-01-01",
    data_fim_prevista: "2099-01-03",
    data_inicio_realizada: null,
    data_fim_realizada: null,
    descricao: null,
    investimento: null,
    publico_projetado: null,
    publico_realizado: null,
    agencia_id: 7,
    diretoria_id: null,
    gestor_id: null,
    tipo_id: null,
    subtipo_id: null,
    tag_ids: [],
    territorio_ids: [],
    status_id: 1,
    created_at: "2026-04-16T10:00:00",
    updated_at: "2026-04-16T10:00:00",
    ...overrides,
  };
}

function findBatchRow(fileName: string) {
  const row = screen.getByText(fileName).closest("tr");
  expect(row).not.toBeNull();
  return row as HTMLElement;
}

async function switchToBatchMode(user: ReturnType<typeof userEvent.setup>) {
  await user.click(screen.getByRole("combobox", { name: /modo de upload bronze/i }));
  await user.click(await screen.findByRole("option", { name: "Upload batch" }));
}

async function selectBatchRowPlatform(row: HTMLElement, user: ReturnType<typeof userEvent.setup>, platform = "email") {
  await user.click(within(row).getByRole("combobox", { name: /plataforma de origem/i }));
  await user.click(await screen.findByRole("option", { name: platform }));
}

async function selectBatchRowEvent(row: HTMLElement, user: ReturnType<typeof userEvent.setup>, optionName: RegExp | string) {
  await user.click(within(row).getByRole("combobox", { name: /evento de referencia/i }));
  await user.click(await screen.findByRole("option", { name: optionName }));
}

async function selectBatchRowOrigem(row: HTMLElement, user: ReturnType<typeof userEvent.setup>, optionName: RegExp | string) {
  await user.click(within(row).getByRole("combobox", { name: /^origem$/i }));
  await user.click(await screen.findByRole("option", { name: optionName }));
}

describe("ImportacaoPage", { timeout: 30000 }, () => {
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
    mockedComputeFileSha256Hex.mockResolvedValue("a".repeat(64));
    mockedListReferenciaEventos.mockResolvedValue([
      {
        id: 42,
        nome: "Evento ETL",
        data_inicio_prevista: "2099-01-01",
        agencia_id: 7,
        supports_activation_import: true,
        activation_import_block_reason: null,
      },
    ]);
    mockedGetLeadImportMetadataHint.mockResolvedValue(null);
    mockedListEventoAtivacoes.mockResolvedValue([]);
    mockedUpdateEvento.mockResolvedValue(createEventoReadBase({ id: 42 }));
  });

  it("renders the canonical Bronze shell with the current date prefilled", async () => {
    renderImportacaoPage();

    await waitFor(() => {
      expect(mockedListReferenciaEventos).toHaveBeenCalledWith("token-123");
    });

    expect(screen.getByText("Importacao de Leads")).toBeInTheDocument();
    expect(screen.getByText("Upload")).toBeInTheDocument();
    expect(screen.getByText("Mapeamento")).toBeInTheDocument();
    expect(screen.getByText("Pipeline")).toBeInTheDocument();
    expect(screen.getByDisplayValue("demo@npbb.com.br")).toBeInTheDocument();
    expect(screen.getByDisplayValue(getLocalDateInputValue())).toBeInTheDocument();
    expect(screen.getByTestId("location")).toHaveTextContent("/leads/importar");
  });

  it("shows a validation error when required fields are missing", async () => {
    renderImportacaoPage();

    const submitButton = screen.getByRole("button", { name: "Enviar para Bronze" });
    const form = submitButton.closest("form");
    expect(form).not.toBeNull();

    fireEvent.submit(form!);

    expect(await screen.findByText("Selecione um arquivo CSV ou XLSX.")).toBeInTheDocument();
    expect(mockedCreateLeadBatch).not.toHaveBeenCalled();
  });

  it("uploads a batch and keeps the operator in the canonical shell preview", async () => {
    mockedCreateLeadBatch.mockResolvedValue({
      id: 10,
      enviado_por: 1,
      plataforma_origem: "email",
      data_envio: "2026-03-09T00:00:00",
      data_upload: "2026-03-09T12:00:00",
      nome_arquivo_original: "leads.csv",
      stage: "bronze",
      evento_id: 42,
      pipeline_status: "pending",
      pipeline_report: null,
      created_at: "2026-03-09T12:00:00",
      ...bronzeBatchBase(),
    });
    mockedGetLeadBatchPreview.mockResolvedValue({
      headers: ["nome", "email"],
      rows: [["Alice", "alice@npbb.com.br"]],
      total_rows: 1,
    });

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();
    const dateInput = container.querySelector('input[type="date"]') as HTMLInputElement;
    const expectedDate = dateInput.value;

    await user.click(screen.getByRole("combobox", { name: /plataforma de origem/i }));
    await user.click(await screen.findByRole("option", { name: "email" }));

    await user.click(screen.getByRole("combobox", { name: /evento de referencia/i }));
    await user.click(await screen.findByRole("option", { name: /Evento ETL/i }));

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    const csvFile = createCsvFile();
    fireEvent.change(fileInput, { target: { files: [csvFile] } });

    await user.click(screen.getByRole("button", { name: "Enviar para Bronze" }));

    await waitFor(() => {
      expect(mockedCreateLeadBatch).toHaveBeenCalledWith("token-123", {
        quem_enviou: "demo@npbb.com.br",
        plataforma_origem: "email",
        data_envio: expectedDate,
        evento_id: 42,
        file: csvFile,
        origem_lote: "proponente",
        tipo_lead_proponente: "entrada_evento",
      });
    });
    await waitFor(() => {
      expect(mockedGetLeadBatchPreview).toHaveBeenCalledWith("token-123", 10);
    });

    expect(await screen.findByText("Preview do lote #10")).toBeInTheDocument();
    expect(screen.getByText("Estado atual do lote #10")).toBeInTheDocument();
    expect(screen.getByText("Colunas detectadas: 2 | Linhas de amostra: 1 de 1")).toBeInTheDocument();
    expect(screen.getByText("Alice")).toBeInTheDocument();
    expect(screen.getByText("alice@npbb.com.br")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByTestId("location")).toHaveTextContent("/leads/importar?step=upload");
    });
  });

  it("rehydrates Bronze metadata from the import hint before submit", async () => {
    mockedComputeFileSha256Hex.mockResolvedValueOnce("b".repeat(64));
    mockedGetLeadImportMetadataHint.mockResolvedValueOnce({
      arquivo_sha256: "b".repeat(64),
      source_batch_id: 91,
      plataforma_origem: "manual",
      data_envio: "2026-03-15T14:00:00",
      origem_lote: "ativacao",
      tipo_lead_proponente: null,
      evento_id: 42,
      ativacao_id: 5,
      confidence: "exact_hash_match",
      source_created_at: "2026-03-10T09:00:00",
    });
    mockedListEventoAtivacoes.mockResolvedValue([
      {
        id: 5,
        evento_id: 42,
        nome: "Stand reidratado",
        descricao: null,
        mensagem_qrcode: null,
        gamificacao_id: null,
        landing_url: null,
        qr_code_url: null,
        url_promotor: null,
        redireciona_pesquisa: false,
        checkin_unico: false,
        termo_uso: false,
        gera_cupom: false,
        created_at: "2026-03-10T09:00:00",
        updated_at: "2026-03-10T09:00:00",
      },
    ]);
    mockedCreateLeadBatch.mockResolvedValue({
      id: 14,
      enviado_por: 1,
      plataforma_origem: "manual",
      data_envio: "2026-03-15T00:00:00",
      data_upload: "2026-03-15T12:00:00",
      nome_arquivo_original: "leads.csv",
      stage: "bronze",
      evento_id: 42,
      origem_lote: "ativacao",
      tipo_lead_proponente: null,
      ativacao_id: 5,
      pipeline_status: "pending",
      pipeline_progress: null,
      pipeline_report: null,
      created_at: "2026-03-15T12:00:00",
    });
    mockedGetLeadBatchPreview.mockResolvedValue({
      headers: ["nome", "email"],
      rows: [["Alice", "alice@npbb.com.br"]],
      total_rows: 1,
    });

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    const csvFile = createCsvFile();
    fireEvent.change(fileInput, { target: { files: [csvFile] } });

    expect(
      await screen.findByText("Metadados recuperados de uma importacao anterior (mesmo ficheiro)."),
    ).toBeInTheDocument();
    await waitFor(() => {
      expect(mockedListEventoAtivacoes).toHaveBeenCalledWith("token-123", 42);
    });
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Enviar para Bronze" })).toBeEnabled();
    });

    await user.click(screen.getByRole("button", { name: "Enviar para Bronze" }));

    await waitFor(() => {
      expect(mockedCreateLeadBatch).toHaveBeenCalledWith("token-123", {
        quem_enviou: "demo@npbb.com.br",
        plataforma_origem: "manual",
        data_envio: "2026-03-15",
        evento_id: 42,
        file: csvFile,
        origem_lote: "ativacao",
        ativacao_id: 5,
      });
    });
  });

  it("preserves manual Bronze edits when the hint resolves later", async () => {
    const hintDeferred = createDeferred<{
      arquivo_sha256: string;
      source_batch_id: number;
      plataforma_origem: string;
      data_envio: string;
      origem_lote: "proponente";
      tipo_lead_proponente: "entrada_evento";
      evento_id: number;
      ativacao_id: null;
      confidence: "exact_hash_match";
      source_created_at: string;
    } | null>();
    mockedComputeFileSha256Hex.mockResolvedValueOnce("c".repeat(64));
    mockedGetLeadImportMetadataHint.mockReturnValueOnce(hintDeferred.promise);
    mockedCreateLeadBatch.mockResolvedValue({
      id: 15,
      enviado_por: 1,
      plataforma_origem: "manual",
      data_envio: "2026-03-20T00:00:00",
      data_upload: "2026-03-20T12:00:00",
      nome_arquivo_original: "leads.csv",
      stage: "bronze",
      evento_id: 42,
      pipeline_status: "pending",
      pipeline_report: null,
      created_at: "2026-03-20T12:00:00",
      ...bronzeBatchBase(),
    });
    mockedGetLeadBatchPreview.mockResolvedValue({
      headers: ["nome", "email"],
      rows: [["Alice", "alice@npbb.com.br"]],
      total_rows: 1,
    });

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    const csvFile = createCsvFile();
    fireEvent.change(fileInput, { target: { files: [csvFile] } });

    await user.click(screen.getByRole("combobox", { name: /plataforma de origem/i }));
    await user.click(await screen.findByRole("option", { name: "manual" }));

    hintDeferred.resolve({
      arquivo_sha256: "c".repeat(64),
      source_batch_id: 92,
      plataforma_origem: "email",
      data_envio: "2026-03-20T14:00:00",
      origem_lote: "proponente",
      tipo_lead_proponente: "entrada_evento",
      evento_id: 42,
      ativacao_id: null,
      confidence: "exact_hash_match",
      source_created_at: "2026-03-11T09:00:00",
    });

    expect(
      await screen.findByText("Metadados recuperados de uma importacao anterior (mesmo ficheiro)."),
    ).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Enviar para Bronze" }));

    await waitFor(() => {
      expect(mockedCreateLeadBatch).toHaveBeenCalledWith(
        "token-123",
        expect.objectContaining({
          file: csvFile,
          plataforma_origem: "manual",
          evento_id: 42,
          origem_lote: "proponente",
        }),
      );
    });
  });

  it("envia lote de ativacao com ativacao_id selecionada", async () => {
    mockedListEventoAtivacoes.mockResolvedValue([
      {
        id: 5,
        evento_id: 42,
        nome: "Stand import",
        descricao: null,
        mensagem_qrcode: null,
        gamificacao_id: null,
        landing_url: null,
        qr_code_url: null,
        url_promotor: null,
        redireciona_pesquisa: false,
        checkin_unico: false,
        termo_uso: false,
        gera_cupom: false,
        created_at: "2026-03-09T12:00:00",
        updated_at: "2026-03-09T12:00:00",
      },
    ]);
    mockedCreateLeadBatch.mockResolvedValue({
      id: 11,
      enviado_por: 1,
      plataforma_origem: "email",
      data_envio: "2026-03-09T00:00:00",
      data_upload: "2026-03-09T12:00:00",
      nome_arquivo_original: "leads.csv",
      stage: "bronze",
      evento_id: 42,
      origem_lote: "ativacao",
      tipo_lead_proponente: null,
      ativacao_id: 5,
      pipeline_status: "pending",
      pipeline_progress: null,
      pipeline_report: null,
      created_at: "2026-03-09T12:00:00",
    });
    mockedGetLeadBatchPreview.mockResolvedValue({
      headers: ["nome", "email"],
      rows: [["Bob", "bob@npbb.com.br"]],
      total_rows: 1,
    });

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();
    const dateInput = container.querySelector('input[type="date"]') as HTMLInputElement;
    const expectedDate = dateInput.value;

    await user.click(screen.getByRole("combobox", { name: /plataforma de origem/i }));
    await user.click(await screen.findByRole("option", { name: "email" }));

    await user.click(screen.getByRole("combobox", { name: /evento de referencia/i }));
    await user.click(await screen.findByRole("option", { name: /Evento ETL/i }));

    await waitFor(() => expect(mockedListEventoAtivacoes).toHaveBeenCalledWith("token-123", 42));

    await user.click(screen.getByRole("radio", { name: /ativacao \(importacao\)/i }));

    await user.click(await screen.findByLabelText(/ativacao vinculada/i));
    const listbox = await screen.findByRole("listbox");
    await user.click(within(listbox).getByText("Stand import"));

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    const csvFile = createCsvFile();
    fireEvent.change(fileInput, { target: { files: [csvFile] } });

    await user.click(screen.getByRole("button", { name: "Enviar para Bronze" }));

    await waitFor(() => {
      expect(mockedCreateLeadBatch).toHaveBeenCalledWith("token-123", {
        quem_enviou: "demo@npbb.com.br",
        plataforma_origem: "email",
        data_envio: expectedDate,
        evento_id: 42,
        file: csvFile,
        origem_lote: "ativacao",
        ativacao_id: 5,
      });
    });
  }, 60_000);

  it("bloqueia envio de lote de ativacao sem ativacao selecionada", async () => {
    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    await user.click(screen.getByRole("combobox", { name: /plataforma de origem/i }));
    await user.click(await screen.findByRole("option", { name: "email" }));

    await user.click(screen.getByRole("combobox", { name: /evento de referencia/i }));
    await user.click(await screen.findByRole("option", { name: /Evento ETL/i }));

    await user.click(screen.getByRole("radio", { name: /ativacao \(importacao\)/i }));

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    const csvFile = createCsvFile();
    fireEvent.change(fileInput, { target: { files: [csvFile] } });
    const submitButton = screen.getByRole("button", { name: "Enviar para Bronze" });

    expect(submitButton).toBeDisabled();
    expect(screen.getByText("Selecione a ativacao desta importacao para continuar.")).toBeInTheDocument();
    expect(mockedCreateLeadBatch).not.toHaveBeenCalled();
  });

  it("creates an ad-hoc event in the Bronze upload step and uses it for the batch", async () => {
    mockedCreateEvento.mockResolvedValue({
      id: 77,
      nome: "Evento Ad Hoc",
      cidade: "Sao Paulo",
      estado: "SP",
      concorrencia: false,
      data_inicio_prevista: "2099-02-01",
      data_fim_prevista: null,
      data_inicio_realizada: null,
      data_fim_realizada: null,
      descricao: null,
      investimento: null,
      publico_projetado: null,
      publico_realizado: null,
      agencia_id: null,
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
    mockedCreateLeadBatch.mockResolvedValue({
      id: 13,
      enviado_por: 1,
      plataforma_origem: "email",
      data_envio: "2026-03-09T00:00:00",
      data_upload: "2026-03-09T12:00:00",
      nome_arquivo_original: "leads.csv",
      stage: "bronze",
      evento_id: 77,
      pipeline_status: "pending",
      pipeline_report: null,
      created_at: "2026-03-09T12:00:00",
      ...bronzeBatchBase(),
    });
    mockedGetLeadBatchPreview.mockResolvedValue({
      headers: ["nome", "email"],
      rows: [["Alice", "alice@npbb.com.br"]],
      total_rows: 1,
    });

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();
    const dateInput = container.querySelector('input[type="date"]') as HTMLInputElement;
    const expectedDate = dateInput.value;

    await user.click(screen.getByRole("combobox", { name: /plataforma de origem/i }));
    await user.click(await screen.findByRole("option", { name: "email" }));

    await user.click(screen.getByRole("combobox", { name: /evento de referencia/i }));
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

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    const csvFile = createCsvFile();
    fireEvent.change(fileInput, { target: { files: [csvFile] } });
    await user.click(screen.getByRole("button", { name: "Enviar para Bronze" }));

    await waitFor(() => {
      expect(mockedCreateLeadBatch).toHaveBeenCalledWith("token-123", {
        quem_enviou: "demo@npbb.com.br",
        plataforma_origem: "email",
        data_envio: expectedDate,
        evento_id: 77,
        file: csvFile,
        origem_lote: "proponente",
        tipo_lead_proponente: "entrada_evento",
      });
    });
  });

  it("permite criar ativacao ad hoc quando o evento nao tem ativacoes", async () => {
    const ativacaoCriada = {
      id: 9,
      evento_id: 42,
      nome: "Nova stand",
      descricao: null,
      mensagem_qrcode: null,
      gamificacao_id: null,
      landing_url: null,
      qr_code_url: null,
      url_promotor: null,
      redireciona_pesquisa: false,
      checkin_unico: false,
      termo_uso: false,
      gera_cupom: false,
      created_at: "2026-03-09T12:00:00",
      updated_at: "2026-03-09T12:00:00",
    };
    mockedListEventoAtivacoes.mockReset();
    mockedListEventoAtivacoes.mockResolvedValueOnce([]).mockResolvedValue([ativacaoCriada]);
    mockedCreateEventoAtivacao.mockResolvedValue(ativacaoCriada);

    mockedCreateLeadBatch.mockResolvedValue({
      id: 12,
      enviado_por: 1,
      plataforma_origem: "email",
      data_envio: "2026-03-09T00:00:00",
      data_upload: "2026-03-09T12:00:00",
      nome_arquivo_original: "leads.csv",
      stage: "bronze",
      evento_id: 42,
      origem_lote: "ativacao",
      tipo_lead_proponente: null,
      ativacao_id: 9,
      pipeline_status: "pending",
      pipeline_progress: null,
      pipeline_report: null,
      created_at: "2026-03-09T12:00:00",
    });
    mockedGetLeadBatchPreview.mockResolvedValue({
      headers: ["nome", "email"],
      rows: [["Carol", "carol@npbb.com.br"]],
      total_rows: 1,
    });

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    await user.click(screen.getByRole("combobox", { name: /plataforma de origem/i }));
    await user.click(await screen.findByRole("option", { name: "email" }));

    await user.click(screen.getByRole("combobox", { name: /evento de referencia/i }));
    await user.click(await screen.findByRole("option", { name: /Evento ETL/i }));

    await user.click(screen.getByRole("radio", { name: /ativacao \(importacao\)/i }));

    await screen.findByText(/Este evento ainda nao possui ativacoes/i);
    await user.click(screen.getByRole("button", { name: /criar ativacao/i }));

    const dialog = await screen.findByRole("dialog");
    const nomeInput = within(dialog).getByLabelText(/nome da ativacao/i);
    fireEvent.change(nomeInput, { target: { value: "Nova stand" } });
    await user.click(within(dialog).getByRole("button", { name: /^criar$/i }));

    await waitFor(() => expect(mockedCreateEventoAtivacao).toHaveBeenCalled());
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [createCsvFile()] } });
    await user.click(screen.getByRole("button", { name: "Enviar para Bronze" }));

    await waitFor(() => {
      expect(mockedCreateLeadBatch).toHaveBeenCalledWith(
        "token-123",
        expect.objectContaining({ origem_lote: "ativacao", ativacao_id: 9 }),
      );
    });
  }, 60_000);

  it("preserves the created activation in single mode when the refresh fails after create", async () => {
    const ativacaoCriada = {
      id: 19,
      evento_id: 42,
      nome: "Ativacao resiliente",
      descricao: null,
      mensagem_qrcode: null,
      gamificacao_id: null,
      landing_url: null,
      qr_code_url: null,
      url_promotor: null,
      redireciona_pesquisa: false,
      checkin_unico: false,
      termo_uso: false,
      gera_cupom: false,
      created_at: "2026-03-09T12:00:00",
      updated_at: "2026-03-09T12:00:00",
    };
    mockedListEventoAtivacoes.mockReset();
    mockedListEventoAtivacoes
      .mockResolvedValueOnce([])
      .mockRejectedValueOnce(new Error("Falha ao recarregar ativacoes."));
    mockedCreateEventoAtivacao.mockResolvedValue(ativacaoCriada);
    mockedCreateLeadBatch.mockResolvedValue({
      id: 21,
      enviado_por: 1,
      plataforma_origem: "email",
      data_envio: "2026-03-09T00:00:00",
      data_upload: "2026-03-09T12:00:00",
      nome_arquivo_original: "leads.csv",
      stage: "bronze",
      evento_id: 42,
      origem_lote: "ativacao",
      tipo_lead_proponente: null,
      ativacao_id: 19,
      pipeline_status: "pending",
      pipeline_progress: null,
      pipeline_report: null,
      created_at: "2026-03-09T12:00:00",
    });
    mockedGetLeadBatchPreview.mockResolvedValue({
      headers: ["nome", "email"],
      rows: [["Carol", "carol@npbb.com.br"]],
      total_rows: 1,
    });

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    await user.click(screen.getByRole("combobox", { name: /plataforma de origem/i }));
    await user.click(await screen.findByRole("option", { name: "email" }));

    await user.click(screen.getByRole("combobox", { name: /evento de referencia/i }));
    await user.click(await screen.findByRole("option", { name: /Evento ETL/i }));

    await user.click(screen.getByRole("radio", { name: /ativacao \(importacao\)/i }));
    await screen.findByText(/Este evento ainda nao possui ativacoes/i);

    await user.click(screen.getByRole("button", { name: /criar ativacao/i }));
    const dialog = await screen.findByRole("dialog");
    fireEvent.change(within(dialog).getByLabelText(/nome da ativacao/i), {
      target: { value: "Ativacao resiliente" },
    });
    await user.click(within(dialog).getByRole("button", { name: /^criar$/i }));

    await waitFor(() => {
      expect(mockedCreateEventoAtivacao).toHaveBeenCalledWith("token-123", 42, {
        nome: "Ativacao resiliente",
      });
    });
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
    expect(screen.queryByText("Falha ao recarregar ativacoes.")).not.toBeInTheDocument();

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [createCsvFile()] } });
    await user.click(screen.getByRole("button", { name: "Enviar para Bronze" }));

    await waitFor(() => {
      expect(mockedCreateLeadBatch).toHaveBeenCalledWith(
        "token-123",
        expect.objectContaining({ origem_lote: "ativacao", ativacao_id: 19 }),
      );
    });
  });

  it("shows a load error instead of the create CTA when activation lookup fails in single mode", async () => {
    mockedListEventoAtivacoes.mockRejectedValueOnce(new Error("Falha ao carregar ativacoes do evento."));

    renderImportacaoPage();
    const user = userEvent.setup();

    await user.click(screen.getByRole("combobox", { name: /plataforma de origem/i }));
    await user.click(await screen.findByRole("option", { name: "email" }));

    await user.click(screen.getByRole("combobox", { name: /evento de referencia/i }));
    await user.click(await screen.findByRole("option", { name: /Evento ETL/i }));

    await user.click(screen.getByRole("radio", { name: /ativacao \(importacao\)/i }));

    expect(await screen.findByText("Falha ao carregar ativacoes do evento.")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /criar ativacao/i })).not.toBeInTheDocument();
  });

  it("reverte para proponente quando o evento selecionado nao suporta importacao por ativacao", async () => {
    mockedListReferenciaEventos.mockResolvedValue([
      {
        id: 42,
        nome: "Evento com agencia",
        data_inicio_prevista: "2099-01-01",
        agencia_id: 7,
        supports_activation_import: true,
        activation_import_block_reason: null,
      },
      {
        id: 77,
        nome: "Evento sem agencia",
        data_inicio_prevista: "2099-02-01",
        agencia_id: null,
        supports_activation_import: false,
        activation_import_block_reason:
          "Vincule uma agencia ao evento antes de importar leads de ativacao.",
      },
    ]);
    mockedCreateLeadBatch.mockResolvedValue({
      id: 18,
      enviado_por: 1,
      plataforma_origem: "email",
      data_envio: "2026-03-09T00:00:00",
      data_upload: "2026-03-09T12:00:00",
      nome_arquivo_original: "leads.csv",
      stage: "bronze",
      evento_id: 77,
      origem_lote: "proponente",
      tipo_lead_proponente: "entrada_evento",
      ativacao_id: null,
      pipeline_status: "pending",
      pipeline_progress: null,
      pipeline_report: null,
      created_at: "2026-03-09T12:00:00",
    });
    mockedGetLeadBatchPreview.mockResolvedValue({
      headers: ["nome", "email"],
      rows: [["Carol", "carol@npbb.com.br"]],
      total_rows: 1,
    });

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    await user.click(screen.getByRole("combobox", { name: /plataforma de origem/i }));
    await user.click(await screen.findByRole("option", { name: "email" }));

    await user.click(screen.getByRole("combobox", { name: /evento de referencia/i }));
    await user.click(await screen.findByRole("option", { name: /Evento com agencia/i }));
    await user.click(screen.getByRole("radio", { name: /ativacao \(importacao\)/i }));
    expect(screen.getByRole("radio", { name: /ativacao \(importacao\)/i })).toBeChecked();

    await user.click(screen.getByRole("combobox", { name: /evento de referencia/i }));
    await user.click(await screen.findByRole("option", { name: /Evento sem agencia/i }));

    expect(
      await screen.findByText("Vincule uma agencia ao evento antes de importar leads de ativacao."),
    ).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: /proponente/i })).toBeChecked();
    expect(screen.getByRole("radio", { name: /ativacao \(importacao\)/i })).toBeDisabled();
    expect(screen.queryByRole("button", { name: /criar ativacao/i })).not.toBeInTheDocument();

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    const csvFile = createCsvFile();
    fireEvent.change(fileInput, { target: { files: [csvFile] } });
    await user.click(screen.getByRole("button", { name: "Enviar para Bronze" }));

    await waitFor(() => {
      expect(mockedCreateLeadBatch).toHaveBeenCalledWith(
        "token-123",
        expect.objectContaining({
          evento_id: 77,
          origem_lote: "proponente",
          ativacao_id: undefined,
        }),
      );
    });
  });

  it("creates one draft row per selected file in Bronze batch mode", async () => {
    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    await switchToBatchMode(user);

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, {
      target: {
        files: [
          new File(["primeiro"], "batch-primeiro.csv", { type: "text/csv" }),
          new File(["segundo"], "batch-segundo.xlsx", {
            type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          }),
        ],
      },
    });

    expect(await screen.findByText("batch-primeiro.csv")).toBeInTheDocument();
    expect(screen.getByText("batch-segundo.xlsx")).toBeInTheDocument();
    expect(screen.getByText("2 arquivo(s)")).toBeInTheDocument();
  });

  it("rehydrates only the matching batch row and keeps the others manual", async () => {
    mockedComputeFileSha256Hex
      .mockResolvedValueOnce("d".repeat(64))
      .mockResolvedValueOnce("e".repeat(64));
    mockedGetLeadImportMetadataHint
      .mockResolvedValueOnce({
        arquivo_sha256: "d".repeat(64),
        source_batch_id: 101,
        plataforma_origem: "manual",
        data_envio: "2026-03-25T10:00:00",
        origem_lote: "proponente",
        tipo_lead_proponente: "bilheteria",
        evento_id: 42,
        ativacao_id: null,
        confidence: "exact_hash_match",
        source_created_at: "2026-03-12T08:00:00",
      })
      .mockResolvedValueOnce(null);
    mockedCreateLeadBatch.mockResolvedValue({
      id: 63,
      enviado_por: 1,
      plataforma_origem: "manual",
      data_envio: "2026-03-25T00:00:00",
      data_upload: "2026-03-25T12:00:00",
      nome_arquivo_original: "batch-com-hint.csv",
      stage: "bronze",
      evento_id: 42,
      pipeline_status: "pending",
      pipeline_report: null,
      created_at: "2026-03-25T12:00:00",
      origem_lote: "proponente",
      tipo_lead_proponente: "bilheteria",
      ativacao_id: null,
      pipeline_progress: null,
    });

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    await switchToBatchMode(user);

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    const fileWithHint = new File(["hint"], "batch-com-hint.csv", { type: "text/csv" });
    const fileWithoutHint = new File(["semhint"], "batch-sem-hint.csv", { type: "text/csv" });
    fireEvent.change(fileInput, {
      target: { files: [fileWithHint, fileWithoutHint] },
    });

    const hintedRow = findBatchRow("batch-com-hint.csv");
    const plainRow = findBatchRow("batch-sem-hint.csv");

    expect(
      await within(hintedRow).findByText("Metadados recuperados de uma importacao anterior (lote #101)."),
    ).toBeInTheDocument();
    expect(within(plainRow).queryByText(/Metadados recuperados/)).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /enviar linhas validas para bronze/i }));

    await waitFor(() => expect(mockedCreateLeadBatch).toHaveBeenCalledTimes(1));
    expect(mockedCreateLeadBatch).toHaveBeenCalledWith(
      "token-123",
      expect.objectContaining({
        file: fileWithHint,
        plataforma_origem: "manual",
        data_envio: "2026-03-25",
        evento_id: 42,
        origem_lote: "proponente",
        tipo_lead_proponente: "bilheteria",
      }),
    );
    expect(within(plainRow).getByText(/Selecione a plataforma de origem\./i)).toBeInTheDocument();
  });

  it("shows the inline agency editor in batch mode and unlocks activation import after updateEvento", async () => {
    mockedListReferenciaEventos.mockResolvedValue([
      {
        id: 77,
        nome: "Evento sem agencia",
        data_inicio_prevista: "2099-02-01",
        agencia_id: null,
        supports_activation_import: false,
        activation_import_block_reason:
          "Vincule uma agencia ao evento antes de importar leads de ativacao.",
      },
    ]);
    mockedUpdateEvento.mockResolvedValue(
      createEventoReadBase({
        id: 77,
        nome: "Evento sem agencia",
        data_inicio_prevista: "2099-02-01",
        agencia_id: 10,
      }),
    );

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    await switchToBatchMode(user);

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, {
      target: { files: [new File(["l1"], "batch-agencia.csv", { type: "text/csv" })] },
    });

    const row = findBatchRow("batch-agencia.csv");
    await selectBatchRowEvent(row, user, /Evento sem agencia/i);
    await selectBatchRowOrigem(row, user, /^Ativacao$/i);

    expect(
      await within(row).findByText("Vincule uma agencia ao evento antes de importar leads de ativacao."),
    ).toBeInTheDocument();
    expect(within(row).queryByText("Selecione a ativacao desta importacao.")).not.toBeInTheDocument();
    await waitFor(() => expect(mockedListAgencias).toHaveBeenCalled());

    await waitFor(() => {
      expect(
        within(findBatchRow("batch-agencia.csv")).getByRole("button", { name: /salvar agencia/i }),
      ).toBeDisabled();
    });
    await user.click(within(findBatchRow("batch-agencia.csv")).getByRole("combobox", { name: /agencia/i }));
    await user.click(await screen.findByRole("option", { name: "Agencia Alpha" }));

    await waitFor(() => {
      expect(
        within(findBatchRow("batch-agencia.csv")).getByRole("button", { name: /salvar agencia/i }),
      ).toBeEnabled();
    });
    await user.click(within(findBatchRow("batch-agencia.csv")).getByRole("button", { name: /salvar agencia/i }));

    await waitFor(() => {
      expect(mockedUpdateEvento).toHaveBeenCalledWith("token-123", 77, { agencia_id: 10 });
    });
    await waitFor(() => {
      expect(mockedListEventoAtivacoes).toHaveBeenCalledWith("token-123", 77);
    });
    expect(await within(findBatchRow("batch-agencia.csv")).findByRole("button", { name: /criar ativacao/i })).toBeInTheDocument();
  });

  it("keeps the agency editor loading responsive while rows change during the agencias request", async () => {
    const agenciasDeferred = createDeferred<Array<{ id: number; nome: string; dominio: string }>>();
    mockedListAgencias.mockReset();
    mockedListAgencias.mockReturnValueOnce(agenciasDeferred.promise);
    mockedListReferenciaEventos.mockResolvedValue([
      {
        id: 77,
        nome: "Evento sem agencia",
        data_inicio_prevista: "2099-02-01",
        agencia_id: null,
        supports_activation_import: false,
        activation_import_block_reason:
          "Vincule uma agencia ao evento antes de importar leads de ativacao.",
      },
    ]);

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    await switchToBatchMode(user);

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, {
      target: { files: [new File(["l1"], "batch-agencia-loading.csv", { type: "text/csv" })] },
    });

    const row = findBatchRow("batch-agencia-loading.csv");
    await selectBatchRowEvent(row, user, /Evento sem agencia/i);
    await selectBatchRowOrigem(row, user, /^Ativacao$/i);
    await waitFor(() => expect(mockedListAgencias).toHaveBeenCalledTimes(1));

    fireEvent.change(within(row).getByLabelText(/quem enviou/i), {
      target: { value: "operador@npbb.com.br" },
    });

    agenciasDeferred.resolve([{ id: 10, nome: "Agencia Alpha", dominio: "alpha.com.br" }]);

    await waitFor(() => {
      expect(within(findBatchRow("batch-agencia-loading.csv")).getByRole("combobox", { name: /agencia/i })).toBeEnabled();
    });
    expect(mockedListAgencias).toHaveBeenCalledTimes(1);
  });

  it("creates an activation inline in batch mode and submits the row as activation import", async () => {
    const ativacaoCriada = {
      id: 9,
      evento_id: 42,
      nome: "Nova ativacao batch",
      descricao: null,
      mensagem_qrcode: null,
      gamificacao_id: null,
      landing_url: null,
      qr_code_url: null,
      url_promotor: null,
      redireciona_pesquisa: false,
      checkin_unico: false,
      termo_uso: false,
      gera_cupom: false,
      created_at: "2026-03-09T12:00:00",
      updated_at: "2026-03-09T12:00:00",
    };
    mockedListEventoAtivacoes.mockReset();
    mockedListEventoAtivacoes.mockResolvedValueOnce([]).mockResolvedValue([ativacaoCriada]);
    mockedCreateEventoAtivacao.mockResolvedValue(ativacaoCriada);
    mockedCreateLeadBatch.mockResolvedValue({
      id: 50,
      enviado_por: 1,
      plataforma_origem: "email",
      data_envio: "2026-03-09T00:00:00",
      data_upload: "2026-03-09T12:00:00",
      nome_arquivo_original: "batch-ativacao.csv",
      stage: "bronze",
      evento_id: 42,
      origem_lote: "ativacao",
      tipo_lead_proponente: null,
      ativacao_id: 9,
      pipeline_status: "pending",
      pipeline_progress: null,
      pipeline_report: null,
      created_at: "2026-03-09T12:00:00",
    });

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    await switchToBatchMode(user);

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    const csvFile = new File(["batch"], "batch-ativacao.csv", { type: "text/csv" });
    fireEvent.change(fileInput, {
      target: { files: [csvFile] },
    });

    const row = findBatchRow("batch-ativacao.csv");
    await selectBatchRowPlatform(row, user);
    await selectBatchRowEvent(row, user, /Evento ETL/i);
    await selectBatchRowOrigem(row, user, /^Ativacao$/i);

    await waitFor(() => expect(mockedListEventoAtivacoes).toHaveBeenCalledWith("token-123", 42));
    await user.click(await within(row).findByRole("button", { name: /criar ativacao/i }));

    const dialog = await screen.findByRole("dialog");
    fireEvent.change(within(dialog).getByLabelText(/nome da ativacao/i), {
      target: { value: "Nova ativacao batch" },
    });
    await user.click(within(dialog).getByRole("button", { name: /^criar$/i }));

    await waitFor(() => expect(mockedCreateEventoAtivacao).toHaveBeenCalledWith("token-123", 42, { nome: "Nova ativacao batch" }));
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());

    await user.click(screen.getByRole("button", { name: /enviar linhas validas para bronze/i }));

    await waitFor(() => {
      expect(mockedCreateLeadBatch).toHaveBeenCalledWith(
        "token-123",
        expect.objectContaining({
          file: csvFile,
          evento_id: 42,
          origem_lote: "ativacao",
          ativacao_id: 9,
        }),
      );
    });
    expect(await within(row).findByRole("button", { name: /abrir mapeamento do batch/i })).toBeInTheDocument();
  });

  it("preserves the created activation in batch mode when the refresh fails after create", async () => {
    const ativacaoCriada = {
      id: 29,
      evento_id: 42,
      nome: "Nova ativacao batch resiliente",
      descricao: null,
      mensagem_qrcode: null,
      gamificacao_id: null,
      landing_url: null,
      qr_code_url: null,
      url_promotor: null,
      redireciona_pesquisa: false,
      checkin_unico: false,
      termo_uso: false,
      gera_cupom: false,
      created_at: "2026-03-09T12:00:00",
      updated_at: "2026-03-09T12:00:00",
    };
    mockedListEventoAtivacoes.mockReset();
    mockedListEventoAtivacoes
      .mockResolvedValueOnce([])
      .mockRejectedValueOnce(new Error("Falha ao recarregar ativacoes do batch."));
    mockedCreateEventoAtivacao.mockResolvedValue(ativacaoCriada);
    mockedCreateLeadBatch.mockResolvedValue({
      id: 51,
      enviado_por: 1,
      plataforma_origem: "email",
      data_envio: "2026-03-09T00:00:00",
      data_upload: "2026-03-09T12:00:00",
      nome_arquivo_original: "batch-ativacao-resiliente.csv",
      stage: "bronze",
      evento_id: 42,
      origem_lote: "ativacao",
      tipo_lead_proponente: null,
      ativacao_id: 29,
      pipeline_status: "pending",
      pipeline_progress: null,
      pipeline_report: null,
      created_at: "2026-03-09T12:00:00",
    });

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    await switchToBatchMode(user);

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    const csvFile = new File(["batch"], "batch-ativacao-resiliente.csv", { type: "text/csv" });
    fireEvent.change(fileInput, {
      target: { files: [csvFile] },
    });

    const row = findBatchRow("batch-ativacao-resiliente.csv");
    await selectBatchRowPlatform(row, user);
    await selectBatchRowEvent(row, user, /Evento ETL/i);
    await selectBatchRowOrigem(row, user, /^Ativacao$/i);
    await waitFor(() => expect(mockedListEventoAtivacoes).toHaveBeenCalledWith("token-123", 42));

    await user.click(await within(row).findByRole("button", { name: /criar ativacao/i }));
    const dialog = await screen.findByRole("dialog");
    fireEvent.change(within(dialog).getByLabelText(/nome da ativacao/i), {
      target: { value: "Nova ativacao batch resiliente" },
    });
    await user.click(within(dialog).getByRole("button", { name: /^criar$/i }));

    await waitFor(() => {
      expect(mockedCreateEventoAtivacao).toHaveBeenCalledWith("token-123", 42, {
        nome: "Nova ativacao batch resiliente",
      });
    });
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
    expect(within(row).queryByText("Falha ao recarregar ativacoes do batch.")).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /enviar linhas validas para bronze/i }));

    await waitFor(() => {
      expect(mockedCreateLeadBatch).toHaveBeenCalledWith(
        "token-123",
        expect.objectContaining({
          file: csvFile,
          evento_id: 42,
          origem_lote: "ativacao",
          ativacao_id: 29,
        }),
      );
    });
  });

  it("shows the row error when inline activation creation fails in batch mode", async () => {
    mockedListEventoAtivacoes.mockReset();
    mockedListEventoAtivacoes.mockResolvedValueOnce([]);
    mockedCreateEventoAtivacao.mockRejectedValueOnce(new Error("Falha ao criar ativacao do batch."));

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    await switchToBatchMode(user);

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, {
      target: { files: [new File(["batch"], "batch-ativacao-erro.csv", { type: "text/csv" })] },
    });

    const row = findBatchRow("batch-ativacao-erro.csv");
    await selectBatchRowPlatform(row, user);
    await selectBatchRowEvent(row, user, /Evento ETL/i);
    await selectBatchRowOrigem(row, user, /^Ativacao$/i);

    await user.click(await within(row).findByRole("button", { name: /criar ativacao/i }));
    const dialog = await screen.findByRole("dialog");
    fireEvent.change(within(dialog).getByLabelText(/nome da ativacao/i), {
      target: { value: "Erro batch" },
    });
    await user.click(within(dialog).getByRole("button", { name: /^criar$/i }));

    expect(await within(dialog).findByText("Falha ao criar ativacao do batch.")).toBeInTheDocument();
    expect(within(row).getByText("Falha ao criar ativacao do batch.")).toBeInTheDocument();
  });

  it("shows the row error when saving the agency fails in batch mode", async () => {
    mockedListReferenciaEventos.mockResolvedValue([
      {
        id: 77,
        nome: "Evento sem agencia",
        data_inicio_prevista: "2099-02-01",
        agencia_id: null,
        supports_activation_import: false,
        activation_import_block_reason:
          "Vincule uma agencia ao evento antes de importar leads de ativacao.",
      },
    ]);
    mockedUpdateEvento.mockRejectedValueOnce(new Error("Falha ao salvar agencia do batch."));

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    await switchToBatchMode(user);

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, {
      target: { files: [new File(["l1"], "batch-agencia-erro.csv", { type: "text/csv" })] },
    });

    const row = findBatchRow("batch-agencia-erro.csv");
    await selectBatchRowEvent(row, user, /Evento sem agencia/i);
    await selectBatchRowOrigem(row, user, /^Ativacao$/i);
    await waitFor(() => expect(mockedListAgencias).toHaveBeenCalled());

    await user.click(within(row).getByRole("combobox", { name: /agencia/i }));
    await user.click(await screen.findByRole("option", { name: "Agencia Alpha" }));
    await user.click(within(row).getByRole("button", { name: /salvar agencia/i }));

    expect((await within(row).findAllByText("Falha ao salvar agencia do batch.")).length).toBeGreaterThan(0);
  });

  it("shows the load error instead of the create CTA when activation lookup fails in batch mode", async () => {
    mockedListEventoAtivacoes.mockReset();
    mockedListEventoAtivacoes.mockRejectedValueOnce(new Error("Falha ao carregar ativacoes do batch."));

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    await switchToBatchMode(user);

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, {
      target: { files: [new File(["batch"], "batch-ativacao-load-error.csv", { type: "text/csv" })] },
    });

    const row = findBatchRow("batch-ativacao-load-error.csv");
    await selectBatchRowPlatform(row, user);
    await selectBatchRowEvent(row, user, /Evento ETL/i);
    await selectBatchRowOrigem(row, user, /^Ativacao$/i);

    expect(await within(row).findByText("Falha ao carregar ativacoes do batch.")).toBeInTheDocument();
    expect(within(row).queryByRole("button", { name: /criar ativacao/i })).not.toBeInTheDocument();
  });

  it("preserves partial successes in batch mode and retries only the failed row", async () => {
    const apiError = new ApiError({
      message: "Falha ao enviar a linha.",
      status: 400,
      detail: { message: "Falha ao enviar a linha." },
      code: "BATCH_UPLOAD_FAILED",
      method: "POST",
      url: "/leads/batches",
    });

    mockedCreateLeadBatch
      .mockResolvedValueOnce({
        id: 60,
        enviado_por: 1,
        plataforma_origem: "email",
        data_envio: "2026-03-09T00:00:00",
        data_upload: "2026-03-09T12:00:00",
        nome_arquivo_original: "batch-ok.csv",
        stage: "bronze",
        evento_id: 42,
        pipeline_status: "pending",
        pipeline_report: null,
        created_at: "2026-03-09T12:00:00",
        ...bronzeBatchBase(),
      })
      .mockRejectedValueOnce(apiError)
      .mockResolvedValueOnce({
        id: 61,
        enviado_por: 1,
        plataforma_origem: "email",
        data_envio: "2026-03-09T00:00:00",
        data_upload: "2026-03-09T12:00:00",
        nome_arquivo_original: "batch-erro.csv",
        stage: "bronze",
        evento_id: 42,
        pipeline_status: "pending",
        pipeline_report: null,
        created_at: "2026-03-09T12:00:00",
        ...bronzeBatchBase(),
      });

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    await switchToBatchMode(user);

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    const fileOk = new File(["ok"], "batch-ok.csv", { type: "text/csv" });
    const fileErro = new File(["erro"], "batch-erro.csv", { type: "text/csv" });
    fireEvent.change(fileInput, {
      target: { files: [fileOk, fileErro] },
    });

    const rowOk = findBatchRow("batch-ok.csv");
    const rowErro = findBatchRow("batch-erro.csv");

    await selectBatchRowPlatform(rowOk, user);
    await selectBatchRowEvent(rowOk, user, /Evento ETL/i);
    await selectBatchRowPlatform(rowErro, user);
    await selectBatchRowEvent(rowErro, user, /Evento ETL/i);

    await user.click(screen.getByRole("button", { name: /enviar linhas validas para bronze/i }));

    await waitFor(() => expect(mockedCreateLeadBatch).toHaveBeenCalledTimes(2));
    expect(await within(rowOk).findByRole("button", { name: /abrir mapeamento do batch/i })).toBeInTheDocument();
    expect(await within(rowErro).findByRole("button", { name: /reenviar linha/i })).toBeInTheDocument();
    expect(within(rowErro).getByText(/Falha ao enviar a linha\./)).toBeInTheDocument();

    await user.click(within(rowErro).getByRole("button", { name: /reenviar linha/i }));

    await waitFor(() => expect(mockedCreateLeadBatch).toHaveBeenCalledTimes(3));
    expect(await within(rowErro).findByRole("button", { name: /abrir mapeamento do batch/i })).toBeInTheDocument();
    expect(mockedCreateLeadBatch).toHaveBeenLastCalledWith(
      "token-123",
      expect.objectContaining({
        file: fileErro,
        evento_id: 42,
        origem_lote: "proponente",
      }),
    );
  });

  it("shows the batch workspace summary and returns from mapping to the grid with context=batch", async () => {
    mockedCreateLeadBatch.mockResolvedValueOnce({
      id: 70,
      enviado_por: 1,
      plataforma_origem: "email",
      data_envio: "2026-03-09T00:00:00",
      data_upload: "2026-03-09T12:00:00",
      nome_arquivo_original: "batch-workspace.csv",
      stage: "bronze",
      evento_id: 42,
      pipeline_status: "pending",
      pipeline_report: null,
      created_at: "2026-03-09T12:00:00",
      ...bronzeBatchBase(),
    });
    mockedGetLeadBatch.mockResolvedValueOnce({
      id: 70,
      enviado_por: 1,
      plataforma_origem: "email",
      data_envio: "2026-03-09T00:00:00",
      data_upload: "2026-03-09T12:00:00",
      nome_arquivo_original: "batch-workspace.csv",
      stage: "bronze",
      evento_id: 42,
      pipeline_status: "pending",
      pipeline_report: null,
      created_at: "2026-03-09T12:00:00",
      ...bronzeBatchBase(),
    });

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    await switchToBatchMode(user);

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    const workspaceFile = new File(["workspace"], "batch-workspace.csv", { type: "text/csv" });
    fireEvent.change(fileInput, { target: { files: [workspaceFile] } });

    const row = findBatchRow("batch-workspace.csv");
    await selectBatchRowPlatform(row, user);
    await selectBatchRowEvent(row, user, /Evento ETL/i);

    await user.click(screen.getByRole("button", { name: /enviar linhas validas para bronze/i }));

    expect(await screen.findByText("Workspace do batch Bronze")).toBeInTheDocument();
    expect(screen.getByText("1 lote(s) criados")).toBeInTheDocument();
    expect(screen.getByText("1 aguardando mapeamento batch")).toBeInTheDocument();
    expect(screen.getByText("0 pronto(s) para pipeline/retomada")).toBeInTheDocument();
    expect(screen.getByText("0 terminal(is)")).toBeInTheDocument();
    expect(await within(row).findByRole("button", { name: /abrir mapeamento do batch/i })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /abrir mapeamento unificado/i }));

    expect(await screen.findByText("Mapeamento batch shell 70")).toBeInTheDocument();
    expect(screen.getByTestId("location")).toHaveTextContent("/leads/importar?step=mapping&batch_id=70&context=batch");

    await user.click(screen.getByRole("button", { name: "Voltar ao batch" }));

    expect(await screen.findByText("Workspace do batch Bronze")).toBeInTheDocument();
    expect(screen.getByText("1 aguardando mapeamento batch")).toBeInTheDocument();
    expect(findBatchRow("batch-workspace.csv")).toBeInTheDocument();
    expect(screen.getByTestId("location")).toHaveTextContent("/leads/importar?step=upload");
  });

  it("returns a mapped batch row to the workspace as pipeline-ready", async () => {
    mockedCreateLeadBatch.mockResolvedValueOnce({
      id: 71,
      enviado_por: 1,
      plataforma_origem: "email",
      data_envio: "2026-03-09T00:00:00",
      data_upload: "2026-03-09T12:00:00",
      nome_arquivo_original: "batch-mapped.csv",
      stage: "bronze",
      evento_id: 42,
      pipeline_status: "pending",
      pipeline_report: null,
      created_at: "2026-03-09T12:00:00",
      ...bronzeBatchBase(),
    });
    mockedGetLeadBatch.mockResolvedValueOnce({
      id: 71,
      enviado_por: 1,
      plataforma_origem: "email",
      data_envio: "2026-03-09T00:00:00",
      data_upload: "2026-03-09T12:00:00",
      nome_arquivo_original: "batch-mapped.csv",
      stage: "bronze",
      evento_id: 42,
      pipeline_status: "pending",
      pipeline_report: null,
      created_at: "2026-03-09T12:00:00",
      ...bronzeBatchBase(),
    });

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    await switchToBatchMode(user);

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, {
      target: { files: [new File(["mapped"], "batch-mapped.csv", { type: "text/csv" })] },
    });

    const row = findBatchRow("batch-mapped.csv");
    await selectBatchRowPlatform(row, user);
    await selectBatchRowEvent(row, user, /Evento ETL/i);

    await user.click(screen.getByRole("button", { name: /enviar linhas validas para bronze/i }));
    await within(row).findByRole("button", { name: /abrir mapeamento do batch/i });

    await user.click(within(row).getByRole("button", { name: /abrir mapeamento do batch/i }));
    expect(await screen.findByText("Mapeamento batch shell 71")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Concluir shell batch mapeamento" }));

    expect(await screen.findByText("Pipeline shell 71")).toBeInTheDocument();
    expect(screen.getByTestId("location")).toHaveTextContent("/leads/importar?step=pipeline&batch_id=71&context=batch");

    await user.click(screen.getByRole("button", { name: "Voltar ao batch" }));

    expect(await screen.findByText("Workspace do batch Bronze")).toBeInTheDocument();
    expect(screen.getByText("0 aguardando mapeamento batch")).toBeInTheDocument();
    expect(screen.getByText("1 pronto(s) para pipeline/retomada")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /abrir proximo pipeline pendente/i })).toBeInTheDocument();
    expect(await within(findBatchRow("batch-mapped.csv")).findByRole("button", { name: /abrir pipeline/i })).toBeInTheDocument();
    expect(within(findBatchRow("batch-mapped.csv")).getByText("Fluxo: Pronto para pipeline")).toBeInTheDocument();
    expect(screen.getByTestId("location")).toHaveTextContent("/leads/importar?step=upload");
  });

  it("offers the next pending batch action in the pipeline screen after the current batch becomes terminal", async () => {
    mockedCreateLeadBatch
      .mockResolvedValueOnce({
        id: 80,
        enviado_por: 1,
        plataforma_origem: "email",
        data_envio: "2026-03-09T00:00:00",
        data_upload: "2026-03-09T12:00:00",
        nome_arquivo_original: "batch-pipeline-a.csv",
        stage: "bronze",
        evento_id: 42,
        pipeline_status: "pending",
        pipeline_report: null,
        created_at: "2026-03-09T12:00:00",
        ...bronzeBatchBase(),
      })
      .mockResolvedValueOnce({
        id: 81,
        enviado_por: 1,
        plataforma_origem: "email",
        data_envio: "2026-03-09T00:00:00",
        data_upload: "2026-03-09T12:00:00",
        nome_arquivo_original: "batch-pipeline-b.csv",
        stage: "bronze",
        evento_id: 42,
        pipeline_status: "pending",
        pipeline_report: null,
        created_at: "2026-03-09T12:00:00",
        ...bronzeBatchBase(),
      });
    mockedGetLeadBatch.mockResolvedValue({
      id: 80,
      enviado_por: 1,
      plataforma_origem: "email",
      data_envio: "2026-03-09T00:00:00",
      data_upload: "2026-03-09T12:00:00",
      nome_arquivo_original: "batch-pipeline-a.csv",
      stage: "bronze",
      evento_id: 42,
      pipeline_status: "pending",
      pipeline_report: null,
      created_at: "2026-03-09T12:00:00",
      ...bronzeBatchBase(),
    });

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    await switchToBatchMode(user);

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, {
      target: {
        files: [
          new File(["pipeline-a"], "batch-pipeline-a.csv", { type: "text/csv" }),
          new File(["pipeline-b"], "batch-pipeline-b.csv", { type: "text/csv" }),
        ],
      },
    });

    const rowA = findBatchRow("batch-pipeline-a.csv");
    const rowB = findBatchRow("batch-pipeline-b.csv");
    await selectBatchRowPlatform(rowA, user);
    await selectBatchRowEvent(rowA, user, /Evento ETL/i);
    await selectBatchRowPlatform(rowB, user);
    await selectBatchRowEvent(rowB, user, /Evento ETL/i);

    await user.click(screen.getByRole("button", { name: /enviar linhas validas para bronze/i }));
    await within(rowA).findByRole("button", { name: /abrir mapeamento do batch/i });
    await within(rowB).findByRole("button", { name: /abrir mapeamento do batch/i });

    await user.click(screen.getByRole("button", { name: /abrir mapeamento unificado/i }));
    expect(await screen.findByText("Mapeamento batch shell 80,81")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Concluir shell batch mapeamento" }));

    expect(await screen.findByText("Pipeline shell 80")).toBeInTheDocument();
    expect(screen.getByTestId("location")).toHaveTextContent("/leads/importar?step=pipeline&batch_id=80&context=batch");
    expect(screen.queryByRole("button", { name: /abrir proximo pipeline pendente/i })).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Sincronizar lote shell" }));

    expect(await screen.findByRole("button", { name: /abrir proximo pipeline pendente/i })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /abrir proximo pipeline pendente/i }));

    expect(await screen.findByText("Pipeline shell 81")).toBeInTheDocument();
    expect(screen.getByTestId("location")).toHaveTextContent("/leads/importar?step=pipeline&batch_id=81&context=batch");
  });

  it("keeps the batch workspace context when the operator falls back to single-file mapping", async () => {
    mockedCreateLeadBatch.mockResolvedValueOnce({
      id: 73,
      enviado_por: 1,
      plataforma_origem: "email",
      data_envio: "2026-03-09T00:00:00",
      data_upload: "2026-03-09T12:00:00",
      nome_arquivo_original: "batch-fallback.csv",
      stage: "bronze",
      evento_id: 42,
      pipeline_status: "pending",
      pipeline_report: null,
      created_at: "2026-03-09T12:00:00",
      ...bronzeBatchBase(),
    });
    mockedGetLeadBatch.mockResolvedValueOnce({
      id: 73,
      enviado_por: 1,
      plataforma_origem: "email",
      data_envio: "2026-03-09T00:00:00",
      data_upload: "2026-03-09T12:00:00",
      nome_arquivo_original: "batch-fallback.csv",
      stage: "bronze",
      evento_id: 42,
      pipeline_status: "pending",
      pipeline_report: null,
      created_at: "2026-03-09T12:00:00",
      ...bronzeBatchBase(),
    });

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    await switchToBatchMode(user);

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, {
      target: { files: [new File(["fallback"], "batch-fallback.csv", { type: "text/csv" })] },
    });

    const row = findBatchRow("batch-fallback.csv");
    await selectBatchRowPlatform(row, user);
    await selectBatchRowEvent(row, user, /Evento ETL/i);

    await user.click(screen.getByRole("button", { name: /enviar linhas validas para bronze/i }));
    await within(row).findByRole("button", { name: /abrir mapeamento do batch/i });

    await user.click(within(row).getByRole("button", { name: /abrir mapeamento do batch/i }));
    expect(await screen.findByText("Mapeamento batch shell 73")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Fallback shell batch mapeamento" }));

    expect(await screen.findByText("Mapeamento shell 73")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Voltar ao batch" })).toBeInTheDocument();
    expect(screen.getByTestId("location")).toHaveTextContent(
      "/leads/importar?step=mapping&batch_id=73&context=batch&mapping_mode=single",
    );

    await user.click(screen.getByRole("button", { name: "Voltar ao batch" }));

    expect(await screen.findByText("Workspace do batch Bronze")).toBeInTheDocument();
    expect(screen.getByTestId("location")).toHaveTextContent("/leads/importar?step=upload");
  });

  it("reconciles the batch workspace row after returning from pipeline", async () => {
    mockedCreateLeadBatch.mockResolvedValueOnce({
      id: 72,
      enviado_por: 1,
      plataforma_origem: "email",
      data_envio: "2026-03-09T00:00:00",
      data_upload: "2026-03-09T12:00:00",
      nome_arquivo_original: "batch-pipeline.csv",
      stage: "bronze",
      evento_id: 42,
      pipeline_status: "pending",
      pipeline_report: null,
      created_at: "2026-03-09T12:00:00",
      ...bronzeBatchBase(),
    });
    mockedGetLeadBatch
      .mockResolvedValueOnce({
        id: 72,
        enviado_por: 1,
        plataforma_origem: "email",
        data_envio: "2026-03-09T00:00:00",
        data_upload: "2026-03-09T12:00:00",
        nome_arquivo_original: "batch-pipeline.csv",
        stage: "bronze",
        evento_id: 42,
        pipeline_status: "pending",
        pipeline_report: null,
        created_at: "2026-03-09T12:00:00",
        ...bronzeBatchBase(),
      })
      .mockResolvedValueOnce({
        id: 72,
        enviado_por: 1,
        plataforma_origem: "email",
        data_envio: "2026-03-09T00:00:00",
        data_upload: "2026-03-09T12:00:00",
        nome_arquivo_original: "batch-pipeline.csv",
        stage: "gold",
        evento_id: 42,
        pipeline_status: "pass",
        pipeline_report: null,
        created_at: "2026-03-09T12:00:00",
        ...bronzeBatchBase(),
      });

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    await switchToBatchMode(user);

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, {
      target: { files: [new File(["pipeline"], "batch-pipeline.csv", { type: "text/csv" })] },
    });

    const row = findBatchRow("batch-pipeline.csv");
    await selectBatchRowPlatform(row, user);
    await selectBatchRowEvent(row, user, /Evento ETL/i);

    await user.click(screen.getByRole("button", { name: /enviar linhas validas para bronze/i }));
    await within(row).findByRole("button", { name: /abrir mapeamento do batch/i });

    await user.click(within(row).getByRole("button", { name: /abrir mapeamento do batch/i }));
    await user.click(await screen.findByRole("button", { name: "Concluir shell batch mapeamento" }));

    expect(await screen.findByText("Pipeline shell 72")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Voltar ao batch" })).toBeInTheDocument();
    expect(screen.getByTestId("location")).toHaveTextContent("/leads/importar?step=pipeline&batch_id=72&context=batch");

    await user.click(screen.getByRole("button", { name: "Voltar ao batch" }));

    expect(await screen.findByText("Workspace do batch Bronze")).toBeInTheDocument();
    expect(screen.getByText("1 terminal(is)")).toBeInTheDocument();
    expect(within(findBatchRow("batch-pipeline.csv")).getByText("Fluxo: Pipeline aprovado")).toBeInTheDocument();
    expect(screen.getByTestId("location")).toHaveTextContent("/leads/importar?step=upload");
    expect(mockedGetLeadBatch).toHaveBeenLastCalledWith("token-123", 72);
  });

  it("marks only pending rows as session-expired when the auth token disappears in batch mode", async () => {
    mockedCreateLeadBatch.mockResolvedValueOnce({
      id: 62,
      enviado_por: 1,
      plataforma_origem: "email",
      data_envio: "2026-03-09T00:00:00",
      data_upload: "2026-03-09T12:00:00",
      nome_arquivo_original: "batch-ok-token.csv",
      stage: "bronze",
      evento_id: 42,
      pipeline_status: "pending",
      pipeline_report: null,
      created_at: "2026-03-09T12:00:00",
      ...bronzeBatchBase(),
    });

    const { container, rerender } = renderImportacaoPage();
    const user = userEvent.setup();

    await switchToBatchMode(user);

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    const createdFile = new File(["ok"], "batch-ok-token.csv", { type: "text/csv" });
    const pendingFile = new File(["pending"], "batch-pendente-token.csv", { type: "text/csv" });
    fireEvent.change(fileInput, {
      target: { files: [createdFile, pendingFile] },
    });

    const createdRow = findBatchRow("batch-ok-token.csv");
    const pendingRow = findBatchRow("batch-pendente-token.csv");

    await selectBatchRowPlatform(createdRow, user);
    await selectBatchRowEvent(createdRow, user, /Evento ETL/i);

    await user.click(screen.getByRole("button", { name: /enviar linhas validas para bronze/i }));

    expect(await within(createdRow).findByRole("button", { name: /abrir mapeamento do batch/i })).toBeInTheDocument();
    expect(within(pendingRow).getByText(/Selecione a plataforma de origem\./i)).toBeInTheDocument();

    mockedUseAuth.mockReturnValue({
      token: null,
      user: { id: 1, email: "demo@npbb.com.br", tipo_usuario: "admin", agencia_id: null },
      loading: false,
      refreshing: false,
      error: null,
      refresh: vi.fn(),
      login: vi.fn(),
      logout: vi.fn(),
    });
    rerender(
      <MemoryRouter initialEntries={["/leads/importar"]}>
        <Routes>
          <Route path="/leads/importar" element={<ImportacaoHarness />} />
        </Routes>
      </MemoryRouter>,
    );

    await user.click(screen.getByRole("button", { name: /enviar linhas validas para bronze/i }));

    expect(await within(findBatchRow("batch-pendente-token.csv")).findByText("Sessao expirada. Faca login novamente.")).toBeInTheDocument();
    expect(within(findBatchRow("batch-ok-token.csv")).queryByText("Sessao expirada. Faca login novamente.")).not.toBeInTheDocument();
    expect(within(findBatchRow("batch-ok-token.csv")).getByRole("button", { name: /abrir mapeamento do batch/i })).toBeInTheDocument();
  });

  it("degrades context=batch to the standalone mapping flow when no batch workspace is active", async () => {
    mockedGetLeadBatch.mockResolvedValueOnce({
      id: 99,
      enviado_por: 1,
      plataforma_origem: "email",
      data_envio: "2026-03-09T00:00:00",
      data_upload: "2026-03-09T12:00:00",
      nome_arquivo_original: "leads.csv",
      stage: "silver",
      evento_id: 42,
      pipeline_status: "pending",
      pipeline_report: null,
      created_at: "2026-03-09T12:00:00",
      ...bronzeBatchBase(),
    });

    renderImportacaoPage("/leads/importar?step=mapping&batch_id=99&context=batch");
    const user = userEvent.setup();

    expect(await screen.findByText("Mapeamento shell 99")).toBeInTheDocument();
    expect(screen.getByTestId("location")).toHaveTextContent("/leads/importar?step=mapping&batch_id=99&context=batch");

    await user.click(screen.getByRole("button", { name: "Concluir shell mapeamento" }));

    expect(await screen.findByText("Pipeline shell 99")).toBeInTheDocument();
    expect(screen.getByTestId("location")).toHaveTextContent("/leads/importar?step=pipeline&batch_id=99");
  });

  it("opens the mapping step inside the same shell and preserves batch_id in the query string", async () => {
    mockedCreateLeadBatch.mockResolvedValue({
      id: 10,
      enviado_por: 1,
      plataforma_origem: "email",
      data_envio: "2026-03-09T00:00:00",
      data_upload: "2026-03-09T12:00:00",
      nome_arquivo_original: "leads.csv",
      stage: "bronze",
      evento_id: 42,
      pipeline_status: "pending",
      pipeline_report: null,
      created_at: "2026-03-09T12:00:00",
      ...bronzeBatchBase(),
    });
    mockedGetLeadBatchPreview.mockResolvedValue({
      headers: ["nome", "email"],
      rows: [["Alice", "alice@npbb.com.br"]],
      total_rows: 1,
    });
    mockedGetLeadBatch.mockResolvedValue({
      id: 10,
      enviado_por: 1,
      plataforma_origem: "email",
      data_envio: "2026-03-09T00:00:00",
      data_upload: "2026-03-09T12:00:00",
      nome_arquivo_original: "leads.csv",
      stage: "bronze",
      evento_id: 42,
      pipeline_status: "pending",
      pipeline_report: null,
      created_at: "2026-03-09T12:00:00",
      ...bronzeBatchBase(),
    });

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    await user.click(screen.getByRole("combobox", { name: /plataforma de origem/i }));
    await user.click(await screen.findByRole("option", { name: "email" }));

    await user.click(screen.getByRole("combobox", { name: /evento de referencia/i }));
    await user.click(await screen.findByRole("option", { name: /Evento ETL/i }));

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [createCsvFile()] } });

    await user.click(screen.getByRole("button", { name: "Enviar para Bronze" }));
    await screen.findByText("Preview do lote #10");

    await user.click(screen.getByRole("button", { name: "Ir para Mapeamento" }));

    expect(await screen.findByText("Mapeamento shell 10")).toBeInTheDocument();
    expect(screen.getByText("Evento fixo shell 42")).toBeInTheDocument();
    expect(screen.getByTestId("location")).toHaveTextContent("/leads/importar?step=mapping&batch_id=10");
    expect(mockedGetLeadBatch).toHaveBeenCalledWith("token-123", 10);
    expect(mockedCreateLeadBatch).toHaveBeenCalledWith(
      "token-123",
      expect.objectContaining({ evento_id: 42 }),
    );
  });

  it("resumes the mapping step from query params and can advance to pipeline without leaving the shell", async () => {
    mockedGetLeadBatch.mockResolvedValue({
      id: 10,
      enviado_por: 1,
      plataforma_origem: "email",
      data_envio: "2026-03-09T00:00:00",
      data_upload: "2026-03-09T12:00:00",
      nome_arquivo_original: "leads.csv",
      stage: "silver",
      evento_id: 42,
      pipeline_status: "pending",
      pipeline_report: null,
      created_at: "2026-03-09T12:00:00",
      ...bronzeBatchBase(),
    });

    renderImportacaoPage("/leads/importar?step=mapping&batch_id=10");
    const user = userEvent.setup();

    expect(await screen.findByText("Mapeamento shell 10")).toBeInTheDocument();
    expect(
      screen.getByText("Campos do evento serao derivados automaticamente do cadastro do evento selecionado."),
    ).toBeInTheDocument();
    expect(screen.getByTestId("location")).toHaveTextContent("/leads/importar?step=mapping&batch_id=10");

    await user.click(screen.getByRole("button", { name: "Concluir shell mapeamento" }));

    expect(await screen.findByText("Pipeline shell 10")).toBeInTheDocument();
    expect(screen.getByTestId("location")).toHaveTextContent("/leads/importar?step=pipeline&batch_id=10");
  });

  it("keeps the mapping event editable for legacy batches without evento_id", async () => {
    mockedGetLeadBatch.mockResolvedValue({
      id: 10,
      enviado_por: 1,
      plataforma_origem: "email",
      data_envio: "2026-03-09T00:00:00",
      data_upload: "2026-03-09T12:00:00",
      nome_arquivo_original: "leads.csv",
      stage: "bronze",
      evento_id: null,
      pipeline_status: "pending",
      pipeline_report: null,
      created_at: "2026-03-09T12:00:00",
      ...bronzeBatchBase(),
    });

    renderImportacaoPage("/leads/importar?step=mapping&batch_id=10");

    expect(await screen.findByText("Mapeamento shell 10")).toBeInTheDocument();
    expect(screen.getByText("Evento editavel shell")).toBeInTheDocument();
    expect(
      screen.queryByText("Campos do evento serao derivados automaticamente do cadastro do evento selecionado."),
    ).not.toBeInTheDocument();
    expect(screen.getByTestId("location")).toHaveTextContent("/leads/importar?step=mapping&batch_id=10");
  });

  it("returns to a fresh Bronze shell from the pipeline step", async () => {
    renderImportacaoPage("/leads/importar?step=pipeline&batch_id=10");
    const user = userEvent.setup();

    expect(screen.getByText("Pipeline shell 10")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Nova importacao shell" }));

    expect(screen.getByRole("button", { name: "Enviar para Bronze" })).toBeInTheDocument();
    expect(screen.getByTestId("location")).toHaveTextContent("/leads/importar?step=upload");
  });

  it("shows the ETL header row prompt when automatic detection needs input", async () => {
    mockedPreviewLeadImportEtl.mockResolvedValue({
      status: "header_required",
      message: "Nao foi possivel identificar automaticamente a linha do cabecalho com CPF.",
      max_row: 10,
      scanned_rows: 10,
      required_fields: ["cpf"],
    });

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    await user.click(screen.getByRole("combobox", { name: /fluxo de processamento/i }));
    await user.click(await screen.findByRole("option", { name: "ETL CSV/XLSX" }));

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    const xlsxFile = createXlsxFile();
    fireEvent.change(fileInput, { target: { files: [xlsxFile] } });

    await user.click(await screen.findByRole("combobox", { name: /evento de referencia/i }));
    await user.click(await screen.findByRole("option", { name: /Evento ETL/i }));
    await user.click(screen.getByRole("button", { name: "Gerar preview ETL" }));

    expect(await screen.findByLabelText("Linha do cabecalho")).toBeInTheDocument();
    expect(mockedPreviewLeadImportEtl).toHaveBeenCalledWith("token-123", xlsxFile, 42, false, {});
    expect(screen.getByTestId("location")).toHaveTextContent("/leads/importar?step=etl");
  });

  it("shows the ETL CPF column prompt with active sheet context when header selection still needs CPF mapping", async () => {
    mockedPreviewLeadImportEtl.mockResolvedValue({
      status: "cpf_column_required",
      message: "A linha indicada nao contem uma coluna de CPF reconhecida.",
      header_row: 2,
      columns: [
        { column_index: 1, column_letter: "A", source_value: "Documento" },
        { column_index: 2, column_letter: "B", source_value: "Email" },
      ],
      required_fields: ["cpf"],
      available_sheets: ["Indice", "Dados"],
      active_sheet: "Dados",
    });

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    await user.click(screen.getByRole("combobox", { name: /fluxo de processamento/i }));
    await user.click(await screen.findByRole("option", { name: "ETL CSV/XLSX" }));

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    const xlsxFile = createXlsxFile();
    fireEvent.change(fileInput, { target: { files: [xlsxFile] } });

    await user.click(await screen.findByRole("combobox", { name: /evento de referencia/i }));
    await user.click(await screen.findByRole("option", { name: /Evento ETL/i }));
    await user.click(screen.getByRole("button", { name: "Gerar preview ETL" }));

    expect(await screen.findByText("Folha ativa na ultima tentativa: Dados")).toBeInTheDocument();

    await user.click(screen.getByRole("combobox", { name: "Aba do ficheiro" }));
    expect(await screen.findByRole("option", { name: "Primeira aba (padrao)" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Dados" })).toBeInTheDocument();
  });

  it("creates an ad-hoc event in the ETL step and uses it for preview", async () => {
    mockedCreateEvento.mockResolvedValue({
      id: 88,
      nome: "Evento ETL Novo",
      cidade: "Rio de Janeiro",
      estado: "RJ",
      concorrencia: false,
      data_inicio_prevista: "2099-03-10",
      data_fim_prevista: "2099-03-12",
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
    mockedPreviewLeadImportEtl.mockResolvedValue({
      status: "previewed",
      session_token: "session-999",
      total_rows: 1,
      valid_rows: 1,
      invalid_rows: 0,
      dq_report: [],
    });

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    await user.click(screen.getByRole("combobox", { name: /fluxo de processamento/i }));
    await user.click(await screen.findByRole("option", { name: "ETL CSV/XLSX" }));

    await user.click(screen.getByRole("combobox", { name: /evento de referencia/i }));
    await user.click(await screen.findByRole("option", { name: /\+ Criar evento rapidamente/i }));

    const dialog = await screen.findByRole("dialog");
    await user.type(within(dialog).getByLabelText(/nome do evento/i), "Evento ETL Novo");
    fireEvent.change(within(dialog).getByLabelText(/data de inicio/i), {
      target: { value: "2099-03-10" },
    });
    fireEvent.change(within(dialog).getByLabelText(/data de fim/i), {
      target: { value: "2099-03-12" },
    });
    await user.type(within(dialog).getByLabelText(/cidade/i), "Rio de Janeiro");
    await user.click(within(dialog).getByRole("combobox", { name: /estado/i }));
    await user.click(await screen.findByRole("option", { name: "RJ" }));
    await user.click(within(dialog).getByRole("combobox", { name: /agencia responsavel/i }));
    await user.click(await screen.findByRole("option", { name: "Agencia Alpha" }));
    await user.click(within(dialog).getByRole("button", { name: "Salvar" }));
    await waitFor(() => {
      expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    });

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    const xlsxFile = createXlsxFile();
    fireEvent.change(fileInput, { target: { files: [xlsxFile] } });
    await user.click(screen.getByRole("button", { name: "Gerar preview ETL" }));

    await waitFor(() => {
      expect(mockedPreviewLeadImportEtl).toHaveBeenCalledWith("token-123", xlsxFile, 88, false, {});
    });
  });

  it("handles ETL warnings and confirms the commit inside the shell", async () => {
    mockedPreviewLeadImportEtl.mockResolvedValue({
      status: "previewed",
      session_token: "session-123",
      total_rows: 3,
      valid_rows: 2,
      invalid_rows: 1,
      dq_report: [
        {
          check_name: "duplicidade_cpf_evento",
          severity: "warning",
          affected_rows: 1,
          sample: [],
          message: "Duplicidade no lote",
        },
      ],
    });
    mockedCommitLeadImportEtl
      .mockRejectedValueOnce(
        new ApiError({
          message: "Commit bloqueado por warnings.",
          status: 400,
          detail: { message: "Commit bloqueado por warnings." },
          code: "ETL_COMMIT_BLOCKED",
          method: "POST",
          url: "/leads/import/etl/commit",
        }),
      )
      .mockResolvedValueOnce({
        session_token: "session-123",
        total_rows: 3,
        valid_rows: 2,
        invalid_rows: 1,
        created: 1,
        updated: 1,
        skipped: 1,
        errors: 0,
        strict: false,
        status: "committed",
        dq_report: [],
        persistence_failures: [],
      });

    const { container } = renderImportacaoPage("/leads/importar?step=etl");
    const user = userEvent.setup();

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    const csvFile = createCsvFile();
    fireEvent.change(fileInput, { target: { files: [csvFile] } });

    await user.click(await screen.findByRole("combobox", { name: /evento de referencia/i }));
    await user.click(await screen.findByRole("option", { name: /Evento ETL/i }));
    await user.click(screen.getByRole("button", { name: "Gerar preview ETL" }));

    expect(await screen.findByText("Linhas: 3 | Validas: 2 | Invalidas: 1")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Confirmar importacao ETL" }));

    expect(await screen.findByText(/Confirme que deseja prosseguir mesmo assim\./)).toBeInTheDocument();
    expect(mockedCommitLeadImportEtl).toHaveBeenNthCalledWith(1, "token-123", "session-123", 42, false);

    await user.click(screen.getByRole("button", { name: "Confirmar mesmo com avisos" }));

    expect(mockedCommitLeadImportEtl).toHaveBeenNthCalledWith(2, "token-123", "session-123", 42, true);
    expect(
      await screen.findByText(
        "Importacao concluida: 1 criado(s), 1 atualizado(s), 1 ignorado(s), 0 erro(s).",
      ),
    ).toBeInTheDocument();
  });

  it("keeps ETL retry available and shows failed rows after partial failure", async () => {
    mockedPreviewLeadImportEtl.mockResolvedValue({
      status: "previewed",
      session_token: "session-123",
      total_rows: 3,
      valid_rows: 2,
      invalid_rows: 1,
      dq_report: [],
    });
    mockedCommitLeadImportEtl
      .mockResolvedValueOnce({
        session_token: "session-123",
        total_rows: 3,
        valid_rows: 2,
        invalid_rows: 1,
        created: 1,
        updated: 0,
        skipped: 1,
        errors: 1,
        strict: false,
        status: "partial_failure",
        dq_report: [],
        persistence_failures: [{ row_number: 7, reason: "db timeout" }],
      })
      .mockResolvedValueOnce({
        session_token: "session-123",
        total_rows: 3,
        valid_rows: 2,
        invalid_rows: 1,
        created: 1,
        updated: 1,
        skipped: 0,
        errors: 0,
        strict: false,
        status: "committed",
        dq_report: [],
        persistence_failures: [],
      });

    const { container } = renderImportacaoPage("/leads/importar?step=etl");
    const user = userEvent.setup();

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    const csvFile = createCsvFile();
    fireEvent.change(fileInput, { target: { files: [csvFile] } });

    await user.click(await screen.findByRole("combobox", { name: /evento de referencia/i }));
    await user.click(await screen.findByRole("option", { name: /Evento ETL/i }));
    await user.click(screen.getByRole("button", { name: "Gerar preview ETL" }));

    await user.click(await screen.findByRole("button", { name: "Confirmar importacao ETL" }));

    expect(
      await screen.findByText(
        /Importacao parcialmente concluida: 1 criado\(s\), 0 atualizado\(s\), 1 ignorado\(s\), 1 erro\(s\)\./,
      ),
    ).toBeInTheDocument();
    expect(await screen.findByText("Linha 7: db timeout")).toBeInTheDocument();

    const retryButton = screen.getByRole("button", { name: "Retentar importacao ETL" });
    expect(retryButton).toBeEnabled();

    await user.click(retryButton);

    expect(mockedCommitLeadImportEtl).toHaveBeenNthCalledWith(1, "token-123", "session-123", 42, false);
    expect(mockedCommitLeadImportEtl).toHaveBeenNthCalledWith(2, "token-123", "session-123", 42, false);
    expect(
      await screen.findByText(
        "Importacao concluida: 1 criado(s), 1 atualizado(s), 0 ignorado(s), 0 erro(s).",
      ),
    ).toBeInTheDocument();
  });
});
