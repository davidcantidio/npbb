import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import LeadImportPage from "../LeadImportPage";
import { useAuth } from "../../../store/auth";
import {
  createLeadBatch,
  getLeadBatchPreview,
  listLeads,
} from "../../../services/leads_import";

vi.mock("../../../store/auth", () => ({ useAuth: vi.fn() }));

vi.mock("../../../services/leads_import", () => ({
  createLeadBatch: vi.fn(),
  getLeadBatchPreview: vi.fn(),
  listLeads: vi.fn(),
  // keep legacy exports for other consumers that still import them
  previewLeadImport: vi.fn(),
  previewLeadImportEtl: vi.fn(),
  commitLeadImportEtl: vi.fn(),
  validateLeadMapping: vi.fn(),
  runLeadImport: vi.fn(),
  listReferenciaEventos: vi.fn(),
  listReferenciaCidades: vi.fn(),
  listReferenciaEstados: vi.fn(),
  listReferenciaGeneros: vi.fn(),
  createLeadAlias: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);
const mockedCreateLeadBatch = vi.mocked(createLeadBatch);
const mockedGetLeadBatchPreview = vi.mocked(getLeadBatchPreview);
const mockedListLeads = vi.mocked(listLeads);

function setupDefaultMocks() {
  mockedUseAuth.mockReturnValue({
    token: "test-token",
    user: { id: 1, email: "demo@npbb.com.br", tipo_usuario: "admin" },
    loading: false,
    refreshing: false,
    error: null,
    refresh: vi.fn(),
    login: vi.fn(),
    logout: vi.fn(),
  });
  mockedListLeads.mockResolvedValue({ page: 1, page_size: 20, total: 0, items: [] });
}

describe("LeadImportPage — Bronze Stepper", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupDefaultMocks();
  });

  it("renders the import page with step 1 visible", async () => {
    render(<LeadImportPage />);

    expect(await screen.findByText("Importar arquivo")).toBeInTheDocument();
    expect(screen.getByText("Metadados e Upload")).toBeInTheDocument();
    expect(screen.getByText("Preview de Colunas")).toBeInTheDocument();
    expect(screen.getByText("Plataforma de origem")).toBeInTheDocument();
    expect(screen.getByText("Informações de envio")).toBeInTheDocument();
  });

  it("does NOT render the old 'Importacao avancada' tab", async () => {
    render(<LeadImportPage />);
    await waitFor(() => {
      expect(screen.queryByRole("tab", { name: /importacao avancada/i })).not.toBeInTheDocument();
    });
  });

  it("shows validation error when required fields are missing on submit", async () => {
    render(<LeadImportPage />);
    const user = userEvent.setup();

    const submitButton = screen.getByRole("button", { name: "Enviar arquivo" });
    await user.click(submitButton);

    expect(await screen.findByText("Selecione a plataforma de origem.")).toBeInTheDocument();
    expect(mockedCreateLeadBatch).not.toHaveBeenCalled();
  });

  it("shows error when file is missing but platform and date are filled", async () => {
    render(<LeadImportPage />);
    const user = userEvent.setup();

    const platformSelect = screen.getByRole("combobox", { name: /plataforma de origem/i });
    await user.click(platformSelect);
    const emailOption = await screen.findByRole("option", { name: "E-mail" });
    await user.click(emailOption);

    fireEvent.change(screen.getByLabelText(/data de envio/i), { target: { value: "2026-01-15" } });

    await user.click(screen.getByRole("button", { name: "Enviar arquivo" }));

    expect(await screen.findByText("Selecione um arquivo CSV ou XLSX.")).toBeInTheDocument();
    expect(mockedCreateLeadBatch).not.toHaveBeenCalled();
  });

  it("advances to step 2 on successful upload showing column preview", async () => {
    mockedCreateLeadBatch.mockResolvedValue({
      batch_id: "batch-uuid-123",
      stage: "bronze",
      pipeline_status: "pending",
    });
    mockedGetLeadBatchPreview.mockResolvedValue({
      batch_id: "batch-uuid-123",
      nome_arquivo: "leads.csv",
      colunas: ["nome", "email", "cpf"],
      amostras: [
        ["Joao Silva", "joao@exemplo.com", "12345678901"],
        ["Maria Souza", "maria@exemplo.com", "98765432100"],
      ],
    });

    const { container } = render(<LeadImportPage />);
    const user = userEvent.setup();

    const platformSelect = screen.getByRole("combobox", { name: /plataforma de origem/i });
    await user.click(platformSelect);
    const emailOption = await screen.findByRole("option", { name: "E-mail" });
    await user.click(emailOption);

    fireEvent.change(screen.getByLabelText(/data de envio/i), { target: { value: "2026-01-15" } });

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    const csvFile = new File(["nome,email,cpf\nJoao Silva,joao@exemplo.com,12345678901"], "leads.csv", {
      type: "text/csv",
    });
    fireEvent.change(fileInput, { target: { files: [csvFile] } });

    await user.click(screen.getByRole("button", { name: "Enviar arquivo" }));

    await waitFor(() => {
      expect(mockedCreateLeadBatch).toHaveBeenCalledWith("test-token", {
        file: csvFile,
        plataforma_origem: "email",
        data_envio: expect.any(String),
      });
    });

    expect(await screen.findByText(/Preview — leads\.csv/)).toBeInTheDocument();
    expect(screen.getByText("nome")).toBeInTheDocument();
    expect(screen.getByText("email")).toBeInTheDocument();
    expect(screen.getByText("cpf")).toBeInTheDocument();
    expect(screen.getByText("batch-uuid-123")).toBeInTheDocument();
    expect(
      screen.getByText("Arquivo salvo com sucesso na camada Bronze. O mapeamento de colunas estará disponível na fase Silver."),
    ).toBeInTheDocument();
  });

  it("shows API error inline when createLeadBatch fails", async () => {
    mockedCreateLeadBatch.mockRejectedValue(new Error("Servidor indisponivel"));

    const { container } = render(<LeadImportPage />);
    const user = userEvent.setup();

    const platformSelect = screen.getByRole("combobox", { name: /plataforma de origem/i });
    await user.click(platformSelect);
    const emailOption = await screen.findByRole("option", { name: "E-mail" });
    await user.click(emailOption);

    fireEvent.change(screen.getByLabelText(/data de envio/i), { target: { value: "2026-01-15" } });

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, {
      target: {
        files: [new File(["x"], "leads.csv", { type: "text/csv" })],
      },
    });

    await user.click(screen.getByRole("button", { name: "Enviar arquivo" }));

    expect(await screen.findByText("Servidor indisponivel")).toBeInTheDocument();
    expect(screen.queryByText(/Preview — leads\.csv/)).not.toBeInTheDocument();
  });

  it("resets stepper when 'Importar outro arquivo' is clicked", async () => {
    mockedCreateLeadBatch.mockResolvedValue({
      batch_id: "batch-uuid-456",
      stage: "bronze",
      pipeline_status: "pending",
    });
    mockedGetLeadBatchPreview.mockResolvedValue({
      batch_id: "batch-uuid-456",
      nome_arquivo: "dados.xlsx",
      colunas: ["A", "B"],
      amostras: [["val1", "val2"]],
    });

    const { container } = render(<LeadImportPage />);
    const user = userEvent.setup();

    const platformSelect = screen.getByRole("combobox", { name: /plataforma de origem/i });
    await user.click(platformSelect);
    const whatsappOption = await screen.findByRole("option", { name: "WhatsApp" });
    await user.click(whatsappOption);

    fireEvent.change(screen.getByLabelText(/data de envio/i), { target: { value: "2026-02-01" } });

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, {
      target: {
        files: [new File(["x"], "dados.xlsx", { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" })],
      },
    });

    await user.click(screen.getByRole("button", { name: "Enviar arquivo" }));

    await screen.findByText(/Preview — dados\.xlsx/);

    await user.click(screen.getByRole("button", { name: "Importar outro arquivo" }));

    expect(screen.getByText("Informações de envio")).toBeInTheDocument();
    expect(screen.queryByText(/Preview — dados\.xlsx/)).not.toBeInTheDocument();
  });
});
