import { createFileRoute, Link } from '@tanstack/react-router';
import { BatteryChargingIcon, SunIcon } from 'lucide-react';
import { useTranslation } from 'react-i18next';

import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { devicesQueryOptions, useDevices } from '@/features/devices/api';
import { DeviceCard } from '@/features/devices/components/device-card';

export const Route = createFileRoute('/_authenticated/sites/$siteId/devices/')({
  loader: ({ context, params }) =>
    context.queryClient.ensureQueryData(devicesQueryOptions(params.siteId)),
  component: DevicesPage,
});

function DevicesPage() {
  const { t } = useTranslation();
  const { siteId } = Route.useParams();
  const { data: devices, isPending } = useDevices(siteId);

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h1 className="text-lg font-semibold">{t('devices.title')}</h1>
          <p className="text-muted-foreground text-sm">{t('devices.description')}</p>
        </div>
        {/* Two explicit actions rather than one form with a type switch: the two
            field sets have nothing in common. */}
        <div className="flex flex-wrap gap-2">
          <Button render={<Link to="/sites/$siteId/devices/pv/new" params={{ siteId }} />}>
            <SunIcon />
            {t('devices.add_pv')}
          </Button>
          <Button
            variant="outline"
            render={<Link to="/sites/$siteId/devices/battery/new" params={{ siteId }} />}
          >
            <BatteryChargingIcon />
            {t('devices.add_battery')}
          </Button>
        </div>
      </div>

      {isPending && <Skeleton className="h-40 w-full" />}

      {!isPending && (devices?.length ?? 0) === 0 && (
        <p className="text-muted-foreground py-12 text-center">{t('devices.empty')}</p>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        {devices?.map((device) => (
          <DeviceCard key={device.id} siteId={siteId} device={device} />
        ))}
      </div>
    </div>
  );
}
