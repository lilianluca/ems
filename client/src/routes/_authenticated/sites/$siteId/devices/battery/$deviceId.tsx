import { createFileRoute, notFound } from '@tanstack/react-router';
import { z } from 'zod';

import { Skeleton } from '@/components/ui/skeleton';
import { devicesQueryOptions, useBatteryDevice } from '@/features/devices/api';
import { BatteryDeviceForm } from '@/features/devices/components/battery-device-form';

const deviceIdSchema = z.coerce.number().int().positive();

export const Route = createFileRoute('/_authenticated/sites/$siteId/devices/battery/$deviceId')({
  parseParams: (params) => {
    // A non-numeric segment is a bad URL, not a crash: 404 rather than throw.
    const deviceId = deviceIdSchema.safeParse(params.deviceId);
    if (!deviceId.success) throw notFound();
    return { deviceId: deviceId.data };
  },
  stringifyParams: ({ deviceId }) => ({ deviceId: String(deviceId) }),
  loader: ({ context, params }) =>
    context.queryClient.ensureQueryData(devicesQueryOptions(params.siteId)),
  component: EditBatteryDevicePage,
});

function EditBatteryDevicePage() {
  const { siteId, deviceId } = Route.useParams();
  const { data: device, isPending } = useBatteryDevice(siteId, deviceId);

  if (isPending) return <Skeleton className="h-96 w-full max-w-xl" />;
  if (!device) throw notFound();

  return <BatteryDeviceForm siteId={siteId} device={device} />;
}
