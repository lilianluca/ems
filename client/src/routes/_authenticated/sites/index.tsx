import { createFileRoute, Link } from '@tanstack/react-router';
import { ChevronRightIcon, MapPinIcon } from 'lucide-react';
import { useTranslation } from 'react-i18next';

import { Card, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { sitesQueryOptions, useSites } from '@/features/sites/api';

export const Route = createFileRoute('/_authenticated/sites/')({
  loader: ({ context }) => context.queryClient.ensureQueryData(sitesQueryOptions()),
  component: MySitesPage,
});

/**
 * Where a user lands without a site to open, and where the site switcher's
 * "all sites" link leads. Sites are created by an administrator, so a user with
 * none can only be told whom to ask.
 */
function MySitesPage() {
  const { t } = useTranslation();
  const { data: sites, isPending } = useSites();

  return (
    <div className="flex flex-col gap-4">
      <div>
        <h1 className="text-lg font-semibold">{t('my_sites.title')}</h1>
        <p className="text-muted-foreground text-sm">{t('my_sites.description')}</p>
      </div>

      {isPending && <Skeleton className="h-24 w-full" />}

      {!isPending && (sites?.length ?? 0) === 0 && (
        <div className="py-12 text-center">
          <p className="font-medium">{t('my_sites.empty_title')}</p>
          <p className="text-muted-foreground text-sm">{t('my_sites.empty_description')}</p>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {sites?.map((site) => (
          <Link
            key={site.id}
            to="/sites/$siteId/dashboard"
            params={{ siteId: site.id }}
            className="focus-visible:ring-ring rounded-xl focus-visible:ring-2 focus-visible:outline-none"
          >
            <Card className="hover:bg-muted/50 h-full transition-colors">
              <CardHeader className="flex flex-row items-center justify-between gap-2">
                <div className="flex min-w-0 flex-col gap-1">
                  <CardTitle className="truncate">{site.name}</CardTitle>
                  <CardDescription className="flex items-center gap-1 tabular-nums">
                    <MapPinIcon className="size-3.5 shrink-0" aria-hidden />
                    {site.latitude.toFixed(4)}, {site.longitude.toFixed(4)}
                  </CardDescription>
                </div>
                <ChevronRightIcon className="text-muted-foreground size-4 shrink-0" aria-hidden />
              </CardHeader>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
