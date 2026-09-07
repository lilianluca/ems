import type { Appliance, ApplianceInput } from './api';
import type { ApplianceFormValues } from './schemas';

/**
 * Translates between the flat form shape and the API's discriminated config.
 *
 * Kept apart from the form so the branch assembly is readable in one place, and
 * so the percent/fraction conversion for probability happens exactly once.
 */
export function toApplianceInput(values: ApplianceFormValues): ApplianceInput {
  const common = {
    name: values.name,
    powerW: values.powerW,
    standbyPowerW: values.standbyPowerW,
    priority: values.priority,
    isShiftable: values.isShiftable,
  };

  const windows = (values.windows ?? []).map((window) => ({
    startHour: window.startHour,
    endHour: window.endHour,
    probability: window.probabilityPercent / 100,
    durationMinutesMin: window.durationMinutesMin,
    durationMinutesMax: window.durationMinutesMax,
  }));

  switch (values.behavior) {
    case 'cyclic':
      return {
        ...common,
        config: {
          behavior: 'cyclic',
          // Present because the schema requires them for this behaviour.
          activeMinutesMin: values.activeMinutesMin ?? 1,
          activeMinutesMax: values.activeMinutesMax ?? 1,
          standbyMinutesMin: values.standbyMinutesMin ?? 1,
          standbyMinutesMax: values.standbyMinutesMax ?? 1,
        },
      };
    case 'scheduled':
      return { ...common, config: { behavior: 'scheduled', windows } };
    case 'on_demand':
      return {
        ...common,
        config: {
          behavior: 'on_demand',
          windows,
          maxUsesPerWindow: values.maxUsesPerWindow ?? 1,
        },
      };
    default:
      return { ...common, config: { behavior: 'constant' } };
  }
}

export function toFormValues(appliance: Appliance): ApplianceFormValues {
  const common = {
    name: appliance.name,
    powerW: appliance.powerW,
    standbyPowerW: appliance.standbyPowerW,
    priority: appliance.priority,
    isShiftable: appliance.isShiftable,
  };

  const config = appliance.config;

  if (config.behavior === 'cyclic') {
    // `config` already carries `behavior: 'cyclic'`.
    return { ...common, ...config };
  }

  if (config.behavior === 'scheduled' || config.behavior === 'on_demand') {
    const windows = config.windows.map((window) => ({
      startHour: window.startHour,
      endHour: window.endHour,
      probabilityPercent: Math.round(window.probability * 1000) / 10,
      durationMinutesMin: window.durationMinutesMin,
      durationMinutesMax: window.durationMinutesMax,
    }));

    return config.behavior === 'scheduled'
      ? { ...common, behavior: 'scheduled', windows }
      : { ...common, behavior: 'on_demand', windows, maxUsesPerWindow: config.maxUsesPerWindow };
  }

  return { ...common, behavior: 'constant' };
}

/** Blank window, biased towards a plausible daytime slot. */
export function emptyTimeWindow() {
  return {
    startHour: 9,
    endHour: 17,
    probabilityPercent: 100,
    durationMinutesMin: 60,
    durationMinutesMax: 60,
  };
}
