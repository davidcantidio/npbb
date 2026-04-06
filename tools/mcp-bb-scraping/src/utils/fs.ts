import { mkdir, stat, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

export async function ensureDir(path: string): Promise<void> {
  await mkdir(path, { recursive: true });
}

export async function validateOutDir(path: string): Promise<void> {
  const target = resolve(path);
  try {
    const info = await stat(target);
    if (!info.isDirectory()) {
      throw new Error(`Diretorio de saida invalido: ${path}. Informe um diretorio, nao um arquivo.`);
    }
  } catch (error) {
    const err = error as NodeJS.ErrnoException;
    if (err.code === "ENOENT") {
      try {
        await ensureDir(target);
        return;
      } catch {
        throw new Error(`Diretorio de saida invalido: ${path}. Nao foi possivel criar.`);
      }
    }
    if (err.code === "ENOTDIR") {
      throw new Error(`Diretorio de saida invalido: ${path}. Informe um diretorio valido.`);
    }
    throw new Error(`Diretorio de saida invalido: ${path}. ${err.message ?? "Erro ao acessar."}`);
  }
}

export async function writeJson(filePath: string, data: unknown): Promise<void> {
  await ensureDir(dirname(filePath));
  await writeFile(filePath, JSON.stringify(data, null, 2) + "\n", "utf8");
}
