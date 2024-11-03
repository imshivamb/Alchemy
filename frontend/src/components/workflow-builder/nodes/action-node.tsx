import React, { memo } from "react";
import { Handle, Position } from "@xyflow/react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent } from "@/components/ui/tooltip";
import { Brain, Coins, Globe, FileJson, AlertCircle } from "lucide-react";
import type { ActionNode as ActionNodeType } from "@/types/workflow.types";

const icons = {
  ai: Brain,
  web3: Coins,
  http: Globe,
  transform: FileJson,
};

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
    const Icon = icons[data.actionType] || Globe;

    const renderConfigSummary = () => {
      switch (data.actionType) {
        case "ai":
          return (
            data.config.ai && (
              <div className="mt-2 space-y-1 text-xs text-gray-500">
                <div>Model: {data.config.ai.model}</div>
                <div>Max Tokens: {data.config.ai.maxTokens}</div>
                {(data.config?.ai?.preprocessors?.length ?? 0) > 0 && (
                  <div>
                    Preprocessors: {data.config?.ai?.preprocessors?.length}
                  </div>
                )}
              </div>
            )
          );

        case "web3":
          return (
            data.config.web3 && (
              <div className="mt-2 space-y-1 text-xs text-gray-500">
                <div>Network: {data.config.web3.network}</div>
                <div>Action: {data.config.web3.actionType}</div>
                {data.config.web3.amount && (
                  <div>Amount: {data.config.web3.amount}</div>
                )}
              </div>
            )
          );

        case "http":
          return (
            data.config.http && (
              <div className="mt-2 space-y-1 text-xs text-gray-500">
                <div>Method: {data.config.http.method}</div>
                <div className="truncate">URL: {data.config.http.url}</div>
              </div>
            )
          );

        case "transform":
          return (
            data.config.transform && (
              <div className="mt-2 space-y-1 text-xs text-gray-500">
                <div>Operations: {data.config.transform.operations.length}</div>
                <div>Error Behavior: {data.config.transform.errorBehavior}</div>
              </div>
            )
          );
      }
    };

    return (
      <div className="relative">
        <Handle
          type="target"
          position={Position.Left}
          isValidConnection={isValidConnection}
          className="h-3 w-3 bg-green-500"
        />

        <Handle
          type="source"
          position={Position.Right}
          isValidConnection={isValidConnection}
          className="h-3 w-3 bg-green-500"
        />

        <Card
          className={`min-w-[200px] ${
            selected ? "ring-2 ring-green-500" : ""
          } ${!data.isValid ? "border-red-300" : ""}`}
        >
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Icon className="h-5 w-5 text-green-500" />
                <div className="font-semibold text-green-600">{data.label}</div>
              </div>
              <Badge
                variant={data.isValid ? "default" : "destructive"}
                className={`${
                  data.actionType === "ai"
                    ? "bg-purple-500"
                    : data.actionType === "web3"
                    ? "bg-orange-500"
                    : data.actionType === "http"
                    ? "bg-blue-500"
                    : "bg-gray-500"
                }`}
              >
                {data.actionType}
              </Badge>
            </div>

            <div className="mt-2 text-sm text-gray-600">{data.description}</div>

            {renderConfigSummary()}

            {!data.isValid && data.errorMessage && (
              <Tooltip>
                <TooltipContent>{data.errorMessage}</TooltipContent>
                <div className="mt-2 flex items-center gap-1 text-xs text-red-500">
                  <AlertCircle className="h-4 w-4" />
                  <span>Configuration Error</span>
                </div>
              </Tooltip>
            )}

            {data.inputSchema && (
              <Tooltip>
                <TooltipContent>
                  <div>
                    <div className="font-bold">Required Inputs:</div>
                    <div>{data.inputSchema.required.join(", ")}</div>
                  </div>
                </TooltipContent>
                <Badge variant="outline" className="mt-2">
                  {data.inputSchema.required.length} Required Inputs
                </Badge>
              </Tooltip>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }
);

ActionNode.displayName = "ActionNode";

export default ActionNode;
