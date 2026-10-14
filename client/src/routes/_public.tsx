import { createFileRoute, Outlet, redirect } from '@tanstack/react-router';

import { LogoMark } from '@/components/layout/logo-mark';

export const Route = createFileRoute('/_public')({
  beforeLoad: ({ context }) => {
    if (context.isAuthenticated()) {
      throw redirect({ to: '/' });
    }
  },
  component: PublicLayout,
});

function PublicLayout() {
  return (
    <div className="bg-muted/30 flex min-h-svh items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="mb-6 flex items-center justify-center gap-2.5">
          <LogoMark className="size-10" />
          <span className="text-primary text-2xl font-bold tracking-wide">EMS</span>
        </div>
        <Outlet />
      </div>
    </div>
  );
}
