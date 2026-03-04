const rawApiBaseUrl = typeof import.meta.env.VITE_API_BASE_URL === "string"
  ? import.meta.env.VITE_API_BASE_URL.trim()
  : "";

/** Base URL for all backend requests in frontend services. */
export const API_BASE_URL = (rawApiBaseUrl || "/api").replace(/\/+$/, "");

const DEFAULT_TIMEOUT_MS = 20_000;
const DEFAULT_RETRY_DELAY_MS = 400;
const RETRYABLE_STATUS = new Set([408, 425, 429, 500, 502, 503, 504]);

export type ApiErrorDetail = string | Record<string, unknown> | Array<unknown> | null;

/** Normalized API error with transport and payload metadata. */
export class ApiError extends Error {
  readonly status: number;
  readonly detail: ApiErrorDetail;
  readonly code: string | null;
  readonly method: string;
  readonly url: string;
  readonly body: unknown;

  constructor(params: {
    message: string;
    status: number;
    detail?: ApiErrorDetail;
    code?: string | null;
    method: string;
    url: string;
    body?: unknown;
  }) {
    super(params.message);
    this.name = "ApiError";
    this.status = params.status;
    this.detail = params.detail ?? null;
    this.code = params.code ?? null;
    this.method = params.method;
    this.url = params.url;
    this.body = params.body ?? null;
  }
}

export type RequestOptions = RequestInit & {
  token?: string | null;
  timeoutMs?: number;
  retries?: number;
  retryDelayMs?: number;
  baseUrl?: string;
};

function wait(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function normalizeUrl(pathOrUrl: string, baseUrl?: string) {
  if (/^https?:\/\//i.test(pathOrUrl)) return pathOrUrl;
  const base = (baseUrl || API_BASE_URL).replace(/\/+$/, "");
  const path = pathOrUrl.startsWith("/") ? pathOrUrl : `/${pathOrUrl}`;
  return `${base}${path}`;
}

function toHeaderRecord(headers?: HeadersInit, token?: string | null): Record<string, string> {
  const record: Record<string, string> = {};

  if (headers instanceof Headers) {
    headers.forEach((value, key) => {
      record[key] = value;
    });
  } else if (Array.isArray(headers)) {
    for (const [key, value] of headers) {
      record[key] = String(value);
    }
  } else if (headers && typeof headers === "object") {
    Object.entries(headers).forEach(([key, value]) => {
      if (typeof value === "undefined") return;
      record[key] = String(value);
    });
  }

  if (token && !record.Authorization && !record.authorization) {
    record.Authorization = `Bearer ${token}`;
  }
  return record;
}

async function parseBodySafe(res: Response): Promise<unknown> {
  if (res.status === 204) return null;
  const hasHeaderGetter = typeof (res as any)?.headers?.get === "function";
  const contentType = hasHeaderGetter ? (res as any).headers.get("content-type") || "" : "";
  if (contentType.includes("application/json")) {
    try {
      return await res.json();
    } catch {
      return null;
    }
  }
  if (!contentType && typeof (res as any)?.json === "function") {
    try {
      return await (res as any).json();
    } catch {
      // fallback para text()
    }
  }
  try {
    const text = typeof (res as any)?.text === "function" ? await (res as any).text() : "";
    if (!text) return null;
    const trimmed = String(text).trim();
    if (
      (trimmed.startsWith("{") && trimmed.endsWith("}")) ||
      (trimmed.startsWith("[") && trimmed.endsWith("]"))
    ) {
      try {
        return JSON.parse(trimmed);
      } catch {
        // fallback para texto puro
      }
    }
    return text;
  } catch {
    return null;
  }
}

function extractErrorDetail(body: unknown, fallback: string): ApiErrorDetail {
  if (!body) return fallback;
  if (typeof body === "string") return body;
  if (typeof body === "object") {
    const detail = (body as any).detail;
    if (typeof detail === "string" || Array.isArray(detail) || (detail && typeof detail === "object")) {
      return detail as ApiErrorDetail;
    }
    return body as Record<string, unknown>;
  }
  return fallback;
}

function extractErrorCode(body: unknown, detail: ApiErrorDetail): string | null {
  if (body && typeof body === "object" && typeof (body as any).code === "string") {
    return (body as any).code;
  }
  if (detail && typeof detail === "object" && !Array.isArray(detail) && typeof (detail as any).code === "string") {
    return (detail as any).code;
  }
  return null;
}

function detailToMessage(detail: ApiErrorDetail, fallback: string) {
  if (typeof detail === "string" && detail.trim()) return detail;
  if (detail && typeof detail === "object" && !Array.isArray(detail)) {
    const message = (detail as any).message;
    if (typeof message === "string" && message.trim()) return message;
  }
  if (Array.isArray(detail) && detail.length > 0) {
    return "Requisicao invalida.";
  }
  return fallback;
}

function isRetryableNetworkError(error: unknown) {
  if (!(error instanceof Error)) return false;
  if (error.name === "AbortError") return true;
  return error.message === "Failed to fetch";
}

function shouldRetry(method: string, status: number | null, error: unknown, attempt: number, maxRetries: number) {
  if (method !== "GET") return false;
  if (attempt >= maxRetries) return false;
  if (typeof status === "number") return RETRYABLE_STATUS.has(status);
  return isRetryableNetworkError(error);
}

/** Executes `fetch` with timeout and external abort signal support. */
export async function fetchWithTimeout(input: string, init: RequestInit, timeoutMs = DEFAULT_TIMEOUT_MS) {
  const controller = new AbortController();
  const signal = init.signal;
  const onAbort = () => controller.abort();
  if (signal) {
    if (signal.aborted) controller.abort();
    else signal.addEventListener("abort", onAbort, { once: true });
  }

  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(input, { ...init, signal: controller.signal });
  } finally {
    clearTimeout(timeout);
    if (signal) signal.removeEventListener("abort", onAbort);
  }
}

/**
 * Executes HTTP requests with auth header, timeout and retry policy for idempotent requests.
 */
export async function fetchWithAuth(pathOrUrl: string, options: RequestOptions = {}): Promise<Response> {
  const {
    token,
    timeoutMs = DEFAULT_TIMEOUT_MS,
    retries,
    retryDelayMs = DEFAULT_RETRY_DELAY_MS,
    baseUrl,
    headers,
    method,
    ...rest
  } = options;
  const url = normalizeUrl(pathOrUrl, baseUrl);
  const resolvedMethod = (method || "GET").toUpperCase();
  const maxRetries = typeof retries === "number" ? retries : resolvedMethod === "GET" ? 1 : 0;
  const mergedHeaders = toHeaderRecord(headers, token);

  let lastError: unknown = null;
  for (let attempt = 0; attempt <= maxRetries; attempt += 1) {
    try {
      const response = await fetchWithTimeout(
        url,
        {
          ...rest,
          method: resolvedMethod,
          headers: mergedHeaders,
          credentials: rest.credentials ?? "include",
        },
        timeoutMs,
      );

      if (response.ok) return response;

      const body = await parseBodySafe(response);
      const detail = extractErrorDetail(body, response.statusText || "Erro na requisicao");
      const code = extractErrorCode(body, detail);
      const message = detailToMessage(detail, `Erro HTTP ${response.status}`);
      const apiError = new ApiError({
        message,
        status: response.status,
        detail,
        code,
        method: resolvedMethod,
        url,
        body,
      });
      lastError = apiError;

      if (shouldRetry(resolvedMethod, response.status, null, attempt, maxRetries)) {
        await wait(retryDelayMs);
        continue;
      }
      throw apiError;
    } catch (error) {
      if (error instanceof ApiError) throw error;
      lastError = error;

      if (shouldRetry(resolvedMethod, null, error, attempt, maxRetries)) {
        await wait(retryDelayMs);
        continue;
      }

      const timeoutMessage = error instanceof Error && error.name === "AbortError";
      throw new ApiError({
        message: timeoutMessage ? "Tempo limite da requisicao excedido." : "Falha de rede ao comunicar com a API.",
        status: 0,
        detail: timeoutMessage ? "TIMEOUT" : "NETWORK_ERROR",
        code: timeoutMessage ? "TIMEOUT" : "NETWORK_ERROR",
        method: resolvedMethod,
        url,
        body: null,
      });
    }
  }

  if (lastError instanceof ApiError) throw lastError;
  throw new ApiError({
    message: "Falha ao realizar requisicao.",
    status: 0,
    detail: "NETWORK_ERROR",
    code: "NETWORK_ERROR",
    method: resolvedMethod,
    url,
    body: null,
  });
}

/** Parses successful API responses and returns typed payload. */
export async function handleApiResponse<T>(res: Response): Promise<T> {
  if (res.status === 204) return undefined as T;
  const body = await parseBodySafe(res);
  return body as T;
}

/** Converts unknown errors into user-facing API messages. */
export function toApiErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof ApiError) {
    return detailToMessage(error.detail, error.message || fallback);
  }
  if (error instanceof Error && error.message.trim()) return error.message;
  return fallback;
}

/** Extracts normalized API error code when available. */
export function toApiErrorCode(error: unknown): string | null {
  if (error instanceof ApiError) return error.code;
  return null;
}
