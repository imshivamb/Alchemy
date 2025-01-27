import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { AIModelType } from "@/types/ai.types";

interface TaskFiltersProps {
  onStatusFilter: (status: string) => void;
  onModelFilter: (model: AIModelType) => void;
  onSort: (key: string) => void;
}

export function TaskFilters({
  onStatusFilter,
  onModelFilter,
  onSort,
}: TaskFiltersProps) {
  return (
    <div className="flex gap-4 mb-4">
      <Select onValueChange={onStatusFilter}>
        <SelectTrigger className="w-[150px]">
          <SelectValue placeholder="Status" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Status</SelectItem>
          <SelectItem value="pending">Pending</SelectItem>
          <SelectItem value="processing">Processing</SelectItem>
          <SelectItem value="completed">Completed</SelectItem>
          <SelectItem value="failed">Failed</SelectItem>
        </SelectContent>
      </Select>

      <Select onValueChange={onModelFilter}>
        <SelectTrigger className="w-[150px]">
          <SelectValue placeholder="Model" />
        </SelectTrigger>
        <SelectContent>
          {Object.values(AIModelType).map((model) => (
            <SelectItem key={model} value={model}>
              {model}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Select onValueChange={onSort}>
        <SelectTrigger className="w-[150px]">
          <SelectValue placeholder="Sort By" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="created_desc">Newest First</SelectItem>
          <SelectItem value="created_asc">Oldest First</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}
