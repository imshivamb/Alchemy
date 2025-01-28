// _components/task-details-panel.tsx
import { Web3Task } from "@/types/web3.types";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { ScrollArea } from "@/components/ui/scroll-area";
import { formatDistanceToNow } from "date-fns";
import { X } from "lucide-react";

interface TaskDetailsPanelProps {
  task: Web3Task;
  onClose: () => void;
}

export function TaskDetailsPanel({ task, onClose }: TaskDetailsPanelProps) {
  return (
    <Sheet open={true} onOpenChange={onClose}>
      <SheetContent className="w-[400px] sm:w-[540px] p-0">
        <SheetHeader className="p-6 border-b">
          <div className="flex justify-between items-center">
            <SheetTitle>Task Details</SheetTitle>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </SheetHeader>

        <ScrollArea className="h-full p-6">
          <div className="space-y-6">
            <div>
              <h3 className="text-sm font-medium">Task ID</h3>
              <p className="font-mono mt-1">{task.workflow_id}</p>
            </div>

            <div>
              <h3 className="text-sm font-medium">Action Type</h3>
              <p className="mt-1 capitalize">{task.action_type}</p>
            </div>

            <div>
              <h3 className="text-sm font-medium">Network</h3>
              <p className="mt-1">{task.network}</p>
            </div>

            <div>
              <h3 className="text-sm font-medium">Parameters</h3>
              <pre className="mt-1 p-2 bg-gray-50 rounded-md overflow-auto text-sm">
                {JSON.stringify(task.params, null, 2)}
              </pre>
            </div>

            {task.result && (
              <div>
                <h3 className="text-sm font-medium">Result</h3>
                <pre className="mt-1 p-2 bg-gray-50 rounded-md overflow-auto text-sm">
                  {JSON.stringify(task.result, null, 2)}
                </pre>
              </div>
            )}

            {task.error && (
              <div>
                <h3 className="text-sm font-medium text-red-600">Error</h3>
                <p className="mt-1 text-red-600">{task.error}</p>
              </div>
            )}

            <div>
              <h3 className="text-sm font-medium">Timestamps</h3>
              <div className="mt-1 space-y-1 text-sm">
                <div>
                  Created: {formatDistanceToNow(new Date(task.created_at))} ago
                </div>
              </div>
            </div>
          </div>
        </ScrollArea>
      </SheetContent>
    </Sheet>
  );
}
