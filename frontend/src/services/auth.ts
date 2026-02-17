const AUTH_TOKEN_KEY = "ai_interviewer_token";
const AUTH_CHANGED_EVENT = "auth-changed";

export function getAuthToken(): string | null {
  return localStorage.getItem(AUTH_TOKEN_KEY);
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
