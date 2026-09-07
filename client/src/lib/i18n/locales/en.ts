import type { ErrorCode } from '@/api/errors';

/** Every error code must have a translation — missing keys fail the build. */
const errors: Record<ErrorCode, string> = {
  // --- Auth ---
  invalid_credentials: 'Invalid email or password.',
  inactive_user: 'Account is deactivated. Please contact an administrator.',
  invalid_token: 'Session has expired. Please log in again.',
  missing_token: 'Session has expired. Please log in again.',
  invalid_refresh_token: 'Session has expired. Please log in again.',
  missing_refresh_token: 'Session has expired. Please log in again.',

  // --- Devices ---
  device_not_found: 'Device not found.',
  device_type_mismatch: 'Device type does not match the expected type.',

  // --- OTE ---
  ote_fetch_error: 'Failed to fetch data from OTE. Please try again later.',
  ote_fetch_too_soon: 'Data from OTE cannot be fetched this frequently. Please try again later.',

  // --- Sites ---
  site_not_found: 'Site not found.',
  membership_not_found: 'User is not a member of this site.',
  insufficient_site_permissions: 'You do not have permission for this action.',
  user_already_member: 'User is already a member of this site.',

  // --- Users ---
  user_already_exists: 'A user with this email already exists.',
  user_not_found: 'User not found.',

  // --- Weather ---
  weather_fetch_error: 'Failed to fetch weather data. Please try again later.',
  weather_fetch_too_soon: 'Weather data cannot be fetched this frequently. Please try again later.',

  // --- Generic ---
  not_found: 'Requested record not found.',
  forbidden: 'You do not have permission for this action.',
  unauthorized: 'You do not have permission for this action.',
  conflict: 'Operation cannot be performed, record conflicts with existing one.',
  validation_error: 'Please check the entered data.',
  internal_error: 'An unexpected error occurred on the server.',
};

export const en = {
  errors,
  // Errors that have no server code.
  client: {
    network_error: 'Failed to connect to the server.',
  },

  validation: {
    email_required: 'E-mail is required.',
    email_invalid: 'Enter a valid email address.',
    password_required: 'Password is required.',
    password_too_short: 'Password must be at least 12 characters.',
    first_name_required: 'First name is required.',
    last_name_required: 'Last name is required.',
    site_name_required: 'Site name is required.',
    latitude_invalid: 'Latitude must be between -90 and 90.',
    longitude_invalid: 'Longitude must be between -180 and 180.',
    owner_required: 'Select a site owner.',
    device_name_required: 'Device name is required.',
    power_positive: 'Enter a positive number.',
    tilt_invalid: 'Tilt must be between 0 and 90°.',
    azimuth_invalid: 'Azimuth must be between 0 and 360°.',
    percent_invalid: 'Enter a percentage.',
    state_of_charge_range: 'Maximum charge must be higher than minimum charge.',
  },

  auth: {
    login_title: 'Sign in',
    login_description: 'Enter your credentials.',
    email: 'Email',
    email_placeholder: 'name@company.com',
    password: 'Password',
    submit: 'Sign in',
    submitting: 'Signing in…',
  },

  users: {
    title: 'Users',
    description: 'Accounts are created here — the system has no public registration.',
    new: 'New user',
    empty: 'No users yet.',
    pagination: '{{from}}–{{to}} of {{total}}',
    previous: 'Previous',
    next: 'Next',

    column_name: 'Name',
    column_email: 'Email',
    column_role: 'Role',
    column_status: 'Status',
    column_created: 'Created',

    role_admin: 'Administrator',
    role_user: 'User',
    status_active: 'Active',
    status_inactive: 'Deactivated',

    create_title: 'New user',
    create_description: 'Choose a password and hand it over through a secure channel.',
    first_name: 'First name',
    last_name: 'Last name',
    email: 'Email',
    password: 'Password',
    role: 'Role',
    submit: 'Create user',
    submitting: 'Creating…',
    cancel: 'Cancel',
    created: 'User {{email}} has been created.',
  },

  sites: {
    title: 'Sites',
    description: 'Sites are created by an administrator and assigned an owner.',
    new: 'New site',
    empty: 'No sites yet.',
    pagination: '{{from}}–{{to}} of {{total}}',
    previous: 'Previous',
    next: 'Next',

    column_name: 'Name',
    column_coordinates: 'Coordinates',
    column_created: 'Created',
    column_actions: 'Actions',

    delete: 'Delete',
    delete_title: 'Delete site {{name}}?',
    delete_description:
      'Its memberships are deleted as well. Measurements in InfluxDB remain but are left without a site. This cannot be undone.',
    deleted: 'Site {{name}} has been deleted.',
    cancel: 'Cancel',

    create_title: 'New site',
    create_description: 'Coordinates drive the weather and PV generation forecasts.',
    name: 'Name',
    latitude: 'Latitude',
    longitude: 'Longitude',
    owner: 'Owner',
    select_owner: 'Select an owner',
    submit: 'Create site',
    submitting: 'Creating…',
    created: 'Site {{name}} has been created.',
  },

  chart: {
    now: 'Now',
    today: 'Today',
    tomorrow: 'Tomorrow',
  },

  ote: {
    title: 'Spot electricity price',
    description: 'OTE day-ahead market, quarter-hour blocks. Today and tomorrow.',
    price: 'Price',
    unit_czk: 'CZK/MWh',
    unit_eur: '€/MWh',
    currency: 'Currency',
    currency_czk: 'CZK',
    currency_eur: 'EUR',
    current: 'Current price',
    cheapest: 'Cheapest block',
    priciest: 'Priciest block',
    tomorrow_pending:
      "Tomorrow's prices are published in the afternoon, once the day-ahead auction clears.",
    empty: 'No prices available yet.',
    load_error: 'Prices could not be loaded.',
  },

  devices: {
    title: 'Devices',
    description: 'Device parameters feed the generation forecast and the optimisation.',
    add_pv: 'Add PV array',
    add_battery: 'Add battery',
    empty: 'No devices configured for this site yet.',

    type_pv: 'Photovoltaics',
    type_battery: 'Battery',

    name: 'Name',
    pv_name_placeholder: 'South roof',
    battery_name_placeholder: 'Home battery',

    installed_power: 'Panel power',
    inverter_power: 'Inverter power',
    tilt: 'Tilt',
    azimuth: 'Azimuth',
    capacity: 'Capacity',
    max_charge_power: 'Max charge power',
    max_discharge_power: 'Max discharge power',
    min_soc: 'Minimum charge',
    max_soc: 'Maximum charge',
    efficiency: 'Round-trip efficiency',
    usable_range: 'Usable range',

    hint_kwp: 'Peak panel power in kWp, from the installation documents.',
    hint_inverter: 'Usually somewhat lower than the panel power.',
    hint_tilt: '0° is flat, 90° is vertical. A pitched roof is usually 30–45°.',
    hint_azimuth: '0° north, 90° east, 180° south, 270° west.',
    hint_soc:
      'A battery is not cycled between empty and full. Usable energy is capacity × (max − min), and some is lost charging and discharging. Both values are on the datasheet.',

    compass_north: 'north',
    compass_northeast: 'north-east',
    compass_east: 'east',
    compass_southeast: 'south-east',
    compass_south: 'south',
    compass_southwest: 'south-west',
    compass_west: 'west',
    compass_northwest: 'north-west',

    pv_create_title: 'New PV array',
    pv_edit_title: 'Edit PV array',
    pv_description: 'A site can have several arrays — one per roof orientation.',
    battery_create_title: 'New battery',
    battery_edit_title: 'Edit battery',
    battery_description: 'Capacity is in kWh, power limits are in kW.',

    edit: 'Edit',
    delete: 'Delete',
    delete_title: 'Delete device {{name}}?',
    delete_description:
      'Forecasts computed for this device stay in the measurement store without a device. This cannot be undone.',
    deleted: 'Device {{name}} has been deleted.',
    created: 'Device {{name}} has been created.',
    updated: 'Device {{name}} has been updated.',
    submit: 'Save',
    submitting: 'Saving…',
    cancel: 'Cancel',
  },

  forecasts: {
    title: 'Generation and consumption forecast',
    description: 'Hourly model for this site. These are predictions, not measurements.',
    generation: 'PV generation',
    consumption: 'Consumption',
    expected_generation: 'Expected generation',
    expected_consumption: 'Expected consumption',
    unit_energy: 'kWh',
    empty: 'No forecasts available for this site yet.',
    load_error: 'Forecasts could not be loaded.',
  },

  nav: {
    dashboard: 'Dashboard',
    measurements: 'Measurements',
    forecasts: 'Forecasts',
    optimization: 'Optimization',
    devices: 'Devices',
    settings: 'Settings',
    users: 'Users',
    sites: 'Sites',
    select_site: 'Select Site',
    manage_sites: 'Manage Sites',
    group_monitoring: 'Monitoring',
    group_configuration: 'Configuration',
    group_administration: 'Administration',
    logout: 'Logout',
    language: 'Language',
    theme: 'Theme',
  },

  theme: {
    light: 'Light',
    dark: 'Dark',
    system: 'System',
  },
} as const;
