import ChevronRightRoundedIcon from "@mui/icons-material/ChevronRightRounded";
import {
  Box,
  Chip,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Tooltip,
  Typography,
} from "@mui/material";
import { Link as RouterLink, useLocation } from "react-router-dom";

import { getDashboardIcon } from "./dashboardIconMap";
import type { DashboardManifestEntry } from "../../types/dashboard";

type DashboardSidebarItemProps = {
  entry: DashboardManifestEntry;
};

export function DashboardSidebarItem({ entry }: DashboardSidebarItemProps) {
  const location = useLocation();
  const Icon = getDashboardIcon(entry.icon);
  const isActive =
    entry.enabled &&
    (location.pathname === entry.route || location.pathname.startsWith(`${entry.route}/`));

  const content = (
    <ListItemButton
      component={entry.enabled ? RouterLink : "div"}
      to={entry.enabled ? entry.route : undefined}
      selected={isActive}
      disabled={!entry.enabled}
      sx={{
        alignItems: "flex-start",
        borderRadius: 2,
        px: 1.25,
        py: 1,
        opacity: entry.enabled ? 1 : 0.7,
      }}
    >
      <ListItemIcon sx={{ minWidth: 40, mt: 0.25 }}>
        <Icon color={isActive ? "primary" : "inherit"} fontSize="small" />
      </ListItemIcon>
      <ListItemText
        primary={
          <Box sx={{ display: "flex", alignItems: "center", gap: 1, minWidth: 0 }}>
            <Typography variant="body2" fontWeight={isActive ? 800 : 700} noWrap>
              {entry.name}
            </Typography>
            {!entry.enabled ? (
              <Chip
                label="Em breve"
                size="small"
                variant="outlined"
                sx={{ height: 22, fontWeight: 700 }}
              />
            ) : null}
          </Box>
        }
        secondary={
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{
              mt: 0.5,
              display: "block",
              whiteSpace: "normal",
            }}
          >
            {entry.description}
          </Typography>
        }
      />
      {entry.enabled ? <ChevronRightRoundedIcon color={isActive ? "primary" : "inherit"} /> : null}
    </ListItemButton>
  );

  if (!entry.enabled) {
    return (
      <Tooltip title="Em breve" placement="right">
        <Box component="span">{content}</Box>
      </Tooltip>
    );
  }

  return content;
}
