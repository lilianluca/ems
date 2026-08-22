import { queryOptions, useQuery } from '@tanstack/react-query';

import { api } from '@/api/client';
import { AppError } from '@/api/errors';
import type { components } from '@/api/schema';

export type Site = components['schemas']['SiteRead'];

export const siteKeys = {
  all: ['sites'] as const,
  list: () => [...siteKeys.all, 'list'] as const,
  detail: (siteId: number) => [...siteKeys.all, 'detail', siteId] as const,
};

/** Shared by the `useSites` hook and route loaders, so both agree on caching. */
export function sitesQueryOptions() {
  return queryOptions({
    queryKey: siteKeys.list(),
    queryFn: async ({ signal }) => {
      const { data, error, response } = await api.GET('/api/v1/sites', { signal });
      if (error) throw new AppError(response.status, error);
      return data;
    },
    // Site membership changes rarely; no need to refetch on every mount.
    staleTime: 10 * 60_000,
  });
}

export function useSites() {
  return useQuery(sitesQueryOptions());
}
