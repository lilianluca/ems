import { ChevronLeftIcon, ChevronRightIcon } from 'lucide-react';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Bar, BarChart, CartesianGrid, ReferenceLine, XAxis, YAxis } from 'recharts';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  type ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from '@/components/ui/chart';
import { Skeleton } from '@/components/ui/skeleton';
import { useNow } from '@/hooks/use-now';
import {
  type CalendarMonth,
  monthDayKeys,
  pragueMonth,
  shiftMonth,
  stepsInPragueDay,
} from '@/lib/datetime';
import { formatMoney } from '@/lib/units';

import { type DailySavings, useMonthSavings, useTotalSavings } from '../api';

/** The month only changes at midnight; re-reading the clock every ten minutes is plenty. */
const MONTH_REFRESH_MS = 10 * 60_000;

interface DayPoint {
  dayKey: string;
  dayOfMonth: number;
  /**
   * The day's saving, split by whether the simulation recorded every step: the
   * two are drawn as one bar in two strengths. Null leaves a gap, not a zero.
   */
  completeCzk: number | null;
  partialCzk: number | null;
  record: DailySavings | null;
  partial: boolean;
}

/** Day keys are calendar dates; formatting them at noon UTC keeps the date whatever the zone. */
function dayKeyToInstant(dayKey: string): number {
  const [year, month, day] = dayKey.split('-').map(Number);
  return Date.UTC(year, month - 1, day, 12);
}

interface SavingsHistoryProps {
  siteId: number;
}

export function SavingsHistory({ siteId }: SavingsHistoryProps) {
  const { t, i18n } = useTranslation();
  const currentMonth = pragueMonth(useNow(MONTH_REFRESH_MS));
  const [month, setMonth] = useState<CalendarMonth>(currentMonth);
  const isCurrentMonth = month.year === currentMonth.year && month.month === currentMonth.month;

  const { data: days, isPending } = useMonthSavings(siteId, month);
  const { data: total } = useTotalSavings(siteId);

  const chartConfig = {
    completeCzk: { label: t('savings.saved'), color: 'var(--chart-3)' },
    partialCzk: { label: t('savings.saved'), color: 'var(--chart-3)' },
  } satisfies ChartConfig;

  const points = useMemo<DayPoint[]>(() => {
    const byDay = new Map((days ?? []).map((record) => [record.day, record]));
    return monthDayKeys(month).map((dayKey, index) => {
      const record = byDay.get(dayKey) ?? null;
      const partial = record !== null && record.steps < stepsInPragueDay(dayKey);
      return {
        dayKey,
        dayOfMonth: index + 1,
        completeCzk: record && !partial ? record.savingsCzk : null,
        partialCzk: record && partial ? record.savingsCzk : null,
        record,
        partial,
      };
    });
  }, [days, month]);

  const recorded = (days ?? []).toSorted((a, b) => a.day.localeCompare(b.day));
  const monthTotal = recorded.reduce((sum, day) => sum + day.savingsCzk, 0);
  const best = recorded.reduce<DailySavings | null>(
    (top, day) => (top === null || day.savingsCzk > top.savingsCzk ? day : top),
    null,
  );

  const formatDay = (dayKey: string, options: Intl.DateTimeFormatOptions) =>
    new Intl.DateTimeFormat(i18n.language, { ...options, timeZone: 'UTC' }).format(
      dayKeyToInstant(dayKey),
    );
  const monthLabel = new Intl.DateTimeFormat(i18n.language, {
    month: 'long',
    year: 'numeric',
    timeZone: 'UTC',
  }).format(Date.UTC(month.year, month.month - 1, 15));
  const money = (value: number) =>
    `${formatMoney(value, i18n.language)} ${t('optimization.unit_money')}`;

  return (
    <Card>
      <CardHeader className="flex flex-row flex-wrap items-start justify-between gap-2">
        <div className="flex flex-col gap-1.5">
          <CardTitle>{t('savings.history_title')}</CardTitle>
          <CardDescription>{t('savings.history_description')}</CardDescription>
        </div>
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon-sm"
            aria-label={t('savings.previous_month')}
            onClick={() => {
              setMonth(shiftMonth(month, -1));
            }}
          >
            <ChevronLeftIcon />
          </Button>
          <span className="min-w-28 text-center text-sm font-medium capitalize">{monthLabel}</span>
          <Button
            variant="ghost"
            size="icon-sm"
            aria-label={t('savings.next_month')}
            disabled={isCurrentMonth}
            onClick={() => {
              setMonth(shiftMonth(month, 1));
            }}
          >
            <ChevronRightIcon />
          </Button>
        </div>
      </CardHeader>

      <CardContent className="flex flex-col gap-4">
        <div className="flex flex-wrap items-baseline gap-x-8 gap-y-2">
          <div>
            <p className="text-muted-foreground text-xs">{t('savings.month_total')}</p>
            <p className="text-2xl font-semibold tabular-nums">
              {recorded.length > 0 ? formatMoney(monthTotal, i18n.language) : '–'}{' '}
              <span className="text-muted-foreground text-sm font-normal">
                {t('optimization.unit_money')}
              </span>
            </p>
          </div>
          <div>
            <p className="text-muted-foreground text-xs">{t('savings.daily_average')}</p>
            <p className="tabular-nums">
              {recorded.length > 0 ? money(monthTotal / recorded.length) : '–'}
            </p>
          </div>
          <div>
            <p className="text-muted-foreground text-xs">{t('savings.best_day')}</p>
            <p className="tabular-nums">
              {best ? (
                <>
                  {money(best.savingsCzk)}{' '}
                  <span className="text-muted-foreground text-sm">
                    {formatDay(best.day, { day: 'numeric', month: 'numeric' })}
                  </span>
                </>
              ) : (
                '–'
              )}
            </p>
          </div>
          {/* Not tied to the month shown: the one figure that answers whether the
              battery is paying for itself. */}
          <div>
            <p className="text-muted-foreground text-xs">{t('savings.since_start')}</p>
            <p className="tabular-nums">
              {total?.since ? (
                <>
                  {money(total.savingsCzk)}{' '}
                  <span className="text-muted-foreground text-sm">
                    {t('savings.since', {
                      date: formatDay(total.since, {
                        day: 'numeric',
                        month: 'numeric',
                        year: 'numeric',
                      }),
                    })}
                  </span>
                </>
              ) : (
                '–'
              )}
            </p>
          </div>
        </div>

        {isPending && <Skeleton className="h-56 w-full" />}

        {!isPending && recorded.length === 0 && (
          <p className="text-muted-foreground py-12 text-center">{t('savings.empty')}</p>
        )}

        {!isPending && recorded.length > 0 && (
          <>
            <ChartContainer config={chartConfig} className="aspect-auto h-56 w-full">
              <BarChart data={points} margin={{ left: 4, right: 8, top: 8 }} barCategoryGap={2}>
                <CartesianGrid vertical={false} />
                <XAxis
                  dataKey="dayOfMonth"
                  tickLine={false}
                  axisLine={false}
                  tickMargin={8}
                  interval="preserveStartEnd"
                />
                <YAxis
                  tickFormatter={(value: number) => formatMoney(value, i18n.language)}
                  tickLine={false}
                  axisLine={false}
                  width={48}
                />
                <ChartTooltip
                  cursor={{ fill: 'var(--muted)', opacity: 0.5 }}
                  content={
                    <ChartTooltipContent
                      hideIndicator
                      labelFormatter={(_label, payload) => {
                        const entry = payload[0] as { payload?: DayPoint } | undefined;
                        const point = entry?.payload;
                        return point
                          ? formatDay(point.dayKey, {
                              weekday: 'short',
                              day: 'numeric',
                              month: 'long',
                            })
                          : '';
                      }}
                      formatter={(_value, _name, item) => {
                        const point = item.payload as DayPoint;
                        // Only one of the two series holds the day's value.
                        const series = point.partial ? 'partialCzk' : 'completeCzk';
                        if (!point.record || item.dataKey !== series) return null;
                        const rows = [
                          [t('savings.saved'), point.record.savingsCzk],
                          [t('savings.baseline_cost'), point.record.baselineCostCzk],
                          [t('savings.cost'), point.record.costCzk],
                        ] as const;

                        return (
                          <div className="flex flex-1 flex-col gap-1">
                            {rows.map(([label, value]) => (
                              <div key={label} className="flex items-center justify-between gap-4">
                                <span className="text-muted-foreground">{label}</span>
                                <span className="text-foreground font-mono font-medium tabular-nums">
                                  {money(value)}
                                </span>
                              </div>
                            ))}
                            {point.partial && (
                              <span className="text-muted-foreground">
                                {t('savings.partial_day', {
                                  steps: point.record.steps,
                                  total: stepsInPragueDay(point.dayKey),
                                })}
                              </span>
                            )}
                          </div>
                        );
                      }}
                    />
                  }
                />
                <ReferenceLine y={0} stroke="var(--border)" strokeWidth={1} />
                {/* One bar per day: a day is in exactly one of the two series, and
                    stacking them puts both in the same slot. */}
                <Bar
                  dataKey="completeCzk"
                  stackId="day"
                  fill="var(--color-completeCzk)"
                  radius={[4, 4, 0, 0]}
                  isAnimationActive={false}
                />
                <Bar
                  dataKey="partialCzk"
                  stackId="day"
                  fill="var(--color-partialCzk)"
                  fillOpacity={0.55}
                  radius={[4, 4, 0, 0]}
                  isAnimationActive={false}
                />
              </BarChart>
            </ChartContainer>

            {points.some((point) => point.partial) && (
              <p className="text-muted-foreground text-xs">{t('savings.partial_note')}</p>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
