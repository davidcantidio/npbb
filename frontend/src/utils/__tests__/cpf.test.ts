import { describe, it, expect } from "vitest";

import { isValidCpf, normalizeCpf } from "../cpf";

describe("cpf utils", () => {
  it("normalizeCpf remove pontuacao", () => {
    expect(normalizeCpf("529.982.247-25")).toBe("52998224725");
  });

  it("isValidCpf valida CPFs validos", () => {
    expect(isValidCpf("529.982.247-25")).toBe(true);
    expect(isValidCpf("11144477735")).toBe(true);
  });

  it("isValidCpf rejeita digitos verificadores invalidos", () => {
    expect(isValidCpf("52998224726")).toBe(false);
  });

  it("isValidCpf rejeita repeticao de digitos", () => {
    expect(isValidCpf("000.000.000-00")).toBe(false);
  });

  it("isValidCpf rejeita sequencia placeholder conhecida", () => {
    expect(isValidCpf("123.456.789-09")).toBe(false);
  });
});

