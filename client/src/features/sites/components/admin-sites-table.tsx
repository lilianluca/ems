import { createColumnHelper, tableFeatures, useTable } from '@tanstack/react-table';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

import type { Site } from '../api';
import { DeleteSiteButton } from './delete-site-button';

// The server paginates and the table renders exactly what it is given.
const features = tableFeatures({});

const columnHelper = createColumnHelper<typeof features, Site>();

const SKELETON_ROWS = 5;

interface AdminSitesTableProps {
  sites: Site[];
  isLoading: boolean;
}

export function AdminSitesTable({ sites, isLoading }: AdminSitesTableProps) {
  const { t, i18n } = useTranslation();

  const columns = useMemo(
    () =>
      columnHelper.columns([
        columnHelper.accessor('name', {
          header: () => t('sites.column_name'),
          cell: (info) => <span className="font-medium">{info.getValue()}</span>,
        }),
        columnHelper.accessor(
          (site) => `${site.latitude.toFixed(4)}, ${site.longitude.toFixed(4)}`,
          {
            id: 'coordinates',
            header: () => t('sites.column_coordinates'),
            cell: (info) => (
              <span className="text-muted-foreground tabular-nums">{info.getValue()}</span>
            ),
          },
        ),
        columnHelper.accessor('createdAt', {
          header: () => t('sites.column_created'),
          cell: (info) => (
            <span className="text-muted-foreground">
              {new Date(info.getValue()).toLocaleDateString(i18n.language)}
            </span>
          ),
        }),
        columnHelper.display({
          id: 'actions',
          header: () => <span className="sr-only">{t('sites.column_actions')}</span>,
          cell: (info) => (
            <div className="flex justify-end">
              <DeleteSiteButton site={info.row.original} />
            </div>
          ),
        }),
      ]),
    [t, i18n.language],
  );

  const table = useTable({ features, columns, data: sites });
  const rows = table.getRowModel().rows;

  return (
    <Table>
      <TableHeader>
        {table.getHeaderGroups().map((headerGroup) => (
          <TableRow key={headerGroup.id}>
            {headerGroup.headers.map((header) => (
              <TableHead key={header.id}>
                <table.FlexRender header={header} />
              </TableHead>
            ))}
          </TableRow>
        ))}
      </TableHeader>

      <TableBody>
        {isLoading &&
          Array.from({ length: SKELETON_ROWS }, (_, rowIndex) => (
            <TableRow key={`skeleton-${String(rowIndex)}`}>
              {columns.map((_column, columnIndex) => (
                <TableCell key={`skeleton-${String(rowIndex)}-${String(columnIndex)}`}>
                  <Skeleton className="h-4 w-24" />
                </TableCell>
              ))}
            </TableRow>
          ))}

        {!isLoading && rows.length === 0 && (
          <TableRow>
            <TableCell colSpan={columns.length} className="text-muted-foreground py-8 text-center">
              {t('sites.empty')}
            </TableCell>
          </TableRow>
        )}

        {!isLoading &&
          rows.map((row) => (
            <TableRow key={row.id}>
              {row.getAllCells().map((cell) => (
                <TableCell key={cell.id}>
                  <table.FlexRender cell={cell} />
                </TableCell>
              ))}
            </TableRow>
          ))}
      </TableBody>
    </Table>
  );
}
