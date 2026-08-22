import { createFileRoute, redirect } from '@tanstack/react-router';

import { isAppError } from '@/api/errors';
import { sitesQueryOptions } from '@/features/sites/api';

export const Route = createFileRoute('/_authenticated/')({
  beforeLoad: async ({ context, location }) => {
    let sites;
    try {
      sites = await context.queryClient.ensureQueryData(sitesQueryOptions());
    } catch (error) {
      // The store can still report authenticated after a refresh token expires;
      // the failed request is the first hard proof the session is gone.
      if (isAppError(error) && error.status === 401) {
        throw redirect({ to: '/login', search: { redirect: location.href } });
      }
      throw error;
    }

    if (sites.length === 0) {
      throw redirect({ to: '/sites' });
    }
    throw redirect({
      to: '/sites/$siteId/dashboard',
      params: { siteId: sites[0].id },
    });
  },
});
