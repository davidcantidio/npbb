import type { DashboardManifestEntry } from "../types/dashboard";

export const DASHBOARD_MANIFEST = [
  {
    id: "leads-age-analysis",
    route: "/dashboard/leads/analise-etaria",
    domain: "leads",
    name: "Analise etaria por evento",
    icon: "age-analysis",
    description: "Distribuicao de leads por faixa etaria com recorte por evento.",
    enabled: true,
  },
  {
    id: "events-closure-report",
    route: "/dashboard/eventos/fechamento",
    domain: "eventos",
    name: "Relatorio de fechamento",
    icon: "event-closure",
    description: "Indicadores consolidados para encerramento e leitura final do evento.",
    enabled: false,
  },
  {
    id: "leads-event-conversion",
    route: "/dashboard/leads/conversao",
    domain: "leads",
    name: "Conversao por evento",
    icon: "event-conversion",
    description: "Visao de conversao entre base de leads, publico e compras.",
    enabled: false,
  },
] satisfies DashboardManifestEntry[];
