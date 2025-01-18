import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { apps } from "@/config/apps.config";
import { Handle, Position } from "@xyflow/react";
import { Plus } from "lucide-react";
import { memo } from "react";
import { ActionNode as ActionNodeType } from "@/types/workflow.types";

interface ActionNodeProps {
  data: ActionNodeType["data"];
  selected: boolean;
  isValidConnection: (connection: {
    source: string;
    target: string;
  }) => boolean;
}

const ActionNode = memo(
  ({ data, selected, isValidConnection }: ActionNodeProps) => {
    const app = apps.find((a) => a.id === data.appId);
    const action = app?.actions?.find((a) => a.id === data.actionId);

    return (
      <div className="relative">
        {/* Input Handle */}
        <Handle
          type="target"
          position={Position.Top}
          className="h-3 w-3 !bg-gray-300"
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
                <span className="text-gray-600">Choose an action app</span>
              </div>
            ) : !data.isConfigured ? (
              // Account connection needed
              <div className="flex items-center gap-2">
                <span className="h-5 w-5 text-gray-400">{app?.icon}</span>
                <div>
                  <h3 className="font-medium">{action?.name}</h3>
                  <p className="text-sm text-gray-500">Connect {app?.name}</p>
                </div>
              </div>
            ) : (
              // Fully configured
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="h-5 w-5 text-green-500">{app?.icon}</span>
                    <div>
                      <h3 className="font-medium text-green-600">
                        {action?.name}
                      </h3>
                      <p className="text-sm text-gray-500">{app?.name}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Add Node Button */}
        <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2">
          <Button
            size="sm"
            variant="outline"
            className="rounded-full h-8 w-8 p-0 bg-white"
            onClick={(e) => {
              e.stopPropagation();
              // This will be handled by workflow builder to open action selection
            }}
          >
            <Plus className="h-4 w-4" />
          </Button>
        </div>
      </div>
    );
  }
);

ActionNode.displayName = "ActionNode";

export default ActionNode;
