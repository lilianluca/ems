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
   * The day's two savings, each split by whether the simulation recorded every
   * step: a day falls in exactly one of the two strengths, and the four series
   * stack into one bar. Null leaves a gap, not a zero.
   */
  batteryCompleteCzk: number | null;
  batteryPartialCzk: number | null;
  restrictionCompleteCzk: number | null;
  restrictionPartialCzk: number | null;
  record: DailySavings | null;
  partial: boolean;
}

/** What the battery and the saving mode saved together. */
function totalSavings(record: DailySavings): number {
  return record.savingsCzk + record.restrictionSavingsCzk;
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
    batteryCompleteCzk: { label: t('savings.by_battery'), color: 'var(--chart-3)' },
    batteryPartialCzk: { label: t('savings.by_battery'), color: 'var(--chart-3)' },
    restrictionCompleteCzk: { label: t('savings.by_restriction'), color: 'var(--chart-1)' },
    restrictionPartialCzk: { label: t('savings.by_restriction'), color: 'var(--chart-1)' },
  } satisfies ChartConfig;

  const points = useMemo<DayPoint[]>(() => {
    const byDay = new Map((days ?? []).map((record) => [record.day, record]));
    return monthDayKeys(month).map((dayKey, index) => {
      const record = byDay.get(dayKey) ?? null;
      const partial = record !== null && record.steps < stepsInPragueDay(dayKey);
      return {
        dayKey,
        dayOfMonth: index + 1,
        batteryCompleteCzk: record && !partial ? record.savingsCzk : null,
        batteryPartialCzk: record && partial ? record.savingsCzk : null,
        restrictionCompleteCzk: record && !partial ? record.restrictionSavingsCzk : null,
        restrictionPartialCzk: record && partial ? record.restrictionSavingsCzk : null,
        record,
        partial,
      };
    });
  }, [days, month]);

  const recorded = (days ?? []).toSorted((a, b) => a.day.localeCompare(b.day));
  const monthBattery = recorded.reduce((sum, day) => sum + day.savingsCzk, 0);
  const monthRestriction = recorded.reduce((sum, day) => sum + day.restrictionSavingsCzk, 0);
  const monthTotal = monthBattery + monthRestriction;
  // A month spent in the normal mode has nothing to split, so it stays one series.
  const hasRestriction = recorded.some((day) => day.restrictionSavingsCzk !== 0);
  const best = recorded.reduce<DailySavings | null>(
    (top, day) => (top === null || totalSavings(day) > totalSavings(top) ? day : top),
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
            {hasRestriction && (
              <p className="text-muted-foreground text-xs tabular-nums">
                {t('savings.split', {
                  battery: money(monthBattery),
                  restriction: money(monthRestriction),
                })}
              </p>
            )}
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
                  {money(totalSavings(best))}{' '}
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
                  {money(total.savingsCzk + total.restrictionSavingsCzk)}{' '}
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
            {hasRestriction && (
              <div className="text-muted-foreground flex flex-wrap gap-x-4 gap-y-1 text-xs">
                <span className="flex items-center gap-1.5">
                  <span
                    className="size-2.5 rounded-sm"
                    style={{ background: 'var(--chart-3)' }}
                    aria-hidden
                  />
                  {t('savings.by_battery')}
                </span>
                <span className="flex items-center gap-1.5">
                  <span
                    className="size-2.5 rounded-sm"
                    style={{ background: 'var(--chart-1)' }}
                    aria-hidden
                  />
                  {t('savings.by_restriction')}
                </span>
              </div>
            )}
            <ChartContainer config={chartConfig} className="aspect-auto h-56 w-full">
              {/* `sign` stacks a negative battery day below the axis and the
                  saving mode's part above it, instead of one hiding the other. */}
              <BarChart
                data={points}
                margin={{ left: 4, right: 8, top: 8 }}
                barCategoryGap={2}
                stackOffset="sign"
              >
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
                        // The tooltip is drawn once per day, on the battery series
                        // that holds the day's value; the other three add nothing.
                        const series = point.partial ? 'batteryPartialCzk' : 'batteryCompleteCzk';
                        if (!point.record || item.dataKey !== series) return null;
                        const rows = [
                          ...(hasRestriction
                            ? ([
                                [t('savings.by_battery'), point.record.savingsCzk],
                                [t('savings.by_restriction'), point.record.restrictionSavingsCzk],
                              ] as const)
                            : []),
                          [t('savings.saved'), totalSavings(point.record)],
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
                {/* One bar per day. The battery's part sits on the axis, the saving
                    mode's on top of it, and only the top end is rounded. */}
                <Bar
                  dataKey="batteryCompleteCzk"
                  stackId="day"
                  fill="var(--color-batteryCompleteCzk)"
                  radius={hasRestriction ? 0 : [4, 4, 0, 0]}
                  isAnimationActive={false}
                />
                <Bar
                  dataKey="batteryPartialCzk"
                  stackId="day"
                  fill="var(--color-batteryPartialCzk)"
                  fillOpacity={0.55}
                  radius={hasRestriction ? 0 : [4, 4, 0, 0]}
                  isAnimationActive={false}
                />
                {hasRestriction && (
                  <>
                    <Bar
                      dataKey="restrictionCompleteCzk"
                      stackId="day"
                      fill="var(--color-restrictionCompleteCzk)"
                      radius={[4, 4, 0, 0]}
                      isAnimationActive={false}
                    />
                    <Bar
                      dataKey="restrictionPartialCzk"
                      stackId="day"
                      fill="var(--color-restrictionPartialCzk)"
                      fillOpacity={0.55}
                      radius={[4, 4, 0, 0]}
                      isAnimationActive={false}
                    />
                  </>
                )}
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
