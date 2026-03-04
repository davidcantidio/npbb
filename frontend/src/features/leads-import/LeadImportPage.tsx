import { Box, Paper, Stack, Tab, Tabs, Typography } from "@mui/material";
import { useCallback, useState } from "react";
import { useAuth } from "../../store/auth";
import { LeadListTable } from "./components/LeadListTable";
import { LeadImportEtlTab } from "./containers/LeadImportEtlTab";
import { LeadImportLegacyTab } from "./containers/LeadImportLegacyTab";
import { useLeadsTable } from "./hooks/useLeadsTable";

/**
 * Page container for assisted lead import and lead listing.
 */
export default function LeadImportPage() {
  const { token } = useAuth();
  const [activeTab, setActiveTab] = useState<"legacy" | "etl">("legacy");

  const {
    leads,
    leadsTotal,
    leadsPage,
    setLeadsPage,
    leadsPageSize,
    setLeadsPageSize,
    leadsLoading,
    leadsError,
    refresh,
  } = useLeadsTable(token);

  const handleResetLeadsPage = useCallback(() => {
    setLeadsPage(1);
  }, [setLeadsPage]);

  return (
    <Box sx={{ width: "100%" }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
        <Box>
          <Typography variant="h4" fontWeight={800}>
            Leads
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Importacao e gestao de leads
          </Typography>
        </Box>
      </Stack>

      <Paper elevation={1} sx={{ p: { xs: 2, md: 3 }, borderRadius: 3 }}>
        <Tabs value={activeTab} onChange={(_, value) => setActiveTab(value)} sx={{ mb: 3 }}>
          <Tab value="legacy" label="Importacao" />
          <Tab value="etl" label="Importacao avancada" />
        </Tabs>

        {activeTab === "legacy" ? (
          <LeadImportLegacyTab
            token={token}
            onImportSuccess={refresh}
            onResetLeadsPage={handleResetLeadsPage}
          />
        ) : null}
        {activeTab === "etl" ? <LeadImportEtlTab token={token} /> : null}
      </Paper>

      <Paper elevation={1} sx={{ mt: 3, borderRadius: 3, overflow: "hidden" }}>
        <LeadListTable
          leads={leads}
          leadsTotal={leadsTotal}
          leadsLoading={leadsLoading}
          leadsError={leadsError}
          leadsPage={leadsPage}
          leadsPageSize={leadsPageSize}
          onPageChange={setLeadsPage}
          onRowsPerPageChange={(pageSize) => {
            setLeadsPageSize(pageSize);
            setLeadsPage(1);
          }}
          onRefresh={refresh}
        />
      </Paper>
    </Box>
  );
}
