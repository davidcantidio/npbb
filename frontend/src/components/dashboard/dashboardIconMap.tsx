import QueryStatsRoundedIcon from "@mui/icons-material/QueryStatsRounded";
import TaskAltRoundedIcon from "@mui/icons-material/TaskAltRounded";
import TrendingUpRoundedIcon from "@mui/icons-material/TrendingUpRounded";
import CampaignRoundedIcon from "@mui/icons-material/CampaignRounded";

import type { DashboardIconKey } from "../../types/dashboard";

type DashboardIconComponent = typeof QueryStatsRoundedIcon;

const DASHBOARD_ICON_MAP: Record<DashboardIconKey, DashboardIconComponent> = {
  "age-analysis": QueryStatsRoundedIcon,
  "event-closure": TaskAltRoundedIcon,
  "event-conversion": TrendingUpRoundedIcon,
  "media-coverage": CampaignRoundedIcon,
};

export function getDashboardIcon(icon: DashboardIconKey): DashboardIconComponent {
  return DASHBOARD_ICON_MAP[icon];
}
