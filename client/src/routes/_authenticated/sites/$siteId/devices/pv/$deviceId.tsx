import { createFileRoute, notFound } from '@tanstack/react-router';
import { z } from 'zod';

import { Skeleton } from '@/components/ui/skeleton';
import { devicesQueryOptions, usePVDevice } from '@/features/devices/api';
import { PVDeviceForm } from '@/features/devices/components/pv-device-form';

const deviceIdSchema = z.coerce.number().int().positive();

export const Route = createFileRoute('/_authenticated/sites/$siteId/devices/pv/$deviceId')({
  parseParams: (params) => {
    // A non-numeric segment is a bad URL, not a crash: 404 rather than throw.
    const deviceId = deviceIdSchema.safeParse(params.deviceId);
    if (!deviceId.success) throw notFound();
    return { deviceId: deviceId.data };
  },
  stringifyParams: ({ deviceId }) => ({ deviceId: String(deviceId) }),
  loader: ({ context, params }) =>
    context.queryClient.ensureQueryData(devicesQueryOptions(params.siteId)),
  component: EditPVDevicePage,
});

function EditPVDevicePage() {
  const { siteId, deviceId } = Route.useParams();
  const { data: device, isPending } = usePVDevice(siteId, deviceId);

  if (isPending) return <Skeleton className="h-96 w-full max-w-xl" />;
  if (!device) throw notFound();

  return <PVDeviceForm siteId={siteId} device={device} />;
}
