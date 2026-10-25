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

/** The same fields as creating a site, less the owner, which is not changed here. */
export const siteDetailsSchema = createSiteSchema.omit({ ownerId: true });

export type SiteDetailsFormValues = z.infer<typeof siteDetailsSchema>;

/** Mirrors `OccupancyWindow` on the server: whole hours, wrapping past midnight. */
const occupancyWindowSchema = z
  .object({
    startHour: z.number(vk('validation.hour_invalid')).int().min(0).max(23),
    endHour: z.number(vk('validation.hour_invalid')).int().min(0).max(23),
  })
  .refine((window) => window.startHour !== window.endHour, {
    message: vk('validation.window_bounds_equal'),
    path: ['endHour'],
  });

export const houseSchema = z.object({
  lightingPowerW: z
    .number(vk('validation.power_not_negative'))
    .int(vk('validation.power_not_negative'))
    .min(0, vk('validation.power_not_negative'))
    .max(10_000, vk('validation.lighting_power_max')),
  occupancyWindows: z.array(occupancyWindowSchema),
});

export type HouseFormValues = z.infer<typeof houseSchema>;
