/**
 * Azimuth in this system follows the pvlib convention used by the simulation:
 * 0° = north, 90° = east, 180° = south, 270° = west.
 *
 * Some other tools measure from south instead, so a user who enters 0 meaning
 * "south" would get a forecast for north-facing panels — wrong, and entirely
 * plausible-looking. The form shows the resulting direction back to them.
 */
export const COMPASS_POINTS = [
  'north',
  'northeast',
  'east',
  'southeast',
  'south',
  'southwest',
  'west',
  'northwest',
] as const;

export type CompassPoint = (typeof COMPASS_POINTS)[number];

export function compassPoint(degrees: number): CompassPoint {
  const index = Math.round(degrees / 45) % COMPASS_POINTS.length;
  return COMPASS_POINTS[index];
}
