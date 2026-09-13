import { useTranslation } from 'react-i18next';

import { translateError } from '@/api/errors';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { useNow } from '@/hooks/use-now';
import { formatPragueDateTime, STEP_DURATION_MS } from '@/lib/datetime';
import { formatFractionAsPercent, formatQuantity, formatWithUnit } from '@/lib/units';
import { cn } from '@/lib/utils';

import { type BatteryDevice, useBatteryState, useDevices } from '../api';

const NOW_REFRESH_MS = 60_000;

/**
 * A state is recorded once a step, so one older than two steps means whatever
 * records it has missed a run. It is still shown, because a flagged value is
 * more useful than none, but it may no longer describe the battery.
 */
const STALE_AFTER_MS = 2 * STEP_DURATION_MS;

interface BatteryStateCardsProps {
  siteId: number;
}

/**
 * One card per battery. A site without one renders nothing: the plan below
 * already says why there is nothing to schedule.
 */
export function BatteryStateCards({ siteId }: BatteryStateCardsProps) {
  const { data: devices } = useDevices(siteId);
  const batteries =
    devices?.filter((device): device is BatteryDevice => device.type === 'battery') ?? [];

  return (
    <>
      {batteries.map((battery) => (
        <BatteryStateCard key={battery.id} siteId={siteId} battery={battery} />
      ))}
    </>
  );
}

interface BatteryStateCardProps {
  siteId: number;
  battery: BatteryDevice;
}

function BatteryStateCard({ siteId, battery }: BatteryStateCardProps) {
  const { t, i18n } = useTranslation();
  const { data: state, isPending, error } = useBatteryState(siteId, battery.id);
  const now = useNow(NOW_REFRESH_MS);

  const measuredAt = state ? new Date(state.measuredAt).getTime() : null;
  const isStale = measuredAt !== null && now - measuredAt > STALE_AFTER_MS;

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('battery_state.title')}</CardTitle>
        <CardDescription>{t('battery_state.description', { name: battery.name })}</CardDescription>
      </CardHeader>

      <CardContent>
        {isPending && <Skeleton className="h-24 w-full" />}

        {error && <p className="text-muted-foreground py-6 text-center">{translateError(error)}</p>}

        {!isPending && !error && state === null && (
          <p className="text-muted-foreground py-6 text-center">{t('battery_state.empty')}</p>
        )}

        {state && measuredAt !== null && (
          <div className="flex flex-col gap-3">
            <div className="flex flex-wrap items-baseline gap-x-8 gap-y-2">
              <div>
                <p className="text-muted-foreground text-xs">
                  {t('battery_state.state_of_charge')}
                </p>
                <p className="text-2xl font-semibold tabular-nums">
                  {formatFractionAsPercent(state.stateOfCharge, i18n.language)}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground text-xs">{t('battery_state.stored_energy')}</p>
                <p className="tabular-nums">
                  {formatQuantity(state.stateOfChargeKwh, 'energy', i18n.language)} /{' '}
                  {formatWithUnit(battery.capacityKwh, 'energy', i18n.language)}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground text-xs">{t('devices.usable_range')}</p>
                <p className="tabular-nums">
                  {formatFractionAsPercent(battery.minStateOfCharge, i18n.language)} –{' '}
                  {formatFractionAsPercent(battery.maxStateOfCharge, i18n.language)}
                </p>
              </div>
            </div>

            <ChargeMeter
              stateOfCharge={state.stateOfCharge}
              minStateOfCharge={battery.minStateOfCharge}
              maxStateOfCharge={battery.maxStateOfCharge}
              label={t('battery_state.meter_label', { name: battery.name })}
            />

            <p className={cn('text-xs', isStale ? 'text-destructive' : 'text-muted-foreground')}>
              {t(isStale ? 'battery_state.stale' : 'battery_state.measured_at', {
                time: formatPragueDateTime(measuredAt, i18n.language),
              })}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

interface ChargeMeterProps {
  stateOfCharge: number;
  minStateOfCharge: number;
  maxStateOfCharge: number;
  label: string;
}

/**
 * The fill is drawn against the whole capacity, with the usable bounds marked,
 * because that is how the number relates to what the optimiser may use: 15 %
 * reads as nearly empty only once you see that the floor sits at 10 %.
 */
function ChargeMeter({
  stateOfCharge,
  minStateOfCharge,
  maxStateOfCharge,
  label,
}: ChargeMeterProps) {
  const percent = (fraction: number) => `${Math.min(Math.max(fraction, 0), 1) * 100}%`;

  return (
    <div
      role="meter"
      aria-label={label}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(stateOfCharge * 100)}
      className="bg-muted relative h-3 w-full overflow-hidden rounded-full"
    >
      <div
        className="absolute inset-y-0 left-0"
        style={{ width: percent(stateOfCharge), background: 'var(--chart-3)' }}
      />
      <div
        className="bg-foreground/60 absolute inset-y-0 w-px"
        style={{ left: percent(minStateOfCharge) }}
      />
      <div
        className="bg-foreground/60 absolute inset-y-0 w-px"
        style={{ left: percent(maxStateOfCharge) }}
      />
    </div>
  );
}
