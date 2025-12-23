const NON_DIGITS = /\D+/g;

const KNOWN_INVALID = new Set(["12345678909"]);

export function normalizeCpf(value: string): string {
  return String(value || "").replace(NON_DIGITS, "").trim();
}

function calcCheckDigit(numbers: number[], startWeight: number): number {
  let total = 0;
  let weight = startWeight;
  for (const n of numbers) {
    total += n * weight;
    weight -= 1;
  }
  const remainder = total % 11;
  return remainder < 2 ? 0 : 11 - remainder;
}

export function isValidCpf(value: string, opts?: { allowKnownInvalid?: boolean }): boolean {
  const digits = normalizeCpf(value);
  if (digits.length !== 11) return false;
  if (digits === digits[0]!.repeat(11)) return false;
  if (!opts?.allowKnownInvalid && KNOWN_INVALID.has(digits)) return false;

  const numbers = [...digits].map((c) => Number(c));
  if (numbers.some((n) => Number.isNaN(n))) return false;

  const first = calcCheckDigit(numbers.slice(0, 9), 10);
  if (first !== numbers[9]) return false;

  const second = calcCheckDigit(numbers.slice(0, 10), 11);
  if (second !== numbers[10]) return false;

  return true;
}

