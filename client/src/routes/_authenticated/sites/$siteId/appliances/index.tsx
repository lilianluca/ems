import { createFileRoute, Link } from '@tanstack/react-router';
import { PlusIcon } from 'lucide-react';
import { useTranslation } from 'react-i18next';

import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { appliancesQueryOptions, useAppliances } from '@/features/appliances/api';
import { ApplianceCard } from '@/features/appliances/components/appliance-card';

export const Route = createFileRoute('/_authenticated/sites/$siteId/appliances/')({
  loader: ({ context, params }) =>
    context.queryClient.ensureQueryData(appliancesQueryOptions(params.siteId)),
  component: AppliancesPage,
});

function AppliancesPage() {
  const { t } = useTranslation();
  const { siteId } = Route.useParams();
  const { data: appliances, isPending } = useAppliances(siteId);

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h1 className="text-lg font-semibold">{t('appliances.title')}</h1>
          <p className="text-muted-foreground text-sm">{t('appliances.description')}</p>
        </div>
        <Button render={<Link to="/sites/$siteId/appliances/new" params={{ siteId }} />}>
          <PlusIcon />
          {t('appliances.new')}
        </Button>
      </div>

      {isPending && <Skeleton className="h-40 w-full" />}

      {!isPending && (appliances?.length ?? 0) === 0 && (
        <p className="text-muted-foreground py-12 text-center">{t('appliances.empty')}</p>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        {appliances?.map((appliance) => (
          <ApplianceCard key={appliance.id} siteId={siteId} appliance={appliance} />
        ))}
      </div>
    </div>
  );
}
