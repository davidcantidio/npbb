import { useCallback, useEffect, useRef, useState } from "react";
import { previewEventoLanding, type LandingPageData, type PreviewEventoLandingPayload } from "../../../services/landing_public";
import { toApiErrorMessage } from "../../../services/http";

export function useLandingPreview(
  token: string | null,
  eventoId: number,
  previewPayload: PreviewEventoLandingPayload,
  configLoaded: boolean,
  loading: boolean,
) {
  const [previewData, setPreviewData] = useState<LandingPageData | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const hasLoadedInitialPreviewRef = useRef(false);
  const previewAbortControllerRef = useRef<AbortController | null>(null);
  const previewRequestVersionRef = useRef(0);

  const loadPreview = useCallback(async () => {
    if (!token || !Number.isFinite(eventoId)) return;

    previewAbortControllerRef.current?.abort();
    const controller = new AbortController();
    previewAbortControllerRef.current = controller;
    const requestVersion = previewRequestVersionRef.current + 1;
    previewRequestVersionRef.current = requestVersion;

    setPreviewLoading(true);
    setPreviewError(null);
    try {
      const response = await previewEventoLanding(token, eventoId, previewPayload, {
        signal: controller.signal,
      });
      if (controller.signal.aborted || requestVersion !== previewRequestVersionRef.current) return;
      setPreviewData(response);
      hasLoadedInitialPreviewRef.current = true;
    } catch (err) {
      if (controller.signal.aborted || requestVersion !== previewRequestVersionRef.current) return;
      setPreviewError(toApiErrorMessage(err, "Erro ao carregar preview da landing."));
    } finally {
      if (!controller.signal.aborted && requestVersion === previewRequestVersionRef.current) {
        setPreviewLoading(false);
      }
    }
  }, [eventoId, previewPayload, token]);

  const refreshPreview = useCallback(async () => {
    await loadPreview();
  }, [loadPreview]);

  useEffect(() => {
    if (loading || !configLoaded || !token || !Number.isFinite(eventoId)) return;

    const delayMs = hasLoadedInitialPreviewRef.current ? 250 : 0;
    const timer = window.setTimeout(() => {
      void loadPreview();
    }, delayMs);

    return () => window.clearTimeout(timer);
  }, [configLoaded, eventoId, loadPreview, loading, token]);

  useEffect(() => {
    return () => {
      previewAbortControllerRef.current?.abort();
    };
  }, []);

  return {
    previewData,
    previewLoading,
    previewError,
    loadPreview,
    refreshPreview,
  };
}
