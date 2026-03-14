import {
  Alert,
  Box,
  CircularProgress,
  IconButton,
  Stack,
  Typography,
} from "@mui/material";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import LandingPageView from "../../../components/landing/LandingPageView";
import MobilePreviewFrame from "../../../components/landing/MobilePreviewFrame";
import type { LandingPageData } from "../../../services/landing_public";

type PreviewSectionProps = {
  previewData: LandingPageData | null;
  previewLoading: boolean;
  previewError: string | null;
};

export function PreviewSection({
  previewData,
  previewLoading,
  previewError,
}: PreviewSectionProps) {
  return (
    <Box>
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
        <Box sx={{ position: "relative" }}>
          {previewData.acesso.landing_url ? (
            <IconButton
              component="a"
              href={previewData.acesso.landing_url}
              target="_blank"
              rel="noreferrer"
              aria-label="Abrir landing pública"
              size="small"
              sx={{
                position: "absolute",
                top: 8,
                right: 8,
                zIndex: 1,
                backgroundColor: "background.paper",
                "&:hover": { backgroundColor: "action.hover" },
              }}
            >
              <OpenInNewIcon fontSize="small" />
            </IconButton>
          ) : null}
          <MobilePreviewFrame>
            <LandingPageView data={previewData} mode="preview" />
          </MobilePreviewFrame>
        </Box>
      ) : (
        <Typography variant="body2" color="text.secondary">
          Nenhum preview disponível no momento.
        </Typography>
      )}
    </Box>
  );
}
