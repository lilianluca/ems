import { Link } from '@tanstack/react-router';
import { PencilIcon } from 'lucide-react';
import { useTranslation } from 'react-i18next';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { formatFractionAsPercent, formatWithUnit } from '@/lib/units';

import type { Device } from '../api';
import { compassPoint } from '../compass';
import { DeleteDeviceButton } from './delete-device-button';

interface DeviceCardProps {
  siteId: number;
  device: Device;
}

/**
 * A card rather than a table row: the device types share almost no fields,
 * so a table would be mostly dashes.
 */
export function DeviceCard({ siteId, device }: DeviceCardProps) {
  const { t, i18n } = useTranslation();

  const specsOf = (item: Device) => {
    if (item.type === 'pv') {
      return [
        {
          label: t('devices.installed_power'),
          value: formatWithUnit(item.installedPowerKwp, 'peakPower', i18n.language),
        },
        {
          label: t('devices.inverter_power'),
          value: formatWithUnit(item.inverterPowerKw, 'power', i18n.language),
        },
        {
          label: t('devices.tilt'),
          value: formatWithUnit(item.tiltDegrees, 'angle', i18n.language),
        },
        {
          label: t('devices.azimuth'),
          value: `${formatWithUnit(item.azimuthDegrees, 'angle', i18n.language)} · ${t(`devices.compass_${compassPoint(item.azimuthDegrees)}`)}`,
        },
      ];
    }
    if (item.type === 'battery') {
      return [
        {
          label: t('devices.capacity'),
          value: formatWithUnit(item.capacityKwh, 'energy', i18n.language),
        },
        {
          label: t('devices.max_charge_power'),
          value: formatWithUnit(item.maxChargePowerKw, 'power', i18n.language),
        },
        {
          label: t('devices.max_discharge_power'),
          value: formatWithUnit(item.maxDischargePowerKw, 'power', i18n.language),
        },
        {
          label: t('devices.usable_range'),
          value: `${formatFractionAsPercent(item.minStateOfCharge, i18n.language)} – ${formatFractionAsPercent(item.maxStateOfCharge, i18n.language)}`,
        },
        {
          label: t('devices.efficiency'),
          value: formatFractionAsPercent(item.roundTripEfficiency, i18n.language),
        },
        {
          label: t('devices.cycle_life'),
          value: `${new Intl.NumberFormat(i18n.language).format(item.cycleLife)} ${t('devices.cycles_unit')}`,
        },
      ];
    }
    const cop = new Intl.NumberFormat(i18n.language, { maximumFractionDigits: 2 });
    return [
      { label: t('devices.cop_at_minus_7'), value: cop.format(item.copAtMinus7C) },
      { label: t('devices.cop_at_2'), value: cop.format(item.copAt2C) },
      { label: t('devices.cop_at_7'), value: cop.format(item.copAt7C) },
      { label: t('devices.cop_at_12'), value: cop.format(item.copAt12C) },
      {
        label: t('devices.max_heat_power'),
        value: formatWithUnit(item.maxHeatPowerKw, 'power', i18n.language),
      },
    ];
  };
  const specs = specsOf(device);

  const editLink = () => {
    if (device.type === 'pv') {
      return (
        <Link to="/sites/$siteId/devices/pv/$deviceId" params={{ siteId, deviceId: device.id }} />
      );
    }
    if (device.type === 'battery') {
      return (
        <Link
          to="/sites/$siteId/devices/battery/$deviceId"
          params={{ siteId, deviceId: device.id }}
        />
      );
    }
    return (
      <Link
        to="/sites/$siteId/devices/heat-pump/$deviceId"
        params={{ siteId, deviceId: device.id }}
      />
    );
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between gap-2">
        <div className="flex flex-col gap-1">
          <CardTitle>{device.name}</CardTitle>
          <Badge variant="secondary" className="w-fit">
            {t(`devices.type_${device.type}`)}
          </Badge>
        </div>
        <div className="flex gap-1">
          <Button variant="ghost" size="icon-sm" aria-label={t('devices.edit')} render={editLink()}>
            <PencilIcon />
          </Button>
          <DeleteDeviceButton siteId={siteId} device={device} />
        </div>
      </CardHeader>

      <CardContent>
        <dl className="grid gap-x-6 gap-y-2 text-sm sm:grid-cols-2">
          {specs.map((spec) => (
            <div key={spec.label} className="flex justify-between gap-4">
              <dt className="text-muted-foreground">{spec.label}</dt>
              <dd className="tabular-nums">{spec.value}</dd>
            </div>
          ))}
        </dl>
      </CardContent>
    </Card>
  );
}
