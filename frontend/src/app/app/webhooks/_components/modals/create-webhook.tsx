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
import { useState } from "react";
import { useWebhookStore } from "@/stores/webhook.store";
import { useWorkflowApiStore } from "@/stores/workflow-api.store";
import { toast } from "sonner";
import { Label } from "@/components/ui/label";

interface CreateWebhookModalProps {
  open: boolean;
  onClose: () => void;
}

interface CreateWebhookFormData {
  name: string;
  type: "trigger" | "action";
  is_reusable: boolean;
}

export function CreateWebhookModal({ open, onClose }: CreateWebhookModalProps) {
  const [formData, setFormData] = useState<CreateWebhookFormData>({
    name: "",
    type: "trigger",
    is_reusable: true,
  });
  const [loading, setLoading] = useState(false);

  const { createWebhook } = useWebhookStore();
  const { currentWorkflow } = useWorkflowApiStore();

  const handleSubmit = async () => {
    if (!currentWorkflow?.id) {
      toast.error("No workflow selected");
      return;
    }

    setLoading(true);
    try {
      const webhookResponse = await createWebhook({
        name: formData.name,
        webhook_type: formData.type,
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
        toast.success("Webhook created successfully");
      }
      onClose();
    } catch (error) {
      if (error instanceof Error) {
        toast.error(error.message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create New Webhook</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div>
            <Label>Name</Label>
            <Input
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              placeholder="Enter webhook name"
            />
          </div>

          <div>
            <Label>Type</Label>
            <Select
              value={formData.type}
              onValueChange={(value: "trigger" | "action") =>
                setFormData({ ...formData, type: value })
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="trigger">Incoming (Trigger)</SelectItem>
                <SelectItem value="action">Outgoing (Action)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Button onClick={handleSubmit} className="w-full" disabled={loading}>
            {loading ? "Creating..." : "Create Webhook"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
