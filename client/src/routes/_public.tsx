import { createFileRoute, Outlet, redirect } from '@tanstack/react-router';

export const Route = createFileRoute('/_public')({
  beforeLoad: ({ context }) => {
    if (context.isAuthenticated()) {
      throw redirect({ to: '/dashboard' });
    }
  },
  component: PublicLayout,
});

function PublicLayout() {
  return (
    <div className="bg-muted/30 flex min-h-svh items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <Outlet />
      </div>
    </div>
  );
}
