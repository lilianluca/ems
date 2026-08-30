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
