// _components/task-details-panel.tsx
import { AITask } from "@/types/ai.types";
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
  task: AITask;
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
              <h3 className="text-sm font-medium">Model Configuration</h3>
              <div className="mt-1 space-y-2">
                <div>Model: {task.model}</div>
                <div>Max Tokens: {task.input_data?.max_tokens}</div>
                <div>Temperature: {task.input_data?.temperature}</div>
              </div>
            </div>

            {task.result && (
              <div>
                <h3 className="text-sm font-medium">Result</h3>
                <pre className="mt-1 p-2 bg-gray-50 rounded-md overflow-auto">
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
              <div className="mt-1 space-y-1">
                <div>
                  Created: {formatDistanceToNow(new Date(task.created_at))} ago
                </div>
                {task.updated_at && (
                  <div>
                    Updated: {formatDistanceToNow(new Date(task.updated_at))}{" "}
                    ago
                  </div>
                )}
              </div>
            </div>
          </div>
        </ScrollArea>
      </SheetContent>
    </Sheet>
  );
}
