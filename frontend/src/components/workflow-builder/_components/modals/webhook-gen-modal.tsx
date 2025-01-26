import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useWebhookStore } from "@/stores/webhook.store";
import { useWorkflowApiStore } from "@/stores/workflow-api.store";
import { useState } from "react";
import { toast } from "sonner";

interface WebhookGenerationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerate: (webhookUrl: string) => void;
}

export const WebhookGenerationModal = ({
  isOpen,
  onClose,
  onGenerate,
}: WebhookGenerationModalProps) => {
  const [loading, setLoading] = useState(false);
  const { createWebhook } = useWebhookStore();
  const { currentWorkflow } = useWorkflowApiStore();

  const handleGenerateWebhook = async () => {
    if (!currentWorkflow?.id) {
      toast.error("No workflow selected");
      return;
    }

    setLoading(true);
    try {
      const webhookResponse = await createWebhook({
        name: `${currentWorkflow.name} - Webhook Trigger`,
        webhook_type: "trigger",
        workflow: currentWorkflow.id,
        http_method: "POST",
        headers: {},
        config: {
          method: "POST",
          retry_strategy: {
            max_retries: 3,
            initial_interval: 60,
            max_interval: 3600,
            multiplier: 2,
          },
        },
      });

      if (webhookResponse.trigger_url) {
        onGenerate(webhookResponse.trigger_url);
        toast.success("Webhook generated successfully");
      }
    } catch (error) {
      if (error instanceof Error) {
        toast.error(error.message);
      }
    } finally {
      setLoading(false);
      onClose();
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Generate Webhook</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <p className="text-sm text-gray-500">
            Generate a unique webhook URL for this trigger
          </p>
          <Button onClick={handleGenerateWebhook} disabled={loading}>
            {loading ? "Generating..." : "Generate Webhook URL"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};
