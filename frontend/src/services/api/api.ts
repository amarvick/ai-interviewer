export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const fallback = `Request failed with status ${response.status}`;
    try {
      const errorPayload = (await response.json()) as { detail?: string };
      throw new Error(errorPayload.detail ?? fallback);
    } catch {
      throw new Error(fallback);
    }
  }

  return (await response.json()) as T;
}
