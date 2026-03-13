import {
  Alert,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
} from "@mui/material";

import type { Gamificacao } from "../../../services/eventos";

export type DeleteGamificacaoDialogProps = {
  open: boolean;
  gamificacao: Gamificacao | null;
  deleting: boolean;
  deleteError: string | null;
  onClose: () => void;
  onConfirm: () => void;
  hasToken: boolean;
};

export function DeleteGamificacaoDialog({
  open,
  gamificacao,
  deleting,
  deleteError,
  onClose,
  onConfirm,
  hasToken,
}: DeleteGamificacaoDialogProps) {
  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Excluir gamificação</DialogTitle>
      <DialogContent>
        {deleteError && (
          <Alert severity="error" variant="filled" sx={{ mb: 2 }}>
            {deleteError}
          </Alert>
        )}
        <DialogContentText>
          {gamificacao
            ? `Tem certeza que deseja excluir a gamificação "${gamificacao.nome}"?`
            : "Tem certeza?"}
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={deleting}>
          Cancelar
        </Button>
        <Button
          color="error"
          variant="contained"
          disabled={!hasToken || deleting || !gamificacao}
          onClick={onConfirm}
          sx={{ fontWeight: 800 }}
        >
          {deleting ? <CircularProgress size={22} color="inherit" /> : "Excluir"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
