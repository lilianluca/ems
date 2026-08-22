import {
  LanguagesIcon,
  LogOutIcon,
  MonitorIcon,
  MoonIcon,
  MoreVerticalIcon,
  SunIcon,
  SunMoonIcon,
} from 'lucide-react';
import { useTranslation } from 'react-i18next';

import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { SidebarMenu, SidebarMenuButton, SidebarMenuItem } from '@/components/ui/sidebar';
import { useLogout } from '@/features/auth/api';
import { useAuthStore } from '@/features/auth/store';
import { type Language, LANGUAGE_NAMES, setLanguage, SUPPORTED_LANGUAGES } from '@/lib/i18n';
import { type Theme, THEMES, useThemeStore } from '@/lib/theme';

const THEME_ICONS: Record<Theme, typeof SunIcon> = {
  light: SunIcon,
  dark: MoonIcon,
  system: MonitorIcon,
};

export function UserMenu() {
  const { t, i18n } = useTranslation();
  const user = useAuthStore((state) => state.user);
  const theme = useThemeStore((state) => state.theme);
  const setTheme = useThemeStore((state) => state.setTheme);
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

          <DropdownMenuContent side="top" align="end" className="min-w-56">
            {/* Repeats the trigger, which shows only the avatar while collapsed. */}
            <div className="flex items-center gap-2 px-1.5 py-1.5 text-sm">
              <Avatar className="size-8 rounded-lg">
                <AvatarFallback className="rounded-lg">{initials}</AvatarFallback>
              </Avatar>
              <div className="grid flex-1 text-left leading-tight">
                <span className="truncate font-medium">
                  {user.firstName} {user.lastName}
                </span>
                <span className="text-muted-foreground truncate text-xs">{user.email}</span>
              </div>
            </div>

            <DropdownMenuSeparator />

            <DropdownMenuSub>
              <DropdownMenuSubTrigger>
                <LanguagesIcon aria-hidden />
                {t('nav.language')}
              </DropdownMenuSubTrigger>
              <DropdownMenuSubContent>
                <DropdownMenuRadioGroup
                  value={i18n.resolvedLanguage}
                  onValueChange={(value) => {
                    void setLanguage(value as Language);
                  }}
                >
                  {SUPPORTED_LANGUAGES.map((language) => (
                    <DropdownMenuRadioItem key={language} value={language}>
                      {LANGUAGE_NAMES[language]}
                    </DropdownMenuRadioItem>
                  ))}
                </DropdownMenuRadioGroup>
              </DropdownMenuSubContent>
            </DropdownMenuSub>

            <DropdownMenuSub>
              <DropdownMenuSubTrigger>
                <SunMoonIcon aria-hidden />
                {t('nav.theme')}
              </DropdownMenuSubTrigger>
              <DropdownMenuSubContent>
                <DropdownMenuRadioGroup
                  value={theme}
                  onValueChange={(value) => {
                    setTheme(value as Theme);
                  }}
                >
                  {THEMES.map((option) => {
                    const Icon = THEME_ICONS[option];
                    return (
                      <DropdownMenuRadioItem key={option} value={option}>
                        <Icon aria-hidden />
                        {t(`theme.${option}`)}
                      </DropdownMenuRadioItem>
                    );
                  })}
                </DropdownMenuRadioGroup>
              </DropdownMenuSubContent>
            </DropdownMenuSub>

            <DropdownMenuSeparator />

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
