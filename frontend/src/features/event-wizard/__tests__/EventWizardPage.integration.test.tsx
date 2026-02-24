import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import EventWizardPage from "../EventWizardPage";
import { useAuth } from "../../../store/auth";
import { listAgencias } from "../../../services/agencias";
import {
  createEvento,
  createTag,
  getEvento,
  listDiretorias,
  listDivisoesDemandantes,
  listTiposEvento,
  listTags,
  listTerritorios,
  listSubtiposEvento,
  updateEvento,
} from "../../../services/eventos";

vi.mock("../../../store/auth", () => ({ useAuth: vi.fn() }));
vi.mock("../../../services/agencias", () => ({ listAgencias: vi.fn() }));
vi.mock("../../../services/eventos", () => ({
  createEvento: vi.fn(),
  createTag: vi.fn(),
  getEvento: vi.fn(),
  listDiretorias: vi.fn(),
  listDivisoesDemandantes: vi.fn(),
  listTiposEvento: vi.fn(),
  listTags: vi.fn(),
  listTerritorios: vi.fn(),
  listSubtiposEvento: vi.fn(),
  updateEvento: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);
const mockedListAgencias = vi.mocked(listAgencias);
const mockedCreateEvento = vi.mocked(createEvento);
const mockedCreateTag = vi.mocked(createTag);
const mockedGetEvento = vi.mocked(getEvento);
const mockedListDiretorias = vi.mocked(listDiretorias);
const mockedListDivisoesDemandantes = vi.mocked(listDivisoesDemandantes);
const mockedListTiposEvento = vi.mocked(listTiposEvento);
const mockedListTags = vi.mocked(listTags);
const mockedListTerritorios = vi.mocked(listTerritorios);
const mockedListSubtiposEvento = vi.mocked(listSubtiposEvento);
const mockedUpdateEvento = vi.mocked(updateEvento);

describe("EventWizardPage integration", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    mockedUseAuth.mockReturnValue({
      token: "token",
      user: { id: 1, email: "demo@npbb.com.br", tipo_usuario: "admin", agencia_id: null },
      loading: false,
      refreshing: false,
      error: null,
      refresh: vi.fn(),
      login: vi.fn(),
      logout: vi.fn(),
    });

    mockedListAgencias.mockResolvedValue([] as never);
    mockedListDiretorias.mockResolvedValue([{ id: 1, nome: "Dir 1" }] as never);
    mockedListDivisoesDemandantes.mockResolvedValue([{ id: 1, nome: "Div 1" }] as never);
    mockedListTiposEvento.mockResolvedValue([{ id: 1, nome: "Tipo 1" }] as never);
    mockedListTags.mockResolvedValue([{ id: 1, nome: "Tag 1" }] as never);
    mockedListTerritorios.mockResolvedValue([{ id: 1, nome: "Territorio 1" }] as never);
    mockedListSubtiposEvento.mockResolvedValue([{ id: 1, tipo_id: 1, nome: "Subtipo 1" }] as never);
    mockedCreateTag.mockResolvedValue({ id: 1, nome: "Tag 1" } as never);
    mockedGetEvento.mockResolvedValue({} as never);
    mockedUpdateEvento.mockResolvedValue({ id: 1 } as never);
    mockedCreateEvento.mockResolvedValue({ id: 123 } as never);
  });

  function renderWizard(initialEntry: string) {
    return render(
      <MemoryRouter initialEntries={[initialEntry]}>
        <Routes>
          <Route path="/eventos/novo" element={<EventWizardPage />} />
          <Route path="/eventos/:id/editar" element={<EventWizardPage />} />
          <Route path="/eventos/:id/formulario-lead" element={<div>Lead form step</div>} />
        </Routes>
      </MemoryRouter>,
    );
  }

  it("does not submit when Enter is pressed on classification autocomplete", async () => {
    renderWizard("/eventos/novo?focus=diretoria_id");

    const diretoriaInput = await screen.findByLabelText("Diretoria");
    fireEvent.keyDown(diretoriaInput, { key: "Enter", code: "Enter" });

    expect(mockedCreateEvento).not.toHaveBeenCalled();
    expect(screen.queryByText("Lead form step")).not.toBeInTheDocument();
  });

  it("navigates to lead step only after explicit click on 'Salvar e continuar'", async () => {
    mockedGetEvento.mockResolvedValueOnce({
      id: 55,
      agencia_id: 10,
      concorrencia: false,
      nome: "Evento carregado",
      descricao: "",
      estado: "SP",
      cidade: "Sao Paulo",
      data_inicio_prevista: "2026-03-01",
      data_fim_prevista: "2026-03-02",
      investimento: "1000",
      diretoria_id: 1,
      divisao_demandante_id: 1,
      tipo_id: 1,
      subtipo_id: 1,
      tag_ids: [1],
      territorio_ids: [1],
    } as never);

    renderWizard("/eventos/55/editar?focus=diretoria_id");
    const user = userEvent.setup();
    await screen.findByLabelText("Diretoria");
    expect(screen.queryByText("Lead form step")).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Salvar e continuar" }));

    await waitFor(() => {
      expect(mockedUpdateEvento).toHaveBeenCalledTimes(1);
      expect(screen.getByText("Lead form step")).toBeInTheDocument();
    });
  });
});

