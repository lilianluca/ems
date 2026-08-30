import { createFileRoute } from '@tanstack/react-router';

import { CreateUserForm } from '@/features/users/components/create-user-form';

export const Route = createFileRoute('/_authenticated/admin/users/new')({
  component: NewUserPage,
});

function NewUserPage() {
  return <CreateUserForm />;
}
