import { useCallback, useEffect, useMemo, useState } from "react";
import {
  createEventoAtivacao,
  deleteAtivacao,
  getEvento,
  listEventoAtivacoes,
  listEventoGamificacoes,
  updateAtivacao,
  type Ativacao,
  type CreateEventoAtivacaoPayload,
  type EventoRead,
  type Gamificacao,
} from "../../../services/eventos";
import {
  getEventApiErrorCode,
  getEventApiErrorExtra,
  getEventApiErrorMessage,
} from "../../../services/http_event_messages";

export type CreateForm = {
  nome: string;
  mensagem_qrcode: string;
  descricao: string;
  gamificacao_id: number | null;
  redireciona_pesquisa: boolean;
  checkin_unico: boolean;
  termo_uso: boolean;
  gera_cupom: boolean;
};

export const EMPTY_CREATE_FORM: CreateForm = {
  nome: "",
  mensagem_qrcode: "",
  descricao: "",
  gamificacao_id: null,
  redireciona_pesquisa: false,
  checkin_unico: false,
  termo_uso: false,
  gera_cupom: false,
};

export const MAX_LEN = {
  nome: 100,
  mensagem_qrcode: 240,
  descricao: 240,
} as const;

function normalizeText(value: string) {
  return String(value || "").trim();
}

function normalizeOptionalText(value: string) {
  const trimmed = String(value || "").trim();
  return trimmed ? trimmed : null;
}

export type UseEventAtivacoesDataOptions = {
  showSuccess: (message: string) => void;
  showError: (message: string) => void;
};

export function useEventAtivacoesData(
  token: string | null,
  eventoId: number,
  options: UseEventAtivacoesDataOptions,
) {
  const { showSuccess, showError } = options;

  const isValidEventoId = Number.isFinite(eventoId) && eventoId > 0;

  const [evento, setEvento] = useState<EventoRead | null>(null);
  const [ativacoes, setAtivacoes] = useState<Ativacao[]>([]);
  const [gamificacoes, setGamificacoes] = useState<Gamificacao[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [outOfScope, setOutOfScope] = useState(false);

  const [createAttempted, setCreateAttempted] = useState(false);
  const [createForm, setCreateForm] = useState<CreateForm>(EMPTY_CREATE_FORM);
  const [creating, setCreating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const [editing, setEditing] = useState<Ativacao | null>(null);

  const [viewing, setViewing] = useState<Ativacao | null>(null);

  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deletingTarget, setDeletingTarget] = useState<Ativacao | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const gamificacaoNameById = useMemo(() => {
    const map = new Map<number, string>();
    for (const item of gamificacoes) {
      map.set(item.id, item.nome);
    }
    return map;
  }, [gamificacoes]);

  const canAct = Boolean(token) && isValidEventoId && !outOfScope;
  const isBusy = creating || saving || deleting;
  const formDisabled = !canAct || isBusy;
  const isEditing = Boolean(editing);

  const nomeNormalized = normalizeText(createForm.nome);
  const nomeRequiredError = createAttempted && !nomeNormalized;

  const resetForm = useCallback(() => {
    setCreateAttempted(false);
    setCreateError(null);
    setCreateForm(EMPTY_CREATE_FORM);
    setEditing(null);
  }, []);

  const startEdit = useCallback((item: Ativacao) => {
    setEditing(item);
    setCreateAttempted(false);
    setCreateError(null);
    setCreateForm({
      nome: item.nome,
      mensagem_qrcode: item.mensagem_qrcode ?? "",
      descricao: item.descricao ?? "",
      gamificacao_id: item.gamificacao_id ?? null,
      redireciona_pesquisa: item.redireciona_pesquisa,
      checkin_unico: item.checkin_unico,
      termo_uso: item.termo_uso,
      gera_cupom: item.gera_cupom,
    });
  }, []);

  const setCreateFormField = useCallback(<K extends keyof CreateForm>(key: K, value: CreateForm[K]) => {
    setCreateForm((prev) => ({ ...prev, [key]: value }));
    setCreateError(null);
  }, []);

  const buildPayload = useCallback((): CreateEventoAtivacaoPayload => ({
    nome: normalizeText(createForm.nome),
    descricao: normalizeOptionalText(createForm.descricao),
    mensagem_qrcode: normalizeOptionalText(createForm.mensagem_qrcode),
    gamificacao_id: createForm.gamificacao_id,
    redireciona_pesquisa: createForm.redireciona_pesquisa,
    checkin_unico: createForm.checkin_unico,
    termo_uso: createForm.termo_uso,
    gera_cupom: createForm.gera_cupom,
  }), [createForm]);

  const handleSubmit = useCallback(async () => {
    if (!token || !isValidEventoId) return;

    setCreateAttempted(true);
    setCreateError(null);
    if (!canAct) return;

    const payload = buildPayload();
    if (!payload.nome) {
      setCreateError("Informe o nome da ativacao.");
      return;
    }

    if (editing) {
      setSaving(true);
      try {
        const updated = await updateAtivacao(token, editing.id, payload);
        setAtivacoes((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
        setViewing((v) => (v?.id === updated.id ? updated : v));
        resetForm();
        showSuccess("Ativacao atualizada com sucesso.");
      } catch (err: unknown) {
        const message = getEventApiErrorMessage(err, "Erro ao atualizar ativacao.");
        setCreateError(message);
        showError(message);
      } finally {
        setSaving(false);
      }
      return;
    }

    setCreating(true);
    try {
      const created = await createEventoAtivacao(token, eventoId, payload);
      setAtivacoes((prev) => [...prev, created].sort((a, b) => a.id - b.id));
      resetForm();
      showSuccess("Ativacao adicionada com sucesso.");
    } catch (err: unknown) {
      const code = getEventApiErrorCode(err);
      if (code === "EVENTO_NOT_FOUND") setOutOfScope(true);
      const message = getEventApiErrorMessage(err, "Erro ao adicionar ativacao.");
      setCreateError(message);
      showError(message);
    } finally {
      setCreating(false);
    }
  }, [token, eventoId, isValidEventoId, canAct, editing, buildPayload, resetForm, showSuccess, showError]);

  const openDelete = useCallback((item: Ativacao) => {
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
      await deleteAtivacao(token, deletingTarget.id);
      setAtivacoes((prev) => prev.filter((a) => a.id !== deletingTarget.id));
      setViewing((v) => (v?.id === deletingTarget.id ? null : v));
      setDeleteOpen(false);
      setDeletingTarget(null);
      showSuccess("Ativacao excluida com sucesso.");
    } catch (err: unknown) {
      const code = getEventApiErrorCode(err);
      if (code === "ATIVACAO_DELETE_BLOCKED") {
        const extra = getEventApiErrorExtra(err);
        const deps = extra?.dependencies;
        if (deps && typeof deps === "object") {
          const items = Object.entries(deps)
            .filter(([, v]) => typeof v === "number" && v > 0)
            .map(([k, v]) => `${k}: ${v}`)
            .join(", ");
          const message = items
            ? `Nao e possivel excluir: existem vinculos (${items}).`
            : "Nao e possivel excluir: existem vinculos.";
          setDeleteError(message);
          showError(message);
          return;
        }
      }

      const message = getEventApiErrorMessage(err, "Erro ao excluir.");
      setDeleteError(message);
      showError(message);
    } finally {
      setDeleting(false);
    }
  }, [token, deletingTarget, showSuccess, showError]);

  useEffect(() => {
    if (!token || !isValidEventoId) return;

    let cancelled = false;
    setLoading(true);
    setError(null);
    setOutOfScope(false);
    setEvento(null);
    setAtivacoes([]);
    setGamificacoes([]);
    setCreateAttempted(false);
    setCreateError(null);
    setCreateForm(EMPTY_CREATE_FORM);
    setEditing(null);

    Promise.all([
      getEvento(token, eventoId),
      listEventoAtivacoes(token, eventoId),
      listEventoGamificacoes(token, eventoId),
    ])
      .then(([eventoRes, ativacoesRes, gamificacoesRes]) => {
        if (cancelled) return;
        setEvento(eventoRes);
        setAtivacoes(ativacoesRes);
        setGamificacoes(gamificacoesRes);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        const code = getEventApiErrorCode(err);
        if (code === "EVENTO_NOT_FOUND") setOutOfScope(true);
        setError(getEventApiErrorMessage(err, "Erro ao carregar ativacoes."));
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
    ativacoes,
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
    viewing,
    setViewing,
    deleteOpen,
    deletingTarget,
    deleting,
    deleteError,
    gamificacaoNameById,
    canAct,
    isBusy,
    formDisabled,
    isEditing,
    nomeRequiredError,
    resetForm,
    startEdit,
    handleSubmit,
    openDelete,
    closeDelete,
    confirmDelete,
  };
}
