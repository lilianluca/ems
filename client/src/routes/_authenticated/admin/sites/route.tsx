import { createFileRoute, Outlet } from '@tanstack/react-router';

export const Route = createFileRoute('/_authenticated/admin/sites')({
  staticData: { breadcrumb: 'nav.manage_sites' },
  component: Outlet,
});
