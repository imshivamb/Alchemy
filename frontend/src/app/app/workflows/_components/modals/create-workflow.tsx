import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { useState } from "react";
import { useWorkflowApiStore } from "@/stores/workflow-api.store";
import { toast } from "sonner";

interface CreateWorkflowModalProps {
  open: boolean;
  onClose: () => void;
}

export function CreateWorkflowModal({
  open,
  onClose,
}: CreateWorkflowModalProps) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    is_active: true,
    workflow_data: {},
  });

  const { createWorkflow } = useWorkflowApiStore();

  const handleSubmit = async () => {
    if (!formData.name.trim()) {
      toast.error("Workflow name is required");
      return;
    }

    setLoading(true);
    try {
      await createWorkflow({
        name: formData.name,
        description: formData.description,
        is_active: formData.is_active,
        workflow_data: {},
      });

      toast.success("Workflow created successfully");
      onClose();
    } catch (error) {
      console.log("Error creating workflow:", error);
      toast.error("Failed to create workflow");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create New Workflow</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label>Name</Label>
            <Input
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              placeholder="Enter workflow name"
            />
          </div>

          <div className="space-y-2">
            <Label>Description</Label>
            <Textarea
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              placeholder="Enter workflow description (optional)"
              rows={3}
            />
          </div>

          <div className="flex items-center justify-between">
            <Label>Active</Label>
            <Switch
              checked={formData.is_active}
              onCheckedChange={(checked) =>
                setFormData({ ...formData, is_active: checked })
              }
            />
          </div>

          <div className="pt-4 space-x-2 flex justify-end">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} disabled={loading}>
              {loading ? "Creating..." : "Create Workflow"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
