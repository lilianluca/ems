import { queryOptions, useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { api } from '@/api/client';
import { AppError } from '@/api/errors';
import type { components } from '@/api/schema';
import { forecastKeys } from '@/features/forecasts/api';

export type PVDevice = components['schemas']['PVDeviceRead'];
export type BatteryDevice = components['schemas']['BatteryDeviceRead'];
export type Device = PVDevice | BatteryDevice;

export type PVDeviceInput = components['schemas']['PVDeviceCreate'];
export type BatteryDeviceInput = components['schemas']['BatteryDeviceCreate'];

export type BatteryState = components['schemas']['BatteryStateRead'];

export const deviceKeys = {
  all: ['devices'] as const,
  list: (siteId: number) => [...deviceKeys.all, 'list', siteId] as const,
  batteryStates: (siteId: number) => [...deviceKeys.all, 'battery-state', siteId] as const,
  batteryState: (siteId: number, deviceId: number) =>
    [...deviceKeys.batteryStates(siteId), deviceId] as const,
};

/** Shared by the hook and route loaders, so both agree on caching. */
export function devicesQueryOptions(siteId: number) {
  return queryOptions({
    queryKey: deviceKeys.list(siteId),
    queryFn: async ({ signal }) => {
      const { data, error, response } = await api.GET('/api/v1/sites/{site_id}/devices', {
        params: { path: { site_id: siteId } },
        signal,
      });
      if (error) throw new AppError(response.status, error);
      return data;
    },
  });
}

export function useDevices(siteId: number) {
  return useQuery(devicesQueryOptions(siteId));
}

/**
 * Picked out of the site's device list rather than fetched on its own: the list
 * is already cached, and there is no endpoint that returns one device typed.
 * Fields are selected explicitly so the caller does not subscribe to every
 * change on the underlying query.
 */
export function usePVDevice(siteId: number, deviceId: number) {
  const query = useDevices(siteId);
  // A type predicate, because `find` does not narrow the union by itself.
  const device = query.data?.find(
    (item): item is PVDevice => item.id === deviceId && item.type === 'pv',
  );
  return { data: device, isPending: query.isPending, isError: query.isError };
}

export function useBatteryDevice(siteId: number, deviceId: number) {
  const query = useDevices(siteId);
  const device = query.data?.find(
    (item): item is BatteryDevice => item.id === deviceId && item.type === 'battery',
  );
  return { data: device, isPending: query.isPending, isError: query.isError };
}

/**
 * A new state lands at most once a step, so polling every minute shows it soon
 * after it is recorded at a load not worth worrying about.
 */
export function batteryStateQueryOptions(siteId: number, deviceId: number) {
  return queryOptions({
    queryKey: deviceKeys.batteryState(siteId, deviceId),
    queryFn: async ({ signal }) => {
      const { data, error, response } = await api.GET(
        '/api/v1/sites/{site_id}/devices/battery/{device_id}/state',
        { params: { path: { site_id: siteId, device_id: deviceId } }, signal },
      );
      if (error) throw new AppError(response.status, error);
      // `null` is the answer for a battery with no recorded state, and React
      // Query rejects `undefined` as data, so the two are not left to differ.
      return data ?? null;
    },
    staleTime: 60_000,
    refetchInterval: 60_000,
  });
}

export function useBatteryState(siteId: number, deviceId: number) {
  return useQuery(batteryStateQueryOptions(siteId, deviceId));
}

/**
 * Device parameters feed the PV simulation, so a change invalidates the stored
 * forecast as well — it was computed from the values that just changed. The
 * battery state goes too, because its percentage is taken of the capacity.
 */
function useDeviceInvalidation(siteId: number) {
  const queryClient = useQueryClient();
  return () => {
    void queryClient.invalidateQueries({ queryKey: deviceKeys.list(siteId) });
    void queryClient.invalidateQueries({ queryKey: deviceKeys.batteryStates(siteId) });
    void queryClient.invalidateQueries({ queryKey: forecastKeys.site(siteId) });
  };
}

export function useCreatePVDevice(siteId: number) {
  const invalidate = useDeviceInvalidation(siteId);

  return useMutation({
    mutationFn: async (input: PVDeviceInput) => {
      const { data, error, response } = await api.POST('/api/v1/sites/{site_id}/devices/pv', {
        params: { path: { site_id: siteId } },
        body: input,
      });
      if (error) throw new AppError(response.status, error);
      return data;
    },
    onSuccess: invalidate,
  });
}

export function useUpdatePVDevice(siteId: number, deviceId: number) {
  const invalidate = useDeviceInvalidation(siteId);

  return useMutation({
    mutationFn: async (input: PVDeviceInput) => {
      const { data, error, response } = await api.PATCH(
        '/api/v1/sites/{site_id}/devices/pv/{device_id}',
        { params: { path: { site_id: siteId, device_id: deviceId } }, body: input },
      );
      if (error) throw new AppError(response.status, error);
      return data;
    },
    onSuccess: invalidate,
  });
}

export function useCreateBatteryDevice(siteId: number) {
  const invalidate = useDeviceInvalidation(siteId);

  return useMutation({
    mutationFn: async (input: BatteryDeviceInput) => {
      const { data, error, response } = await api.POST('/api/v1/sites/{site_id}/devices/battery', {
        params: { path: { site_id: siteId } },
        body: input,
      });
      if (error) throw new AppError(response.status, error);
      return data;
    },
    onSuccess: invalidate,
  });
}

export function useUpdateBatteryDevice(siteId: number, deviceId: number) {
  const invalidate = useDeviceInvalidation(siteId);

  return useMutation({
    mutationFn: async (input: BatteryDeviceInput) => {
      const { data, error, response } = await api.PATCH(
        '/api/v1/sites/{site_id}/devices/battery/{device_id}',
        { params: { path: { site_id: siteId, device_id: deviceId } }, body: input },
      );
      if (error) throw new AppError(response.status, error);
      return data;
    },
    onSuccess: invalidate,
  });
}

export function useDeleteDevice(siteId: number) {
  const invalidate = useDeviceInvalidation(siteId);

  return useMutation({
    mutationFn: async (deviceId: number) => {
      const { error, response } = await api.DELETE('/api/v1/sites/{site_id}/devices/{device_id}', {
        params: { path: { site_id: siteId, device_id: deviceId } },
      });
      if (error) throw new AppError(response.status, error);
    },
    onSuccess: invalidate,
  });
}
