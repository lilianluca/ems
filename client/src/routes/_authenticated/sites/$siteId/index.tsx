import { createFileRoute, redirect } from '@tanstack/react-router';

export const Route = createFileRoute('/_authenticated/sites/$siteId/')({
  beforeLoad: ({ params }) => {
    throw redirect({ to: '/sites/$siteId/dashboard', params });
  },
});
