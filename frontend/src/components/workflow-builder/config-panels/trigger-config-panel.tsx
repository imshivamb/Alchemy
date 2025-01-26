import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { apps } from "@/config/apps.config";
import { TriggerNode } from "@/types/workflow.types";
import { Plus } from "lucide-react";
import React from "react";
import { toast } from "sonner";
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
      <div className="flex-1 p-4 overflow-auto">
        {app?.id === "webhook" && trigger?.id === "incoming_webhook" ? (
          <div className="space-y-4">
            {data.config?.webhook?.webhookUrl ? (
              <>
                <div className="p-4 border rounded-lg bg-gray-50">
                  <Label>Webhook URL</Label>
                  <div className="flex items-center gap-2 mt-1">
                    <Input
                      readOnly
                      value={data.config.webhook.webhookUrl || ""}
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        navigator.clipboard.writeText(
                          data.config.webhook?.webhookUrl || ""
                        );
                        toast.success("URL copied");
                      }}
                    >
                      Copy
                    </Button>
                  </div>
                </div>
                <WebhookConfig
                  config={data.config.webhook}
                  onChange={(webhookConfig) => {
                    onChange({
                      ...data,
                      config: { ...data.config, webhook: webhookConfig },
                    });
                  }}
                />
              </>
            ) : (
              <Card className="p-6 text-center">
                <h3 className="font-medium mb-2">Webhook Configuration</h3>
                <p className="text-sm text-gray-500 mb-4">
                  Configure your webhook settings after URL generation
                </p>
              </Card>
            )}
          </div>
        ) : data.isConfigured ? (
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
          </div>
        ) : (
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
