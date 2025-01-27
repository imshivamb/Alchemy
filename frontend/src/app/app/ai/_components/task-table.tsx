import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useAIStore } from "@/stores/ai.store";
import { AIModelType } from "@/types/ai.types";
import { formatDistanceToNow } from "date-fns";

interface TaskTableProps {
  tasks: {
    workflow_id: string;
    status: string;
    created_at: string;
    input_data: any;
    model: string;
    result: any;
    error?: string;
    updated_at: string;
  }[];
  searchQuery: string;
  statusFilter: string;
  modelFilter: AIModelType | null;
  sortKey: string;
  onSelect: (task: any) => void;
}

export function TaskTable({ tasks, searchQuery, onSelect }: TaskTableProps) {
  const { retryTask } = useAIStore();

  const filteredTasks = tasks.filter(
    (task) =>
      task?.workflow_id
        ?.toString()
        .toLowerCase()
        .includes(searchQuery.toLowerCase()) ||
      task?.status?.toLowerCase().includes(searchQuery.toLowerCase())
  );
  type TaskStatus =
    | "pending"
    | "processing"
    | "completed"
    | "failed"
    | "cancelled";
  const getStatusColor = (status: string) => {
    const colors: Record<TaskStatus, string> = {
      pending: "bg-yellow-100 text-yellow-800",
      processing: "bg-blue-100 text-blue-800",
      completed: "bg-green-100 text-green-800",
      failed: "bg-red-100 text-red-800",
      cancelled: "bg-gray-100 text-gray-800",
    };
    return colors[status as TaskStatus];
  };
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>ID</TableHead>
          <TableHead>Model</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Created</TableHead>
          <TableHead>Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {filteredTasks.map((task, index) => (
          <TableRow
            key={`${task.workflow_id}-${index}`}
            className="cursor-pointer hover:bg-gray-50"
            onClick={() => onSelect(task)}
          >
            <TableCell className="font-mono">{task.workflow_id}</TableCell>
            <TableCell>{task.model}</TableCell>
            <TableCell>
              <Badge
                variant="secondary"
                className={getStatusColor(task.status)}
              >
                {task.status}
              </Badge>
            </TableCell>
            <TableCell>
              {formatDistanceToNow(new Date(task.created_at))} ago
            </TableCell>
            <TableCell>
              <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
                {task.status === "failed" && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => retryTask(task.workflow_id)}
                  >
                    Retry
                  </Button>
                )}
              </div>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
