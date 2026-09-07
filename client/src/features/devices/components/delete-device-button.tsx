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

import { type Device, useDeleteDevice } from '../api';

interface DeleteDeviceButtonProps {
  siteId: number;
  device: Device;
}

export function DeleteDeviceButton({ siteId, device }: DeleteDeviceButtonProps) {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const deleteDevice = useDeleteDevice(siteId);

  const onConfirm = () => {
    deleteDevice.mutate(device.id, {
      onSuccess: () => {
        toast.success(t('devices.deleted', { name: device.name }));
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
          <Button variant="ghost" size="icon-sm" aria-label={t('devices.delete')}>
            <Trash2Icon />
          </Button>
        }
      />
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{t('devices.delete_title', { name: device.name })}</AlertDialogTitle>
          <AlertDialogDescription>{t('devices.delete_description')}</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={deleteDevice.isPending}>
            {t('devices.cancel')}
          </AlertDialogCancel>
          {/* Not a Close primitive, so the dialog stays open until the mutation
              settles and `onSuccess` closes it. */}
          <AlertDialogAction
            variant="destructive"
            disabled={deleteDevice.isPending}
            onClick={onConfirm}
          >
            {deleteDevice.isPending && <Loader2Icon className="animate-spin" aria-hidden />}
            {t('devices.delete')}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
