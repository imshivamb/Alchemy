import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Plus, RefreshCw } from "lucide-react";

interface AIHeaderProps {
  onSearch: (query: string) => void;
  onCreateNew: () => void;
  onBatchProcess: () => void;
  onRefresh: () => void;
}

export function AIHeader({ onSearch, onCreateNew, onRefresh }: AIHeaderProps) {
  return (
    <div className="flex justify-between items-center p-4 border-b">
      <div className="flex gap-2 w-72">
        <Input
          placeholder="Search tasks..."
          onChange={(e) => onSearch(e.target.value)}
        ></Input>
      </div>
      <div className="flex gap-2">
        <Button variant="outline" size="sm" onClick={onRefresh}>
          <RefreshCw className="w-4 h-4" />
        </Button>
        <Button onClick={onCreateNew}>
          <Plus className="w-4 h-4 mr-2" />
          New Task
        </Button>
      </div>
    </div>
  );
}
