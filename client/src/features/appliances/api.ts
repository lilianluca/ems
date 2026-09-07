import { queryOptions, useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { api } from '@/api/client';
import { AppError } from '@/api/errors';
import type { components } from '@/api/schema';
import { forecastKeys } from '@/features/forecasts/api';

export type Appliance = components['schemas']['ApplianceRead'];
export type ApplianceInput = components['schemas']['ApplianceCreate'];
export type ApplianceBehavior = components['schemas']['ApplianceBehavior'];
export type ApplianceTimeWindow = components['schemas']['TimeWindow'];

export const APPLIANCE_BEHAVIORS = ['constant', 'cyclic', 'scheduled', 'on_demand'] as const;

export const applianceKeys = {
  all: ['appliances'] as const,
  list: (siteId: number) => [...applianceKeys.all, 'list', siteId] as const,
};

/** Shared by the hook and route loaders, so both agree on caching. */
export function appliancesQueryOptions(siteId: number) {
  return queryOptions({
    queryKey: applianceKeys.list(siteId),
    queryFn: async ({ signal }) => {
      const { data, error, response } = await api.GET('/api/v1/sites/{site_id}/appliances', {
        params: { path: { site_id: siteId } },
        signal,
      });
      if (error) throw new AppError(response.status, error);
      return data;
    },
  });
}

export function useAppliances(siteId: number) {
  return useQuery(appliancesQueryOptions(siteId));
}

export function useAppliance(siteId: number, applianceId: number) {
  const query = useAppliances(siteId);
  return {
    data: query.data?.find((item) => item.id === applianceId),
    isPending: query.isPending,
    isError: query.isError,
  };
}

/**
 * Appliances are the whole input to the load forecast, so a change invalidates
 * the stored forecast as well — it was computed from what just changed.
 */
function useApplianceInvalidation(siteId: number) {
  const queryClient = useQueryClient();
  return () => {
    void queryClient.invalidateQueries({ queryKey: applianceKeys.list(siteId) });
    void queryClient.invalidateQueries({ queryKey: forecastKeys.site(siteId) });
  };
}

export function useCreateAppliance(siteId: number) {
  const invalidate = useApplianceInvalidation(siteId);

  return useMutation({
    mutationFn: async (input: ApplianceInput) => {
      const { data, error, response } = await api.POST('/api/v1/sites/{site_id}/appliances', {
        params: { path: { site_id: siteId } },
        body: input,
      });
      if (error) throw new AppError(response.status, error);
      return data;
    },
    onSuccess: invalidate,
  });
}

export function useUpdateAppliance(siteId: number, applianceId: number) {
  const invalidate = useApplianceInvalidation(siteId);

  return useMutation({
    mutationFn: async (input: ApplianceInput) => {
      const { data, error, response } = await api.PATCH(
        '/api/v1/sites/{site_id}/appliances/{appliance_id}',
        { params: { path: { site_id: siteId, appliance_id: applianceId } }, body: input },
      );
      if (error) throw new AppError(response.status, error);
      return data;
    },
    onSuccess: invalidate,
  });
}

export function useDeleteAppliance(siteId: number) {
  const invalidate = useApplianceInvalidation(siteId);

  return useMutation({
    mutationFn: async (applianceId: number) => {
      const { error, response } = await api.DELETE(
        '/api/v1/sites/{site_id}/appliances/{appliance_id}',
        { params: { path: { site_id: siteId, appliance_id: applianceId } } },
      );
      if (error) throw new AppError(response.status, error);
    },
    onSuccess: invalidate,
  });
}
