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
 * A card rather than a table row: the two device types share almost no fields,
 * so a table would be mostly dashes.
 */
export function DeviceCard({ siteId, device }: DeviceCardProps) {
  const { t, i18n } = useTranslation();

  const specs =
    device.type === 'pv'
      ? [
          {
            label: t('devices.installed_power'),
            value: formatWithUnit(device.installedPowerKwp, 'peakPower', i18n.language),
          },
          {
            label: t('devices.inverter_power'),
            value: formatWithUnit(device.inverterPowerKw, 'power', i18n.language),
          },
          {
            label: t('devices.tilt'),
            value: formatWithUnit(device.tiltDegrees, 'angle', i18n.language),
          },
          {
            label: t('devices.azimuth'),
            value: `${formatWithUnit(device.azimuthDegrees, 'angle', i18n.language)} · ${t(`devices.compass_${compassPoint(device.azimuthDegrees)}`)}`,
          },
        ]
      : [
          {
            label: t('devices.capacity'),
            value: formatWithUnit(device.capacityKwh, 'energy', i18n.language),
          },
          {
            label: t('devices.max_charge_power'),
            value: formatWithUnit(device.maxChargePowerKw, 'power', i18n.language),
          },
          {
            label: t('devices.max_discharge_power'),
            value: formatWithUnit(device.maxDischargePowerKw, 'power', i18n.language),
          },
          {
            label: t('devices.usable_range'),
            value: `${formatFractionAsPercent(device.minStateOfCharge, i18n.language)} – ${formatFractionAsPercent(device.maxStateOfCharge, i18n.language)}`,
          },
          {
            label: t('devices.efficiency'),
            value: formatFractionAsPercent(device.roundTripEfficiency, i18n.language),
          },
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
