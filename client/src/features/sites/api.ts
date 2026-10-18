import { queryOptions, useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { api } from '@/api/client';
import { AppError } from '@/api/errors';
import type { components } from '@/api/schema';
import type { AppliancePriority } from '@/features/appliances/api';
import { forecastKeys } from '@/features/forecasts/api';
import { optimizationKeys } from '@/features/optimization/api';

export type Site = components['schemas']['SiteRead'];
export type SiteUpdateInput = components['schemas']['SiteUpdate'];
export type SavingMode = components['schemas']['SavingMode'];

/** From the mode that cuts nothing to the one that keeps only the essential. */
export const SAVING_MODES = [
  'low',
  'medium',
  'high',
  'extreme',
] as const satisfies readonly SavingMode[];

/**
 * The least needed priority each mode still runs, mirroring
 * `SavingMode.max_priority` on the server. The server decides what the forecast
 * leaves out; this only lets the appliance list say so.
 */
export const SAVING_MODE_MAX_PRIORITY: Record<SavingMode, AppliancePriority> = {
  low: 4,
  medium: 3,
  high: 2,
  extreme: 1,
};

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

/** One of the caller's sites, read from the list the site switcher already holds. */
export function useSite(siteId: number) {
  return useQuery({
    ...sitesQueryOptions(),
    select: (sites) => sites.find((site) => site.id === siteId) ?? null,
  });
}

/**
 * A change of saving mode rebuilds the consumption forecast on the server, and
 * the plan is computed from it, so both are refetched along with the site.
 */
export function useUpdateSite(siteId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: SiteUpdateInput) => {
      const { data, error, response } = await api.PATCH('/api/v1/sites/{site_id}', {
        params: { path: { site_id: siteId } },
        body: input,
      });
      if (error) throw new AppError(response.status, error);
      return data;
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: siteKeys.all });
      void queryClient.invalidateQueries({ queryKey: forecastKeys.site(siteId) });
      void queryClient.invalidateQueries({ queryKey: optimizationKeys.site(siteId) });
    },
  });
}
