import { createFileRoute, notFound } from '@tanstack/react-router';
import { z } from 'zod';

import { Skeleton } from '@/components/ui/skeleton';
import { appliancesQueryOptions, useAppliance } from '@/features/appliances/api';
import { ApplianceForm } from '@/features/appliances/components/appliance-form';

const applianceIdSchema = z.coerce.number().int().positive();

export const Route = createFileRoute('/_authenticated/sites/$siteId/appliances/$applianceId')({
  parseParams: (params) => {
    // A non-numeric segment is a bad URL, not a crash: 404 rather than throw.
    const applianceId = applianceIdSchema.safeParse(params.applianceId);
    if (!applianceId.success) throw notFound();
    return { applianceId: applianceId.data };
  },
  stringifyParams: ({ applianceId }) => ({ applianceId: String(applianceId) }),
  loader: ({ context, params }) =>
    context.queryClient.ensureQueryData(appliancesQueryOptions(params.siteId)),
  component: EditAppliancePage,
});

function EditAppliancePage() {
  const { siteId, applianceId } = Route.useParams();
  const { data: appliance, isPending } = useAppliance(siteId, applianceId);

  if (isPending) return <Skeleton className="h-96 w-full max-w-3xl" />;
  if (!appliance) throw notFound();

  return <ApplianceForm siteId={siteId} appliance={appliance} />;
}
