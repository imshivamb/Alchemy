import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AuthStore } from "@/stores/auth.store";
import { Save, Play } from "lucide-react";
import Link from "next/link";

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
            onChange={(e) => setWorkflowName(e.target.value)}
            placeholder="Untitled workflow"
          />
          <Badge variant="secondary">Draft</Badge>
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
