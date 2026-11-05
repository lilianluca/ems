import { createFileRoute } from '@tanstack/react-router';

import { HeatPumpDeviceForm } from '@/features/devices/components/heat-pump-device-form';

export const Route = createFileRoute('/_authenticated/sites/$siteId/devices/heat-pump/new')({
  staticData: { breadcrumb: 'devices.heat_pump_create_title' },
  component: NewHeatPumpDevicePage,
});

function NewHeatPumpDevicePage() {
  const { siteId } = Route.useParams();
  return <HeatPumpDeviceForm siteId={siteId} />;
}
