import { useMemo } from "react";
import { Box, Divider, List, ListSubheader, Stack, Typography } from "@mui/material";

import { DashboardSidebarItem } from "./DashboardSidebarItem";
import type { DashboardManifestEntry } from "../../types/dashboard";

type DashboardSidebarProps = {
  entries: DashboardManifestEntry[];
};

type DashboardSidebarSection = {
  domain: string;
  title: string;
  entries: DashboardManifestEntry[];
};

const DOMAIN_TITLES: Record<string, string> = {
  leads: "Leads",
  eventos: "Eventos",
  publicidade: "Publicidade",
};

function getSectionTitle(domain: string) {
  return DOMAIN_TITLES[domain] ?? `${domain.slice(0, 1).toUpperCase()}${domain.slice(1)}`;
}

function buildSections(entries: DashboardManifestEntry[]): DashboardSidebarSection[] {
  const grouped = new Map<string, DashboardManifestEntry[]>();

  for (const entry of entries) {
    const current = grouped.get(entry.domain) ?? [];
    current.push(entry);
    grouped.set(entry.domain, current);
  }

  return Array.from(grouped.entries()).map(([domain, domainEntries]) => ({
    domain,
    title: getSectionTitle(domain),
    entries: domainEntries,
  }));
}

export function DashboardSidebar({ entries }: DashboardSidebarProps) {
  const sections = useMemo(() => buildSections(entries), [entries]);

  return (
    <Box component="nav" aria-label="Navegacao do dashboard">
      <Stack spacing={2.5}>
        <Box>
          <Typography variant="subtitle2" fontWeight={900} letterSpacing={0.2}>
            Painel de analises
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Navegacao orientada por manifesto.
          </Typography>
        </Box>

        {sections.map((section, index) => (
          <Box key={section.domain}>
            {index > 0 ? <Divider sx={{ mb: 2 }} /> : null}
            <List
              disablePadding
              subheader={
                <ListSubheader
                  disableGutters
                  sx={{
                    bgcolor: "transparent",
                    color: "text.secondary",
                    fontSize: 11,
                    fontWeight: 700,
                    letterSpacing: 0.8,
                    lineHeight: 1.6,
                    mb: 0.5,
                    px: 1.25,
                    textTransform: "uppercase",
                  }}
                >
                  {section.title}
                </ListSubheader>
              }
              sx={{ display: "grid", gap: 0.5, bgcolor: "transparent" }}
            >
              {section.entries.map((entry) => (
                <DashboardSidebarItem key={entry.id} entry={entry} />
              ))}
            </List>
          </Box>
        ))}
      </Stack>
    </Box>
  );
}
