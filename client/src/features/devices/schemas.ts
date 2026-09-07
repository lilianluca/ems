import { z } from 'zod';

import { vk } from '@/lib/i18n/keys';

// No `z.coerce`: an empty numeric input coerces to 0, which passes most of these
// bounds and would quietly store a wrong parameter. The forms convert instead.
export const pvDeviceSchema = z.object({
  name: z.string().trim().min(1, vk('validation.device_name_required')).max(255),
  installedPowerKwp: z
    .number(vk('validation.power_positive'))
    .positive(vk('validation.power_positive')),
  inverterPowerKw: z
    .number(vk('validation.power_positive'))
    .positive(vk('validation.power_positive')),
  tiltDegrees: z
    .number(vk('validation.tilt_invalid'))
    .min(0, vk('validation.tilt_invalid'))
    .max(90, vk('validation.tilt_invalid')),
  azimuthDegrees: z
    .number(vk('validation.azimuth_invalid'))
    .min(0, vk('validation.azimuth_invalid'))
    .lt(360, vk('validation.azimuth_invalid')),
});

export type PVDeviceFormValues = z.infer<typeof pvDeviceSchema>;

export const batteryDeviceSchema = z
  .object({
    name: z.string().trim().min(1, vk('validation.device_name_required')).max(255),
    capacityKwh: z
      .number(vk('validation.power_positive'))
      .positive(vk('validation.power_positive')),
    maxChargePowerKw: z
      .number(vk('validation.power_positive'))
      .positive(vk('validation.power_positive')),
    maxDischargePowerKw: z
      .number(vk('validation.power_positive'))
      .positive(vk('validation.power_positive')),
    // Percentages in the form, fractions on the wire — the API computes with
    // fractions, but nobody reads a battery datasheet in decimals.
    minStateOfChargePercent: z
      .number(vk('validation.percent_invalid'))
      .min(0, vk('validation.percent_invalid'))
      .lt(100, vk('validation.percent_invalid')),
    maxStateOfChargePercent: z
      .number(vk('validation.percent_invalid'))
      .gt(0, vk('validation.percent_invalid'))
      .max(100, vk('validation.percent_invalid')),
    roundTripEfficiencyPercent: z
      .number(vk('validation.percent_invalid'))
      .gt(0, vk('validation.percent_invalid'))
      .max(100, vk('validation.percent_invalid')),
  })
  .refine((values) => values.minStateOfChargePercent < values.maxStateOfChargePercent, {
    message: vk('validation.state_of_charge_range'),
    path: ['maxStateOfChargePercent'],
  });

export type BatteryDeviceFormValues = z.infer<typeof batteryDeviceSchema>;
