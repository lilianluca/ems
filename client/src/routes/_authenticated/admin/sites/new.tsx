import { createFileRoute } from '@tanstack/react-router';

import { CreateSiteForm } from '@/features/sites/components/create-site-form';

export const Route = createFileRoute('/_authenticated/admin/sites/new')({
  component: NewSitePage,
});

function NewSitePage() {
  return <CreateSiteForm />;
}
