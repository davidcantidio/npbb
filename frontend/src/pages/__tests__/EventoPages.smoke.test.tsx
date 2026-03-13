import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
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
  getLandingAnalytics,
  getLandingCustomizationAudit,
  getEventoQuestionario,
  getFormularioCamposPossiveis,
  listDiretorias,
  listEventoAtivacoes,
  listEventoGamificacoes,
  listEventos,
  listFormularioTemplates,
  listStatusEvento,
  updateAtivacao,
  updateEvento,
  updateEventoFormConfig,
  updateEventoQuestionario,
} from "../../services/eventos";
import { listAgencias } from "../../services/agencias";
import { API_BASE_URL } from "../../services/http";
import { previewEventoLanding, type LandingPageData } from "../../services/landing_public";

vi.mock("../../store/auth", () => ({ useAuth: vi.fn() }));
vi.mock("../../services/agencias", () => ({ listAgencias: vi.fn() }));
vi.mock("../../services/landing_public", () => ({ previewEventoLanding: vi.fn() }));
vi.mock("../../services/eventos", () => ({
  createEventoAtivacao: vi.fn(),
  createEventoGamificacao: vi.fn(),
  deleteAtivacao: vi.fn(),
  deleteGamificacao: vi.fn(),
  exportEventosCsv: vi.fn(),
  getEvento: vi.fn(),
  getLandingAnalytics: vi.fn(),
  getLandingCustomizationAudit: vi.fn(),
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
  updateAtivacao: vi.fn(),
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
const mockedGetLandingAnalytics = vi.mocked(getLandingAnalytics);
const mockedGetLandingCustomizationAudit = vi.mocked(getLandingCustomizationAudit);
const mockedListEventoGamificacoes = vi.mocked(listEventoGamificacoes);
const mockedCreateEventoGamificacao = vi.mocked(createEventoGamificacao);
const mockedListEventoAtivacoes = vi.mocked(listEventoAtivacoes);
const mockedCreateEventoAtivacao = vi.mocked(createEventoAtivacao);
const mockedUpdateAtivacao = vi.mocked(updateAtivacao);
const mockedGetEventoQuestionario = vi.mocked(getEventoQuestionario);
const mockedUpdateEventoQuestionario = vi.mocked(updateEventoQuestionario);
const mockedPreviewEventoLanding = vi.mocked(previewEventoLanding);

function createDeferred<T>() {
  let resolve!: (value: T | PromiseLike<T>) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return { promise, resolve, reject };
}

type LandingPreviewOverrides = {
  ativacao_id?: LandingPageData["ativacao_id"];
  ativacao?: LandingPageData["ativacao"];
  evento?: Partial<LandingPageData["evento"]>;
  template?: Partial<LandingPageData["template"]>;
  formulario?: Partial<LandingPageData["formulario"]>;
  marca?: Partial<LandingPageData["marca"]>;
  acesso?: Partial<LandingPageData["acesso"]>;
  gamificacoes?: LandingPageData["gamificacoes"];
  lead_reconhecido?: LandingPageData["lead_reconhecido"];
  lead_ja_converteu_nesta_ativacao?: LandingPageData["lead_ja_converteu_nesta_ativacao"];
  token?: LandingPageData["token"];
};

function createLandingPreviewPayload(overrides: LandingPreviewOverrides = {}): LandingPageData {
  return {
    ativacao_id: overrides.ativacao_id ?? null,
    ativacao: overrides.ativacao ?? null,
    evento: {
      id: 1,
      nome: "Evento QA",
      descricao: "Descricao completa do evento QA.",
      descricao_curta: "Resumo do evento QA.",
      data_inicio: "2026-03-01",
      data_fim: "2026-03-02",
      cidade: "Brasilia",
      estado: "DF",
      cta_personalizado: null,
      ...overrides.evento,
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
      cta_experiment_enabled: false,
      cta_variants: [],
      ...overrides.template,
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
      ...overrides.formulario,
    },
    marca: {
      tagline: "Banco do Brasil. Pra tudo que voce imaginar.",
      ...overrides.marca,
    },
    acesso: {
      landing_url: "http://localhost:5173/landing/eventos/1",
      qr_code_url: null,
      url_promotor: "http://localhost:5173/landing/eventos/1",
      ...overrides.acesso,
    },
    gamificacoes: overrides.gamificacoes ?? [],
    lead_reconhecido: overrides.lead_reconhecido ?? false,
    lead_ja_converteu_nesta_ativacao: overrides.lead_ja_converteu_nesta_ativacao ?? false,
    token: overrides.token ?? null,
  };
}

describe("Evento pages smoke", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

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
    mockedPreviewEventoLanding.mockResolvedValue(createLandingPreviewPayload() as never);
    mockedGetLandingAnalytics.mockResolvedValue([
      {
        event_id: 1,
        categoria: "evento_cultural",
        tema: "Cultural",
        page_views: 12,
        form_starts: 6,
        submit_attempts: 4,
        submit_successes: 3,
        conversion_rate: 0.25,
        variants: [],
      },
    ] as never);
    mockedGetLandingCustomizationAudit.mockResolvedValue([
      {
        id: 1,
        event_id: 1,
        field_name: "cta_personalizado",
        old_value: "Quero conhecer",
        new_value: "Quero receber novidades",
        changed_by_user_id: 1,
        created_at: "2026-03-06T10:00:00Z",
      },
    ] as never);
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
    mockedUpdateAtivacao.mockResolvedValue({
      id: 1,
      evento_id: 1,
      nome: "Ativ 1 atualizada",
      descricao: "Descricao atualizada",
      mensagem_qrcode: null,
      gamificacao_id: null,
      redireciona_pesquisa: false,
      checkin_unico: true,
      termo_uso: false,
      gera_cupom: false,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-02T00:00:00Z",
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

    expect(await screen.findByText(/preview atualiza em tempo real/i)).toBeInTheDocument();
    expect(screen.queryByText(/Salvar e continuar/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/Hero image URL/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/hero_image_url/i)).not.toBeInTheDocument();
    expect(
      screen.getByText(/O visual do fundo e determinado pelo template selecionado\./i),
    ).toBeInTheDocument();
    expect(await screen.findByText(/landing form-only publicada/i)).toBeInTheDocument();
    expect(screen.getByTestId("landing-preview-badge")).toBeInTheDocument();
    expect(await screen.findByText(/Analytics da landing/i)).toBeInTheDocument();
    expect(screen.getByText(/Auditoria de customizacao/i)).toBeInTheDocument();
    const previewHost = screen.getByTestId("event-lead-preview-host");
    expect(previewHost).toHaveStyle({
      position: "relative",
      overflow: "hidden",
    });
    expect(within(previewHost).getByTestId("full-page-background-root")).toHaveAttribute(
      "data-layer-mode",
      "embedded",
    );
    expect(within(previewHost).getByTestId("full-page-background-layer")).toHaveStyle({
      position: "absolute",
      inset: "0",
      width: "100%",
    });
    expect(within(previewHost).getByTestId("full-page-overlay-layer")).toHaveStyle({
      position: "absolute",
      pointerEvents: "none",
    });
    await waitFor(() =>
      expect(mockedPreviewEventoLanding).toHaveBeenCalledWith(
        "token",
        1,
        expect.objectContaining({
          template_id: null,
          template_override: null,
          cta_personalizado: null,
          descricao_curta: null,
          campos: [{ nome_campo: "Email", obrigatorio: true, ordem: 0 }],
        }),
        expect.objectContaining({ signal: expect.any(Object) }),
      ),
    );

    await userEvent.click(screen.getByRole("button", { name: "Salvar" }));
    await waitFor(() => expect(mockedUpdateEventoFormConfig).toHaveBeenCalledTimes(1));
    await waitFor(() =>
      expect(mockedUpdateEvento).toHaveBeenCalledWith("token", 1, {
        template_override: null,
        cta_personalizado: null,
        descricao_curta: null,
      }),
    );
    expect(mockedPreviewEventoLanding).toHaveBeenCalled();
  });

  it("auto-refreshes the preview when the selected theme changes", async () => {
    const user = userEvent.setup();
    mockedListFormularioTemplates.mockResolvedValue([{ id: 7, nome: "Surf" }] as never);
    mockedPreviewEventoLanding
      .mockResolvedValueOnce(createLandingPreviewPayload() as never)
      .mockResolvedValueOnce(
        createLandingPreviewPayload({
          template: {
            categoria: "esporte_radical",
            tema: "Radical",
            mood: "Alta energia, autenticidade e movimento.",
            cta_text: "Quero fazer parte",
            color_primary: "#FF6E91",
            color_secondary: "#FCFC30",
            color_background: "#FFF7FB",
            color_text: "#1F2937",
            hero_layout: "full-bleed",
            cta_variant: "gradient",
            graphics_style: "dynamic",
            tone_of_voice: "enthusiasm",
            cta_experiment_enabled: false,
            cta_variants: [],
          },
        }) as never,
      );

    render(
      <MemoryRouter initialEntries={["/eventos/1/formulario-lead"]}>
        <Routes>
          <Route path="/eventos/:id/formulario-lead" element={<EventLeadFormConfig />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByRole("button", { name: /quero conhecer/i })).toBeInTheDocument();

    const input = screen.getByLabelText(/^Tema$/i);
    await user.click(input);
    await user.type(input, "Surf");
    await user.keyboard("{ArrowDown}{Enter}");

    await waitFor(() =>
      expect(mockedPreviewEventoLanding).toHaveBeenLastCalledWith(
        "token",
        1,
        expect.objectContaining({ template_id: 7 }),
        expect.objectContaining({ signal: expect.any(Object) }),
      ),
    );
    expect(await screen.findByRole("button", { name: /quero fazer parte/i })).toBeInTheDocument();
  });

  it("auto-refreshes the preview when copy and active fields change", async () => {
    const user = userEvent.setup();
    mockedPreviewEventoLanding
      .mockResolvedValueOnce(createLandingPreviewPayload() as never)
      .mockResolvedValueOnce(
        createLandingPreviewPayload({
          evento: {
            cta_personalizado: "Receber novidades",
            descricao_curta: "Preview com Nome e Email.",
          },
          formulario: {
            campos: [
              {
                key: "email",
                label: "Email",
                input_type: "email",
                required: true,
                autocomplete: "email",
                placeholder: "voce@exemplo.com",
              },
              {
                key: "nome",
                label: "Nome",
                input_type: "text",
                required: true,
                autocomplete: "name",
                placeholder: "Como voce gostaria de ser chamado?",
              },
            ],
            campos_obrigatorios: ["email", "nome"],
            campos_opcionais: [],
          },
          template: {
            cta_text: "Receber novidades",
          },
        }) as never,
      );

    render(
      <MemoryRouter initialEntries={["/eventos/1/formulario-lead"]}>
        <Routes>
          <Route path="/eventos/:id/formulario-lead" element={<EventLeadFormConfig />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByRole("button", { name: /quero conhecer/i })).toBeInTheDocument();
    await user.type(screen.getByLabelText(/CTA personalizado/i), "Receber novidades");
    await user.type(screen.getByLabelText(/Descricao curta/i), "Preview com Nome e Email.");
    await user.click(
      within(screen.getByTestId("lead-field-card-nome")).getByRole("checkbox", { name: /Ativo/i }),
    );

    await waitFor(() =>
      expect(mockedPreviewEventoLanding).toHaveBeenLastCalledWith(
        "token",
        1,
        expect.objectContaining({
          cta_personalizado: "Receber novidades",
          descricao_curta: "Preview com Nome e Email.",
          campos: [
            { nome_campo: "Email", obrigatorio: true, ordem: 0 },
            { nome_campo: "Nome", obrigatorio: true, ordem: 1 },
          ],
        }),
        expect.objectContaining({ signal: expect.any(Object) }),
      ),
    );
    expect(await screen.findByRole("button", { name: /receber novidades/i })).toBeInTheDocument();
  });

  it("keeps the latest preview when an older request resolves later", async () => {
    const user = userEvent.setup();
    const oldPreview = createDeferred<LandingPageData>();
    const latestPreview = createDeferred<LandingPageData>();

    mockedPreviewEventoLanding
      .mockResolvedValueOnce(createLandingPreviewPayload() as never)
      .mockImplementationOnce(() => oldPreview.promise as never)
      .mockImplementationOnce(() => latestPreview.promise as never);

    render(
      <MemoryRouter initialEntries={["/eventos/1/formulario-lead"]}>
        <Routes>
          <Route path="/eventos/:id/formulario-lead" element={<EventLeadFormConfig />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByRole("button", { name: /quero conhecer/i })).toBeInTheDocument();

    const input = screen.getByLabelText(/template override/i);
    await user.clear(input);
    await user.type(input, "show_musical");
    await waitFor(() => expect(mockedPreviewEventoLanding).toHaveBeenCalledTimes(2));

    await user.clear(input);
    await user.type(input, "tecnologia");
    await waitFor(() => expect(mockedPreviewEventoLanding).toHaveBeenCalledTimes(3));

    latestPreview.resolve(
      createLandingPreviewPayload({
        template: {
          categoria: "tecnologia",
          tema: "Tech",
          mood: "Futuro, comunidade e inovacao.",
          cta_text: "Quero participar",
          color_primary: "#54DCFC",
          color_secondary: "#83FFEA",
          color_background: "#07111F",
          color_text: "#F8FAFC",
          hero_layout: "dark-overlay",
          cta_variant: "gradient",
          graphics_style: "grid",
          tone_of_voice: "enthusiasm",
          cta_experiment_enabled: false,
          cta_variants: [],
        },
      }),
    );
    expect(await screen.findByRole("button", { name: /quero participar/i })).toBeInTheDocument();

    oldPreview.resolve(
      createLandingPreviewPayload({
        template: {
          categoria: "show_musical",
          tema: "Show",
          mood: "Vibrante, noturno e memoravel.",
          cta_text: "Quero ir",
          color_primary: "#735CC6",
          color_secondary: "#FF6E91",
          color_background: "#140F2E",
          color_text: "#F8FAFC",
          hero_layout: "dark-overlay",
          cta_variant: "gradient",
          graphics_style: "dynamic",
          tone_of_voice: "enthusiasm",
          cta_experiment_enabled: false,
          cta_variants: [],
        },
      }),
    );

    await waitFor(() =>
      expect(screen.getByRole("button", { name: /quero participar/i })).toBeInTheDocument(),
    );
    expect(screen.queryByRole("button", { name: /quero ir/i })).not.toBeInTheDocument();
  });

  it("keeps the last preview visible and surfaces validation errors from preview requests", async () => {
    const user = userEvent.setup();
    mockedPreviewEventoLanding
      .mockResolvedValueOnce(createLandingPreviewPayload() as never)
      .mockRejectedValueOnce(new Error("template_override fora do catalogo homologado") as never);

    render(
      <MemoryRouter initialEntries={["/eventos/1/formulario-lead"]}>
        <Routes>
          <Route path="/eventos/:id/formulario-lead" element={<EventLeadFormConfig />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByRole("button", { name: /quero conhecer/i })).toBeInTheDocument();

    const input = screen.getByLabelText(/template override/i);
    await user.clear(input);
    await user.type(input, "template-nao-homologado");

    expect(
      await screen.findByText(/template_override fora do catalogo homologado/i),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /quero conhecer/i })).toBeInTheDocument();
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

  it("edits an ativacao from EventAtivacoes page", async () => {
    mockedListEventoAtivacoes.mockResolvedValueOnce([
      {
        id: 7,
        evento_id: 1,
        nome: "Ativacao existente",
        descricao: "Descricao original",
        mensagem_qrcode: null,
        gamificacao_id: null,
        redireciona_pesquisa: false,
        checkin_unico: false,
        termo_uso: false,
        gera_cupom: false,
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:00Z",
      },
    ] as never);
    mockedUpdateAtivacao.mockResolvedValueOnce({
      id: 7,
      evento_id: 1,
      nome: "Ativacao existente",
      descricao: "Descricao revisada",
      mensagem_qrcode: null,
      gamificacao_id: null,
      redireciona_pesquisa: false,
      checkin_unico: true,
      termo_uso: false,
      gera_cupom: false,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-02T00:00:00Z",
    } as never);

    const user = userEvent.setup();
    render(
      <MemoryRouter initialEntries={["/eventos/1/ativacoes"]}>
        <Routes>
          <Route path="/eventos/:id/ativacoes" element={<EventAtivacoes />} />
        </Routes>
      </MemoryRouter>,
    );

    const row = (await screen.findByText("Ativacao existente")).closest("tr");
    expect(row).not.toBeNull();
    await user.click(within(row as HTMLTableRowElement).getByRole("button", { name: /editar/i }));

    const descricaoInput = await screen.findByLabelText(/descricao/i);
    await user.clear(descricaoInput);
    await user.type(descricaoInput, "Descricao revisada");
    await user.click(screen.getByRole("checkbox", { name: /conversao unica por cpf/i }));
    await user.click(screen.getByRole("button", { name: /salvar ativacao/i }));

    await waitFor(() =>
      expect(mockedUpdateAtivacao).toHaveBeenCalledWith("token", 7, expect.objectContaining({
        nome: "Ativacao existente",
        descricao: "Descricao revisada",
        checkin_unico: true,
      })),
    );
    expect(await screen.findByText("Unica")).toBeInTheDocument();
  });

  it("shows qr preview and triggers download from the ativacao modal", async () => {
    mockedListEventoAtivacoes.mockResolvedValueOnce([
      {
        id: 11,
        evento_id: 1,
        nome: "Ativacao com QR",
        descricao: "Descricao com QR",
        mensagem_qrcode: "Escaneie para entrar.",
        gamificacao_id: null,
        landing_url: "https://npbb.example/landing/ativacoes/11",
        qr_code_url: "/qr/ativacao-11.svg",
        url_promotor: "https://npbb.example/promotor/11",
        redireciona_pesquisa: false,
        checkin_unico: false,
        termo_uso: false,
        gera_cupom: false,
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:00Z",
      },
    ] as never);

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      blob: vi.fn().mockResolvedValue(new Blob(["<svg/>"], { type: "image/svg+xml" })),
    } as unknown as Response);
    vi.stubGlobal("fetch", fetchMock);
    Object.defineProperty(URL, "createObjectURL", {
      configurable: true,
      writable: true,
      value: vi.fn(() => "blob:ativacao-11"),
    });
    Object.defineProperty(URL, "revokeObjectURL", {
      configurable: true,
      writable: true,
      value: vi.fn(),
    });

    const clickSpy = vi.fn();
    let createdAnchor: unknown = null;
    const realCreateElement = document.createElement.bind(document);
    vi.spyOn(document, "createElement").mockImplementation((tagName: string) => {
      const element = realCreateElement(tagName);
      if (tagName.toLowerCase() === "a") {
        createdAnchor = element;
        Object.defineProperty(element, "click", {
          configurable: true,
          value: clickSpy,
        });
      }
      return element;
    });

    const user = userEvent.setup();
    render(
      <MemoryRouter initialEntries={["/eventos/1/ativacoes"]}>
        <Routes>
          <Route path="/eventos/:id/ativacoes" element={<EventAtivacoes />} />
        </Routes>
      </MemoryRouter>,
    );

    const row = (await screen.findByText("Ativacao com QR")).closest("tr");
    expect(row).not.toBeNull();
    await user.click(within(row as HTMLTableRowElement).getByRole("button", { name: /visualizar/i }));

    expect(await screen.findByText("Visualizar ativacao")).toBeInTheDocument();
    expect(screen.getByTestId("ativacao-qr-image")).toHaveAttribute("src", `${API_BASE_URL}/qr/ativacao-11.svg`);

    await user.click(screen.getByRole("button", { name: /baixar qr/i }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(`${API_BASE_URL}/qr/ativacao-11.svg`));
    await waitFor(() => expect(clickSpy).toHaveBeenCalledTimes(1));
    expect(createdAnchor).not.toBeNull();
    if (!createdAnchor) {
      throw new Error("Anchor de download nao foi criado.");
    }
    const anchor = createdAnchor as HTMLAnchorElement;
    expect(anchor.download).toBe("ativacao-11-qr.svg");
  });

  it("shows a qr placeholder when the ativacao does not have qr_code_url yet", async () => {
    mockedListEventoAtivacoes.mockResolvedValueOnce([
      {
        id: 12,
        evento_id: 1,
        nome: "Ativacao sem QR",
        descricao: "Descricao sem QR",
        mensagem_qrcode: null,
        gamificacao_id: null,
        landing_url: "https://npbb.example/landing/ativacoes/12",
        qr_code_url: null,
        url_promotor: "https://npbb.example/promotor/12",
        redireciona_pesquisa: false,
        checkin_unico: true,
        termo_uso: false,
        gera_cupom: false,
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:00Z",
      },
    ] as never);

    const user = userEvent.setup();
    render(
      <MemoryRouter initialEntries={["/eventos/1/ativacoes"]}>
        <Routes>
          <Route path="/eventos/:id/ativacoes" element={<EventAtivacoes />} />
        </Routes>
      </MemoryRouter>,
    );

    const row = (await screen.findByText("Ativacao sem QR")).closest("tr");
    expect(row).not.toBeNull();
    await user.click(within(row as HTMLTableRowElement).getByRole("button", { name: /visualizar/i }));

    expect(await screen.findByTestId("ativacao-qr-placeholder")).toHaveTextContent(
      "QR ainda nao disponivel para esta ativacao.",
    );
    expect(screen.getByRole("button", { name: /baixar qr/i })).toBeDisabled();
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
