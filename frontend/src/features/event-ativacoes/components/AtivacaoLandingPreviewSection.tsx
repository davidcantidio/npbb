import { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  IconButton,
  Stack,
  Typography,
} from "@mui/material";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";

import MobilePreviewFrame from "../../../components/landing/MobilePreviewFrame";
import LandingPageView from "../../../components/landing/LandingPageView";
import type { Ativacao } from "../../../services/eventos";
import {
  getLandingByAtivacao,
  type LandingPageData,
} from "../../../services/landing_public";

type AtivacaoLandingPreviewSectionProps = {
  ativacao: Ativacao | null;
};

function getPreviewErrorMessage(error: unknown) {
  if (error instanceof Error && error.message.trim()) {
    return error.message;
  }
  return "Erro ao carregar preview da landing.";
}

export function AtivacaoLandingPreviewSection({
  ativacao,
}: AtivacaoLandingPreviewSectionProps) {
  const [previewData, setPreviewData] = useState<LandingPageData | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const [refreshVersion, setRefreshVersion] = useState(0);

  useEffect(() => {
    if (!ativacao) {
      setPreviewData(null);
      setPreviewError(null);
      setPreviewLoading(false);
      return;
    }

    let cancelled = false;
    setPreviewData(null);
    setPreviewError(null);
    setPreviewLoading(true);

    getLandingByAtivacao(ativacao.id)
      .then((data) => {
        if (cancelled) return;
        setPreviewData(data);
      })
      .catch((error: unknown) => {
        if (cancelled) return;
        setPreviewError(getPreviewErrorMessage(error));
      })
      .finally(() => {
        if (cancelled) return;
        setPreviewLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [ativacao, refreshVersion]);

  return (
    <Box>
      <Box mb={1.5}>
        <Typography variant="subtitle1" fontWeight={900}>
          Preview da landing
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ maxWidth: { md: "34ch" } }}>
          {ativacao
            ? `O painel abaixo renderiza a landing publicada da ativação "${ativacao.nome}" em modo preview.`
            : "Selecione uma ativação na lista ou salve uma nova ativação para carregar o preview nesta coluna."}
        </Typography>
      </Box>

      <Stack
        data-testid="event-ativacoes-preview-actions"
        direction={{ xs: "column", sm: "row" }}
        spacing={1}
        useFlexGap
        flexWrap="wrap"
        mb={1.5}
      >
        <Button
          variant="outlined"
          onClick={() => setRefreshVersion((value) => value + 1)}
          disabled={!ativacao || previewLoading}
          size="small"
          sx={{ textTransform: "none", whiteSpace: "nowrap", fontWeight: 700 }}
        >
          {previewLoading ? <CircularProgress size={18} color="inherit" /> : "Atualizar preview"}
        </Button>
      </Stack>

      {previewError ? (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {previewError}
        </Alert>
      ) : null}

      {!ativacao ? (
        <Typography
          data-testid="event-ativacoes-preview-empty-state"
          variant="body2"
          color="text.secondary"
        >
          Nenhuma ativação em foco no momento.
        </Typography>
      ) : previewLoading && !previewData ? (
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
          <MobilePreviewFrame testId="event-ativacoes-preview-host">
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
