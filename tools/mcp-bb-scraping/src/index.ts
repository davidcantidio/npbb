import { existsSync } from "node:fs";
import { resolve, basename, join } from "node:path";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { chromium, type BrowserContext } from "playwright";
import { launchBrowser, newContext } from "./browser";
import type { Logger as ScraperLogger } from "./logger";
import { scrapeInstagram } from "./scrapers/instagram";
import { scrapeTikTok } from "./scrapers/tiktok";
import { scrapeX } from "./scrapers/x";
import { buildSummary, filterByReportPeriod } from "./summary";
import type { InstagramPost, InstagramPostEnriched, ProfileSnapshot, RunConfig, Summary, TikTokProfileSnapshot, TikTokVideo, XTweet } from "./types";
import { parseArgs, parseIntArg, stringArg, dateArg } from "./utils/args";
import { sanitizeHandle, sanitizeLabel, outputPostsPath } from "./utils/output";
import { listAthleteHandles, lookupAthleteName } from "./utils/athletes";
import { resolvePipelineRoot } from "./utils/root";
import {
  buildInstagramProfileUrl,
  buildTikTokProfileUrl,
  buildXProfileUrl,
  normalizeProfileHandle,
} from "./utils/profile";
import { writeInstagramPostsEnrichedCsv } from "./writers";

const execFileAsync = promisify(execFile);

const DEFAULT_NPBB_ENDPOINT = "/internal/scraping/ingestions";

type LogLevel = "INFO" | "WARN" | "ERROR";

interface OperationalLogLine {
  timestamp: string;
  level: LogLevel;
  message: string;
}

interface NpbbIngestionPayload {
  execution: {
    handle: string | null;
    athleteName: string | null;
    since: string | null;
    until: string | null;
    max: number;
    started_at: string;
    finished_at: string;
  };
  platforms: {
    instagram: {
      posts: InstagramPost[];
      profile: ProfileSnapshot | null;
    };
    x: {
      posts: XTweet[];
      profile: ProfileSnapshot | null;
    };
    tiktok: {
      posts: TikTokVideo[];
      profile: TikTokProfileSnapshot | null;
    };
  };
  summary: Summary;
  logs: OperationalLogLine[];
}

class OperationalLogger {
  private readonly logs: OperationalLogLine[] = [];

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
    // Logger em memoria; nada para fechar.
  }

  asScraperLogger(): ScraperLogger {
    return this as unknown as ScraperLogger;
  }

  snapshot(limit = 120): OperationalLogLine[] {
    return this.logs.slice(-limit);
  }

  private write(level: LogLevel, message: string): void {
    const timestamp = new Date().toISOString();
    const line = `${timestamp} [${level}] ${normalizeLogMessage(message)}`;
    process.stdout.write(`${line}\n`);
    this.logs.push({ timestamp, level, message: normalizeLogMessage(message) });
    if (this.logs.length > 500) this.logs.shift();
  }
}

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
  const logger = new OperationalLogger();
  for (const warning of config.authWarnings) {
    logger.warn(warning);
  }
  const startedAt = new Date().toISOString();
  logger.info(
    `Iniciando scraping: max=${config.max}, since=${config.since ? config.since.toISOString() : "null"}, until=${config.until ? config.until.toISOString() : "null"}`,
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
  const scrapeLogger = logger.asScraperLogger();

  try {
    let instagramPosts: InstagramPost[] = [];
    let instagramProfile: ProfileSnapshot | null = null;
    let xTweets: XTweet[] = [];
    let xProfile: ProfileSnapshot | null = null;
    let tiktokVideos: TikTokVideo[] = [];
    let tiktokProfile: TikTokProfileSnapshot | null = null;
    const nowIso = new Date().toISOString();

    let enrichedInstagramPosts: InstagramPostEnriched[] = [];

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
          logger: scrapeLogger,
          timeoutMs: config.timeoutMs,
          debug: config.debug,
          hasAuth: sharedContext != null || config.instagramStorageStatePath != null,
          bbAliases: config.bbAliases,
        });
        if (!sharedContext) await context.close();

        instagramPosts = posts;
        enrichedInstagramPosts = enrichedPosts;
        instagramProfile = profile;
        if (config.debug) logger.info(`Instagram: debug links coletados=${debug.links.length}`);
        logger.info(`Instagram: posts coletados=${posts.length}, enriquecidos=${enrichedPosts.length}`);

        try {
          await writeInstagramPostsEnrichedCsv(config.outDir, enrichedPosts, config.outputHandle, config.athleteName);
          logger.info(`Instagram: CSV enriquecido salvo em ${config.outDir}`);
        } catch (writeError) {
          logger.warn(`Instagram: falha ao salvar CSV enriquecido: ${String(writeError)}`);
        }

        didAny = true;
      } catch (error) {
        logger.error(`Instagram: erro geral: ${String(error)}`);
        instagramPosts = [];
        enrichedInstagramPosts = [];
        instagramProfile = emptyProfile(config.instagramProfileUrl, nowIso);
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
          logger: scrapeLogger,
          timeoutMs: config.timeoutMs,
        });
        if (!sharedContext) await context.close();

        xTweets = tweets;
        xProfile = profile;
        logger.info(`X: tweets coletados=${tweets.length}`);
        didAny = true;
      } catch (error) {
        logger.error(`X: erro geral: ${String(error)}`);
        xTweets = [];
        xProfile = emptyProfile(config.xProfileUrl, nowIso);
      }
    }

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
          logger: scrapeLogger,
          timeoutMs: config.timeoutMs,
          debug: config.debug,
          hasAuth: sharedContext != null || config.tiktokStorageStatePath != null,
        });
        if (!sharedContext) await context.close();

        tiktokVideos = videos;
        tiktokProfile = profile;
        if (config.debug) logger.info(`TikTok: debug links coletados=${debug.links.length}`);
        logger.info(`TikTok: videos coletados=${videos.length}`);
        didAny = true;
      } catch (error) {
        logger.error(`TikTok: erro geral: ${String(error)}`);
        tiktokVideos = [];
        tiktokProfile = emptyTikTokProfile(config.tiktokProfileUrl, nowIso);
      }
    }

    const summary = buildSummary(
      filterByReportPeriod(instagramPosts, config.since, config.until),
      filterByReportPeriod(xTweets, config.since, config.until),
      filterByReportPeriod(tiktokVideos, config.since, config.until),
    );

    const finishedAt = new Date().toISOString();
    const payload = buildNpbbPayload(
      config,
      {
        instagramPosts,
        instagramProfile,
        xTweets,
        xProfile,
        tiktokVideos,
        tiktokProfile,
      },
      summary,
      startedAt,
      finishedAt,
      logger.snapshot(),
    );

    if (!config.publishEnabled) {
      logger.info(`Publicacao NPBB desativada por --no-publish. Endpoint alvo: ${config.npbbApiEndpoint}`);
    } else {
      if (!config.npbbApiBaseUrl || !config.npbbApiToken) {
        logger.warn("Publicacao NPBB: --npbb-url ou --npbb-token ausentes. Pulando publicacao.");
      } else {
        await publishToNpbb(config, payload, logger);
      }
    }

    await runDeterministicReport(config, enrichedInstagramPosts, logger);
  } finally {
    await browser.close();
    logger.close();
  }

  if (!didAny) process.exitCode = 1;
}

async function runDeterministicReport(
  config: RunConfig,
  enrichedPosts: InstagramPostEnriched[],
  logger: OperationalLogger,
): Promise<void> {
  if (!config.scrapeInstagram) return;
  if (enrichedPosts.length === 0) {
    logger.warn("Relatorio: nenhum post enriquecido disponivel; pulando geracao.");
    return;
  }

  const pipelineRoot = resolvePipelineRoot();
  const outDir = resolve(config.outDir);
  const scriptPath = resolve(pipelineRoot, "generate_report.py");

  if (!existsSync(scriptPath)) {
    logger.warn(`Relatorio: script nao encontrado: ${scriptPath}`);
    return;
  }

  const csvPath = outputPostsPath(outDir, config.athleteName, config.outputHandle, "csv");
  if (!existsSync(csvPath)) {
    logger.warn(`Relatorio: CSV enriquecido nao encontrado: ${csvPath}`);
    return;
  }

  const baseArgs = [scriptPath, "--file", csvPath, "--user", config.outputHandle ?? "", "--out", outDir];
  const since = formatDateOnly(config.since);
  if (since) baseArgs.push("--since", since);
  const until = formatDateOnly(config.until);
  if (until) baseArgs.push("--until", until);

  // Snapshot agregado por data em out/relatorios/YYYY-MM-DD
  const athleteDirName = sanitizeLabel(config.athleteName) ?? sanitizeHandle(config.outputHandle) ?? "perfil";
  const todayLocal = new Date().toLocaleDateString("sv-SE"); // YYYY-MM-DD no fuso local
  const snapshotDir = resolve(pipelineRoot, "out", "relatorios", todayLocal);
  baseArgs.push("--report-snapshot-dir", snapshotDir, "--report-file-prefix", athleteDirName);

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
      logger.info(`Relatorio: gerado em ${outDir} e snapshot em ${snapshotDir}`);
      return;
    } catch (error) {
      lastError = error;
      logger.warn(`Relatorio: falha com ${runner.cmd} (${String(error)})`);
    }
  }

  logger.warn(`Relatorio: falha ao executar generate_report.py (${String(lastError)})`);
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

  const publishEnabled = !args.has("no-publish");
  const npbbUrlArg = args.get("npbb-url");
  const npbbTokenArg = args.get("npbb-token");
  const npbbEndpointArg = args.get("npbb-endpoint");

  if (args.has("npbb-url") && !(npbbUrlArg ?? "").trim()) {
    throw new Error("Valor invalido em --npbb-url: vazio. Informe a URL base do backend NPBB.");
  }
  if (args.has("npbb-token") && !(npbbTokenArg ?? "").trim()) {
    throw new Error("Valor invalido em --npbb-token: vazio. Informe o token Bearer.");
  }
  if (args.has("npbb-endpoint") && !(npbbEndpointArg ?? "").trim()) {
    throw new Error("Valor invalido em --npbb-endpoint: vazio. Informe o path de ingestao.");
  }

  const npbbApiBaseUrl = stringArg(npbbUrlArg, "").trim() || null;
  const npbbApiToken = stringArg(npbbTokenArg, "").trim() || null;
  const npbbApiEndpoint = normalizeEndpoint(stringArg(npbbEndpointArg, DEFAULT_NPBB_ENDPOINT));

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
    npbbApiBaseUrl,
    npbbApiToken,
    npbbApiEndpoint,
    publishEnabled,
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
      "  --max <n>         Maximo de itens coletados por plataforma (default: 150); nao depende do periodo",
      "  --out <dir>       Diretorio legado de saida (default: out, nao obrigatorio para publicacao NPBB)",
      "  --since <date>    Data minima (YYYY-MM-DD) para resumo, indicadores e relatorio (opcional)",
      "  --until <date>    Data maxima (YYYY-MM-DD, inclusiva, fim do dia UTC) para resumo/indicadores/relatorio (opcional)",
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
      "  --npbb-url <url>  URL base do backend NPBB para publicacao HTTP",
      "  --npbb-token <t>  Token Bearer para autenticacao no NPBB",
      `  --npbb-endpoint <p> Path de ingestao NPBB (default: ${DEFAULT_NPBB_ENDPOINT})`,
      "  --no-publish      Nao envia para NPBB (modo debug da coleta/payload)",
    ].join("\n") + "\n",
  );
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

function buildNpbbPayload(
  config: RunConfig,
  data: {
    instagramPosts: InstagramPost[];
    instagramProfile: ProfileSnapshot | null;
    xTweets: XTweet[];
    xProfile: ProfileSnapshot | null;
    tiktokVideos: TikTokVideo[];
    tiktokProfile: TikTokProfileSnapshot | null;
  },
  summary: Summary,
  startedAt: string,
  finishedAt: string,
  logs: OperationalLogLine[],
): NpbbIngestionPayload {
  return {
    execution: {
      handle: config.outputHandle,
      athleteName: config.athleteName,
      since: formatDateOnly(config.since),
      until: formatDateOnly(config.until),
      max: config.max,
      started_at: startedAt,
      finished_at: finishedAt,
    },
    platforms: {
      instagram: {
        posts: data.instagramPosts,
        profile: data.instagramProfile,
      },
      x: {
        posts: data.xTweets,
        profile: data.xProfile,
      },
      tiktok: {
        posts: data.tiktokVideos,
        profile: data.tiktokProfile,
      },
    },
    summary,
    logs,
  };
}

async function publishToNpbb(config: RunConfig, payload: NpbbIngestionPayload, logger: OperationalLogger): Promise<void> {
  if (!config.npbbApiBaseUrl || !config.npbbApiToken) {
    throw new Error("Configuracao invalida: informe --npbb-url e --npbb-token (ou use --no-publish).");
  }

  const targetUrl = buildNpbbIngestionUrl(config.npbbApiBaseUrl, config.npbbApiEndpoint);
  logger.info(`Iniciando publicacao NPBB: ${targetUrl}`);

  let response: Response;
  try {
    response = await fetch(targetUrl, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${config.npbbApiToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  } catch (error) {
    logger.error(`Falha de rede na publicacao NPBB: ${String(error)}`);
    throw new Error(`Publicacao NPBB falhou por erro de rede: ${String(error)}`);
  }

  const responseBody = truncateText(await safeResponseText(response), 600);
  if (!response.ok) {
    logger.error(`Falha publicacao NPBB: status=${response.status}, resposta=${responseBody || "<vazia>"}`);
    throw new Error(`Publicacao NPBB retornou status ${response.status}.`);
  }

  logger.info(`Publicacao NPBB concluida com sucesso: status=${response.status}`);
}

async function safeResponseText(response: Response): Promise<string> {
  try {
    return normalizeLogMessage(await response.text());
  } catch {
    return "";
  }
}

function normalizeEndpoint(rawEndpoint: string): string {
  const trimmed = rawEndpoint.trim();
  if (!trimmed) return DEFAULT_NPBB_ENDPOINT;
  return trimmed.startsWith("/") ? trimmed : `/${trimmed}`;
}

function buildNpbbIngestionUrl(baseUrl: string, endpoint: string): string {
  try {
    const normalizedBase = baseUrl.endsWith("/") ? baseUrl : `${baseUrl}/`;
    return new URL(endpoint, normalizedBase).toString();
  } catch {
    throw new Error(`Valor invalido em --npbb-url: ${baseUrl}`);
  }
}

function truncateText(value: string, maxLen: number): string {
  if (value.length <= maxLen) return value;
  return `${value.slice(0, maxLen)}...`;
}

function normalizeLogMessage(message: string): string {
  return String(message ?? "").replace(/\s+/g, " ").trim();
}

