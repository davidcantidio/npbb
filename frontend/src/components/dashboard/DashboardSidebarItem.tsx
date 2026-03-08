import ChevronRightRoundedIcon from "@mui/icons-material/ChevronRightRounded";
import { alpha } from "@mui/material/styles";
import {
  Box,
  Chip,
  ListItem,
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
    <ListItem disablePadding>
      <ListItemButton
        component={entry.enabled ? RouterLink : "div"}
        to={entry.enabled ? entry.route : undefined}
        selected={isActive}
        disabled={!entry.enabled}
        aria-current={isActive ? "page" : undefined}
        aria-disabled={!entry.enabled || undefined}
        sx={(theme) => ({
          alignItems: "flex-start",
          border: 1,
          borderColor: isActive ? theme.palette.primary.main : "transparent",
          borderRadius: 2.5,
          px: 1.25,
          py: 1.125,
          opacity: entry.enabled ? 1 : 0.64,
          transition: "background-color 120ms ease, border-color 120ms ease, opacity 120ms ease",
          ...(isActive
            ? {
                backgroundColor: alpha(theme.palette.primary.main, 0.08),
              }
            : null),
          "&:hover": {
            backgroundColor: entry.enabled
              ? alpha(theme.palette.primary.main, isActive ? 0.12 : 0.04)
              : "transparent",
          },
          "&.Mui-disabled": {
            color: theme.palette.text.secondary,
            opacity: 0.64,
          },
        })}
      >
        <ListItemIcon
          sx={{
            color: isActive ? "primary.main" : entry.enabled ? "text.secondary" : "action.disabled",
            minWidth: 40,
            mt: 0.25,
          }}
        >
          <Icon fontSize="small" />
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
        {entry.enabled ? (
          <ChevronRightRoundedIcon color={isActive ? "primary" : "inherit"} />
        ) : null}
      </ListItemButton>
    </ListItem>
  );

  if (!entry.enabled) {
    return (
      <Tooltip title="Em breve" placement="right" describeChild>
        <Box
          component="span"
          data-testid={`dashboard-sidebar-disabled-${entry.id}`}
          sx={{ display: "block" }}
        >
          {content}
        </Box>
      </Tooltip>
    );
  }

  return content;
}
