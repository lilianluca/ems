import type { ErrorCode } from '@/api/errors';

/** Every error code must have a translation — missing keys fail the build. */
const errors: Record<ErrorCode, string> = {
  // --- Auth ---
  invalid_credentials: 'Nesprávný e-mail nebo heslo.',
  inactive_user: 'Účet je deaktivovaný. Kontaktujte správce.',
  invalid_token: 'Přihlášení vypršelo. Přihlaste se prosím znovu.',
  missing_token: 'Přihlášení vypršelo. Přihlaste se prosím znovu.',
  invalid_refresh_token: 'Přihlášení vypršelo. Přihlaste se prosím znovu.',
  missing_refresh_token: 'Přihlášení vypršelo. Přihlaste se prosím znovu.',

  // --- Devices ---
  device_not_found: 'Zařízení nebylo nalezeno.',
  device_type_mismatch: 'Typ zařízení neodpovídá očekávanému.',

  // --- OTE ---
  ote_fetch_error: 'Nepodařilo se načíst data z OTE. Zkuste to prosím později.',
  ote_fetch_too_soon: 'Data z OTE nelze načíst tak často. Zkuste to prosím později.',

  // --- Sites ---
  site_not_found: 'Lokace nebyla nalezena.',
  membership_not_found: 'Uživatel není členem této lokace.',
  insufficient_site_permissions: 'K této akci nemáte oprávnění.',
  user_already_member: 'Uživatel je již členem této lokace.',

  // --- Users ---
  user_already_exists: 'Uživatel s tímto e-mailem už existuje.',
  user_not_found: 'Uživatel nebyl nalezen.',

  // --- Weather ---
  weather_fetch_error: 'Nepodařilo se načíst data o počasí. Zkuste to prosím později.',
  weather_fetch_too_soon: 'Data o počasí nelze načíst tak často. Zkuste to prosím později.',

  // --- Generic ---
  not_found: 'Požadovaný záznam nebyl nalezen.',
  forbidden: 'K této akci nemáte oprávnění.',
  unauthorized: 'K této akci nemáte oprávnění.',
  conflict: 'Operaci nelze provést, záznam koliduje s existujícím.',
  validation_error: 'Zkontrolujte prosím zadané údaje.',
  internal_error: 'Došlo k neočekávané chybě serveru.',
};

export const cs = {
  errors,
  // Errors that have no server code.
  client: {
    network_error: 'Nepodařilo se spojit se serverem.',
  },

  validation: {
    email_required: 'E-mail je povinný.',
    email_invalid: 'Zadejte platný e-mail.',
    password_required: 'Heslo je povinné.',
    password_too_short: 'Heslo musí mít alespoň 8 znaků.',
    first_name_required: 'Jméno je povinné.',
    last_name_required: 'Příjmení je povinné.',
  },

  auth: {
    login_title: 'Přihlášení',
    login_description: 'Zadejte své přihlašovací údaje.',
    email: 'E-mail',
    email_placeholder: 'jmeno@firma.cz',
    password: 'Heslo',
    submit: 'Přihlásit se',
    submitting: 'Přihlašuji…',
  },

  nav: {
    dashboard: 'Přehled',
    measurements: 'Měření',
    forecasts: 'Predikce',
    optimization: 'Optimalizace',
    devices: 'Zařízení',
    settings: 'Nastavení',
    users: 'Uživatelé',
    sites: 'Lokality',
    select_site: 'Vyberte lokalitu',
    manage_sites: 'Správa lokalit',
    group_monitoring: 'Monitoring',
    group_configuration: 'Konfigurace',
    group_administration: 'Správa',
    logout: 'Odhlásit se',
  },
} as const;
