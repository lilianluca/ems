import type { ChangeEvent } from 'react';

/**
 * React Hook Form types a field by its schema, but `defaultValues` legitimately
 * starts a required number as undefined. These helpers keep such inputs
 * controlled without repeating the null-coalescing at every call site.
 */
export function toInputValue(value: number | undefined): number | string {
  return value ?? '';
}

export function toSelectValue(value: number | undefined): number | null {
  return value ?? null;
}

/** Empty stays undefined rather than becoming 0, which is a valid value here. */
export function numberFromInput(event: ChangeEvent<HTMLInputElement>): number | undefined {
  const { value, valueAsNumber } = event.currentTarget;
  return value === '' ? undefined : valueAsNumber;
}
