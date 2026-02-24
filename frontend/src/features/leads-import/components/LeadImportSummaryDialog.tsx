import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Typography } from "@mui/material";

type LeadImportSummaryDialogProps = {
  open: boolean;
  onClose: () => void;
  result: {
    filename: string;
    created: number;
    updated: number;
    skipped: number;
  } | null;
};

/**
 * Displays lead import summary after a successful import.
 */
export function LeadImportSummaryDialog({ open, onClose, result }: LeadImportSummaryDialogProps) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle>Importacao concluida</DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Arquivo: {result?.filename}
        </Typography>
        <Typography variant="body2">Criados: {result?.created ?? 0}</Typography>
        <Typography variant="body2">Atualizados: {result?.updated ?? 0}</Typography>
        <Typography variant="body2">Ignorados: {result?.skipped ?? 0}</Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} sx={{ textTransform: "none", fontWeight: 700 }}>
          Fechar
        </Button>
      </DialogActions>
    </Dialog>
  );
}
