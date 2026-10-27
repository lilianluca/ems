import { createFileRoute, Outlet } from '@tanstack/react-router';

export const Route = createFileRoute('/_authenticated/admin/users')({
  staticData: { breadcrumb: 'nav.users' },
  component: Outlet,
});
