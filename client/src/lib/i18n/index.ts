import i18next from 'i18next';
import { initReactI18next } from 'react-i18next';

import { cs } from './locales/cs';
import { en } from './locales/en';

export const SUPPORTED_LANGUAGES = ['cs', 'en'] as const;
export type Language = (typeof SUPPORTED_LANGUAGES)[number];

void i18next.use(initReactI18next).init({
  resources: {
    cs: { translation: cs },
    en: { translation: en },
  },
  lng: 'cs',
  fallbackLng: 'en',
  interpolation: { escapeValue: false }, // React escapes by default
});

export default i18next;
