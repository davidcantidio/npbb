import { handleDeleteResponse, handleResponse, requestWithAuth } from "./http";

export type QuestionarioOpcao = {
  id?: number;
  ordem: number;
  texto: string;
};

export type QuestionarioPergunta = {
  id?: number;
  ordem: number;
  tipo: string;
  texto: string;
  obrigatoria: boolean;
  opcoes: QuestionarioOpcao[];
};

export type QuestionarioPagina = {
  id?: number;
  ordem: number;
  titulo: string;
  descricao?: string | null;
  perguntas: QuestionarioPergunta[];
};

export type QuestionarioEstrutura = {
  evento_id?: number;
  paginas: QuestionarioPagina[];
};

export type UpdateEventoQuestionarioPayload = {
  paginas: QuestionarioPagina[];
};

export type Gamificacao = {
  id: number;
  evento_id: number;
  nome: string;
  descricao: string;
  premio: string;
  titulo_feedback: string;
  texto_feedback: string;
};

export type CreateEventoGamificacaoPayload = {
  nome: string;
  descricao: string;
  premio: string;
  titulo_feedback: string;
  texto_feedback: string;
};

export type UpdateGamificacaoPayload = {
  nome?: string;
  descricao?: string;
  premio?: string;
  titulo_feedback?: string;
  texto_feedback?: string;
};

export type Ativacao = {
  id: number;
  evento_id: number;
  nome: string;
  descricao?: string | null;
  mensagem_qrcode?: string | null;
  gamificacao_id?: number | null;
  landing_url?: string | null;
  qr_code_url?: string | null;
  url_promotor?: string | null;
  redireciona_pesquisa: boolean;
  checkin_unico: boolean;
  termo_uso: boolean;
  gera_cupom: boolean;
  created_at: string;
  updated_at: string;
};

export type CreateEventoAtivacaoPayload = {
  nome: string;
  descricao?: string | null;
  mensagem_qrcode?: string | null;
  gamificacao_id?: number | null;
  redireciona_pesquisa?: boolean;
  checkin_unico?: boolean;
  termo_uso?: boolean;
  gera_cupom?: boolean;
};

export type UpdateAtivacaoPayload = {
  nome?: string;
  descricao?: string | null;
  mensagem_qrcode?: string | null;
  gamificacao_id?: number | null;
  redireciona_pesquisa?: boolean;
  checkin_unico?: boolean;
  termo_uso?: boolean;
  gera_cupom?: boolean;
};

/**
 * Fetches questionnaire structure for an event.
 * @param token Auth token.
 * @param eventoId Event id.
 * @returns Current questionnaire structure.
 */
export async function getEventoQuestionario(
  token: string,
  eventoId: number,
): Promise<QuestionarioEstrutura> {
  const res = await requestWithAuth(`/evento/${eventoId}/questionario`, { token });
  return handleResponse<QuestionarioEstrutura>(res);
}

/**
 * Updates event questionnaire structure.
 * @param token Auth token.
 * @param eventoId Event id.
 * @param payload Questionnaire payload.
 * @returns Updated questionnaire structure.
 */
export async function updateEventoQuestionario(
  token: string,
  eventoId: number,
  payload: UpdateEventoQuestionarioPayload,
): Promise<QuestionarioEstrutura> {
  const res = await requestWithAuth(`/evento/${eventoId}/questionario`, {
    token,
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<QuestionarioEstrutura>(res);
}

/**
 * Lists gamificacoes for an event.
 * @param token Auth token.
 * @param eventoId Event id.
 * @returns Gamificacao list.
 */
export async function listEventoGamificacoes(token: string, eventoId: number): Promise<Gamificacao[]> {
  const res = await requestWithAuth(`/evento/${eventoId}/gamificacoes`, { token });
  return handleResponse<Gamificacao[]>(res);
}

/**
 * Creates a new gamificacao for an event.
 * @param token Auth token.
 * @param eventoId Event id.
 * @param payload Gamificacao payload.
 * @returns Created gamificacao.
 */
export async function createEventoGamificacao(
  token: string,
  eventoId: number,
  payload: CreateEventoGamificacaoPayload,
): Promise<Gamificacao> {
  const res = await requestWithAuth(`/evento/${eventoId}/gamificacoes`, {
    token,
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<Gamificacao>(res);
}

/**
 * Updates an existing gamificacao.
 * @param token Auth token.
 * @param gamificacaoId Gamificacao id.
 * @param payload Partial update payload.
 * @returns Updated gamificacao.
 */
export async function updateGamificacao(
  token: string,
  gamificacaoId: number,
  payload: UpdateGamificacaoPayload,
): Promise<Gamificacao> {
  const res = await requestWithAuth(`/gamificacao/${gamificacaoId}`, {
    token,
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<Gamificacao>(res);
}

/**
 * Deletes a gamificacao.
 * @param token Auth token.
 * @param gamificacaoId Gamificacao id.
 */
export async function deleteGamificacao(token: string, gamificacaoId: number): Promise<void> {
  const res = await requestWithAuth(`/gamificacao/${gamificacaoId}`, {
    token,
    method: "DELETE",
  });
  await handleDeleteResponse(res);
}

/**
 * Lists ativacoes for an event.
 * @param token Auth token.
 * @param eventoId Event id.
 * @returns Ativacao list.
 */
export async function listEventoAtivacoes(token: string, eventoId: number): Promise<Ativacao[]> {
  const res = await requestWithAuth(`/evento/${eventoId}/ativacoes`, { token });
  return handleResponse<Ativacao[]>(res);
}

/**
 * Creates a new ativacao for an event.
 * @param token Auth token.
 * @param eventoId Event id.
 * @param payload Ativacao payload.
 * @returns Created ativacao.
 */
export async function createEventoAtivacao(
  token: string,
  eventoId: number,
  payload: CreateEventoAtivacaoPayload,
): Promise<Ativacao> {
  const res = await requestWithAuth(`/evento/${eventoId}/ativacoes`, {
    token,
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<Ativacao>(res);
}

/**
 * Updates an existing ativacao.
 * @param token Auth token.
 * @param ativacaoId Ativacao id.
 * @param payload Partial update payload.
 * @returns Updated ativacao.
 */
export async function updateAtivacao(
  token: string,
  ativacaoId: number,
  payload: UpdateAtivacaoPayload,
): Promise<Ativacao> {
  const res = await requestWithAuth(`/ativacao/${ativacaoId}`, {
    token,
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<Ativacao>(res);
}

/**
 * Deletes an ativacao.
 * @param token Auth token.
 * @param ativacaoId Ativacao id.
 */
export async function deleteAtivacao(token: string, ativacaoId: number): Promise<void> {
  const res = await requestWithAuth(`/ativacao/${ativacaoId}`, {
    token,
    method: "DELETE",
  });
  await handleDeleteResponse(res);
}
