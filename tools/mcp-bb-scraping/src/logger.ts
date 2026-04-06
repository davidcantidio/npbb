import { createWriteStream, WriteStream } from "node:fs";
import { ensureDir } from "./utils/fs";
import { escapeCsvValue } from "./utils/csv";
import { outputPath } from "./utils/output";

export class Logger {
  private csv: WriteStream;
  private log: WriteStream;

  private constructor(csv: WriteStream, log: WriteStream) {
    this.csv = csv;
    this.log = log;
  }

  static async create(outDir: string, handle: string | null = null): Promise<Logger> {
    await ensureDir(outDir);
    const csvPath = outputPath(outDir, "run", "csv", handle);
    const logPath = outputPath(outDir, "run", "log", handle);

    const csv = createWriteStream(csvPath, { flags: "w" });
    csv.write("\ufeffdatetime;level;message\r\n");

    const log = createWriteStream(logPath, { flags: "w" });

    return new Logger(csv, log);
  }

  info(message: string): void {
    this.write("INFO", message);
  }

  warn(message: string): void {
    this.write("WARN", message);
  }

  error(message: string): void {
    this.write("ERROR", message);
  }

  close(): void {
    this.csv.end();
    this.log.end();
  }

  private write(level: string, message: string): void {
    const datetime = new Date().toISOString();
    const consoleLine = `${datetime} [${level}] ${message}\n`;
    process.stdout.write(consoleLine);
    this.log.write(consoleLine);

    const delimiter = ";";
    const cleanMessage = normalizeLogMessage(message);
    const row = [datetime, level, cleanMessage].map((v) => escapeCsvValue(v, delimiter)).join(delimiter) + "\r\n";
    this.csv.write(row);
  }
}

function normalizeLogMessage(message: string): string {
  return String(message ?? "").replace(/\s+/g, " ").trim();
}
