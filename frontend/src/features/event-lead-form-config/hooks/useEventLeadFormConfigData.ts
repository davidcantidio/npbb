import { useCallback, useEffect, useRef, useState } from "react";
import {
  getEvento,
  getEventoFormConfig,
  getFormularioCamposPossiveis,
  listFormularioTemplates,
  updateEvento,
  updateEventoFormConfig,
  type EventoFormConfig,
  type FormularioTemplate,
} from "../../../services/eventos";
import { useCamposState } from "./useCamposState";

export type LandingMeta = {
  template_override: string;
  cta_personalizado: string;
  descricao_curta: string;
};

export function useEventLeadFormConfigData(
  token: string | null,
  eventoId: number,
  options: {
    onSaveSuccess?: () => void;
    showSuccess: (message: string) => void;
    showError: (message: string) => void;
  },
) {
  const { onSaveSuccess, showSuccess, showError } = options;

  const [config, setConfig] = useState<EventoFormConfig | null>(null);
  const [camposPossiveis, setCamposPossiveis] = useState<string[]>([]);
  const [templates, setTemplates] = useState<FormularioTemplate[]>([]);
  const [templateId, setTemplateId] = useState<number | null>(null);
  const [landingMeta, setLandingMeta] = useState<LandingMeta>({
    template_override: "",
    cta_personalizado: "",
    descricao_curta: "",
  });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const camposState = useCamposState(camposPossiveis);
  const syncFromConfigRef = useRef(camposState.syncFromConfig);
  syncFromConfigRef.current = camposState.syncFromConfig;

  const load = useCallback(async () => {
    if (!token || !Number.isFinite(eventoId)) return;
    setLoading(true);
    setError(null);
    try {
      const [configRes, templatesRes, camposRes, eventoRes] = await Promise.all([
        getEventoFormConfig(token, eventoId),
        listFormularioTemplates(token).catch(() => []),
        getFormularioCamposPossiveis(token),
        getEvento(token, eventoId),
      ]);
      setConfig(configRes);
      setTemplates(templatesRes);
      setCamposPossiveis(camposRes);
      setTemplateId(configRes.template_id ?? null);
      setLandingMeta({
        template_override: eventoRes.template_override ?? "",
        cta_personalizado: eventoRes.cta_personalizado ?? "",
        descricao_curta: eventoRes.descricao_curta ?? "",
      });
      syncFromConfigRef.current(configRes.campos, camposRes);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Erro ao carregar configuração do formulário";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [token, eventoId]);

  useEffect(() => {
    load();
  }, [load]);

  const handleSave = useCallback(
    async (afterSave?: () => void | Promise<void>) => {
      if (!token || !Number.isFinite(eventoId)) return;

      setSaving(true);
      try {
        const updated = await updateEventoFormConfig(token, eventoId, {
          template_id: templateId ?? null,
          campos: camposState.camposPayload,
        });
        const updatedEvento = await updateEvento(token, eventoId, {
          template_override: landingMeta.template_override.trim() || null,
          cta_personalizado: landingMeta.cta_personalizado.trim() || null,
          descricao_curta: landingMeta.descricao_curta.trim() || null,
        });

        setConfig(updated);
        setTemplateId(updated.template_id ?? null);
        setLandingMeta({
          template_override: updatedEvento.template_override ?? "",
          cta_personalizado: updatedEvento.cta_personalizado ?? "",
          descricao_curta: updatedEvento.descricao_curta ?? "",
        });
        camposState.syncFromConfig(updated.campos, camposPossiveis);

        showSuccess("Configuração salva com sucesso.");
        onSaveSuccess?.();
        void afterSave?.();
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : "Erro ao salvar configuração.";
        showError(message);
      } finally {
        setSaving(false);
      }
    },
    [
      camposPossiveis,
      camposState.camposPayload,
      camposState.syncFromConfig,
      eventoId,
      landingMeta,
      onSaveSuccess,
      showError,
      showSuccess,
      templateId,
      token,
    ],
  );

  return {
    config,
    templates,
    templateId,
    setTemplateId,
    landingMeta,
    setLandingMeta,
    camposPossiveis,
    loading,
    saving,
    error,
    camposState,
    handleSave,
  };
}
