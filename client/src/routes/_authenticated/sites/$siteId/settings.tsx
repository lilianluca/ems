import { createFileRoute } from '@tanstack/react-router';
import { useTranslation } from 'react-i18next';

import { Skeleton } from '@/components/ui/skeleton';
import { sitesQueryOptions, useSite } from '@/features/sites/api';
import { HouseForm } from '@/features/sites/components/house-form';
import { SavingModePicker } from '@/features/sites/components/saving-mode-picker';
import { SiteDetailsForm } from '@/features/sites/components/site-details-form';

export const Route = createFileRoute('/_authenticated/sites/$siteId/settings')({
  loader: ({ context }) =>
    context.queryClient.query({ ...sitesQueryOptions(), staleTime: 'static' }),
  component: SiteSettingsPage,
});

function SiteSettingsPage() {
  const { t } = useTranslation();
  const { siteId } = Route.useParams();
  const { data: site, isPending } = useSite(siteId);

  return (
    <div className="flex max-w-3xl flex-col gap-4">
      <div>
        <h1 className="text-lg font-semibold">{t('settings.title')}</h1>
        <p className="text-sm text-muted-foreground">{t('settings.description')}</p>
      </div>

      {isPending && <Skeleton className="h-64 w-full" />}

      {site && (
        <>
          <SavingModePicker site={site} />
          {/* Keyed by the site, so switching sites starts the forms from the new one. */}
          <HouseForm key={`house-${site.id}`} site={site} />
          <SiteDetailsForm key={site.id} site={site} />
        </>
      )}
    </div>
  );
}
