import { createFileRoute, notFound, Outlet } from '@tanstack/react-router';
import { z } from 'zod';

const siteIdSchema = z.coerce.number().int().positive();

export const Route = createFileRoute('/_authenticated/sites/$siteId')({
  params: {
    parse: (params) => {
      // A non-numeric segment is a bad URL, not a crash: 404 rather than throw.
      const siteId = siteIdSchema.safeParse(params.siteId);
      if (!siteId.success) throw notFound();
      return { siteId: siteId.data };
    },
    stringify: ({ siteId }) => ({ siteId: String(siteId) }),
  },
  component: Outlet,
});
