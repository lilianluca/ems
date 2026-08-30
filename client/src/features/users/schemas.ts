import { z } from 'zod';

import { vk } from '@/lib/i18n/keys';

/** Mirrors MIN_PASSWORD_LENGTH in the server's users schemas. */
export const MIN_PASSWORD_LENGTH = 12;

export const USER_ROLES = ['user', 'admin'] as const;

export const createUserSchema = z.object({
  email: z.email(vk('validation.email_invalid')).min(1, vk('validation.email_required')),
  firstName: z.string().trim().min(1, vk('validation.first_name_required')),
  lastName: z.string().trim().min(1, vk('validation.last_name_required')),
  password: z.string().min(MIN_PASSWORD_LENGTH, vk('validation.password_too_short')),
  role: z.enum(USER_ROLES),
});

export type CreateUserFormValues = z.infer<typeof createUserSchema>;
