import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate } from '@tanstack/react-router';
import { Loader2Icon, SaveIcon } from 'lucide-react';
import { Controller, useForm, useWatch } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { toast } from 'sonner';

import { translateError } from '@/api/errors';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Field, FieldError, FieldGroup, FieldLabel } from '@/components/ui/field';
import { Input } from '@/components/ui/input';
import { numberFromInput, toInputValue } from '@/lib/form';
import type { ValidationKey } from '@/lib/i18n/keys';

import { type PVDevice, useCreatePVDevice, useUpdatePVDevice } from '../api';
import { compassPoint } from '../compass';
import { type PVDeviceFormValues, pvDeviceSchema } from '../schemas';

interface PVDeviceFormProps {
  siteId: number;
  device?: PVDevice;
}

export function PVDeviceForm({ siteId, device }: PVDeviceFormProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const createDevice = useCreatePVDevice(siteId);
  const updateDevice = useUpdatePVDevice(siteId, device?.id ?? 0);
  const mutation = device ? updateDevice : createDevice;

  const { control, handleSubmit, setError, formState } = useForm<PVDeviceFormValues>({
    resolver: zodResolver(pvDeviceSchema),
    defaultValues: device
      ? {
          name: device.name,
          installedPowerKwp: device.installedPowerKwp,
          inverterPowerKw: device.inverterPowerKw,
          tiltDegrees: device.tiltDegrees,
          azimuthDegrees: device.azimuthDegrees,
        }
      : {
          name: '',
          installedPowerKwp: undefined,
          inverterPowerKw: undefined,
          tiltDegrees: undefined,
          azimuthDegrees: undefined,
        },
  });

  const azimuth = useWatch({ control, name: 'azimuthDegrees' });

  const onSubmit = (values: PVDeviceFormValues) => {
    if (mutation.isPending) return;

    mutation.mutate(values, {
      onSuccess: (saved) => {
        toast.success(t(device ? 'devices.updated' : 'devices.created', { name: saved.name }));
        void navigate({ to: '/sites/$siteId/devices', params: { siteId } });
      },
      onError: (error) => {
        setError('root', { message: translateError(error) });
      },
    });
  };

  return (
    <Card className="max-w-xl">
      <CardHeader>
        <CardTitle>{t(device ? 'devices.pv_edit_title' : 'devices.pv_create_title')}</CardTitle>
        <CardDescription>{t('devices.pv_description')}</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <FieldGroup>
            <Controller
              control={control}
              name="name"
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="name">{t('devices.name')}</FieldLabel>
                  <Input
                    {...field}
                    id="name"
                    placeholder={t('devices.pv_name_placeholder')}
                    aria-invalid={fieldState.invalid}
                  />
                  {fieldState.error && (
                    <FieldError>{t(fieldState.error.message as ValidationKey)}</FieldError>
                  )}
                </Field>
              )}
            />

            <div className="grid gap-5 sm:grid-cols-2">
              <Controller
                control={control}
                name="installedPowerKwp"
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="installedPowerKwp">
                      {t('devices.installed_power')}
                    </FieldLabel>
                    <Input
                      {...field}
                      value={toInputValue(field.value)}
                      onChange={(event) => {
                        field.onChange(numberFromInput(event));
                      }}
                      id="installedPowerKwp"
                      type="number"
                      step="any"
                      placeholder="9.8"
                      aria-invalid={fieldState.invalid}
                    />
                    <p className="text-muted-foreground text-xs">{t('devices.hint_kwp')}</p>
                    {fieldState.error && (
                      <FieldError>{t(fieldState.error.message as ValidationKey)}</FieldError>
                    )}
                  </Field>
                )}
              />

              <Controller
                control={control}
                name="inverterPowerKw"
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="inverterPowerKw">{t('devices.inverter_power')}</FieldLabel>
                    <Input
                      {...field}
                      value={toInputValue(field.value)}
                      onChange={(event) => {
                        field.onChange(numberFromInput(event));
                      }}
                      id="inverterPowerKw"
                      type="number"
                      step="any"
                      placeholder="8"
                      aria-invalid={fieldState.invalid}
                    />
                    <p className="text-muted-foreground text-xs">{t('devices.hint_inverter')}</p>
                    {fieldState.error && (
                      <FieldError>{t(fieldState.error.message as ValidationKey)}</FieldError>
                    )}
                  </Field>
                )}
              />

              <Controller
                control={control}
                name="tiltDegrees"
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="tiltDegrees">{t('devices.tilt')}</FieldLabel>
                    <Input
                      {...field}
                      value={toInputValue(field.value)}
                      onChange={(event) => {
                        field.onChange(numberFromInput(event));
                      }}
                      id="tiltDegrees"
                      type="number"
                      step="any"
                      placeholder="35"
                      aria-invalid={fieldState.invalid}
                    />
                    <p className="text-muted-foreground text-xs">{t('devices.hint_tilt')}</p>
                    {fieldState.error && (
                      <FieldError>{t(fieldState.error.message as ValidationKey)}</FieldError>
                    )}
                  </Field>
                )}
              />

              <Controller
                control={control}
                name="azimuthDegrees"
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="azimuthDegrees">{t('devices.azimuth')}</FieldLabel>
                    <Input
                      {...field}
                      value={toInputValue(field.value)}
                      onChange={(event) => {
                        field.onChange(numberFromInput(event));
                      }}
                      id="azimuthDegrees"
                      type="number"
                      step="any"
                      placeholder="180"
                      aria-invalid={fieldState.invalid}
                    />
                    {/* Reads the entered angle back as a compass direction: this is
                        the field where a wrong convention produces a plausible but
                        completely wrong forecast. */}
                    <p className="text-muted-foreground text-xs">
                      {t('devices.hint_azimuth')}
                      {typeof azimuth === 'number' && !Number.isNaN(azimuth) && (
                        <>
                          {' · '}
                          <span className="text-foreground font-medium">
                            {t(`devices.compass_${compassPoint(azimuth)}`)}
                          </span>
                        </>
                      )}
                    </p>
                    {fieldState.error && (
                      <FieldError>{t(fieldState.error.message as ValidationKey)}</FieldError>
                    )}
                  </Field>
                )}
              />
            </div>

            {formState.errors.root && (
              <p role="alert" className="text-destructive text-sm">
                {formState.errors.root.message}
              </p>
            )}

            <div className="flex gap-2">
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending ? (
                  <Loader2Icon className="animate-spin" aria-hidden />
                ) : (
                  <SaveIcon />
                )}
                {t(mutation.isPending ? 'devices.submitting' : 'devices.submit')}
              </Button>
              <Button
                type="button"
                variant="outline"
                disabled={mutation.isPending}
                onClick={() => {
                  void navigate({ to: '/sites/$siteId/devices', params: { siteId } });
                }}
              >
                {t('devices.cancel')}
              </Button>
            </div>
          </FieldGroup>
        </form>
      </CardContent>
    </Card>
  );
}
