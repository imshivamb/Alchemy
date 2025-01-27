import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { WebhookStatus } from "@/types/webhook.types";

interface WebhookFiltersProps {
  onFilterChange: (filters: WebhookFilters) => void;
}

interface WebhookFilters {
  status?: WebhookStatus;
  search?: string;
  type?: "incoming" | "outgoing";
}

export function WebhookFilters({ onFilterChange }: WebhookFiltersProps) {
  return (
    <div className="flex gap-4 mb-4">
      <Input
        placeholder="Search webhooks..."
        className="max-w-sm"
        onChange={(e) => onFilterChange({ search: e.target.value })}
      />

      <Select
        onValueChange={(value) =>
          onFilterChange({ status: value as WebhookStatus })
        }
      >
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="Status" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value={WebhookStatus.ACTIVE}>Active</SelectItem>
          <SelectItem value={WebhookStatus.INACTIVE}>Inactive</SelectItem>
          <SelectItem value={WebhookStatus.FAILED}>Failed</SelectItem>
        </SelectContent>
      </Select>

      <Select
        onValueChange={(value) =>
          onFilterChange({ type: value as "incoming" | "outgoing" })
        }
      >
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="Type" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="incoming">Incoming</SelectItem>
          <SelectItem value="outgoing">Outgoing</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}
