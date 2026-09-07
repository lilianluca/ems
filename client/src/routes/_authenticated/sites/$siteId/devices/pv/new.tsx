import { createFileRoute } from '@tanstack/react-router';

import { PVDeviceForm } from '@/features/devices/components/pv-device-form';

export const Route = createFileRoute('/_authenticated/sites/$siteId/devices/pv/new')({
  component: NewPVDevicePage,
});

function NewPVDevicePage() {
  const { siteId } = Route.useParams();
  return <PVDeviceForm siteId={siteId} />;
}
