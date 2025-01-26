import { Card, CardContent } from "@/components/ui/card";
import { apps } from "@/config/apps.config";
import { Handle, Position } from "@xyflow/react";
import { Plus } from "lucide-react";
import React, { memo } from "react";
import {
  NodeAction,
  TriggerNode as TriggerNodeType,
} from "@/types/workflow.types";
import { NodeActions } from "./node-actions";

interface TriggerNodeProps {
  data: TriggerNodeType["data"];
  selected: boolean;
  isValidConnection: (connection: {
    source: string;
    target: string;
  }) => boolean;
  onAction?: (action: NodeAction) => void;
}
const TriggerNode = memo(
  ({ data, selected, isValidConnection, onAction }: TriggerNodeProps) => {
    const app = apps.find((a) => a.id === data.appId);
    const trigger = app?.triggers?.find((t) => t.id === data.triggerId);
    const handleClick = (e: React.MouseEvent) => {
      e.stopPropagation();
    };

    return (
      <div className="relative">
        <Handle
          type="source"
          position={Position.Bottom}
          id="output"
          className="h-3 w-3 bg-blue-500"
          isValidConnection={isValidConnection}
        />

        <Card
          className={`min-w-[280px] ${selected ? "ring-2 ring-blue-500" : ""} ${
            !data.isValid ? "border-red-500" : ""
          }`}
        >
          <CardContent className="p-4">
            {!data.appId ? (
              // Initial state
              <div className="flex items-center gap-2 justify-center py-2">
                <Plus className="h-4 w-4 text-gray-400" />
                <span className="text-gray-600">Choose a trigger app</span>
              </div>
            ) : !data.isConfigured ? (
              // Account connection needed
              <div className="flex items-center gap-2">
                <span className="h-5 w-5 text-gray-400">
                  {app?.icon
                    ? React.createElement(app.icon, { className: "h-5 w-5" })
                    : null}
                </span>
                <div>
                  <h3 className="font-medium">{trigger?.name}</h3>
                  <p className="text-sm text-gray-500">Connect {app?.name}</p>
                </div>
              </div>
            ) : (
              // Fully configured
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="h-5 w-5 text-gray-400">
                      {app?.icon
                        ? React.createElement(app.icon, {
                            className: "h-5 w-5",
                          })
                        : null}
                    </span>
                    <div>
                      <h3 className="font-medium text-blue-600">
                        {trigger?.name}
                      </h3>
                      <p className="text-sm text-gray-500">{app?.name}</p>
                    </div>
                    <NodeActions
                      onRename={() => onAction?.("rename")}
                      onCopy={() => onAction?.("copy")}
                      onAddNote={() => onAction?.("note")}
                      onClick={handleClick}
                    />
                  </div>
                </div>

                <div className="text-sm text-gray-600">
                  {data.appId === "webhook" && data.config?.webhook && (
                    <>Method: {data.config.webhook.method}</>
                  )}
                  {data.appId === "gmail" &&
                    data.triggerId === "new_email" &&
                    data.config?.email && (
                      <>Filters: {data.config.email.filters.length}</>
                    )}
                  {/* Add other app-specific summaries */}
                  {data.appId === "sheets" && <>Spreadsheet connected</>}
                  {data.appId === "slack" && <>Channel configured</>}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }
);

TriggerNode.displayName = "TriggerNode";

export default TriggerNode;
