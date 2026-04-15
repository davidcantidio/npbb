import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";

import { ApiError } from "../../services/http";
import {
  commitLeadImportEtl,
  createLeadBatch,
  getLeadBatch,
  getLeadBatchPreview,
  listReferenciaEventos,
  previewLeadImportEtl,
} from "../../services/leads_import";
import { createEventoAtivacao, listEventoAtivacoes } from "../../services/eventos/workflow";
import { useAuth } from "../../store/auth";
import ImportacaoPage from "../leads/ImportacaoPage";

vi.mock("../leads/MapeamentoPage", () => ({
  default: ({
    batchId,
    fixedEventoId,
    onCancel,
    onMapped,
  }: {
    batchId?: number;
    fixedEventoId?: number | null;
    onCancel?: () => void;
    onMapped?: (result: { batch_id: number; silver_count: number; stage: string }) => void;
  }) => (
    <div>
      <div>{`Mapeamento shell ${batchId ?? 0}`}</div>
      <div>{fixedEventoId != null ? `Evento fixo shell ${fixedEventoId}` : "Evento editavel shell"}</div>
      <button type="button" onClick={() => onCancel?.()}>
        Cancelar shell mapeamento
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

vi.mock("../leads/PipelineStatusPage", () => ({
  default: ({
    batchId,
    onNewImport,
  }: {
    batchId?: number;
    onNewImport?: () => void;
  }) => (
    <div>
      <div>{`Pipeline shell ${batchId ?? 0}`}</div>
      <button type="button" onClick={() => onNewImport?.()}>
        Nova importacao shell
      </button>
    </div>
  ),
}));

vi.mock("../../store/auth", () => ({ useAuth: vi.fn() }));
vi.mock("../../services/leads_import", () => ({
  commitLeadImportEtl: vi.fn(),
  createLeadBatch: vi.fn(),
  getLeadBatch: vi.fn(),
  getLeadBatchPreview: vi.fn(),
  listReferenciaEventos: vi.fn(),
  previewLeadImportEtl: vi.fn(),
}));
vi.mock("../../services/eventos/workflow", () => ({
  listEventoAtivacoes: vi.fn(),
  createEventoAtivacao: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);
const mockedCommitLeadImportEtl = vi.mocked(commitLeadImportEtl);
const mockedCreateLeadBatch = vi.mocked(createLeadBatch);
const mockedGetLeadBatch = vi.mocked(getLeadBatch);
const mockedGetLeadBatchPreview = vi.mocked(getLeadBatchPreview);
const mockedListReferenciaEventos = vi.mocked(listReferenciaEventos);
const mockedPreviewLeadImportEtl = vi.mocked(previewLeadImportEtl);
const mockedListEventoAtivacoes = vi.mocked(listEventoAtivacoes);
const mockedCreateEventoAtivacao = vi.mocked(createEventoAtivacao);

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

function bronzeBatchBase() {
  return {
    origem_lote: "proponente" as const,
    tipo_lead_proponente: "entrada_evento",
    ativacao_id: null as number | null,
    pipeline_progress: null as null,
  };
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
    mockedListReferenciaEventos.mockResolvedValue([
      { id: 42, nome: "Evento ETL", data_inicio_prevista: "2099-01-01" },
    ]);
    mockedListEventoAtivacoes.mockResolvedValue([]);
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
    expect(screen.getByDisplayValue(new Date().toISOString().slice(0, 10))).toBeInTheDocument();
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
    expect(mockedPreviewLeadImportEtl).toHaveBeenCalledWith("token-123", xlsxFile, 42, false, undefined);
    expect(screen.getByTestId("location")).toHaveTextContent("/leads/importar?step=etl");
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
});
