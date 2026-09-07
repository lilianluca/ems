import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { CartesianGrid, Line, LineChart, XAxis, YAxis } from 'recharts';

import { dayBands, nowLine, useTimeAxis } from '@/components/chart/time-axis';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  type ChartConfig,
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
} from '@/components/ui/chart';
import { Skeleton } from '@/components/ui/skeleton';
import { useNow } from '@/hooks/use-now';
import { formatPragueTime } from '@/lib/datetime';

import { FORECAST_STEP_MS, type SiteForecastPoint, useSiteForecast } from '../api';

const NOW_REFRESH_MS = 60_000;

interface ChartPoint {
  timestamp: number;
  pvGenerationKw: number | null;
  loadKw: number | null;
}

interface SiteForecastChartProps {
  siteId: number;
  /** Shared with the price chart so the two stack on one time axis. */
  window: [number, number];
}

export function SiteForecastChart({ siteId, window }: SiteForecastChartProps) {
  const { t, i18n } = useTranslation();
  const { data, isPending, isError } = useSiteForecast(siteId);
  const { ticks, dayStarts } = useTimeAxis(window);
  const now = useNow(NOW_REFRESH_MS);

  // Two grey series on a greyscale palette are hard to tell apart by colour
  // alone, so the dash pattern below carries the distinction as well.
  const chartConfig = {
    pvGenerationKw: {
      label: t('forecasts.generation'),
      theme: { light: 'var(--chart-5)', dark: 'var(--chart-1)' },
    },
    loadKw: {
      label: t('forecasts.consumption'),
      theme: { light: 'var(--chart-2)', dark: 'var(--chart-2)' },
    },
  } satisfies ChartConfig;

  const points = useMemo<ChartPoint[]>(
    () =>
      (data ?? []).map((point: SiteForecastPoint) => ({
        timestamp: new Date(point.startsAt).getTime(),
        // The schema marks these optional as well as nullable; normalise both
        // "absent" shapes to null so Recharts reliably breaks the line.
        pvGenerationKw: point.pvGenerationKw ?? null,
        loadKw: point.loadKw ?? null,
      })),
    [data],
  );

  // Hourly samples of kW integrate to kWh one-for-one.
  const totals = useMemo(
    () => ({
      generation: points.reduce((sum, point) => sum + (point.pvGenerationKw ?? 0), 0),
      consumption: points.reduce((sum, point) => sum + (point.loadKw ?? 0), 0),
    }),
    [points],
  );

  const energyFormatter = new Intl.NumberFormat(i18n.language, { maximumFractionDigits: 1 });

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('forecasts.title')}</CardTitle>
        <CardDescription>{t('forecasts.description')}</CardDescription>
      </CardHeader>

      <CardContent className="flex flex-col gap-4">
        {isPending && <Skeleton className="h-64 w-full" />}

        {isError && (
          <p className="text-muted-foreground py-12 text-center">{t('forecasts.load_error')}</p>
        )}

        {!isPending && !isError && points.length === 0 && (
          <p className="text-muted-foreground py-12 text-center">{t('forecasts.empty')}</p>
        )}

        {!isPending && !isError && points.length > 0 && (
          <>
            <div className="flex flex-wrap items-baseline gap-x-8 gap-y-2">
              {/* Named as predictions, never as measurements: nothing here was
                  measured, it is all model output. */}
              <div>
                <p className="text-muted-foreground text-xs">
                  {t('forecasts.expected_generation')}
                </p>
                <p className="tabular-nums">
                  {energyFormatter.format(totals.generation)}{' '}
                  <span className="text-muted-foreground text-xs">
                    {t('forecasts.unit_energy')}
                  </span>
                </p>
              </div>
              <div>
                <p className="text-muted-foreground text-xs">
                  {t('forecasts.expected_consumption')}
                </p>
                <p className="tabular-nums">
                  {energyFormatter.format(totals.consumption)}{' '}
                  <span className="text-muted-foreground text-xs">
                    {t('forecasts.unit_energy')}
                  </span>
                </p>
              </div>
            </div>

            <ChartContainer config={chartConfig} className="aspect-auto h-64 w-full">
              <LineChart data={points} margin={{ left: 4, right: 8, top: 8 }}>
                <CartesianGrid vertical={false} />

                {/* The bands repeat in every stacked panel: they are background,
                    not annotation, and without them the lower panel loses the day
                    context that makes vertical reading work. */}
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
                  tickFormatter={(value: number) => energyFormatter.format(value)}
                  tickLine={false}
                  axisLine={false}
                  width={48}
                />

                <ChartTooltip
                  cursor={{ strokeDasharray: '4 4' }}
                  content={
                    <ChartTooltipContent
                      labelFormatter={(_label, payload) => {
                        const entry = payload[0] as { payload?: ChartPoint } | undefined;
                        const timestamp = entry?.payload?.timestamp;
                        if (timestamp === undefined) return '';

                        return `${formatPragueTime(timestamp, i18n.language)}–${formatPragueTime(
                          timestamp + FORECAST_STEP_MS,
                          i18n.language,
                        )}`;
                      }}
                    />
                  }
                />

                <ChartLegend content={<ChartLegendContent />} />

                {/* No label here: the marker repeats in every panel, but the
                    price chart above names it once for the whole stack. */}
                {nowLine(now, window)}

                {/* Straight segments between samples: these are hourly samples of
                    a continuous quantity, and a curve would invent detail the
                    model never produced. */}
                <Line
                  type="linear"
                  dataKey="pvGenerationKw"
                  stroke="var(--color-pvGenerationKw)"
                  strokeWidth={2}
                  dot={false}
                  connectNulls={false}
                  isAnimationActive={false}
                />
                <Line
                  type="linear"
                  dataKey="loadKw"
                  stroke="var(--color-loadKw)"
                  strokeWidth={2}
                  strokeDasharray="5 3"
                  dot={false}
                  connectNulls={false}
                  isAnimationActive={false}
                />
              </LineChart>
            </ChartContainer>
          </>
        )}
      </CardContent>
    </Card>
  );
}
