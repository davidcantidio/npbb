import type { BrowserContext, Page } from "playwright";
import type { TikTokProfileSnapshot, TikTokVideo } from "../types";
import { Logger } from "../logger";
import { parseCompactNumber } from "../utils/numbers";
import { analyzeBancoDoBrasilMention, extractHashtags, extractMentions, normalizeText } from "../parse";
import { shuffleInPlace } from "../utils/random";
import { sleep, sleepBetween } from "../utils/sleep";
import { extractHandleFromProfileUrl } from "../utils/profile";

export interface TikTokScrapeOptions {
  profileUrl: string;
  max: number;
  since: Date | null;
  until: Date | null;
  logger: Logger;
  timeoutMs: number;
  debug: boolean;
  hasAuth: boolean;
}

export interface TikTokScrapeResult {
  profile: TikTokProfileSnapshot;
  videos: TikTokVideo[];
  debug: {
    links: string[];
  };
}

function isInDateRange(datetime: string | null, since: Date | null, until: Date | null): boolean {
  if (!since && !until) return true;
  if (!datetime) return false;
  const dt = new Date(datetime).getTime();
  if (!Number.isFinite(dt)) return false;
  if (since && dt < since.getTime()) return false;
  if (until && dt > until.getTime()) return false;
  return true;
}

export async function scrapeTikTok(context: BrowserContext, options: TikTokScrapeOptions): Promise<TikTokScrapeResult> {
  const page = await context.newPage();
  page.setDefaultTimeout(options.timeoutMs);
  page.setDefaultNavigationTimeout(options.timeoutMs);
  const targetHandle = extractHandleFromProfileUrl(options.profileUrl);
  const targetHandleLower = targetHandle ? targetHandle.toLowerCase() : null;

  try {
    options.logger.info(`TikTok: abrindo perfil ${options.profileUrl}`);
    await gotoWithRetries(page, options.profileUrl, options.timeoutMs, options.logger);
    await bestEffortDismissBanners(page);

    const finalUrl = page.url();
    const finalHandle = extractHandleFromProfileUrl(finalUrl);
    if (targetHandleLower && (!finalHandle || finalHandle.toLowerCase() !== targetHandleLower)) {
      options.logger.warn(
        `TikTok: pagina nao parece estar no perfil alvo (esperado @${targetHandleLower}, atual=${finalHandle ?? "desconhecido"}).`,
      );
    }

    const profile = await extractProfileSnapshot(page, finalUrl);
    if (targetHandleLower && profile.username && profile.username.toLowerCase() !== targetHandleLower) {
      options.logger.warn(
        `TikTok: username detectado (${profile.username}) nao bate com o handle esperado (@${targetHandleLower}).`,
      );
    }

    await page.waitForTimeout(1500);
    const videoUrls = await collectVideoUrls(page, options.max, options.logger, targetHandleLower);
    const shuffledVideoUrls = [...videoUrls];
    shuffleInPlace(shuffledVideoUrls);

    if (!options.hasAuth && videoUrls.length === 0) {
      options.logger.warn(
        "TikTok: sem sessão (storageState), a grade de vídeos pode não carregar; rode `npm run auth:tiktok` e tente novamente.",
      );
    }

    options.logger.info(`TikTok: encontrados ${videoUrls.length} links de vídeos (pré-filtro).`);

    const videos: TikTokVideo[] = [];
    const videoPage = await context.newPage();
    videoPage.setDefaultTimeout(options.timeoutMs);
    videoPage.setDefaultNavigationTimeout(options.timeoutMs);

    try {
      for (const url of shuffledVideoUrls) {
        if (videos.length >= options.max) break;
        const item = await safeScrapeVideo(videoPage, url, options.logger, options.timeoutMs);
        if (!item) continue;
        if (!isInDateRange(item.datetime, options.since, options.until)) continue;
        videos.push(item);
        await sleepBetween(700, 1900);
      }
    } finally {
      await videoPage.close();
    }

    options.logger.info(`TikTok: coletados ${videos.length} itens.`);
    return { profile, videos, debug: { links: videoUrls } };
  } finally {
    await page.close();
  }
}

async function extractProfileSnapshot(page: Page, url: string): Promise<TikTokProfileSnapshot> {
  const fetched_at = new Date().toISOString();

  const metaDescription = await getMetaContent(page, 'meta[name="description"]');
  const ogTitle = await getMetaContent(page, 'meta[property="og:title"]');
  const ogDescription = await getMetaContent(page, 'meta[property="og:description"]');

  const dom = await page.evaluate(() => {
    function text(sel: string): string | null {
      const el = document.querySelector(sel);
      const t = (el?.textContent ?? "").trim();
      return t ? t : null;
    }

    function href(sel: string): string | null {
      const el = document.querySelector(sel) as HTMLAnchorElement | null;
      return el?.href ?? null;
    }

    return {
      username: text('[data-e2e="user-title"]'),
      display_name: text('[data-e2e="user-subtitle"]'),
      bio: text('[data-e2e="user-bio"]'),
      external_url: href('[data-e2e="user-link"]') ?? text('[data-e2e="user-link"]'),
      following: text('[data-e2e="following-count"]'),
      followers: text('[data-e2e="followers-count"]'),
      likes: text('[data-e2e="likes-count"]'),
    };
  });

  return {
    url,
    fetched_at,
    username: dom.username,
    display_name: dom.display_name,
    bio: dom.bio,
    external_url: dom.external_url,
    metaDescription,
    ogTitle,
    ogDescription,
    metrics: {
      followers: parseCompactNumber(dom.followers ?? ""),
      following: parseCompactNumber(dom.following ?? ""),
      likes: parseCompactNumber(dom.likes ?? ""),
    },
  };
}

async function collectVideoUrls(
  page: Page,
  max: number,
  logger: Logger,
  targetHandleLower: string | null,
): Promise<string[]> {
  const urls = new Set<string>();
  const maxScrolls = Math.min(2000, Math.max(40, Math.ceil(max / 12) * 4));
  let stableRounds = 0;
  const selectors = [
    '[data-e2e="user-post-item"] a[href*="/video/"]',
    '[data-e2e="user-post-item-list"] a[href*="/video/"]',
    'a[href*="/video/"]',
  ];

  for (const selector of selectors) {
    const ok = await page.waitForSelector(selector, { timeout: 5_000 }).then(() => true).catch(() => false);
    if (ok) break;
  }

  for (let i = 0; i < maxScrolls && urls.size < max; i++) {
    let hrefs: string[] = [];
    for (const selector of selectors) {
      const found = await page
        .$$eval(selector, (anchors) => anchors.map((a) => (a as HTMLAnchorElement).href).filter(Boolean))
        .catch(() => [] as string[]);
      if (found.length) {
        hrefs = found;
        break;
      }
    }

    const before = urls.size;
    for (const href of hrefs) {
      const cleaned = stripQuery(href);
      if (!isTikTokVideoUrlForHandle(cleaned, targetHandleLower)) continue;
      urls.add(cleaned);
    }
    const after = urls.size;
    if (after === before) stableRounds += 1;
    else stableRounds = 0;

    if ((i + 1) % 5 === 0) logger.info(`TikTok: scroll ${i + 1}, urls=${urls.size}`);
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await sleep(900, 900);

    const stableLimit = urls.size === 0 ? 8 : 3;
    if (stableRounds >= stableLimit) break;
  }

  if (urls.size === 0) {
    const fallback = await extractVideoUrlsFromState(page, targetHandleLower);
    if (fallback.length) {
      for (const url of fallback) urls.add(url);
      logger.info(`TikTok: fallback via estado/HTML, urls=${urls.size}.`);
    }
  }

  return [...urls].slice(0, max);
}

async function safeScrapeVideo(page: Page, url: string, logger: Logger, timeoutMs: number): Promise<TikTokVideo | null> {
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      logger.info(`TikTok: coletando ${url} (tentativa ${attempt}/3)`);
      await gotoWithRetries(page, url, timeoutMs, logger);
      await bestEffortDismissBanners(page);

      await page.waitForTimeout(800);

      const ldJson = await extractLdJson(page);
      const ldVideo = findVideoObject(ldJson);

      const ogDescription = await getMetaContent(page, 'meta[property="og:description"]');
      const ogTitle = await getMetaContent(page, 'meta[property="og:title"]');
      const desc = await getMetaContent(page, 'meta[name="description"]');

      const dom = await page.evaluate(() => {
        function text(sel: string): string | null {
          const el = document.querySelector(sel);
          const t = (el?.textContent ?? "").trim();
          return t ? t : null;
        }

        return {
          caption:
            text('[data-e2e="browse-video-desc"]') ??
            text('[data-e2e="video-desc"]') ??
            text('[data-e2e="browse-video-caption"]') ??
            null,
          likes: text('[data-e2e="like-count"]'),
          comments: text('[data-e2e="comment-count"]'),
          shares: text('[data-e2e="share-count"]'),
          views: text('[data-e2e="play-count"]') ?? text('[data-e2e="view-count"]'),
        };
      });

      const captionRaw = dom.caption ?? ldVideo?.description ?? ogTitle ?? ogDescription ?? desc ?? "";
      const caption = normalizeText(captionRaw);

      const datetime = normalizeIsoDateTime(ldVideo?.uploadDate ?? null);

      const hashtags = extractHashtags(caption);
      const mentions = extractMentions(caption);
      const bbAnalysis = analyzeBancoDoBrasilMention(caption, { hashtags, mentions });

      return {
        video_url: url,
        datetime,
        caption,
        hashtags,
        mentions,
        is_bb_mention: bbAnalysis.is_bb_mention,
        bb_connection_type: bbAnalysis.connection_type,
        bb_markers_count: bbAnalysis.markers_count,
        likes: parseCompactNumber(dom.likes ?? ""),
        comments: parseCompactNumber(dom.comments ?? ""),
        shares: parseCompactNumber(dom.shares ?? ""),
        views: parseCompactNumber(dom.views ?? ""),
      };
    } catch (error) {
      logger.warn(`TikTok: falha ao coletar ${url}: ${String(error)}`);
      await sleep(600 * attempt, 1000);
    }
  }

  return null;
}

async function extractLdJson(page: Page): Promise<unknown[]> {
  const texts = await page
    .$$eval('script[type="application/ld+json"]', (els) => els.map((e) => e.textContent).filter(Boolean))
    .catch(() => [] as string[]);

  const parsed: unknown[] = [];
  for (const text of texts) {
    try {
      parsed.push(JSON.parse(text));
    } catch {
      // ignore
    }
  }
  return parsed;
}

type VideoObject = { description?: string; uploadDate?: string } | null;

function findVideoObject(items: unknown[]): VideoObject {
  for (const item of items) {
    const found = findVideoObjectInUnknown(item);
    if (found) return found;
  }
  return null;
}

function findVideoObjectInUnknown(value: unknown): VideoObject {
  if (!value) return null;

  if (Array.isArray(value)) {
    for (const v of value) {
      const found = findVideoObjectInUnknown(v);
      if (found) return found;
    }
    return null;
  }

  if (typeof value !== "object") return null;
  const obj = value as Record<string, unknown>;
  const type = String(obj["@type"] ?? "");
  if (type.toLowerCase() === "videoobject") {
    const description = typeof obj.description === "string" ? obj.description : undefined;
    const uploadDate = typeof obj.uploadDate === "string" ? obj.uploadDate : undefined;
    return { description, uploadDate };
  }

  const graph = obj["@graph"];
  if (graph) return findVideoObjectInUnknown(graph);

  return null;
}

function normalizeIsoDateTime(value: string | null): string | null {
  if (!value) return null;
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? null : d.toISOString();
}

async function getMetaContent(page: Page, selector: string): Promise<string | null> {
  return (await page.locator(selector).first().getAttribute("content").catch(() => null)) ?? null;
}

async function bestEffortDismissBanners(page: Page): Promise<void> {
  const candidates = [
    'button:has-text("Aceitar")',
    'button:has-text("Permitir")',
    'button:has-text("Accept")',
    'button:has-text("Allow")',
    'button:has-text("OK")',
    'button:has-text("Not now")',
    'button:has-text("Agora não")',
    'button[aria-label="Close"]',
    'button[aria-label="Fechar"]',
  ];

  for (const selector of candidates) {
    const button = page.locator(selector).first();
    if (await button.isVisible().catch(() => false)) {
      await button.click({ timeout: 2_000 }).catch(() => undefined);
    }
  }
}

function stripQuery(url: string): string {
  try {
    const u = new URL(url);
    u.search = "";
    u.hash = "";
    return u.toString();
  } catch {
    return url;
  }
}

function isTikTokVideoUrl(url: string): boolean {
  try {
    const u = new URL(url);
    if (!/tiktok\.com$/i.test(u.hostname)) return false;
    return /\/video\/\d+/.test(u.pathname);
  } catch {
    return false;
  }
}

function isTikTokVideoUrlForHandle(url: string, handleLower: string | null): boolean {
  if (!isTikTokVideoUrl(url)) return false;
  if (!handleLower) return true;
  try {
    const u = new URL(url);
    const parts = u.pathname.split("/").filter(Boolean);
    if (parts.length < 3) return false;
    const handle = parts[0].replace(/^@/, "").toLowerCase();
    return handle === handleLower;
  } catch {
    return false;
  }
}

async function extractVideoUrlsFromState(page: Page, handleLower: string | null): Promise<string[]> {
  const urls = new Set<string>();
  const scripts = await page
    .evaluate(() => {
      const sigi = document.querySelector('script#SIGI_STATE')?.textContent ?? null;
      const universal = document.querySelector('script#__UNIVERSAL_DATA_FOR_REHYDRATION__')?.textContent ?? null;
      const win = window as unknown as Record<string, unknown>;
      return {
        sigi,
        universal,
        sigiGlobal: win.SIGI_STATE ?? null,
        universalGlobal: win.__UNIVERSAL_DATA_FOR_REHYDRATION__ ?? null,
      };
    })
    .catch(
      () =>
        ({
          sigi: null,
          universal: null,
          sigiGlobal: null,
          universalGlobal: null,
        }) as {
          sigi: string | null;
          universal: string | null;
          sigiGlobal: unknown | null;
          universalGlobal: unknown | null;
        },
    );

  if (scripts.sigi) {
    extractVideoUrlsFromText(scripts.sigi, handleLower, urls);
    const parsed = safeParseJson(scripts.sigi);
    const itemModule = findItemModule(parsed, 0);
    if (itemModule) addUrlsFromItemModule(itemModule, handleLower, urls);
    if (parsed) collectVideoItems(parsed, handleLower, urls, 0);
  }

  if (scripts.universal) {
    extractVideoUrlsFromText(scripts.universal, handleLower, urls);
    const parsed = safeParseJson(scripts.universal);
    const itemModule = findItemModule(parsed, 0);
    if (itemModule) addUrlsFromItemModule(itemModule, handleLower, urls);
    if (parsed) collectVideoItems(parsed, handleLower, urls, 0);
  }

  if (scripts.sigiGlobal) {
    const sigiText = typeof scripts.sigiGlobal === "string" ? scripts.sigiGlobal : JSON.stringify(scripts.sigiGlobal);
    extractVideoUrlsFromText(sigiText, handleLower, urls);
    const itemModule = findItemModule(scripts.sigiGlobal, 0);
    if (itemModule) addUrlsFromItemModule(itemModule, handleLower, urls);
    collectVideoItems(scripts.sigiGlobal, handleLower, urls, 0);
  }

  if (scripts.universalGlobal) {
    const universalText =
      typeof scripts.universalGlobal === "string" ? scripts.universalGlobal : JSON.stringify(scripts.universalGlobal);
    extractVideoUrlsFromText(universalText, handleLower, urls);
    const itemModule = findItemModule(scripts.universalGlobal, 0);
    if (itemModule) addUrlsFromItemModule(itemModule, handleLower, urls);
    collectVideoItems(scripts.universalGlobal, handleLower, urls, 0);
  }

  if (urls.size === 0) {
    const html = await page.content().catch(() => "");
    if (html) extractVideoUrlsFromText(html, handleLower, urls);
  }

  return [...urls];
}

function extractVideoUrlsFromText(text: string, handleLower: string | null, urls: Set<string>): void {
  if (!text) return;
  const normalized = normalizeStateText(text);
  const absRe = /https?:\/\/(?:www\.)?tiktok\.com\/@([a-z0-9._-]+)\/video\/(\d+)/gi;
  const relRe = /\/@([a-z0-9._-]+)\/video\/(\d+)/gi;

  let match: RegExpExecArray | null;
  while ((match = absRe.exec(normalized))) {
    addVideoUrl(match[1], match[2], handleLower, urls);
  }
  while ((match = relRe.exec(normalized))) {
    addVideoUrl(match[1], match[2], handleLower, urls);
  }
}

function addVideoUrl(handle: string, id: string, handleLower: string | null, urls: Set<string>): void {
  const safeHandle = String(handle ?? "").replace(/^@+/, "").trim();
  const safeId = String(id ?? "").trim();
  if (!safeHandle || !safeId) return;
  if (handleLower && safeHandle.toLowerCase() !== handleLower) return;
  urls.add(buildTikTokVideoUrl(safeHandle, safeId));
}

function buildTikTokVideoUrl(handle: string, id: string): string {
  return `https://www.tiktok.com/@${handle}/video/${id}`;
}

function normalizeStateText(text: string): string {
  return text
    .replace(/\\\\u002f/gi, "/")
    .replace(/\\\\u0040/gi, "@")
    .replace(/\\u002f/gi, "/")
    .replace(/\\u0040/gi, "@")
    .replace(/\\\//g, "/");
}

function safeParseJson(text: string): unknown | null {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

function findItemModule(value: unknown, depth: number): Record<string, unknown> | null {
  if (!value || typeof value !== "object") return null;
  if (depth > 4) return null;

  const obj = value as Record<string, unknown>;
  const direct = obj.ItemModule;
  if (direct && typeof direct === "object") return direct as Record<string, unknown>;

  for (const child of Object.values(obj)) {
    const found = findItemModule(child, depth + 1);
    if (found) return found;
  }

  return null;
}

function addUrlsFromItemModule(module: Record<string, unknown>, handleLower: string | null, urls: Set<string>): void {
  for (const [key, raw] of Object.entries(module)) {
    if (!raw || typeof raw !== "object") continue;
    const item = raw as Record<string, unknown>;
    const id = String(item.id ?? key ?? "").trim();
    const author = String(item.author ?? item.authorName ?? item.authorUniqueId ?? "").trim();
    addVideoUrl(author, id, handleLower, urls);
  }
}

function collectVideoItems(value: unknown, handleLower: string | null, urls: Set<string>, depth: number): void {
  if (!value || depth > 5) return;

  if (Array.isArray(value)) {
    for (const item of value) collectVideoItems(item, handleLower, urls, depth + 1);
    return;
  }

  if (typeof value !== "object") return;
  const obj = value as Record<string, unknown>;

  const idRaw = String(obj.id ?? "").trim();
  const id = /^\d+$/.test(idRaw) ? idRaw : null;
  const authorFromObj = resolveAuthorFromItem(obj);
  if (id && authorFromObj) addVideoUrl(authorFromObj, id, handleLower, urls);

  for (const child of Object.values(obj)) {
    collectVideoItems(child, handleLower, urls, depth + 1);
  }
}

function resolveAuthorFromItem(item: Record<string, unknown>): string | null {
  const direct = String(item.author ?? item.authorName ?? item.authorUniqueId ?? "").trim();
  if (direct) return direct;

  const author = item.author;
  if (author && typeof author === "object") {
    const obj = author as Record<string, unknown>;
    const nested = String(obj.uniqueId ?? obj.id ?? obj.name ?? "").trim();
    return nested || null;
  }

  return null;
}

async function gotoWithRetries(page: Page, url: string, timeoutMs: number, logger: Logger): Promise<void> {
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      await page.goto(url, { waitUntil: "domcontentloaded", timeout: timeoutMs });
      return;
    } catch (error) {
      logger.warn(`TikTok: falha ao abrir ${url} (tentativa ${attempt}/3): ${String(error)}`);
      await sleep(500 * attempt, 800);
    }
  }
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: timeoutMs });
}
