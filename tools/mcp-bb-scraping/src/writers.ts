import { writeFile } from "node:fs/promises";
import type { InstagramPost, InstagramPostEnriched, ProfileSnapshot, Summary, TikTokProfileSnapshot, TikTokVideo, XTweet } from "./types";
import { toCsv } from "./utils/csv";
import { ensureDir } from "./utils/fs";
import { outputPath, outputPostsPath } from "./utils/output";

export async function writeUnifiedPostsCsv(
  outDir: string,
  instagramPosts: InstagramPost[],
  xTweets: XTweet[],
  tiktokVideos: TikTokVideo[],
  handle: string | null = null,
): Promise<void> {
  await ensureDir(outDir);

  const headers = [
    "platform",
    "url",
    "datetime",
    "date",
    "text",
    "hashtags",
    "mentions",
    "is_bb_mention",
    "bb_connection_type",
    "bb_markers_count",
    "likes",
    "comments",
    "views",
    "replies",
    "reposts",
    "shares",
  ];

  const rows: string[][] = [];

  for (const post of instagramPosts) {
    rows.push([
      "instagram",
      post.post_url,
      post.datetime ?? "",
      formatIsoDate(post.datetime),
      post.caption ?? "",
      post.hashtags.join("|"),
      post.mentions.join("|"),
      String(post.is_bb_mention),
      post.bb_connection_type ?? "",
      String(post.bb_markers_count),
      post.likes == null ? "" : String(post.likes),
      post.comments == null ? "" : String(post.comments),
      post.views == null ? "" : String(post.views),
      "",
      "",
      "",
    ]);
  }

  for (const tweet of xTweets) {
    rows.push([
      "x",
      tweet.tweet_url,
      tweet.datetime ?? "",
      formatIsoDate(tweet.datetime),
      tweet.text ?? "",
      tweet.hashtags.join("|"),
      tweet.mentions.join("|"),
      String(tweet.is_bb_mention),
      tweet.bb_connection_type ?? "",
      String(tweet.bb_markers_count),
      tweet.likes == null ? "" : String(tweet.likes),
      "",
      tweet.views == null ? "" : String(tweet.views),
      tweet.replies == null ? "" : String(tweet.replies),
      tweet.reposts == null ? "" : String(tweet.reposts),
      "",
    ]);
  }

  for (const video of tiktokVideos) {
    rows.push([
      "tiktok",
      video.video_url,
      video.datetime ?? "",
      formatIsoDate(video.datetime),
      video.caption ?? "",
      video.hashtags.join("|"),
      video.mentions.join("|"),
      String(video.is_bb_mention),
      video.bb_connection_type ?? "",
      String(video.bb_markers_count),
      video.likes == null ? "" : String(video.likes),
      video.comments == null ? "" : String(video.comments),
      video.views == null ? "" : String(video.views),
      "",
      "",
      video.shares == null ? "" : String(video.shares),
    ]);
  }

  const csv = toCsv(headers, rows);
  await writeFile(outputPath(outDir, "posts", "csv", handle), csv, "utf8");
}

export async function writeInstagramPostsCsv(outDir: string, posts: InstagramPost[], handle: string | null = null): Promise<void> {
  await ensureDir(outDir);
  const headers = [
    "post_url",
    "datetime",
    "date",
    "caption",
    "hashtags",
    "mentions",
    "is_bb_mention",
    "bb_connection_type",
    "bb_markers_count",
    "likes",
    "comments",
    "views",
  ];
  const rows = posts.map((p) => [
    p.post_url,
    p.datetime ?? "",
    formatIsoDate(p.datetime),
    p.caption ?? "",
    p.hashtags.join("|"),
    p.mentions.join("|"),
    String(p.is_bb_mention),
    p.bb_connection_type ?? "",
    String(p.bb_markers_count),
    p.likes == null ? "" : String(p.likes),
    p.comments == null ? "" : String(p.comments),
    p.views == null ? "" : String(p.views),
  ]);
  const csv = toCsv(headers, rows);
  await writeFile(outputPath(outDir, "instagram_posts", "csv", handle), csv, "utf8");
}

export async function writeInstagramPostsEnrichedCsv(
  outDir: string,
  posts: InstagramPostEnriched[],
  handle: string | null = null,
  athleteName: string | null = null,
): Promise<void> {
  await ensureDir(outDir);
  const headers = [
    "post_url",
    "datetime",
    "date",
    "caption",
    "hashtags",
    "mentions",
    "is_bb_mention",
    "bb_connection_type",
    "bb_markers_count",
    "likes",
    "comments",
    "views",
    "owner_username",
    "is_owner_profile",
    "media_type",
    "shortcode",
    "is_collab",
    "coauthors",
    "paid_partnership",
    "paid_partner",
    "location",
    "plays_or_views",
    "scraped_at",
  ];

  const rows = posts.map((p) => [
    p.post_url,
    p.datetime ?? "",
    formatIsoDate(p.datetime),
    p.caption ?? "",
    p.hashtags.join("|"),
    p.mentions.join("|"),
    String(p.is_bb_mention),
    p.bb_connection_type ?? "",
    String(p.bb_markers_count),
    p.likes == null ? "" : String(p.likes),
    p.comments == null ? "" : String(p.comments),
    p.views == null ? "" : String(p.views),
    p.owner_username ?? "",
    String(p.is_owner_profile),
    p.media_type,
    p.shortcode ?? "",
    String(p.is_collab),
    p.coauthors.join("|"),
    String(p.paid_partnership),
    p.paid_partner ?? "",
    p.location ?? "",
    p.plays_or_views == null ? "" : String(p.plays_or_views),
    p.scraped_at ?? "",
  ]);

  const csv = toCsv(headers, rows);
  await writeFile(outputPostsPath(outDir, athleteName, handle, "csv"), csv, "utf8");
}

export async function writeInstagramPostsEnrichedJson(
  outDir: string,
  posts: InstagramPostEnriched[],
  handle: string | null = null,
  athleteName: string | null = null,
): Promise<void> {
  await ensureDir(outDir);
  const json = JSON.stringify(posts, null, 2);
  await writeFile(outputPostsPath(outDir, athleteName, handle, "json"), json, "utf8");
}

export async function writeXTweetsCsv(outDir: string, tweets: XTweet[], handle: string | null = null): Promise<void> {
  await ensureDir(outDir);
  const headers = [
    "tweet_url",
    "datetime",
    "date",
    "text",
    "hashtags",
    "mentions",
    "is_bb_mention",
    "bb_connection_type",
    "bb_markers_count",
    "replies",
    "reposts",
    "likes",
    "views",
  ];
  const rows = tweets.map((t) => [
    t.tweet_url,
    t.datetime ?? "",
    formatIsoDate(t.datetime),
    t.text ?? "",
    t.hashtags.join("|"),
    t.mentions.join("|"),
    String(t.is_bb_mention),
    t.bb_connection_type ?? "",
    String(t.bb_markers_count),
    t.replies == null ? "" : String(t.replies),
    t.reposts == null ? "" : String(t.reposts),
    t.likes == null ? "" : String(t.likes),
    t.views == null ? "" : String(t.views),
  ]);
  const csv = toCsv(headers, rows);
  await writeFile(outputPath(outDir, "x_tweets", "csv", handle), csv, "utf8");
}

export async function writeInstagramProfileCsv(
  outDir: string,
  profile: ProfileSnapshot,
  handle: string | null = null,
): Promise<void> {
  await ensureDir(outDir);
  const headers = ["url", "fetched_at", "followers", "following", "posts", "metaDescription", "ogTitle", "ogDescription"];
  const rows = [
    [
      profile.url,
      profile.fetched_at,
      formatNullableNumber(profile.metrics.followers),
      formatNullableNumber(profile.metrics.following),
      formatNullableNumber(profile.metrics.posts),
      profile.metaDescription ?? "",
      profile.ogTitle ?? "",
      profile.ogDescription ?? "",
    ],
  ];
  const csv = toCsv(headers, rows);
  await writeFile(outputPath(outDir, "instagram_profile", "csv", handle), csv, "utf8");
}

export async function writeInstagramProfileJson(
  outDir: string,
  profile: ProfileSnapshot,
  handle: string | null = null,
): Promise<void> {
  await ensureDir(outDir);
  const data = {
    url: profile.url,
    collected_at: profile.fetched_at,
    followers: profile.metrics.followers,
    following: profile.metrics.following,
    posts_count: profile.metrics.posts,
    metaDescription: profile.metaDescription,
    ogTitle: profile.ogTitle,
    ogDescription: profile.ogDescription,
  };
  await writeFile(outputPath(outDir, "instagram_profile", "json", handle), JSON.stringify(data, null, 2), "utf8");
}

export async function writeXProfileCsv(outDir: string, profile: ProfileSnapshot, handle: string | null = null): Promise<void> {
  await ensureDir(outDir);
  const headers = ["url", "fetched_at", "followers", "following", "posts", "metaDescription", "ogTitle", "ogDescription"];
  const rows = [
    [
      profile.url,
      profile.fetched_at,
      formatNullableNumber(profile.metrics.followers),
      formatNullableNumber(profile.metrics.following),
      formatNullableNumber(profile.metrics.posts),
      profile.metaDescription ?? "",
      profile.ogTitle ?? "",
      profile.ogDescription ?? "",
    ],
  ];
  const csv = toCsv(headers, rows);
  await writeFile(outputPath(outDir, "x_profile", "csv", handle), csv, "utf8");
}

export async function writeSummaryCsv(outDir: string, summary: Summary, handle: string | null = null): Promise<void> {
  await ensureDir(outDir);
  const headers = [
    "total_itens_ig",
    "total_itens_x",
    "total_itens_tiktok",
    "bb_mentions_ig",
    "bb_mentions_x",
    "bb_mentions_tiktok",
    "share_bb_ig",
    "share_bb_x",
    "share_bb_tiktok",
    "last_bb_datetime_ig",
    "last_bb_datetime_x",
    "last_bb_datetime_tiktok",
  ];
  const rows = [
    [
      String(summary.total_itens_ig),
      String(summary.total_itens_x),
      String(summary.total_itens_tiktok),
      String(summary.bb_mentions_ig),
      String(summary.bb_mentions_x),
      String(summary.bb_mentions_tiktok),
      formatNullableDecimal(summary.share_bb_ig),
      formatNullableDecimal(summary.share_bb_x),
      formatNullableDecimal(summary.share_bb_tiktok),
      summary.last_bb_datetime_ig ?? "",
      summary.last_bb_datetime_x ?? "",
      summary.last_bb_datetime_tiktok ?? "",
    ],
  ];
  const csv = toCsv(headers, rows);
  await writeFile(outputPath(outDir, "summary", "csv", handle), csv, "utf8");

  await writeTopListCsv(outDir, "top_hashtags_bb", "hashtag", summary.top_hashtags_bb, handle);
  await writeTopListCsv(outDir, "top_mentions_bb", "mention", summary.top_mentions_bb, handle);
}

export async function writeIgLinksCsv(outDir: string, links: string[], handle: string | null = null): Promise<void> {
  await ensureDir(outDir);
  const headers = ["post_url"];
  const rows = links.map((l) => [l]);
  const csv = toCsv(headers, rows);
  await writeFile(outputPath(outDir, "ig_links", "csv", handle), csv, "utf8");
}

export async function writeTikTokVideosCsv(outDir: string, videos: TikTokVideo[], handle: string | null = null): Promise<void> {
  await ensureDir(outDir);
  const headers = [
    "video_url",
    "datetime",
    "date",
    "caption",
    "hashtags",
    "mentions",
    "is_bb_mention",
    "bb_connection_type",
    "bb_markers_count",
    "likes",
    "comments",
    "shares",
    "views",
  ];
  const rows = videos.map((v) => [
    v.video_url,
    v.datetime ?? "",
    formatIsoDate(v.datetime),
    v.caption ?? "",
    v.hashtags.join("|"),
    v.mentions.join("|"),
    String(v.is_bb_mention),
    v.bb_connection_type ?? "",
    String(v.bb_markers_count),
    v.likes == null ? "" : String(v.likes),
    v.comments == null ? "" : String(v.comments),
    v.shares == null ? "" : String(v.shares),
    v.views == null ? "" : String(v.views),
  ]);
  const csv = toCsv(headers, rows);
  await writeFile(outputPath(outDir, "tiktok_videos", "csv", handle), csv, "utf8");
}

export async function writeTikTokProfileCsv(
  outDir: string,
  profile: TikTokProfileSnapshot,
  handle: string | null = null,
): Promise<void> {
  await ensureDir(outDir);
  const headers = [
    "url",
    "fetched_at",
    "username",
    "display_name",
    "followers",
    "following",
    "likes",
    "bio",
    "external_url",
    "metaDescription",
    "ogTitle",
    "ogDescription",
  ];
  const rows = [
    [
      profile.url,
      profile.fetched_at,
      profile.username ?? "",
      profile.display_name ?? "",
      formatNullableNumber(profile.metrics.followers),
      formatNullableNumber(profile.metrics.following),
      formatNullableNumber(profile.metrics.likes),
      profile.bio ?? "",
      profile.external_url ?? "",
      profile.metaDescription ?? "",
      profile.ogTitle ?? "",
      profile.ogDescription ?? "",
    ],
  ];
  const csv = toCsv(headers, rows);
  await writeFile(outputPath(outDir, "tiktok_profile", "csv", handle), csv, "utf8");
}

export async function writeTikTokLinksCsv(outDir: string, links: string[], handle: string | null = null): Promise<void> {
  await ensureDir(outDir);
  const headers = ["video_url"];
  const rows = links.map((l) => [l]);
  const csv = toCsv(headers, rows);
  await writeFile(outputPath(outDir, "tiktok_links", "csv", handle), csv, "utf8");
}

async function writeTopListCsv(
  outDir: string,
  baseName: string,
  label: string,
  items: Array<{ value: string; count: number }>,
  handle: string | null = null,
): Promise<void> {
  const headers = [label, "count"];
  const rows = items.map((i) => [i.value, String(i.count)]);
  const csv = toCsv(headers, rows);
  await writeFile(outputPath(outDir, baseName, "csv", handle), csv, "utf8");
}

function formatNullableNumber(value: number | null): string {
  return value == null ? "" : String(value);
}

function formatNullableDecimal(value: number | null): string {
  if (value == null) return "";
  // Excel pt-BR costuma interpretar decimal com vírgula.
  return String(value).replace(".", ",");
}

function formatIsoDate(value: string | null | undefined): string {
  const raw = (value ?? "").trim();
  if (!raw) return "";

  if (raw.length >= 10 && raw[4] === "-" && raw[7] === "-") return raw.slice(0, 10);

  const d = new Date(raw);
  return Number.isNaN(d.getTime()) ? "" : d.toISOString().slice(0, 10);
}
