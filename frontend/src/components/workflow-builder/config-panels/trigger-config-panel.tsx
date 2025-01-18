import { TriggerNode } from "@/types/workflow.types";
import { apps } from "@/config/apps.config";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Settings, Plus } from "lucide-react";
import EmailConfig from "./trigger/email-config";
import WebhookConfig from "./trigger/webhook-config";

interface TriggerConfigPanelProps {
  data: TriggerNode["data"];
  onChange: (data: Partial<TriggerNode["data"]>) => void;
}

export const TriggerConfigPanel: React.FC<TriggerConfigPanelProps> = ({
  data,
  onChange,
}) => {
  const app = apps.find((a) => a.id === data.appId);
  const trigger = app?.triggers?.find((t) => t.id === data.triggerId);

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {app?.icon && <app.icon className="h-5 w-5" />}
            <h2 className="font-semibold">
              {trigger?.name || "Choose Trigger"}
            </h2>
          </div>
          <Button variant="ghost" size="icon">
            <Settings className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Config Content */}
      <div className="flex-1 p-4 overflow-auto">
        {data.isConfigured ? (
          // Show specific config based on app and trigger
          <div className="space-y-4">
            {app?.id === "gmail" && trigger?.id === "new_email" && (
              <EmailConfig
                config={data.config.email}
                onChange={(emailConfig) =>
                  onChange({
                    ...data,
                    config: { ...data.config, email: emailConfig },
                  })
                }
              />
            )}
            {app?.id === "webhook" && (
              <WebhookConfig
                config={data.config.webhook}
                onChange={(webhookConfig) =>
                  onChange({
                    ...data,
                    config: { ...data.config, webhook: webhookConfig },
                  })
                }
              />
            )}
            {/* Add other app-specific configurations */}
          </div>
        ) : (
          // Show connection required state
          <Card className="p-6 text-center">
            <h3 className="font-medium mb-2">
              Connect your {app?.name} account
            </h3>
            <p className="text-sm text-gray-500 mb-4">
              To use this trigger, you need to connect your {app?.name} account
              first
            </p>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Connect Account
            </Button>
          </Card>
        )}
      </div>
    </div>
  );
};
