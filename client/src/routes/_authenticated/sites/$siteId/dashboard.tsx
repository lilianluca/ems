import { createFileRoute } from '@tanstack/react-router';

import { spotPricesQueryOptions } from '@/features/ote/api';
import { SpotPriceChart } from '@/features/ote/components/spot-price-chart';

export const Route = createFileRoute('/_authenticated/sites/$siteId/dashboard')({
  loader: ({ context }) => context.queryClient.ensureQueryData(spotPricesQueryOptions()),
  component: DashboardPage,
});

function DashboardPage() {
  return (
    <div className="flex flex-col gap-4">
      {/* Spot prices are nationwide, so this card is the same for every site. */}
      <SpotPriceChart />
    </div>
  );
}
