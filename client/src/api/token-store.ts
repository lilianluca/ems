// The access token lives in memory only. It is deliberately not persisted:
// localStorage is readable by any injected script, while the httpOnly refresh
// cookie already provides persistence across reloads.
let accessToken: string | null = null;

export function getAccessToken(): string | null {
  return accessToken;
}

export function setAccessToken(token: string | null): void {
  accessToken = token;
}
