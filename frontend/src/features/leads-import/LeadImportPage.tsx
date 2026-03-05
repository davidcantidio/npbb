import { Box, Paper, Stack, Typography } from "@mui/material";
import { useCallback } from "react";
import { useAuth } from "../../store/auth";
import { LeadListTable } from "./components/LeadListTable";
import { ImportacaoBronzeStepper } from "./components/ImportacaoBronzeStepper";
import { useLeadsTable } from "./hooks/useLeadsTable";

/**
 * Unified lead import page — Bronze ingestion stepper + lead listing.
 * Replaces the previous dual-tab "Importacao / Importacao Avancada" layout.
 */
export default function LeadImportPage() {
  const { token } = useAuth();

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
        <Typography variant="h6" fontWeight={700} mb={3}>
          Importar arquivo
        </Typography>
        <ImportacaoBronzeStepper
          token={token}
          onBatchCreated={() => {
            handleResetLeadsPage();
            refresh();
          }}
        />
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
