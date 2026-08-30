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

export type User = components['schemas']['UserRead'];
export type UserRole = components['schemas']['UserRole'];
export type CreateUserInput = components['schemas']['UserCreate'];

export const USERS_PAGE_SIZE = 20;

/** The API caps `limit` at 100, so pickers show at most that many accounts. */
export const USER_PICKER_LIMIT = 100;

export const userKeys = {
  all: ['users'] as const,
  list: (page: number) => [...userKeys.all, 'list', page] as const,
  picker: () => [...userKeys.all, 'picker'] as const,
};

/** Flat list of accounts for owner pickers, where paging would be in the way. */
export function userPickerQueryOptions() {
  return queryOptions({
    queryKey: userKeys.picker(),
    queryFn: async ({ signal }) => {
      const { data, error, response } = await api.GET('/api/v1/admin/users', {
        params: { query: { offset: 0, limit: USER_PICKER_LIMIT } },
        signal,
      });
      if (error) throw new AppError(response.status, error);
      return data.items;
    },
    staleTime: 5 * 60_000,
  });
}

/** Shared by the `useUsers` hook and the route loader, so both agree on caching. */
export function usersQueryOptions(page: number) {
  return queryOptions({
    queryKey: userKeys.list(page),
    queryFn: async ({ signal }) => {
      const { data, error, response } = await api.GET('/api/v1/admin/users', {
        params: { query: { offset: (page - 1) * USERS_PAGE_SIZE, limit: USERS_PAGE_SIZE } },
        signal,
      });
      if (error) throw new AppError(response.status, error);
      return data;
    },
    // Keeps the previous page visible while the next one loads, so the table
    // does not collapse to a skeleton on every page change.
    placeholderData: keepPreviousData,
  });
}

export function useUsers(page: number) {
  return useQuery(usersQueryOptions(page));
}

export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: CreateUserInput) => {
      const { data, error, response } = await api.POST('/api/v1/admin/users', { body: input });
      if (error) throw new AppError(response.status, error);
      return data;
    },
    onSuccess: () => {
      // Every page is stale once a user is added; totals and offsets shift.
      void queryClient.invalidateQueries({ queryKey: userKeys.all });
    },
  });
}
