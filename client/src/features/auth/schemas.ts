import { z } from 'zod';

import { vk } from '@/lib/i18n/keys';

export const loginSchema = z.object({
  email: z.email(vk('validation.email_invalid')).min(1, vk('validation.email_required')),
  password: z.string().min(1, vk('validation.password_required')),
});

export type LoginFormValues = z.infer<typeof loginSchema>;
