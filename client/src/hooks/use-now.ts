import { useEffect, useState } from 'react';

/**
 * The current time as a ticking value.
 *
 * Reading `Date.now()` during render is impure and, worse, freezes: a "now"
 * marker rendered that way stops moving until something else re-renders the
 * component. This keeps it advancing and keeps the clock read out of render.
 */
export function useNow(intervalMs: number): number {
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    const id = setInterval(() => {
      setNow(Date.now());
    }, intervalMs);

    return () => {
      clearInterval(id);
    };
  }, [intervalMs]);

  return now;
}
