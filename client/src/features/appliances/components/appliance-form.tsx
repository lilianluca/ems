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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { numberFromInput, toInputValue } from '@/lib/form';
import type { ValidationKey } from '@/lib/i18n/keys';

import {
  type Appliance,
  APPLIANCE_BEHAVIORS,
  type ApplianceBehavior,
  useCreateAppliance,
  useUpdateAppliance,
} from '../api';
import { toApplianceInput, toFormValues } from '../mapping';
import { type ApplianceFormValues, applianceSchema } from '../schemas';
import { TimeWindowsField } from './time-windows-field';

interface ApplianceFormProps {
  siteId: number;
  appliance?: Appliance;
}

export function ApplianceForm({ siteId, appliance }: ApplianceFormProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const createAppliance = useCreateAppliance(siteId);
  const updateAppliance = useUpdateAppliance(siteId, appliance?.id ?? 0);
  const mutation = appliance ? updateAppliance : createAppliance;

  const { control, handleSubmit, setError, formState } = useForm<ApplianceFormValues>({
    resolver: zodResolver(applianceSchema),
    defaultValues: appliance
      ? toFormValues(appliance)
      : {
          name: '',
          powerW: undefined,
          standbyPowerW: 0,
          priority: 1,
          isShiftable: false,
          behavior: 'constant',
          windows: [],
        },
  });

  const behavior = useWatch({ control, name: 'behavior' });
  const powerW = useWatch({ control, name: 'powerW' });
  const isWindowed = behavior === 'scheduled' || behavior === 'on_demand';

  const onSubmit = (values: ApplianceFormValues) => {
    if (mutation.isPending) return;

    mutation.mutate(toApplianceInput(values), {
      onSuccess: (saved) => {
        toast.success(
          t(appliance ? 'appliances.updated' : 'appliances.created', { name: saved.name }),
        );
        void navigate({ to: '/sites/$siteId/appliances', params: { siteId } });
      },
      onError: (error) => {
        setError('root', { message: translateError(error) });
      },
    });
  };

  const numberField = (
    name: 'powerW' | 'standbyPowerW' | 'maxUsesPerWindow',
    label: string,
    unit?: string,
    hint?: string,
  ) => (
    <Controller
      control={control}
      name={name}
      render={({ field, fieldState }) => (
        <Field data-invalid={fieldState.invalid}>
          <FieldLabel htmlFor={name}>
            {label} {unit && <span className="text-muted-foreground font-normal">({unit})</span>}
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

  const cycleField = (
    name: 'activeMinutesMin' | 'activeMinutesMax' | 'standbyMinutesMin' | 'standbyMinutesMax',
    label: string,
  ) => (
    <Controller
      control={control}
      name={name}
      render={({ field, fieldState }) => (
        <Field data-invalid={fieldState.invalid}>
          <FieldLabel htmlFor={name} className="text-xs">
            {label}
          </FieldLabel>
          <Input
            {...field}
            value={toInputValue(field.value)}
            onChange={(event) => {
              field.onChange(numberFromInput(event));
            }}
            id={name}
            type="number"
            step="1"
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
    <Card className="max-w-3xl">
      <CardHeader>
        <CardTitle>{t(appliance ? 'appliances.edit_title' : 'appliances.create_title')}</CardTitle>
        <CardDescription>{t('appliances.form_description')}</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <FieldGroup>
            <Controller
              control={control}
              name="name"
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="name">{t('appliances.name')}</FieldLabel>
                  <Input
                    {...field}
                    id="name"
                    placeholder={t('appliances.name_placeholder')}
                    aria-invalid={fieldState.invalid}
                  />
                  {fieldState.error && (
                    <FieldError>{t(fieldState.error.message as ValidationKey)}</FieldError>
                  )}
                </Field>
              )}
            />

            <div className="grid gap-5 sm:grid-cols-2">
              {/* Watts, unlike every other power in this app — the live conversion
                  below is there so a value meant as kW is obvious immediately. */}
              {numberField(
                'powerW',
                t('appliances.power'),
                'W',
                typeof powerW === 'number' && !Number.isNaN(powerW)
                  ? t('appliances.hint_power', { kw: (powerW / 1000).toFixed(3) })
                  : t('appliances.hint_power_empty'),
              )}
              {numberField('standbyPowerW', t('appliances.standby_power'), 'W')}
            </div>

            <Controller
              control={control}
              name="behavior"
              render={({ field }) => (
                <Field>
                  <FieldLabel htmlFor="behavior">{t('appliances.behavior')}</FieldLabel>
                  <Select
                    value={field.value}
                    onValueChange={(value) => {
                      if (value !== null) field.onChange(value);
                    }}
                  >
                    <SelectTrigger id="behavior" className="w-full" onBlur={field.onBlur}>
                      <SelectValue>
                        {(value: ApplianceBehavior) => t(`appliances.behavior_${value}`)}
                      </SelectValue>
                    </SelectTrigger>
                    <SelectContent>
                      {APPLIANCE_BEHAVIORS.map((option) => (
                        <SelectItem key={option} value={option}>
                          {t(`appliances.behavior_${option}`)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <p className="text-muted-foreground text-xs">
                    {t(`appliances.behavior_hint_${behavior}`)}
                  </p>
                </Field>
              )}
            />

            {behavior === 'cyclic' && (
              <div className="grid gap-3 rounded-lg border p-3 sm:grid-cols-4">
                {cycleField('activeMinutesMin', t('appliances.active_min'))}
                {cycleField('activeMinutesMax', t('appliances.active_max'))}
                {cycleField('standbyMinutesMin', t('appliances.standby_min'))}
                {cycleField('standbyMinutesMax', t('appliances.standby_max'))}
              </div>
            )}

            {isWindowed && (
              <TimeWindowsField
                control={control}
                error={
                  formState.errors.windows?.message
                    ? t(formState.errors.windows.message as ValidationKey)
                    : undefined
                }
              />
            )}

            {behavior === 'on_demand' && (
              <div className="sm:max-w-xs">
                {numberField('maxUsesPerWindow', t('appliances.max_uses'))}
              </div>
            )}

            {/* Neither field reaches the forecast yet; both are inputs the
                optimisation will need, so they are labelled as such. */}
            <div className="grid gap-5 sm:grid-cols-2">
              <Controller
                control={control}
                name="priority"
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="priority">{t('appliances.priority')}</FieldLabel>
                    <Input
                      {...field}
                      value={toInputValue(field.value)}
                      onChange={(event) => {
                        field.onChange(numberFromInput(event));
                      }}
                      id="priority"
                      type="number"
                      min={1}
                      max={4}
                      step="1"
                      aria-invalid={fieldState.invalid}
                    />
                    <p className="text-muted-foreground text-xs">
                      {t('appliances.hint_future_use')}
                    </p>
                    {fieldState.error && (
                      <FieldError>{t(fieldState.error.message as ValidationKey)}</FieldError>
                    )}
                  </Field>
                )}
              />

              <Controller
                control={control}
                name="isShiftable"
                render={({ field }) => (
                  <Field>
                    <FieldLabel htmlFor="isShiftable">{t('appliances.shiftable')}</FieldLabel>
                    <Switch
                      id="isShiftable"
                      checked={field.value}
                      onCheckedChange={(checked) => {
                        field.onChange(checked);
                      }}
                    />
                    <p className="text-muted-foreground text-xs">
                      {t('appliances.hint_future_use')}
                    </p>
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
                {t(mutation.isPending ? 'appliances.submitting' : 'appliances.submit')}
              </Button>
              <Button
                type="button"
                variant="outline"
                disabled={mutation.isPending}
                onClick={() => {
                  void navigate({ to: '/sites/$siteId/appliances', params: { siteId } });
                }}
              >
                {t('appliances.cancel')}
              </Button>
            </div>
          </FieldGroup>
        </form>
      </CardContent>
    </Card>
  );
}
