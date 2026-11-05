import { createFileRoute, notFound } from '@tanstack/react-router';
import { z } from 'zod';

import { Skeleton } from '@/components/ui/skeleton';
import { devicesQueryOptions, useHeatPumpDevice } from '@/features/devices/api';
import { HeatPumpDeviceForm } from '@/features/devices/components/heat-pump-device-form';

const deviceIdSchema = z.coerce.number().int().positive();

export const Route = createFileRoute('/_authenticated/sites/$siteId/devices/heat-pump/$deviceId')({
  staticData: { breadcrumb: 'devices.heat_pump_edit_title' },
  params: {
    parse: (params) => {
      // A non-numeric segment is a bad URL, not a crash: 404 rather than throw.
      const deviceId = deviceIdSchema.safeParse(params.deviceId);
      if (!deviceId.success) throw notFound();
      return { deviceId: deviceId.data };
    },
    stringify: ({ deviceId }) => ({ deviceId: String(deviceId) }),
  },
  loader: ({ context, params }) =>
    context.queryClient.query({ ...devicesQueryOptions(params.siteId), staleTime: 'static' }),
  component: EditHeatPumpDevicePage,
});

function EditHeatPumpDevicePage() {
  const { siteId, deviceId } = Route.useParams();
  const { data: device, isPending } = useHeatPumpDevice(siteId, deviceId);

  if (isPending) return <Skeleton className="h-96 w-full max-w-xl" />;
  if (!device) throw notFound();

  return <HeatPumpDeviceForm siteId={siteId} device={device} />;
}
