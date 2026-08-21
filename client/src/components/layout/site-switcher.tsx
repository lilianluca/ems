import { Link, useParams } from '@tanstack/react-router';
import { CheckIcon, ChevronsUpDownIcon, ZapIcon } from 'lucide-react';
import { useTranslation } from 'react-i18next';

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { SidebarMenu, SidebarMenuButton, SidebarMenuItem } from '@/components/ui/sidebar';
import { Skeleton } from '@/components/ui/skeleton';
import { useSites } from '@/features/sites/api';

export function SiteSwitcher() {
  const { t } = useTranslation();
  const { siteId } = useParams({ strict: false });
  const { data: sites, isPending } = useSites();

  if (isPending) {
    return <Skeleton className="h-12 w-full" />;
  }

  const current = sites?.find((site) => site.id === Number(siteId));

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger
            render={
              <SidebarMenuButton size="lg">
                <div className="bg-sidebar-primary text-sidebar-primary-foreground flex aspect-square size-8 items-center justify-center rounded-lg">
                  <ZapIcon className="size-4" aria-hidden />
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-medium">
                    {current?.name ?? t('nav.select_site')}
                  </span>
                  {/* TODO: Display actual city name */}
                  <span className="text-muted-foreground truncate text-xs">City</span>
                </div>
                <ChevronsUpDownIcon className="ml-auto size-4" aria-hidden />
              </SidebarMenuButton>
            }
          />

          <DropdownMenuContent align="start">
            <DropdownMenuGroup>
              <DropdownMenuLabel className="text-muted-foreground text-xs">
                {t('nav.sites')}
              </DropdownMenuLabel>

              {sites?.map((site) => (
                <DropdownMenuItem
                  key={site.id}
                  render={
                    <Link to="/sites/$siteId/dashboard" params={{ siteId: site.id }}>
                      <span className="flex-1 truncate">{site.name}</span>
                      {site.id === current?.id && <CheckIcon className="size-4" aria-hidden />}
                    </Link>
                  }
                />
              ))}
            </DropdownMenuGroup>

            <DropdownMenuSeparator />
            <DropdownMenuItem render={<Link to="/sites">{t('nav.manage_sites')}</Link>} />
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  );
}
