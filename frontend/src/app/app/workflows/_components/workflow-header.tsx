import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus, RefreshCw } from "lucide-react";
import { useWorkflowApiStore } from "@/stores/workflow-api.store";

interface WorkflowHeaderProps {
  onSearch: (query: string) => void;
  onCreateNew: () => void;
}

export function WorkflowHeader({ onSearch, onCreateNew }: WorkflowHeaderProps) {
  const { workflowLimits, fetchWorkflows } = useWorkflowApiStore();

  return (
    <div className="border-b p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-semibold">Workflows</h1>
          {workflowLimits && (
            <div className="text-sm text-muted-foreground">
              {workflowLimits.current_count} / {workflowLimits.total_limit}{" "}
              workflows used
            </div>
          )}
        </div>
        <div className="flex items-center gap-4">
          <Input
            placeholder="Search workflows..."
            className="w-[300px]"
            onChange={(e) => onSearch(e.target.value)}
          />
          <Button
            variant="outline"
            size="icon"
            onClick={() => fetchWorkflows()}
          >
            <RefreshCw className="h-4 w-4" />
          </Button>
          <Button onClick={onCreateNew}>
            <Plus className="h-4 w-4 mr-2" />
            Create Workflow
          </Button>
        </div>
      </div>
    </div>
  );
}
