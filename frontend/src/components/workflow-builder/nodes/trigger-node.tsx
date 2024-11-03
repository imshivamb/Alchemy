import React, { memo } from "react";
import { TriggerNode as TriggerNodeType } from "@/types/workflow.types";
import { Webhook, Clock, Mail, AlertCircle } from "lucide-react";
import { Handle, Position } from "@xyflow/react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent } from "@/components/ui/tooltip";

const icons = {
  webhook: Webhook,
  schedule: Clock,
  email: Mail,
};

type TriggerNodeProps = {
  data: TriggerNodeType["data"];
  selected: boolean;
  isValidConnection: (connection: {
    source: string;
    target: string;
  }) => boolean;
};

const TriggerNode = memo(
  ({ data, selected, isValidConnection }: TriggerNodeProps) => {
    const Icon = icons[data.triggerType] || Webhook;

    return (
      <div className="relative">
        {/* Output Handle */}
        <Handle
          type="source"
          position={Position.Right}
          id="output"
          className="h-3 w-3 bg-blue-500"
          isValidConnection={isValidConnection}
        />

        <Card
          className={`min-w-[200px] ${selected ? "ring-2 ring-blue-500" : ""} ${
            !data.isValid ? "border-red-500" : ""
          }`}
        >
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Icon className="size-5 text-blue-500" />
                <div className="font-semibold text-blue-600">{data.label}</div>
              </div>
              <Badge variant={data.isValid ? "default" : "destructive"}>
                {data.triggerType}
              </Badge>
            </div>

            <div className="mt-2 text-sm text-gray-600">{data.description}</div>

            {/* Configuration SUmmary */}
            <div className="mt-2 space-y-1 text-xs text-gray-500">
              {data.triggerType === "webhook" && data.config?.webhook && (
                <>
                  <div className="">Method: {data.config.webhook.method}</div>
                  <div className="truncate">
                    URL: {data.config.webhook.webhookUrl}
                  </div>
                </>
              )}
              {data.triggerType === "schedule" && data.config?.schedule && (
                <>
                  <div>Type: {data.config.schedule.scheduleType}</div>
                  {data.config.schedule?.cronExpression && (
                    <div>Cron: {data.config.schedule.cronExpression}</div>
                  )}
                  <div>Timezone: {data.config.schedule.timezone}</div>
                </>
              )}
              {data.triggerType === "email" && data.config.email && (
                <>
                  <div>Filters: {data.config.email.filters.length}</div>
                  <div>Folders: {data.config.email.folders.join(", ")}</div>
                </>
              )}
            </div>

            {/* Validation Error */}
            {!data.isValid && data.errorMessage && (
              <Tooltip>
                <TooltipContent>{data.errorMessage}</TooltipContent>
                <div className="mt-2 flex items-center gap-1 text-xs text-red-500">
                  <AlertCircle className="h-4 w-4" />
                  <span>Configuration Error</span>
                </div>
              </Tooltip>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }
);

TriggerNode.displayName = "TriggerNode";

export default TriggerNode;
