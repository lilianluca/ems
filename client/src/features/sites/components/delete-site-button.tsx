import { Loader2Icon, Trash2Icon } from 'lucide-react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { toast } from 'sonner';

import { translateError } from '@/api/errors';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { Button } from '@/components/ui/button';

import { useDeleteSite } from '../admin-api';
import type { Site } from '../api';

interface DeleteSiteButtonProps {
  site: Site;
}

export function DeleteSiteButton({ site }: DeleteSiteButtonProps) {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const deleteSite = useDeleteSite();

  const onConfirm = () => {
    deleteSite.mutate(site.id, {
      onSuccess: () => {
        toast.success(t('sites.deleted', { name: site.name }));
        setOpen(false);
      },
      onError: (error) => {
        toast.error(translateError(error));
      },
    });
  };

  return (
    <AlertDialog open={open} onOpenChange={setOpen}>
      <AlertDialogTrigger
        render={
          <Button variant="ghost" size="icon-sm" aria-label={t('sites.delete')}>
            <Trash2Icon />
          </Button>
        }
      />
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{t('sites.delete_title', { name: site.name })}</AlertDialogTitle>
          <AlertDialogDescription>{t('sites.delete_description')}</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={deleteSite.isPending}>{t('sites.cancel')}</AlertDialogCancel>
          {/* Not a Close primitive, so the dialog stays open until the
              mutation settles and `onSuccess` closes it. */}
          <AlertDialogAction
            variant="destructive"
            disabled={deleteSite.isPending}
            onClick={onConfirm}
          >
            {deleteSite.isPending && <Loader2Icon className="animate-spin" aria-hidden />}
            {t('sites.delete')}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
