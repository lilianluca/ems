import { Loader2Icon, RefreshCwIcon } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { toast } from 'sonner';

import { translateError } from '@/api/errors';
import { Button } from '@/components/ui/button';

import { useRefreshForecasts } from '../api';

interface RefreshForecastsButtonProps {
  siteId: number;
}

/**
 * The escape hatch for the hourly jobs, which leave gaps a user can see: right
 * after a restart, and between adding a PV array and the next scheduled run.
 */
export function RefreshForecastsButton({ siteId }: RefreshForecastsButtonProps) {
  const { t } = useTranslation();
  const refresh = useRefreshForecasts(siteId);

  const onClick = () => {
    refresh.mutate(undefined, {
      onSuccess: (result) => {
        // A site with no PV array gets a consumption forecast and nothing else.
        // That is the correct answer rather than a half-failure, and saying so
        // matters: otherwise the empty generation line reads as a bug.
        toast.success(
          result.pvDeviceCount === 0
            ? t('forecasts.refreshed_without_pv')
            : t('forecasts.refreshed', {
                generation: result.pvGenerationPoints,
                consumption: result.loadPoints,
              }),
        );
      },
      onError: (error) => {
        toast.error(translateError(error));
      },
    });
  };

  return (
    <Button
      variant="ghost"
      size="icon-sm"
      aria-label={t('forecasts.refresh')}
      disabled={refresh.isPending}
      onClick={onClick}
    >
      {refresh.isPending ? <Loader2Icon className="animate-spin" aria-hidden /> : <RefreshCwIcon />}
    </Button>
  );
}
