import { Link, useMatchRoute, useParams } from '@tanstack/react-router';
import {
  LayoutDashboardIcon,
  MapPinIcon,
  PiggyBankIcon,
  PlugIcon,
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
} from '@/components/ui/sidebar';
import { useAuthStore } from '@/features/auth/store';

import { SiteSwitcher } from './site-switcher';
import { UserMenu } from './user-menu';

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
        {siteId && (
          <>
            <SidebarGroup>
              <SidebarGroupLabel>{t('nav.group_monitoring')}</SidebarGroupLabel>
              <SidebarMenu>
                <SidebarMenuItem>
                  <SidebarMenuButton
                    tooltip={t('nav.dashboard')}
                    isActive={!!matchRoute({ to: '/sites/$siteId/dashboard', params: siteParams })}
                    render={
                      <Link to="/sites/$siteId/dashboard" params={siteParams}>
                        <LayoutDashboardIcon aria-hidden />
                        <span>{t('nav.dashboard')}</span>
                      </Link>
                    }
                  />
                </SidebarMenuItem>

                <SidebarMenuItem>
                  <SidebarMenuButton
                    tooltip={t('nav.savings')}
                    isActive={!!matchRoute({ to: '/sites/$siteId/savings', params: siteParams })}
                    render={
                      <Link to="/sites/$siteId/savings" params={siteParams}>
                        <PiggyBankIcon aria-hidden />
                        <span>{t('nav.savings')}</span>
                      </Link>
                    }
                  />
                </SidebarMenuItem>
              </SidebarMenu>
            </SidebarGroup>

            <SidebarGroup>
              <SidebarGroupLabel>{t('nav.group_configuration')}</SidebarGroupLabel>
              <SidebarMenu>
                <SidebarMenuItem>
                  <SidebarMenuButton
                    tooltip={t('nav.devices')}
                    isActive={!!matchRoute({ to: '/sites/$siteId/devices', params: siteParams })}
                    render={
                      <Link to="/sites/$siteId/devices" params={siteParams}>
                        <PlugIcon aria-hidden />
                        <span>{t('nav.devices')}</span>
                      </Link>
                    }
                  />
                </SidebarMenuItem>

                <SidebarMenuItem>
                  <SidebarMenuButton
                    tooltip={t('nav.appliances')}
                    isActive={!!matchRoute({ to: '/sites/$siteId/appliances', params: siteParams })}
                    render={
                      <Link to="/sites/$siteId/appliances" params={siteParams}>
                        <WashingMachineIcon aria-hidden />
                        <span>{t('nav.appliances')}</span>
                      </Link>
                    }
                  />
                </SidebarMenuItem>
              </SidebarMenu>
            </SidebarGroup>
          </>
        )}

        {role === 'admin' && (
          <SidebarGroup>
            <SidebarGroupLabel>{t('nav.group_administration')}</SidebarGroupLabel>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton
                  tooltip={t('nav.users')}
                  isActive={!!matchRoute({ to: '/admin/users' })}
                  render={
                    <Link to="/admin/users">
                      <UsersIcon aria-hidden />
                      <span>{t('nav.users')}</span>
                    </Link>
                  }
                />
              </SidebarMenuItem>

              <SidebarMenuItem>
                <SidebarMenuButton
                  tooltip={t('nav.manage_sites')}
                  isActive={!!matchRoute({ to: '/admin/sites' })}
                  render={
                    <Link to="/admin/sites">
                      <MapPinIcon aria-hidden />
                      <span>{t('nav.manage_sites')}</span>
                    </Link>
                  }
                />
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroup>
        )}
      </SidebarContent>

      <SidebarFooter>
        <UserMenu />
      </SidebarFooter>
    </Sidebar>
  );
}
