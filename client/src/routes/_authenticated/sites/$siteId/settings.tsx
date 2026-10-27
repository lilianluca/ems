import { createFileRoute } from '@tanstack/react-router';

import { Skeleton } from '@/components/ui/skeleton';
import { sitesQueryOptions, useSite } from '@/features/sites/api';
import { HouseForm } from '@/features/sites/components/house-form';
import { SavingModePicker } from '@/features/sites/components/saving-mode-picker';
import { SiteDetailsForm } from '@/features/sites/components/site-details-form';

export const Route = createFileRoute('/_authenticated/sites/$siteId/settings')({
  staticData: { breadcrumb: 'nav.settings' },
  loader: ({ context }) =>
    context.queryClient.query({ ...sitesQueryOptions(), staleTime: 'static' }),
  component: SiteSettingsPage,
});

function SiteSettingsPage() {
  const { siteId } = Route.useParams();
  const { data: site, isPending } = useSite(siteId);

  return (
    <div className="flex max-w-3xl flex-col gap-4">
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
