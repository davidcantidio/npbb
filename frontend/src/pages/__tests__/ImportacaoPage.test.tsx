import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";

import ImportacaoPage from "../leads/ImportacaoPage";
import { useAuth } from "../../store/auth";
import { createLeadBatch, getLeadBatchPreview } from "../../services/leads_import";

vi.mock("../../store/auth", () => ({ useAuth: vi.fn() }));
vi.mock("../../services/leads_import", () => ({
  createLeadBatch: vi.fn(),
  getLeadBatchPreview: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);
const mockedCreateLeadBatch = vi.mocked(createLeadBatch);
const mockedGetLeadBatchPreview = vi.mocked(getLeadBatchPreview);

function MapeamentoProbe() {
  const location = useLocation();
  return <div>{`Mapeamento route ${location.search}`}</div>;
}

function renderImportacaoPage() {
  return render(
    <MemoryRouter initialEntries={["/leads/importar"]}>
      <Routes>
        <Route path="/leads/importar" element={<ImportacaoPage />} />
        <Route path="/leads/mapeamento" element={<MapeamentoProbe />} />
      </Routes>
    </MemoryRouter>,
  );
}

function createCsvFile() {
  return new File(["nome,email\nAlice,alice@npbb.com.br"], "leads.csv", { type: "text/csv" });
}

describe("ImportacaoPage", () => {
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
  });

  it("renders the active Bronze stepper with the current date prefilled", () => {
    renderImportacaoPage();

    expect(screen.getByText("Importacao de Leads")).toBeInTheDocument();
    expect(screen.getByText("Metadados e upload")).toBeInTheDocument();
    expect(screen.getByText("Preview de colunas")).toBeInTheDocument();
    expect(screen.getByDisplayValue("demo@npbb.com.br")).toBeInTheDocument();
    expect(screen.getByDisplayValue(new Date().toISOString().slice(0, 10))).toBeInTheDocument();
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

  it("uploads a batch and shows the preview for the current Bronze flow", async () => {
    mockedCreateLeadBatch.mockResolvedValue({
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

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    const csvFile = createCsvFile();
    fireEvent.change(fileInput, { target: { files: [csvFile] } });

    await user.click(screen.getByRole("button", { name: "Enviar para Bronze" }));

    await waitFor(() => {
      expect(mockedCreateLeadBatch).toHaveBeenCalledWith("token-123", {
        quem_enviou: "demo@npbb.com.br",
        plataforma_origem: "email",
        data_envio: expectedDate,
        file: csvFile,
      });
    });
    await waitFor(() => {
      expect(mockedGetLeadBatchPreview).toHaveBeenCalledWith("token-123", 10);
    });

    expect(await screen.findByText("Preview do lote #10")).toBeInTheDocument();
    expect(screen.getByText("Colunas detectadas: 2 | Linhas de amostra: 1 de 1")).toBeInTheDocument();
    expect(screen.getAllByText("nome").length).toBeGreaterThan(0);
    expect(screen.getAllByText("email").length).toBeGreaterThan(0);
    expect(screen.getByText("Alice")).toBeInTheDocument();
    expect(screen.getByText("alice@npbb.com.br")).toBeInTheDocument();
  });

  it("shows the API error inline when batch creation fails", async () => {
    mockedCreateLeadBatch.mockRejectedValue(new Error("Servidor indisponivel"));

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    await user.click(screen.getByRole("combobox", { name: /plataforma de origem/i }));
    await user.click(await screen.findByRole("option", { name: "email" }));

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [createCsvFile()] } });

    await user.click(screen.getByRole("button", { name: "Enviar para Bronze" }));

    expect(await screen.findByText("Servidor indisponivel")).toBeInTheDocument();
    expect(mockedGetLeadBatchPreview).not.toHaveBeenCalled();
  });

  it("navigates to mapping after a successful preview", async () => {
    mockedCreateLeadBatch.mockResolvedValue({
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
    });
    mockedGetLeadBatchPreview.mockResolvedValue({
      headers: ["nome", "email"],
      rows: [["Alice", "alice@npbb.com.br"]],
      total_rows: 1,
    });

    const { container } = renderImportacaoPage();
    const user = userEvent.setup();

    await user.click(screen.getByRole("combobox", { name: /plataforma de origem/i }));
    await user.click(await screen.findByRole("option", { name: "email" }));

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [createCsvFile()] } });

    await user.click(screen.getByRole("button", { name: "Enviar para Bronze" }));
    await screen.findByText("Preview do lote #10");

    await user.click(screen.getByRole("button", { name: "Avancar para Mapeamento" }));

    expect(await screen.findByText("Mapeamento route ?batch_id=10")).toBeInTheDocument();
  });
});
