import { LogOutIcon, MoreVerticalIcon } from 'lucide-react';
import { useTranslation } from 'react-i18next';

import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { SidebarMenu, SidebarMenuButton, SidebarMenuItem } from '@/components/ui/sidebar';
import { useLogout } from '@/features/auth/api';
import { useAuthStore } from '@/features/auth/store';

export function UserMenu() {
  const { t } = useTranslation();
  const user = useAuthStore((state) => state.user);
  const logout = useLogout();

  if (!user) return null;

  const initials = `${user.firstName.charAt(0)}${user.lastName.charAt(0)}`.toUpperCase();

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger
            render={
              <SidebarMenuButton size="lg">
                <Avatar className="size-8 rounded-lg">
                  <AvatarFallback className="rounded-lg">{initials}</AvatarFallback>
                </Avatar>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-medium">
                    {user.firstName} {user.lastName}
                  </span>
                  <span className="text-muted-foreground truncate text-xs">{user.email}</span>
                </div>
                <MoreVerticalIcon className="ml-auto size-4" aria-hidden />
              </SidebarMenuButton>
            }
          />

          <DropdownMenuContent side="top" align="end">
            <DropdownMenuItem
              onSelect={() => {
                logout.mutate();
              }}
            >
              <LogOutIcon aria-hidden />
              {t('nav.logout')}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  );
}
