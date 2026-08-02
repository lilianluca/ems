import { createFileRoute } from '@tanstack/react-router';
import { z } from 'zod';

const searchSchema = z.object({
  redirect: z.string().optional(),
});

export const Route = createFileRoute('/_public/login')({
  validateSearch: searchSchema,
  component: LoginPage,
});

function LoginPage() {
  const { redirect } = Route.useSearch();

  return (
    <p className="text-muted-foreground text-sm">
      Login form goes here. Redirect target: {redirect ?? 'none'}
    </p>
  );
}
