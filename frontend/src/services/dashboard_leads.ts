const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export type DashboardLeadsReportResponse = {
  version: number;
  generated_at: string;
  filters: {
    data_inicio: string | null;
    data_fim: string | null;
    evento_id: number | null;
    evento_nome: string | null;
  };
  big_numbers: {
    total_leads: number;
    total_compras: number;
    total_publico: number;
    taxa_conversao: number;
    criterio_publico: string;
    criterio_compras: string;
  };
  perfil_publico: {
    distribuicao_idade: { faixa: string; total: number; percentual: number }[];
    distribuicao_genero: { faixa: string; total: number; percentual: number }[];
    percent_sem_idade: number;
    percent_sem_genero: number;
  };
  clientes_bb: {
    total_clientes_bb: number;
    percentual_clientes_bb: number;
    criterio_usado: string;
  };
  pre_venda: {
    janela_pre_venda: string | null;
    volume_pre_venda: number;
    volume_venda_geral: number;
    observacao: string | null;
  };
  redes: {
    status: "sem_dados" | "ok";
    observacao: string | null;
    metricas: Record<string, number> | null;
  };
  dados_faltantes: string[];
};

async function handleResponse<T>(res: Response): Promise<T> {
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) {
    const detail = (data as any)?.detail ?? res.statusText;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return data as T;
}

export async function getDashboardLeadsReport(
  token: string,
  params: {
    evento_id?: number;
    evento_nome?: string;
    data_inicio?: string;
    data_fim?: string;
  },
): Promise<DashboardLeadsReportResponse> {
  const qs = new URLSearchParams();
  if (params.evento_id) qs.set("evento_id", String(params.evento_id));
  if (params.evento_nome) qs.set("evento_nome", params.evento_nome);
  if (params.data_inicio) qs.set("data_inicio", params.data_inicio);
  if (params.data_fim) qs.set("data_fim", params.data_fim);
  const url = `${API_BASE_URL}/dashboard/leads/relatorio${qs.toString() ? `?${qs}` : ""}`;
  const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
  return handleResponse<DashboardLeadsReportResponse>(res);
}
