/** Alinhado ao restante do app (ex.: Register, IngressosPortal). */
export const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function isValidEmail(value: string): boolean {
  const t = value.trim();
  if (!t) return true;
  return EMAIL_REGEX.test(t);
}

/** E.164: + seguido de 7 a 15 digitos (primeiro digito 1-9). */
export const INTERNATIONAL_PHONE_COMPACT_REGEX = /^\+[1-9]\d{6,14}$/;

export function compactInternationalPhone(value: string): string {
  return value.replace(/\s/g, "").trim();
}

export function isValidInternationalPhone(value: string): boolean {
  const c = compactInternationalPhone(value);
  if (!c) return true;
  return INTERNATIONAL_PHONE_COMPACT_REGEX.test(c);
}

/** Mascara leve: + e grupos de ate 4 digitos (E.164 ate 15 digitos apos o +). */
export function formatInternationalPhoneInput(raw: string): string {
  const hadPlus = /^\s*\+/.test(raw);
  let digits = raw.replace(/\D/g, "");
  if (digits.length > 15) digits = digits.slice(0, 15);
  if (digits.length === 0) {
    return hadPlus ? "+" : "";
  }
  const parts: string[] = [];
  for (let i = 0; i < digits.length; i += 4) {
    parts.push(digits.slice(i, i + 4));
  }
  return `+${parts.join(" ")}`;
}

export function displayInternationalPhoneFromApi(api: string | null | undefined): string {
  const v = (api || "").trim();
  if (!v) return "";
  if (v.startsWith("+")) return formatInternationalPhoneInput(v);
  return v;
}
