import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { apps } from "@/config/apps.config";

type AccountConnectionModalProps = {
  isOpen: boolean;
  onClose: () => void;
  appId: string;
  onConnect: () => void;
};

export const AccountConnectionModal = ({
  isOpen,
  onClose,
  appId,
  onConnect,
}: AccountConnectionModalProps) => {
  const app = apps.find((a) => a.id === appId);
  if (!app) return null;

  const handleConnect = () => {
    // Here you'll implement OAuth or other authentication flows
    onConnect();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <app.icon className="h-5 w-5" />
            Connect {app.name}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="text-center">
            <app.icon className="h-12 w-12 mx-auto mb-4" />
            <h3 className="font-medium mb-2">
              Connect your {app.name} account
            </h3>
            <p className="text-sm text-gray-500">
              Allow Alchemy to access your {app.name} account to automate your
              workflows
            </p>
          </div>

          <Button className="w-full" onClick={handleConnect}>
            Connect {app.name}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};
