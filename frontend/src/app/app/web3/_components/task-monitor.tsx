import { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { formatDistanceToNow } from "date-fns";
import {
  Web3ActionType,
  TransactionStatus,
  Web3Task,
} from "@/types/web3.types";
import { useWeb3Store } from "@/stores/web3.store";
import { LoadingState } from "../../_components/loading-state";

interface TaskMonitorProps {
  onSelectTask: (task: Web3Task) => void;
}

export function TaskMonitor({}: TaskMonitorProps) {
  const { tasks, getTaskStatus, isLoading } = useWeb3Store();
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<TransactionStatus | "all">(
    "all"
  );
  const [actionFilter, setActionFilter] = useState<Web3ActionType | "all">(
    "all"
  );

  // Poll active tasks
  useEffect(() => {
    const activeTasks = tasks.filter(
      (task) =>
        task.status === TransactionStatus.PENDING ||
        task.status === TransactionStatus.PROCESSING
    );

    if (activeTasks.length > 0) {
      const interval = setInterval(() => {
        activeTasks.forEach((task) => {
          getTaskStatus(task.workflow_id);
        });
      }, 5000);

      return () => clearInterval(interval);
    }
  }, [tasks]);

  const getStatusColor = (status: TransactionStatus) => {
    const colors = {
      [TransactionStatus.PENDING]: "bg-yellow-100 text-yellow-800",
      [TransactionStatus.PROCESSING]: "bg-blue-100 text-blue-800",
      [TransactionStatus.COMPLETED]: "bg-green-100 text-green-800",
      [TransactionStatus.FAILED]: "bg-red-100 text-red-800",
    };
    return colors[status];
  };

  const filteredTasks = tasks.filter((task) => {
    const matchesSearch =
      task.workflow_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.action_type.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesStatus =
      statusFilter === "all" || task.status === statusFilter;
    const matchesAction =
      actionFilter === "all" || task.action_type === actionFilter;

    return matchesSearch && matchesStatus && matchesAction;
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Web3 Tasks</CardTitle>
        <CardDescription>
          Monitor and manage your Web3 operations
        </CardDescription>
        <div className="flex gap-4 mt-4">
          <Input
            placeholder="Search tasks..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="max-w-sm"
          />
          <Select
            value={statusFilter}
            onValueChange={(value) =>
              setStatusFilter(value as TransactionStatus | "all")
            }
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value={TransactionStatus.PENDING}>Pending</SelectItem>
              <SelectItem value={TransactionStatus.PROCESSING}>
                Processing
              </SelectItem>
              <SelectItem value={TransactionStatus.COMPLETED}>
                Completed
              </SelectItem>
              <SelectItem value={TransactionStatus.FAILED}>Failed</SelectItem>
            </SelectContent>
          </Select>
          <Select
            value={actionFilter}
            onValueChange={(value) =>
              setActionFilter(value as Web3ActionType | "all")
            }
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Filter by action" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Actions</SelectItem>
              {Object.values(Web3ActionType).map((action) => (
                <SelectItem key={action} value={action}>
                  {action}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Task ID</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Created</TableHead>
              <TableHead>Network</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredTasks.map((task) => (
              <TableRow key={task.workflow_id}>
                <TableCell className="font-mono">
                  {task.workflow_id.slice(0, 8)}...
                </TableCell>
                <TableCell className="capitalize">{task.action_type}</TableCell>
                <TableCell>
                  <Badge className={getStatusColor(task.status)}>
                    {task.status}
                  </Badge>
                </TableCell>
                <TableCell>
                  {formatDistanceToNow(new Date(task.created_at))} ago
                </TableCell>
                <TableCell>{task.network}</TableCell>
                <TableCell>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => getTaskStatus(task.workflow_id)}
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <LoadingState message="Retrying..." />
                    ) : (
                      <LoadingState message="Retry" />
                    )}
                  </Button>
                </TableCell>
              </TableRow>
            ))}
            {filteredTasks.length === 0 && (
              <TableRow>
                <TableCell
                  colSpan={6}
                  className="text-center text-muted-foreground"
                >
                  No tasks found
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
