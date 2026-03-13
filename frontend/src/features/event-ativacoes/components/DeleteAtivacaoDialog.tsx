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

import type { Ativacao } from "../../../services/eventos";

export type DeleteAtivacaoDialogProps = {
  open: boolean;
  ativacao: Ativacao | null;
  deleting: boolean;
  deleteError: string | null;
  onClose: () => void;
  onConfirm: () => void;
  hasToken: boolean;
};

export function DeleteAtivacaoDialog({
  open,
  ativacao,
  deleting,
  deleteError,
  onClose,
  onConfirm,
  hasToken,
}: DeleteAtivacaoDialogProps) {
  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Excluir ativacao</DialogTitle>
      <DialogContent>
        {deleteError && (
          <Alert severity="error" variant="filled" sx={{ mb: 2 }}>
            {deleteError}
          </Alert>
        )}
        <DialogContentText>
          {ativacao
            ? `Tem certeza que deseja excluir a ativacao "${ativacao.nome}"?`
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
          disabled={!hasToken || deleting || !ativacao}
          onClick={onConfirm}
          sx={{ fontWeight: 800 }}
        >
          {deleting ? <CircularProgress size={22} color="inherit" /> : "Excluir"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
