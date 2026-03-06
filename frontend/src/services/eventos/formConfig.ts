import { handleResponse, requestWithAuth } from "./http";

export type FormularioTemplate = {
  id: number;
  nome: string;
};

export type FormularioCampo = {
  nome_campo: string;
  obrigatorio: boolean;
  ordem: number;
};

export type EventoFormConfigUrls = {
  url_landing: string;
  url_checkin_sem_qr: string;
  url_questionario: string;
  url_api: string;
};

export type EventoFormConfig = {
  evento_id: number;
  template_id: number | null;
  campos: FormularioCampo[];
  urls: EventoFormConfigUrls;
};

export type UpdateEventoFormConfigPayload = {
  template_id?: number | null;
  campos?: FormularioCampo[];
};

export const FORMULARIO_CAMPOS_POSSIVEIS_FALLBACK = [
  "Nome",
  "Email",
  "CPF",
  "Telefone",
  "Sobrenome",
  "Estado",
  "Data de nascimento",
  "Endereco",
  "Interesses",
  "Genero",
  "Area de atuacao",
] as const;

/**
 * Lists available form templates for event lead forms.
 * @param token Auth token.
 * @param search Optional template search query.
 * @returns Form template list.
 */
export async function listFormularioTemplates(
  token: string,
  search?: string,
): Promise<FormularioTemplate[]> {
  const qs = new URLSearchParams();
  if (search) qs.set("search", search);

  const res = await requestWithAuth(`/evento/all/formulario-templates${qs.toString() ? `?${qs}` : ""}`, {
    token,
  });
  return handleResponse<FormularioTemplate[]>(res);
}

/**
 * Fetches lead form configuration for a specific event.
 * @param token Auth token.
 * @param eventoId Event id.
 * @returns Form configuration.
 */
export async function getEventoFormConfig(token: string, eventoId: number): Promise<EventoFormConfig> {
  const res = await requestWithAuth(`/evento/${eventoId}/form-config`, { token });
  return handleResponse<EventoFormConfig>(res);
}

/**
 * Updates lead form configuration for an event.
 * @param token Auth token.
 * @param eventoId Event id.
 * @param payload Partial form config payload.
 * @returns Updated form configuration.
 */
export async function updateEventoFormConfig(
  token: string,
  eventoId: number,
  payload: UpdateEventoFormConfigPayload,
): Promise<EventoFormConfig> {
  const res = await requestWithAuth(`/evento/${eventoId}/form-config`, {
    token,
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<EventoFormConfig>(res);
}

/**
 * Lists allowed form field names for event lead forms.
 * @param token Auth token.
 * @returns Field names list.
 */
export async function listFormularioCampos(token: string): Promise<string[]> {
  const res = await requestWithAuth("/evento/all/formulario-campos", { token });
  return handleResponse<string[]>(res);
}

/**
 * Returns supported lead form field names with fallback when backend endpoint fails.
 * @param token Auth token.
 * @returns Allowed field names list.
 */
export async function getFormularioCamposPossiveis(token: string): Promise<string[]> {
  try {
    return await listFormularioCampos(token);
  } catch {
    return [...FORMULARIO_CAMPOS_POSSIVEIS_FALLBACK];
  }
}
