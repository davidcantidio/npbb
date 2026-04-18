import { describe, expect, it } from "vitest";

import {
  compactInternationalPhone,
  formatInternationalPhoneInput,
  isValidEmail,
  isValidInternationalPhone,
} from "../contactValidation";

describe("contactValidation", () => {
  it("isValidEmail aceita vazio e formato basico", () => {
    expect(isValidEmail("")).toBe(true);
    expect(isValidEmail("  ")).toBe(true);
    expect(isValidEmail("a@b.co")).toBe(true);
    expect(isValidEmail("nao-email")).toBe(false);
    expect(isValidEmail("@dominio.com")).toBe(false);
  });

  it("isValidInternationalPhone aceita vazio e E.164", () => {
    expect(isValidInternationalPhone("")).toBe(true);
    expect(isValidInternationalPhone("+5511987654321")).toBe(true);
    expect(isValidInternationalPhone("+1 415 555 2671")).toBe(true);
    expect(compactInternationalPhone("+1 415 555 2671")).toBe("+14155552671");
    expect(isValidInternationalPhone("+0123")).toBe(false);
    expect(isValidInternationalPhone("5511987654321")).toBe(false);
  });

  it("formatInternationalPhoneInput aplica grupos e limite E.164", () => {
    expect(formatInternationalPhoneInput("")).toBe("");
    expect(formatInternationalPhoneInput("+")).toBe("+");
    expect(formatInternationalPhoneInput("+5511987654321")).toBe("+5511 9876 5432 1");
    expect(formatInternationalPhoneInput("5511987654321")).toBe("+5511 9876 5432 1");
    const long = "1".repeat(20);
    expect(formatInternationalPhoneInput(long).replace(/\D/g, "").length).toBe(15);
  });
});
