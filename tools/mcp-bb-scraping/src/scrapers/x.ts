import type { BrowserContext, Page } from "playwright";
import type { ProfileSnapshot, XTweet } from "../types";
import { Logger } from "../logger";
import { parseCompactNumber } from "../utils/numbers";
import { analyzeBancoDoBrasilMention, extractHashtags, extractMentions, normalizeText } from "../parse";
import { sleep } from "../utils/sleep";

export interface XScrapeOptions {
  profileUrl: string;
  max: number;
  logger: Logger;
  timeoutMs: number;
}

export interface XScrapeResult {
  profile: ProfileSnapshot;
  tweets: XTweet[];
}

export async function scrapeX(context: BrowserContext, options: XScrapeOptions): Promise<XScrapeResult> {
  const page = await context.newPage();
  page.setDefaultTimeout(options.timeoutMs);
  page.setDefaultNavigationTimeout(options.timeoutMs);

  try {
    options.logger.info(`X: abrindo perfil ${options.profileUrl}`);
    await gotoWithRetries(page, options.profileUrl, options.timeoutMs, options.logger);
    await bestEffortDismissBanners(page);

    if (page.url().includes("/i/flow/login") || page.url().includes("/login")) {
      options.logger.warn("X: página redirecionou para login; gere uma sessão com `npm run auth:x` (salva em auth/x_state.json).");
    }

    const profile = await extractProfileSnapshot(page, options.profileUrl);

    await page.waitForSelector("article", { timeout: Math.min(10_000, options.timeoutMs) }).catch(() => undefined);

    const tweets = await collectTweets(page, options);
    options.logger.info(`X: coletados ${tweets.length} itens.`);
    return { profile, tweets };
  } finally {
    await page.close();
  }
}

async function collectTweets(page: Page, options: XScrapeOptions): Promise<XTweet[]> {
  const tweets: XTweet[] = [];
  const seen = new Set<string>();

  let stableRounds = 0;
  for (let i = 0; i < 60 && tweets.length < options.max && stableRounds < 3; i++) {
    const extracted = await extractTweetsFromDom(page);
    let added = 0;

    for (const item of extracted) {
      if (!item.tweet_url) continue;
      const url = stripQuery(item.tweet_url);
      if (seen.has(url)) continue;
      seen.add(url);

      const text = normalizeText(item.text ?? "");
      const hashtags = extractHashtags(text);
      const mentions = extractMentions(text);
      const bbAnalysis = analyzeBancoDoBrasilMention(text, { hashtags, mentions });

      const tweet: XTweet = {
        tweet_url: url,
        datetime: item.datetime ?? null,
        text,
        hashtags,
        mentions,
        is_bb_mention: bbAnalysis.is_bb_mention,
        bb_connection_type: bbAnalysis.connection_type,
        bb_markers_count: bbAnalysis.markers_count,
        replies: parseCompactNumber(item.replies_text ?? ""),
        reposts: parseCompactNumber(item.reposts_text ?? ""),
        likes: parseCompactNumber(item.likes_text ?? ""),
        views: parseCompactNumber(item.views_text ?? ""),
      };

      tweets.push(tweet);
      added += 1;
      if (tweets.length >= options.max) break;
    }

    if (added === 0) stableRounds += 1;
    else stableRounds = 0;

    options.logger.info(`X: scroll ${i + 1}, tweets=${tweets.length}`);
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await sleep(900, 900);
  }

  return tweets.slice(0, options.max);
}

type ExtractedTweet = {
  tweet_url: string | null;
  datetime: string | null;
  text: string | null;
  replies_text: string | null;
  reposts_text: string | null;
  likes_text: string | null;
  views_text: string | null;
};

async function extractTweetsFromDom(page: Page): Promise<ExtractedTweet[]> {
  return page
    .evaluate(() => {
      function metric(article: Element, testId: string): string | null {
        const el = article.querySelector(`[data-testid="${testId}"]`);
        if (!el) return null;
        const spans = Array.from(el.querySelectorAll("span"));
        for (const span of spans) {
          const t = (span.textContent ?? "").trim();
          if (!t) continue;
          if (/^\d/.test(t) || /^\d/.test(t.replace(",", "."))) return t;
          if (/^\d+(\.\d+)?[KMB]$/i.test(t.replace(",", "."))) return t;
        }
        return null;
      }

      function findTweetUrl(article: Element): string | null {
        const a = article.querySelector('a[href*="/status/"]') as HTMLAnchorElement | null;
        return a?.href ?? null;
      }

      function findText(article: Element): string | null {
        const el = article.querySelector('[data-testid="tweetText"]');
        return (el?.textContent ?? "").trim() || null;
      }

      function findViews(article: Element): string | null {
        const a = article.querySelector('a[href*="/analytics"]') as HTMLAnchorElement | null;
        if (!a) return null;
        const spans = Array.from(a.querySelectorAll("span"));
        for (const span of spans) {
          const t = (span.textContent ?? "").trim();
          if (!t) continue;
          if (/^\d/.test(t) || /^\d+(\.\d+)?[KMB]$/i.test(t.replace(",", "."))) return t;
        }
        return null;
      }

      const articles = Array.from(document.querySelectorAll("article"));
      const out: ExtractedTweet[] = [];
      for (const article of articles) {
        const time = article.querySelector("time");
        const datetime = time?.getAttribute("datetime") ?? null;
        out.push({
          tweet_url: findTweetUrl(article),
          datetime,
          text: findText(article),
          replies_text: metric(article, "reply"),
          reposts_text: metric(article, "retweet") ?? metric(article, "repost"),
          likes_text: metric(article, "like"),
          views_text: findViews(article),
        });
      }
      return out;
    })
    .catch(() => [] as ExtractedTweet[]);
}

async function extractProfileSnapshot(page: Page, url: string): Promise<ProfileSnapshot> {
  const metaDescription = await getMetaContent(page, 'meta[name="description"]');
  const ogTitle = await getMetaContent(page, 'meta[property="og:title"]');
  const ogDescription = await getMetaContent(page, 'meta[property="og:description"]');

  const metrics = parseXProfileMetrics(metaDescription ?? "");
  return {
    url,
    fetched_at: new Date().toISOString(),
    metaDescription: metaDescription ?? null,
    ogTitle: ogTitle ?? null,
    ogDescription: ogDescription ?? null,
    metrics,
  };
}

function parseXProfileMetrics(metaDescription: string): ProfileSnapshot["metrics"] {
  const fallback = { followers: null, following: null, posts: null };
  if (!metaDescription) return fallback;

  // Example (en): "123 Followers, 45 Following, 67 Posts - ..."
  const en = metaDescription.match(/([\d.,KMB]+)\s+Followers?,\s+([\d.,KMB]+)\s+Following,\s+([\d.,KMB]+)\s+(Posts|Tweets)/i);
  if (en) {
    return {
      followers: parseCompactNumber(en[1]),
      following: parseCompactNumber(en[2]),
      posts: parseCompactNumber(en[3]),
    };
  }

  // Example (pt): "123 seguidores, 45 seguindo"
  const pt = metaDescription.match(/([\d.,KMB]+)\s+seguidores?,\s+([\d.,KMB]+)\s+seguindo/iu);
  if (pt) {
    return {
      followers: parseCompactNumber(pt[1]),
      following: parseCompactNumber(pt[2]),
      posts: null,
    };
  }

  return fallback;
}

async function getMetaContent(page: Page, selector: string): Promise<string | null> {
  return (await page.locator(selector).first().getAttribute("content").catch(() => null)) ?? null;
}

async function bestEffortDismissBanners(page: Page): Promise<void> {
  const candidates = [
    'button:has-text("Not now")',
    'button:has-text("Agora não")',
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

async function gotoWithRetries(page: Page, url: string, timeoutMs: number, logger: Logger): Promise<void> {
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      await page.goto(url, { waitUntil: "domcontentloaded", timeout: timeoutMs });
      return;
    } catch (error) {
      logger.warn(`X: falha ao abrir ${url} (tentativa ${attempt}/3): ${String(error)}`);
      await sleep(500 * attempt, 800);
    }
  }
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: timeoutMs });
}
