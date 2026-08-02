import { createRouter } from '@tanstack/react-router';

import { queryClient } from '@/api/query-client';

import { routeTree } from './routeTree.gen';

export const router = createRouter({
  routeTree,
  context: {
    queryClient,
    // Placeholder until the auth store exists.
    isAuthenticated: () => true,
  },
  defaultPreload: 'intent',
  scrollRestoration: true,
});

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}
