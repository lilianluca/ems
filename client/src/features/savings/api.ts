import { queryOptions, useQuery } from '@tanstack/react-query';

import { api } from '@/api/client';
import { AppError } from '@/api/errors';
import type { components } from '@/api/schema';

export type DailySavings = components['schemas']['DailySavings'];

export const savingsKeys = {
  all: ['savings'] as const,
  today: (siteId: number) => [...savingsKeys.all, siteId, 'today'] as const,
};

/**
 * Today's savings from the steps the battery has already carried out. Without
 * bounds the endpoint answers for today, as one row, or none before the first
 * step is recorded.
 */
export function todaySavingsQueryOptions(siteId: number) {
  return queryOptions({
    queryKey: savingsKeys.today(siteId),
    queryFn: async ({ signal }) => {
      const { data, error, response } = await api.GET('/api/v1/sites/{site_id}/savings', {
        params: { path: { site_id: siteId } },
        signal,
      });
      if (error) throw new AppError(response.status, error);
      return data[0] ?? null;
    },
    // A step is recorded every quarter-hour.
    staleTime: 15 * 60_000,
    refetchInterval: 15 * 60_000,
  });
}

export function useTodaySavings(siteId: number) {
  return useQuery(todaySavingsQueryOptions(siteId));
}
