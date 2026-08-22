import type { cs } from './locales/cs';

export type ValidationKey = `validation.${keyof typeof cs.validation}`;

/**
 * Marks a translation key used as a Zod message. The key is resolved at render
 * time, so validation messages follow language changes.
 */
export function vk(key: ValidationKey): string {
  return key;
}
