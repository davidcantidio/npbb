import { describe, expect, it } from "vitest";

import { API_BASE_URL, ApiError, resolveApiAssetUrl, toApiErrorMessage } from "../http";

describe("resolveApiAssetUrl", () => {
  it("preserves data urls", () => {
    expect(resolveApiAssetUrl("data:image/svg+xml;base64,AAA")).toBe("data:image/svg+xml;base64,AAA");
  });

  it("preserves absolute urls", () => {
    expect(resolveApiAssetUrl("https://cdn.example/qr.svg")).toBe("https://cdn.example/qr.svg");
  });

  it("normalizes absolute backend paths against API_BASE_URL", () => {
    expect(resolveApiAssetUrl("/ativacoes/123/qr-code")).toBe(`${API_BASE_URL}/ativacoes/123/qr-code`);
  });

  it("normalizes relative backend paths against API_BASE_URL", () => {
    expect(resolveApiAssetUrl("ativacoes/123/qr-code")).toBe(`${API_BASE_URL}/ativacoes/123/qr-code`);
  });

  it("returns null for empty values", () => {
    expect(resolveApiAssetUrl("   ")).toBeNull();
    expect(resolveApiAssetUrl(null)).toBeNull();
  });
});

describe("toApiErrorMessage", () => {
  it("returns friendly timeout message instead of TIMEOUT detail", () => {
    const err = new ApiError({
      message: "Tempo limite da requisicao excedido.",
      status: 0,
      detail: "TIMEOUT",
      code: "TIMEOUT",
      method: "GET",
      url: "/api/foo",
    });
    expect(toApiErrorMessage(err, "fallback")).not.toBe("TIMEOUT");
    expect(toApiErrorMessage(err, "fallback")).toContain("Tempo limite");
  });

  it("returns friendly message for NETWORK_ERROR instead of raw detail", () => {
    const err = new ApiError({
      message: "Falha de rede ao comunicar com a API.",
      status: 0,
      detail: "NETWORK_ERROR",
      code: "NETWORK_ERROR",
      method: "GET",
      url: "/api/foo",
    });
    expect(toApiErrorMessage(err, "fallback")).not.toBe("NETWORK_ERROR");
    expect(toApiErrorMessage(err, "fallback")).toContain("Falha de rede");
  });

  it("uses fallback when transport ApiError has blank message", () => {
    const err = new ApiError({
      message: "   ",
      status: 0,
      detail: "TIMEOUT",
      code: "TIMEOUT",
      method: "GET",
      url: "/api/foo",
    });
    expect(toApiErrorMessage(err, "fallback")).toBe("fallback");
  });

  it("still prefers string detail for other ApiError codes", () => {
    const err = new ApiError({
      message: "Erro HTTP 400",
      status: 400,
      detail: "Campo invalido",
      code: "BAD_REQUEST",
      method: "POST",
      url: "/api/foo",
    });
    expect(toApiErrorMessage(err, "fallback")).toBe("Campo invalido");
  });
});
