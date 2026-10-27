import { createRouter } from '@tanstack/react-router';
import type { ParseKeys } from 'i18next';
import type { ComponentType } from 'react';

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

  interface StaticDataRouteOption {
    /** Translation key of this route's crumb in the header breadcrumb. */
    breadcrumb?: ParseKeys;
    /** Page actions rendered on the right of the header; the deepest route's win. */
    headerActions?: ComponentType;
  }
}
