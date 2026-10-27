import { Link, useMatches, useParams } from '@tanstack/react-router';
import { createElement, Fragment } from 'react';
import { useTranslation } from 'react-i18next';

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb';
import { SidebarTrigger } from '@/components/ui/sidebar';

import { SiteStatus } from './site-status';

export function AppHeader() {
  const { t } = useTranslation();
  const { siteId } = useParams({ strict: false });
  // Each route names its own level via `staticData.breadcrumb`.
  const crumbs = useMatches({
    select: (matches) =>
      matches.flatMap(({ id, pathname, staticData: { breadcrumb } }) =>
        breadcrumb ? [{ id, pathname, breadcrumb }] : [],
      ),
  });
  const actions = useMatches({
    select: (matches) =>
      matches.findLast((match) => match.staticData.headerActions)?.staticData.headerActions,
  });

  return (
    <header className="flex h-14 shrink-0 items-center gap-2 border-b px-4">
      <SidebarTrigger className="-ml-1" />
      <Breadcrumb className="min-w-0">
        <BreadcrumbList>
          {crumbs.map((crumb, index) => {
            const label = t(crumb.breadcrumb);
            const isLast = index === crumbs.length - 1;

            return (
              <Fragment key={crumb.id}>
                {index > 0 && <BreadcrumbSeparator />}
                <BreadcrumbItem>
                  {isLast ? (
                    <BreadcrumbPage>{label}</BreadcrumbPage>
                  ) : (
                    <BreadcrumbLink render={<Link to={crumb.pathname}>{label}</Link>} />
                  )}
                </BreadcrumbItem>
              </Fragment>
            );
          })}
        </BreadcrumbList>
      </Breadcrumb>
      <div className="ml-auto flex shrink-0 items-center gap-6">
        {siteId !== undefined && <SiteStatus siteId={siteId} />}
        {actions && (
          <div className="flex items-center gap-2">
            {/* A module-level component from route static data, so its identity is stable
                across renders; JSX would trip the compiler's static-components lint. */}
            {createElement(actions)}
          </div>
        )}
      </div>
    </header>
  );
}
