export type IsoDateTimeString = string;

export type BbConnectionType = "mention" | "hashtag" | "mention-hashtag";

export interface InstagramPost {
  post_url: string;
  datetime: IsoDateTimeString | null;
  caption: string;
  hashtags: string[];
  mentions: string[];
  is_bb_mention: boolean;
  bb_connection_type: BbConnectionType | null;
  bb_markers_count: number;
  likes: number | null;
  comments: number | null;
  views: number | null;
}

export type InstagramMediaType = "reel" | "post" | "carousel" | "video" | "unknown";

export interface InstagramPostEnriched extends InstagramPost {
  owner_username: string | null;
  is_owner_profile: boolean;
  media_type: InstagramMediaType;
  shortcode: string;
  is_collab: boolean;
  coauthors: string[];
  paid_partnership: boolean;
  paid_partner: string | null;
  location: string | null;
  plays_or_views: number | null;
  scraped_at: IsoDateTimeString;
}

export interface XTweet {
  tweet_url: string;
  datetime: IsoDateTimeString | null;
  text: string;
  hashtags: string[];
  mentions: string[];
  is_bb_mention: boolean;
  bb_connection_type: BbConnectionType | null;
  bb_markers_count: number;
  replies: number | null;
  reposts: number | null;
  likes: number | null;
  views: number | null;
}

export interface TikTokVideo {
  video_url: string;
  datetime: IsoDateTimeString | null;
  caption: string;
  hashtags: string[];
  mentions: string[];
  is_bb_mention: boolean;
  bb_connection_type: BbConnectionType | null;
  bb_markers_count: number;
  likes: number | null;
  comments: number | null;
  shares: number | null;
  views: number | null;
}

export interface TikTokProfileSnapshot {
  url: string;
  fetched_at: IsoDateTimeString;
  username: string | null;
  display_name: string | null;
  bio: string | null;
  external_url: string | null;
  metaDescription: string | null;
  ogTitle: string | null;
  ogDescription: string | null;
  metrics: {
    followers: number | null;
    following: number | null;
    likes: number | null;
  };
}

export interface ProfileSnapshot {
  url: string;
  fetched_at: IsoDateTimeString;
  metaDescription: string | null;
  ogTitle: string | null;
  ogDescription: string | null;
  metrics: {
    followers: number | null;
    following: number | null;
    posts: number | null;
  };
}

export interface SummaryTopItem {
  value: string;
  count: number;
}

export interface Summary {
  total_itens_ig: number;
  total_itens_x: number;
  total_itens_tiktok: number;
  bb_mentions_ig: number;
  bb_mentions_x: number;
  bb_mentions_tiktok: number;
  share_bb_ig: number;
  share_bb_x: number;
  share_bb_tiktok: number;
  last_bb_datetime_ig: IsoDateTimeString | null;
  last_bb_datetime_x: IsoDateTimeString | null;
  last_bb_datetime_tiktok: IsoDateTimeString | null;
  top_hashtags_bb: SummaryTopItem[];
  top_mentions_bb: SummaryTopItem[];
}

export interface RunConfig {
  max: number;
  outDir: string;
  outputHandle: string | null;
  athleteName: string | null;
  since: Date | null;
  until: Date | null;
  headful: boolean;
  debug: boolean;
  timeoutMs: number;
  locale: string;
  cdpEndpoint: string | null;
  bbAliases: string[];
  authWarnings: string[];
  instagramProfileUrl: string;
  xProfileUrl: string;
  tiktokProfileUrl: string;
  instagramStorageStatePath: string | null;
  xStorageStatePath: string | null;
  tiktokStorageStatePath: string | null;
  scrapeInstagram: boolean;
  scrapeX: boolean;
  scrapeTikTok: boolean;
  publishEnabled: boolean;
  npbbApiBaseUrl: string | null;
  npbbApiToken: string | null;
  npbbApiEndpoint: string;
  publishTimeoutMs?: number;
}

// NPBB direct ingestion contracts
export interface ScrapingIngestionMeta {
  handle: string | null;
  athleteName: string | null;
  since: IsoDateTimeString | null;
  until: IsoDateTimeString | null;
  max: number;
  runStartedAt: IsoDateTimeString;
  runFinishedAt: IsoDateTimeString;
  generatedAt: IsoDateTimeString;
  scrapeInstagram: boolean;
  scrapeX: boolean;
  scrapeTikTok: boolean;
}

export interface ScrapingIngestionPlatforms {
  instagramPosts: InstagramPostEnriched[];
  xTweets: XTweet[];
  tiktokVideos: TikTokVideo[];
}

export interface ScrapingIngestionProfiles {
  instagram: ProfileSnapshot | null;
  x: ProfileSnapshot | null;
  tiktok: TikTokProfileSnapshot | null;
}

export interface ScrapingIngestionPayload {
  meta: ScrapingIngestionMeta;
  platforms: ScrapingIngestionPlatforms;
  profiles: ScrapingIngestionProfiles;
  summary: Summary;
  raw?: Record<string, unknown>;
}

export interface PublishResult {
  ok: boolean;
  status: number | null;
  ingestionId?: string | number | null;
  message?: string | null;
  errorCode?: string | null;
}
