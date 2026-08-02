import type { components } from './schema';

type ErrorResponse = components['schemas']['ErrorResponse'];

/** Error thrown by query and mutation functions when the API returns 4xx/5xx. */
export class AppError extends Error {
  readonly status: number;
  readonly code: string;
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
