import { createFileRoute } from '@tanstack/react-router';

import { devicesQueryOptions } from '@/features/devices/api';
import { BatteryStateCards } from '@/features/devices/components/battery-state-card';
import { siteForecastQueryOptions } from '@/features/forecasts/api';
import { SiteForecastChart } from '@/features/forecasts/components/site-forecast-chart';
import { optimizationQueryOptions } from '@/features/optimization/api';
import { OptimizationChart } from '@/features/optimization/components/optimization-chart';
import { spotPricesQueryOptions } from '@/features/ote/api';
import { SpotPriceChart } from '@/features/ote/components/spot-price-chart';
import { useNow } from '@/hooks/use-now';
import { pragueMarketWindow } from '@/lib/datetime';

/** The window only shifts at midnight; re-deriving it every ten minutes is plenty. */
const WINDOW_REFRESH_MS = 10 * 60_000;

export const Route = createFileRoute('/_authenticated/sites/$siteId/dashboard')({
  loader: ({ context, params }) =>
    Promise.all([
      context.queryClient.ensureQueryData(spotPricesQueryOptions()),
      context.queryClient.ensureQueryData(siteForecastQueryOptions(params.siteId)),
      // Loaded up front so the battery cards appear with the page rather than
      // popping in above the charts and pushing them down.
      context.queryClient.ensureQueryData(devicesQueryOptions(params.siteId)),
      // The plan answers 422 for a site with no battery, which is a normal
      // state rather than a failed route.
      context.queryClient
        .ensureQueryData(optimizationQueryOptions(params.siteId))
        .catch(() => null),
    ]),
  component: DashboardPage,
});

function DashboardPage() {
  const { siteId } = Route.useParams();
  const now = useNow(WINDOW_REFRESH_MS);

  // Both charts are pinned to the market window rather than to their own data,
  // so they can be read vertically: a cheap hour lines up with the surplus it
  // should be spent on. It also means that before tomorrow's auction clears, the
  // right half stays empty instead of one day being stretched across full width.
  const window = pragueMarketWindow(now);

  return (
    <div className="flex flex-col gap-4">
      {/* Spot prices are nationwide, so this card is the same for every site. */}
      <SpotPriceChart window={window} />
      <SiteForecastChart siteId={siteId} window={window} />
      {/* Directly above the plan, which starts from the state shown here. */}
      <BatteryStateCards siteId={siteId} />
      <OptimizationChart siteId={siteId} window={window} />
    </div>
  );
}
