import { createFileRoute, Outlet } from '@tanstack/react-router';

export const Route = createFileRoute('/_authenticated/sites/$siteId/devices')({
  staticData: { breadcrumb: 'nav.devices' },
  component: Outlet,
});
