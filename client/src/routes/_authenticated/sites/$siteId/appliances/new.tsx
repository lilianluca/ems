import { createFileRoute } from '@tanstack/react-router';

import { ApplianceForm } from '@/features/appliances/components/appliance-form';

export const Route = createFileRoute('/_authenticated/sites/$siteId/appliances/new')({
  staticData: { breadcrumb: 'appliances.create_title' },
  component: NewAppliancePage,
});

function NewAppliancePage() {
  const { siteId } = Route.useParams();
  return <ApplianceForm siteId={siteId} />;
}
