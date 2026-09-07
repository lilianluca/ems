import { createFileRoute } from '@tanstack/react-router';

import { BatteryDeviceForm } from '@/features/devices/components/battery-device-form';

export const Route = createFileRoute('/_authenticated/sites/$siteId/devices/battery/new')({
  component: NewBatteryDevicePage,
});

function NewBatteryDevicePage() {
  const { siteId } = Route.useParams();
  return <BatteryDeviceForm siteId={siteId} />;
}
