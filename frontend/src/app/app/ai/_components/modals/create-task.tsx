// _components/modals/create-task.tsx
import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { AIConfig, AIModelType, OutputFormat } from "@/types/ai.types";
import { useAIStore } from "@/stores/ai.store";

interface CreateTaskModalProps {
  open: boolean;
  onClose: () => void;
}

export function CreateTaskModal({ open, onClose }: CreateTaskModalProps) {
  const { models, processAI, estimateCost } = useAIStore();
  const [config, setConfig] = useState<Partial<AIConfig>>({
    model: AIModelType.GPT_35_TURBO,
    temperature: 0.7,
    max_tokens: 150,
    output_format: OutputFormat.TEXT,
  });
  const [estimatedCost, setEstimatedCost] = useState<number | null>(null);

  const handleSubmit = async () => {
    try {
      await processAI(config as AIConfig);
      onClose();
    } catch (error) {
      console.error("Failed to create task:", error);
    }
  };

  const updateConfig = async (updates: Partial<AIConfig>) => {
    const newConfig = { ...config, ...updates };
    setConfig(newConfig);
    if (newConfig.prompt) {
      const estimate = await estimateCost(newConfig as AIConfig);
      setEstimatedCost(estimate.estimated_cost);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Create New AI Task</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <label>Model</label>
            <Select
              value={config.model}
              onValueChange={(value) =>
                updateConfig({ model: value as AIModelType })
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="Select model" />
              </SelectTrigger>
              <SelectContent>
                {models.map((model) => (
                  <SelectItem key={model.id} value={model.id}>
                    {model.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <label>Prompt</label>
            <Input
              value={config.prompt || ""}
              onChange={(e) => updateConfig({ prompt: e.target.value })}
              placeholder="Enter your prompt"
            />
          </div>

          <div className="space-y-2">
            <label>Temperature ({config.temperature})</label>
            <Slider
              value={[config.temperature || 0.7]}
              onValueChange={([value]) => updateConfig({ temperature: value })}
              min={0}
              max={1}
              step={0.1}
            />
          </div>

          <div className="space-y-2">
            <label>Max Tokens ({config.max_tokens})</label>
            <Slider
              value={[config.max_tokens || 150]}
              onValueChange={([value]) => updateConfig({ max_tokens: value })}
              min={1}
              max={2000}
              step={1}
            />
          </div>

          <div className="space-y-2">
            <label>Output Format</label>
            <Select
              value={config.output_format}
              onValueChange={(value) =>
                updateConfig({ output_format: value as OutputFormat })
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="Select format" />
              </SelectTrigger>
              <SelectContent>
                {Object.values(OutputFormat).map((format) => (
                  <SelectItem key={format} value={format}>
                    {format}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {estimatedCost !== null && (
            <div className="text-sm text-gray-600">
              Estimated cost: ${estimatedCost.toFixed(4)}
            </div>
          )}
        </div>

        <div className="flex justify-end gap-3">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSubmit}>Create Task</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
