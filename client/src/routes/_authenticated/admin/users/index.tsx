import { createFileRoute, Link, useNavigate } from '@tanstack/react-router';
import { ChevronLeftIcon, ChevronRightIcon, UserPlusIcon } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { z } from 'zod';

import { Button } from '@/components/ui/button';
import { USERS_PAGE_SIZE, usersQueryOptions, useUsers } from '@/features/users/api';
import { UsersTable } from '@/features/users/components/users-table';

const searchSchema = z.object({
  // Optional so `<Link to="/users">` needs no search params; a malformed value
  // falls back to the first page rather than erroring the route.
  page: z.coerce.number().int().min(1).optional().catch(undefined),
});

export const Route = createFileRoute('/_authenticated/admin/users/')({
  validateSearch: searchSchema,
  loaderDeps: ({ search }) => ({ page: search.page ?? 1 }),
  loader: ({ context, deps }) => context.queryClient.ensureQueryData(usersQueryOptions(deps.page)),
  component: UsersPage,
});

function UsersPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { page = 1 } = Route.useSearch();
  const { data, isPending } = useUsers(page);

  const total = data?.total ?? 0;
  const firstOnPage = total === 0 ? 0 : (page - 1) * USERS_PAGE_SIZE + 1;
  const lastOnPage = Math.min(page * USERS_PAGE_SIZE, total);
  const hasPrevious = page > 1;
  const hasNext = page * USERS_PAGE_SIZE < total;

  const goToPage = (target: number) => {
    void navigate({ to: '/admin/users', search: { page: target } });
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h1 className="text-lg font-semibold">{t('users.title')}</h1>
          <p className="text-muted-foreground text-sm">{t('users.description')}</p>
        </div>
        <Button render={<Link to="/admin/users/new" />}>
          <UserPlusIcon />
          {t('users.new')}
        </Button>
      </div>

      <UsersTable users={data?.items ?? []} isLoading={isPending} />

      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-muted-foreground text-sm">
          {t('users.pagination', { from: firstOnPage, to: lastOnPage, total })}
        </p>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={!hasPrevious}
            onClick={() => {
              goToPage(page - 1);
            }}
          >
            <ChevronLeftIcon />
            {t('users.previous')}
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={!hasNext}
            onClick={() => {
              goToPage(page + 1);
            }}
          >
            {t('users.next')}
            <ChevronRightIcon />
          </Button>
        </div>
      </div>
    </div>
  );
}
