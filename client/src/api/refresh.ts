import { setAccessToken } from './token-store';

interface RefreshResponse {
  accessToken: string;
}

let inFlight: Promise<boolean> | null = null;

async function performRefresh(): Promise<boolean> {
  try {
    const response = await fetch('/api/v1/auth/refresh', {
      method: 'POST',
      credentials: 'include',
    });
    if (!response.ok) {
      setAccessToken(null);
      return false;
    }
    const data = (await response.json()) as RefreshResponse;
    setAccessToken(data.accessToken);
    return true;
  } catch {
    setAccessToken(null);
    return false;
  }
}

/**
 * Refreshes the access token. Concurrent callers share one request: the backend
 * rotates the refresh token on every call, so parallel refreshes would consume
 * each other's cookie and log the user out.
 *
 * Uses plain fetch rather than the API client to avoid recursing through the
 * 401 interceptor.
 */
export function refreshAccessToken(): Promise<boolean> {
  inFlight ??= performRefresh().finally(() => {
    inFlight = null;
  });
  return inFlight;
}
