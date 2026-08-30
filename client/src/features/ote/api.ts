import { queryOptions, useQuery } from '@tanstack/react-query';

import { api } from '@/api/client';
import { AppError } from '@/api/errors';
import type { components } from '@/api/schema';

export type SpotPrice = components['schemas']['OTEPriceRead'];

/** Each price holds for a quarter-hour block of the day-ahead market. */
export const BLOCK_DURATION_MS = 15 * 60_000;

export const oteKeys = {
  all: ['ote'] as const,
  prices: () => [...oteKeys.all, 'prices'] as const,
};

/** Shared by the hook and route loaders, so both agree on caching. */
export function spotPricesQueryOptions() {
  return queryOptions({
    queryKey: oteKeys.prices(),
    queryFn: async ({ signal }) => {
      const { data, error, response } = await api.GET('/api/v1/ote/prices', { signal });
      if (error) throw new AppError(response.status, error);
      return data;
    },
    // Day-ahead prices are auction results: once published they never change.
    // The only daily event is tomorrow's block appearing in the early
    // afternoon, so a slow poll is enough to pick it up on an open dashboard.
    staleTime: 15 * 60_000,
    refetchInterval: 15 * 60_000,
  });
}

export function useSpotPrices() {
  return useQuery(spotPricesQueryOptions());
}
