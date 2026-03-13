import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import LandingPageView from "../LandingPageView";
import GamificacaoBlock from "../GamificacaoBlock";
import { createTemplateFixture, GAMIFICACAO_MOCK } from "./landingFixtures";

/**
 * AFLPD-F4-01-002 — Validação dos fluxos UC-01 a UC-04
 *
 * UC-01: Ativação sem gamificação
 * UC-02: Ativação com mensagem de orientação
 * UC-03: Ativação com gamificação (fluxo completo)
 * UC-04: Preview no backoffice
 */

describe("AFLPD-F4-01-002 — Fluxos UC-01 a UC-04", () => {
  describe("UC-01 — Ativação sem gamificação", () => {
    it("exibe formulário com título = ativacao.nome", () => {
      const data = createTemplateFixture("esporte_convencional", {
        withAtivacao: true,
        withGamificacao: false,
      });
      render(<LandingPageView data={data} mode="public" />);

      expect(screen.getByText("Stand Principal")).toBeInTheDocument();
    });

    it("exibe campos obrigatórios com label e asterisco", () => {
      const data = createTemplateFixture("esporte_convencional", { withGamificacao: false });
      render(<LandingPageView data={data} mode="public" />);

      expect(screen.getByLabelText(/Nome \*/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Email \*/i)).toBeInTheDocument();
    });

    it("exibe checkbox LGPD funcional", async () => {
      const user = userEvent.setup();
      const onConsentimento = vi.fn();
      const data = createTemplateFixture("esporte_convencional", { withGamificacao: false });
      render(
        <LandingPageView
          data={data}
          mode="public"
          onConsentimentoChange={onConsentimento}
        />,
      );

      const checkbox = screen.getByRole("checkbox");
      expect(checkbox).not.toBeChecked();
      await user.click(checkbox);
      expect(onConsentimento).toHaveBeenCalledWith(true);
    });

    it("exibe botão CTA com texto do template", () => {
      const data = createTemplateFixture("esporte_convencional", { withGamificacao: false });
      render(<LandingPageView data={data} mode="public" />);

      expect(screen.getByRole("button", { name: /garanta sua vaga/i })).toBeInTheDocument();
    });

    it("CTA dispara onSubmit quando clicado", async () => {
      const user = userEvent.setup();
      const onSubmit = vi.fn();
      const data = createTemplateFixture("esporte_convencional", { withGamificacao: false });
      render(<LandingPageView data={data} mode="public" onSubmit={onSubmit} />);

      await user.click(screen.getByRole("button", { name: /garanta sua vaga/i }));
      expect(onSubmit).toHaveBeenCalledTimes(1);
    });

    it("exibe mensagem de sucesso após submit", () => {
      const data = createTemplateFixture("esporte_convencional", { withGamificacao: false });
      render(
        <LandingPageView
          data={data}
          mode="public"
          submitted={{
            lead_id: 1,
            event_id: 10,
            ativacao_id: 1,
            ativacao_lead_id: 1,
            mensagem_sucesso: "Cadastro realizado com sucesso.",
            lead_reconhecido: true,
            conversao_registrada: true,
            bloqueado_cpf_duplicado: false,
          }}
        />,
      );

      expect(screen.getByText("Cadastro realizado com sucesso.")).toBeInTheDocument();
      expect(screen.getByText("Cadastro concluido")).toBeInTheDocument();
    });

    it("não exibe bloco de gamificação", () => {
      const data = createTemplateFixture("esporte_convencional", { withGamificacao: false });
      render(<LandingPageView data={data} mode="public" />);

      expect(screen.queryByText("Roleta da Sorte BB")).not.toBeInTheDocument();
      expect(screen.queryByText(/preencha o cadastro acima/i)).not.toBeInTheDocument();
    });
  });

  describe("UC-02 — Ativação com mensagem de orientação", () => {
    it("exibe callout com mensagem_qrcode acima dos campos", () => {
      const data = createTemplateFixture("evento_cultural", {
        withAtivacao: true,
        withGamificacao: false,
      });
      render(<LandingPageView data={data} mode="public" />);

      expect(
        screen.getByText("Escaneie o QR code no totem para se cadastrar."),
      ).toBeInTheDocument();
    });

    it("não exibe callout quando mensagem_qrcode está ausente", () => {
      const data = createTemplateFixture("evento_cultural", { withAtivacao: false });
      render(<LandingPageView data={data} mode="public" />);

      expect(
        screen.queryByText("Escaneie o QR code no totem para se cadastrar."),
      ).not.toBeInTheDocument();
    });

    it("formulário funciona normalmente com callout presente", async () => {
      const user = userEvent.setup();
      const onInputChange = vi.fn();
      const data = createTemplateFixture("evento_cultural", { withAtivacao: true });
      render(
        <LandingPageView data={data} mode="public" onInputChange={onInputChange} />,
      );

      const nomeField = screen.getByLabelText(/Nome \*/i);
      await user.type(nomeField, "Maria");
      expect(onInputChange).toHaveBeenCalled();
    });
  });

  describe("UC-03 — Ativação com gamificação (fluxo completo)", () => {
    it("exibe card de gamificação com botão desabilitado antes do submit", () => {
      render(
        <GamificacaoBlock
          gamificacoes={[GAMIFICACAO_MOCK]}
          leadSubmitted={false}
          onComplete={vi.fn()}
          onReset={vi.fn()}
        />,
      );

      expect(screen.getByText("Roleta da Sorte BB")).toBeInTheDocument();
      expect(screen.getByText(/gire a roleta/i)).toBeInTheDocument();
      expect(screen.getByText(/Premio: Camiseta oficial BB/i)).toBeInTheDocument();
      expect(screen.getByText(/preencha o cadastro acima para participar/i)).toBeInTheDocument();

      const btn = screen.getByRole("button", { name: /quero participar/i });
      expect(btn).toBeDisabled();
      expect(btn).toHaveAttribute("aria-disabled", "true");
    });

    it("habilita botão após lead ser submetido", () => {
      render(
        <GamificacaoBlock
          gamificacoes={[GAMIFICACAO_MOCK]}
          leadSubmitted={true}
          onComplete={vi.fn()}
          onReset={vi.fn()}
        />,
      );

      const btn = screen.getByRole("button", { name: /quero participar/i });
      expect(btn).not.toBeDisabled();
    });

    it("transição PRESENTING → ACTIVE ao clicar 'Quero participar'", async () => {
      const user = userEvent.setup();
      render(
        <GamificacaoBlock
          gamificacoes={[GAMIFICACAO_MOCK]}
          leadSubmitted={true}
          onComplete={vi.fn()}
          onReset={vi.fn()}
        />,
      );

      await user.click(screen.getByRole("button", { name: /quero participar/i }));

      expect(screen.getByText(/participe da atividade/i)).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /conclui/i })).toBeInTheDocument();
    });

    it("transição ACTIVE → COMPLETED ao clicar 'Concluí'", async () => {
      const user = userEvent.setup();
      const onComplete = vi.fn().mockResolvedValue(undefined);
      render(
        <GamificacaoBlock
          gamificacoes={[GAMIFICACAO_MOCK]}
          leadSubmitted={true}
          onComplete={onComplete}
          onReset={vi.fn()}
        />,
      );

      await user.click(screen.getByRole("button", { name: /quero participar/i }));
      await user.click(screen.getByRole("button", { name: /conclui/i }));

      expect(onComplete).toHaveBeenCalledWith(GAMIFICACAO_MOCK.id);
      expect(screen.getByText("Parabens!")).toBeInTheDocument();
      expect(screen.getByText(/concluiu a gamificacao/i)).toBeInTheDocument();
    });

    it("'Nova pessoa' reseta para estado PRESENTING", async () => {
      const user = userEvent.setup();
      const onReset = vi.fn();
      render(
        <GamificacaoBlock
          gamificacoes={[GAMIFICACAO_MOCK]}
          leadSubmitted={true}
          onComplete={vi.fn().mockResolvedValue(undefined)}
          onReset={onReset}
        />,
      );

      await user.click(screen.getByRole("button", { name: /quero participar/i }));
      await user.click(screen.getByRole("button", { name: /conclui/i }));
      await user.click(screen.getByRole("button", { name: /nova pessoa/i }));

      expect(onReset).toHaveBeenCalledTimes(1);
      expect(screen.getByRole("button", { name: /quero participar/i })).toBeInTheDocument();
    });
  });

  describe("UC-04 — Preview no backoffice", () => {
    it("exibe apenas badge de preview e replica o layout publico", () => {
      const data = createTemplateFixture("show_musical");
      render(<LandingPageView data={data} mode="preview" />);

      expect(screen.getByTestId("landing-preview-badge")).toHaveTextContent("Preview");
      expect(screen.queryByText(data.template.mood)).not.toBeInTheDocument();
      expect(screen.queryByText(new RegExp(`Categoria: ${data.template.categoria}`))).not.toBeInTheDocument();
      expect(screen.queryByText(new RegExp(`Template: ${data.template.tema}`))).not.toBeInTheDocument();
    });

    it("formulário está desabilitado em isPreview", () => {
      const data = createTemplateFixture("show_musical");
      render(<LandingPageView data={data} mode="preview" />);

      const inputs = screen.getAllByRole("textbox");
      for (const input of inputs) {
        expect(input).toBeDisabled();
      }

      const checkbox = screen.getByRole("checkbox");
      expect(checkbox).toBeDisabled();

      const ctaButton = screen.getByRole("button", { name: new RegExp(data.template.cta_text, "i") });
      expect(ctaButton).toBeDisabled();
    });

    it("nao exibe mensagem operacional extra no preview", () => {
      const data = createTemplateFixture("show_musical");
      render(<LandingPageView data={data} mode="preview" />);

      expect(screen.queryByText(/preview fiel ao contrato real/i)).not.toBeInTheDocument();
    });

    it("exibe o mesmo footer minimo em modo preview", () => {
      const data = createTemplateFixture("show_musical");
      render(<LandingPageView data={data} mode="preview" />);

      expect(screen.getByText("Banco do Brasil. Pra tudo que voce imaginar.")).toBeInTheDocument();
      expect(screen.getByRole("link", { name: /politica de privacidade e lgpd/i })).toBeInTheDocument();
    });
  });
});
