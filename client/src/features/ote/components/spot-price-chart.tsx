import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Area, AreaChart, CartesianGrid, ReferenceLine, XAxis, YAxis } from 'recharts';

import { dayBands, nowLine, useTimeAxis } from '@/components/chart/time-axis';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  type ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from '@/components/ui/chart';
import { Skeleton } from '@/components/ui/skeleton';
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group';
import { useNow } from '@/hooks/use-now';
import { formatPragueTime, STEP_DURATION_MS } from '@/lib/datetime';

import { type SpotPrice, useSpotPrices } from '../api';

/** How often the "now" marker and the current block are recomputed. */
const NOW_REFRESH_MS = 60_000;

const CURRENCIES = ['czk', 'eur'] as const;
type Currency = (typeof CURRENCIES)[number];

function isCurrency(value: unknown): value is Currency {
  return CURRENCIES.some((currency) => currency === value);
}

/** Which field each currency reads, and how many decimals it needs. */
const CURRENCY_FIELD = {
  czk: 'priceCzkMwh',
  eur: 'priceEurMwh',
} as const satisfies Record<Currency, keyof Omit<ChartPoint, 'timestamp'>>;

// Czech prices run in the thousands, euro prices in the hundreds, so rounding
// the euro series to whole units would flatten most of its detail.
const CURRENCY_DECIMALS: Record<Currency, number> = { czk: 0, eur: 2 };

interface ChartPoint {
  timestamp: number;
  priceCzkMwh: number;
  priceEurMwh: number;
}

interface SpotPriceChartProps {
  /** Shared with the forecast chart so the two stack on one time axis. */
  window: [number, number];
}

export function SpotPriceChart({ window }: SpotPriceChartProps) {
  const { t, i18n } = useTranslation();
  const { data: prices, isPending, isError } = useSpotPrices();
  const [currency, setCurrency] = useState<Currency>('czk');

  const field = CURRENCY_FIELD[currency];
  const unit = t(currency === 'czk' ? 'ote.unit_czk' : 'ote.unit_eur');

  const chartConfig = {
    // Both series are declared so `--color-<field>` resolves whichever is shown.
    priceCzkMwh: { label: t('ote.price'), color: 'var(--chart-5)' },
    priceEurMwh: { label: t('ote.price'), color: 'var(--chart-5)' },
  } satisfies ChartConfig;

  const points = useMemo<ChartPoint[]>(
    () =>
      (prices ?? []).map((price: SpotPrice) => ({
        timestamp: new Date(price.startsAt).getTime(),
        priceCzkMwh: price.priceCzkMwh,
        priceEurMwh: price.priceEurMwh,
      })),
    [prices],
  );

  const { ticks, dayStarts } = useTimeAxis(window);
  const now = useNow(NOW_REFRESH_MS);
  const currentBlock = points.findLast(
    (point) => point.timestamp <= now && now < point.timestamp + STEP_DURATION_MS,
  );

  const priceFormatter = new Intl.NumberFormat(i18n.language, {
    maximumFractionDigits: CURRENCY_DECIMALS[currency],
  });
  const hasNegativePrice = points.some((point) => point[field] < 0);

  return (
    <Card>
      <CardHeader className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <CardTitle>{t('ote.title')}</CardTitle>
          <CardDescription>{t('ote.description')}</CardDescription>
        </div>

        <ToggleGroup
          size="sm"
          value={[currency]}
          aria-label={t('ote.currency')}
          onValueChange={(values: unknown[]) => {
            // Base UI reports the group value as an array and allows clearing it;
            // a currency must always be selected, so ignore an empty result.
            const next = values[0];
            if (isCurrency(next)) setCurrency(next);
          }}
        >
          {CURRENCIES.map((option) => (
            <ToggleGroupItem key={option} value={option}>
              {t(option === 'czk' ? 'ote.currency_czk' : 'ote.currency_eur')}
            </ToggleGroupItem>
          ))}
        </ToggleGroup>
      </CardHeader>

      <CardContent className="flex flex-col gap-4">
        {isPending && <Skeleton className="h-80 w-full" />}

        {isError && (
          <p className="text-muted-foreground py-12 text-center">{t('ote.load_error')}</p>
        )}

        {!isPending && !isError && points.length === 0 && (
          <p className="text-muted-foreground py-12 text-center">{t('ote.empty')}</p>
        )}

        {!isPending && !isError && points.length > 0 && (
          <>
            <div className="flex flex-wrap items-baseline gap-x-8 gap-y-2">
              <div>
                <p className="text-muted-foreground text-xs">{t('ote.current')}</p>
                <p className="text-2xl font-semibold tabular-nums">
                  {currentBlock ? priceFormatter.format(currentBlock[field]) : '—'}{' '}
                  <span className="text-muted-foreground text-sm font-normal">{unit}</span>
                </p>
              </div>
              <Stat
                label={t('ote.cheapest')}
                points={points}
                field={field}
                pick={Math.min}
                formatter={priceFormatter}
                locale={i18n.language}
              />
              <Stat
                label={t('ote.priciest')}
                points={points}
                field={field}
                pick={Math.max}
                formatter={priceFormatter}
                locale={i18n.language}
              />
            </div>

            <ChartContainer config={chartConfig} className="aspect-auto h-80 w-full">
              <AreaChart data={points} margin={{ left: 4, right: 8, top: 8 }}>
                <CartesianGrid vertical={false} />

                {/* Declared before the series so the bands sit behind them. */}
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

                {/* No zero-anchored domain: negative spot prices are real and are
                    exactly the hours an EMS cares about. */}
                <YAxis
                  tickFormatter={(value: number) => priceFormatter.format(value)}
                  tickLine={false}
                  axisLine={false}
                  width={48}
                />

                <ChartTooltip
                  cursor={{ strokeDasharray: '4 4' }}
                  content={
                    <ChartTooltipContent
                      unit={unit}
                      valueFormatter={(value) => priceFormatter.format(value)}
                      labelFormatter={(_label, payload) => {
                        // Recharts types the payload loosely; the point shape is
                        // ours, so narrow it rather than reading through `any`.
                        const entry = payload[0] as { payload?: ChartPoint } | undefined;
                        const timestamp = entry?.payload?.timestamp;
                        if (timestamp === undefined) return '';

                        return `${formatPragueTime(timestamp, i18n.language)}–${formatPragueTime(
                          timestamp + STEP_DURATION_MS,
                          i18n.language,
                        )}`;
                      }}
                    />
                  }
                />

                {hasNegativePrice && <ReferenceLine y={0} stroke="var(--border)" strokeWidth={1} />}

                {nowLine(now, window, t('chart.now'))}

                {/* A step, not a curve: the price holds for the whole block and
                    then jumps. Interpolating would draw prices that never existed. */}
                <Area
                  type="stepAfter"
                  dataKey={field}
                  stroke={`var(--color-${field})`}
                  fill={`var(--color-${field})`}
                  fillOpacity={0.15}
                  strokeWidth={2}
                  baseValue={0}
                  dot={false}
                  isAnimationActive={false}
                />
              </AreaChart>
            </ChartContainer>

            {/* Tomorrow's auction result is published in the early afternoon; until
                then the chart simply ends at midnight, which looks like a fault. */}
            {points[points.length - 1].timestamp < window[1] - STEP_DURATION_MS && (
              <p className="text-muted-foreground text-sm">{t('ote.tomorrow_pending')}</p>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}

interface StatProps {
  label: string;
  points: ChartPoint[];
  field: (typeof CURRENCY_FIELD)[Currency];
  pick: (...values: number[]) => number;
  formatter: Intl.NumberFormat;
  locale: string;
}

function Stat({ label, points, field, pick, formatter, locale }: StatProps) {
  const value = pick(...points.map((point) => point[field]));
  const at = points.find((point) => point[field] === value);

  return (
    <div>
      <p className="text-muted-foreground text-xs">{label}</p>
      <p className="tabular-nums">
        {formatter.format(value)}{' '}
        {at && (
          <span className="text-muted-foreground text-xs">
            · {formatPragueTime(at.timestamp, locale)}
          </span>
        )}
      </p>
    </div>
  );
}
