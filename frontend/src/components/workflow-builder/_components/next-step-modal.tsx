import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Aperture, GitBranch } from "lucide-react";

interface NextStepModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectAction: () => void;
  onSelectCondition?: () => void;
}

const NextStepModal = ({
  isOpen,
  onClose,
  onSelectAction,
  onSelectCondition,
}: NextStepModalProps) => {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[400px]">
        <DialogHeader>
          <DialogTitle>Add next step</DialogTitle>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <Button
            variant="outline"
            className="justify-start h-auto p-4"
            onClick={onSelectAction}
          >
            <div className="flex items-start gap-3">
              <Aperture className="h-5 w-5 mt-0.5 text-blue-500" />
              <div className="text-left">
                <h3 className="font-medium mb-1">Action</h3>
                <p className="text-sm text-gray-500">
                  Add an action to perform when the trigger conditions are met
                </p>
              </div>
            </div>
          </Button>

          {onSelectCondition && (
            <Button
              variant="outline"
              className="justify-start h-auto p-4"
              onClick={onSelectCondition}
            >
              <div className="flex items-start gap-3">
                <GitBranch className="h-5 w-5 mt-0.5 text-purple-500" />
                <div className="text-left">
                  <h3 className="font-medium mb-1">Condition</h3>
                  <p className="text-sm text-gray-500">
                    Add conditional logic to control the workflow path
                  </p>
                </div>
              </div>
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default NextStepModal;
