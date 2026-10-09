import { queryOptions, useQuery } from '@tanstack/react-query';

import { api } from '@/api/client';
import { AppError } from '@/api/errors';
import type { components } from '@/api/schema';
import { type CalendarMonth, pragueMonthWindow } from '@/lib/datetime';

export type DailySavings = components['schemas']['DailySavings'];
export type SavingsTotal = components['schemas']['SavingsTotal'];

export const savingsKeys = {
  all: ['savings'] as const,
  today: (siteId: number) => [...savingsKeys.all, siteId, 'today'] as const,
  month: (siteId: number, { year, month }: CalendarMonth) =>
    [...savingsKeys.all, siteId, 'month', year, month] as const,
  total: (siteId: number) => [...savingsKeys.all, siteId, 'total'] as const,
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

/** One row per day of the month that has at least one recorded step. */
export function monthSavingsQueryOptions(siteId: number, month: CalendarMonth) {
  return queryOptions({
    queryKey: savingsKeys.month(siteId, month),
    queryFn: async ({ signal }) => {
      const [start, end] = pragueMonthWindow(month);
      const { data, error, response } = await api.GET('/api/v1/sites/{site_id}/savings', {
        params: {
          path: { site_id: siteId },
          query: { start: new Date(start).toISOString(), end: new Date(end).toISOString() },
        },
        signal,
      });
      if (error) throw new AppError(response.status, error);
      return data;
    },
    staleTime: 15 * 60_000,
  });
}

export function useMonthSavings(siteId: number, month: CalendarMonth) {
  return useQuery(monthSavingsQueryOptions(siteId, month));
}

export function totalSavingsQueryOptions(siteId: number) {
  return queryOptions({
    queryKey: savingsKeys.total(siteId),
    queryFn: async ({ signal }) => {
      const { data, error, response } = await api.GET('/api/v1/sites/{site_id}/savings/total', {
        params: { path: { site_id: siteId } },
        signal,
      });
      if (error) throw new AppError(response.status, error);
      return data;
    },
    staleTime: 15 * 60_000,
  });
}

export function useTotalSavings(siteId: number) {
  return useQuery(totalSavingsQueryOptions(siteId));
}
