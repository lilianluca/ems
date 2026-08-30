import { zodResolver } from '@hookform/resolvers/zod';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from '@tanstack/react-router';
import { Loader2Icon, MapPinPlusIcon } from 'lucide-react';
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
import { userPickerQueryOptions } from '@/features/users/api';
import type { ValidationKey } from '@/lib/i18n/keys';

import { useCreateSite } from '../admin-api';
import { type CreateSiteFormValues, createSiteSchema } from '../schemas';

// React Hook Form types these fields as `number` because the schema requires
// one, but `defaultValues` legitimately starts them undefined. These helpers
// keep the inputs controlled without lying about it at every call site.
function toInputValue(value: number | undefined): number | string {
  return value ?? '';
}

function toSelectValue(value: number | undefined): number | null {
  return value ?? null;
}

export function CreateSiteForm() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const createSite = useCreateSite();
  const { data: users, isPending: usersPending } = useQuery(userPickerQueryOptions());

  const {
    control,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<CreateSiteFormValues>({
    resolver: zodResolver(createSiteSchema),
    // Coordinates start empty rather than at 0,0, which is a real place in the
    // Atlantic and would silently produce a plausible-looking forecast.
    defaultValues: { name: '', latitude: undefined, longitude: undefined, ownerId: undefined },
  });

  const onSubmit = (values: CreateSiteFormValues) => {
    if (createSite.isPending) return;

    createSite.mutate(values, {
      onSuccess: (site) => {
        toast.success(t('sites.created', { name: site.name }));
        void navigate({ to: '/admin/sites' });
      },
      onError: (error) => {
        setError('root', { message: translateError(error) });
      },
    });
  };

  return (
    <Card className="max-w-xl">
      <CardHeader>
        <CardTitle>{t('sites.create_title')}</CardTitle>
        <CardDescription>{t('sites.create_description')}</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <FieldGroup>
            <Controller
              control={control}
              name="name"
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="name">{t('sites.name')}</FieldLabel>
                  <Input {...field} id="name" aria-invalid={fieldState.invalid} />
                  {fieldState.error && (
                    <FieldError>{t(fieldState.error.message as ValidationKey)}</FieldError>
                  )}
                </Field>
              )}
            />

            <div className="grid gap-5 sm:grid-cols-2">
              <Controller
                control={control}
                name="latitude"
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="latitude">{t('sites.latitude')}</FieldLabel>
                    <Input
                      {...field}
                      value={toInputValue(field.value)}
                      onChange={(event) => {
                        const { value, valueAsNumber } = event.currentTarget;
                        field.onChange(value === '' ? undefined : valueAsNumber);
                      }}
                      id="latitude"
                      type="number"
                      step="any"
                      placeholder="50.0755"
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
                name="longitude"
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="longitude">{t('sites.longitude')}</FieldLabel>
                    <Input
                      {...field}
                      value={toInputValue(field.value)}
                      onChange={(event) => {
                        const { value, valueAsNumber } = event.currentTarget;
                        field.onChange(value === '' ? undefined : valueAsNumber);
                      }}
                      id="longitude"
                      type="number"
                      step="any"
                      placeholder="14.4378"
                      aria-invalid={fieldState.invalid}
                    />
                    {fieldState.error && (
                      <FieldError>{t(fieldState.error.message as ValidationKey)}</FieldError>
                    )}
                  </Field>
                )}
              />
            </div>

            <Controller
              control={control}
              name="ownerId"
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="ownerId">{t('sites.owner')}</FieldLabel>
                  <Select
                    value={toSelectValue(field.value)}
                    disabled={usersPending}
                    onValueChange={(ownerId) => {
                      if (ownerId !== null) {
                        field.onChange(ownerId);
                      }
                    }}
                  >
                    <SelectTrigger id="ownerId" className="w-full" onBlur={field.onBlur}>
                      <SelectValue placeholder={t('sites.select_owner')}>
                        {(ownerId: number | null) => {
                          const owner = users?.find((user) => user.id === ownerId);
                          return owner
                            ? `${owner.firstName} ${owner.lastName} (${owner.email})`
                            : t('sites.select_owner');
                        }}
                      </SelectValue>
                    </SelectTrigger>
                    <SelectContent>
                      {users?.map((user) => (
                        <SelectItem key={user.id} value={user.id}>
                          {`${user.firstName} ${user.lastName} (${user.email})`}
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
              <Button type="submit" disabled={createSite.isPending}>
                {createSite.isPending ? (
                  <Loader2Icon className="animate-spin" aria-hidden />
                ) : (
                  <MapPinPlusIcon />
                )}
                {createSite.isPending ? t('sites.submitting') : t('sites.submit')}
              </Button>
              <Button
                type="button"
                variant="outline"
                disabled={createSite.isPending}
                onClick={() => {
                  void navigate({ to: '/admin/sites' });
                }}
              >
                {t('sites.cancel')}
              </Button>
            </div>
          </FieldGroup>
        </form>
      </CardContent>
    </Card>
  );
}
