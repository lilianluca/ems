import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2Icon, PlusIcon, SaveIcon, Trash2Icon } from 'lucide-react';
import { type Control, Controller, useFieldArray, useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { toast } from 'sonner';

import { translateError } from '@/api/errors';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Field, FieldDescription, FieldError, FieldGroup, FieldLabel } from '@/components/ui/field';
import { Input } from '@/components/ui/input';
import { numberFromInput, toInputValue } from '@/lib/form';
import type { ValidationKey } from '@/lib/i18n/keys';

import { type Site, useUpdateSite } from '../api';
import { type HouseFormValues, houseSchema } from '../schemas';

interface HouseFormProps {
  site: Site;
}

/** Lighting: on while someone is home and it is dark, see docs/vypocty/osvetleni.md. */
export function HouseForm({ site }: HouseFormProps) {
  const { t } = useTranslation();
  const updateSite = useUpdateSite(site.id);

  const { control, handleSubmit, setError, formState } = useForm<HouseFormValues>({
    resolver: zodResolver(houseSchema),
    defaultValues: {
      lightingPowerW: site.lightingPowerW,
      occupancyWindows: site.occupancyWindows,
    },
  });
  const { fields, append, remove } = useFieldArray({ control, name: 'occupancyWindows' });

  const onSubmit = (values: HouseFormValues) => {
    if (updateSite.isPending) return;

    updateSite.mutate(values, {
      onSuccess: () => {
        toast.success(t('settings.house_saved'));
      },
      onError: (error) => {
        setError('root', { message: translateError(error) });
      },
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('settings.house_title')}</CardTitle>
        <CardDescription>{t('settings.house_description')}</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <FieldGroup>
            <Controller
              control={control}
              name="lightingPowerW"
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="lightingPowerW">{t('settings.lighting_power')}</FieldLabel>
                  <Input
                    {...field}
                    value={toInputValue(field.value)}
                    onChange={(event) => {
                      field.onChange(numberFromInput(event));
                    }}
                    id="lightingPowerW"
                    type="number"
                    step="1"
                    min="0"
                    placeholder="150"
                    className="sm:max-w-60"
                    aria-invalid={fieldState.invalid}
                  />
                  <FieldDescription>{t('settings.lighting_power_hint')}</FieldDescription>
                  {fieldState.error && (
                    <FieldError>{t(fieldState.error.message as ValidationKey)}</FieldError>
                  )}
                </Field>
              )}
            />

            <div className="flex flex-col gap-3">
              <div>
                <p className="text-sm font-medium">{t('settings.occupancy')}</p>
                <p className="text-xs text-muted-foreground">{t('settings.occupancy_hint')}</p>
              </div>

              {fields.map((field, index) => (
                <div
                  key={field.id}
                  className="grid grid-cols-[1fr_1fr_auto] items-start gap-3 rounded-lg border p-3 sm:max-w-md"
                >
                  <HourField
                    control={control}
                    index={index}
                    name="startHour"
                    label={t('appliances.window_from')}
                  />
                  <HourField
                    control={control}
                    index={index}
                    name="endHour"
                    label={t('appliances.window_to')}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon-sm"
                    aria-label={t('appliances.remove_window')}
                    className="mt-6"
                    onClick={() => {
                      remove(index);
                    }}
                  >
                    <Trash2Icon />
                  </Button>
                </div>
              ))}

              <Button
                type="button"
                variant="outline"
                size="sm"
                className="w-fit"
                onClick={() => {
                  append({ startHour: 17, endHour: 22 });
                }}
              >
                <PlusIcon />
                {t('appliances.add_window')}
              </Button>
            </div>

            {formState.errors.root && (
              <p role="alert" className="text-sm text-destructive">
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

interface HourFieldProps {
  control: Control<HouseFormValues>;
  index: number;
  name: 'startHour' | 'endHour';
  label: string;
}

function HourField({ control, index, name, label }: HourFieldProps) {
  const { t } = useTranslation();

  return (
    <Controller
      control={control}
      name={`occupancyWindows.${index}.${name}` as const}
      render={({ field, fieldState }) => (
        <Field data-invalid={fieldState.invalid}>
          <FieldLabel className="text-xs">{label}</FieldLabel>
          <Input
            {...field}
            value={toInputValue(field.value)}
            onChange={(event) => {
              field.onChange(numberFromInput(event));
            }}
            type="number"
            step="1"
            min="0"
            max="23"
            aria-invalid={fieldState.invalid}
          />
          {fieldState.error && (
            <FieldError>{t(fieldState.error.message as ValidationKey)}</FieldError>
          )}
        </Field>
      )}
    />
  );
}
