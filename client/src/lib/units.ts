/**
 * One place that decides how a physical quantity is written.
 *
 * The decimals are fixed per quantity rather than per component. A dashboard is
 * read by comparing numbers across cards and charts, and that only works if the
 * same quantity is always written the same way — six components each choosing
 * their own precision is how "3,4 kW" and "3,45 kW" end up side by side.
 *
 * The symbols live here rather than in the translations because SI units are
 * not translated. Anything carrying a currency does go through i18n, because
 * "Kč" and "CZK" differ by language.
 *
 * One quantity is deliberately absent: the spot price is formatted by its own
 * chart, because the precision follows the currency — thousands of CZK/MWh want
 * no decimals where hundreds of EUR/MWh want two. That is a choice, not an
 * oversight, and unifying it here would lose it.
 */

export type Quantity =
  'power' | 'wattPower' | 'peakPower' | 'energy' | 'percent' | 'angle' | 'minutes';

/** Chosen so the smallest difference that matters is still visible. */
const DECIMALS: Record<Quantity, number> = {
  power: 2,
  wattPower: 0,
  peakPower: 2,
  energy: 1,
  percent: 0,
  angle: 0,
  minutes: 0,
};

export const UNIT: Record<Quantity, string> = {
  power: 'kW',
  wattPower: 'W',
  peakPower: 'kWp',
  energy: 'kWh',
  percent: '%',
  angle: '°',
  minutes: 'min',
};

/** The number alone, for callers that style the unit separately. */
export function formatQuantity(value: number, quantity: Quantity, locale: string): string {
  return new Intl.NumberFormat(locale, {
    minimumFractionDigits: 0,
    maximumFractionDigits: DECIMALS[quantity],
  }).format(value);
}

/** Number and unit as one string, for table cells and definition lists. */
export function formatWithUnit(value: number, quantity: Quantity, locale: string): string {
  const separator = quantity === 'angle' ? '' : ' ';
  return `${formatQuantity(value, quantity, locale)}${separator}${UNIT[quantity]}`;
}

/** A fraction stored as 0–1, shown as a percentage. */
export function formatFractionAsPercent(fraction: number, locale: string): string {
  return formatWithUnit(fraction * 100, 'percent', locale);
}

/**
 * Money is formatted by magnitude, not by a fixed rule: a saving of 4,94 Kč and
 * a spot price of 3 618 Kč/MWh both have to read naturally, and two decimals on
 * the second would be noise.
 */
export function formatMoney(value: number, locale: string): string {
  const decimals = Math.abs(value) < 100 ? 2 : 0;
  return new Intl.NumberFormat(locale, {
    minimumFractionDigits: 0,
    maximumFractionDigits: decimals,
  }).format(value);
}
