import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Stack, Typography } from "@mui/material";
import type { LeadImportEtlResult } from "../../../services/leads_import";

type LeadImportEtlSummaryDialogProps = {
  open: boolean;
  onClose: () => void;
  result: LeadImportEtlResult | null;
};

/**
 * Displays ETL commit summary after a successful ETL import.
 */
export function LeadImportEtlSummaryDialog({ open, onClose, result }: LeadImportEtlSummaryDialogProps) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Importacao ETL concluida</DialogTitle>
      <DialogContent>
        <Stack spacing={1.2}>
          <Typography variant="body2" color="text.secondary">
            Sessao: {result?.session_token ?? "-"}
          </Typography>
          <Typography variant="body2">Total de linhas: {result?.total_rows ?? 0}</Typography>
          <Typography variant="body2">Validas: {result?.valid_rows ?? 0}</Typography>
          <Typography variant="body2">Invalidas: {result?.invalid_rows ?? 0}</Typography>
          <Typography variant="body2">Criadas: {result?.created ?? 0}</Typography>
          <Typography variant="body2">Atualizadas: {result?.updated ?? 0}</Typography>
          <Typography variant="body2">Ignoradas: {result?.skipped ?? 0}</Typography>
          <Typography variant="body2">Erros: {result?.errors ?? 0}</Typography>
          <Typography variant="body2" color="text.secondary">
            Status: {result?.status ?? "-"}
          </Typography>
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} sx={{ textTransform: "none", fontWeight: 700 }}>
          Fechar
        </Button>
      </DialogActions>
    </Dialog>
  );
}
