import { existsSync } from "node:fs";
import { unlink } from "node:fs/promises";
import { resolve, join, basename } from "node:path";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { chromium, type BrowserContext } from "playwright";
import { launchBrowser, newContext } from "./browser";
import { Logger } from "./logger";
import { scrapeInstagram } from "./scrapers/instagram";
import { scrapeTikTok } from "./scrapers/tiktok";
import { scrapeX } from "./scrapers/x";
import { buildSummary } from "./summary";
import type { InstagramPost, ProfileSnapshot, RunConfig, TikTokProfileSnapshot, TikTokVideo, XTweet } from "./types";
import { parseArgs, parseIntArg, stringArg, dateArg } from "./utils/args";
import { validateOutDir } from "./utils/fs";
import { outputPath, outputPostsPath, sanitizeHandle, sanitizeLabel } from "./utils/output";
import { listAthleteHandles, lookupAthleteName } from "./utils/athletes";
import { resolvePipelineRoot } from "./utils/root";
import {
  buildInstagramProfileUrl,
  buildTikTokProfileUrl,
  buildXProfileUrl,
  normalizeProfileHandle,
} from "./utils/profile";
import {
  writeInstagramPostsCsv,
  writeInstagramPostsEnrichedCsv,
  writeInstagramPostsEnrichedJson,
  writeInstagramProfileCsv,
  writeInstagramProfileJson,
  writeUnifiedPostsCsv,
  writeIgLinksCsv,
  writeSummaryCsv,
  writeTikTokLinksCsv,
  writeTikTokVideosCsv,
  writeTikTokProfileCsv,
  writeXTweetsCsv,
  writeXProfileCsv,
} from "./writers";

const execFileAsync = promisify(execFile);

export async function run(argv: string[]): Promise<void> {
  const args = parseArgs(argv);
  if (args.has("help") || args.has("h")) {
    printUsage();
    process.exit(0);
  }
  if (args.has("all-athletes")) {
    await runAllAthletes(argv, args);
    return;
  }

  const config = parseRunConfig(argv);
  await runSingle(config);
}

function stripArg(argv: string[], key: string): string[] {
  const out: string[] = [];
  for (let i = 0; i < argv.length; i++) {
    const raw = argv[i];
    if (raw === `--${key}`) {
      const next = argv[i + 1];
      if (next && !next.startsWith("--")) i += 1;
      continue;
    }
    if (raw.startsWith(`--${key}=`)) continue;
    out.push(raw);
  }
  return out;
}

function isBatchEligibleStatus(status: string): boolean {
  const safe = status.trim().toLowerCase();
  return safe !== "alias" && safe !== "missing_handle";
}

async function runAllAthletes(argv: string[], args: Map<string, string | null>): Promise<void> {
  const pipelineRoot = resolvePipelineRoot();
  const requestedStatuses = new Set(parseListArg(args.get("all-status")).map((v) => v.toLowerCase()));

  const athletes = listAthleteHandles(pipelineRoot).filter((athlete) => {
    if (!athlete.handle) return false;
    if (requestedStatuses.size > 0) return requestedStatuses.has(athlete.status);
    return isBatchEligibleStatus(athlete.status);
  });

  if (!athletes.length) {
    throw new Error("Nenhum atleta elegivel encontrado em config/instagram_handles.csv para --all-athletes.");
  }

  let baseArgv = [...argv];
  for (const key of ["all-athletes", "all-status", "profile", "perfil", "ig-url", "x-url", "tiktok-url", "h", "help"]) {
    baseArgv = stripArg(baseArgv, key);
  }

  process.stdout.write(
    `Modo lote (--all-athletes): ${athletes.length} atletas selecionados. Filtro status=${requestedStatuses.size ? [...requestedStatuses].join(",") : "default"}\n`,
  );

  let failures = 0;
  for (let index = 0; index < athletes.length; index++) {
    const athlete = athletes[index];
    const runArgv = [...baseArgv, "--profile", athlete.handle];
    process.stdout.write(`\n[${index + 1}/${athletes.length}] ${athlete.handle}${athlete.name ? ` (${athlete.name})` : ""}\n`);
    try {
      const config = parseRunConfig(runArgv);
      await runSingle(config);
    } catch (error) {
      failures += 1;
      process.stderr.write(`Falha no atleta ${athlete.handle}: ${String(error)}\n`);
    }
  }

  process.stdout.write(`\nLote concluido: total=${athletes.length}, falhas=${failures}\n`);
  if (failures > 0) process.exitCode = 1;
}

async function runSingle(config: RunConfig): Promise<void> {
  await validateOutDir(config.outDir);
  await removeLegacyJsonOutputs(config.outDir);
  const logger = await Logger.create(config.outDir, config.outputHandle);
  for (const warning of config.authWarnings) {
    logger.warn(warning);
  }
  logger.info(
    `Iniciando scraping: out=${config.outDir}, max=${config.max}, since=${config.since ? config.since.toISOString() : "null"}, until=${config.until ? config.until.toISOString() : "null"}`,
  );

  const useCdp = config.cdpEndpoint != null;
  const browser = useCdp ? await chromium.connectOverCDP(config.cdpEndpoint!) : await launchBrowser({ headless: !config.headful });
  const sharedContext: BrowserContext | null = useCdp ? browser.contexts()[0] ?? null : null;
  if (useCdp) {
    if (!sharedContext) {
      await browser.close();
      throw new Error(
        "Nao foi possivel acessar o contexto default do Chrome via CDP. Inicie o Chrome com --remote-debugging-port=9222 e tente novamente.",
      );
    }
    logger.info(`Conectado via CDP: ${config.cdpEndpoint}`);
  }
  let didAny = false;

  try {
    let instagramPosts: InstagramPost[] = [];
    let xTweets: XTweet[] = [];
    let tiktokVideos: TikTokVideo[] = [];
    const nowIso = new Date().toISOString();

    if (config.scrapeInstagram) {
      try {
        const context =
          sharedContext ??
          (await newContext(browser, {
            storageStatePath: config.instagramStorageStatePath,
            viewport: { width: 1280, height: 720 },
            locale: config.locale,
          }));
        const { posts, enrichedPosts, profile, debug } = await scrapeInstagram(context, {
          profileUrl: config.instagramProfileUrl,
          max: config.max,
          since: config.since,
          until: config.until,
          logger,
          timeoutMs: config.timeoutMs,
          debug: config.debug,
          hasAuth: sharedContext != null || config.instagramStorageStatePath != null,
          bbAliases: config.bbAliases,
        });
        if (!sharedContext) await context.close();

        instagramPosts = posts;
        await writeInstagramPostsCsv(config.outDir, posts, config.outputHandle);
        await writeInstagramPostsEnrichedCsv(config.outDir, enrichedPosts, config.outputHandle, config.athleteName);
        await writeInstagramPostsEnrichedJson(config.outDir, enrichedPosts, config.outputHandle, config.athleteName);
        await writeInstagramProfileCsv(config.outDir, profile, config.outputHandle);
        await writeInstagramProfileJson(config.outDir, profile, config.outputHandle);
        if (config.debug) await writeIgLinksCsv(config.outDir, debug.links, config.outputHandle);

        didAny = true;
      } catch (error) {
        logger.error(`Instagram: erro geral: ${String(error)}`);
        await writeInstagramPostsCsv(config.outDir, [], config.outputHandle);
        await writeInstagramPostsEnrichedCsv(config.outDir, [], config.outputHandle, config.athleteName);
        await writeInstagramPostsEnrichedJson(config.outDir, [], config.outputHandle, config.athleteName);
        await writeInstagramProfileCsv(config.outDir, emptyProfile(config.instagramProfileUrl, nowIso), config.outputHandle);
        await writeInstagramProfileJson(config.outDir, emptyProfile(config.instagramProfileUrl, nowIso), config.outputHandle);
      }
    }

    if (config.scrapeX) {
      try {
        const context =
          sharedContext ??
          (await newContext(browser, {
            storageStatePath: config.xStorageStatePath,
            viewport: { width: 1280, height: 720 },
            locale: config.locale,
          }));
        const { tweets, profile } = await scrapeX(context, {
          profileUrl: config.xProfileUrl,
          max: config.max,
          since: config.since,
          until: config.until,
          logger,
          timeoutMs: config.timeoutMs,
        });
        if (!sharedContext) await context.close();

        xTweets = tweets;
        await writeXTweetsCsv(config.outDir, tweets, config.outputHandle);
        await writeXProfileCsv(config.outDir, profile, config.outputHandle);
        didAny = true;
      } catch (error) {
        logger.error(`X: erro geral: ${String(error)}`);
        await writeXTweetsCsv(config.outDir, [], config.outputHandle);
        await writeXProfileCsv(config.outDir, emptyProfile(config.xProfileUrl, nowIso), config.outputHandle);
      }
    }

    let tiktokProfile: TikTokProfileSnapshot | null = null;
    if (config.scrapeTikTok) {
      try {
        const context =
          sharedContext ??
          (await newContext(browser, {
            storageStatePath: config.tiktokStorageStatePath,
            viewport: { width: 1280, height: 720 },
            locale: config.locale,
          }));
        const { videos, profile, debug } = await scrapeTikTok(context, {
          profileUrl: config.tiktokProfileUrl,
          max: config.max,
          since: config.since,
          until: config.until,
          logger,
          timeoutMs: config.timeoutMs,
          debug: config.debug,
          hasAuth: sharedContext != null || config.tiktokStorageStatePath != null,
        });
        if (!sharedContext) await context.close();

        tiktokVideos = videos;
        tiktokProfile = profile;
        await writeTikTokVideosCsv(config.outDir, videos, config.outputHandle);
        await writeTikTokProfileCsv(config.outDir, profile, config.outputHandle);
        if (config.debug) await writeTikTokLinksCsv(config.outDir, debug.links, config.outputHandle);
        didAny = true;
      } catch (error) {
        logger.error(`TikTok: erro geral: ${String(error)}`);
        await writeTikTokVideosCsv(config.outDir, [], config.outputHandle);
        await writeTikTokProfileCsv(config.outDir, emptyTikTokProfile(config.tiktokProfileUrl, nowIso), config.outputHandle);
      }
    }

    await writeUnifiedPostsCsv(config.outDir, instagramPosts, xTweets, tiktokVideos, config.outputHandle);
    const summary = buildSummary(instagramPosts, xTweets, tiktokVideos);
    await writeSummaryCsv(config.outDir, summary, config.outputHandle);
    await runIndicators(config, logger);
    await runDeterministicReport(config, logger);
    verifyInstagramOutputs(config, logger);
  } finally {
    await browser.close();
    logger.close();
  }

  printOutputs(config);
  if (!didAny) process.exitCode = 1;
}

function parseRunConfig(argv: string[]): RunConfig {
  const args = parseArgs(argv);

  const pipelineRoot = resolvePipelineRoot();
  const maxArg = args.get("max");
  if (args.has("max") && !(maxArg ?? "").trim()) {
    throw new Error("Valor invalido em --max: vazio. Use inteiro > 0.");
  }
  const max = parseIntArg(maxArg, 150, "max");
  const outArg = args.get("out");
  if (args.has("out") && !(outArg ?? "").trim()) {
    throw new Error("Valor invalido em --out: vazio. Informe um diretorio.");
  }
  const sinceArg = args.get("since");
  if (args.has("since") && !(sinceArg ?? "").trim()) {
    throw new Error("Valor invalido em --since: vazio. Use YYYY-MM-DD.");
  }
  const since = dateArg(sinceArg, "since");
  const untilArg = args.get("until");
  if (args.has("until") && !(untilArg ?? "").trim()) {
    throw new Error("Valor invalido em --until: vazio. Use YYYY-MM-DD.");
  }
  const untilStart = dateArg(untilArg, "until");
  const until = untilStart ? endOfDayUtc(untilStart) : null;
  if (since && until && since.getTime() > until.getTime()) {
    throw new Error("Intervalo invalido: --since deve ser menor ou igual a --until.");
  }
  const headful = args.has("headful");
  const debug = args.has("debug");
  const timeoutArg = args.get("timeout");
  if (args.has("timeout") && !(timeoutArg ?? "").trim()) {
    throw new Error("Valor invalido em --timeout: vazio. Use inteiro > 0.");
  }
  const timeoutMs = parseIntArg(timeoutArg, 30_000, "timeout");
  const locale = stringArg(args.get("locale"), "pt-BR");
  const cdpEndpointRaw = stringArg(args.get("cdp"), "").trim();
  const cdpEndpoint = cdpEndpointRaw ? cdpEndpointRaw : null;
  const bbAliases = parseListArg(args.get("bb-aliases"));
  const authWarnings: string[] = [];

  const warnMissingAuth = (key: string, raw: string | null | undefined): void => {
    const v = (raw ?? "").trim();
    if (!v) return;
    const candidate = resolve(pipelineRoot, v);
    if (!existsSync(candidate)) {
      authWarnings.push(`Auth: caminho nao encontrado para --${key}: ${candidate}. Continuando sem auth.`);
    }
  };

  const profileArg = args.get("profile") ?? args.get("perfil");
  const profileHandle = normalizeProfileHandle(profileArg);
  if ((args.has("profile") || args.has("perfil")) && !profileHandle) {
    throw new Error("Perfil invalido em --profile/--perfil. Use @handle, handle ou URL do perfil.");
  }
  const defaultInstagramProfileUrl = profileHandle ? buildInstagramProfileUrl(profileHandle) : "https://www.instagram.com/filipetoledo/";
  const defaultXProfileUrl = profileHandle ? buildXProfileUrl(profileHandle) : "https://x.com/Filipetoledo77";
  const defaultTikTokProfileUrl = profileHandle ? buildTikTokProfileUrl(profileHandle) : "https://www.tiktok.com/@filipetoledo";

  const instagramProfileUrl = stringArg(args.get("ig-url"), defaultInstagramProfileUrl);
  const xProfileUrl = stringArg(args.get("x-url"), defaultXProfileUrl);
  const tiktokProfileUrl = stringArg(args.get("tiktok-url"), defaultTikTokProfileUrl);

  const scrapeInstagram = !args.has("no-ig");
  const scrapeX = !args.has("no-x");
  const scrapeTikTok = !args.has("no-tiktok");
  if (!scrapeInstagram && !scrapeX && !scrapeTikTok) {
    throw new Error("Nada para fazer: use sem `--no-ig`/`--no-x`, ou selecione ao menos uma plataforma.");
  }

  const outputHandle =
    profileHandle ??
    normalizeProfileHandle(
      (scrapeInstagram ? instagramProfileUrl : null) ??
        (scrapeX ? xProfileUrl : null) ??
        (scrapeTikTok ? tiktokProfileUrl : null),
    );

  const authIgArg = args.get("auth-ig");
  const authXArg = args.get("auth-x");
  const authTikTokArg = args.get("auth-tiktok");
  warnMissingAuth("auth-ig", authIgArg);
  warnMissingAuth("auth-x", authXArg);
  warnMissingAuth("auth-tiktok", authTikTokArg);

  const instagramStorageStatePath = storageStatePathArg(
    authIgArg,
    [resolve(pipelineRoot, "auth", "ig_state.json"), resolve(pipelineRoot, "auth", "instagram.json")],
    pipelineRoot,
  );
  const xStorageStatePath = storageStatePathArg(
    authXArg,
    [resolve(pipelineRoot, "auth", "x_state.json"), resolve(pipelineRoot, "auth", "x.json")],
    pipelineRoot,
  );
  const tiktokStorageStatePath = storageStatePathArg(
    authTikTokArg,
    [resolve(pipelineRoot, "auth", "tiktok_state.json")],
    pipelineRoot,
  );

  const athleteName = lookupAthleteName(outputHandle, pipelineRoot);
  const athleteDirName = sanitizeLabel(athleteName) ?? sanitizeHandle(outputHandle);
  const handleDirName = sanitizeHandle(outputHandle);
  const outRoot = resolve(pipelineRoot, stringArg(outArg, "out"));
  const outDir =
    athleteDirName && basename(outRoot).toLowerCase() !== athleteDirName
      ? resolve(outRoot, athleteDirName)
      : outRoot;

  const outRootBase = basename(outRoot).toLowerCase();
  if (athleteDirName && handleDirName && athleteDirName !== handleDirName) {
    const canonicalDir = resolve(outRoot, athleteDirName);
    const legacyHandleDir = resolve(outRoot, handleDirName);
    if (outRootBase === handleDirName) {
      authWarnings.push(
        `Saida: --out aponta para pasta legada por handle (${outRoot}). O pipeline atual vai gravar em ${canonicalDir}.`,
      );
    } else if (outRootBase !== athleteDirName && existsSync(legacyHandleDir)) {
      authWarnings.push(
        `Saida: pasta legada detectada (${legacyHandleDir}). O pipeline atual grava em ${canonicalDir}.`,
      );
    }
  }

  return {
    max,
    outDir,
    outputHandle,
    athleteName,
    since,
    until,
    headful,
    debug,
    timeoutMs,
    locale,
    cdpEndpoint,
    bbAliases,
    authWarnings,
    instagramProfileUrl,
    xProfileUrl,
    tiktokProfileUrl,
    instagramStorageStatePath,
    xStorageStatePath,
    tiktokStorageStatePath,
    scrapeInstagram,
    scrapeX,
    scrapeTikTok,
  };
}

function storageStatePathArg(explicit: string | null | undefined, defaultPaths: string[], rootDir: string): string | null {
  const v = (explicit ?? "").trim();
  if (v) {
    const candidate = resolve(rootDir, v);
    return existsSync(candidate) ? candidate : null;
  }

  for (const candidate of defaultPaths) {
    if (existsSync(candidate)) return candidate;
  }

  return null;
}

function parseListArg(value: string | null | undefined): string[] {
  const raw = (value ?? "").trim();
  if (!raw) return [];
  return raw
    .split(",")
    .map((v) => v.trim())
    .filter(Boolean);
}

function formatDateOnly(value: Date | null): string | null {
  if (!value) return null;
  return value.toISOString().slice(0, 10);
}

function endOfDayUtc(value: Date): Date {
  const out = new Date(value.getTime());
  out.setUTCHours(23, 59, 59, 999);
  return out;
}

function printUsage(): void {
  process.stdout.write(
    [
      "Uso:",
      "  npm run scrape -- --max 150 --out out --since 2024-01-01",
      "  npm run scrape -- --all-athletes --no-x --no-tiktok --since 2026-02-01 --until 2026-02-15 --out out",
      "",
      "Opcoes:",
      "  --max <n>         Maximo de itens por plataforma (default: 150)",
      "  --out <dir>       Diretorio base de saida (default: out)",
      "  --since <date>    Data minima (YYYY-MM-DD) para filtrar (opcional)",
      "  --until <date>    Data maxima (YYYY-MM-DD, inclusiva) para filtrar (opcional)",
      "  --profile <h>     Perfil base (handle) para IG/X/TikTok (alias: --perfil)",
      "  --all-athletes    Roda em lote para todos os handles de config/instagram_handles.csv",
      "  --all-status <l>  Filtro de status no lote (csv, ex: confirmed,needs_confirmation)",
      "  --headful         Abre navegador visivel (util para debug/login)",
      "  --debug           Gera artefatos extras (ex: ig_links_<handle>.csv)",
      "  --cdp <url>       Conecta a um Chrome ja aberto via CDP (ex: http://127.0.0.1:9222)",
      "  --timeout <ms>    Timeout padrao de navegacao/acoes (default: 30000)",
      "  --bb-aliases <v>  Aliases extras do BB (comma-separated, ex: #squadbb,#tamojuntobb)",
      "  --locale <tag>    Locale do navegador (default: pt-BR)",
      "  --no-ig           Nao coletar Instagram",
      "  --no-x            Nao coletar X",
      "  --no-tiktok       Nao coletar TikTok",
      "  --auth-ig <path>  Caminho do storageState do Instagram (default: auth/ig_state.json ou auth/instagram.json se existir)",
      "  --auth-x <path>   Caminho do storageState do X (default: auth/x_state.json ou auth/x.json se existir)",
      "  --auth-tiktok <path> Caminho do storageState do TikTok (default: auth/tiktok_state.json se existir)",
      "  --ig-url <url>    URL do perfil Instagram (override do --profile)",
      "  --x-url <url>     URL do perfil X (override do --profile)",
      "  --tiktok-url <url> URL do perfil TikTok (override do --profile)",
    ].join("\n") + "\n",
  );
}

function printOutputs(config: RunConfig): void {
  const outDir = resolve(config.outDir);
  const handle = config.outputHandle;
  const files: string[] = [];
  files.push(outputPath(outDir, "posts", "csv", handle));
  if (config.scrapeInstagram) {
    files.push(outputPath(outDir, "instagram_posts", "csv", handle));
    files.push(outputPostsPath(outDir, config.athleteName, handle, "csv"));
    files.push(outputPostsPath(outDir, config.athleteName, handle, "json"));
    files.push(outputPath(outDir, "instagram_profile", "csv", handle));
    files.push(outputPath(outDir, "instagram_profile", "json", handle));
    files.push(outputPath(outDir, "indicadores", "csv", handle));
    files.push(outputPath(outDir, "indicadores_bb_por_mes", "csv", handle));
    files.push(join(outDir, "indicadores.json"));
    files.push(join(outDir, "texto_relatorio.md"));
    files.push(join(outDir, "tabelas.md"));
  }
  if (config.scrapeX) {
    files.push(outputPath(outDir, "x_tweets", "csv", handle));
    files.push(outputPath(outDir, "x_profile", "csv", handle));
  }
  if (config.scrapeTikTok) {
    files.push(outputPath(outDir, "tiktok_videos", "csv", handle));
    files.push(outputPath(outDir, "tiktok_profile", "csv", handle));
  }
  files.push(
    outputPath(outDir, "summary", "csv", handle),
    outputPath(outDir, "top_hashtags_bb", "csv", handle),
    outputPath(outDir, "top_mentions_bb", "csv", handle),
    outputPath(outDir, "run", "csv", handle),
    outputPath(outDir, "run", "log", handle),
  );
  process.stdout.write("\nArquivos (esperados) em:\n");
  for (const file of files) process.stdout.write(`- ${file}\n`);
  if (config.debug && config.scrapeInstagram) process.stdout.write(`- ${outputPath(outDir, "ig_links", "csv", handle)}\n`);
  if (config.debug && config.scrapeTikTok) process.stdout.write(`- ${outputPath(outDir, "tiktok_links", "csv", handle)}\n`);
}

function verifyInstagramOutputs(config: RunConfig, logger: Logger): void {
  if (!config.scrapeInstagram) return;
  const outDir = resolve(config.outDir);
  const handle = config.outputHandle;
  const required = [
    outputPath(outDir, "instagram_posts", "csv", handle),
    outputPostsPath(outDir, config.athleteName, handle, "csv"),
    outputPath(outDir, "instagram_profile", "csv", handle),
  ];
  const missing = required.filter((path) => !existsSync(path));
  if (missing.length > 0) {
    logger.warn(`IG: arquivos esperados nao encontrados: ${missing.join("; ")}`);
  }
}

function emptyProfile(url: string, nowIso: string): ProfileSnapshot {
  return {
    url,
    fetched_at: nowIso,
    metaDescription: null,
    ogTitle: null,
    ogDescription: null,
    metrics: {
      followers: null,
      following: null,
      posts: null,
    },
  };
}

async function removeLegacyJsonOutputs(outDir: string): Promise<void> {
  const legacyFiles = [
    "instagram_profile.json",
    "x_profile.json",
    "tiktok_profile.json",
    "summary.json",
    "ig_links.json",
    "tiktok_links.json",
    "run.log",
  ];

  for (const file of legacyFiles) {
    await unlink(join(outDir, file)).catch(() => undefined);
  }
}

function emptyTikTokProfile(url: string, nowIso: string): TikTokProfileSnapshot {
  return {
    url,
    fetched_at: nowIso,
    username: null,
    display_name: null,
    bio: null,
    external_url: null,
    metaDescription: null,
    ogTitle: null,
    ogDescription: null,
    metrics: {
      followers: null,
      following: null,
      likes: null,
    },
  };
}

async function runIndicators(config: RunConfig, logger: Logger): Promise<void> {
  if (!config.scrapeInstagram) return;

  const pipelineRoot = resolvePipelineRoot();
  const outDir = resolve(config.outDir);
  const csvPath = outputPostsPath(outDir, config.athleteName, config.outputHandle, "csv");
  const outPath = outputPath(outDir, "indicadores", "csv", config.outputHandle);
  const scriptPath = resolve(pipelineRoot, "report", "append_indicator.py");

  if (!existsSync(scriptPath)) {
    logger.warn(`Indicadores: script nao encontrado: ${scriptPath}`);
    return;
  }
  if (!existsSync(csvPath)) {
    logger.warn(`Indicadores: CSV nao encontrado: ${csvPath}`);
    return;
  }

  const baseArgs = [scriptPath, "--csv", csvPath, "--out", outPath];
  if (config.outputHandle) baseArgs.push("--handle", config.outputHandle);

  const runners = [
    { cmd: "python", args: baseArgs },
    { cmd: "py", args: ["-3", ...baseArgs] },
  ];

  let lastError: unknown = null;
  for (const runner of runners) {
    try {
      const { stdout, stderr } = await execFileAsync(runner.cmd, runner.args, { windowsHide: true, encoding: "utf8" });
      const stdOut = String(stdout ?? "").replace(/\s+/g, " ").trim();
      const stdErr = String(stderr ?? "").replace(/\s+/g, " ").trim();
      if (stdOut) logger.info(`Indicadores: ${stdOut}`);
      if (stdErr) logger.warn(`Indicadores: ${stdErr}`);
      logger.info(`Indicadores: gerado ${outPath}`);
      return;
    } catch (error) {
      lastError = error;
      logger.warn(`Indicadores: falha com ${runner.cmd} (${String(error)})`);
    }
  }

  logger.warn(`Indicadores: falha ao executar append_indicator (${String(lastError)})`);
}

async function runDeterministicReport(config: RunConfig, logger: Logger): Promise<void> {
  if (!config.scrapeInstagram) return;

  const pipelineRoot = resolvePipelineRoot();
  const outDir = resolve(config.outDir);
  const csvPath = outputPostsPath(outDir, config.athleteName, config.outputHandle, "csv");
  const scriptPath = resolve(pipelineRoot, "generate_report.py");

  if (!existsSync(scriptPath)) {
    logger.warn(`Relatorio: script nao encontrado: ${scriptPath}`);
    return;
  }
  if (!existsSync(csvPath)) {
    logger.warn(`Relatorio: CSV nao encontrado: ${csvPath}`);
    return;
  }

  const baseArgs = [scriptPath, "--file", csvPath, "--user", config.outputHandle ?? "", "--out", outDir];
  const since = formatDateOnly(config.since);
  if (since) baseArgs.push("--since", since);

  const runners = [
    { cmd: "python", args: baseArgs },
    { cmd: "py", args: ["-3", ...baseArgs] },
  ];

  let lastError: unknown = null;
  for (const runner of runners) {
    try {
      const { stdout, stderr } = await execFileAsync(runner.cmd, runner.args, { windowsHide: true, encoding: "utf8" });
      const stdOut = String(stdout ?? "").replace(/\s+/g, " ").trim();
      const stdErr = String(stderr ?? "").replace(/\s+/g, " ").trim();
      if (stdOut) logger.info(`Relatorio: ${stdOut}`);
      if (stdErr) logger.warn(`Relatorio: ${stdErr}`);
      logger.info(`Relatorio: gerado ${join(outDir, "indicadores.json")}`);
      return;
    } catch (error) {
      lastError = error;
      logger.warn(`Relatorio: falha com ${runner.cmd} (${String(error)})`);
    }
  }

  logger.warn(`Relatorio: falha ao executar generate_report (${String(lastError)})`);
}

