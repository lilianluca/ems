import { createColumnHelper, tableFeatures, useTable } from '@tanstack/react-table';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

import type { User } from '../api';

// The server paginates and the table renders exactly what it is given, so no
// sorting, filtering or pagination features are enabled.
const features = tableFeatures({});

const columnHelper = createColumnHelper<typeof features, User>();

const SKELETON_ROWS = 5;

interface UsersTableProps {
  users: User[];
  isLoading: boolean;
}

export function UsersTable({ users, isLoading }: UsersTableProps) {
  const { t, i18n } = useTranslation();

  // `columnHelper.columns` rather than a bare array: it preserves each column's
  // value type instead of widening the union to `unknown`.
  const columns = useMemo(
    () =>
      columnHelper.columns([
        columnHelper.accessor((user) => `${user.firstName} ${user.lastName}`, {
          id: 'name',
          header: () => t('users.column_name'),
          cell: (info) => <span className="font-medium">{info.getValue()}</span>,
        }),
        columnHelper.accessor('email', {
          header: () => t('users.column_email'),
          cell: (info) => <span className="text-muted-foreground">{info.getValue()}</span>,
        }),
        columnHelper.accessor('role', {
          header: () => t('users.column_role'),
          cell: (info) =>
            info.getValue() === 'admin' ? (
              <Badge>{t('users.role_admin')}</Badge>
            ) : (
              <Badge variant="secondary">{t('users.role_user')}</Badge>
            ),
        }),
        columnHelper.accessor('isActive', {
          header: () => t('users.column_status'),
          cell: (info) =>
            info.getValue() ? (
              <Badge variant="outline">{t('users.status_active')}</Badge>
            ) : (
              <Badge variant="destructive">{t('users.status_inactive')}</Badge>
            ),
        }),
        columnHelper.accessor('createdAt', {
          header: () => t('users.column_created'),
          cell: (info) => (
            <span className="text-muted-foreground">
              {new Date(info.getValue()).toLocaleDateString(i18n.language)}
            </span>
          ),
        }),
      ]),
    [t, i18n.language],
  );

  const table = useTable({ features, columns, data: users });
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
              {t('users.empty')}
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
