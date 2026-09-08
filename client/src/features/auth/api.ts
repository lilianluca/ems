import { useMutation, useQueryClient } from '@tanstack/react-query';

import { api } from '@/api/client';
import { AppError } from '@/api/errors';
import { setAccessToken } from '@/api/token-store';
import { router } from '@/router';

import { useAuthStore } from './store';

export interface LoginCredentials {
  email: string;
  password: string;
}

export function useLogin() {
  return useMutation({
    mutationFn: async (credentials: LoginCredentials) => {
      const login = await api.POST('/api/v1/auth/login', { body: credentials });
      if (login.error) throw new AppError(login.response.status, login.error);

      setAccessToken(login.data.accessToken);

      const me = await api.GET('/api/v1/auth/me');
      if (me.error) throw new AppError(me.response.status, me.error);
      return me.data;
    },
    // No `router.invalidate()` here: the caller navigates away from the login
    // page, and that navigation already runs the guards against the store
    // written below. Doing both starts two competing load passes, and the
    // abandoned one cancels its in-flight queries as its matches unmount —
    // a `CancelledError` the loader awaiting them surfaces as a route error.
    onSuccess: (user) => {
      useAuthStore.getState().setAuthenticated(user);
    },
  });
}

export function useLogout() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      await api.POST('/api/v1/auth/logout');
    },
    // onSettled, not onSuccess: a failed request must still log the user out
    // locally rather than trapping them in the application.
    onSettled: async () => {
      setAccessToken(null);
      useAuthStore.getState().setAnonymous();
      try {
        // Redirect before clearing: the guard sends the router to /login and
        // tears the authenticated routes down, so the clear below cannot cancel
        // a query some loader is still awaiting.
        await router.invalidate();
      } finally {
        // Clears cached data so it cannot leak to the next user on this device.
        queryClient.clear();
      }
    },
  });
}
