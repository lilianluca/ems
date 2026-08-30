import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate } from '@tanstack/react-router';
import { Loader2Icon, UserPlusIcon } from 'lucide-react';
import { Controller, useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { toast } from 'sonner';

import { translateError } from '@/api/errors';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Field, FieldError, FieldGroup, FieldLabel } from '@/components/ui/field';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { ValidationKey } from '@/lib/i18n/keys';

import { useCreateUser, type UserRole } from '../api';
import { type CreateUserFormValues, createUserSchema, USER_ROLES } from '../schemas';

export function CreateUserForm() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const createUser = useCreateUser();

  const {
    control,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<CreateUserFormValues>({
    resolver: zodResolver(createUserSchema),
    defaultValues: { email: '', firstName: '', lastName: '', password: '', role: 'user' },
  });

  const onSubmit = (values: CreateUserFormValues) => {
    if (createUser.isPending) return;

    createUser.mutate(values, {
      onSuccess: (user) => {
        toast.success(t('users.created', { email: user.email }));
        void navigate({ to: '/admin/users' });
      },
      onError: (error) => {
        setError('root', { message: translateError(error) });
      },
    });
  };

  return (
    <Card className="max-w-xl">
      <CardHeader>
        <CardTitle>{t('users.create_title')}</CardTitle>
        <CardDescription>{t('users.create_description')}</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <FieldGroup>
            <Controller
              control={control}
              name="firstName"
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="firstName">{t('users.first_name')}</FieldLabel>
                  <Input
                    {...field}
                    id="firstName"
                    autoComplete="given-name"
                    aria-invalid={fieldState.invalid}
                  />
                  {fieldState.error && (
                    <FieldError>{t(fieldState.error.message as ValidationKey)}</FieldError>
                  )}
                </Field>
              )}
            />

            <Controller
              control={control}
              name="lastName"
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="lastName">{t('users.last_name')}</FieldLabel>
                  <Input
                    {...field}
                    id="lastName"
                    autoComplete="family-name"
                    aria-invalid={fieldState.invalid}
                  />
                  {fieldState.error && (
                    <FieldError>{t(fieldState.error.message as ValidationKey)}</FieldError>
                  )}
                </Field>
              )}
            />

            <Controller
              control={control}
              name="email"
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="email">{t('users.email')}</FieldLabel>
                  <Input
                    {...field}
                    id="email"
                    type="email"
                    autoComplete="off"
                    placeholder={t('auth.email_placeholder')}
                    aria-invalid={fieldState.invalid}
                  />
                  {fieldState.error && (
                    <FieldError>{t(fieldState.error.message as ValidationKey)}</FieldError>
                  )}
                </Field>
              )}
            />

            <Controller
              control={control}
              name="password"
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="password">{t('users.password')}</FieldLabel>
                  <Input
                    {...field}
                    id="password"
                    type="password"
                    // The administrator sets an initial password and hands it over;
                    // never let a password manager capture it as their own.
                    autoComplete="new-password"
                    aria-invalid={fieldState.invalid}
                  />
                  {fieldState.error && (
                    <FieldError>{t(fieldState.error.message as ValidationKey)}</FieldError>
                  )}
                </Field>
              )}
            />

            <Controller
              control={control}
              name="role"
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="role">{t('users.role')}</FieldLabel>
                  <Select
                    value={field.value}
                    onValueChange={(role) => {
                      // Base UI reports a cleared selection as null; a role is
                      // always required, so keep the previous value instead.
                      if (role !== null) {
                        field.onChange(role);
                      }
                    }}
                  >
                    <SelectTrigger id="role" className="w-full" onBlur={field.onBlur}>
                      <SelectValue>{(role: UserRole) => t(`users.role_${role}`)}</SelectValue>
                    </SelectTrigger>
                    <SelectContent>
                      {USER_ROLES.map((role) => (
                        <SelectItem key={role} value={role}>
                          {t(`users.role_${role}`)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {fieldState.error && (
                    <FieldError>{t(fieldState.error.message as ValidationKey)}</FieldError>
                  )}
                </Field>
              )}
            />

            {errors.root && (
              <p role="alert" className="text-destructive text-sm">
                {errors.root.message}
              </p>
            )}

            <div className="flex gap-2">
              <Button type="submit" disabled={createUser.isPending}>
                {createUser.isPending ? (
                  <Loader2Icon className="animate-spin" aria-hidden />
                ) : (
                  <UserPlusIcon />
                )}
                {createUser.isPending ? t('users.submitting') : t('users.submit')}
              </Button>
              <Button
                type="button"
                variant="outline"
                disabled={createUser.isPending}
                onClick={() => {
                  void navigate({ to: '/admin/users' });
                }}
              >
                {t('users.cancel')}
              </Button>
            </div>
          </FieldGroup>
        </form>
      </CardContent>
    </Card>
  );
}
