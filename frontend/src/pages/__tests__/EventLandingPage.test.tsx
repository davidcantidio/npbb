import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import EventLandingPage from "../EventLandingPage";
import {
  getLandingByAtivacao,
  getLandingByEvento,
  submitLandingForm,
  type LandingPageData,
} from "../../services/landing_public";

vi.mock("../../services/landing_public", () => ({
  getLandingByAtivacao: vi.fn(),
  getLandingByEvento: vi.fn(),
  submitLandingForm: vi.fn(),
}));

const mockedGetLandingByAtivacao = vi.mocked(getLandingByAtivacao);
const mockedGetLandingByEvento = vi.mocked(getLandingByEvento);
const mockedSubmitLandingForm = vi.mocked(submitLandingForm);

const landingFixture: LandingPageData = {
  ativacao_id: 1,
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
  },
  formulario: {
    event_id: 10,
    ativacao_id: 1,
    submit_url: "/landing/ativacoes/1/submit",
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
    versao_logo: "positivo",
    url_hero_image: "data:image/svg+xml;base64,PHN2Zy8+",
    hero_alt: "Imagem de destaque do evento BB Summit 2026",
  },
  acesso: {
    landing_url: "https://npbb.example/landing/ativacoes/1",
    qr_code_url: "data:image/svg+xml;base64,PHN2Zy8+",
    url_promotor: "https://npbb.example/landing/ativacoes/1",
  },
};

describe("EventLandingPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedGetLandingByAtivacao.mockResolvedValue(landingFixture);
    mockedGetLandingByEvento.mockResolvedValue(landingFixture);
    mockedSubmitLandingForm.mockResolvedValue({
      lead_id: 99,
      event_id: 10,
      ativacao_id: 1,
      mensagem_sucesso: "Cadastro realizado com sucesso.",
    });
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

    expect(await screen.findByText("BB Summit 2026")).toBeInTheDocument();
    await user.type(screen.getByLabelText(/nome \*/i), "Maria");
    await user.type(screen.getByLabelText(/email \*/i), "maria@example.com");
    await user.click(screen.getByRole("checkbox"));
    await user.click(screen.getByRole("button", { name: /confirmar presenca/i }));

    await waitFor(() =>
      expect(mockedSubmitLandingForm).toHaveBeenCalledWith("/landing/ativacoes/1/submit", {
        nome: "Maria",
        sobrenome: undefined,
        email: "maria@example.com",
        cpf: undefined,
        telefone: undefined,
        data_nascimento: undefined,
        estado: undefined,
        endereco: undefined,
        interesses: undefined,
        genero: undefined,
        area_de_atuacao: undefined,
        consentimento_lgpd: true,
      }),
    );
    expect(await screen.findByText("Cadastro realizado com sucesso.")).toBeInTheDocument();
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

    expect(await screen.findByText("BB Summit 2026")).toBeInTheDocument();
    await user.type(screen.getByLabelText(/nome \*/i), "Joao");
    await user.type(screen.getByLabelText(/email \*/i), "joao@example.com");
    await user.click(screen.getByRole("button", { name: /confirmar presenca/i }));

    expect(await screen.findByText(/precisa aceitar o tratamento de dados/i)).toBeInTheDocument();
    expect(mockedSubmitLandingForm).not.toHaveBeenCalled();
    expect(mockedGetLandingByEvento).toHaveBeenCalledWith(10);
  });
});
