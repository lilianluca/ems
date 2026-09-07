import { PlusIcon, Trash2Icon } from 'lucide-react';
import { type Control, Controller, useFieldArray } from 'react-hook-form';
import { useTranslation } from 'react-i18next';

import { Button } from '@/components/ui/button';
import { Field, FieldError, FieldLabel } from '@/components/ui/field';
import { Input } from '@/components/ui/input';
import { numberFromInput, toInputValue } from '@/lib/form';
import type { ValidationKey } from '@/lib/i18n/keys';

import { emptyTimeWindow } from '../mapping';
import type { ApplianceFormValues } from '../schemas';

interface TimeWindowsFieldProps {
  control: Control<ApplianceFormValues>;
  /** Message for the array itself, e.g. "at least one window is required". */
  error?: string;
}

export function TimeWindowsField({ control, error }: TimeWindowsFieldProps) {
  const { t } = useTranslation();
  const { fields, append, remove } = useFieldArray({ control, name: 'windows' });

  return (
    <div className="flex flex-col gap-3">
      <div>
        <p className="text-sm font-medium">{t('appliances.windows')}</p>
        {/* The forecast spreads the expected runtime across the window rather
            than placing it at one moment, which is worth saying out loud. */}
        <p className="text-muted-foreground text-xs">{t('appliances.hint_windows')}</p>
      </div>

      {fields.map((field, index) => (
        <div
          key={field.id}
          className="grid items-start gap-3 rounded-lg border p-3 sm:grid-cols-[repeat(5,1fr)_auto]"
        >
          <WindowNumber
            control={control}
            index={index}
            name="startHour"
            label={t('appliances.window_from')}
          />
          <WindowNumber
            control={control}
            index={index}
            name="endHour"
            label={t('appliances.window_to')}
          />
          <WindowNumber
            control={control}
            index={index}
            name="probabilityPercent"
            label={t('appliances.window_probability')}
          />
          <WindowNumber
            control={control}
            index={index}
            name="durationMinutesMin"
            label={t('appliances.window_duration_min')}
          />
          <WindowNumber
            control={control}
            index={index}
            name="durationMinutesMax"
            label={t('appliances.window_duration_max')}
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

      {error && (
        <p role="alert" className="text-destructive text-sm">
          {error}
        </p>
      )}

      <Button
        type="button"
        variant="outline"
        size="sm"
        className="w-fit"
        onClick={() => {
          append(emptyTimeWindow());
        }}
      >
        <PlusIcon />
        {t('appliances.add_window')}
      </Button>
    </div>
  );
}

interface WindowNumberProps {
  control: Control<ApplianceFormValues>;
  index: number;
  name:
    'startHour' | 'endHour' | 'probabilityPercent' | 'durationMinutesMin' | 'durationMinutesMax';
  label: string;
}

function WindowNumber({ control, index, name, label }: WindowNumberProps) {
  const { t } = useTranslation();

  return (
    <Controller
      control={control}
      name={`windows.${index}.${name}` as const}
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
