import React, { memo } from "react";
import { ConditionNode as ConditionNodeType } from "@/types/workflow.types";
import { Handle, Position } from "@xyflow/react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent } from "@/components/ui/tooltip";
import { AlertCircle } from "lucide-react";

type ConditionNodeProps = {
  data: ConditionNodeType["data"];
  selected: boolean;
  isValidConnection: (connection: {
    source: string;
    target: string;
  }) => boolean;
};

const ConditionNode = memo(
  ({ data, selected, isValidConnection }: ConditionNodeProps) => {
    const renderConditionSummary = (
      condition: ConditionNodeType["data"]["config"]["condition"]
    ) => {
      const ruleCount = condition.rules.length;
      return (
        <div className="mt-2 space-y-1 text-xs text-gray-500">
          <div>Operator: {condition.operator.toUpperCase()}</div>
          <div>Rules: {ruleCount}</div>
          {data.config.customLogic && <div>Custom Logic Applied</div>}
        </div>
      );
    };

    return (
      <div className="relative">
        <Handle
          type="target"
          position={Position.Left}
          isValidConnection={isValidConnection}
          className="h-3 w-3 bg-yellow-500"
        />

        {/* True path */}
        <Handle
          type="source"
          position={Position.Right}
          id="true"
          isValidConnection={isValidConnection}
          className="h-3 w-3 bg-green-500"
        />

        {/* False path */}
        <Handle
          type="source"
          position={Position.Bottom}
          id="false"
          isValidConnection={isValidConnection}
          className="h-3 w-3 bg-red-500"
        />

        <Card
          className={`min-w-[200px] ${
            selected ? "ring-2 ring-yellow-500" : ""
          } ${!data.isValid ? "border-red-300" : ""}`}
        >
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertCircle className="h-5 w-5 text-yellow-500" />
                <div className="font-semibold text-yellow-600">
                  {data.label}
                </div>
              </div>
              <Badge
                variant={data.isValid ? "default" : "destructive"}
                className="bg-yellow-500"
              >
                Condition
              </Badge>
            </div>

            <div className="mt-2 text-sm text-gray-600">{data.description}</div>

            {renderConditionSummary(data.config.condition)}

            <div className="mt-2 flex gap-2">
              <Badge variant="outline" className="bg-green-100">
                True →
              </Badge>
              <Badge variant="outline" className="bg-red-100">
                False ↓
              </Badge>
            </div>

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

ConditionNode.displayName = "ConditionNode";

export default ConditionNode;
