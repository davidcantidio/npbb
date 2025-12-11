import { describe, it, expect, vi, afterEach } from "vitest";
import { login, getMe } from "../auth";

type FetchResponse = {
  ok: boolean;
  status: number;
  statusText: string;
  text: () => Promise<string>;
};

function mockFetchSequence(responses: FetchResponse[]) {
  const fetchMock = vi.fn().mockImplementation(() => {
    const next = responses.shift();
    if (!next) {
      return Promise.reject(new Error("No more mocked responses"));
    }
    return Promise.resolve(next);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("auth service", () => {
  it("login success retorna token e usuário", async () => {
    const payload = {
      email: "user@example.com",
      password: "senha",
    };
    const mockRes: FetchResponse = {
      ok: true,
      status: 200,
      statusText: "OK",
      text: () =>
        Promise.resolve(
          JSON.stringify({
            access_token: "token123",
            token_type: "bearer",
            user: {
              id: 1,
              email: payload.email,
              tipo_usuario: "bb",
              funcionario_id: null,
              agencia_id: null,
            },
          }),
        ),
    };
    const fetchMock = mockFetchSequence([mockRes]);

    const res = await login(payload);

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringMatching(/\/auth\/login$/),
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
      }),
    );
    expect(res.access_token).toBe("token123");
    expect(res.user.email).toBe(payload.email);
  });

  it("login erro 401 lança exceção", async () => {
    const mockRes: FetchResponse = {
      ok: false,
      status: 401,
      statusText: "Unauthorized",
      text: () => Promise.resolve(JSON.stringify({ detail: "Credenciais inválidas" })),
    };
    mockFetchSequence([mockRes]);

    await expect(
      login({ email: "x@example.com", password: "errada" }),
    ).rejects.toThrow(/Credenciais inválidas/);
  });

  it("getMe retorna usuário com token válido", async () => {
    const mockRes: FetchResponse = {
      ok: true,
      status: 200,
      statusText: "OK",
      text: () =>
        Promise.resolve(
          JSON.stringify({
            id: 1,
            email: "user@example.com",
            tipo_usuario: "bb",
            funcionario_id: null,
            agencia_id: null,
          }),
        ),
    };
    const fetchMock = mockFetchSequence([mockRes]);

    const me = await getMe("token123");

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringMatching(/\/auth\/me$/),
      expect.objectContaining({
        headers: { Authorization: "Bearer token123" },
      }),
    );
    expect(me.email).toBe("user@example.com");
  });
});
