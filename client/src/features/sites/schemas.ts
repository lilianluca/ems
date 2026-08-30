import { z } from 'zod';

import { vk } from '@/lib/i18n/keys';

// Deliberately no `z.coerce`: it turns an empty input into 0, which is a valid
// latitude and longitude, so a forgotten field would silently place the site in
// the Atlantic. The form converts to a number and leaves blanks undefined.
export const createSiteSchema = z.object({
  name: z.string().trim().min(1, vk('validation.site_name_required')).max(255),
  latitude: z
    .number(vk('validation.latitude_invalid'))
    .min(-90, vk('validation.latitude_invalid'))
    .max(90, vk('validation.latitude_invalid')),
  longitude: z
    .number(vk('validation.longitude_invalid'))
    .min(-180, vk('validation.longitude_invalid'))
    .max(180, vk('validation.longitude_invalid')),
  ownerId: z
    .number(vk('validation.owner_required'))
    .int()
    .positive(vk('validation.owner_required')),
});

export type CreateSiteFormValues = z.infer<typeof createSiteSchema>;
