import createClient from 'openapi-fetch';

import type { paths } from './schema';

export const api = createClient<paths>({
  baseUrl: '/', // Vite proxy in dev, nginx in production
});
