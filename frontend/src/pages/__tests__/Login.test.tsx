import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import Login from "../Login";
import { ApiError } from "../../services/http";
import { useAuth } from "../../store/auth";

vi.mock("../../store/auth", () => ({ useAuth: vi.fn() }));

const mockedUseAuth = vi.mocked(useAuth);

function renderLogin() {
  return render(
    <MemoryRouter initialEntries={["/login"]}>
      <Login />
    </MemoryRouter>,
  );
}

function makeAuthValue(login = vi.fn()) {
  return {
    user: null,
    token: null,
    loading: false,
    refreshing: false,
    error: null,
    login,
    logout: vi.fn(),
    refresh: vi.fn(),
  };
}

describe("Login", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("desabilita o submit durante o bootstrap de sessao sem exibir spinner", () => {
    mockedUseAuth.mockReturnValue({
      user: null,
      token: null,
      loading: true,
      refreshing: false,
      error: null,
      login: vi.fn(),
      logout: vi.fn(),
      refresh: vi.fn(),
    });

    renderLogin();

    const submitButton = screen.getByRole("button", { name: "Entrar" });
    expect(submitButton).toBeDisabled();
    expect(screen.queryByRole("progressbar")).not.toBeInTheDocument();
  });

  it("exibe mensagem especifica quando o login falha por timeout", async () => {
    const user = userEvent.setup();
    const login = vi.fn().mockRejectedValue(
      new ApiError({
        message: "Tempo limite da requisicao excedido.",
        status: 0,
        detail: "TIMEOUT",
        code: "TIMEOUT",
        method: "POST",
        url: "http://localhost/api/auth/login",
      }),
    );

    mockedUseAuth.mockReturnValue(makeAuthValue(login));

    renderLogin();

    await user.type(screen.getByLabelText(/email/i), "a@b.com");
    await user.type(screen.getByLabelText(/^senha/i), "secret");
    await user.click(screen.getByRole("button", { name: "Entrar" }));

    expect(
      await screen.findByText(
        "O servidor demorou demais para responder. Confirme que o backend esta em execucao e tente novamente.",
      ),
    ).toBeInTheDocument();
  });

  it("exibe mensagem especifica quando o login falha por erro de rede", async () => {
    const user = userEvent.setup();
    const login = vi.fn().mockRejectedValue(
      new ApiError({
        message: "Falha de rede ao comunicar com a API.",
        status: 0,
        detail: "NETWORK_ERROR",
        code: "NETWORK_ERROR",
        method: "POST",
        url: "http://localhost/api/auth/login",
      }),
    );

    mockedUseAuth.mockReturnValue(makeAuthValue(login));

    renderLogin();

    await user.type(screen.getByLabelText(/email/i), "a@b.com");
    await user.type(screen.getByLabelText(/^senha/i), "secret");
    await user.click(screen.getByRole("button", { name: "Entrar" }));

    expect(
      await screen.findByText(
        "Nao foi possivel alcancar a API. Verifique se o backend, o proxy do Vite e o CORS estao configurados corretamente.",
      ),
    ).toBeInTheDocument();
  });

  it("exibe mensagem especifica quando o backend responde 503 por timeout do banco", async () => {
    const user = userEvent.setup();
    const login = vi.fn().mockRejectedValue(
      new ApiError({
        message: "Banco de dados indisponivel ou demorando para responder.",
        status: 503,
        detail: {
          code: "DB_TIMEOUT",
          message: "Banco de dados indisponivel ou demorando para responder.",
        },
        code: "DB_TIMEOUT",
        method: "POST",
        url: "http://localhost/api/auth/login",
      }),
    );

    mockedUseAuth.mockReturnValue(makeAuthValue(login));

    renderLogin();

    await user.type(screen.getByLabelText(/email/i), "a@b.com");
    await user.type(screen.getByLabelText(/^senha/i), "secret");
    await user.click(screen.getByRole("button", { name: "Entrar" }));

    expect(
      await screen.findByText(
        "A autenticacao esta temporariamente indisponivel porque o banco de dados demorou demais para responder.",
      ),
    ).toBeInTheDocument();
  });

  it("preserva erro de credenciais invalidas", async () => {
    const user = userEvent.setup();
    const login = vi.fn().mockRejectedValue(
      new ApiError({
        message: "Credenciais invalidas",
        status: 401,
        detail: "Credenciais invalidas",
        code: null,
        method: "POST",
        url: "http://localhost/api/auth/login",
      }),
    );

    mockedUseAuth.mockReturnValue(makeAuthValue(login));

    renderLogin();

    await user.type(screen.getByLabelText(/email/i), "a@b.com");
    await user.type(screen.getByLabelText(/^senha/i), "secret");
    await user.click(screen.getByRole("button", { name: "Entrar" }));

    expect(await screen.findByText("Credenciais invalidas")).toBeInTheDocument();
  });
});
