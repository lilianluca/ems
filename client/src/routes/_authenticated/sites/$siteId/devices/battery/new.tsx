import { createFileRoute } from '@tanstack/react-router';

import { BatteryDeviceForm } from '@/features/devices/components/battery-device-form';

export const Route = createFileRoute('/_authenticated/sites/$siteId/devices/battery/new')({
  staticData: { breadcrumb: 'devices.battery_create_title' },
  component: NewBatteryDevicePage,
});

function NewBatteryDevicePage() {
  const { siteId } = Route.useParams();
  return <BatteryDeviceForm siteId={siteId} />;
}
