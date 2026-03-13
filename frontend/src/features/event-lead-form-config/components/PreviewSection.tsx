import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Stack,
  Typography,
} from "@mui/material";
import LandingPageView from "../../../components/landing/LandingPageView";
import type { LandingPageData } from "../../../services/landing_public";

type PreviewSectionProps = {
  previewData: LandingPageData | null;
  previewLoading: boolean;
  previewError: string | null;
  onRefresh: () => void | Promise<void>;
};

export function PreviewSection({
  previewData,
  previewLoading,
  previewError,
  onRefresh,
}: PreviewSectionProps) {
  return (
    <Box>
      <Stack
        direction={{ xs: "column", md: "row" }}
        justifyContent="space-between"
        alignItems={{ xs: "flex-start", md: "center" }}
        gap={1.5}
        mb={1.5}
      >
        <Box>
          <Typography variant="subtitle1" fontWeight={900}>
            Preview da landing
          </Typography>
          <Typography variant="body2" color="text.secondary">
            O painel abaixo renderiza a mesma landing form-only publicada,             com interacoes desabilitadas por estar em preview interno.
          </Typography>
        </Box>
        <Stack direction="row" spacing={1} flexWrap="wrap">
          <Button
            variant="outlined"
            onClick={() => void onRefresh()}
            disabled={previewLoading}
          >
            {previewLoading ? (
              <CircularProgress size={18} color="inherit" />
            ) : (
              "Atualizar preview"
            )}
          </Button>
          {previewData?.acesso.landing_url ? (
            <Button
              component="a"
              href={previewData.acesso.landing_url}
              target="_blank"
              rel="noreferrer"
              variant="contained"
            >
              Abrir landing publica
            </Button>
          ) : null}
        </Stack>
      </Stack>

      {previewError ? (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {previewError}
        </Alert>
      ) : null}

      {previewLoading && !previewData ? (
        <Stack direction="row" spacing={1} alignItems="center">
          <CircularProgress size={22} />
          <Typography variant="body2" color="text.secondary">
            Carregando preview...
          </Typography>
        </Stack>
      ) : previewData ? (
        <Box
          data-testid="event-lead-preview-host"
          sx={{
            mt: 1,
            position: "relative",
            isolation: "isolate",
            borderRadius: 4,
            overflow: "hidden",
            border: 1,
            borderColor: "divider",
          }}
        >
          <LandingPageView data={previewData} mode="preview" />
        </Box>
      ) : (
        <Typography variant="body2" color="text.secondary">
          Nenhum preview disponível no momento.
        </Typography>
      )}
    </Box>
  );
}
