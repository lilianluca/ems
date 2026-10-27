import { useEffect, useState } from 'react';

/**
 * The current time as a ticking value.
 *
 * Reading `Date.now()` during render is impure and, worse, freezes: a "now"
 * marker rendered that way stops moving until something else re-renders the
 * component. This keeps it advancing and keeps the clock read out of render.
 *
 * Ticks land on wall-clock multiples of the interval rather than counting from
 * mount. Every caller then ticks together, and a minute tick falls exactly on
 * each quarter-hour, so the header and the dashboard switch blocks at once
 * instead of up to an interval apart.
 */
export function useNow(intervalMs: number): number {
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    let id: ReturnType<typeof setTimeout>;

    // Re-aimed on every tick, so a timer that fires late or early does not drift.
    const schedule = () => {
      id = setTimeout(
        () => {
          setNow(Date.now());
          schedule();
        },
        intervalMs - (Date.now() % intervalMs),
      );
    };
    schedule();

    return () => {
      clearTimeout(id);
    };
  }, [intervalMs]);

  return now;
}
