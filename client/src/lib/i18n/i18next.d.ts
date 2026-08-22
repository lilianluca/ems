import type { cs } from './locales/cs';

declare module 'i18next' {
  interface CustomTypeOptions {
    defaultNS: 'translation';
    resources: { translation: typeof cs };
  }
}
