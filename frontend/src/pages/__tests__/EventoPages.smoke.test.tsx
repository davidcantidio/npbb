import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import EventsList from "../EventsList";
import EventLeadFormConfig from "../EventLeadFormConfig";
import EventGamificacao from "../EventGamificacao";
import EventAtivacoes from "../EventAtivacoes";
import EventQuestionario from "../EventQuestionario";
import { useAuth } from "../../store/auth";
import {
  createEventoAtivacao,
  createEventoGamificacao,
  getEvento,
  getEventoFormConfig,
  getEventoQuestionario,
  getFormularioCamposPossiveis,
  listDiretorias,
  listEventoAtivacoes,
  listEventoGamificacoes,
  listEventos,
  listFormularioTemplates,
  listStatusEvento,
  updateEvento,
  updateEventoFormConfig,
  updateEventoQuestionario,
} from "../../services/eventos";
import { listAgencias } from "../../services/agencias";
import { getLandingByEvento } from "../../services/landing_public";

vi.mock("../../store/auth", () => ({ useAuth: vi.fn() }));
vi.mock("../../services/agencias", () => ({ listAgencias: vi.fn() }));
vi.mock("../../services/landing_public", () => ({ getLandingByEvento: vi.fn() }));
vi.mock("../../services/eventos", () => ({
  createEventoAtivacao: vi.fn(),
  createEventoGamificacao: vi.fn(),
  deleteAtivacao: vi.fn(),
  deleteGamificacao: vi.fn(),
  exportEventosCsv: vi.fn(),
  getEvento: vi.fn(),
  getEventoFormConfig: vi.fn(),
  getEventoQuestionario: vi.fn(),
  getFormularioCamposPossiveis: vi.fn(),
  importEventosCsv: vi.fn(),
  listDiretorias: vi.fn(),
  listEventoAtivacoes: vi.fn(),
  listEventoGamificacoes: vi.fn(),
  listEventos: vi.fn(),
  listFormularioTemplates: vi.fn(),
  listStatusEvento: vi.fn(),
  updateEvento: vi.fn(),
  updateEventoFormConfig: vi.fn(),
  updateEventoQuestionario: vi.fn(),
  updateGamificacao: vi.fn(),
}));
vi.mock("../../components/eventos/EventoRow", () => ({
  EventoRow: ({ item }: { item: { nome: string } }) => (
    <tr>
      <td>{item.nome}</td>
    </tr>
  ),
}));

const mockedUseAuth = vi.mocked(useAuth);
const mockedListAgencias = vi.mocked(listAgencias);
const mockedListDiretorias = vi.mocked(listDiretorias);
const mockedListStatusEvento = vi.mocked(listStatusEvento);
const mockedListEventos = vi.mocked(listEventos);
const mockedUpdateEvento = vi.mocked(updateEvento);
const mockedGetEventoFormConfig = vi.mocked(getEventoFormConfig);
const mockedGetFormularioCamposPossiveis = vi.mocked(getFormularioCamposPossiveis);
const mockedListFormularioTemplates = vi.mocked(listFormularioTemplates);
const mockedUpdateEventoFormConfig = vi.mocked(updateEventoFormConfig);
const mockedGetEvento = vi.mocked(getEvento);
const mockedListEventoGamificacoes = vi.mocked(listEventoGamificacoes);
const mockedCreateEventoGamificacao = vi.mocked(createEventoGamificacao);
const mockedListEventoAtivacoes = vi.mocked(listEventoAtivacoes);
const mockedCreateEventoAtivacao = vi.mocked(createEventoAtivacao);
const mockedGetEventoQuestionario = vi.mocked(getEventoQuestionario);
const mockedUpdateEventoQuestionario = vi.mocked(updateEventoQuestionario);
const mockedGetLandingByEvento = vi.mocked(getLandingByEvento);

describe("Evento pages smoke", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedUseAuth.mockReturnValue({
      token: "token",
      user: { id: 1, email: "qa@npbb.com.br", tipo_usuario: "npbb", agencia_id: null },
      loading: false,
      refreshing: false,
      error: null,
      refresh: vi.fn(),
      login: vi.fn(),
      logout: vi.fn(),
    });

    mockedListAgencias.mockResolvedValue([] as never);
    mockedListDiretorias.mockResolvedValue([{ id: 1, nome: "Dir 1" }] as never);
    mockedListStatusEvento.mockResolvedValue([{ id: 1, nome: "Previsto" }] as never);
    mockedListEventos.mockResolvedValue({
      total: 1,
      items: [
        {
          id: 10,
          nome: "Evento QA",
          cidade: "Brasilia",
          estado: "DF",
          status_id: 1,
          agencia_id: null,
          diretoria_id: 1,
          data_inicio_prevista: "2026-03-01",
          data_fim_prevista: "2026-03-02",
          concorrencia: false,
          investimento: null,
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
          qr_code_url: null,
          external_project_code: null,
          data_inicio_realizada: null,
          data_fim_realizada: null,
          data_health: null,
        },
      ],
    } as never);
    mockedUpdateEvento.mockResolvedValue({ id: 10 } as never);

    mockedGetEvento.mockResolvedValue({ id: 1, nome: "Evento QA" } as never);
    mockedGetLandingByEvento.mockResolvedValue({
      ativacao_id: null,
      evento: {
        id: 1,
        nome: "Evento QA",
        descricao: "Descricao completa do evento QA.",
        descricao_curta: "Resumo do evento QA.",
        data_inicio: "2026-03-01",
        data_fim: "2026-03-02",
        cidade: "Brasilia",
        estado: "DF",
      },
      template: {
        categoria: "evento_cultural",
        tema: "Cultural",
        mood: "Sofisticado, acessivel e inspirador.",
        cta_text: "Quero conhecer",
        color_primary: "#00EBD0",
        color_secondary: "#BDB6FF",
        color_background: "#F7FBFB",
        color_text: "#111827",
        hero_layout: "editorial",
        cta_variant: "outlined",
        graphics_style: "organic",
        tone_of_voice: "attention",
      },
      formulario: {
        event_id: 1,
        ativacao_id: null,
        submit_url: "/landing/eventos/1/submit",
        campos: [
          {
            key: "nome",
            label: "Nome",
            input_type: "text",
            required: true,
            autocomplete: "name",
            placeholder: "Como voce gostaria de ser chamado?",
          },
          {
            key: "email",
            label: "Email",
            input_type: "email",
            required: true,
            autocomplete: "email",
            placeholder: "voce@exemplo.com",
          },
        ],
        campos_obrigatorios: ["nome", "email"],
        campos_opcionais: [],
        mensagem_sucesso: "Cadastro confirmado.",
        lgpd_texto: "Ao enviar seus dados, voce concorda com o tratamento das informacoes.",
        privacy_policy_url: "https://www.bb.com.br/site/privacidade-e-lgpd/",
      },
      marca: {
        tagline: "Banco do Brasil. Pra tudo que voce imaginar.",
        versao_logo: "positivo",
        url_hero_image: "data:image/svg+xml;base64,PHN2Zy8+",
        hero_alt: "Imagem de destaque do evento Evento QA",
      },
      acesso: {
        landing_url: "http://localhost:5173/landing/eventos/1",
        qr_code_url: null,
        url_promotor: "http://localhost:5173/landing/eventos/1",
      },
    } as never);
    mockedListEventoGamificacoes.mockResolvedValue([] as never);
    mockedCreateEventoGamificacao.mockResolvedValue({
      id: 1,
      evento_id: 1,
      nome: "Gami 1",
      descricao: "",
      premio: "",
      titulo_feedback: "",
      texto_feedback: "",
    } as never);
    mockedListEventoAtivacoes.mockResolvedValue([] as never);
    mockedCreateEventoAtivacao.mockResolvedValue({
      id: 1,
      evento_id: 1,
      nome: "Ativ 1",
      descricao: null,
      mensagem_qrcode: null,
      gamificacao_id: null,
      redireciona_pesquisa: false,
      checkin_unico: false,
      termo_uso: false,
      gera_cupom: false,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    } as never);

    mockedGetEventoFormConfig.mockResolvedValue({
      evento_id: 1,
      template_id: null,
      campos: [{ nome_campo: "Email", obrigatorio: true, ordem: 0 }],
      urls: {
        url_landing: "http://localhost:5173/landing",
        url_checkin_sem_qr: "http://localhost:5173/checkin",
        url_questionario: "http://localhost:5173/questionario",
        url_api: "http://localhost:8000/docs",
      },
    } as never);
    mockedGetFormularioCamposPossiveis.mockResolvedValue(["Email", "Nome"] as never);
    mockedListFormularioTemplates.mockResolvedValue([] as never);
    mockedUpdateEventoFormConfig.mockResolvedValue({
      evento_id: 1,
      template_id: null,
      campos: [{ nome_campo: "Email", obrigatorio: true, ordem: 0 }],
      urls: {
        url_landing: "http://localhost:5173/landing",
        url_checkin_sem_qr: "http://localhost:5173/checkin",
        url_questionario: "http://localhost:5173/questionario",
        url_api: "http://localhost:8000/docs",
      },
    } as never);

    mockedGetEventoQuestionario.mockResolvedValue({
      evento_id: 1,
      paginas: [
        {
          id: 11,
          ordem: 0,
          titulo: "Pagina 1",
          descricao: "",
          perguntas: [
            {
              id: 21,
              ordem: 0,
              tipo: "aberta_texto_simples",
              texto: "Pergunta 1",
              obrigatoria: true,
              opcoes: [],
            },
          ],
        },
      ],
    } as never);
    mockedUpdateEventoQuestionario.mockResolvedValue({
      evento_id: 1,
      paginas: [],
    } as never);
  });

  it("renders EventsList with loaded data", async () => {
    render(
      <MemoryRouter initialEntries={["/eventos"]}>
        <Routes>
          <Route path="/eventos" element={<EventsList />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Evento QA")).toBeInTheDocument();
    expect(mockedListEventos).toHaveBeenCalled();
  });

  it("updates EventLeadFormConfig and keeps copy aligned with save CTA", async () => {
    render(
      <MemoryRouter initialEntries={["/eventos/1/formulario-lead"]}>
        <Routes>
          <Route path="/eventos/:id/formulario-lead" element={<EventLeadFormConfig />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText(/clicar em "Salvar"\./i)).toBeInTheDocument();
    expect(screen.queryByText(/Salvar e continuar/i)).not.toBeInTheDocument();
    expect(await screen.findByText(/Preview fiel ao contrato real da landing/i)).toBeInTheDocument();
    expect(screen.getByText(/Checklist minimo da ativacao/i)).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Salvar" }));
    await waitFor(() => expect(mockedUpdateEventoFormConfig).toHaveBeenCalledTimes(1));
    expect(mockedGetLandingByEvento).toHaveBeenCalledWith(1);
  });

  it("adds a gamificacao from EventGamificacao page", async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter initialEntries={["/eventos/1/gamificacao"]}>
        <Routes>
          <Route path="/eventos/:id/gamificacao" element={<EventGamificacao />} />
        </Routes>
      </MemoryRouter>,
    );

    await screen.findByLabelText(/Nome da gamifica/i);
    const textboxes = screen.getAllByRole("textbox");
    for (const [index, input] of textboxes.entries()) {
      await user.type(input, `valor-${index + 1}`);
    }
    const submitButton = screen.getByRole("button", { name: /Adicionar gamifica/i });
    expect(submitButton).toBeEnabled();
    await user.click(submitButton);

    await waitFor(() => expect(mockedCreateEventoGamificacao).toHaveBeenCalledTimes(1));
  });

  it("adds an ativacao from EventAtivacoes page", async () => {
    render(
      <MemoryRouter initialEntries={["/eventos/1/ativacoes"]}>
        <Routes>
          <Route path="/eventos/:id/ativacoes" element={<EventAtivacoes />} />
        </Routes>
      </MemoryRouter>,
    );

    const nomeInput = await screen.findByLabelText(/Nome da ativ/i);
    await userEvent.type(nomeInput, "Nova ativacao");
    await userEvent.click(screen.getByRole("button", { name: /Adicionar ativa/i }));

    await waitFor(() => expect(mockedCreateEventoAtivacao).toHaveBeenCalledTimes(1));
  });

  it("saves questionnaire from EventQuestionario page", async () => {
    render(
      <MemoryRouter initialEntries={["/eventos/1/questionario"]}>
        <Routes>
          <Route path="/eventos/:id/questionario" element={<EventQuestionario />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText(/Estrutura do questionario/i)).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Salvar" }));

    await waitFor(() => expect(mockedUpdateEventoQuestionario).toHaveBeenCalledTimes(1));
  });
});
