import { queryOptions, useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { api } from '@/api/client';
import { AppError } from '@/api/errors';
import type { components } from '@/api/schema';
import { optimizationKeys } from '@/features/optimization/api';

export type SiteForecastPoint = components['schemas']['SiteForecastPoint'];
export type ForecastRefreshResult = components['schemas']['ForecastRefreshResult'];

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

/**
 * Recompute the site's forecasts now, rather than waiting for the hourly jobs.
 *
 * The plan is derived from these series, so it is invalidated with them —
 * otherwise the chart would refresh under a plan built from the old forecast.
 */
export function useRefreshForecasts(siteId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      const { data, error, response } = await api.POST(
        '/api/v1/sites/{site_id}/forecasts/refresh',
        { params: { path: { site_id: siteId } } },
      );
      if (error) throw new AppError(response.status, error);
      return data;
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: forecastKeys.site(siteId) });
      void queryClient.invalidateQueries({ queryKey: optimizationKeys.site(siteId) });
    },
  });
}
