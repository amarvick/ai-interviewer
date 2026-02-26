const AUTH_TOKEN_KEY = "ai_interviewer_token";
const AUTH_CHANGED_EVENT = "auth-changed";

function decodeBase64Url(value: string): string {
  const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
  const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, "=");
  return atob(padded);
}

function isTokenExpired(token: string): boolean {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) {
      return true;
    }
    const payloadText = decodeBase64Url(parts[1]);
    const payload = JSON.parse(payloadText) as { exp?: number };
    if (typeof payload.exp !== "number") {
      return true;
    }
    const nowSeconds = Math.floor(Date.now() / 1000);
    return payload.exp <= nowSeconds;
  } catch {
    return true;
  }
}

export function getAuthToken(): string | null {
  const token = localStorage.getItem(AUTH_TOKEN_KEY);
  if (!token) {
    return null;
  }
  if (isTokenExpired(token)) {
    clearAuthToken();
    return null;
  }
  return token;
}

export function setAuthToken(token: string): void {
  localStorage.setItem(AUTH_TOKEN_KEY, token);
  window.dispatchEvent(new Event(AUTH_CHANGED_EVENT));
}

export function clearAuthToken(): void {
  localStorage.removeItem(AUTH_TOKEN_KEY);
  window.dispatchEvent(new Event(AUTH_CHANGED_EVENT));
}

export function isAuthenticated(): boolean {
  return Boolean(getAuthToken());
}

export function onAuthChanged(listener: () => void): () => void {
  const onStorage = (event: StorageEvent) => {
    if (event.key === AUTH_TOKEN_KEY) {
      listener();
    }
  };

  window.addEventListener(AUTH_CHANGED_EVENT, listener);
  window.addEventListener("storage", onStorage);

  return () => {
    window.removeEventListener(AUTH_CHANGED_EVENT, listener);
    window.removeEventListener("storage", onStorage);
  };
}
