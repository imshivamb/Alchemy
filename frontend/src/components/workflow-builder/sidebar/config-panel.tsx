import { apps } from "@/config/apps.config";
import WebhookConfig from "../config-panels/trigger/webhook-config";
import { Settings } from "lucide-react";
import { Button } from "@/components/ui/button";
import EmailConfig from "../config-panels/trigger/email-config";
import { WorkflowNode, TriggerNode } from "@/types/workflow.types";

interface ConfigurationPanelProps {
  node: WorkflowNode;
  onUpdate: (nodeId: string, data: Partial<WorkflowNode["data"]>) => void;
}

export const ConfigurationPanel = ({
  node,
  onUpdate,
}: ConfigurationPanelProps) => {
  // Early return if not a trigger node
  if (node.type !== "trigger") return null;

  // Now TypeScript knows this is a TriggerNode
  const triggerNode = node as TriggerNode;
  const app = apps.find((a) => a.id === triggerNode.data.appId);
  const trigger = app?.triggers?.find(
    (t) => t.id === triggerNode.data.triggerId
  );

  if (!app || !trigger) return null;

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b flex items-center justify-between">
        <div className="flex items-center gap-2">
          <app.icon className="h-5 w-5" />
          <div>
            <h3 className="font-medium">{trigger.name}</h3>
            <p className="text-sm text-gray-500">{app.name}</p>
          </div>
        </div>
        <Button variant="ghost" size="sm">
          <Settings className="h-4 w-4" />
        </Button>
      </div>

      <div className="flex-1 overflow-auto p-4">
        {app.id === "webhook" && (
          <WebhookConfig
            config={triggerNode.data.config.webhook}
            onChange={(webhookConfig) =>
              onUpdate(triggerNode.id, {
                config: { ...triggerNode.data.config, webhook: webhookConfig },
              })
            }
          />
        )}
        {app.id === "gmail" && trigger.id === "new_email" && (
          <EmailConfig
            config={triggerNode.data.config.email}
            onChange={(emailConfig) =>
              onUpdate(triggerNode.id, {
                config: { ...triggerNode.data.config, email: emailConfig },
              })
            }
          />
        )}
      </div>
    </div>
  );
};
