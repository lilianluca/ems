import { createFileRoute, Outlet } from '@tanstack/react-router';

export const Route = createFileRoute('/_authenticated/sites/$siteId/appliances')({
  staticData: { breadcrumb: 'nav.appliances' },
  component: Outlet,
});
