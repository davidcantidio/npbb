import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { createMemoryRouter, MemoryRouter, Route, RouterProvider, Routes } from "react-router-dom";

import EventLandingPage from "../EventLandingPage";
import {
  completeGamificacao,
  getLandingByAtivacao,
  getLandingByEventoAtivacao,
  getLandingByEvento,
  trackLandingAnalytics,
  submitLandingForm,
  type LandingPageData,
} from "../../services/landing_public";

vi.mock("../../services/landing_public", () => ({
  completeGamificacao: vi.fn(),
  getLandingByAtivacao: vi.fn(),
  getLandingByEventoAtivacao: vi.fn(),
  getLandingByEvento: vi.fn(),
  trackLandingAnalytics: vi.fn(),
  submitLandingForm: vi.fn(),
}));

vi.mock("../../services/landing_experiments", () => ({
  getLandingSessionId: () => "landing-test-session-123",
  selectLandingCtaVariant: (d: LandingPageData) => {
    const v = d.template.cta_variants?.[0];
    return v ?? null;
  },
}));

const mockedCompleteGamificacao = vi.mocked(completeGamificacao);
const mockedGetLandingByAtivacao = vi.mocked(getLandingByAtivacao);
const mockedGetLandingByEventoAtivacao = vi.mocked(getLandingByEventoAtivacao);
const mockedGetLandingByEvento = vi.mocked(getLandingByEvento);
const mockedTrackLandingAnalytics = vi.mocked(trackLandingAnalytics);
const mockedSubmitLandingForm = vi.mocked(submitLandingForm);

function createDeferred<T>() {
  let resolve: (value: T | PromiseLike<T>) => void = () => undefined;
  let reject: (reason?: unknown) => void = () => undefined;
  const promise = new Promise<T>((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return { promise, resolve, reject };
}

const landingFixture: LandingPageData = {
  ativacao_id: 1,
  ativacao: {
    id: 1,
    nome: "Stand Principal",
    conversao_unica: false,
    descricao: "Venha conhecer as novidades do BB.",
    mensagem_qrcode: "Escaneie o QR code no totem para se cadastrar.",
  },
  evento: {
    id: 10,
    nome: "BB Summit 2026",
    descricao: "Descricao completa do evento.",
    descricao_curta: "Resumo curto do evento.",
    data_inicio: "2026-04-10",
    data_fim: "2026-04-12",
    cidade: "Brasilia",
    estado: "DF",
  },
  template: {
    categoria: "corporativo",
    tema: "Corp",
    mood: "Profissional, confiavel e estrategico.",
    cta_text: "Confirmar presenca",
    color_primary: "#1E3A8A",
    color_secondary: "#FCFC30",
    color_background: "#F5F7FB",
    color_text: "#111827",
    hero_layout: "split",
    cta_variant: "outlined",
    graphics_style: "grid",
    tone_of_voice: "attention",
    cta_experiment_enabled: false,
    cta_variants: [],
  },
  formulario: {
    event_id: 10,
    ativacao_id: 1,
    submit_url: "/leads",
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
      {
        key: "cpf",
        label: "CPF",
        input_type: "text",
        required: false,
        autocomplete: "off",
        placeholder: "00000000000",
      },
    ],
    campos_obrigatorios: ["nome", "email"],
    campos_opcionais: ["cpf"],
    mensagem_sucesso: "Cadastro realizado com sucesso.",
    lgpd_texto: "Ao enviar seus dados, voce concorda com o tratamento das informacoes.",
    privacy_policy_url: "https://www.bb.com.br/site/privacidade-e-lgpd/",
  },
  marca: {
    tagline: "Banco do Brasil. Pra tudo que voce imaginar.",
  },
  acesso: {
    landing_url: "https://npbb.example/landing/ativacoes/1",
    qr_code_url: "data:image/svg+xml;base64,PHN2Zy8+",
    url_promotor: "https://npbb.example/landing/ativacoes/1",
  },
  lead_reconhecido: false,
  lead_ja_converteu_nesta_ativacao: false,
  token: null,
  gamificacoes: [
    {
      id: 321,
      nome: "Quiz BB",
      descricao: "Responda as perguntas no stand.",
      premio: "Brinde oficial",
      titulo_feedback: "Participacao concluida",
      texto_feedback: "Obrigado por concluir a gamificacao.",
    },
  ],
};

const culturalLandingFixture: LandingPageData = {
  ...landingFixture,
  evento: {
    ...landingFixture.evento,
    nome: "Mostra CCBB 2026",
    descricao_curta: "Exposicao, programacao e experiencias curatoriais.",
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
  },
};

const landingFixtureAtivacao2: LandingPageData = {
  ...landingFixture,
  ativacao_id: 2,
  ativacao: {
    id: 2,
    nome: "Stand Secundario",
    conversao_unica: false,
    descricao: "Ponto alternativo de atendimento.",
    mensagem_qrcode: "Escaneie o QR code no balcão secundario.",
  },
  formulario: {
    ...landingFixture.formulario,
    ativacao_id: 2,
    submit_url: "/leads",
  },
  acesso: {
    ...landingFixture.acesso,
    landing_url: "https://npbb.example/landing/ativacoes/2",
    url_promotor: "https://npbb.example/landing/ativacoes/2",
  },
};

const showLandingFixture: LandingPageData = {
  ...landingFixture,
  evento: {
    ...landingFixture.evento,
    nome: "Festival BB Noite Viva",
  },
  template: {
    categoria: "show_musical",
    tema: "Show",
    mood: "Vibrante, noturno e memoravel.",
    cta_text: "Quero receber novidades",
    color_primary: "#735CC6",
    color_secondary: "#FF6E91",
    color_background: "#140F2E",
    color_text: "#F8FAFC",
    hero_layout: "dark-overlay",
    cta_variant: "gradient",
    graphics_style: "dynamic",
    tone_of_voice: "enthusiasm",
    cta_experiment_enabled: true,
    cta_variants: [
      { id: "show_a", label: "Show A", text: "Cadastre-se na experiencia" },
      { id: "show_b", label: "Show B", text: "Quero receber novidades" },
    ],
  },
};

const landingFixtureConversaoUnica: LandingPageData = {
  ...landingFixture,
  ativacao: {
    ...landingFixture.ativacao!,
    conversao_unica: true,
  },
};

const landingFixtureConversaoUnicaJaConvertida: LandingPageData = {
  ...landingFixtureConversaoUnica,
  lead_reconhecido: true,
  lead_ja_converteu_nesta_ativacao: true,
  token: "abc123",
};

async function unlockCpfFirstStep(user: ReturnType<typeof userEvent.setup>, cpf = "529.982.247-25") {
  await user.type(screen.getByLabelText(/^cpf/i), cpf);
  await user.click(screen.getByRole("button", { name: /continuar/i }));
}

describe("EventLandingPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedGetLandingByAtivacao.mockResolvedValue(landingFixture);
    mockedGetLandingByEventoAtivacao.mockResolvedValue(landingFixture);
    mockedGetLandingByEvento.mockResolvedValue(landingFixture);
    mockedTrackLandingAnalytics.mockResolvedValue();
    mockedCompleteGamificacao.mockResolvedValue({
      ativacao_lead_id: 444,
      gamificacao_id: 321,
      gamificacao_completed: true,
      gamificacao_completed_at: "2026-04-10T12:00:00Z",
    });
    mockedSubmitLandingForm.mockResolvedValue({
      lead_id: 99,
      event_id: 10,
      ativacao_id: 1,
      ativacao_lead_id: 444,
      mensagem_sucesso: "Cadastro realizado com sucesso.",
      lead_reconhecido: true,
      conversao_registrada: true,
      bloqueado_cpf_duplicado: false,
    });
  });

  it("renderiza a landing na rota canonica e repassa o token", async () => {
    render(
      <MemoryRouter initialEntries={["/eventos/10/ativacoes/1?token=abc123"]}>
        <Routes>
          <Route path="/eventos/:evento_id/ativacoes/:ativacao_id" element={<EventLandingPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Stand Principal")).toBeInTheDocument();
    expect(screen.getByText("Escaneie o QR code no totem para se cadastrar.")).toBeInTheDocument();
    expect(mockedGetLandingByEventoAtivacao).toHaveBeenCalledWith(10, 1, { token: "abc123" });
    expect(mockedGetLandingByAtivacao).not.toHaveBeenCalled();
    expect(mockedGetLandingByEvento).not.toHaveBeenCalled();
  });

  it("pula CPF e abre formulario completo quando a landing vem reconhecida em ativacao multipla", async () => {
    mockedGetLandingByEventoAtivacao.mockResolvedValueOnce({
      ...landingFixture,
      lead_reconhecido: true,
      token: "abc123",
    });

    render(
      <MemoryRouter initialEntries={["/eventos/10/ativacoes/1?token=abc123"]}>
        <Routes>
          <Route path="/eventos/:evento_id/ativacoes/:ativacao_id" element={<EventLandingPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Stand Principal")).toBeInTheDocument();
    expect(screen.queryByTestId("cpf-first-input")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /continuar/i })).not.toBeInTheDocument();
    expect(screen.getByLabelText(/nome \*/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email \*/i)).toBeInTheDocument();
    expect(screen.queryByLabelText(/^cpf/i)).not.toBeInTheDocument();
    expect(mockedGetLandingByEventoAtivacao).toHaveBeenCalledWith(10, 1, { token: "abc123" });
  });

  it("mantem CPF-first quando a landing vem reconhecida em ativacao unica", async () => {
    mockedGetLandingByEventoAtivacao.mockResolvedValueOnce({
      ...landingFixtureConversaoUnica,
      lead_reconhecido: true,
      token: "abc123",
    });

    render(
      <MemoryRouter initialEntries={["/eventos/10/ativacoes/1?token=abc123"]}>
        <Routes>
          <Route path="/eventos/:evento_id/ativacoes/:ativacao_id" element={<EventLandingPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Stand Principal")).toBeInTheDocument();
    expect(screen.getByTestId("cpf-first-input")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /continuar/i })).toBeInTheDocument();
    expect(screen.queryByLabelText(/nome \*/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/email \*/i)).not.toBeInTheDocument();
  });

  it('mostra estado "Registrar outro CPF" quando lead reconhecido ja converteu em ativacao unica', async () => {
    mockedGetLandingByEventoAtivacao.mockResolvedValueOnce(landingFixtureConversaoUnicaJaConvertida);

    render(
      <MemoryRouter initialEntries={["/eventos/10/ativacoes/1?token=abc123"]}>
        <Routes>
          <Route path="/eventos/:evento_id/ativacoes/:ativacao_id" element={<EventLandingPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Stand Principal")).toBeInTheDocument();
    expect(screen.getByText("Você já se cadastrou nesta ativação.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /registrar outro cpf/i })).toBeInTheDocument();
    expect(screen.queryByTestId("cpf-first-input")).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/nome \*/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/email \*/i)).not.toBeInTheDocument();
  });

  it('reabre CPF-first ao clicar em "Registrar outro CPF"', async () => {
    const user = userEvent.setup();
    mockedGetLandingByEventoAtivacao.mockResolvedValueOnce(landingFixtureConversaoUnicaJaConvertida);

    render(
      <MemoryRouter initialEntries={["/eventos/10/ativacoes/1?token=abc123"]}>
        <Routes>
          <Route path="/eventos/:evento_id/ativacoes/:ativacao_id" element={<EventLandingPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Stand Principal")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /registrar outro cpf/i }));

    expect(await screen.findByTestId("cpf-first-input")).toBeInTheDocument();
    expect(screen.queryByText("Você já se cadastrou nesta ativação.")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /continuar/i })).toBeInTheDocument();
  });

  it("permite novo cadastro com outro CPF apos liberar o fluxo em ativacao unica", async () => {
    const user = userEvent.setup();
    mockedGetLandingByEventoAtivacao.mockResolvedValueOnce(landingFixtureConversaoUnicaJaConvertida);

    render(
      <MemoryRouter initialEntries={["/eventos/10/ativacoes/1?token=abc123"]}>
        <Routes>
          <Route path="/eventos/:evento_id/ativacoes/:ativacao_id" element={<EventLandingPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Stand Principal")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /registrar outro cpf/i }));
    await unlockCpfFirstStep(user, "111.444.777-35");
    await user.type(screen.getByLabelText(/nome \*/i), "Maria");
    await user.type(screen.getByLabelText(/email \*/i), "maria@example.com");
    await user.click(screen.getByRole("checkbox"));
    await user.click(screen.getByRole("button", { name: /confirmar presenca/i }));

    await waitFor(() =>
      expect(mockedSubmitLandingForm).toHaveBeenCalledWith("/leads", {
        nome: "Maria",
        sobrenome: undefined,
        email: "maria@example.com",
        event_id: 10,
        ativacao_id: 1,
        cpf: "11144477735",
        telefone: undefined,
        data_nascimento: undefined,
        estado: undefined,
        endereco: undefined,
        interesses: undefined,
        genero: undefined,
        area_de_atuacao: undefined,
        cta_variant_id: undefined,
        landing_session_id: expect.any(String),
        consentimento_lgpd: true,
      }),
    );
    expect(await screen.findByText("Cadastro realizado com sucesso.")).toBeInTheDocument();
  });

  it("mostra apenas CPF no primeiro acesso da ativacao", async () => {
    render(
      <MemoryRouter initialEntries={["/eventos/10/ativacoes/1"]}>
        <Routes>
          <Route path="/eventos/:evento_id/ativacoes/:ativacao_id" element={<EventLandingPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Stand Principal")).toBeInTheDocument();
    expect(screen.getByLabelText(/^cpf/i)).toBeInTheDocument();
    expect(screen.queryByLabelText(/nome \*/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/email \*/i)).not.toBeInTheDocument();
    expect(screen.queryByRole("checkbox")).not.toBeInTheDocument();
  });

  it("bloqueia CPF invalido antes de liberar o formulario", async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter initialEntries={["/eventos/10/ativacoes/1"]}>
        <Routes>
          <Route path="/eventos/:evento_id/ativacoes/:ativacao_id" element={<EventLandingPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Stand Principal")).toBeInTheDocument();
    await unlockCpfFirstStep(user, "52998224726");

    expect(await screen.findByText("Informe um CPF valido.")).toBeInTheDocument();
    expect(screen.queryByLabelText(/nome \*/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/email \*/i)).not.toBeInTheDocument();
  });

  it("libera o formulario completo apos CPF valido", async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter initialEntries={["/eventos/10/ativacoes/1"]}>
        <Routes>
          <Route path="/eventos/:evento_id/ativacoes/:ativacao_id" element={<EventLandingPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Stand Principal")).toBeInTheDocument();
    await unlockCpfFirstStep(user);

    expect(await screen.findByLabelText(/nome \*/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email \*/i)).toBeInTheDocument();
    expect(screen.getByRole("checkbox")).toBeInTheDocument();
    expect(screen.getByDisplayValue("52998224725")).toBeDisabled();
  });

  it("renderiza a landing por ativacao e envia o formulario", async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter initialEntries={["/landing/ativacoes/1"]}>
        <Routes>
          <Route path="/landing/ativacoes/:ativacaoId" element={<EventLandingPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Stand Principal")).toBeInTheDocument();
    expect(screen.getByText("Escaneie o QR code no totem para se cadastrar.")).toBeInTheDocument();
    await waitFor(() => {
      expect(mockedGetLandingByAtivacao).toHaveBeenCalledWith(1);
      expect(mockedGetLandingByEventoAtivacao).toHaveBeenCalledWith(10, 1, { token: null });
    });
    await unlockCpfFirstStep(user);
    await user.type(screen.getByLabelText(/nome \*/i), "Maria");
    await user.type(screen.getByLabelText(/email \*/i), "maria@example.com");
    await user.click(screen.getByRole("checkbox"));
    await user.click(screen.getByRole("button", { name: /confirmar presenca/i }));

    await waitFor(() =>
      expect(mockedSubmitLandingForm).toHaveBeenCalledWith("/leads", {
        nome: "Maria",
        sobrenome: undefined,
        email: "maria@example.com",
        event_id: 10,
        ativacao_id: 1,
        cpf: "52998224725",
        telefone: undefined,
        data_nascimento: undefined,
        estado: undefined,
        endereco: undefined,
        interesses: undefined,
        genero: undefined,
        area_de_atuacao: undefined,
        cta_variant_id: undefined,
        landing_session_id: expect.any(String),
        consentimento_lgpd: true,
      }),
    );
    expect(mockedTrackLandingAnalytics).toHaveBeenCalled();
    expect(await screen.findByText("Cadastro realizado com sucesso.")).toBeInTheDocument();
  });

  it("submete direto em ativacao multipla reconhecida sem exigir CPF", async () => {
    const user = userEvent.setup();

    mockedGetLandingByEventoAtivacao.mockResolvedValueOnce({
      ...landingFixture,
      lead_reconhecido: true,
      token: "abc123",
    });

    render(
      <MemoryRouter initialEntries={["/eventos/10/ativacoes/1?token=abc123"]}>
        <Routes>
          <Route path="/eventos/:evento_id/ativacoes/:ativacao_id" element={<EventLandingPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Stand Principal")).toBeInTheDocument();
    expect(screen.queryByTestId("cpf-first-input")).not.toBeInTheDocument();

    await user.type(screen.getByLabelText(/nome \*/i), "Maria");
    await user.type(screen.getByLabelText(/email \*/i), "maria@example.com");
    await user.click(screen.getByRole("checkbox"));
    await user.click(screen.getByRole("button", { name: /confirmar presenca/i }));

    await waitFor(() =>
      expect(mockedSubmitLandingForm).toHaveBeenCalledWith("/leads", {
        nome: "Maria",
        sobrenome: undefined,
        email: "maria@example.com",
        event_id: 10,
        ativacao_id: 1,
        cpf: undefined,
        telefone: undefined,
        data_nascimento: undefined,
        estado: undefined,
        endereco: undefined,
        interesses: undefined,
        genero: undefined,
        area_de_atuacao: undefined,
        cta_variant_id: undefined,
        landing_session_id: expect.any(String),
        consentimento_lgpd: true,
      }),
    );
    expect(await screen.findByText("Cadastro realizado com sucesso.")).toBeInTheDocument();
  });

  it("ignora cpf.required escondido no fluxo reconhecido de ativacao multipla", async () => {
    const user = userEvent.setup();

    mockedGetLandingByEventoAtivacao.mockResolvedValueOnce({
      ...landingFixture,
      lead_reconhecido: true,
      token: "abc123",
      formulario: {
        ...landingFixture.formulario,
        campos: landingFixture.formulario.campos.map((field) =>
          field.key === "cpf" ? { ...field, required: true } : field,
        ),
        campos_obrigatorios: ["nome", "email", "cpf"],
        campos_opcionais: [],
      },
    });

    render(
      <MemoryRouter initialEntries={["/eventos/10/ativacoes/1?token=abc123"]}>
        <Routes>
          <Route path="/eventos/:evento_id/ativacoes/:ativacao_id" element={<EventLandingPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Stand Principal")).toBeInTheDocument();
    expect(screen.queryByTestId("cpf-first-input")).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/^cpf/i)).not.toBeInTheDocument();

    await user.type(screen.getByLabelText(/nome \*/i), "Maria");
    await user.type(screen.getByLabelText(/email \*/i), "maria@example.com");
    await user.click(screen.getByRole("checkbox"));
    await user.click(screen.getByRole("button", { name: /confirmar presenca/i }));

    await waitFor(() =>
      expect(mockedSubmitLandingForm).toHaveBeenCalledWith("/leads", {
        nome: "Maria",
        sobrenome: undefined,
        email: "maria@example.com",
        event_id: 10,
        ativacao_id: 1,
        cpf: undefined,
        telefone: undefined,
        data_nascimento: undefined,
        estado: undefined,
        endereco: undefined,
        interesses: undefined,
        genero: undefined,
        area_de_atuacao: undefined,
        cta_variant_id: undefined,
        landing_session_id: expect.any(String),
        consentimento_lgpd: true,
      }),
    );
    expect(await screen.findByText("Cadastro realizado com sucesso.")).toBeInTheDocument();
  });

  it("exibe mensagem clara e volta ao passo do CPF quando o backend bloqueia duplicidade", async () => {
    const user = userEvent.setup();

    mockedSubmitLandingForm.mockResolvedValueOnce({
      lead_id: 99,
      event_id: 10,
      ativacao_id: 1,
      ativacao_lead_id: 444,
      mensagem_sucesso: "Cadastro realizado com sucesso.",
      lead_reconhecido: true,
      conversao_registrada: false,
      bloqueado_cpf_duplicado: true,
    });

    render(
      <MemoryRouter initialEntries={["/landing/ativacoes/1"]}>
        <Routes>
          <Route path="/landing/ativacoes/:ativacaoId" element={<EventLandingPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Stand Principal")).toBeInTheDocument();
    await unlockCpfFirstStep(user);
    await user.type(screen.getByLabelText(/nome \*/i), "Maria");
    await user.type(screen.getByLabelText(/email \*/i), "maria@example.com");
    await user.click(screen.getByRole("checkbox"));
    await user.click(screen.getByRole("button", { name: /confirmar presenca/i }));

    expect(
      await screen.findByText(
        "Este CPF ja foi cadastrado nesta ativacao. Se estiver cadastrando outra pessoa, informe outro CPF.",
      ),
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/^cpf/i)).toBeInTheDocument();
    expect(screen.queryByLabelText(/nome \*/i)).not.toBeInTheDocument();
    expect(screen.queryByText("Cadastro realizado com sucesso.")).not.toBeInTheDocument();
  });

  it("bloqueia submit sem aceite LGPD na rota por evento", async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter initialEntries={["/landing/eventos/10"]}>
        <Routes>
          <Route path="/landing/eventos/:eventId" element={<EventLandingPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Stand Principal")).toBeInTheDocument();
    await user.type(screen.getByLabelText(/nome \*/i), "Joao");
    await user.type(screen.getByLabelText(/email \*/i), "joao@example.com");
    await user.click(screen.getByRole("button", { name: /confirmar presenca/i }));

    expect(await screen.findByText(/precisa aceitar o tratamento de dados/i)).toBeInTheDocument();
    expect(mockedSubmitLandingForm).not.toHaveBeenCalled();
    expect(mockedGetLandingByEvento).toHaveBeenCalledWith(10);
  });

  it("renderiza variacao editorial para evento cultural", async () => {
    mockedGetLandingByEvento.mockResolvedValueOnce(culturalLandingFixture);

    render(
      <MemoryRouter initialEntries={["/landing/eventos/10"]}>
        <Routes>
          <Route path="/landing/eventos/:eventId" element={<EventLandingPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Stand Principal")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /quero conhecer/i })).toBeInTheDocument();
    expect(screen.queryByText(/Programacao e contexto/i)).not.toBeInTheDocument();
  });

  it("aplica exposicao de CTA para template musical", async () => {
    mockedGetLandingByEvento.mockResolvedValueOnce(showLandingFixture);

    render(
      <MemoryRouter initialEntries={["/landing/eventos/10"]}>
        <Routes>
          <Route path="/landing/eventos/:eventId" element={<EventLandingPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Stand Principal")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /cadastre-se na experiencia|quero receber novidades/i }),
    ).toBeInTheDocument();
    await waitFor(() =>
      expect(mockedTrackLandingAnalytics).toHaveBeenCalledWith(
        expect.objectContaining({ event_name: "cta_exposure" }),
      ),
    );
  });

  it("habilita e conclui gamificacao apos submit com ativacao_lead_id", async () => {
    const user = userEvent.setup();

    mockedSubmitLandingForm.mockResolvedValueOnce({
      lead_id: 77,
      event_id: 10,
      ativacao_id: 1,
      ativacao_lead_id: 777,
      mensagem_sucesso: "Cadastro realizado com sucesso.",
      lead_reconhecido: true,
      conversao_registrada: true,
      bloqueado_cpf_duplicado: false,
    });

    render(
      <MemoryRouter initialEntries={["/landing/ativacoes/1"]}>
        <Routes>
          <Route path="/landing/ativacoes/:ativacaoId" element={<EventLandingPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Stand Principal")).toBeInTheDocument();
    await unlockCpfFirstStep(user);
    await user.type(screen.getByLabelText(/nome \*/i), "Maria");
    await user.type(screen.getByLabelText(/email \*/i), "maria@example.com");
    await user.click(screen.getByRole("checkbox"));
    await user.click(screen.getByRole("button", { name: /confirmar presenca/i }));
    expect(await screen.findByText("Cadastro realizado com sucesso.")).toBeInTheDocument();

    const participarButton = await screen.findByRole("button", { name: /quero participar/i });
    expect(participarButton).toBeEnabled();
    await user.click(participarButton);
    await user.click(await screen.findByRole("button", { name: /conclui/i }));

    await waitFor(() =>
      expect(mockedCompleteGamificacao).toHaveBeenCalledWith(777, {
        gamificacao_id: 321,
        gamificacao_completed: true,
      }),
    );
    expect(await screen.findByRole("button", { name: /nova pessoa/i })).toBeInTheDocument();
  });

  it("nao chama API de gamificacao quando submit nao retorna ativacao_lead_id", async () => {
    const user = userEvent.setup();

    mockedSubmitLandingForm.mockResolvedValueOnce({
      lead_id: 88,
      event_id: 10,
      ativacao_id: 1,
      ativacao_lead_id: null,
      mensagem_sucesso: "Cadastro realizado com sucesso.",
      lead_reconhecido: true,
      conversao_registrada: true,
      bloqueado_cpf_duplicado: false,
    });

    render(
      <MemoryRouter initialEntries={["/landing/ativacoes/1"]}>
        <Routes>
          <Route path="/landing/ativacoes/:ativacaoId" element={<EventLandingPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Stand Principal")).toBeInTheDocument();
    await unlockCpfFirstStep(user);
    await user.type(screen.getByLabelText(/nome \*/i), "Rafa");
    await user.type(screen.getByLabelText(/email \*/i), "rafa@example.com");
    await user.click(screen.getByRole("checkbox"));
    await user.click(screen.getByRole("button", { name: /confirmar presenca/i }));
    expect(await screen.findByText("Cadastro realizado com sucesso.")).toBeInTheDocument();

    const participarButton = await screen.findByRole("button", { name: /quero participar/i });
    expect(participarButton).toBeDisabled();
    expect(
      screen.getByText(/gamificacao esta indisponivel para este envio/i),
    ).toBeInTheDocument();

    expect(mockedCompleteGamificacao).not.toHaveBeenCalled();
  });

  it("desabilita reset do formulario enquanto conclusao da gamificacao esta em andamento", async () => {
    const user = userEvent.setup();
    const deferred = createDeferred<{
      ativacao_lead_id: number;
      gamificacao_id: number;
      gamificacao_completed: boolean;
      gamificacao_completed_at: string;
    }>();
    mockedCompleteGamificacao.mockReturnValueOnce(deferred.promise);

    mockedSubmitLandingForm.mockResolvedValueOnce({
      lead_id: 10,
      event_id: 10,
      ativacao_id: 1,
      ativacao_lead_id: 1001,
      mensagem_sucesso: "Cadastro realizado com sucesso.",
      lead_reconhecido: true,
      conversao_registrada: true,
      bloqueado_cpf_duplicado: false,
    });

    render(
      <MemoryRouter initialEntries={["/landing/ativacoes/1"]}>
        <Routes>
          <Route path="/landing/ativacoes/:ativacaoId" element={<EventLandingPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Stand Principal")).toBeInTheDocument();
    await unlockCpfFirstStep(user);
    await user.type(screen.getByLabelText(/nome \*/i), "Ana");
    await user.type(screen.getByLabelText(/email \*/i), "ana@bb.com.br");
    await user.click(screen.getByRole("checkbox"));
    await user.click(screen.getByRole("button", { name: /confirmar presenca/i }));
    expect(await screen.findByText("Cadastro realizado com sucesso.")).toBeInTheDocument();

    await user.click(await screen.findByRole("button", { name: /quero participar/i }));
    await user.click(await screen.findByRole("button", { name: /conclui/i }));

    await waitFor(() =>
      expect(screen.getByRole("button", { name: /cadastrar outro email/i })).toBeDisabled(),
    );

    deferred.resolve({
      ativacao_lead_id: 1001,
      gamificacao_id: 321,
      gamificacao_completed: true,
      gamificacao_completed_at: "2026-04-10T12:00:00Z",
    });

    expect(await screen.findByRole("button", { name: /nova pessoa/i })).toBeInTheDocument();
  });

  it("reseta formulario e gamificacao ao clicar em Nova pessoa", async () => {
    const user = userEvent.setup();

    mockedSubmitLandingForm.mockResolvedValueOnce({
      lead_id: 66,
      event_id: 10,
      ativacao_id: 1,
      ativacao_lead_id: 666,
      mensagem_sucesso: "Cadastro realizado com sucesso.",
      lead_reconhecido: true,
      conversao_registrada: true,
      bloqueado_cpf_duplicado: false,
    });

    render(
      <MemoryRouter initialEntries={["/landing/ativacoes/1"]}>
        <Routes>
          <Route path="/landing/ativacoes/:ativacaoId" element={<EventLandingPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Stand Principal")).toBeInTheDocument();
    await unlockCpfFirstStep(user);
    await user.type(screen.getByLabelText(/nome \*/i), "Bia");
    await user.type(screen.getByLabelText(/email \*/i), "bia@example.com");
    await user.click(screen.getByRole("checkbox"));
    await user.click(screen.getByRole("button", { name: /confirmar presenca/i }));
    expect(await screen.findByText("Cadastro realizado com sucesso.")).toBeInTheDocument();

    await user.click(await screen.findByRole("button", { name: /quero participar/i }));
    await user.click(await screen.findByRole("button", { name: /conclui/i }));
    await user.click(await screen.findByRole("button", { name: /nova pessoa/i }));

    expect(await screen.findByLabelText(/^cpf/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /quero participar/i })).toBeDisabled();
    expect(screen.queryByText("Cadastro realizado com sucesso.")).not.toBeInTheDocument();
  });

  it("reseta estado da gamificacao ao clicar em Cadastrar outro email", async () => {
    const user = userEvent.setup();

    mockedSubmitLandingForm.mockResolvedValueOnce({
      lead_id: 123,
      event_id: 10,
      ativacao_id: 1,
      ativacao_lead_id: 987,
      mensagem_sucesso: "Cadastro realizado com sucesso.",
      lead_reconhecido: true,
      conversao_registrada: true,
      bloqueado_cpf_duplicado: false,
    });

    render(
      <MemoryRouter initialEntries={["/landing/ativacoes/1"]}>
        <Routes>
          <Route path="/landing/ativacoes/:ativacaoId" element={<EventLandingPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Stand Principal")).toBeInTheDocument();
    await unlockCpfFirstStep(user);
    await user.type(screen.getByLabelText(/nome \*/i), "Beto");
    await user.type(screen.getByLabelText(/email \*/i), "beto@example.com");
    await user.click(screen.getByRole("checkbox"));
    await user.click(screen.getByRole("button", { name: /confirmar presenca/i }));
    expect(await screen.findByText("Cadastro realizado com sucesso.")).toBeInTheDocument();

    await user.click(await screen.findByRole("button", { name: /quero participar/i }));
    expect(await screen.findByRole("button", { name: /conclui/i })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /cadastrar outro email/i }));

    expect(await screen.findByLabelText(/^cpf/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /quero participar/i })).toBeDisabled();
    expect(screen.queryByRole("button", { name: /conclui/i })).not.toBeInTheDocument();
  });

  it("reinicializa estado ao trocar rota de ativacao", async () => {
    const user = userEvent.setup();
    mockedGetLandingByAtivacao.mockImplementation(async (ativacaoId) =>
      ativacaoId === 2 ? landingFixtureAtivacao2 : landingFixture,
    );
    mockedGetLandingByEventoAtivacao.mockImplementation(async (_eventId, ativacaoId) =>
      ativacaoId === 2 ? landingFixtureAtivacao2 : landingFixture,
    );

    const router = createMemoryRouter(
      [
        {
          path: "/landing/ativacoes/:ativacaoId",
          element: <EventLandingPage />,
        },
      ],
      { initialEntries: ["/landing/ativacoes/1"] },
    );

    render(<RouterProvider router={router} />);

    expect(await screen.findByText("Stand Principal")).toBeInTheDocument();
    await unlockCpfFirstStep(user);
    await user.type(screen.getByLabelText(/nome \*/i), "Maria");
    await user.type(screen.getByLabelText(/email \*/i), "maria@example.com");
    await user.click(screen.getByRole("checkbox"));
    await user.click(screen.getByRole("button", { name: /confirmar presenca/i }));
    expect(await screen.findByText("Cadastro realizado com sucesso.")).toBeInTheDocument();

    await act(async () => {
      await router.navigate("/landing/ativacoes/2");
    });
    expect(await screen.findByText("Stand Secundario")).toBeInTheDocument();
    expect(screen.queryByText("Cadastro realizado com sucesso.")).not.toBeInTheDocument();
    expect(screen.getByLabelText(/^cpf/i)).toHaveValue("");
    expect(screen.getByRole("button", { name: /quero participar/i })).toBeDisabled();
  });
});
