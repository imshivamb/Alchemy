import React from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

import WebhookConfig from "./trigger/webhook-config";
import { ScheduleConfig } from "./trigger/schedule-config";
import EmailConfig from "./trigger/email-config";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { TriggerNode } from "@/types/workflow.types";

interface TriggerConfigProps {
  data: TriggerNode["data"];
  onChange: (data: Partial<TriggerNode["data"]>) => void;
}

export const TriggerConfig: React.FC<TriggerConfigProps> = ({
  data,
  onChange,
}) => {
  return (
    <div className="space-y-4 p-4">
      {/* Basic Information */}
      <div className="space-y-2">
        <div>
          <Label>Name</Label>
          <Input
            value={data.label}
            onChange={(e) => onChange({ ...data, label: e.target.value })}
            placeholder="Enter trigger name"
          />
        </div>
        <div>
          <Label>Description</Label>
          <Input
            value={data.description}
            onChange={(e) => onChange({ ...data, description: e.target.value })}
            placeholder="Enter description"
          />
        </div>
      </div>

      {/* Trigger Type Specific Configuration */}
      <Tabs
        defaultValue={data.triggerType}
        onValueChange={(value: any) =>
          onChange({ ...data, triggerType: value })
        }
      >
        <TabsList className="w-full">
          <TabsTrigger value="webhook">Webhook</TabsTrigger>
          <TabsTrigger value="schedule">Schedule</TabsTrigger>
          <TabsTrigger value="email">Email</TabsTrigger>
        </TabsList>

        <TabsContent value="webhook">
          <WebhookConfig
            config={data.config.webhook}
            onChange={(webhookConfig) =>
              onChange({
                ...data,
                config: { ...data.config, webhook: webhookConfig },
              })
            }
          />
        </TabsContent>

        <TabsContent value="schedule">
          <ScheduleConfig
            config={data.config.schedule}
            onChange={(scheduleConfig) =>
              onChange({
                ...data,
                config: { ...data.config, schedule: scheduleConfig },
              })
            }
          />
        </TabsContent>

        <TabsContent value="email">
          <EmailConfig
            config={data.config.email}
            onChange={(emailConfig) =>
              onChange({
                ...data,
                config: { ...data.config, email: emailConfig },
              })
            }
          />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default TriggerConfig;
