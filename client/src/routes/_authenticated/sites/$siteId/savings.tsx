import { createFileRoute } from '@tanstack/react-router';

import { monthSavingsQueryOptions, totalSavingsQueryOptions } from '@/features/savings/api';
import { SavingsHistory } from '@/features/savings/components/savings-history';
import { pragueMonth } from '@/lib/datetime';

export const Route = createFileRoute('/_authenticated/sites/$siteId/savings')({
  loader: ({ context, params }) =>
    Promise.all([
      context.queryClient.ensureQueryData(
        monthSavingsQueryOptions(params.siteId, pragueMonth(Date.now())),
      ),
      context.queryClient.ensureQueryData(totalSavingsQueryOptions(params.siteId)),
    ]),
  component: SavingsPage,
});

function SavingsPage() {
  const { siteId } = Route.useParams();
  return <SavingsHistory siteId={siteId} />;
}
