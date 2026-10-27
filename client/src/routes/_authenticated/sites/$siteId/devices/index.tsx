import { createFileRoute, Link } from '@tanstack/react-router';
import { BatteryChargingIcon, SunIcon } from 'lucide-react';
import { useTranslation } from 'react-i18next';

import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { devicesQueryOptions, useDevices } from '@/features/devices/api';
import { DeviceCard } from '@/features/devices/components/device-card';

export const Route = createFileRoute('/_authenticated/sites/$siteId/devices/')({
  loader: ({ context, params }) =>
    context.queryClient.query({ ...devicesQueryOptions(params.siteId), staleTime: 'static' }),
  staticData: { headerActions: DevicesActions },
  component: DevicesPage,
});

/** Two explicit actions rather than one form with a type switch: the two field sets have nothing in common. */
function DevicesActions() {
  const { t } = useTranslation();
  const { siteId } = Route.useParams();

  return (
    <>
      <Button size="sm" render={<Link to="/sites/$siteId/devices/pv/new" params={{ siteId }} />}>
        <SunIcon />
        {t('devices.add_pv')}
      </Button>
      <Button
        size="sm"
        variant="outline"
        render={<Link to="/sites/$siteId/devices/battery/new" params={{ siteId }} />}
      >
        <BatteryChargingIcon />
        {t('devices.add_battery')}
      </Button>
    </>
  );
}

function DevicesPage() {
  const { t } = useTranslation();
  const { siteId } = Route.useParams();
  const { data: devices, isPending } = useDevices(siteId);

  return (
    <div className="flex flex-col gap-4">
      {isPending && <Skeleton className="h-40 w-full" />}

      {!isPending && (devices?.length ?? 0) === 0 && (
        <p className="py-12 text-center text-muted-foreground">{t('devices.empty')}</p>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        {devices?.map((device) => (
          <DeviceCard key={device.id} siteId={siteId} device={device} />
        ))}
      </div>
    </div>
  );
}
