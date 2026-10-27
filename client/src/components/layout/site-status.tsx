import {
  BatteryChargingIcon,
  BatteryFullIcon,
  BatteryLowIcon,
  PiggyBankIcon,
  ZapIcon,
} from 'lucide-react';
import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { type BatteryDevice, useBatteryState, useDevices } from '@/features/devices/api';
import { useSpotPrices } from '@/features/ote/api';
import { useTodaySavings } from '@/features/savings/api';
import { useNow } from '@/hooks/use-now';
import { STEP_DURATION_MS } from '@/lib/datetime';
import { formatFractionAsPercent, formatMoney } from '@/lib/units';

const NOW_REFRESH_MS = 60_000;

/** A measured charge settles a hair under its target, so "full" allows one percent. */
const FULL_TOLERANCE = 0.01;

interface SiteStatusProps {
  siteId: number;
}

/**
 * Live figures for the header. Each one hides while it loads or when it has no
 * data, because the dashboard is where a missing value gets explained.
 */
export function SiteStatus({ siteId }: SiteStatusProps) {
  const { data: devices } = useDevices(siteId);
  const batteries =
    devices?.filter((device): device is BatteryDevice => device.type === 'battery') ?? [];

  return (
    <div className="hidden items-center gap-4 md:flex">
      <SpotPriceIndicator />
      {batteries.map((battery) => (
        <BatteryIndicator key={battery.id} siteId={siteId} battery={battery} />
      ))}
      <SavingsIndicator siteId={siteId} />
    </div>
  );
}

function SpotPriceIndicator() {
  const { t, i18n } = useTranslation();
  const { data: prices } = useSpotPrices();
  const now = useNow(NOW_REFRESH_MS);

  const current = prices?.findLast((price) => {
    const startsAt = new Date(price.startsAt).getTime();
    return startsAt <= now && now < startsAt + STEP_DURATION_MS;
  });
  if (!current) return null;

  // Whole crowns, as the spot price chart writes them.
  const price = new Intl.NumberFormat(i18n.language, { maximumFractionDigits: 0 }).format(
    current.priceCzkMwh,
  );

  return (
    <Indicator icon={<ZapIcon />} tooltip={t('ote.current')}>
      {price} <Unit>{t('ote.unit_czk')}</Unit>
    </Indicator>
  );
}

interface BatteryIndicatorProps {
  siteId: number;
  battery: BatteryDevice;
}

function BatteryIndicator({ siteId, battery }: BatteryIndicatorProps) {
  const { t, i18n } = useTranslation();
  const { data: state } = useBatteryState(siteId, battery.id);

  if (!state) return null;

  // Full means the usable ceiling, which is all the optimiser will ever charge to.
  const isFull = state.stateOfCharge >= battery.maxStateOfCharge - FULL_TOLERANCE;

  return (
    <Indicator
      icon={
        state.chargeKw > 0 ? (
          <BatteryChargingIcon />
        ) : isFull ? (
          <BatteryFullIcon />
        ) : (
          <BatteryLowIcon />
        )
      }
      tooltip={t('battery_state.meter_label', { name: battery.name })}
    >
      {formatFractionAsPercent(state.stateOfCharge, i18n.language)}
    </Indicator>
  );
}

function SavingsIndicator({ siteId }: SiteStatusProps) {
  const { t, i18n } = useTranslation();
  const { data: savings } = useTodaySavings(siteId);

  if (!savings) return null;

  return (
    <Indicator icon={<PiggyBankIcon />} tooltip={t('optimization.saved_today')}>
      {formatMoney(savings.savingsCzk + savings.restrictionSavingsCzk, i18n.language)}{' '}
      <Unit>{t('optimization.unit_money')}</Unit>
    </Indicator>
  );
}

interface IndicatorProps {
  icon: ReactNode;
  tooltip: string;
  children: ReactNode;
}

function Indicator({ icon, tooltip, children }: IndicatorProps) {
  return (
    <Tooltip>
      <TooltipTrigger
        render={
          <span className="flex items-center gap-1.5 text-sm font-medium tabular-nums [&_svg]:size-4 [&_svg]:text-muted-foreground">
            {icon}
            <span>{children}</span>
          </span>
        }
      />
      <TooltipContent side="bottom">{tooltip}</TooltipContent>
    </Tooltip>
  );
}

function Unit({ children }: { children: ReactNode }) {
  return <span className="font-normal text-muted-foreground">{children}</span>;
}
