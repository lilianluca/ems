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
