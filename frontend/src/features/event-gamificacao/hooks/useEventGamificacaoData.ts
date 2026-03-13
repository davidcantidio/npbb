import { useCallback, useEffect, useState } from "react";
import {
  createEventoGamificacao,
  deleteGamificacao,
  getEvento,
  listEventoGamificacoes,
  updateGamificacao,
  type CreateEventoGamificacaoPayload,
  type EventoRead,
  type Gamificacao,
} from "../../../services/eventos";
import { getEventApiErrorCode, getEventApiErrorMessage } from "../../../services/http_event_messages";

export type CreateForm = CreateEventoGamificacaoPayload;

export const EMPTY_FORM: CreateForm = {
  nome: "",
  descricao: "",
  premio: "",
  titulo_feedback: "",
  texto_feedback: "",
};

export const MAX_LEN = {
  nome: 150,
  descricao: 240,
  premio: 200,
  titulo_feedback: 200,
  texto_feedback: 240,
} as const;

function normalizeText(value: string) {
  return String(value || "").trim();
}

export type UseEventGamificacaoDataOptions = {
  showSuccess: (message: string) => void;
  showError: (message: string) => void;
};

export function useEventGamificacaoData(
  token: string | null,
  eventoId: number,
  options: UseEventGamificacaoDataOptions,
) {
  const { showSuccess, showError } = options;

  const isValidEventoId = Number.isFinite(eventoId) && eventoId > 0;

  const [evento, setEvento] = useState<EventoRead | null>(null);
  const [gamificacoes, setGamificacoes] = useState<Gamificacao[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [outOfScope, setOutOfScope] = useState(false);

  const [createAttempted, setCreateAttempted] = useState(false);
  const [createForm, setCreateForm] = useState<CreateForm>(EMPTY_FORM);
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const [editing, setEditing] = useState<Gamificacao | null>(null);
  const [saving, setSaving] = useState(false);

  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deletingTarget, setDeletingTarget] = useState<Gamificacao | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const canAct = Boolean(token) && isValidEventoId && !outOfScope;
  const isBusy = creating || saving || deleting;
  const isEditing = Boolean(editing);

  const cancelEdit = useCallback(() => {
    setEditing(null);
    setCreateAttempted(false);
    setCreateError(null);
    setCreateForm(EMPTY_FORM);
  }, []);

  const startEdit = useCallback((item: Gamificacao) => {
    setEditing(item);
    setCreateAttempted(false);
    setCreateError(null);
    setCreateForm({
      nome: item.nome,
      descricao: item.descricao,
      premio: item.premio,
      titulo_feedback: item.titulo_feedback,
      texto_feedback: item.texto_feedback,
    });
  }, []);

  const setCreateFormField = useCallback(<K extends keyof CreateForm>(key: K, value: CreateForm[K]) => {
    setCreateForm((prev) => ({ ...prev, [key]: value }));
    setCreateError(null);
  }, []);

  const handleSubmit = useCallback(async () => {
    if (!token || !isValidEventoId) return;

    setCreateAttempted(true);
    setCreateError(null);

    const nome = normalizeText(createForm.nome);
    const descricao = normalizeText(createForm.descricao);
    const premio = normalizeText(createForm.premio);
    const titulo = normalizeText(createForm.titulo_feedback);
    const texto = normalizeText(createForm.texto_feedback);

    if (!nome || !descricao || !premio || !titulo || !texto) {
      setCreateError("Preencha todos os campos obrigatórios.");
      return;
    }

    if (editing) {
      setSaving(true);
      try {
        const updated = await updateGamificacao(token, editing.id, {
          nome,
          descricao,
          premio,
          titulo_feedback: titulo,
          texto_feedback: texto,
        });
        setGamificacoes((prev) => prev.map((g) => (g.id === updated.id ? updated : g)));
        cancelEdit();
        showSuccess("Gamificação atualizada com sucesso.");
      } catch (err: unknown) {
        const message = getEventApiErrorMessage(err, "Erro ao atualizar gamificação.");
        setCreateError(message);
        showError(message);
      } finally {
        setSaving(false);
      }
      return;
    }

    setCreating(true);
    try {
      const created = await createEventoGamificacao(token, eventoId, {
        nome,
        descricao,
        premio,
        titulo_feedback: titulo,
        texto_feedback: texto,
      });
      setGamificacoes((prev) => [...prev, created].sort((a, b) => a.id - b.id));
      setCreateAttempted(false);
      setCreateForm(EMPTY_FORM);
      showSuccess("Gamificação adicionada com sucesso.");
    } catch (err: unknown) {
      const code = getEventApiErrorCode(err);
      if (code === "EVENTO_NOT_FOUND") setOutOfScope(true);
      const message = getEventApiErrorMessage(err, "Erro ao criar gamificação.");
      setCreateError(message);
      showError(message);
    } finally {
      setCreating(false);
    }
  }, [
    token,
    eventoId,
    isValidEventoId,
    createForm,
    editing,
    cancelEdit,
    showSuccess,
    showError,
  ]);

  const openDelete = useCallback((item: Gamificacao) => {
    setDeleteError(null);
    setDeletingTarget(item);
    setDeleteOpen(true);
  }, []);

  const closeDelete = useCallback(() => {
    if (!deleting) setDeleteOpen(false);
  }, [deleting]);

  const confirmDelete = useCallback(async () => {
    if (!token || !deletingTarget) return;
    setDeleting(true);
    setDeleteError(null);
    try {
      await deleteGamificacao(token, deletingTarget.id);
      setGamificacoes((prev) => prev.filter((g) => g.id !== deletingTarget.id));
      if (editing?.id === deletingTarget.id) cancelEdit();
      setDeleteOpen(false);
      setDeletingTarget(null);
      showSuccess("Gamificação excluída com sucesso.");
    } catch (err: unknown) {
      const message = getEventApiErrorMessage(err, "Erro ao excluir.");
      setDeleteError(message);
      showError(message);
    } finally {
      setDeleting(false);
    }
  }, [token, deletingTarget, editing?.id, cancelEdit, showSuccess, showError]);

  useEffect(() => {
    if (!token || !isValidEventoId) return;

    let cancelled = false;
    setLoading(true);
    setError(null);
    setOutOfScope(false);
    setEvento(null);
    setGamificacoes([]);

    Promise.all([getEvento(token, eventoId), listEventoGamificacoes(token, eventoId)])
      .then(([eventoRes, listRes]) => {
        if (cancelled) return;
        setEvento(eventoRes);
        setGamificacoes(listRes);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        const code = getEventApiErrorCode(err);
        if (code === "EVENTO_NOT_FOUND") setOutOfScope(true);
        setError(getEventApiErrorMessage(err, "Erro ao carregar gamificações."));
      })
      .finally(() => {
        if (cancelled) return;
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [token, eventoId, isValidEventoId]);

  return {
    evento,
    gamificacoes,
    loading,
    error,
    outOfScope,
    isValidEventoId,
    createForm,
    setCreateFormField,
    createAttempted,
    createError,
    creating,
    saving,
    editing,
    deleteOpen,
    deletingTarget,
    deleting,
    deleteError,
    canAct,
    isBusy,
    isEditing,
    cancelEdit,
    startEdit,
    handleSubmit,
    openDelete,
    closeDelete,
    confirmDelete,
  };
}
