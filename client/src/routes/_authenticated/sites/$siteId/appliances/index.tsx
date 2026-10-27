import { createFileRoute, Link } from '@tanstack/react-router';
import { PlusIcon } from 'lucide-react';
import { useTranslation } from 'react-i18next';

import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { appliancesQueryOptions, useAppliances } from '@/features/appliances/api';
import { ApplianceCard } from '@/features/appliances/components/appliance-card';

export const Route = createFileRoute('/_authenticated/sites/$siteId/appliances/')({
  loader: ({ context, params }) =>
    context.queryClient.query({ ...appliancesQueryOptions(params.siteId), staleTime: 'static' }),
  staticData: { headerActions: AppliancesActions },
  component: AppliancesPage,
});

function AppliancesActions() {
  const { t } = useTranslation();
  const { siteId } = Route.useParams();

  return (
    <Button size="sm" render={<Link to="/sites/$siteId/appliances/new" params={{ siteId }} />}>
      <PlusIcon />
      {t('appliances.new')}
    </Button>
  );
}

function AppliancesPage() {
  const { t } = useTranslation();
  const { siteId } = Route.useParams();
  const { data: appliances, isPending } = useAppliances(siteId);

  return (
    <div className="flex flex-col gap-4">
      {isPending && <Skeleton className="h-40 w-full" />}

      {!isPending && (appliances?.length ?? 0) === 0 && (
        <p className="py-12 text-center text-muted-foreground">{t('appliances.empty')}</p>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        {appliances?.map((appliance) => (
          <ApplianceCard key={appliance.id} siteId={siteId} appliance={appliance} />
        ))}
      </div>
    </div>
  );
}
