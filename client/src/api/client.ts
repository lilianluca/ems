import createClient from 'openapi-fetch';

import { refreshAccessToken } from './refresh';
import type { paths } from './schema';
import { getAccessToken, setAccessToken } from './token-store';

export const api = createClient<paths>({
  baseUrl: '/',
  credentials: 'include',
});

/** Endpoints that carry no access token and must not trigger a refresh loop. */
const PUBLIC_PATHS = new Set([
  '/api/v1/auth/login',
  '/api/v1/auth/register',
  '/api/v1/auth/refresh',
]);

// A Request body is a stream and can only be read once, so requests are cloned
// before being sent in case they need replaying after a refresh.
const replayable = new Map<string, Request>();

api.use({
  onRequest({ request, id, schemaPath }) {
    if (PUBLIC_PATHS.has(schemaPath)) return request;

    const token = getAccessToken();
    if (token) {
      request.headers.set('Authorization', `Bearer ${token}`);
    }
    replayable.set(id, request.clone());
    return request;
  },

  async onResponse({ response, id, schemaPath }) {
    const original = replayable.get(id);
    replayable.delete(id);

    if (response.status !== 401 || !original || PUBLIC_PATHS.has(schemaPath)) {
      return response;
    }

    const refreshed = await refreshAccessToken();
    if (!refreshed) {
      setAccessToken(null);
      return response;
    }

    original.headers.set('Authorization', `Bearer ${getAccessToken() ?? ''}`);
    return fetch(original);
  },

  onError({ id }) {
    replayable.delete(id);
  },
});
