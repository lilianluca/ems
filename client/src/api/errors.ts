import i18n from '@/lib/i18n';

import type { components } from './schema';

export type ErrorCode = components['schemas']['ErrorCode'];

type ErrorResponse = components['schemas']['ErrorResponse'];

/** Error thrown by query and mutation functions when the API returns 4xx/5xx. */
export class AppError extends Error {
  readonly status: number;
  readonly code: ErrorCode;
  readonly fields?: Record<string, string[]>;

  constructor(status: number, body: ErrorResponse) {
    super(body.error.message);
    this.name = 'AppError';
    this.status = status;
    this.code = body.error.code;
    this.fields = body.error.fields ?? undefined;
  }
}

export function isAppError(error: unknown): error is AppError {
  return error instanceof AppError;
}

/** Resolves a user-facing message from an error code. */
export function translateError(error: unknown): string {
  if (!isAppError(error)) {
    return i18n.t('client.network_error');
  }
  return i18n.t(`errors.${error.code}`);
}
