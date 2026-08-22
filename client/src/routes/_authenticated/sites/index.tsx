import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/_authenticated/sites/')({
  component: RouteComponent,
});

function RouteComponent() {
  return <div>Hello "/_authenticated/sites/"!</div>;
}
