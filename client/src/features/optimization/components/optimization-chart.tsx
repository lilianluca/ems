import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Area, AreaChart, CartesianGrid, ReferenceLine, XAxis, YAxis } from 'recharts';

import { translateError } from '@/api/errors';
import { dayBands, nowLine, useTimeAxis } from '@/components/chart/time-axis';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  type ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from '@/components/ui/chart';
import { Skeleton } from '@/components/ui/skeleton';
import { useNow } from '@/hooks/use-now';
import { formatPragueTime } from '@/lib/datetime';
import { formatMoney, formatQuantity, UNIT } from '@/lib/units';

import { type OptimizationStep, useOptimizationPlan } from '../api';

const NOW_REFRESH_MS = 60_000;
const STEP_DURATION_MS = 60 * 60_000;

interface ChartPoint {
  timestamp: number;
  /** Positive when the battery supplies the house, negative when it absorbs. */
  batteryKw: number;
  stateOfChargeKwh: number;
}

interface OptimizationChartProps {
  siteId: number;
  /** Shared with the other dashboard charts so all of them stack on one axis. */
  window: [number, number];
}

export function OptimizationChart({ siteId, window }: OptimizationChartProps) {
  const { t, i18n } = useTranslation();
  const { data: plan, isPending, error } = useOptimizationPlan(siteId);
  const { ticks, dayStarts } = useTimeAxis(window);
  const now = useNow(NOW_REFRESH_MS);

  const chartConfig = {
    batteryKw: { label: t('optimization.battery'), color: 'var(--chart-3)' },
  } satisfies ChartConfig;

  const points = useMemo<ChartPoint[]>(
    () =>
      (plan?.steps ?? []).map((step: OptimizationStep) => ({
        timestamp: new Date(step.startsAt).getTime(),
        // One signed series rather than two: charge and discharge never happen
        // at once, and the sign carries the direction without a second colour.
        batteryKw: step.dischargeKw - step.chargeKw,
        stateOfChargeKwh: step.stateOfChargeKwh,
      })),
    [plan],
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('optimization.title')}</CardTitle>
        <CardDescription>{t('optimization.description')}</CardDescription>
      </CardHeader>

      <CardContent className="flex flex-col gap-4">
        {isPending && <Skeleton className="h-56 w-full" />}

        {/* A site with no battery or no forecasts answers 422 with a reason, and
            that reason is more useful than a generic failure. */}
        {error && (
          <p className="text-muted-foreground py-12 text-center">{translateError(error)}</p>
        )}

        {!isPending && !error && points.length > 0 && (
          <>
            <div className="flex flex-wrap items-baseline gap-x-8 gap-y-2">
              <div>
                <p className="text-muted-foreground text-xs">{t('optimization.savings')}</p>
                <p className="text-2xl font-semibold tabular-nums">
                  {formatMoney(plan.savingsCzk, i18n.language)}{' '}
                  <span className="text-muted-foreground text-sm font-normal">
                    {t('optimization.unit_money')}
                  </span>
                </p>
              </div>
              <div>
                <p className="text-muted-foreground text-xs">{t('optimization.baseline_cost')}</p>
                <p className="tabular-nums">{formatMoney(plan.baselineCostCzk, i18n.language)}</p>
              </div>
              <div>
                <p className="text-muted-foreground text-xs">{t('optimization.planned_cost')}</p>
                <p className="tabular-nums">{formatMoney(plan.costCzk, i18n.language)}</p>
              </div>
            </div>

            <ChartContainer config={chartConfig} className="aspect-auto h-56 w-full">
              <AreaChart data={points} margin={{ left: 4, right: 8, top: 8 }}>
                <CartesianGrid vertical={false} />

                {dayBands(dayStarts, window[1], [t('chart.today'), t('chart.tomorrow')])}

                <XAxis
                  dataKey="timestamp"
                  type="number"
                  scale="time"
                  domain={window}
                  ticks={ticks}
                  tickFormatter={(value: number) => formatPragueTime(value, i18n.language)}
                  tickLine={false}
                  axisLine={false}
                  tickMargin={8}
                />

                <YAxis
                  tickFormatter={(value: number) => formatQuantity(value, 'power', i18n.language)}
                  tickLine={false}
                  axisLine={false}
                  width={48}
                />

                <ChartTooltip
                  cursor={{ strokeDasharray: '4 4' }}
                  content={
                    <ChartTooltipContent
                      // The direction is spelled out rather than left as a sign
                      // for the reader to decode, and the state of charge is
                      // named so it cannot be read as "how much was charged".
                      formatter={(value) => {
                        const power = Number(value);
                        const action =
                          power < 0
                            ? 'optimization.charging'
                            : power > 0
                              ? 'optimization.discharging'
                              : 'optimization.idle';

                        return (
                          <div className="flex flex-1 items-center justify-between gap-4">
                            <span className="text-muted-foreground">{t(action)}</span>
                            <span className="text-foreground font-mono font-medium tabular-nums">
                              {formatQuantity(Math.abs(power), 'power', i18n.language)}{' '}
                              <span className="text-muted-foreground font-normal">
                                {UNIT.power}
                              </span>
                            </span>
                          </div>
                        );
                      }}
                      labelFormatter={(_label, payload) => {
                        const entry = payload[0] as { payload?: ChartPoint } | undefined;
                        const point = entry?.payload;
                        if (!point) return '';

                        return `${formatPragueTime(point.timestamp, i18n.language)}–${formatPragueTime(
                          point.timestamp + STEP_DURATION_MS,
                          i18n.language,
                        )} · ${t('optimization.state_of_charge')} ${formatQuantity(
                          point.stateOfChargeKwh,
                          'energy',
                          i18n.language,
                        )} ${UNIT.energy}`;
                      }}
                    />
                  }
                />

                {/* The zero line is the whole point here: above it the battery
                    supplies the house, below it the battery is being filled. */}
                <ReferenceLine y={0} stroke="var(--border)" strokeWidth={1} />

                {nowLine(now, window)}

                <Area
                  type="stepAfter"
                  dataKey="batteryKw"
                  stroke="var(--color-batteryKw)"
                  fill="var(--color-batteryKw)"
                  fillOpacity={0.15}
                  strokeWidth={2}
                  baseValue={0}
                  dot={false}
                  isAnimationActive={false}
                />
              </AreaChart>
            </ChartContainer>
          </>
        )}
      </CardContent>
    </Card>
  );
}
