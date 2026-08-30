import { createFileRoute, Link, useNavigate } from '@tanstack/react-router';
import { ChevronLeftIcon, ChevronRightIcon, MapPinPlusIcon } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { z } from 'zod';

import { Button } from '@/components/ui/button';
import { adminSitesQueryOptions, SITES_PAGE_SIZE, useAdminSites } from '@/features/sites/admin-api';
import { AdminSitesTable } from '@/features/sites/components/admin-sites-table';

const searchSchema = z.object({
  // Optional so `<Link to="/admin/sites">` needs no search params; a malformed
  // value falls back to the first page rather than erroring the route.
  page: z.coerce.number().int().min(1).optional().catch(undefined),
});

export const Route = createFileRoute('/_authenticated/admin/sites/')({
  validateSearch: searchSchema,
  loaderDeps: ({ search }) => ({ page: search.page ?? 1 }),
  loader: ({ context, deps }) =>
    context.queryClient.ensureQueryData(adminSitesQueryOptions(deps.page)),
  component: AdminSitesPage,
});

function AdminSitesPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { page = 1 } = Route.useSearch();
  const { data, isPending } = useAdminSites(page);

  const total = data?.total ?? 0;
  const firstOnPage = total === 0 ? 0 : (page - 1) * SITES_PAGE_SIZE + 1;
  const lastOnPage = Math.min(page * SITES_PAGE_SIZE, total);
  const hasPrevious = page > 1;
  const hasNext = page * SITES_PAGE_SIZE < total;

  const goToPage = (target: number) => {
    void navigate({ to: '/admin/sites', search: { page: target } });
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h1 className="text-lg font-semibold">{t('sites.title')}</h1>
          <p className="text-muted-foreground text-sm">{t('sites.description')}</p>
        </div>
        <Button render={<Link to="/admin/sites/new" />}>
          <MapPinPlusIcon />
          {t('sites.new')}
        </Button>
      </div>

      <AdminSitesTable sites={data?.items ?? []} isLoading={isPending} />

      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-muted-foreground text-sm">
          {t('sites.pagination', { from: firstOnPage, to: lastOnPage, total })}
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
            {t('sites.previous')}
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={!hasNext}
            onClick={() => {
              goToPage(page + 1);
            }}
          >
            {t('sites.next')}
            <ChevronRightIcon />
          </Button>
        </div>
      </div>
    </div>
  );
}
