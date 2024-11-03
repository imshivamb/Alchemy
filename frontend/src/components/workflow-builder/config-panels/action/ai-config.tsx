import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Textarea } from "@/components/ui/textarea";
import { AIConfig as AIConfigType, AIModelType } from "@/types/workflow.types";
import React from "react";

type AIConfigProps = {
  config: AIConfigType;
  onChange: (config: AIConfigType) => void;
};

const AIConfig = ({ config, onChange }: AIConfigProps) => {
  return (
    <div className="space-y-4">
      <Select
        value={config?.model ?? "gpt-4o-mini"}
        onValueChange={(value: AIModelType) =>
          onChange({ ...config, model: value })
        }
      >
        <SelectTrigger>
          <SelectValue placeholder="Select model" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="gpt-4">GPT-4</SelectItem>
          <SelectItem value="gpt-3.5-turbo">GPT-3.5</SelectItem>
          <SelectItem value="claude-2">Claude 2</SelectItem>
          <SelectItem value="gpt-4o-mini">GPT-4o-mini</SelectItem>
        </SelectContent>
      </Select>

      <Slider
        value={[config?.temperature ?? 0.7]}
        min={0}
        max={1}
        step={0.1}
        onValueChange={([value]) => onChange({ ...config, temperature: value })}
      />

      <Input
        type="number"
        value={config?.maxTokens ?? 150}
        onChange={(e) =>
          onChange({ ...config, maxTokens: parseInt(e.target.value) })
        }
      />

      <Textarea
        value={config?.prompt ?? ""}
        onChange={(e) => onChange({ ...config, prompt: e.target.value })}
        placeholder="Enter prompt template..."
      />

      {/* Add other AI-specific configurations */}
    </div>
  );
};

export default AIConfig;
