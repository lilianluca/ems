import { create } from 'zustand';

export const THEMES = ['light', 'dark', 'system'] as const;
export type Theme = (typeof THEMES)[number];

const STORAGE_KEY = 'theme';
const DEFAULT_THEME: Theme = 'system';

function isTheme(value: string | null): value is Theme {
  return value !== null && THEMES.includes(value as Theme);
}

function readStoredTheme(): Theme | undefined {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return isTheme(stored) ? stored : undefined;
  } catch {
    // Private mode or blocked site data — fall back to the default.
    return undefined;
  }
}

function prefersDark(): MediaQueryList {
  return window.matchMedia('(prefers-color-scheme: dark)');
}

/** Tailwind's dark variant keys off a `dark` class on the document element. */
function applyTheme(theme: Theme): void {
  const dark = theme === 'dark' || (theme === 'system' && prefersDark().matches);
  document.documentElement.classList.toggle('dark', dark);
}

interface ThemeState {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

const initialTheme = readStoredTheme() ?? DEFAULT_THEME;

// The inline script in index.html has already painted this; re-applying keeps
// the class correct if storage changed since, and costs nothing.
applyTheme(initialTheme);

export const useThemeStore = create<ThemeState>((set) => ({
  theme: initialTheme,
  setTheme: (theme) => {
    applyTheme(theme);
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch {
      // Persistence is a convenience; the switch itself still applies.
    }
    set({ theme });
  },
}));

// Follow the OS only while the user has not pinned a specific theme.
prefersDark().addEventListener('change', () => {
  if (useThemeStore.getState().theme === 'system') {
    applyTheme('system');
  }
});
