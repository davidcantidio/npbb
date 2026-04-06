import type { BbConnectionType } from "./types";

const HASHTAG_RE = /#[\p{L}\p{N}_]+/gu;
const MENTION_RE = /@[\p{L}\p{N}_.]+/gu;

export interface BancoDoBrasilMentionOptions {
  aliases?: string[];
  mentions?: string[];
  hashtags?: string[];
}

export interface BancoDoBrasilAnalysis {
  is_bb_mention: boolean;
  connection_type: BbConnectionType | null;
  markers_count: number;
}


export const DEFAULT_BB_ALIASES = [
  "@bancodobrasil",
  "@bancodobrasiloficial",
  "banco do brasil",
  "#bancodobrasil",
  "#bancodobrasiloficial",
  "#tamojuntobb",
  "#squadbb",
  "@festivaltamojuntobb",
  "#festivaltamojuntobb",
];

export function buildBancoDoBrasilAliases(extra: string[] = []): string[] {
  const out: string[] = [];
  const seen = new Set<string>();

  for (const alias of [...DEFAULT_BB_ALIASES, ...extra]) {
    const normalized = normalizeText(String(alias ?? "")).toLowerCase();
    if (!normalized) continue;
    if (seen.has(normalized)) continue;
    seen.add(normalized);
    out.push(normalized);
  }

  return out;
}

export function normalizeText(text: string): string {
  return text.replace(/\s+/g, " ").trim();
}

export function extractHashtags(text: string): string[] {
  return uniqueInOrder(normalizeText(text).match(HASHTAG_RE) ?? []);
}

export function extractMentions(text: string): string[] {
  return uniqueInOrder(normalizeText(text).match(MENTION_RE) ?? []);
}

export function isBancoDoBrasilMentionLegacy(text: string): boolean {
  const normalized = normalizeText(text).toLowerCase();

  if (normalized.includes("@bancodobrasil")) return true;
  if (normalized.includes("#bancodobrasil")) return true;
  if (normalized.includes("banco do brasil")) return true;

  const hasBbToken = /(^|[^a-z0-9])bb([^a-z0-9]|$)/.test(normalized);
  if (hasBbToken && (normalized.includes("banco") || normalized.includes("brasil"))) return true;

  return false;
}

export function isBancoDoBrasilMention(text: string, options: BancoDoBrasilMentionOptions = {}): boolean {
  return analyzeBancoDoBrasilMention(text, options).is_bb_mention;
}


export function analyzeBancoDoBrasilMention(text: string, options: BancoDoBrasilMentionOptions = {}): BancoDoBrasilAnalysis {
  const normalizedText = normalizeText(text).toLowerCase();
  const aliases = buildBancoDoBrasilAliases(options.aliases ?? []);
  const aliasGroups = splitAliasesByType(aliases);

  const mentions = (options.mentions ?? extractMentions(text)).map((m) => m.toLowerCase());
  const hashtags = (options.hashtags ?? extractHashtags(text)).map((h) => h.toLowerCase());

  const foundMentions = new Set<string>();
  for (const mention of mentions) {
    if (aliasGroups.mentions.has(mention)) foundMentions.add(mention);
  }

  const foundHashtags = new Set<string>();
  for (const hashtag of hashtags) {
    if (aliasGroups.hashtags.has(hashtag)) foundHashtags.add(hashtag);
  }

  const foundText = new Set<string>();
  for (const alias of aliasGroups.text) {
    if (normalizedText.includes(alias)) foundText.add(alias);
  }

  const hasBbToken = /(^|[^a-z0-9])bb([^a-z0-9]|$)/.test(normalizedText);
  if (hasBbToken && (normalizedText.includes("banco") || normalizedText.includes("brasil"))) {
    foundText.add("bb");
  }

  const hasMention = foundMentions.size > 0;
  const hasHashtag = foundHashtags.size > 0;
  const hasText = foundText.size > 0;

  let connectionType: BbConnectionType | null = null;
  if (hasMention && hasHashtag) connectionType = "mention-hashtag";
  else if (hasHashtag) connectionType = "hashtag";
  else if (hasMention || hasText) connectionType = "mention";

  const markersCount = foundMentions.size + foundHashtags.size + foundText.size;
  const is_bb_mention = markersCount > 0;

  return { is_bb_mention, connection_type: connectionType, markers_count: markersCount };
}

type AliasGroups = {
  mentions: Set<string>;
  hashtags: Set<string>;
  text: Set<string>;
};

function splitAliasesByType(aliases: string[]): AliasGroups {
  const groups: AliasGroups = {
    mentions: new Set<string>(),
    hashtags: new Set<string>(),
    text: new Set<string>(),
  };

  for (const alias of aliases) {
    if (!alias) continue;
    if (alias.startsWith("@")) groups.mentions.add(alias);
    else if (alias.startsWith("#")) groups.hashtags.add(alias);
    else groups.text.add(alias);
  }

  return groups;
}

function uniqueInOrder(items: string[]): string[] {
  const seen = new Set<string>();
  const result: string[] = [];
  for (const item of items) {
    const key = item.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    result.push(item);
  }
  return result;
}
