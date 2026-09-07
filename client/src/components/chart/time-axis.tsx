import { useMemo } from 'react';
import { ReferenceArea, ReferenceLine } from 'recharts';

import { pragueDayKey, pragueHourMinute } from '@/lib/datetime';

/** One tick every six hours keeps a two-day window readable. */
const TICK_INTERVAL_HOURS = 6;
const HOUR_MS = 3_600_000;

export interface TimeAxis {
  ticks: number[];
  /** Start of each calendar day inside the window, in Prague. */
  dayStarts: number[];
}

/**
 * Axis marks derived from the window rather than from the data.
 *
 * Stacked charts only read vertically if their gridlines line up, and the series
 * they show cover different spans — prices start at midnight, forecasts at the
 * current hour. Deriving ticks from each chart's own points would put the
 * gridlines in different places.
 */
export function useTimeAxis([start, end]: [number, number]): TimeAxis {
  return useMemo(() => {
    const ticks: number[] = [];
    const dayStarts: number[] = [start];
    let previousDay = pragueDayKey(start);

    for (let instant = start; instant <= end; instant += HOUR_MS) {
      const { hour, minute } = pragueHourMinute(instant);
      if (minute === 0 && hour % TICK_INTERVAL_HOURS === 0) {
        ticks.push(instant);
      }

      const day = pragueDayKey(instant);
      if (day !== previousDay) {
        dayStarts.push(instant);
        previousDay = day;
      }
    }

    return { ticks, dayStarts };
  }, [start, end]);
}

/**
 * Recharts scans its direct children to find reference elements, so these are
 * plain functions returning arrays rather than components — a wrapper component
 * would hide them from that scan.
 */
export function dayBands(dayStarts: number[], end: number, labels: string[]): React.ReactElement[] {
  return dayStarts.map((dayStart, index) => (
    <ReferenceArea
      key={dayStart}
      x1={dayStart}
      x2={dayStarts[index + 1] ?? end}
      // The first day stays on the card background; only later days are tinted,
      // so the shading reads as "this is the next day" rather than as decoration.
      fill={index === 0 ? 'transparent' : 'var(--muted)'}
      fillOpacity={index === 0 ? 0 : 0.6}
      label={{
        value: labels[index] ?? '',
        position: 'insideTopLeft',
        className: 'fill-muted-foreground text-xs',
      }}
    />
  ));
}

/**
 * The vertical marker repeats in every stacked panel because it carries the
 * vertical reading; only the topmost panel names it, so the label is optional.
 */
export function nowLine(now: number, window: [number, number], label?: string) {
  if (now < window[0] || now > window[1]) return null;

  return (
    <ReferenceLine
      x={now}
      stroke="var(--foreground)"
      strokeWidth={1.5}
      label={
        label
          ? {
              value: label,
              // Bottom, so it never collides with the day labels above.
              position: 'insideBottomLeft',
              className: 'fill-foreground text-xs',
            }
          : undefined
      }
    />
  );
}
