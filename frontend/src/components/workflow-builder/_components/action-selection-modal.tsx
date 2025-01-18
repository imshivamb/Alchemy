import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ChevronRight } from "lucide-react";
import { apps } from "@/config/apps.config";

type ActionSelectionModalProps = {
  isOpen: boolean;
  onClose: () => void;
  selectedAppId: string;
  onSelectAction: (actionId: string) => void;
};

export const ActionSelectionModal = ({
  isOpen,
  onClose,
  selectedAppId,
  onSelectAction,
}: ActionSelectionModalProps) => {
  const app = apps.find((a) => a.id === selectedAppId);
  if (!app) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <app.icon className="h-5 w-5" />
            Choose a {app.name} action
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-2">
          {app.actions?.map((action) => (
            <button
              key={action.id}
              onClick={() => onSelectAction(action.id)}
              className="w-full flex items-center justify-between p-4 rounded-lg border hover:border-blue-500 hover:shadow-sm transition-all bg-white group"
            >
              <div className="flex-1">
                <h3 className="font-medium text-sm group-hover:text-blue-600">
                  {action.name}
                </h3>
                <p className="text-sm text-gray-500 mt-1">
                  {action.description}
                </p>
              </div>
              <ChevronRight className="h-5 w-5 text-gray-400 group-hover:text-blue-500" />
            </button>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
};
