import { Link } from '@tanstack/react-router';
import { PencilIcon } from 'lucide-react';
import { useTranslation } from 'react-i18next';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

import type { Device } from '../api';
import { compassPoint } from '../compass';
import { DeleteDeviceButton } from './delete-device-button';

interface DeviceCardProps {
  siteId: number;
  device: Device;
}

/**
 * A card rather than a table row: the two device types share almost no fields,
 * so a table would be mostly dashes.
 */
export function DeviceCard({ siteId, device }: DeviceCardProps) {
  const { t, i18n } = useTranslation();
  const format = new Intl.NumberFormat(i18n.language, { maximumFractionDigits: 1 });
  const percent = (fraction: number) => `${format.format(fraction * 100)} %`;

  const specs =
    device.type === 'pv'
      ? [
          {
            label: t('devices.installed_power'),
            value: `${format.format(device.installedPowerKwp)} kWp`,
          },
          {
            label: t('devices.inverter_power'),
            value: `${format.format(device.inverterPowerKw)} kW`,
          },
          { label: t('devices.tilt'), value: `${format.format(device.tiltDegrees)}°` },
          {
            label: t('devices.azimuth'),
            value: `${format.format(device.azimuthDegrees)}° · ${t(`devices.compass_${compassPoint(device.azimuthDegrees)}`)}`,
          },
        ]
      : [
          { label: t('devices.capacity'), value: `${format.format(device.capacityKwh)} kWh` },
          {
            label: t('devices.max_charge_power'),
            value: `${format.format(device.maxChargePowerKw)} kW`,
          },
          {
            label: t('devices.max_discharge_power'),
            value: `${format.format(device.maxDischargePowerKw)} kW`,
          },
          {
            label: t('devices.usable_range'),
            value: `${percent(device.minStateOfCharge)} – ${percent(device.maxStateOfCharge)}`,
          },
          { label: t('devices.efficiency'), value: percent(device.roundTripEfficiency) },
        ];

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between gap-2">
        <div className="flex flex-col gap-1">
          <CardTitle>{device.name}</CardTitle>
          <Badge variant="secondary" className="w-fit">
            {t(device.type === 'pv' ? 'devices.type_pv' : 'devices.type_battery')}
          </Badge>
        </div>
        <div className="flex gap-1">
          <Button
            variant="ghost"
            size="icon-sm"
            aria-label={t('devices.edit')}
            render={
              device.type === 'pv' ? (
                <Link
                  to="/sites/$siteId/devices/pv/$deviceId"
                  params={{ siteId, deviceId: device.id }}
                />
              ) : (
                <Link
                  to="/sites/$siteId/devices/battery/$deviceId"
                  params={{ siteId, deviceId: device.id }}
                />
              )
            }
          >
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
