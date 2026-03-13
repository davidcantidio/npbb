import { useState } from "react";
import DownloadOutlinedIcon from "@mui/icons-material/DownloadOutlined";
import QrCode2OutlinedIcon from "@mui/icons-material/QrCode2Outlined";
import { Alert, Box, Button, CircularProgress, Stack, Typography } from "@mui/material";

export const QR_PLACEHOLDER_MESSAGE = "QR ainda nao disponivel para esta ativacao.";
export const QR_DOWNLOAD_ERROR_MESSAGE = "Nao foi possivel baixar o QR agora. Tente novamente.";

type AtivacaoQrPreviewProps = {
  ativacaoId: number;
  nome: string;
  qrCodeUrl?: string | null;
};

export function inferQrFileExtension(blobType: string | null | undefined, qrCodeUrl: string): "svg" | "png" {
  const normalizedType = String(blobType || "").toLowerCase();
  const normalizedUrl = qrCodeUrl.toLowerCase();

  if (normalizedType.includes("svg") || normalizedUrl.startsWith("data:image/svg+xml") || normalizedUrl.includes(".svg")) {
    return "svg";
  }

  return "png";
}

export function buildQrDownloadFilename(ativacaoId: number, extension: "svg" | "png"): string {
  return `ativacao-${ativacaoId}-qr.${extension}`;
}

export default function AtivacaoQrPreview({ ativacaoId, nome, qrCodeUrl }: AtivacaoQrPreviewProps) {
  const [downloading, setDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  const handleDownload = async () => {
    if (!qrCodeUrl || downloading) return;

    setDownloading(true);
    setDownloadError(null);

    try {
      const response = await fetch(qrCodeUrl);
      if (!response.ok) {
        throw new Error(`download_failed_${response.status}`);
      }

      const blob = await response.blob();
      const extension = inferQrFileExtension(blob.type, qrCodeUrl);
      const objectUrl = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = objectUrl;
      anchor.download = buildQrDownloadFilename(ativacaoId, extension);
      document.body.appendChild(anchor);
      anchor.click();
      document.body.removeChild(anchor);
      URL.revokeObjectURL(objectUrl);
    } catch {
      setDownloadError(QR_DOWNLOAD_ERROR_MESSAGE);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <Stack spacing={1.5}>
      <Stack direction={{ xs: "column", sm: "row" }} spacing={1} justifyContent="space-between" alignItems={{ xs: "flex-start", sm: "center" }}>
        <Typography variant="body2" sx={{ fontWeight: 700 }}>
          QR Code da ativacao
        </Typography>
        <Button
          variant="outlined"
          size="small"
          startIcon={
            downloading ? <CircularProgress size={16} color="inherit" /> : <DownloadOutlinedIcon fontSize="small" />
          }
          onClick={handleDownload}
          disabled={!qrCodeUrl || downloading}
          sx={{ textTransform: "none", fontWeight: 700 }}
        >
          {downloading ? "Baixando..." : "Baixar QR"}
        </Button>
      </Stack>

      {downloadError ? (
        <Alert severity="error" variant="outlined">
          {downloadError}
        </Alert>
      ) : null}

      {qrCodeUrl ? (
        <Box
          component="img"
          src={qrCodeUrl}
          alt={`QR Code da ativacao ${nome}`}
          data-testid="ativacao-qr-image"
          sx={{
            width: 180,
            height: 180,
            borderRadius: 2,
            border: "1px solid",
            borderColor: "divider",
            bgcolor: "common.white",
            p: 1,
          }}
        />
      ) : (
        <Alert severity="info" variant="outlined" icon={<QrCode2OutlinedIcon fontSize="inherit" />} data-testid="ativacao-qr-placeholder">
          {QR_PLACEHOLDER_MESSAGE}
        </Alert>
      )}

      <Typography variant="caption" color="text.secondary">
        O download preserva automaticamente o formato do QR quando o arquivo estiver disponivel.
      </Typography>
    </Stack>
  );
}
