import { stdin as input, stdout as output } from "node:process";
import { createInterface } from "node:readline/promises";
import { existsSync } from "node:fs";
import { copyFile, cp, rm } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { chromium, type Browser, type BrowserContext } from "playwright";
import { ensureDir } from "./utils/fs";
import { resolvePipelineRoot } from "./utils/root";

type Platform = "ig" | "x" | "tiktok";

const pipelineRoot = resolvePipelineRoot();

async function main(): Promise<void> {
  const args = parseArgs(process.argv.slice(2));
  if (args.has("help") || args.has("h")) {
    printUsage();
    process.exit(0);
  }

  const platform = (stringArg(args.get("platform"), "") as Platform) || null;
  if (platform !== "ig" && platform !== "x" && platform !== "tiktok") {
    throw new Error("Use `--platform ig`, `--platform x` ou `--platform tiktok`.");
  }

  const defaultOut =
    platform === "ig"
      ? resolve(pipelineRoot, "auth", "ig_state.json")
      : platform === "x"
        ? resolve(pipelineRoot, "auth", "x_state.json")
        : resolve(pipelineRoot, "auth", "tiktok_state.json");
  const outPath = resolve(pipelineRoot, stringArg(args.get("out"), defaultOut));
  const defaultUrl = platform === "ig" ? "https://www.instagram.com/" : platform === "x" ? "https://x.com/" : "https://www.tiktok.com/";
  const url = stringArg(args.get("url"), defaultUrl);
  const cdpEndpoint = stringArg(args.get("cdp"), "");
  const chromeUserDataDir = stringArg(args.get("chrome-user-data-dir"), "");
  const chromeProfileDir = stringArg(args.get("chrome-profile-dir"), "");
  const channel = stringArg(args.get("channel"), "") || (platform === "tiktok" ? "chrome" : "");

  await ensureDir(dirname(outPath));

  const { context, close, mode } = await openAuthContext({ cdpEndpoint, chromeUserDataDir, chromeProfileDir, channel });

  try {
    const page = await context.newPage();
    process.stdout.write(`\nAbrindo: ${url}\n`);
    try {
      await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30_000 });
    } catch (error) {
      process.stderr.write(`[WARN] Nao consegui abrir ${url}. Voce pode navegar manualmente no browser. Detalhes: ${String(error)}\n`);
    }
    if (mode === "cdp") process.stdout.write(`\n[CDP] Conectado a ${cdpEndpoint}\n`);
    if (mode === "chrome-profile") {
      process.stdout.write(
        [
          "",
          "[Chrome profile] Usando seu perfil local do Chrome.",
          "Dica: feche todas as janelas do Chrome antes de rodar este comando (para evitar erro de perfil em uso).",
        ].join("\n") + "\n",
      );
    }
    process.stdout.write(
      [
        "",
        "Faca login manualmente no navegador.",
        "Depois volte neste terminal.",
        "",
      ].join("\n"),
    );

    const rl = createInterface({ input, output });
    try {
      await rl.question(`Pressione ENTER para salvar em: ${outPath}\n`);
    } finally {
      rl.close();
    }

    await context.storageState({ path: outPath });
    process.stdout.write(`Salvo storageState em ${outPath}\n`);
    await warnIfLikelyNotLoggedIn(platform, outPath);
    await page.close().catch(() => undefined);
  } finally {
    await close();
  }
}

function printUsage(): void {
  process.stdout.write(
    [
      "Uso:",
      "  npm run auth -- --platform ig",
      "  npm run auth -- --platform x",
      "  npm run auth -- --platform tiktok",
      "  npm run auth:tiktok -- --cdp http://localhost:9222",
      "  npm run auth:tiktok -- --chrome-user-data-dir \"C:\\Users\\SEU_USUARIO\\AppData\\Local\\Google\\Chrome\\User Data\" --chrome-profile-dir Default",
      "",
      "Opcoes:",
      "  --platform <ig|x|tiktok>  Plataforma (obrigatorio)",
      "  --out <path>              Caminho do storageState (default: auth/ig_state.json, auth/x_state.json ou auth/tiktok_state.json)",
      "  --url <url>              URL inicial (default: instagram.com, x.com ou tiktok.com/login)",
      "  --cdp <endpoint>         Conecta em um Chrome ja aberto com --remote-debugging-port (ex: http://localhost:9222)",
      "  --chrome-user-data-dir <path>  Usa um perfil do Chrome via launchPersistentContext (requer Chrome fechado)",
      "  --chrome-profile-dir <name>    Nome do profile (ex: Default, Profile 1). Opcional.",
      "  --channel <name>          Canal do Chromium (ex: chrome, msedge). Default: tiktok usa 'chrome'.",
    ].join("\n") + "\n",
  );
}

function parseArgs(argv: string[]): Map<string, string | null> {
  const map = new Map<string, string | null>();
  for (let i = 0; i < argv.length; i++) {
    const raw = argv[i];
    if (!raw.startsWith("--")) continue;
    const trimmed = raw.slice(2);
    const eq = trimmed.indexOf("=");
    if (eq >= 0) {
      map.set(trimmed.slice(0, eq), trimmed.slice(eq + 1));
      continue;
    }
    const key = trimmed;
    const next = argv[i + 1];
    if (next && !next.startsWith("--")) {
      map.set(key, next);
      i++;
    } else {
      map.set(key, null);
    }
  }
  return map;
}

function stringArg(value: string | null | undefined, fallback: string): string {
  const v = (value ?? "").trim();
  return v ? v : fallback;
}

async function openAuthContext(
  options: {
    cdpEndpoint: string;
    chromeUserDataDir: string;
    chromeProfileDir: string;
    channel: string;
  },
): Promise<{ context: BrowserContext; close: () => Promise<void>; mode: "playwright" | "cdp" | "chrome-profile" }> {
  const cdpEndpoint = (options.cdpEndpoint ?? "").trim();
  const chromeUserDataDir = (options.chromeUserDataDir ?? "").trim();
  const chromeProfileDir = (options.chromeProfileDir ?? "").trim();
  const channel = (options.channel ?? "").trim();

  if (cdpEndpoint && chromeUserDataDir) {
    throw new Error("Use apenas um modo: --cdp OU --chrome-user-data-dir.");
  }

  if (!cdpEndpoint && !chromeUserDataDir) {
    let browser: Browser;
    if (channel) {
      try {
        browser = await chromium.launch({ headless: false, channel });
      } catch (error) {
        process.stderr.write(
          `[WARN] Nao foi possivel iniciar com --channel ${channel}; tentando modo padrao. Detalhes: ${String(error)}\n`,
        );
        browser = await chromium.launch({ headless: false });
      }
    } else {
      browser = await chromium.launch({ headless: false });
    }
    const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
    return {
      context,
      mode: "playwright",
      close: async () => {
        await context.close();
        await browser.close();
      },
    };
  }

  if (chromeUserDataDir) {
    const profileDir = chromeProfileDir || "Default";
    process.stdout.write(
      [
        "",
        `[Chrome profile] Preparando copia do perfil "${profileDir}" para uso no Playwright...`,
        "Feche todas as janelas do Chrome antes, ou a copia pode falhar por arquivos em uso.",
      ].join("\n") + "\n",
    );

    const clonedUserDataDir = await cloneChromeProfile(chromeUserDataDir, profileDir);

    const args: string[] = [];
    if (profileDir) args.push(`--profile-directory=${profileDir}`);
    const context = await chromium.launchPersistentContext(clonedUserDataDir, {
      channel: "chrome",
      headless: false,
      viewport: { width: 1280, height: 720 },
      args: args.length ? args : undefined,
    });

    return {
      context,
      mode: "chrome-profile",
      close: async () => {
        await context.close();
      },
    };
  }

  const browser: Browser = await chromium.connectOverCDP(cdpEndpoint);
  const context = browser.contexts()[0];
  if (!context) {
    await browser.close();
    throw new Error(
      "Nao foi possivel acessar o contexto default do Chrome via CDP. Inicie o Chrome com --remote-debugging-port=9222 e tente novamente.",
    );
  }

  return {
    context,
    mode: "cdp",
    close: async () => {
      await browser.close();
    },
  };
}

async function cloneChromeProfile(sourceUserDataDir: string, profileDir: string): Promise<string> {
  const sourceRoot = resolve(sourceUserDataDir);
  const sourceLocalState = join(sourceRoot, "Local State");
  const sourceProfile = join(sourceRoot, profileDir);

  if (!existsSync(sourceLocalState)) {
    throw new Error(`Nao encontrei o arquivo "Local State" em: ${sourceRoot}`);
  }
  if (!existsSync(sourceProfile)) {
    throw new Error(`Nao encontrei o profile "${profileDir}" em: ${sourceRoot}`);
  }

  const destRoot = resolve(pipelineRoot, "auth", "chrome_user_data");
  const destProfile = join(destRoot, profileDir);

  await rm(destRoot, { recursive: true, force: true });
  await ensureDir(destRoot);
  await ensureDir(destProfile);

  try {
    await copyFile(sourceLocalState, join(destRoot, "Local State"));
  } catch (error) {
    throw new Error(`Falha ao copiar "Local State". Feche o Chrome e tente novamente. Detalhes: ${String(error)}`);
  }

  // "Service Worker" pode ter dezenas de milhares de arquivos e costuma ser desnecessario para carregar sessao (cookies).
  const profileDirsToCopy = ["Network", "Local Storage", "Session Storage", "IndexedDB"];
  const profileFilesToCopy = ["Preferences", "Secure Preferences"];

  for (const dirName of profileDirsToCopy) {
    const src = join(sourceProfile, dirName);
    if (!existsSync(src)) continue;
    const dst = join(destProfile, dirName);
    process.stdout.write(`[Chrome profile] Copiando ${dirName}...\n`);
    try {
      await cp(src, dst, { recursive: true, force: true });
    } catch (error) {
      throw new Error(`Falha ao copiar "${dirName}". Feche o Chrome e tente novamente. Detalhes: ${String(error)}`);
    }
  }

  for (const fileName of profileFilesToCopy) {
    const src = join(sourceProfile, fileName);
    if (!existsSync(src)) continue;
    const dst = join(destProfile, fileName);
    process.stdout.write(`[Chrome profile] Copiando ${fileName}...\n`);
    try {
      await copyFile(src, dst);
    } catch (error) {
      throw new Error(`Falha ao copiar "${fileName}". Feche o Chrome e tente novamente. Detalhes: ${String(error)}`);
    }
  }

  process.stdout.write(`[Chrome profile] Copia pronta em: ${destRoot}\n`);
  return destRoot;
}

async function warnIfLikelyNotLoggedIn(platform: Platform, storageStatePath: string): Promise<void> {
  if (platform !== "tiktok") return;
  try {
    const { readFile } = await import("node:fs/promises");
    const raw = await readFile(storageStatePath, "utf-8");
    const data = JSON.parse(raw) as { cookies?: Array<{ name?: string; domain?: string }> };
    const cookies = Array.isArray(data.cookies) ? data.cookies : [];
    const tiktokCookies = cookies.filter((c) => String(c.domain ?? "").includes("tiktok"));
    const names = new Set(tiktokCookies.map((c) => String(c.name ?? "")));

    const sessionCookieNames = ["sessionid", "sessionid_ss", "sid_tt", "sid_guard", "uid_tt", "passport_auth_status", "passport_auth_status_ss"];
    const hasAnySessionCookie = sessionCookieNames.some((name) => names.has(name));

    if (!hasAnySessionCookie) {
      process.stderr.write(
        [
          "",
          "[WARN] O storageState do TikTok parece NAO estar logado (nao encontrei cookies de sessao como sessionid/sid_tt).",
          "Se voce clicou em \"Continuar com Google\" nessa janela, o Google pode bloquear por ser um browser automatizado.",
          "Sugestao: faca login no TikTok no Chrome normal (ou use login por telefone/email/QR code), depois rode este comando e apenas confirme que ja esta logado antes de salvar.",
          "",
        ].join("\n") + "\n",
      );
    }
  } catch {
    // best effort
  }
}

main().catch((error) => {
  process.stderr.write(String(error) + "\n");
  process.exitCode = 1;
});
