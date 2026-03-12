import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { LandingPageData } from "../../../services/landing_public";
import FormCard from "../FormCard";
import { resolveLandingContent } from "../landingContent";
import { getLayoutVisualSpec } from "../landingStyle";

function createLandingFixture(overrides: Partial<LandingPageData> = {}): LandingPageData {
  return {
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
      cta_personalizado: null,
      descricao: "Descricao completa do evento.",
      descricao_curta: "Resumo curto do evento.",
      data_inicio: "2026-04-10",
      data_fim: "2026-04-12",
      cidade: "Brasilia",
      estado: "DF",
    },
    template: {
      categoria: "corporativo",
      tema: "Tema Interno",
      mood: "mood-interno",
      cta_text: "Confirmar presenca",
      color_primary: "#1E3A8A",
      color_secondary: "#FCFC30",
      color_background: "#F5F7FB",
      color_text: "#111827",
      hero_layout: "split",
      cta_variant: "outlined",
      graphics_style: "grid",
      tone_of_voice: "tom-interno",
      cta_experiment_enabled: false,
      cta_variants: [],
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
      ],
      campos_obrigatorios: ["nome", "email"],
      campos_opcionais: [],
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
    gamificacoes: [],
    lead_reconhecido: false,
    lead_ja_converteu_nesta_ativacao: false,
    ...overrides,
  };
}

function renderFormCard(data: LandingPageData) {
  const content = resolveLandingContent(data);
  const layout = getLayoutVisualSpec(data);

  return render(
    <FormCard
      data={data}
      content={content}
      layout={layout}
      isPreview={false}
      formState={{}}
      consentimento={false}
      submitError={null}
      saving={false}
      submitted={null}
    />,
  );
}

describe("FormCard", () => {
  it("renderiza titulo com fallback ativacao.nome ?? evento.nome", () => {
    const data = createLandingFixture();
    renderFormCard(data);

    expect(screen.getByRole("heading", { name: "Stand Principal" })).toBeInTheDocument();
  });

  it("usa nome do evento quando ativacao estiver ausente", () => {
    const data = createLandingFixture({
      ativacao_id: null,
      ativacao: null,
      evento: {
        ...createLandingFixture().evento,
        nome: "Evento sem ativacao",
      },
    });

    renderFormCard(data);

    expect(screen.getByRole("heading", { name: "Evento sem ativacao" })).toBeInTheDocument();
  });

  it("nao exibe subtitulo quando ativacao.descricao e evento.descricao_curta estiverem ausentes", () => {
    const data = createLandingFixture({
      ativacao: {
        ...createLandingFixture().ativacao!,
        descricao: null,
      },
      evento: {
        ...createLandingFixture().evento,
        descricao_curta: null,
        descricao: "Descricao longa que nao deve aparecer no subtitulo",
      },
    });

    renderFormCard(data);

    expect(screen.queryByText("Descricao longa que nao deve aparecer no subtitulo")).not.toBeInTheDocument();
  });

  it("exibe callout de mensagem_qrcode quando presente", () => {
    const data = createLandingFixture();
    renderFormCard(data);

    expect(screen.getByText("Escaneie o QR code no totem para se cadastrar.")).toBeInTheDocument();
  });

  it("prioriza cta_personalizado sobre cta_text", () => {
    const data = createLandingFixture({
      evento: {
        ...createLandingFixture().evento,
        cta_personalizado: "Cadastre-se agora",
      },
    });

    renderFormCard(data);

    expect(screen.getByRole("button", { name: /cadastre-se agora/i })).toBeInTheDocument();
  });

  it("mapeia token visual corporativo", () => {
    const data = createLandingFixture({
      template: {
        ...createLandingFixture().template,
        categoria: "corporativo",
      },
    });

    const layout = getLayoutVisualSpec(data);

    expect(layout.formCardBackground).toBe("#FFFFFF");
    expect(layout.formCardBorder).toBe("2px solid rgba(252, 252, 48, 0.6)");
  });

  it("mapeia token visual de esporte_convencional", () => {
    const data = createLandingFixture({
      template: {
        ...createLandingFixture().template,
        categoria: "esporte_convencional",
      },
    });

    const layout = getLayoutVisualSpec(data);

    expect(layout.formCardBackground).toBe("rgba(255, 255, 255, 0.96)");
    expect(layout.formCardShadow).toBe("0 8px 32px rgba(0,0,0,0.35)");
  });

  it("define contrato responsivo de largura e padding", () => {
    const data = createLandingFixture();
    renderFormCard(data);

    const css = Array.from(document.querySelectorAll("style[data-emotion]")).map((node) => node.textContent).join("\n");

    expect(css).toMatch(/min\(92vw,\s*440px\)/);
    expect(css).toMatch(/padding:20px/);
    expect(css).toMatch(/min-width:768px/);
    expect(css).toMatch(/min\(480px,\s*90vw\)/);
    expect(css).toMatch(/padding:32px/);
    expect(css).toMatch(/min-width:1280px/);
    expect(css).toMatch(/min\(520px,\s*90vw\)/);
  });
});
