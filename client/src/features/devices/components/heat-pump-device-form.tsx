import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate } from '@tanstack/react-router';
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

import { type HeatPumpDevice, useCreateHeatPumpDevice, useUpdateHeatPumpDevice } from '../api';
import { type HeatPumpDeviceFormValues, heatPumpDeviceSchema } from '../schemas';

interface HeatPumpDeviceFormProps {
  siteId: number;
  device?: HeatPumpDevice;
}

export function HeatPumpDeviceForm({ siteId, device }: HeatPumpDeviceFormProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const createDevice = useCreateHeatPumpDevice(siteId);
  const updateDevice = useUpdateHeatPumpDevice(siteId, device?.id ?? 0);
  const mutation = device ? updateDevice : createDevice;

  const { control, handleSubmit, setError, formState } = useForm<HeatPumpDeviceFormValues>({
    resolver: zodResolver(heatPumpDeviceSchema),
    defaultValues: device
      ? {
          name: device.name,
          copAtMinus7C: device.copAtMinus7C,
          copAt2C: device.copAt2C,
          copAt7C: device.copAt7C,
          copAt12C: device.copAt12C,
          maxHeatPowerKw: device.maxHeatPowerKw,
        }
      : {
          name: '',
          copAtMinus7C: undefined,
          copAt2C: undefined,
          copAt7C: undefined,
          copAt12C: undefined,
          maxHeatPowerKw: undefined,
        },
  });

  const onSubmit = (values: HeatPumpDeviceFormValues) => {
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

  const numericField = (
    name: 'copAtMinus7C' | 'copAt2C' | 'copAt7C' | 'copAt12C' | 'maxHeatPowerKw',
    label: string,
    placeholder: string,
  ) => (
    <Controller
      control={control}
      name={name}
      render={({ field, fieldState }) => (
        <Field data-invalid={fieldState.invalid}>
          <FieldLabel htmlFor={name}>{label}</FieldLabel>
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
    <Card className="max-w-xl">
      <CardHeader>
        <CardTitle>
          {t(device ? 'devices.heat_pump_edit_title' : 'devices.heat_pump_create_title')}
        </CardTitle>
        <CardDescription>{t('devices.heat_pump_description')}</CardDescription>
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
                    placeholder={t('devices.heat_pump_name_placeholder')}
                    aria-invalid={fieldState.invalid}
                  />
                  {fieldState.error && (
                    <FieldError>{t(fieldState.error.message as ValidationKey)}</FieldError>
                  )}
                </Field>
              )}
            />

            <div className="flex flex-col gap-3">
              <div className="grid gap-5 sm:grid-cols-4">
                {numericField('copAtMinus7C', t('devices.cop_at_minus_7'), '2.5')}
                {numericField('copAt2C', t('devices.cop_at_2'), '4.1')}
                {numericField('copAt7C', t('devices.cop_at_7'), '4.9')}
                {numericField('copAt12C', t('devices.cop_at_12'), '6.3')}
              </div>
              <p className="text-xs text-muted-foreground">{t('devices.hint_cop')}</p>
            </div>

            <div className="flex flex-col gap-3">
              {numericField('maxHeatPowerKw', `${t('devices.max_heat_power')} (kW)`, '2.3')}
              <p className="text-xs text-muted-foreground">{t('devices.hint_max_heat_power')}</p>
            </div>

            {formState.errors.root && (
              <p role="alert" className="text-sm text-destructive">
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
