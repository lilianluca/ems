import { queryOptions, useQuery } from '@tanstack/react-query';

import { api } from '@/api/client';
import { AppError } from '@/api/errors';
import type { components } from '@/api/schema';

export type OptimizationPlan = components['schemas']['OptimizationPlan'];
export type OptimizationStep = components['schemas']['OptimizationStep'];

export const optimizationKeys = {
  all: ['optimization'] as const,
  site: (siteId: number) => [...optimizationKeys.all, siteId] as const,
};

/** Shared by the hook and route loaders, so both agree on caching. */
export function optimizationQueryOptions(siteId: number) {
  return queryOptions({
    queryKey: optimizationKeys.site(siteId),
    queryFn: async ({ signal }) => {
      const { data, error, response } = await api.GET('/api/v1/sites/{site_id}/optimization', {
        params: { path: { site_id: siteId } },
        signal,
      });
      if (error) throw new AppError(response.status, error);
      return data;
    },
    // The plan is recomputed per request and its horizon shortens by an hour as
    // the day passes, so it is refreshed on roughly that cadence.
    staleTime: 15 * 60_000,
    refetchInterval: 15 * 60_000,
    // A site without a battery or without forecasts answers 422 every time;
    // retrying would not change that.
    retry: false,
  });
}

export function useOptimizationPlan(siteId: number) {
  return useQuery(optimizationQueryOptions(siteId));
}
