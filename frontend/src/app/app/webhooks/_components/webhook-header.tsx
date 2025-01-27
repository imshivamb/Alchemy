import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Plus, RefreshCcw } from "lucide-react";

interface WebhookHeaderProps {
  onSearch: (query: string) => void;
  onCreateNew: () => void;
  onRefresh: () => Promise<void>;
}

export function WebhookHeader({
  onSearch,
  onCreateNew,
  onRefresh,
}: WebhookHeaderProps) {
  return (
    <div className="border-b p-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Webhooks</h1>
        <div className="flex items-center gap-4">
          <Input
            placeholder="Search webhooks..."
            className="w-[300px]"
            onChange={(e) => onSearch(e.target.value)}
          />
          <Button variant="outline" size="icon" onClick={onRefresh}>
            <RefreshCcw className="h-4 w-4" />
          </Button>
          <Button onClick={onCreateNew}>
            <Plus className="h-4 w-4 mr-2" />
            Create Webhook
          </Button>
        </div>
      </div>
    </div>
  );
}
