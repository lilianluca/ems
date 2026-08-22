import { api } from '@/api/client';
import { refreshAccessToken } from '@/api/refresh';

import { useAuthStore } from './store';

/**
 * Restores the session before the router mounts. Without this, guards would run
 * while status is still 'unknown' and briefly bounce a logged-in user to /login
 * on every page reload.
 */
export async function bootstrapAuth(): Promise<void> {
  const { setAuthenticated, setAnonymous } = useAuthStore.getState();

  if (!(await refreshAccessToken())) {
    setAnonymous();
    return;
  }

  const { data, error } = await api.GET('/api/v1/auth/me');
  if (error ?? !data) {
    setAnonymous();
    return;
  }
  setAuthenticated(data);
}
