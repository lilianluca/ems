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

import { type Appliance, useDeleteAppliance } from '../api';

interface DeleteApplianceButtonProps {
  siteId: number;
  appliance: Appliance;
}

export function DeleteApplianceButton({ siteId, appliance }: DeleteApplianceButtonProps) {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const deleteAppliance = useDeleteAppliance(siteId);

  const onConfirm = () => {
    deleteAppliance.mutate(appliance.id, {
      onSuccess: () => {
        toast.success(t('appliances.deleted', { name: appliance.name }));
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
          <Button variant="ghost" size="icon-sm" aria-label={t('appliances.delete')}>
            <Trash2Icon />
          </Button>
        }
      />
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>
            {t('appliances.delete_title', { name: appliance.name })}
          </AlertDialogTitle>
          <AlertDialogDescription>{t('appliances.delete_description')}</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={deleteAppliance.isPending}>
            {t('appliances.cancel')}
          </AlertDialogCancel>
          {/* Not a Close primitive, so the dialog stays open until the mutation
              settles and `onSuccess` closes it. */}
          <AlertDialogAction
            variant="destructive"
            disabled={deleteAppliance.isPending}
            onClick={onConfirm}
          >
            {deleteAppliance.isPending && <Loader2Icon className="animate-spin" aria-hidden />}
            {t('appliances.delete')}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
