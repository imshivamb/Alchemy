import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Edit, Trash2, ExternalLink } from "lucide-react";
import { Workflow } from "@/types/workflow-api.types";
import { formatDistanceToNow } from "date-fns";
import { useState } from "react";
import { useWorkflowApiStore } from "@/stores/workflow-api.store";
import { toast } from "sonner";
import Link from "next/link";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { WorkflowPagination } from "./workflow-pagination";
import { DeleteWorkflowModal } from "./modals/delete-workflow";

interface WorkflowGridProps {
  workflows?: Workflow[];
  searchQuery: string;
  onSelect: (workflow: Workflow) => void;
}

export function WorkflowGrid({
  workflows = [],
  searchQuery,
  onSelect,
}: WorkflowGridProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [workflowToDelete, setWorkflowToDelete] = useState<Workflow | null>(
    null
  );
  const [sortBy, setSortBy] = useState<"name" | "updated" | "tasks">("updated");
  const { deleteWorkflow } = useWorkflowApiStore();
  const ITEMS_PER_PAGE = 9;

  // Filter workflows based on search
  const filteredWorkflows = Array.isArray(workflows)
    ? workflows.filter((workflow) =>
        workflow.name.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : [];

  // Sort workflows
  const sortedWorkflows = [...filteredWorkflows].sort((a, b) => {
    switch (sortBy) {
      case "name":
        return a.name.localeCompare(b.name);
      case "tasks":
        return b.task_count - a.task_count;
      default:
        return (
          new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
        );
    }
  });

  // Paginate workflows
  const paginatedWorkflows = sortedWorkflows.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  const handleDelete = async () => {
    if (!workflowToDelete) return;
    try {
      await deleteWorkflow(workflowToDelete.id);
      toast.success("Workflow deleted successfully");
    } catch (error) {
      console.log("Error deleting workflow:", error);
      toast.error("Failed to delete workflow");
    } finally {
      setWorkflowToDelete(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-end">
        <Select
          value={sortBy}
          onValueChange={(value: "name" | "updated" | "tasks") =>
            setSortBy(value)
          }
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Sort by" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="name">Name</SelectItem>
            <SelectItem value="updated">Last Updated</SelectItem>
            <SelectItem value="tasks">Task Count</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {paginatedWorkflows.map((workflow) => (
          <Card
            key={workflow.id}
            className="cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => onSelect(workflow)}
          >
            <CardContent className="p-6">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold text-lg">{workflow.name}</h3>
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {workflow.description || "No description"}
                  </p>
                </div>
                <div
                  className="flex items-center gap-2"
                  onClick={(e) => e.stopPropagation()}
                >
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => onSelect(workflow)}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setWorkflowToDelete(workflow)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon" asChild>
                    <Link href={`/editor/${workflow.id}`}>
                      <ExternalLink className="h-4 w-4" />
                    </Link>
                  </Button>
                </div>
              </div>

              <div className="mt-4 flex items-center gap-4 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <div
                    className={`w-2 h-2 rounded-full ${
                      workflow.is_active ? "bg-green-500" : "bg-gray-300"
                    }`}
                  />
                  {workflow.is_active ? "Active" : "Inactive"}
                </div>
                <div>Tasks: {workflow.task_count}</div>
                <div>Webhooks: {workflow.webhook_count}</div>
              </div>

              <div className="mt-2 text-xs text-muted-foreground">
                Updated{" "}
                {formatDistanceToNow(new Date(workflow.updated_at), {
                  addSuffix: true,
                })}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredWorkflows.length > ITEMS_PER_PAGE && (
        <div className="mt-4 flex justify-center">
          <WorkflowPagination
            currentPage={currentPage}
            totalPages={Math.ceil(filteredWorkflows.length / ITEMS_PER_PAGE)}
            onPageChange={setCurrentPage}
          />
        </div>
      )}

      <DeleteWorkflowModal
        open={!!workflowToDelete}
        onClose={() => setWorkflowToDelete(null)}
        onConfirm={handleDelete}
        workflowName={workflowToDelete?.name || ""}
      />
    </div>
  );
}
