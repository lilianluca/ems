import { queryOptions, useQuery } from '@tanstack/react-query';

import { api } from '@/api/client';
import { AppError } from '@/api/errors';
import type { components } from '@/api/schema';

export type SiteForecastPoint = components['schemas']['SiteForecastPoint'];

/** The forecast is produced hourly, unlike the quarter-hourly spot price. */
export const FORECAST_STEP_MS = 60 * 60_000;

export const forecastKeys = {
  all: ['forecasts'] as const,
  site: (siteId: number) => [...forecastKeys.all, siteId] as const,
};

/** Shared by the hook and route loaders, so both agree on caching. */
export function siteForecastQueryOptions(siteId: number) {
  return queryOptions({
    queryKey: forecastKeys.site(siteId),
    queryFn: async ({ signal }) => {
      const { data, error, response } = await api.GET('/api/v1/sites/{site_id}/forecasts', {
        params: { path: { site_id: siteId } },
        signal,
      });
      if (error) throw new AppError(response.status, error);
      return data;
    },
    // Regenerated shortly after every hourly weather fetch.
    staleTime: 15 * 60_000,
    refetchInterval: 15 * 60_000,
  });
}

export function useSiteForecast(siteId: number) {
  return useQuery(siteForecastQueryOptions(siteId));
}
