import { API_BASE_URL } from "../http";

const EVENTOS_API_BASE_URL = API_BASE_URL;

function buildAuthHeaders(token: string, headers?: HeadersInit): HeadersInit {
  if (!headers) return { Authorization: `Bearer ${token}` };
  if (headers instanceof Headers) {
    const next = new Headers(headers);
    next.set("Authorization", `Bearer ${token}`);
    return next;
  }
  if (Array.isArray(headers)) {
    return [...headers, ["Authorization", `Bearer ${token}`]];
  }
  return { ...headers, Authorization: `Bearer ${token}` };
}

/**
 * Safely parses a JSON payload when the response body may be empty or malformed.
 * @param text Raw response text.
 * @returns Parsed payload or `null` when parsing fails.
 */
export async function parseJsonSafe(text: string): Promise<unknown> {
  try {
    return text ? JSON.parse(text) : null;
  } catch {
    return null;
  }
}

/**
 * Parses a backend response and throws an `Error` when the request fails.
 * @param res HTTP response from the API.
 * @returns Parsed JSON payload cast to `T`.
 * @throws Error when the response status is not successful.
 */
export async function handleResponse<T>(res: Response): Promise<T> {
  const text = await res.text();
  const data = await parseJsonSafe(text);

  if (!res.ok) {
    const detail = (data as { detail?: unknown } | null)?.detail ?? res.statusText;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }

  return data as T;
}

/**
 * Executes an authenticated request against evento endpoints.
 * @param path Relative API path beginning with `/`.
 * @param options Request options with auth token.
 * @returns Native `Response` from `fetch`.
 */
export async function requestWithAuth(
  path: string,
  options: Omit<RequestInit, "headers"> & { token: string; headers?: HeadersInit },
): Promise<Response> {
  const { token, headers, ...rest } = options;
  return fetch(`${EVENTOS_API_BASE_URL}${path}`, {
    ...rest,
    headers: buildAuthHeaders(token, headers),
  });
}

/**
 * Handles DELETE responses where backend may return `204` or an error payload.
 * @param res HTTP response from delete endpoint.
 * @throws Error when delete fails.
 */
export async function handleDeleteResponse(res: Response): Promise<void> {
  if (res.status === 204) return;
  await handleResponse<unknown>(res);
}

export { EVENTOS_API_BASE_URL };
