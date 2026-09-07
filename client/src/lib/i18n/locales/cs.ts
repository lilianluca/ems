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
    password_too_short: 'Heslo musí mít alespoň 12 znaků.',
    first_name_required: 'Jméno je povinné.',
    last_name_required: 'Příjmení je povinné.',
    site_name_required: 'Název lokality je povinný.',
    latitude_invalid: 'Zeměpisná šířka musí být mezi -90 a 90.',
    longitude_invalid: 'Zeměpisná délka musí být mezi -180 a 180.',
    owner_required: 'Vyberte vlastníka lokality.',
    device_name_required: 'Název zařízení je povinný.',
    power_positive: 'Zadejte kladné číslo.',
    tilt_invalid: 'Sklon musí být mezi 0 a 90°.',
    azimuth_invalid: 'Azimut musí být mezi 0 a 360°.',
    percent_invalid: 'Zadejte hodnotu v procentech.',
    state_of_charge_range: 'Maximální nabití musí být vyšší než minimální.',
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

  users: {
    title: 'Uživatelé',
    description: 'Účty se zakládají zde — systém nemá veřejnou registraci.',
    new: 'Nový uživatel',
    empty: 'Zatím tu nejsou žádní uživatelé.',
    pagination: '{{from}}–{{to}} z {{total}}',
    previous: 'Předchozí',
    next: 'Další',

    column_name: 'Jméno',
    column_email: 'E-mail',
    column_role: 'Role',
    column_status: 'Stav',
    column_created: 'Vytvořen',

    role_admin: 'Správce',
    role_user: 'Uživatel',
    status_active: 'Aktivní',
    status_inactive: 'Deaktivovaný',

    create_title: 'Nový uživatel',
    create_description: 'Heslo zvolte a předejte ho uživateli bezpečnou cestou.',
    first_name: 'Jméno',
    last_name: 'Příjmení',
    email: 'E-mail',
    password: 'Heslo',
    role: 'Role',
    submit: 'Vytvořit uživatele',
    submitting: 'Vytvářím…',
    cancel: 'Zrušit',
    created: 'Uživatel {{email}} byl vytvořen.',
  },

  sites: {
    title: 'Lokality',
    description: 'Lokality zakládá správce a přiřazuje jim vlastníka.',
    new: 'Nová lokalita',
    empty: 'Zatím tu nejsou žádné lokality.',
    pagination: '{{from}}–{{to}} z {{total}}',
    previous: 'Předchozí',
    next: 'Další',

    column_name: 'Název',
    column_coordinates: 'Souřadnice',
    column_created: 'Vytvořena',
    column_actions: 'Akce',

    delete: 'Smazat',
    delete_title: 'Smazat lokalitu {{name}}?',
    delete_description:
      'Smažou se i všechna členství. Naměřená data v InfluxDB zůstanou, ale zůstanou bez lokality. Akci nelze vrátit.',
    deleted: 'Lokalita {{name}} byla smazána.',
    cancel: 'Zrušit',

    create_title: 'Nová lokalita',
    create_description: 'Souřadnice se používají pro předpověď počasí a výroby FVE.',
    name: 'Název',
    latitude: 'Zeměpisná šířka',
    longitude: 'Zeměpisná délka',
    owner: 'Vlastník',
    select_owner: 'Vyberte vlastníka',
    submit: 'Vytvořit lokalitu',
    submitting: 'Vytvářím…',
    created: 'Lokalita {{name}} byla vytvořena.',
  },

  chart: {
    now: 'Teď',
    today: 'Dnes',
    tomorrow: 'Zítra',
  },

  ote: {
    title: 'Spotová cena elektřiny',
    description: 'Denní trh OTE, čtvrthodinové bloky. Dnešek a zítřek.',
    price: 'Cena',
    unit_czk: 'Kč/MWh',
    unit_eur: '€/MWh',
    currency: 'Měna',
    currency_czk: 'CZK',
    currency_eur: 'EUR',
    current: 'Aktuální cena',
    cheapest: 'Nejlevnější blok',
    priciest: 'Nejdražší blok',
    tomorrow_pending: 'Zítřejší ceny se zveřejňují odpoledne, až proběhne aukce denního trhu.',
    empty: 'Zatím nejsou k dispozici žádné ceny.',
    load_error: 'Ceny se nepodařilo načíst.',
  },

  devices: {
    title: 'Zařízení',
    description: 'Parametry zařízení vstupují do predikce výroby a do optimalizace.',
    add_pv: 'Přidat FVE',
    add_battery: 'Přidat baterii',
    empty: 'Pro tuto lokalitu zatím nejsou zadaná žádná zařízení.',

    type_pv: 'Fotovoltaika',
    type_battery: 'Baterie',

    name: 'Název',
    pv_name_placeholder: 'Střecha jih',
    battery_name_placeholder: 'Domácí baterie',

    installed_power: 'Výkon panelů',
    inverter_power: 'Výkon střídače',
    tilt: 'Sklon',
    azimuth: 'Azimut',
    capacity: 'Kapacita',
    max_charge_power: 'Max. nabíjecí výkon',
    max_discharge_power: 'Max. vybíjecí výkon',
    min_soc: 'Minimální nabití',
    max_soc: 'Maximální nabití',
    efficiency: 'Účinnost cyklu',
    usable_range: 'Využitelný rozsah',

    hint_kwp: 'Špičkový výkon panelů v kWp podle projektu.',
    hint_inverter: 'Bývá o něco nižší než výkon panelů.',
    hint_tilt: '0° vodorovně, 90° svisle. Šikmá střecha obvykle 30–45°.',
    hint_azimuth: '0° sever, 90° východ, 180° jih, 270° západ.',
    hint_soc:
      'Baterie se necykluje mezi nulou a plným nabitím. Využitelná energie je kapacita × (max − min), a část se navíc ztratí při nabíjení a vybíjení. Hodnoty najdete v datovém listu.',

    compass_north: 'sever',
    compass_northeast: 'severovýchod',
    compass_east: 'východ',
    compass_southeast: 'jihovýchod',
    compass_south: 'jih',
    compass_southwest: 'jihozápad',
    compass_west: 'západ',
    compass_northwest: 'severozápad',

    pv_create_title: 'Nová fotovoltaika',
    pv_edit_title: 'Úprava fotovoltaiky',
    pv_description: 'Lokalita může mít víc polí — pro každou orientaci střechy jedno.',
    battery_create_title: 'Nová baterie',
    battery_edit_title: 'Úprava baterie',
    battery_description: 'Kapacita je v kWh, výkony v kW.',

    edit: 'Upravit',
    delete: 'Smazat',
    delete_title: 'Smazat zařízení {{name}}?',
    delete_description:
      'Predikce spočítané pro toto zařízení zůstanou v databázi měření bez vazby. Akci nelze vrátit.',
    deleted: 'Zařízení {{name}} bylo smazáno.',
    created: 'Zařízení {{name}} bylo vytvořeno.',
    updated: 'Zařízení {{name}} bylo upraveno.',
    submit: 'Uložit',
    submitting: 'Ukládám…',
    cancel: 'Zrušit',
  },

  forecasts: {
    title: 'Predikce výroby a spotřeby',
    description: 'Hodinový model pro tuto lokalitu. Jde o předpověď, ne o naměřené hodnoty.',
    generation: 'Výroba FVE',
    consumption: 'Spotřeba',
    expected_generation: 'Předpokládaná výroba',
    expected_consumption: 'Předpokládaná spotřeba',
    unit_energy: 'kWh',
    empty: 'Pro tuto lokalitu zatím nejsou k dispozici žádné predikce.',
    load_error: 'Predikce se nepodařilo načíst.',
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
    language: 'Jazyk',
    theme: 'Vzhled',
  },

  theme: {
    light: 'Světlý',
    dark: 'Tmavý',
    system: 'Systémový',
  },
} as const;
