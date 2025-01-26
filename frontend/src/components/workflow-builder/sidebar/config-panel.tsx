import { Button } from "@/components/ui/button";
import { apps } from "@/config/apps.config";
import { WorkflowNode } from "@/types/workflow.types";
import { Settings } from "lucide-react";
import React from "react";
import ActionConfigPanel from "../config-panels/action-config-panel";
import { TriggerConfigPanel } from "../config-panels/trigger-config-panel";

interface ConfigurationPanelProps {
  node: WorkflowNode;
  onUpdate: (nodeId: string, data: Partial<WorkflowNode["data"]>) => void;
}

export const ConfigurationPanel = ({
  node,
  onUpdate,
}: ConfigurationPanelProps) => {
  // Early return if not a trigger or action node
  if (node.type !== "trigger" && node.type !== "action") return null;

  const app = apps.find((a) => a.id === node.data.appId);
  const trigger =
    node.type === "trigger"
      ? app?.triggers?.find((t) => t.id === node.data.triggerId)
      : null;
  const action =
    node.type === "action"
      ? app?.actions?.find((a) => a.id === node.data.actionId)
      : null;

  if (!app || (!trigger && !action)) return null;

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b flex items-center justify-between">
        <div className="flex items-center gap-2">
          {app?.icon
            ? React.createElement(app.icon, { className: "h-5 w-5" })
            : null}
          <div>
            <h3 className="font-medium">{trigger?.name || action?.name}</h3>
            <p className="text-sm text-gray-500">{app.name}</p>
          </div>
        </div>
        <Button variant="ghost" size="sm">
          <Settings className="h-4 w-4" />
        </Button>
      </div>

      <div className="flex-1 overflow-auto">
        {node.type === "trigger" && (
          <TriggerConfigPanel
            data={node.data}
            onChange={(data) => onUpdate(node.id, data)}
          />
        )}
        {node.type === "action" && (
          <ActionConfigPanel
            data={node.data}
            onChange={(data) => onUpdate(node.id, data)}
          />
        )}
      </div>
    </div>
  );
};
