import i18next from 'i18next';
import { initReactI18next } from 'react-i18next';

import { cs } from './locales/cs';
import { en } from './locales/en';

export const SUPPORTED_LANGUAGES = ['cs', 'en'] as const;
export type Language = (typeof SUPPORTED_LANGUAGES)[number];

/** Endonyms — a language is always listed in its own language, never translated. */
export const LANGUAGE_NAMES: Record<Language, string> = {
  cs: 'Čeština',
  en: 'English',
};

const STORAGE_KEY = 'language';
const DEFAULT_LANGUAGE: Language = 'cs';

function isLanguage(value: string | null): value is Language {
  return SUPPORTED_LANGUAGES.some((language) => language === value);
}

function readStoredLanguage(): Language | undefined {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return isLanguage(stored) ? stored : undefined;
  } catch {
    // Private mode or blocked site data — fall back to the default.
    return undefined;
  }
}

const initialLanguage = readStoredLanguage() ?? DEFAULT_LANGUAGE;

void i18next.use(initReactI18next).init({
  resources: {
    cs: { translation: cs },
    en: { translation: en },
  },
  lng: initialLanguage,
  fallbackLng: 'en',
  interpolation: { escapeValue: false }, // React escapes by default
});

// Keeps screen readers and browser translation from misreading the page.
document.documentElement.lang = initialLanguage;

/** Switches the active language and remembers the choice across reloads. */
export async function setLanguage(language: Language): Promise<void> {
  await i18next.changeLanguage(language);
  document.documentElement.lang = language;
  try {
    localStorage.setItem(STORAGE_KEY, language);
  } catch {
    // Persistence is a convenience; the switch itself still applies.
  }
}

export default i18next;
