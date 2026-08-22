import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/_authenticated/sites/$siteId/measurements')({
  component: RouteComponent,
});

function RouteComponent() {
  return <div>Hello "/_authenticated/sites/$siteId/measurements"!</div>;
}
