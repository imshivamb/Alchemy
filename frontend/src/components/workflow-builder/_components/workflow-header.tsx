import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { toast } from "@/hooks/use-toast";
import { AuthStore } from "@/stores/auth.store";
import { useWorkflowApiStore } from "@/stores/workflow-api.store";
import { Save, Play } from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { DebouncedFunc, debounce } from "lodash";

interface WorkflowHeaderProps {
  workflowName: string;
  setWorkflowName: (name: string) => void;
  onSave: () => void;
  onTest: () => void;
  isValid: boolean;
  isDirty: boolean;
}

export const WorkflowHeader = ({
  workflowName,
  setWorkflowName,
  onSave,
  onTest,
  isValid,
  isDirty,
}: WorkflowHeaderProps) => {
  const { user } = AuthStore();
  const { currentWorkflow, updateWorkflow } = useWorkflowApiStore();
  const [isSaving, setIsSaving] = useState(false);
  const debouncedUpdate: DebouncedFunc<(name: string) => Promise<void>> =
    useCallback(
      debounce(async (name: string) => {
        if (currentWorkflow?.id && name !== currentWorkflow.name) {
          setIsSaving(true);
          try {
            await updateWorkflow(currentWorkflow.id, {
              name: name,
            });
            toast({
              title: "Success",
              description: "Workflow name updated successfully",
              duration: 2000,
            });
          } catch (error) {
            toast({
              title: "Error",
              description: "Failed to update workflow name",
              variant: "destructive",
            });
            console.log("Error updating workflow name:", error);
            setWorkflowName(currentWorkflow.name);
          } finally {
            setIsSaving(false);
          }
        }
      }, 1000),
      [currentWorkflow, updateWorkflow, setWorkflowName]
    );

  useEffect(() => {
    return () => {
      debouncedUpdate.cancel();
    };
  }, [debouncedUpdate]);

  // Handle name change
  const handleNameChange = (name: string) => {
    setWorkflowName(name);
    debouncedUpdate(name);
  };

  return (
    <div className="h-12 border-b flex items-center px-4 bg-background">
      <div className="flex-1 flex items-center justify-between">
        <Link href="/app/workflows">Workflows</Link>
        <div className="flex items-center gap-2">
          <Link href="/app/workflows">
            <span className="text-sm text-gray-500">
              {user?.first_name} {user?.last_name} /
            </span>
          </Link>
          <input
            className="bg-transparent border-none text-sm font-medium focus:outline-none"
            value={workflowName}
            onChange={(e) => handleNameChange(e.target.value)}
            placeholder="Untitled workflow"
          />
          {isSaving && (
            <span className="absolute -right-5 top-1/2 -translate-y-1/2">
              <span className="animate-spin">⌛</span>
            </span>
          )}
          <Badge variant="secondary">
            {currentWorkflow?.is_active ? "Active" : "Draft"}
          </Badge>
        </div>

        <div className="flex items-center gap-2">
          <Button size="sm" onClick={onSave} disabled={!isDirty || !isValid}>
            <Save className="h-4 w-4 mr-2" />
            Save
          </Button>
          <Button
            size="sm"
            variant="secondary"
            onClick={onTest}
            disabled={!isValid}
          >
            <Play className="h-4 w-4 mr-2" />
            Test
          </Button>
        </div>
      </div>
    </div>
  );
};
