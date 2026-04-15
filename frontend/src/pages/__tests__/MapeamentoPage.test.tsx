import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";

import MapeamentoPage from "../leads/MapeamentoPage";
import { useAuth } from "../../store/auth";
import {
  getLeadBatchColunas,
  listReferenciaEventos,
  mapearLeadBatch,
} from "../../services/leads_import";

vi.mock("../../store/auth", () => ({ useAuth: vi.fn() }));
vi.mock("../../services/leads_import", () => ({
  getLeadBatchColunas: vi.fn(),
  listReferenciaEventos: vi.fn(),
  mapearLeadBatch: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);
const mockedGetLeadBatchColunas = vi.mocked(getLeadBatchColunas);
const mockedListReferenciaEventos = vi.mocked(listReferenciaEventos);
const mockedMapearLeadBatch = vi.mocked(mapearLeadBatch);
const EVENTOS_LOAD_ERROR = "Nao foi possivel carregar os eventos. Tente recarregar a pagina.";

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
