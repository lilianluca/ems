import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/_authenticated/dashboard')({
  component: DashboardPage,
});

function DashboardPage() {
  return <h1 className="p-6 text-2xl font-semibold">Dashboard</h1>;
}
