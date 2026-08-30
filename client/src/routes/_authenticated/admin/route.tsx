import { createFileRoute, Outlet, redirect } from '@tanstack/react-router';

export const Route = createFileRoute('/_authenticated/admin')({
  // Everything below /admin is back-office; the API enforces this too, but the
  // guard keeps a non-admin from reaching a page that can only fail.
  beforeLoad: ({ context }) => {
    if (!context.isAdmin()) {
      throw redirect({ to: '/' });
    }
  },
  component: Outlet,
});
