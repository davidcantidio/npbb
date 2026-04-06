export function parseCompactNumber(input: string): number | null {
  const text = input.trim();
  if (!text) return null;

  const normalized = text.replace(/\s+/g, "");
  const match = normalized.match(/^(-?[\d.,]+)([A-Za-zÀ-ÿ]+)?$/);
  if (!match) return parseIntegerLike(text);

  const numberPart = match[1];
  const suffixRaw = String(match[2] ?? "");
  const multiplier = suffixToMultiplier(suffixRaw);

  if (multiplier != null) {
    const value = parseLocaleFloat(numberPart);
    if (value == null) return null;
    return Math.round(value * multiplier);
  }

  const digitsOnly = numberPart.replace(/[.,]/g, "");
  if (!digitsOnly) return null;
  const value = Number(digitsOnly);
  return Number.isFinite(value) ? value : null;
}

function parseIntegerLike(text: string): number | null {
  const normalized = text.replace(/[^\d]/g, "");
  if (!normalized) return null;
  const value = Number(normalized);
  return Number.isFinite(value) ? value : null;
}

function parseLocaleFloat(text: string): number | null {
  const raw = String(text ?? "").trim();
  if (!raw) return null;

  const hasDot = raw.includes(".");
  const hasComma = raw.includes(",");

  let normalized = raw;
  if (hasDot && hasComma) {
    // pt-BR típico: 1.234,5
    normalized = raw.replace(/\./g, "").replace(/,/g, ".");
  } else if (hasComma) {
    // 20,5 -> 20.5
    normalized = raw.replace(/,/g, ".");
  } else if (hasDot) {
    // Decide se é separador de milhar (1.234) ou decimal (1.2)
    const parts = raw.split(".");
    const last = parts[parts.length - 1] ?? "";
    if (parts.length > 1 && last.length === 3) normalized = parts.join("");
  }

  const value = Number(normalized);
  return Number.isFinite(value) ? value : null;
}

function suffixToMultiplier(input: string): number | null {
  const raw = String(input ?? "").trim();
  if (!raw) return null;

  const clean = raw
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();

  if (clean === "k" || clean === "mil") return 1_000;
  if (clean === "m" || clean === "mi" || clean.startsWith("milhao") || clean.startsWith("milhoes")) return 1_000_000;
  if (clean === "b" || clean === "bi" || clean.startsWith("bilhao") || clean.startsWith("bilhoes")) return 1_000_000_000;

  return null;
}
