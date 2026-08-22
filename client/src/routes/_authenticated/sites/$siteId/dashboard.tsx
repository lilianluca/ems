import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/_authenticated/sites/$siteId/dashboard')({
  component: RouteComponent,
});

function RouteComponent() {
  return <div>Hello "/_authenticated/sites/$siteId/dashboard"!</div>;
}
