import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2Icon, SaveIcon } from 'lucide-react';
import { Controller, useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { toast } from 'sonner';

import { translateError } from '@/api/errors';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Field, FieldError, FieldGroup, FieldLabel } from '@/components/ui/field';
import { Input } from '@/components/ui/input';
import { numberFromInput, toInputValue } from '@/lib/form';
import type { ValidationKey } from '@/lib/i18n/keys';

import { type Site, useUpdateSite } from '../api';
import { type SiteDetailsFormValues, siteDetailsSchema } from '../schemas';

interface SiteDetailsFormProps {
  site: Site;
}

/** Name and coordinates. The coordinates pick the weather the forecasts are made from. */
export function SiteDetailsForm({ site }: SiteDetailsFormProps) {
  const { t } = useTranslation();
  const updateSite = useUpdateSite(site.id);

  const { control, handleSubmit, setError, formState } = useForm<SiteDetailsFormValues>({
    resolver: zodResolver(siteDetailsSchema),
    defaultValues: { name: site.name, latitude: site.latitude, longitude: site.longitude },
  });

  const onSubmit = (values: SiteDetailsFormValues) => {
    if (updateSite.isPending) return;

    updateSite.mutate(values, {
      onSuccess: (saved) => {
        toast.success(t('settings.details_saved', { name: saved.name }));
      },
      onError: (error) => {
        setError('root', { message: translateError(error) });
      },
    });
  };

  const coordinateField = (name: 'latitude' | 'longitude', placeholder: string) => (
    <Controller
      control={control}
      name={name}
      render={({ field, fieldState }) => (
        <Field data-invalid={fieldState.invalid}>
          <FieldLabel htmlFor={name}>{t(`sites.${name}`)}</FieldLabel>
          <Input
            {...field}
            value={toInputValue(field.value)}
            onChange={(event) => {
              field.onChange(numberFromInput(event));
            }}
            id={name}
            type="number"
            step="any"
            placeholder={placeholder}
            aria-invalid={fieldState.invalid}
          />
          {fieldState.error && (
            <FieldError>{t(fieldState.error.message as ValidationKey)}</FieldError>
          )}
        </Field>
      )}
    />
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('settings.details_title')}</CardTitle>
        <CardDescription>{t('settings.details_description')}</CardDescription>
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
              {coordinateField('latitude', '50.0755')}
              {coordinateField('longitude', '14.4378')}
            </div>

            {formState.errors.root && (
              <p role="alert" className="text-destructive text-sm">
                {formState.errors.root.message}
              </p>
            )}

            <div>
              <Button type="submit" disabled={updateSite.isPending}>
                {updateSite.isPending ? (
                  <Loader2Icon className="animate-spin" aria-hidden />
                ) : (
                  <SaveIcon />
                )}
                {t(updateSite.isPending ? 'settings.saving' : 'settings.save')}
              </Button>
            </div>
          </FieldGroup>
        </form>
      </CardContent>
    </Card>
  );
}
