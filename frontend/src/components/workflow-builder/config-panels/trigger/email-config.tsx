import React from "react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Trash2 } from "lucide-react";
import {
  EmailConfig as EmailConfigType,
  EmailFilter,
} from "@/types/workflow.types";

interface EmailConfigProps {
  config?: EmailConfigType;
  onChange: (config: EmailConfigType) => void;
}

type EmailFilterCondition = "equals" | "contains" | "starts_with" | "ends_with";

interface EmailFilterType {
  type: EmailFilter;
  value: string;
  condition: EmailFilterCondition;
}

// Default filter values
const defaultFilter: EmailFilterType = {
  type: "subject",
  condition: "contains",
  value: "",
};

// Default config values
const defaultConfig: EmailConfigType = {
  filters: [],
  folders: [],
  includeAttachments: false,
  markAsRead: false,
};

export const EmailConfig: React.FC<EmailConfigProps> = ({
  config = defaultConfig,
  onChange,
}) => {
  const handleFilterUpdate = (
    index: number,
    updates: Partial<EmailFilterType>
  ) => {
    const newFilters = [...(config.filters ?? [])];
    newFilters[index] = { ...newFilters[index], ...updates };
    onChange({ ...config, filters: newFilters });
  };

  return (
    <div className="space-y-4">
      <div>
        <Label>Email Filters</Label>
        {config?.filters?.map((filter, index) => (
          <div key={index} className="mt-2 space-y-2">
            <Select
              value={filter.type}
              onValueChange={(value: EmailFilter) => {
                handleFilterUpdate(index, { type: value });
              }}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="subject">Subject</SelectItem>
                <SelectItem value="from">From</SelectItem>
                <SelectItem value="to">To</SelectItem>
                <SelectItem value="body">Body</SelectItem>
              </SelectContent>
            </Select>

            <Select
              value={filter.condition}
              onValueChange={(value: EmailFilterCondition) => {
                handleFilterUpdate(index, { condition: value });
              }}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="equals">Equals</SelectItem>
                <SelectItem value="contains">Contains</SelectItem>
                <SelectItem value="starts_with">Starts With</SelectItem>
                <SelectItem value="ends_with">Ends With</SelectItem>
              </SelectContent>
            </Select>

            <Input
              placeholder="Filter value"
              value={filter.value}
              onChange={(e) => {
                handleFilterUpdate(index, { value: e.target.value });
              }}
            />

            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                const newFilters = config.filters.filter((_, i) => i !== index);
                onChange({ ...config, filters: newFilters });
              }}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        ))}

        <Button
          variant="outline"
          className="mt-2"
          onClick={() => {
            const newFilters = [...(config.filters ?? []), defaultFilter];
            onChange({ ...config, filters: newFilters });
          }}
        >
          Add Filter
        </Button>
      </div>

      <div>
        <Label>Folders</Label>
        <Input
          placeholder="Comma-separated folders"
          value={config?.folders?.join(", ") ?? ""}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
            onChange({
              ...config,
              folders: e.target.value
                .split(",")
                .map((f) => f.trim())
                .filter(Boolean),
            })
          }
        />
      </div>

      <div className="space-y-2">
        <div className="flex items-center">
          <Checkbox
            id="includeAttachments"
            checked={config?.includeAttachments ?? false}
            onCheckedChange={(checked: boolean) =>
              onChange({ ...config, includeAttachments: checked })
            }
          />
          <Label htmlFor="includeAttachments" className="ml-2">
            Include Attachments
          </Label>
        </div>

        <div className="flex items-center">
          <Checkbox
            id="markAsRead"
            checked={config?.markAsRead ?? false}
            onCheckedChange={(checked: boolean) =>
              onChange({ ...config, markAsRead: checked })
            }
          />
          <Label htmlFor="markAsRead" className="ml-2">
            Mark as Read
          </Label>
        </div>
      </div>
    </div>
  );
};

export default EmailConfig;
