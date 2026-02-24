import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const DIST_DIR = path.join(ROOT_DIR, "dist");
const REPORT_DIR = path.join(ROOT_DIR, "reports", "build");

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

async function listFiles(dir) {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...(await listFiles(fullPath)));
      continue;
    }
    files.push(fullPath);
  }
  return files;
}

async function main() {
  const files = await listFiles(DIST_DIR);
  const stats = await Promise.all(
    files.map(async (file) => ({
      file: path.relative(DIST_DIR, file).replace(/\\/g, "/"),
      size: (await fs.stat(file)).size,
    })),
  );

  stats.sort((a, b) => b.size - a.size);
  const top = stats.slice(0, 10);
  const totalSize = stats.reduce((sum, item) => sum + item.size, 0);

  console.log("Top 10 chunks/assets por tamanho:");
  for (const item of top) {
    console.log(`- ${item.file}: ${formatBytes(item.size)}`);
  }
  console.log(`Total dist: ${formatBytes(totalSize)}`);

  const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
  await fs.mkdir(REPORT_DIR, { recursive: true });
  const reportPath = path.join(REPORT_DIR, `${timestamp}.json`);
  await fs.writeFile(
    reportPath,
    JSON.stringify(
      {
        generated_at: new Date().toISOString(),
        total_size_bytes: totalSize,
        top_assets: top,
        all_assets: stats,
      },
      null,
      2,
    ),
    "utf8",
  );

  console.log(`Relatorio salvo em ${path.relative(ROOT_DIR, reportPath)}`);
}

main().catch((error) => {
  console.error("Falha ao gerar build stats:", error.message || error);
  process.exitCode = 1;
});
