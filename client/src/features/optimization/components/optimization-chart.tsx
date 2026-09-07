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
    batteryKw: {
      label: t('optimization.battery'),
      theme: { light: 'var(--chart-3)', dark: 'var(--chart-1)' },
    },
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

  const powerFormatter = new Intl.NumberFormat(i18n.language, { maximumFractionDigits: 2 });
  const moneyFormatter = new Intl.NumberFormat(i18n.language, { maximumFractionDigits: 2 });

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
                  {moneyFormatter.format(plan.savingsCzk)}{' '}
                  <span className="text-muted-foreground text-sm font-normal">
                    {t('optimization.unit_money')}
                  </span>
                </p>
              </div>
              <div>
                <p className="text-muted-foreground text-xs">{t('optimization.baseline_cost')}</p>
                <p className="tabular-nums">{moneyFormatter.format(plan.baselineCostCzk)}</p>
              </div>
              <div>
                <p className="text-muted-foreground text-xs">{t('optimization.planned_cost')}</p>
                <p className="tabular-nums">{moneyFormatter.format(plan.costCzk)}</p>
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
                  tickFormatter={(value: number) => powerFormatter.format(value)}
                  tickLine={false}
                  axisLine={false}
                  width={48}
                />

                <ChartTooltip
                  cursor={{ strokeDasharray: '4 4' }}
                  content={
                    <ChartTooltipContent
                      unit={t('optimization.unit_power')}
                      valueFormatter={(value) => powerFormatter.format(value)}
                      labelFormatter={(_label, payload) => {
                        const entry = payload[0] as { payload?: ChartPoint } | undefined;
                        const point = entry?.payload;
                        if (!point) return '';

                        return `${formatPragueTime(point.timestamp, i18n.language)}–${formatPragueTime(
                          point.timestamp + STEP_DURATION_MS,
                          i18n.language,
                        )} · ${t('optimization.state_of_charge')} ${powerFormatter.format(
                          point.stateOfChargeKwh,
                        )} kWh`;
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
