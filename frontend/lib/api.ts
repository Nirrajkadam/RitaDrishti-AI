/**
 * RitaDrishti-AI Frontend API Client
 * Centralized HTTP client managing authentication token persistence,
 * environment base URL configuration, and API methods.
 */

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

/**
 * Safely parses Base64URL JWT payload and validates token expiration timestamp.
 * Includes a 30-second clock skew tolerance buffer.
 */
export function isTokenExpired(token: string, clockSkewSeconds: number = 30): boolean {
  if (!token || typeof token !== "string") return true;

  try {
    const parts = token.split(".");
    if (parts.length !== 3) return true;

    const payloadBase64 = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(payloadBase64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );

    const parsed = JSON.parse(jsonPayload);
    if (!parsed || typeof parsed.exp !== "number") return true;

    const currentTime = Math.floor(Date.now() / 1000);
    return parsed.exp < currentTime + clockSkewSeconds;
  } catch (err) {
    return true;
  }
}

export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  const token = localStorage.getItem("ritadrishti_jwt_token");
  if (!token) return null;

  if (isTokenExpired(token)) {
    removeAuthToken();
    return null;
  }
  return token;
}

export function setAuthToken(token: string) {
  if (typeof window !== "undefined") {
    localStorage.setItem("ritadrishti_jwt_token", token);
  }
}

export function removeAuthToken() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("ritadrishti_jwt_token");
  }
}

export async function apiFetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    if (response.status === 401) {
      removeAuthToken();
      if (typeof window !== "undefined") {
        window.dispatchEvent(new CustomEvent("ritadrishti_unauthorized"));
      }
    }
    const errorMsg = data?.error?.message || data?.detail || `HTTP Error ${response.status}`;
    throw new Error(errorMsg);
  }

  return data as T;
}
