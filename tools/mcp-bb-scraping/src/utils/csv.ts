export interface CsvOptions {
  delimiter?: string;
  newline?: "\n" | "\r\n";
  includeBom?: boolean;
}

export function escapeCsvValue(value: string, delimiter = ";"): string {
  let v = value ?? "";
  if (v.includes('"')) v = v.replace(/"/g, '""');
  const mustQuote = v.includes(delimiter) || v.includes("\n") || v.includes("\r") || v.includes('"');
  return mustQuote ? `"${v}"` : v;
}

export function toCsv(headers: string[], rows: string[][], options: CsvOptions = {}): string {
  const delimiter = options.delimiter ?? ";";
  const newline = options.newline ?? "\r\n";
  const includeBom = options.includeBom ?? true;

  const out: string[] = [];
  out.push(headers.map((h) => escapeCsvValue(h, delimiter)).join(delimiter));
  for (const row of rows) {
    out.push(row.map((cell) => escapeCsvValue(cell, delimiter)).join(delimiter));
  }

  const content = out.join(newline) + newline;
  return includeBom ? "\ufeff" + content : content;
}
