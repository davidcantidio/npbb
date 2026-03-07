import { useMemo } from "react";
import { Box, Divider, List, Stack, Typography } from "@mui/material";

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

function buildSections(entries: DashboardManifestEntry[]): DashboardSidebarSection[] {
  const grouped = new Map<string, DashboardManifestEntry[]>();

  for (const entry of entries) {
    const current = grouped.get(entry.domain) ?? [];
    current.push(entry);
    grouped.set(entry.domain, current);
  }

  return Array.from(grouped.entries()).map(([domain, domainEntries]) => ({
    domain,
    title: DOMAIN_TITLES[domain] ?? domain,
    entries: domainEntries,
  }));
}

export function DashboardSidebar({ entries }: DashboardSidebarProps) {
  const sections = useMemo(() => buildSections(entries), [entries]);

  return (
    <Stack spacing={2}>
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
          <Typography
            variant="overline"
            color="text.secondary"
            sx={{ display: "block", px: 1.25, mb: 0.5 }}
          >
            {section.title}
          </Typography>
          <List disablePadding sx={{ display: "grid", gap: 0.5 }}>
            {section.entries.map((entry) => (
              <DashboardSidebarItem key={entry.id} entry={entry} />
            ))}
          </List>
        </Box>
      ))}
    </Stack>
  );
}
