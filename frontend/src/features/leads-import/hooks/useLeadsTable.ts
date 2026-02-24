import { useCallback, useEffect, useState } from "react";
import { LeadListItem, listLeads } from "../../../services/leads_import";
import { toApiErrorMessage } from "../../../services/http";

/**
 * Manages paginated lead listing and refresh state.
 * @param token Auth token used by lead listing endpoint.
 * @returns Paginated lead list state plus pagination and refresh controls.
 */
export function useLeadsTable(token: string | null) {
  const [leads, setLeads] = useState<LeadListItem[]>([]);
  const [leadsTotal, setLeadsTotal] = useState(0);
  const [leadsPage, setLeadsPage] = useState(1);
  const [leadsPageSize, setLeadsPageSize] = useState(20);
  const [leadsLoading, setLeadsLoading] = useState(false);
  const [leadsError, setLeadsError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (!token) return;

    let cancelled = false;
    setLeadsLoading(true);
    setLeadsError(null);

    listLeads(token, { page: leadsPage, page_size: leadsPageSize })
      .then((data) => {
        if (cancelled) return;
        setLeads(data.items);
        setLeadsTotal(data.total);
      })
      .catch((err) => {
        if (cancelled) return;
        setLeadsError(toApiErrorMessage(err, "Erro ao carregar lista de leads."));
      })
      .finally(() => {
        if (cancelled) return;
        setLeadsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [token, leadsPage, leadsPageSize, reloadKey]);

  const refresh = useCallback(() => {
    setReloadKey((prev) => prev + 1);
  }, []);

  return {
    leads,
    leadsTotal,
    leadsPage,
    setLeadsPage,
    leadsPageSize,
    setLeadsPageSize,
    leadsLoading,
    leadsError,
    refresh,
  };
}
