import { useState } from "react";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { AIConfig } from "@/types/ai.types";
import { useAIStore } from "@/stores/ai.store";

interface BatchProcessModalProps {
  open: boolean;
  onClose: () => void;
}

export function BatchProcessModal({ open, onClose }: BatchProcessModalProps) {
  const { processBatch } = useAIStore();
  const [prompts, setPrompts] = useState<string>("");
  const [config, setConfig] = useState<Partial<AIConfig>>({});

  const handleSubmit = async () => {
    const promptList = prompts.split("\n").filter((p) => p.trim());
    const configs = promptList.map((prompt) => ({
      ...config,
      prompt,
    }));

    await processBatch(configs as AIConfig[]);
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <h2>Batch Process</h2>
        <Textarea
          value={prompts}
          onChange={(e) => setPrompts(e.target.value)}
          placeholder="Enter prompts (one per line)"
          rows={10}
        />
        {/* Reuse config options from CreateTaskModal */}
        <Button onClick={handleSubmit}>Process Batch</Button>
      </DialogContent>
    </Dialog>
  );
}
