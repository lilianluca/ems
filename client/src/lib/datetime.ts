/**
 * Formatting helpers pinned to the Czech market timezone.
 *
 * Spot prices, forecasts and optimisation schedules are all anchored to
 * `Europe/Prague`, so rendering them in the viewer's own timezone would show the
 * wrong hours to anyone abroad. Local `Date` getters are banned by ESLint for
 * exactly this reason — go through these helpers instead.
 */
export const PRAGUE_TIME_ZONE = 'Europe/Prague';

export function formatPragueTime(value: Date | number, locale: string): string {
  return new Intl.DateTimeFormat(locale, {
    hour: '2-digit',
    minute: '2-digit',
    timeZone: PRAGUE_TIME_ZONE,
  }).format(value);
}

export function formatPragueDateTime(value: Date | number, locale: string): string {
  return new Intl.DateTimeFormat(locale, {
    day: 'numeric',
    month: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: PRAGUE_TIME_ZONE,
  }).format(value);
}

/** Calendar day in Prague as `YYYY-MM-DD` — used to detect a day boundary. */
const dayKeyFormatter = new Intl.DateTimeFormat('en-CA', {
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  timeZone: PRAGUE_TIME_ZONE,
});

export function pragueDayKey(value: Date | number): string {
  return dayKeyFormatter.format(value);
}

/** Wall-clock hour and minute in Prague, for picking axis ticks. */
const hourMinuteFormatter = new Intl.DateTimeFormat('en-GB', {
  hour: '2-digit',
  minute: '2-digit',
  hourCycle: 'h23', // never render midnight as 24:00
  timeZone: PRAGUE_TIME_ZONE,
});

export function pragueHourMinute(value: Date | number): { hour: number; minute: number } {
  const [hour, minute] = hourMinuteFormatter.format(value).split(':');
  return { hour: Number(hour), minute: Number(minute) };
}

const HOUR_MS = 3_600_000;

/**
 * The step every series is sampled at, mirroring `STEP` on the server.
 *
 * Prices, forecasts and the plan all hold for one of these blocks, so this is
 * both how wide a point is on a chart and how long a tooltip range runs.
 */
export const STEP_DURATION_MS = HOUR_MS / 4;

/** Wall-clock time in Prague expressed as if it were UTC, used to derive the offset. */
function pragueWallClock(value: number): number {
  const parts = new Intl.DateTimeFormat('en-CA', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hourCycle: 'h23',
    timeZone: PRAGUE_TIME_ZONE,
  }).formatToParts(value);

  const get = (type: Intl.DateTimeFormatPartTypes) =>
    Number(parts.find((part) => part.type === type)?.value);

  return Date.UTC(
    get('year'),
    get('month') - 1,
    get('day'),
    get('hour'),
    get('minute'),
    get('second'),
  );
}

/** Midnight in Prague, `dayOffset` days from the given instant, as epoch ms. */
function pragueMidnight(value: number, dayOffset: number): number {
  const wall = pragueWallClock(value);
  const offset = wall - value;

  const midnightWall = new Date(wall);
  midnightWall.setUTCHours(0, 0, 0, 0);
  midnightWall.setUTCDate(midnightWall.getUTCDate() + dayOffset);

  // The offset can differ on the target day (daylight saving), so it is
  // resolved once more against the provisional instant.
  const provisional = midnightWall.getTime() - offset;
  return midnightWall.getTime() - (pragueWallClock(provisional) - provisional);
}

/**
 * Today and tomorrow as the Czech market defines a day.
 *
 * Mirrors `default_market_window()` on the server. Both charts pin their axis to
 * this window rather than to whatever data happens to exist, so they stay
 * aligned — and so a half-empty chart reads as "not published yet" instead of
 * silently stretching one day across the full width.
 */
export function pragueMarketWindow(now: number): [number, number] {
  return [pragueMidnight(now, 0), pragueMidnight(now, 2) - STEP_DURATION_MS];
}
