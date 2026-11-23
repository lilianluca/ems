import { createFileRoute } from '@tanstack/react-router';

import { WaterHeaterDeviceForm } from '@/features/devices/components/water-heater-device-form';

export const Route = createFileRoute('/_authenticated/sites/$siteId/devices/water-heater/new')({
  staticData: { breadcrumb: 'devices.water_heater_create_title' },
  component: NewWaterHeaterDevicePage,
});

function NewWaterHeaterDevicePage() {
  const { siteId } = Route.useParams();
  return <WaterHeaterDeviceForm siteId={siteId} />;
}
