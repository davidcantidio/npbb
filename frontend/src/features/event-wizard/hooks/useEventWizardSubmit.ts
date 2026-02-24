import { useCallback } from "react";
import { NavigateFunction } from "react-router-dom";
import { createEvento, createTag, EventoCreate, updateEvento } from "../../../services/eventos";
import { EventWizardFormState, normalizeWizardText, parseWizardId } from "./useEventWizardForm";

/**
 * Resolves if submit should navigate to the next workflow stage.
 * @param params Continue flags from UI interaction.
 * @returns `true` when wizard should navigate after save.
 */
export function resolveSubmitAndContinue(params: {
  clickedContinue: boolean;
  requestedContinue: boolean;
}): boolean {
  return params.clickedContinue || params.requestedContinue;
}

type SubmitParams = {
  token: string;
  isEdit: boolean;
  eventoId: number;
  canPickAgencia: boolean;
  form: EventWizardFormState;
  shouldContinue: boolean;
  navigate: NavigateFunction;
  onSaveSuccess: (message: string | null) => void;
};

/**
 * Handles create/update submission and navigation decisions for event wizard.
 * @returns A submit function that persists wizard state and navigates based on CTA intent.
 */
export function useEventWizardSubmit() {
  const submitEventWizard = useCallback(async (params: SubmitParams) => {
    const {
      token,
      isEdit,
      eventoId,
      canPickAgencia,
      form,
      shouldContinue,
      navigate,
      onSaveSuccess,
    } = params;

    let tagIds = form.tag_ids.map((id) => Number(id)).filter((id) => Number.isFinite(id) && id > 0);
    if (form.tag_names.length) {
      const createdTags = await Promise.all(form.tag_names.map((name) => createTag(token, name)));
      const createdIds = createdTags.map((tag) => tag.id).filter((id) => Number.isFinite(id) && id > 0);
      tagIds = Array.from(new Set([...tagIds, ...createdIds]));
    }

    const descricao = normalizeWizardText(form.descricao);
    const payload: EventoCreate = {
      nome: normalizeWizardText(form.nome),
      investimento: normalizeWizardText(form.investimento) || undefined,
      concorrencia: Boolean(form.concorrencia),
      cidade: normalizeWizardText(form.cidade),
      estado: normalizeWizardText(form.estado).toUpperCase(),
      divisao_demandante_id: parseWizardId(form.divisao_demandante_id) || undefined,
      data_inicio_prevista: form.data_inicio_prevista,
      data_fim_prevista: form.data_fim_prevista || undefined,
      tag_ids: tagIds,
      territorio_ids: form.territorio_ids
        .map((id) => Number(id))
        .filter((id) => Number.isFinite(id) && id > 0),
    };

    if (descricao) payload.descricao = descricao;

    const tipoId = parseWizardId(form.tipo_id);
    if (tipoId) payload.tipo_id = tipoId;

    const diretoriaId = parseWizardId(form.diretoria_id);
    if (diretoriaId) payload.diretoria_id = diretoriaId;

    const subtipoId = parseWizardId(form.subtipo_id);
    if (subtipoId) payload.subtipo_id = subtipoId;

    if (canPickAgencia) {
      const agenciaId = parseWizardId(form.agencia_id);
      if (agenciaId) payload.agencia_id = agenciaId;
    }

    if (isEdit) {
      const updated = await updateEvento(token, eventoId, payload);
      if (shouldContinue) {
        navigate(`/eventos/${updated.id}/formulario-lead`, { replace: true });
      } else {
        onSaveSuccess("Evento salvo com sucesso.");
      }
      return;
    }

    const created = await createEvento(token, payload);
    if (shouldContinue) {
      navigate(`/eventos/${created.id}/formulario-lead`, { replace: true });
    } else {
      navigate(`/eventos/${created.id}/editar`, { replace: true });
    }
  }, []);

  return { submitEventWizard };
}
