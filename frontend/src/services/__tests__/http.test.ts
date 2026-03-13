import { describe, expect, it } from "vitest";

import { API_BASE_URL, resolveApiAssetUrl } from "../http";

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
