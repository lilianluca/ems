import { Link, useMatchRoute, useParams } from '@tanstack/react-router';
import {
  LayoutDashboardIcon,
  MapPinIcon,
  PiggyBankIcon,
  PlugIcon,
  SettingsIcon,
  UsersIcon,
  WashingMachineIcon,
} from 'lucide-react';
import { useTranslation } from 'react-i18next';

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from '@/components/ui/sidebar';
import { useAuthStore } from '@/features/auth/store';

import { SiteSwitcher } from './site-switcher';
import { UserMenu } from './user-menu';

const siteNavGroups = [
  {
    labelKey: 'nav.group_monitoring',
    items: [
      { to: '/sites/$siteId/dashboard', labelKey: 'nav.dashboard', icon: LayoutDashboardIcon },
      { to: '/sites/$siteId/savings', labelKey: 'nav.savings', icon: PiggyBankIcon },
    ],
  },
  {
    labelKey: 'nav.group_configuration',
    items: [
      { to: '/sites/$siteId/devices', labelKey: 'nav.devices', icon: PlugIcon },
      { to: '/sites/$siteId/appliances', labelKey: 'nav.appliances', icon: WashingMachineIcon },
      { to: '/sites/$siteId/settings', labelKey: 'nav.settings', icon: SettingsIcon },
    ],
  },
] as const;

const adminNavItems = [
  { to: '/admin/users', labelKey: 'nav.users', icon: UsersIcon },
  { to: '/admin/sites', labelKey: 'nav.manage_sites', icon: MapPinIcon },
] as const;

export function AppSidebar() {
  const { t } = useTranslation();
  const { siteId } = useParams({ strict: false });
  const matchRoute = useMatchRoute();
  const role = useAuthStore((state) => state.user?.role);

  const siteParams = { siteId: Number(siteId) };

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader>
        <SiteSwitcher />
      </SidebarHeader>

      <SidebarContent>
        {siteId &&
          siteNavGroups.map((group) => (
            <SidebarGroup key={group.labelKey}>
              <SidebarGroupLabel>{t(group.labelKey)}</SidebarGroupLabel>
              <SidebarMenu className="gap-1">
                {group.items.map(({ to, labelKey, icon: Icon }) => (
                  <SidebarMenuItem key={to}>
                    <SidebarMenuButton
                      tooltip={t(labelKey)}
                      isActive={!!matchRoute({ to, fuzzy: true })}
                      render={
                        <Link to={to} params={siteParams}>
                          <Icon aria-hidden />
                          <span>{t(labelKey)}</span>
                        </Link>
                      }
                    />
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroup>
          ))}

        {role === 'admin' && (
          <SidebarGroup>
            <SidebarGroupLabel>{t('nav.group_administration')}</SidebarGroupLabel>
            <SidebarMenu className="gap-1">
              {adminNavItems.map(({ to, labelKey, icon: Icon }) => (
                <SidebarMenuItem key={to}>
                  <SidebarMenuButton
                    tooltip={t(labelKey)}
                    isActive={!!matchRoute({ to, fuzzy: true })}
                    render={
                      <Link to={to}>
                        <Icon aria-hidden />
                        <span>{t(labelKey)}</span>
                      </Link>
                    }
                  />
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroup>
        )}
      </SidebarContent>

      <SidebarFooter>
        <UserMenu />
      </SidebarFooter>

      <SidebarRail />
    </Sidebar>
  );
}
