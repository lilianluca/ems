import { Link } from '@tanstack/react-router';
import { PencilIcon } from 'lucide-react';
import { useTranslation } from 'react-i18next';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { formatWithUnit } from '@/lib/units';

import type { Appliance } from '../api';
import { DeleteApplianceButton } from './delete-appliance-button';

interface ApplianceCardProps {
  siteId: number;
  appliance: Appliance;
}

export function ApplianceCard({ siteId, appliance }: ApplianceCardProps) {
  const { t, i18n } = useTranslation();
  const config = appliance.config;

  const specs: { label: string; value: string }[] = [
    {
      label: t('appliances.power'),
      value: formatWithUnit(appliance.powerW, 'wattPower', i18n.language),
    },
    {
      label: t('appliances.standby_power'),
      value: formatWithUnit(appliance.standbyPowerW, 'wattPower', i18n.language),
    },
  ];

  if (config.behavior === 'cyclic') {
    specs.push({
      label: t('appliances.cycle'),
      value: t('appliances.cycle_value', {
        activeMin: config.activeMinutesMin,
        activeMax: config.activeMinutesMax,
        standbyMin: config.standbyMinutesMin,
        standbyMax: config.standbyMinutesMax,
      }),
    });
  }

  if (config.behavior === 'scheduled' || config.behavior === 'on_demand') {
    specs.push({
      label: t('appliances.windows'),
      value: config.windows
        .map((window) => `${String(window.startHour)}–${String(window.endHour)} h`)
        .join(', '),
    });
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between gap-2">
        <div className="flex flex-col gap-1">
          <CardTitle>{appliance.name}</CardTitle>
          <Badge variant="secondary" className="w-fit">
            {t(`appliances.behavior_${appliance.behavior}`)}
          </Badge>
        </div>
        <div className="flex gap-1">
          <Button
            variant="ghost"
            size="icon-sm"
            aria-label={t('appliances.edit')}
            render={
              <Link
                to="/sites/$siteId/appliances/$applianceId"
                params={{ siteId, applianceId: appliance.id }}
              />
            }
          >
            <PencilIcon />
          </Button>
          <DeleteApplianceButton siteId={siteId} appliance={appliance} />
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
