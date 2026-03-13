import {
  Alert,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  InputAdornment,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";

import AtivacaoQrPreview from "../../../components/eventos/AtivacaoQrPreview";
import type { Ativacao } from "../../../services/eventos";

export type AtivacaoViewDialogProps = {
  open: boolean;
  ativacao: Ativacao | null;
  gamificacaoNameById: Map<number, string>;
  onClose: () => void;
  onCopy: (text: string | null | undefined, label: string) => void;
};

export function AtivacaoViewDialog({
  open,
  ativacao,
  gamificacaoNameById,
  onClose,
  onCopy,
}: AtivacaoViewDialogProps) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Visualizar ativacao</DialogTitle>
      <DialogContent>
        {ativacao ? (
          <Stack spacing={1}>
            <Typography variant="body2">
              <strong>Nome:</strong> {ativacao.nome}
            </Typography>
            <Typography variant="body2">
              <strong>Descricao:</strong> {ativacao.descricao || "-"}
            </Typography>
            <Typography variant="body2">
              <strong>Mensagem QR Code:</strong> {ativacao.mensagem_qrcode || "-"}
            </Typography>
            <Typography variant="body2">
              <strong>Gamificacao:</strong>{" "}
              {ativacao.gamificacao_id
                ? gamificacaoNameById.get(ativacao.gamificacao_id) ?? `#${ativacao.gamificacao_id}`
                : "Nenhuma"}
            </Typography>
            <Typography variant="body2">
              <strong>Tipo de conversao:</strong> {ativacao.checkin_unico ? "Unica" : "Multipla"}
            </Typography>
            <Typography variant="body2">
              <strong>Redireciona pesquisa:</strong> {ativacao.redireciona_pesquisa ? "Sim" : "Nao"}
            </Typography>
            <Typography variant="body2">
              <strong>Termo de uso:</strong> {ativacao.termo_uso ? "Sim" : "Nao"}
            </Typography>
            <Typography variant="body2">
              <strong>Gera cupom:</strong> {ativacao.gera_cupom ? "Sim" : "Nao"}
            </Typography>
            <Alert severity="info" variant="outlined">
              Para quem nao consegue ler QR Code, o promotor pode digitar ou compartilhar a URL abaixo.
            </Alert>
            <TextField
              label="Landing publica"
              value={ativacao.landing_url || ""}
              fullWidth
              InputProps={{
                readOnly: true,
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      edge="end"
                      aria-label="Copiar landing publica"
                      onClick={() => onCopy(ativacao.landing_url, "Landing publica")}
                    >
                      <ContentCopyIcon fontSize="small" />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            <TextField
              label="URL alternativa do promotor"
              value={ativacao.url_promotor || ""}
              fullWidth
              InputProps={{
                readOnly: true,
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      edge="end"
                      aria-label="Copiar URL alternativa do promotor"
                      onClick={() => onCopy(ativacao.url_promotor, "URL alternativa do promotor")}
                    >
                      <ContentCopyIcon fontSize="small" />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            <AtivacaoQrPreview
              ativacaoId={ativacao.id}
              nome={ativacao.nome}
              qrCodeUrl={ativacao.qr_code_url}
            />
          </Stack>
        ) : null}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Fechar</Button>
      </DialogActions>
    </Dialog>
  );
}
