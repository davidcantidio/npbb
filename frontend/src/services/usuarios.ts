import { API_BASE_URL } from "./http";

export type UsuarioTipo = "bb" | "npbb" | "agencia";

export type UsuarioRead = {
  id: number;
  email: string;
  tipo_usuario: UsuarioTipo;
  funcionario_id?: number | null;
  agencia_id?: number | null;
};

export type Diretoria = {
  id: number;
  nome: string;
};

export type UsuarioCreate = {
  email: string;
  password: string;
  tipo_usuario: UsuarioTipo;
  matricula?: string;
  agencia_id?: number;
  diretoria_id?: number;
};

export type ApiErrorDetail =
  | string
  | {
      code?: string;
      message?: string;
      field?: string;
    };

export class ApiError extends Error {
  status: number;
  detail: ApiErrorDetail | null;

  constructor(status: number, detail: ApiErrorDetail | null) {
    const message =
      typeof detail === "string"
        ? detail
        : typeof detail?.message === "string"
          ? detail.message
          : "Erro na requisicao";
    super(message);
    this.status = status;
    this.detail = detail;
  }
}

async function parseJsonSafe(text: string) {
  try {
    return text ? JSON.parse(text) : null;
  } catch {
    return null;
  }
}

export async function createUsuario(payload: UsuarioCreate): Promise<UsuarioRead> {
  const res = await fetch(`${API_BASE_URL}/usuarios/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const text = await res.text();
  const data = await parseJsonSafe(text);

  if (!res.ok) {
    const detail = (data as any)?.detail ?? res.statusText;
    throw new ApiError(res.status, detail);
  }

  return data as UsuarioRead;
}

export async function listDiretoriasPublic(): Promise<Diretoria[]> {
  const res = await fetch(`${API_BASE_URL}/usuarios/diretorias`);
  const text = await res.text();
  const data = await parseJsonSafe(text);
  if (!res.ok) {
    const detail = (data as any)?.detail ?? res.statusText;
    throw new ApiError(res.status, detail);
  }
  return data as Diretoria[];
}

export async function updatePerfil(
  token: string,
  payload: { matricula: string; diretoria_id: number },
): Promise<UsuarioRead> {
  const res = await fetch(`${API_BASE_URL}/usuarios/me`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  });

  const text = await res.text();
  const data = await parseJsonSafe(text);
  if (!res.ok) {
    const detail = (data as any)?.detail ?? res.statusText;
    throw new ApiError(res.status, detail);
  }
  return data as UsuarioRead;
}

export async function setDiretoriaForUser(
  token: string,
  diretoria_id: number,
): Promise<UsuarioRead> {
  const res = await fetch(`${API_BASE_URL}/usuarios/diretoria`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify({ diretoria_id }),
  });

  const text = await res.text();
  const data = await parseJsonSafe(text);
  if (!res.ok) {
    const detail = (data as any)?.detail ?? res.statusText;
    throw new ApiError(res.status, detail);
  }
  return data as UsuarioRead;
}

export type ForgotPasswordResponse = {
  message: string;
  token?: string | null;
  expires_at?: string | null;
  reset_url?: string | null;
};

export async function forgotPassword(email: string): Promise<ForgotPasswordResponse> {
  const res = await fetch(`${API_BASE_URL}/usuarios/forgot-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });

  const text = await res.text();
  const data = await parseJsonSafe(text);

  if (!res.ok) {
    const detail = (data as any)?.detail ?? res.statusText;
    throw new ApiError(res.status, detail);
  }

  return data as ForgotPasswordResponse;
}

export type ResetPasswordResponse = {
  message: string;
};

export async function resetPassword(token: string, password: string): Promise<ResetPasswordResponse> {
  const res = await fetch(`${API_BASE_URL}/usuarios/reset-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, password }),
  });

  const text = await res.text();
  const data = await parseJsonSafe(text);

  if (!res.ok) {
    const detail = (data as any)?.detail ?? res.statusText;
    throw new ApiError(res.status, detail);
  }

  return data as ResetPasswordResponse;
}
