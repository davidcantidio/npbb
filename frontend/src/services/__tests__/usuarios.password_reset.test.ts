import { describe, it, expect, vi, afterEach } from "vitest";
import { ApiError, forgotPassword, resetPassword } from "../usuarios";

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

describe("usuarios service - password recovery", () => {
  it("forgotPassword success retorna message (e debug fields se existirem)", async () => {
    const mockRes: FetchResponse = {
      ok: true,
      status: 200,
      statusText: "OK",
      text: () =>
        Promise.resolve(
          JSON.stringify({
            message: "Email de recuperacao enviado",
            token: "debug-token",
            reset_url: "http://localhost:5173/reset-password?token=debug-token",
          }),
        ),
    };
    const fetchMock = mockFetchSequence([mockRes]);

    const res = await forgotPassword("user@example.com");

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringMatching(/\/usuarios\/forgot-password$/),
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
      }),
    );
    expect(res.message).toMatch(/Email/);
  });

  it("forgotPassword 404 lança ApiError com detail estruturado", async () => {
    const mockRes: FetchResponse = {
      ok: false,
      status: 404,
      statusText: "Not Found",
      text: () =>
        Promise.resolve(
          JSON.stringify({
            detail: { code: "USER_NOT_FOUND", message: "Email nao encontrado", field: "email" },
          }),
        ),
    };
    mockFetchSequence([mockRes]);

    await expect(forgotPassword("missing@example.com")).rejects.toMatchObject<ApiError>({
      status: 404,
      detail: { code: "USER_NOT_FOUND", field: "email" },
    });
  });

  it("resetPassword success retorna message", async () => {
    const mockRes: FetchResponse = {
      ok: true,
      status: 200,
      statusText: "OK",
      text: () => Promise.resolve(JSON.stringify({ message: "Senha atualizada com sucesso" })),
    };
    const fetchMock = mockFetchSequence([mockRes]);

    const res = await resetPassword("token123", "Nova123");

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringMatching(/\/usuarios\/reset-password$/),
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
      }),
    );
    expect(res.message).toMatch(/Senha/);
  });

  it("resetPassword token expirado lança ApiError", async () => {
    const mockRes: FetchResponse = {
      ok: false,
      status: 400,
      statusText: "Bad Request",
      text: () =>
        Promise.resolve(JSON.stringify({ detail: { code: "TOKEN_EXPIRED", message: "Token expirado" } })),
    };
    mockFetchSequence([mockRes]);

    await expect(resetPassword("token123", "Nova123")).rejects.toMatchObject<ApiError>({
      status: 400,
      detail: { code: "TOKEN_EXPIRED" },
    });
  });
});

