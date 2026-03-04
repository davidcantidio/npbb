import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import LeadImportPage from "../LeadImportPage";
import { useAuth } from "../../../store/auth";
import {
  createLeadAlias,
  listLeads,
  listReferenciaCidades,
  listReferenciaEstados,
  listReferenciaEventos,
  listReferenciaGeneros,
  previewLeadImportEtl,
  commitLeadImportEtl,
  previewLeadImport,
  runLeadImport,
  validateLeadMapping,
} from "../../../services/leads_import";

vi.mock("../../../store/auth", () => ({ useAuth: vi.fn() }));

vi.mock("../../../services/leads_import", () => ({
  previewLeadImport: vi.fn(),
  previewLeadImportEtl: vi.fn(),
  commitLeadImportEtl: vi.fn(),
  validateLeadMapping: vi.fn(),
  runLeadImport: vi.fn(),
  listReferenciaEventos: vi.fn(),
  listReferenciaCidades: vi.fn(),
  listReferenciaEstados: vi.fn(),
  listReferenciaGeneros: vi.fn(),
  listLeads: vi.fn(),
  createLeadAlias: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);
const mockedPreviewLeadImport = vi.mocked(previewLeadImport);
const mockedPreviewLeadImportEtl = vi.mocked(previewLeadImportEtl);
const mockedCommitLeadImportEtl = vi.mocked(commitLeadImportEtl);
const mockedValidateLeadMapping = vi.mocked(validateLeadMapping);
const mockedRunLeadImport = vi.mocked(runLeadImport);
const mockedListReferenciaEventos = vi.mocked(listReferenciaEventos);
const mockedListReferenciaCidades = vi.mocked(listReferenciaCidades);
const mockedListReferenciaEstados = vi.mocked(listReferenciaEstados);
const mockedListReferenciaGeneros = vi.mocked(listReferenciaGeneros);
const mockedListLeads = vi.mocked(listLeads);
const mockedCreateLeadAlias = vi.mocked(createLeadAlias);

function setupDefaultMocks() {
  mockedUseAuth.mockReturnValue({
    token: "token",
    user: { id: 1, email: "demo@npbb.com.br", tipo_usuario: "admin" },
    loading: false,
    refreshing: false,
    error: null,
    refresh: vi.fn(),
    login: vi.fn(),
    logout: vi.fn(),
  });

  mockedListReferenciaEventos.mockResolvedValue([{ id: 55, nome: "Evento Alvo" }]);
  mockedListReferenciaCidades.mockResolvedValue(["Sao Paulo"]);
  mockedListReferenciaEstados.mockResolvedValue(["SP"]);
  mockedListReferenciaGeneros.mockResolvedValue(["Masculino"]);
  mockedListLeads.mockResolvedValue({ page: 1, page_size: 20, total: 0, items: [] });
  mockedValidateLeadMapping.mockResolvedValue({ ok: true });
  mockedRunLeadImport.mockResolvedValue({ filename: "ok.csv", created: 1, updated: 0, skipped: 0 });
  mockedPreviewLeadImportEtl.mockResolvedValue({
    session_token: "etl-1",
    total_rows: 0,
    valid_rows: 0,
    invalid_rows: 0,
    dq_report: [],
  });
  mockedCommitLeadImportEtl.mockResolvedValue({
    session_token: "etl-1",
    total_rows: 0,
    valid_rows: 0,
    invalid_rows: 0,
    created: 0,
    updated: 0,
    skipped: 0,
    errors: 0,
    strict: false,
    status: "committed",
    dq_report: [],
  });
  mockedCreateLeadAlias.mockResolvedValue({
    id: 1,
    tipo: "EVENTO",
    valor_origem: "Evento Alvo",
    valor_normalizado: "evento alvo",
    canonical_value: null,
    evento_id: 55,
  });
}

describe("LeadImportPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupDefaultMocks();
  });

  it("renders tabs with legacy as default", async () => {
    render(<LeadImportPage />);

    const legacyTab = await screen.findByRole("tab", { name: "Importacao" });
    const etlTab = await screen.findByRole("tab", { name: "Importacao avancada" });

    expect(legacyTab).toBeInTheDocument();
    expect(etlTab).toBeInTheDocument();
    expect(legacyTab).toHaveAttribute("aria-selected", "true");
  });

  it("blocks invalid file extension before preview request", async () => {
    mockedPreviewLeadImport.mockResolvedValue({
      filename: "valid.csv",
      headers: [],
      rows: [],
      delimiter: ";",
      start_index: 0,
      suggestions: [],
      samples_by_column: [],
    });

    const { container } = render(<LeadImportPage />);

    await waitFor(() => {
      expect(mockedListLeads).toHaveBeenCalled();
    });

    const input = container.querySelector('input[type="file"]') as HTMLInputElement;
    const user = userEvent.setup();
    const invalidFile = new File(["invalid"], "leads.csv", { type: "text/plain" });

    await user.upload(input, invalidFile);

    expect(mockedPreviewLeadImport).not.toHaveBeenCalled();
    expect(await screen.findByText("Tipo MIME nao suportado para importacao.")).toBeInTheDocument();
  });

  it("blocks double submit while import is in progress", async () => {
    mockedPreviewLeadImport.mockResolvedValue({
      filename: "valid.csv",
      headers: ["Email", "CPF"],
      rows: [["a@a.com", "12345678901"]],
      delimiter: ";",
      start_index: 0,
      suggestions: [
        { coluna: "Email", campo: "email", confianca: 1 },
        { coluna: "CPF", campo: "cpf", confianca: 1 },
      ],
      samples_by_column: [["a@a.com"], ["12345678901"]],
    });

    let resolveValidate!: (value: { ok: boolean }) => void;
    const validatePromise = new Promise<{ ok: boolean }>((resolve) => {
      resolveValidate = (value) => resolve(value);
    });
    mockedValidateLeadMapping.mockReturnValueOnce(validatePromise);

    const { container } = render(<LeadImportPage />);
    const user = userEvent.setup();

    const input = container.querySelector('input[type="file"]') as HTMLInputElement;
    await user.upload(input, new File(["x"], "leads.csv", { type: "text/csv" }));

    const importButton = await screen.findByRole("button", { name: "Importar" });
    fireEvent.click(importButton);

    await waitFor(() => {
      expect(importButton).toBeDisabled();
    });

    fireEvent.click(importButton);

    resolveValidate({ ok: true });

    await waitFor(() => {
      expect(mockedRunLeadImport).toHaveBeenCalledTimes(1);
    });
  });

  it("shows non-blocking alias warning when alias persistence fails", async () => {
    mockedPreviewLeadImport.mockResolvedValue({
      filename: "valid.csv",
      headers: ["Evento"],
      rows: [["Evento Alvo"]],
      delimiter: ";",
      start_index: 0,
      suggestions: [{ coluna: "Evento", campo: "evento_nome", confianca: 1 }],
      samples_by_column: [["Evento Alvo"]],
    });

    mockedCreateLeadAlias.mockRejectedValueOnce(new Error("alias-failed"));

    const { container } = render(<LeadImportPage />);
    const user = userEvent.setup();

    const input = container.querySelector('input[type="file"]') as HTMLInputElement;
    await user.upload(input, new File(["x"], "leads.csv", { type: "text/csv" }));

    await user.click(await screen.findByRole("button", { name: "Importar" }));

    expect(
      await screen.findByText(/correspondencia\(s\) de alias nao foram salvas/i),
    ).toBeInTheDocument();

    expect(await screen.findByText("Importacao concluida")).toBeInTheDocument();
  });
});
