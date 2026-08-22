import { createFileRoute } from '@tanstack/react-router';
import { z } from 'zod';

import { LoginForm } from '@/features/auth/components/login-form';

const searchSchema = z.object({
  redirect: z
    .string()
    .refine((value) => value.startsWith('/') && !value.startsWith('//'), {
      message: 'Only internal paths are allowed.',
    })
    .optional(),
});

export const Route = createFileRoute('/_public/login')({
  validateSearch: searchSchema,
  component: LoginPage,
});

function LoginPage() {
  const { redirect } = Route.useSearch();

  return <LoginForm redirectTo={redirect} />;
}
