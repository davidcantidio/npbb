import type { BrowserContext, Page } from "playwright";
import type { InstagramMediaType, InstagramPost, InstagramPostEnriched, ProfileSnapshot } from "../types";
import { Logger } from "../logger";
import { parseCompactNumber } from "../utils/numbers";
import { analyzeBancoDoBrasilMention, extractHashtags, extractMentions, isBancoDoBrasilMentionLegacy, normalizeText } from "../parse";
import { shuffleInPlace } from "../utils/random";
import { sleep, sleepBetween } from "../utils/sleep";
import { extractInstagramProfileHandle } from "../utils/profile";

export interface InstagramScrapeOptions {
  profileUrl: string;
  max: number;
  logger: Logger;
  timeoutMs: number;
  debug: boolean;
  hasAuth: boolean;
  bbAliases?: string[];
}

export interface InstagramScrapeResult {
  profile: ProfileSnapshot;
  posts: InstagramPost[];
  enrichedPosts: InstagramPostEnriched[];
  stats: {
    total: number;
    owner_profile: number;
    with_plays: number;
    bb_mentions: number;
    bb_mentions_legacy: number;
  };
  debug: {
    links: string[];
  };
}

export async function scrapeInstagram(context: BrowserContext, options: InstagramScrapeOptions): Promise<InstagramScrapeResult> {
  const page = await context.newPage();
  page.setDefaultTimeout(options.timeoutMs);
  page.setDefaultNavigationTimeout(options.timeoutMs);
  const targetHandle = extractInstagramProfileHandle(options.profileUrl);
  const targetHandleLower = targetHandle ? targetHandle.toLowerCase() : null;

  try {
    options.logger.info(`Instagram: abrindo perfil ${options.profileUrl}`);
    await page.goto(options.profileUrl, { waitUntil: "domcontentloaded" });
    await bestEffortDismissBanners(page);

    if (page.url().includes("/accounts/login")) {
      options.logger.warn("Instagram: página redirecionou para login; gere uma sessão com `npm run auth:ig` (salva em auth/ig_state.json).");
    }

    if (page.url().includes("/accounts/login")) {
      const msg =
        "Instagram: pagina redirecionou para login. Gere uma sessao com `npm run auth:ig` (salva em auth/ig_state.json) e rode novamente.";
      if (!options.hasAuth) throw new Error(msg);
      throw new Error(`${msg} (storageState atual parece invalido)`);
    }

    const profile = await extractProfileSnapshot(page, options.profileUrl);

    await page
      .waitForSelector('a[href*="/p/"], a[href*="/reel/"]', { timeout: 10_000 })
      .catch(() => undefined);

    const postUrls = await collectPostUrls(page, options.max, options.logger);
    const shuffledPostUrls = [...postUrls];
    shuffleInPlace(shuffledPostUrls);
    if (!options.hasAuth && (profile.metrics.posts == null || profile.metrics.posts > 12) && postUrls.length <= 12) {
      options.logger.warn(
        "Instagram: sem sessão (storageState), o site costuma limitar a apenas ~12 itens; rode `npm run auth:ig` e tente novamente.",
      );
    }
    options.logger.info(`Instagram: encontrados ${postUrls.length} links de posts/reels (pré-filtro).`);

    const bbAliases = options.bbAliases ?? [];

    const posts: InstagramPost[] = [];
    const enrichedPosts: InstagramPostEnriched[] = [];
    let bbLegacyCount = 0;
    let bbNewCount = 0;
    let ownerProfileCount = 0;
    let withPlaysCount = 0;
    const postPage = await context.newPage();
    postPage.setDefaultTimeout(options.timeoutMs);
    postPage.setDefaultNavigationTimeout(options.timeoutMs);

    try {
      for (const url of shuffledPostUrls) {
        if (posts.length >= options.max) break;
        const result = await safeScrapePostEnriched(
          postPage,
          url,
          options.logger,
          options.timeoutMs,
          bbAliases,
          options.hasAuth,
          targetHandleLower,
        );
        if (!result) continue;
        const { post: enriched, isBbLegacy } = result;

        enrichedPosts.push(enriched);
        posts.push({
          post_url: enriched.post_url,
          datetime: enriched.datetime,
          caption: enriched.caption,
          hashtags: enriched.hashtags,
          mentions: enriched.mentions,
          is_bb_mention: enriched.is_bb_mention,
          bb_connection_type: enriched.bb_connection_type,
          bb_markers_count: enriched.bb_markers_count,
          likes: enriched.likes,
          comments: enriched.comments,
          views: enriched.views,
        });

        if (isBbLegacy) bbLegacyCount += 1;
        if (enriched.is_bb_mention) bbNewCount += 1;
        if (enriched.is_owner_profile) ownerProfileCount += 1;
        if (enriched.plays_or_views != null) withPlaysCount += 1;

        await sleepBetween(800, 2200);
      }
    } finally {
      await postPage.close();
    }

    options.logger.info(`Instagram: coletados ${posts.length} itens.`);
    options.logger.info(
      `Instagram: stats total=${posts.length}, owner_profile=${ownerProfileCount}, with_plays=${withPlaysCount}, bb_new=${bbNewCount}, bb_legacy=${bbLegacyCount}`,
    );

    return {
      profile,
      posts,
      enrichedPosts,
      stats: {
        total: posts.length,
        owner_profile: ownerProfileCount,
        with_plays: withPlaysCount,
        bb_mentions: bbNewCount,
        bb_mentions_legacy: bbLegacyCount,
      },
      debug: { links: postUrls },
    };
  } finally {
    await page.close();
  }
}

async function safeScrapePostEnriched(
  page: Page,
  url: string,
  logger: Logger,
  timeoutMs: number,
  bbAliases: string[],
  hasAuth: boolean,
  targetHandleLower: string | null,
): Promise<{ post: InstagramPostEnriched; isBbLegacy: boolean } | null> {
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      logger.info(`Instagram: coletando ${url} (tentativa ${attempt}/3)`);
      await page.goto(url, { waitUntil: "domcontentloaded", timeout: timeoutMs });
      await bestEffortDismissBanners(page);

      if (page.url().includes("/accounts/login")) {
        const msg =
          "Instagram: pagina de post redirecionou para login. Gere uma sessao com `npm run auth:ig` (salva em auth/ig_state.json) e rode novamente.";
        if (!hasAuth) throw new Error(msg);
        throw new Error(`${msg} (storageState atual parece invalido)`);
      }

      const scraped_at = new Date().toISOString();
      const ogDescription = await getMetaContent(page, 'meta[property="og:description"]');
      const ogTitle = await getMetaContent(page, 'meta[property="og:title"]');
      const ldJsonItems = await extractLdJson(page);

      const captionRaw =
        extractCaptionFromLdJson(ldJsonItems) ??
        extractCaptionFromMetaText(ogDescription) ??
        extractCaptionFromMetaText(ogTitle) ??
        (await extractCaptionFromArticle(page)) ??
        "";
      const caption = normalizeText(captionRaw);

      const datetime =
        (await page.locator("time[datetime]").first().getAttribute("datetime").catch(() => null)) ??
        (await getMetaContent(page, 'meta[property="og:updated_time"]'));

      const hashtags = extractHashtags(caption);
      const mentions = extractMentions(caption);
      const bbAnalysis = analyzeBancoDoBrasilMention(caption, { aliases: bbAliases, hashtags, mentions });
      const is_bb_mention = bbAnalysis.is_bb_mention;
      const bb_connection_type = bbAnalysis.connection_type;
      const bb_markers_count = bbAnalysis.markers_count;
      const isBbLegacy = isBancoDoBrasilMentionLegacy(caption);

      const { likes, comments, views: viewsFromOg } = extractMetricsFromOgDescription(ogDescription);
      const viewsFromLd = extractViewsFromLdJson(ldJsonItems);

      let htmlForFallback: string | null = null;
      let viewsFromHtml: number | null = null;
      if (viewsFromLd == null) {
        htmlForFallback = await page.content().catch(() => null);
        viewsFromHtml = extractViewsFromHtml(htmlForFallback);
      }

      const viewsFromDom = viewsFromLd == null && viewsFromHtml == null ? await extractViewsFromDom(page) : null;
      const plays_or_views = viewsFromLd ?? viewsFromHtml ?? viewsFromDom;
      const views = plays_or_views ?? viewsFromOg;

      const ownerInfo = await extractOwnerInfo(page, url);
      const owner_username = ownerInfo.owner_username;
      const ownerLower = owner_username ? owner_username.toLowerCase() : null;
      const is_owner_profile = targetHandleLower ? ownerLower === targetHandleLower : false;
      const is_collab = ownerInfo.coauthors.length > 1;

      const media_type = guessMediaType(url, ldJsonItems, htmlForFallback);
      const shortcode = extractShortcode(url);

      const enriched: InstagramPostEnriched = {
        post_url: url,
        datetime: datetime ?? null,
        caption,
        hashtags,
        mentions,
        is_bb_mention,
        bb_connection_type,
        bb_markers_count,
        likes,
        comments,
        views,
        owner_username,
        is_owner_profile,
        media_type,
        shortcode,
        is_collab,
        coauthors: ownerInfo.coauthors,
        paid_partnership: ownerInfo.paid_partnership,
        paid_partner: ownerInfo.paid_partner,
        location: ownerInfo.location,
        plays_or_views,
        scraped_at,
      };

      return { post: enriched, isBbLegacy };
    } catch (error) {
      logger.warn(`Instagram: falha ao coletar ${url}: ${String(error)}`);
      await sleep(500 * attempt, 1200 * attempt);
    }
  }

  return null;
}

type OwnerInfo = {
  owner_username: string | null;
  coauthors: string[];
  paid_partnership: boolean;
  paid_partner: string | null;
  location: string | null;
};

async function extractOwnerInfo(page: Page, url: string): Promise<OwnerInfo> {
  const fromUrl = extractOwnerFromUrl(url);

  const dom = await page
    .evaluate(() => {
      function uniqLower(items: string[]): string[] {
        const out: string[] = [];
        const seen = new Set<string>();
        for (const raw of items) {
          const v = String(raw ?? "").trim();
          if (!v) continue;
          const key = v.toLowerCase();
          if (seen.has(key)) continue;
          seen.add(key);
          out.push(v);
        }
        return out;
      }

      function usernameFromHref(href: string | null): string | null {
        const raw = String(href ?? "");
        const m = raw.match(/^\/([A-Za-z0-9._]+)\/$/);
        if (!m) return null;
        const u = m[1];
        const blocked = new Set(["p", "reel", "explore", "accounts", "stories", "about", "legal", "tv"]);
        if (blocked.has(u.toLowerCase())) return null;
        return u;
      }

      const article = document.querySelector("article");
      const header = article?.querySelector("header") ?? document.querySelector("header");

      const authorAnchors = header ? Array.from(header.querySelectorAll("a")) : [];
      const authors = uniqLower(
        authorAnchors
          .map((a) => usernameFromHref((a as HTMLAnchorElement).getAttribute("href")))
          .filter(Boolean) as string[],
      );

      const locationAnchor = (header?.querySelector('a[href*="/explore/locations/"]') as HTMLAnchorElement | null) ?? null;
      const location = (locationAnchor?.textContent ?? "").trim() || null;

      const headerText = (header?.innerText ?? "").trim();
      const paidPartnership = /parceria paga|paid partnership/i.test(headerText);

      let paidPartner: string | null = null;
      if (paidPartnership) {
        const m =
          headerText.match(/parceria paga(?:\\s+com)?\\s+([^\\n]+)/i) ?? headerText.match(/paid partnership(?:\\s+with)?\\s+([^\\n]+)/i);
        const tail = (m?.[1] ?? "").trim();
        if (tail) paidPartner = tail;
        const h = tail.match(/@([A-Za-z0-9._]+)/);
        if (h) paidPartner = h[1];
      }

      return { authors, location, paidPartnership, paidPartner };
    })
    .catch(() => ({ authors: [] as string[], location: null as string | null, paidPartnership: false, paidPartner: null as string | null }));

  const coauthors = dom.authors.length ? dom.authors : fromUrl ? [fromUrl] : [];
  const owner_username = dom.authors[0] ?? fromUrl ?? null;

  return {
    owner_username,
    coauthors,
    paid_partnership: Boolean(dom.paidPartnership),
    paid_partner: dom.paidPartner,
    location: dom.location,
  };
}

function extractOwnerFromUrl(url: string): string | null {
  try {
    const u = new URL(url);
    const parts = u.pathname.split("/").filter(Boolean);
    const idx = parts.findIndex((p) => p === "p" || p === "reel");
    if (idx <= 0) return null;
    const candidate = parts[idx - 1] ?? "";
    if (!candidate || candidate === "p" || candidate === "reel") return null;
    return candidate;
  } catch {
    return null;
  }
}

function extractShortcode(url: string): string {
  try {
    const u = new URL(url);
    const parts = u.pathname.split("/").filter(Boolean);
    const idx = parts.findIndex((p) => p === "p" || p === "reel");
    const code = idx >= 0 ? parts[idx + 1] : null;
    return code ?? "";
  } catch {
    return "";
  }
}

function guessMediaType(url: string, ldJsonItems: unknown[], html: string | null): InstagramMediaType {
  try {
    const u = new URL(url);
    if (u.pathname.includes("/reel/")) return "reel";
    if (u.pathname.includes("/p/")) {
      if (html) {
        const lower = html.toLowerCase();
        if (lower.includes('"__typename":"graphsidecar"') || lower.includes("edge_sidecar_to_children")) return "carousel";
        if (lower.includes('"is_video":true') || lower.includes('"video_view_count"') || lower.includes('"play_count"')) return "video";
      }
      if (hasVideoObject(ldJsonItems)) return "video";
      return "post";
    }
    return "unknown";
  } catch {
    return "unknown";
  }
}

function hasVideoObject(items: unknown[]): boolean {
  for (const item of items) {
    if (findVideoObjectInUnknown(item)) return true;
  }
  return false;
}

function findVideoObjectInUnknown(value: unknown): boolean {
  if (!value) return false;
  if (Array.isArray(value)) return value.some((v) => findVideoObjectInUnknown(v));
  if (typeof value !== "object") return false;
  const obj = value as Record<string, unknown>;
  const type = String(obj["@type"] ?? "");
  if (type.toLowerCase() === "videoobject") return true;
  if (obj["@graph"]) return findVideoObjectInUnknown(obj["@graph"]);
  return Object.values(obj).some((v) => findVideoObjectInUnknown(v));
}

function extractCaptionFromLdJson(items: unknown[]): string | null {
  const caption = findFirstStringField(items, new Set(["caption"]));
  if (caption) return caption;
  const desc = findFirstStringField(items, new Set(["description"]));
  return desc;
}

async function extractCaptionFromArticle(page: Page): Promise<string | null> {
  return await page
    .evaluate(() => {
      const article = document.querySelector("article");
      const text = (article?.innerText ?? "").trim();
      return text ? text : null;
    })
    .catch(() => null);
}

function findFirstStringField(value: unknown, keys: Set<string>): string | null {
  if (!value) return null;
  if (typeof value === "string") return null;

  if (Array.isArray(value)) {
    for (const item of value) {
      const found = findFirstStringField(item, keys);
      if (found) return found;
    }
    return null;
  }

  if (typeof value !== "object") return null;
  const obj = value as Record<string, unknown>;
  for (const key of keys) {
    const v = obj[key];
    if (typeof v === "string" && v.trim()) return v.trim();
  }

  for (const v of Object.values(obj)) {
    const found = findFirstStringField(v, keys);
    if (found) return found;
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
      parsed.push(JSON.parse(text as string));
    } catch {
      // ignore
    }
  }
  return parsed;
}

function extractViewsFromLdJson(items: unknown[]): number | null {
  const candidates: number[] = [];

  function visit(value: unknown): void {
    if (!value) return;
    if (Array.isArray(value)) {
      for (const v of value) visit(v);
      return;
    }
    if (typeof value !== "object") return;

    const obj = value as Record<string, unknown>;
    const stats = obj["interactionStatistic"];
    if (stats) {
      const arr = Array.isArray(stats) ? stats : [stats];
      for (const s of arr) {
        if (!s || typeof s !== "object") continue;
        const stat = s as Record<string, unknown>;
        const countRaw = stat["userInteractionCount"];
        const name = String(stat["name"] ?? "").toLowerCase();
        const interactionType = stat["interactionType"];
        const typeStr =
          typeof interactionType === "string"
            ? interactionType
            : interactionType && typeof interactionType === "object"
              ? String((interactionType as Record<string, unknown>)["@type"] ?? "")
              : "";
        const typeLower = typeStr.toLowerCase();

        const looksLikeView =
          typeLower.includes("watchaction") || name.includes("view") || name.includes("visualiza") || name.includes("play");
        if (!looksLikeView) continue;

        const n = typeof countRaw === "number" ? countRaw : parseCompactNumber(String(countRaw ?? ""));
        if (n != null) candidates.push(n);
      }
    }

    for (const v of Object.values(obj)) visit(v);
  }

  visit(items);
  if (!candidates.length) return null;
  return Math.max(...candidates);
}

function extractViewsFromHtml(html: string | null): number | null {
  const raw = String(html ?? "");
  if (!raw) return null;

  const patterns: RegExp[] = [
    /"play_count"\s*:\s*"?(\d+)"?/,
    /"video_view_count"\s*:\s*"?(\d+)"?/,
    /"view_count"\s*:\s*"?(\d+)"?/,
  ];

  for (const re of patterns) {
    const m = raw.match(re);
    if (!m) continue;
    const n = Number(m[1]);
    if (Number.isFinite(n)) return n;
  }

  return null;
}

 async function extractViewsFromDom(page: Page): Promise<number | null> {
  const text = await page.evaluate(() => document.body?.innerText ?? "").catch(() => "");

  const m = String(text).match(
    /([\d.,]+\s*(?:k|m|b|mil|mi|milh[\p{L}]*|bi|bilh[\p{L}]*)?)\s*(views?|visualiza|plays?)/iu,
  );
  if (!m) return null;
  return parseCompactNumber(m[1]);
}

async function collectPostUrls(page: Page, max: number, logger: Logger): Promise<string[]> {
  const urls = new Set<string>();

  const maxScrolls = Math.min(2000, Math.max(40, Math.ceil(max / 12) * 4));
  let stableRounds = 0;
  for (let i = 0; i < maxScrolls && urls.size < max && stableRounds < 3; i++) {
    const hrefs = await page
      .$$eval('a[href*="/p/"], a[href*="/reel/"]', (anchors) =>
        anchors.map((a) => (a as HTMLAnchorElement).href).filter(Boolean),
      )
      .catch(() => [] as string[]);

    const before = urls.size;
    for (const href of hrefs) {
      const cleaned = stripQuery(href);
      if (!isInstagramPostUrl(cleaned)) continue;
      urls.add(cleaned);
    }
    const after = urls.size;
    if (after === before) stableRounds += 1;
    else stableRounds = 0;

    logger.info(`Instagram: scroll ${i + 1}, urls=${urls.size}`);
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await sleep(800, 900);
  }

  return [...urls].slice(0, max);
}

async function extractProfileSnapshot(page: Page, url: string): Promise<ProfileSnapshot> {
  const metaDescription = await getMetaContent(page, 'meta[name="description"]');
  const ogTitle = await getMetaContent(page, 'meta[property="og:title"]');
  const ogDescription = await getMetaContent(page, 'meta[property="og:description"]');

  const metrics = parseInstagramProfileMetrics(metaDescription ?? "");

  return {
    url,
    fetched_at: new Date().toISOString(),
    metaDescription: metaDescription ?? null,
    ogTitle: ogTitle ?? null,
    ogDescription: ogDescription ?? null,
    metrics,
  };
}

function parseInstagramProfileMetrics(metaDescription: string): ProfileSnapshot["metrics"] {
  const fallback = { followers: null, following: null, posts: null };
  if (!metaDescription) return fallback;

  const head = metaDescription.split("-")[0] ?? metaDescription;
  const parts = head.split(",").map((p) => p.trim());

  let followers: number | null = null;
  let following: number | null = null;
  let posts: number | null = null;

  for (const part of parts) {
    const countText =
      part.match(/^[\d.,]+\s*(?:k|m|b|mil|mi|milh[\p{L}]*|bi|bilh[\p{L}]*)?/iu)?.[0]?.trim() ?? "";
    const count = parseCompactNumber(countText);
    if (count == null) continue;

    if (/followers?/i.test(part) || /seguidores?/iu.test(part)) followers = count;
    else if (/following/i.test(part) || /seguindo/iu.test(part)) following = count;
    else if (/posts?/i.test(part) || /publica/iu.test(part)) posts = count;
  }

  if (followers != null || following != null || posts != null) return { followers, following, posts };

  // English: "123K Followers, 12 Following, 34 Posts - ..."
  const en = metaDescription.match(/([\d.,KMB]+)\s+Followers?,\s+([\d.,KMB]+)\s+Following,\s+([\d.,KMB]+)\s+Posts/i);
  if (en) {
    return {
      followers: parseCompactNumber(en[1]),
      following: parseCompactNumber(en[2]),
      posts: parseCompactNumber(en[3]),
    };
  }

  // Portuguese: "123 mil seguidores, 12 seguindo, 34 publicações - ..."
  const pt = metaDescription.match(/([\d.,KMB]+)\s+seguidores?,\s+([\d.,KMB]+)\s+seguindo,\s+([\d.,KMB]+)\s+publica/iu);
  if (pt) {
    return {
      followers: parseCompactNumber(pt[1]),
      following: parseCompactNumber(pt[2]),
      posts: parseCompactNumber(pt[3]),
    };
  }

  return fallback;
}

function extractCaptionFromMetaText(metaText: string | null): string | null {
  if (!metaText) return null;

  const ascii = metaText.match(/"([^"]*)"\s*[.!?…]*\s*$/);
  if (ascii) return ascii[1].trim();

  const curly = metaText.match(/“([^”]*)”\s*[.!?…]*\s*$/);
  if (curly) return curly[1].trim();

  const first = metaText.indexOf('"');
  const last = metaText.lastIndexOf('"');
  if (first >= 0 && last > first) return metaText.slice(first + 1, last).trim();

  return null;
}

function extractMetricsFromOgDescription(ogDescription: string | null): { likes: number | null; comments: number | null; views: number | null } {
  if (!ogDescription) return { likes: null, comments: null, views: null };

  const token = /([\d.,]+\s*(?:k|m|b|mil|mi|milh[\p{L}]*|bi|bilh[\p{L}]*)?)/iu;

  const likesEnhanced =
    matchNumber(ogDescription, new RegExp(`${token.source}\\s+likes`, "iu")) ??
    matchNumber(ogDescription, new RegExp(`${token.source}\\s+curtidas?`, "iu"));
  const commentsEnhanced =
    matchNumber(ogDescription, new RegExp(`${token.source}\\s+comments?`, "iu")) ??
    matchNumber(ogDescription, new RegExp(`${token.source}\\s+coment`, "iu"));
  const viewsEnhanced =
    matchNumber(ogDescription, new RegExp(`${token.source}\\s+views?`, "iu")) ??
    matchNumber(ogDescription, new RegExp(`${token.source}\\s+visualiza`, "iu")) ??
    matchNumber(ogDescription, new RegExp(`${token.source}\\s+plays?`, "iu"));

  if (likesEnhanced != null || commentsEnhanced != null || viewsEnhanced != null) {
    return { likes: likesEnhanced, comments: commentsEnhanced, views: viewsEnhanced };
  }

  const likes =
    matchNumber(ogDescription, /([\d.,KMB]+)\s+likes/i) ?? matchNumber(ogDescription, /([\d.,KMB]+)\s+curtidas?/iu);
  const comments =
    matchNumber(ogDescription, /([\d.,KMB]+)\s+comments?/i) ??
    matchNumber(ogDescription, /([\d.,KMB]+)\s+coment[aá]rios?/iu);
  const views =
    matchNumber(ogDescription, /([\d.,KMB]+)\s+views?/i) ??
    matchNumber(ogDescription, /([\d.,KMB]+)\s+visualiza/iu) ??
    matchNumber(ogDescription, /([\d.,KMB]+)\s+plays?/i);

  return { likes, comments, views };
}

function matchNumber(text: string, re: RegExp): number | null {
  const match = text.match(re);
  if (!match) return null;
  return parseCompactNumber(match[1]);
}

async function getMetaContent(page: Page, selector: string): Promise<string | null> {
  return (await page.locator(selector).first().getAttribute("content").catch(() => null)) ?? null;
}

async function bestEffortDismissBanners(page: Page): Promise<void> {
  const candidates = [
    'button:has-text("Agora não")',
    'button:has-text("Not now")',
    'svg[aria-label="Close"]',
    'svg[aria-label="Fechar"]',
    'button[aria-label="Close"]',
    'button[aria-label="Fechar"]',
    'button:has-text("Aceitar")',
    'button:has-text("Permitir")',
    'button:has-text("Accept")',
    'button:has-text("Allow")',
    'button:has-text("OK")',
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

function isInstagramPostUrl(url: string): boolean {
  try {
    const u = new URL(url);
    if (!/instagram\.com$/i.test(u.hostname)) return false;
    return /^\/(?:[^/]+\/)?(p|reel)\/[^/]+\/?$/.test(u.pathname);
  } catch {
    return false;
  }
}
