export type DashboardIconKey =
  | "age-analysis"
  | "event-closure"
  | "event-conversion"
  | "media-coverage";

export type DashboardManifestEntry = {
  id: string;
  route: string;
  domain: string;
  name: string;
  icon: DashboardIconKey;
  description: string;
  enabled: boolean;
};
