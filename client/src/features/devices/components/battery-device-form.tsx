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

import { type BatteryDevice, useCreateBatteryDevice, useUpdateBatteryDevice } from '../api';
import { type BatteryDeviceFormValues, batteryDeviceSchema } from '../schemas';

interface BatteryDeviceFormProps {
  siteId: number;
  device?: BatteryDevice;
}

/** Percentages in the form, fractions on the wire. */
const toPercent = (fraction: number) => Math.round(fraction * 1000) / 10;
const toFraction = (percent: number) => percent / 100;

export function BatteryDeviceForm({ siteId, device }: BatteryDeviceFormProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const createDevice = useCreateBatteryDevice(siteId);
  const updateDevice = useUpdateBatteryDevice(siteId, device?.id ?? 0);
  const mutation = device ? updateDevice : createDevice;

  const { control, handleSubmit, setError, formState } = useForm<BatteryDeviceFormValues>({
    resolver: zodResolver(batteryDeviceSchema),
    defaultValues: device
      ? {
          name: device.name,
          capacityKwh: device.capacityKwh,
          maxChargePowerKw: device.maxChargePowerKw,
          maxDischargePowerKw: device.maxDischargePowerKw,
          minStateOfChargePercent: toPercent(device.minStateOfCharge),
          maxStateOfChargePercent: toPercent(device.maxStateOfCharge),
          roundTripEfficiencyPercent: toPercent(device.roundTripEfficiency),
        }
      : {
          name: '',
          capacityKwh: undefined,
          maxChargePowerKw: undefined,
          maxDischargePowerKw: undefined,
          // Plausible defaults for a home battery — they belong on the datasheet,
          // not in this form, so they are a starting point rather than a truth.
          minStateOfChargePercent: 10,
          maxStateOfChargePercent: 100,
          roundTripEfficiencyPercent: 90,
        },
  });

  const onSubmit = (values: BatteryDeviceFormValues) => {
    if (mutation.isPending) return;

    mutation.mutate(
      {
        name: values.name,
        capacityKwh: values.capacityKwh,
        maxChargePowerKw: values.maxChargePowerKw,
        maxDischargePowerKw: values.maxDischargePowerKw,
        minStateOfCharge: toFraction(values.minStateOfChargePercent),
        maxStateOfCharge: toFraction(values.maxStateOfChargePercent),
        roundTripEfficiency: toFraction(values.roundTripEfficiencyPercent),
      },
      {
        onSuccess: (saved) => {
          toast.success(t(device ? 'devices.updated' : 'devices.created', { name: saved.name }));
          void navigate({ to: '/sites/$siteId/devices', params: { siteId } });
        },
        onError: (error) => {
          setError('root', { message: translateError(error) });
        },
      },
    );
  };

  const numericField = (
    name: 'capacityKwh' | 'maxChargePowerKw' | 'maxDischargePowerKw',
    label: string,
    unit: string,
    placeholder: string,
  ) => (
    <Controller
      control={control}
      name={name}
      render={({ field, fieldState }) => (
        <Field data-invalid={fieldState.invalid}>
          <FieldLabel htmlFor={name}>
            {label} <span className="text-muted-foreground font-normal">({unit})</span>
          </FieldLabel>
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

  const percentField = (
    name: 'minStateOfChargePercent' | 'maxStateOfChargePercent' | 'roundTripEfficiencyPercent',
    label: string,
    hint?: string,
  ) => (
    <Controller
      control={control}
      name={name}
      render={({ field, fieldState }) => (
        <Field data-invalid={fieldState.invalid}>
          <FieldLabel htmlFor={name}>
            {label} <span className="text-muted-foreground font-normal">(%)</span>
          </FieldLabel>
          <Input
            {...field}
            value={toInputValue(field.value)}
            onChange={(event) => {
              field.onChange(numberFromInput(event));
            }}
            id={name}
            type="number"
            step="any"
            aria-invalid={fieldState.invalid}
          />
          {hint && <p className="text-muted-foreground text-xs">{hint}</p>}
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
          {t(device ? 'devices.battery_edit_title' : 'devices.battery_create_title')}
        </CardTitle>
        <CardDescription>{t('devices.battery_description')}</CardDescription>
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
                    placeholder={t('devices.battery_name_placeholder')}
                    aria-invalid={fieldState.invalid}
                  />
                  {fieldState.error && (
                    <FieldError>{t(fieldState.error.message as ValidationKey)}</FieldError>
                  )}
                </Field>
              )}
            />

            {/* Capacity is energy, the two limits are power — different units that
                are easy to confuse, so each label carries its own. */}
            <div className="grid gap-5 sm:grid-cols-3">
              {numericField('capacityKwh', t('devices.capacity'), 'kWh', '10')}
              {numericField('maxChargePowerKw', t('devices.max_charge_power'), 'kW', '5')}
              {numericField('maxDischargePowerKw', t('devices.max_discharge_power'), 'kW', '5')}
            </div>

            <div className="grid gap-5 sm:grid-cols-3">
              {percentField('minStateOfChargePercent', t('devices.min_soc'))}
              {percentField('maxStateOfChargePercent', t('devices.max_soc'))}
              {percentField('roundTripEfficiencyPercent', t('devices.efficiency'))}
            </div>
            <p className="text-muted-foreground text-xs">{t('devices.hint_soc')}</p>

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
