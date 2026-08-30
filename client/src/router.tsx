import { createRouter } from '@tanstack/react-router';

import { queryClient } from '@/api/query-client';
import { isAdmin, isAuthenticated } from '@/features/auth/store';

import { routeTree } from './routeTree.gen';

export const router = createRouter({
  routeTree,
  context: { queryClient, isAuthenticated, isAdmin },
  defaultPreload: 'intent',
  scrollRestoration: true,
});

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}
