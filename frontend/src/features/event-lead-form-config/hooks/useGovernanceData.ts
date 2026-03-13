import { useCallback, useEffect, useState } from "react";
import {
  getLandingAnalytics,
  getLandingCustomizationAudit,
  type LandingAnalyticsSummary,
  type LandingCustomizationAuditItem,
} from "../../../services/eventos";

export function useGovernanceData(token: string | null, eventoId: number) {
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [analyticsData, setAnalyticsData] = useState<LandingAnalyticsSummary[]>([]);
  const [auditLoading, setAuditLoading] = useState(false);
  const [auditItems, setAuditItems] = useState<LandingCustomizationAuditItem[]>([]);

  const loadGovernanceData = useCallback(async () => {
    if (!token || !Number.isFinite(eventoId)) return;
    setAnalyticsLoading(true);
    setAuditLoading(true);
    try {
      const [analyticsRes, auditRes] = await Promise.all([
        getLandingAnalytics(token, eventoId).catch(() => []),
        getLandingCustomizationAudit(token, eventoId).catch(() => []),
      ]);
      setAnalyticsData(analyticsRes);
      setAuditItems(auditRes);
    } finally {
      setAnalyticsLoading(false);
      setAuditLoading(false);
    }
  }, [token, eventoId]);

  useEffect(() => {
    void loadGovernanceData();
  }, [loadGovernanceData]);

  return {
    analyticsData,
    analyticsLoading,
    auditItems,
    auditLoading,
    loadGovernanceData,
  };
}
