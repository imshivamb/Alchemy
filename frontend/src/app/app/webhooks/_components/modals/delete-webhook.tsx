import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { FastAPIWebhook } from "@/types/webhook.types";

interface DeleteWebhookModalProps {
  open: boolean;
  onClose: () => void;
  onConfirm: (webhook: FastAPIWebhook) => Promise<void>;
  webhookName: string;
  webhook: FastAPIWebhook;
}

export function DeleteWebhookModal({
  open,
  onClose,
  onConfirm,
  webhookName,
  webhook,
}: DeleteWebhookModalProps) {
  return (
    <AlertDialog open={open} onOpenChange={onClose}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Delete Webhook</AlertDialogTitle>
          <AlertDialogDescription>
            Are you sure you want to delete &quot;{webhookName}&quot;? This
            action cannot be undone.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={() => onConfirm(webhook)}>
            Delete
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
