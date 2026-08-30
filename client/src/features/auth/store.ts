import { create } from 'zustand';

import type { components } from '@/api/schema';

type User = components['schemas']['UserRead'];

type AuthStatus = 'unknown' | 'authenticated' | 'anonymous';

interface AuthState {
  status: AuthStatus;
  user: User | null;
  setAuthenticated: (user: User) => void;
  setAnonymous: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  status: 'unknown',
  user: null,
  setAuthenticated: (user) => {
    set({ status: 'authenticated', user });
  },
  setAnonymous: () => {
    set({ status: 'anonymous', user: null });
  },
}));

/** Non-reactive read for router guards, which run outside the React tree. */
export function isAuthenticated(): boolean {
  return useAuthStore.getState().status === 'authenticated';
}

/** Non-reactive read for router guards, which run outside the React tree. */
export function isAdmin(): boolean {
  return useAuthStore.getState().user?.role === 'admin';
}
