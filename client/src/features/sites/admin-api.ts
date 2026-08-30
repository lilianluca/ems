import {
  keepPreviousData,
  queryOptions,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query';

import { api } from '@/api/client';
import { AppError } from '@/api/errors';
import type { components } from '@/api/schema';

import { siteKeys } from './api';

export type CreateSiteInput = components['schemas']['SiteCreate'];

export const SITES_PAGE_SIZE = 20;

/** Namespaced separately from `siteKeys.list()`, which holds the caller's own sites. */
export const adminSiteKeys = {
  all: [...siteKeys.all, 'admin'] as const,
  list: (page: number) => [...adminSiteKeys.all, 'list', page] as const,
};

/** Shared by the `useAdminSites` hook and the route loader, so both agree on caching. */
export function adminSitesQueryOptions(page: number) {
  return queryOptions({
    queryKey: adminSiteKeys.list(page),
    queryFn: async ({ signal }) => {
      const { data, error, response } = await api.GET('/api/v1/admin/sites', {
        params: { query: { offset: (page - 1) * SITES_PAGE_SIZE, limit: SITES_PAGE_SIZE } },
        signal,
      });
      if (error) throw new AppError(response.status, error);
      return data;
    },
    // Keeps the previous page visible while the next one loads.
    placeholderData: keepPreviousData,
  });
}

export function useAdminSites(page: number) {
  return useQuery(adminSitesQueryOptions(page));
}

/** Invalidates both the admin listing and the sidebar's own-sites list. */
function useSiteListInvalidation() {
  const queryClient = useQueryClient();
  return () => {
    void queryClient.invalidateQueries({ queryKey: siteKeys.all });
  };
}

export function useCreateSite() {
  const invalidate = useSiteListInvalidation();

  return useMutation({
    mutationFn: async (input: CreateSiteInput) => {
      const { data, error, response } = await api.POST('/api/v1/admin/sites', { body: input });
      if (error) throw new AppError(response.status, error);
      return data;
    },
    onSuccess: invalidate,
  });
}

export function useDeleteSite() {
  const invalidate = useSiteListInvalidation();

  return useMutation({
    mutationFn: async (siteId: number) => {
      const { error, response } = await api.DELETE('/api/v1/admin/sites/{site_id}', {
        params: { path: { site_id: siteId } },
      });
      if (error) throw new AppError(response.status, error);
    },
    onSuccess: invalidate,
  });
}
