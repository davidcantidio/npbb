import type { InstagramPost, Summary, SummaryTopItem, TikTokVideo, XTweet } from "./types";

/** True if post datetime falls in [since, until] (inclusive), matching CLI --since/--until semantics. */
export function isInReportPeriod(datetime: string | null, since: Date | null, until: Date | null): boolean {
  if (!since && !until) return true;
  if (!datetime) return false;
  const dt = new Date(datetime).getTime();
  if (!Number.isFinite(dt)) return false;
  if (since && dt < since.getTime()) return false;
  if (until && dt > until.getTime()) return false;
  return true;
}

/** Filter items for summary stats; full CSVs stay unfiltered. */
export function filterByReportPeriod<T extends { datetime: string | null }>(items: T[], since: Date | null, until: Date | null): T[] {
  if (!since && !until) return items;
  return items.filter((item) => isInReportPeriod(item.datetime, since, until));
}

export function buildSummary(instagramPosts: InstagramPost[], xTweets: XTweet[], tiktokVideos: TikTokVideo[]): Summary {
  const total_itens_ig = instagramPosts.length;
  const total_itens_x = xTweets.length;
  const total_itens_tiktok = tiktokVideos.length;

  const bb_mentions_ig = instagramPosts.filter((p) => p.is_bb_mention).length;
  const bb_mentions_x = xTweets.filter((t) => t.is_bb_mention).length;
  const bb_mentions_tiktok = tiktokVideos.filter((v) => v.is_bb_mention).length;

  const share_bb_ig = total_itens_ig === 0 ? 0 : bb_mentions_ig / total_itens_ig;
  const share_bb_x = total_itens_x === 0 ? 0 : bb_mentions_x / total_itens_x;
  const share_bb_tiktok = total_itens_tiktok === 0 ? 0 : bb_mentions_tiktok / total_itens_tiktok;

  const last_bb_datetime_ig = latestBbDatetime(instagramPosts.map((p) => ({ is_bb_mention: p.is_bb_mention, datetime: p.datetime })));
  const last_bb_datetime_x = latestBbDatetime(xTweets.map((t) => ({ is_bb_mention: t.is_bb_mention, datetime: t.datetime })));
  const last_bb_datetime_tiktok = latestBbDatetime(tiktokVideos.map((v) => ({ is_bb_mention: v.is_bb_mention, datetime: v.datetime })));

  const top_hashtags_bb = topFromBbItems([
    ...instagramPosts.map((p) => ({ isBb: p.is_bb_mention, values: p.hashtags })),
    ...xTweets.map((t) => ({ isBb: t.is_bb_mention, values: t.hashtags })),
    ...tiktokVideos.map((v) => ({ isBb: v.is_bb_mention, values: v.hashtags })),
  ]);

  const top_mentions_bb = topFromBbItems([
    ...instagramPosts.map((p) => ({ isBb: p.is_bb_mention, values: p.mentions })),
    ...xTweets.map((t) => ({ isBb: t.is_bb_mention, values: t.mentions })),
    ...tiktokVideos.map((v) => ({ isBb: v.is_bb_mention, values: v.mentions })),
  ]);

  return {
    total_itens_ig,
    total_itens_x,
    total_itens_tiktok,
    bb_mentions_ig,
    bb_mentions_x,
    bb_mentions_tiktok,
    share_bb_ig,
    share_bb_x,
    share_bb_tiktok,
    last_bb_datetime_ig,
    last_bb_datetime_x,
    last_bb_datetime_tiktok,
    top_hashtags_bb,
    top_mentions_bb,
  };
}

function latestBbDatetime(items: Array<{ is_bb_mention: boolean; datetime: string | null }>): string | null {
  let latest: string | null = null;
  for (const item of items) {
    if (!item.is_bb_mention) continue;
    if (!item.datetime) continue;
    if (!latest) {
      latest = item.datetime;
      continue;
    }
    if (new Date(item.datetime).getTime() > new Date(latest).getTime()) latest = item.datetime;
  }
  return latest;
}

function topFromBbItems(items: Array<{ isBb: boolean; values: string[] }>, limit = 15): SummaryTopItem[] {
  const counter = new Map<string, number>();
  for (const item of items) {
    if (!item.isBb) continue;
    for (const value of item.values) {
      const key = value.toLowerCase();
      counter.set(key, (counter.get(key) ?? 0) + 1);
    }
  }

  return [...counter.entries()]
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .slice(0, limit)
    .map(([value, count]) => ({ value, count }));
}
