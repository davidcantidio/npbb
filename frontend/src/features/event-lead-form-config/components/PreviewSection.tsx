import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Stack,
  Typography,
} from "@mui/material";
import LandingPageView from "../../../components/landing/LandingPageView";
import MobilePreviewFrame from "../../../components/landing/MobilePreviewFrame";
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
      <Box mb={1.5}>
        <Typography variant="subtitle1" fontWeight={900}>
          Preview da landing
        </Typography>
      </Box>

      <Stack
        data-testid="event-lead-preview-actions"
        direction={{ xs: "column", sm: "row" }}
        spacing={1}
        useFlexGap
        flexWrap="wrap"
        mb={1.5}
      >
        <Button
          variant="outlined"
          onClick={() => void onRefresh()}
          disabled={previewLoading}
          size="small"
          sx={{ textTransform: "none", whiteSpace: "nowrap", fontWeight: 700 }}
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
            size="small"
            sx={{ textTransform: "none", whiteSpace: "nowrap", fontWeight: 800 }}
          >
            Abrir landing publica
          </Button>
        ) : null}
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
        <MobilePreviewFrame>
          <LandingPageView data={previewData} mode="preview" />
        </MobilePreviewFrame>
      ) : (
        <Typography variant="body2" color="text.secondary">
          Nenhum preview disponível no momento.
        </Typography>
      )}
    </Box>
  );
}
