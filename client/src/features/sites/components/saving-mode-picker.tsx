import { cn } from 'cn';
import { useTranslation } from 'react-i18next';
import { toast } from 'sonner';

import { translateError } from '@/api/errors';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { APPLIANCE_PRIORITIES } from '@/features/appliances/api';

import {
  SAVING_MODE_MAX_PRIORITY,
  SAVING_MODES,
  type SavingMode,
  type Site,
  useUpdateSite,
} from '../api';

interface SavingModePickerProps {
  site: Site;
}

/**
 * Saved as soon as a mode is picked: it is a single choice with nothing else to
 * fill in, and the forecast is rebuilt from it straight away.
 */
export function SavingModePicker({ site }: SavingModePickerProps) {
  const { t } = useTranslation();
  const updateSite = useUpdateSite(site.id);

  const choose = (mode: SavingMode) => {
    if (mode === site.savingMode || updateSite.isPending) return;

    updateSite.mutate(
      { savingMode: mode },
      {
        onSuccess: () => {
          toast.success(t('settings.saving_mode_saved', { mode: t(`saving_mode.${mode}`) }));
        },
        onError: (error) => {
          toast.error(translateError(error));
        },
      },
    );
  };

  // While saving, the choice already shows the mode being saved.
  const selected = updateSite.isPending ? updateSite.variables.savingMode : site.savingMode;

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('settings.saving_mode_title')}</CardTitle>
        <CardDescription>{t('settings.saving_mode_description')}</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        <fieldset className="grid gap-3 sm:grid-cols-2" disabled={updateSite.isPending}>
          <legend className="sr-only">{t('settings.saving_mode_title')}</legend>
          {SAVING_MODES.map((mode) => {
            const running = APPLIANCE_PRIORITIES.filter(
              (priority) => priority <= SAVING_MODE_MAX_PRIORITY[mode],
            );

            return (
              <label
                key={mode}
                className={cn(
                  'flex cursor-pointer flex-col gap-1 rounded-lg border p-4 transition-colors',
                  'has-focus-visible:ring-2 has-focus-visible:ring-ring',
                  selected === mode ? 'border-primary bg-primary/5' : 'hover:bg-muted/50',
                )}
              >
                <input
                  type="radio"
                  name="saving-mode"
                  value={mode}
                  checked={selected === mode}
                  onChange={() => {
                    choose(mode);
                  }}
                  className="sr-only"
                />
                <span className="font-medium">{t(`saving_mode.${mode}`)}</span>
                <span className="text-sm text-muted-foreground">
                  {t(`saving_mode.hint_${mode}`)}
                </span>
                <span className="text-xs text-muted-foreground">
                  {t('saving_mode.running', {
                    priorities: running
                      .map((priority) => t(`appliances.priority_${priority}`).toLowerCase())
                      .join(', '),
                  })}
                </span>
              </label>
            );
          })}
        </fieldset>
        <p className="text-xs text-muted-foreground">{t('settings.saving_mode_note')}</p>
      </CardContent>
    </Card>
  );
}
