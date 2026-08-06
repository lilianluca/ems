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
    onSuccess: (user) => {
      useAuthStore.getState().setAuthenticated(user);
      // Guards read context outside React, so the router must re-evaluate them.
      void router.invalidate();
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
    onSettled: () => {
      setAccessToken(null);
      useAuthStore.getState().setAnonymous();
      // Clears cached data so it cannot leak to the next user on this device.
      queryClient.clear();
      void router.invalidate();
    },
  });
}
