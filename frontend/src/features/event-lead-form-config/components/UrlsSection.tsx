import { Box, IconButton, InputAdornment, Stack, TextField, Typography } from "@mui/material";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import type { EventoFormConfigUrls } from "../../../services/eventos";

type UrlsSectionProps = {
  urls: EventoFormConfigUrls;
  onCopy: (text: string, label: string) => void | Promise<void>;
};

export function UrlsSection({ urls, onCopy }: UrlsSectionProps) {
  return (
    <Box sx={{ maxWidth: { xs: "100%", md: 480 } }}>
      <Typography variant="subtitle1" fontWeight={900} gutterBottom>
        URLs geradas
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
        Links publicos gerados pela API (somente leitura).
      </Typography>

      <Stack spacing={1}>
        <TextField
          label="Landing"
          value={urls.url_landing}
          fullWidth
          InputProps={{
            readOnly: true,
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  aria-label="Copiar URL da landing"
                  size="small"
                  onClick={() => onCopy(urls.url_landing, "Landing")}
                >
                  <ContentCopyIcon fontSize="small" />
                </IconButton>
              </InputAdornment>
            ),
          }}
        />
        <TextField
          label="Check-in sem QR"
          value={urls.url_checkin_sem_qr}
          fullWidth
          InputProps={{
            readOnly: true,
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  aria-label="Copiar URL do check-in sem QR"
                  size="small"
                  onClick={() => onCopy(urls.url_checkin_sem_qr, "Check-in sem QR")}
                >
                  <ContentCopyIcon fontSize="small" />
                </IconButton>
              </InputAdornment>
            ),
          }}
        />
        <TextField
          label="Question\u00e1rio"
          value={urls.url_questionario}
          fullWidth
          InputProps={{
            readOnly: true,
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  aria-label="Copiar URL do questionario"
                  size="small"
                  onClick={() => onCopy(urls.url_questionario, "Questionário")}
                >
                  <ContentCopyIcon fontSize="small" />
                </IconButton>
              </InputAdornment>
            ),
          }}
        />
        <TextField
          label="API"
          value={urls.url_api}
          fullWidth
          InputProps={{
            readOnly: true,
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  aria-label="Copiar URL da API"
                  size="small"
                  onClick={() => onCopy(urls.url_api, "API")}
                >
                  <ContentCopyIcon fontSize="small" />
                </IconButton>
              </InputAdornment>
            ),
          }}
        />
      </Stack>
    </Box>
  );
}
