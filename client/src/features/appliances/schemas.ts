import { z } from 'zod';

import { vk } from '@/lib/i18n/keys';

import { APPLIANCE_BEHAVIORS } from './api';

export const timeWindowSchema = z
  .object({
    startHour: z.number(vk('validation.hour_invalid')).int().min(0).max(23),
    endHour: z.number(vk('validation.hour_invalid')).int().min(0).max(23),
    // Percent in the form, fraction on the wire.
    probabilityPercent: z
      .number(vk('validation.percent_invalid'))
      .min(0, vk('validation.percent_invalid'))
      .max(100, vk('validation.percent_invalid')),
    durationMinutesMin: z.number(vk('validation.minutes_invalid')).int().min(1),
    durationMinutesMax: z.number(vk('validation.minutes_invalid')).int().min(1),
  })
  .refine((window) => window.startHour !== window.endHour, {
    message: vk('validation.window_bounds_equal'),
    path: ['endHour'],
  })
  .refine((window) => window.durationMinutesMin <= window.durationMinutesMax, {
    message: vk('validation.minutes_range'),
    path: ['durationMinutesMax'],
  });

/**
 * A flat shape validated by behaviour, rather than a discriminated union.
 *
 * The API models the config as a union, but React Hook Form cannot address a
 * field that exists in only one branch of one — every `name` would have to be
 * narrowed first. Keeping the form flat and validating conditionally gives the
 * same guarantees with field names the form can actually use; the branch is
 * assembled on submit.
 */
export const applianceSchema = z
  .object({
    name: z.string().trim().min(1, vk('validation.appliance_name_required')).max(255),
    powerW: z.number(vk('validation.power_positive')).positive(vk('validation.power_positive')),
    standbyPowerW: z.number(vk('validation.power_not_negative')).min(0),
    priority: z.number(vk('validation.priority_invalid')).int().min(1).max(4),
    isShiftable: z.boolean(),
    behavior: z.enum(APPLIANCE_BEHAVIORS),

    activeMinutesMin: z.number().int().min(1).optional(),
    activeMinutesMax: z.number().int().min(1).optional(),
    standbyMinutesMin: z.number().int().min(1).optional(),
    standbyMinutesMax: z.number().int().min(1).optional(),

    windows: z.array(timeWindowSchema).optional(),
    maxUsesPerWindow: z.number().int().min(1).optional(),
  })
  .superRefine((values, ctx) => {
    const require = (path: string, value: unknown, message: string) => {
      if (value === undefined) {
        ctx.addIssue({ code: 'custom', path: [path], message });
      }
    };

    if (values.behavior === 'cyclic') {
      require('activeMinutesMin', values.activeMinutesMin, vk('validation.minutes_invalid'));
      require('activeMinutesMax', values.activeMinutesMax, vk('validation.minutes_invalid'));
      require('standbyMinutesMin', values.standbyMinutesMin, vk('validation.minutes_invalid'));
      require('standbyMinutesMax', values.standbyMinutesMax, vk('validation.minutes_invalid'));

      if (
        values.activeMinutesMin !== undefined &&
        values.activeMinutesMax !== undefined &&
        values.activeMinutesMin > values.activeMinutesMax
      ) {
        ctx.addIssue({
          code: 'custom',
          path: ['activeMinutesMax'],
          message: vk('validation.minutes_range'),
        });
      }
      if (
        values.standbyMinutesMin !== undefined &&
        values.standbyMinutesMax !== undefined &&
        values.standbyMinutesMin > values.standbyMinutesMax
      ) {
        ctx.addIssue({
          code: 'custom',
          path: ['standbyMinutesMax'],
          message: vk('validation.minutes_range'),
        });
      }
    }

    if (values.behavior === 'scheduled' || values.behavior === 'on_demand') {
      if (!values.windows || values.windows.length === 0) {
        ctx.addIssue({
          code: 'custom',
          path: ['windows'],
          message: vk('validation.window_required'),
        });
      }
    }

    if (values.behavior === 'on_demand') {
      require('maxUsesPerWindow', values.maxUsesPerWindow, vk('validation.uses_invalid'));
    }
  });

export type ApplianceFormValues = z.infer<typeof applianceSchema>;
export type TimeWindowFormValues = z.infer<typeof timeWindowSchema>;
