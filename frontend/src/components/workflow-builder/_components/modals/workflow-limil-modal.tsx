import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";

interface WorkflowLimitModalProps {
  isOpen: boolean;
  onClose: () => void;
  limitInfo: {
    current_count: number;
    max_allowed: number;
    plan: string;
  };
}

export const WorkflowLimitModal = ({
  isOpen,
  onClose,
  limitInfo,
}: WorkflowLimitModalProps) => {
  const router = useRouter();

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Workflow Limit Reached</DialogTitle>
          <DialogDescription>
            You&apos;ve reached the maximum number of workflows allowed on your{" "}
            {limitInfo.plan} plan.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span>Current Workflows:</span>
              <span className="font-medium">{limitInfo.current_count}</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Maximum Allowed:</span>
              <span className="font-medium">{limitInfo.max_allowed}</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Current Plan:</span>
              <span className="font-medium capitalize">{limitInfo.plan}</span>
            </div>
          </div>
        </div>

        <DialogFooter className="flex gap-2">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={() => router.push("/settings/billing")}>
            Upgrade Plan
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
