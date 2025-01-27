import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { FastAPIWebhook } from "@/types/webhook.types";
import { Copy, Eye, EyeOff } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { DynamicKeyValueInput } from "@/components/ui/dynamic-key-value-input";
import { TestWebhookDialog } from "@/components/workflow-builder/_components/test-webhook-dialog";

interface WebhookConfigurationProps {
  webhook: FastAPIWebhook;
}

export function WebhookConfiguration({ webhook }: WebhookConfigurationProps) {
  const [showSecret, setShowSecret] = useState(false);
  const [showTestDialog, setShowTestDialog] = useState(false);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard");
  };

  return (
    <div className="space-y-6">
      {/* Basic Configuration */}
      <Card className="p-4 space-y-4">
        <h3 className="text-lg font-medium">Basic Configuration</h3>

        <div className="space-y-2">
          <Label>Webhook URL</Label>
          <div className="flex gap-2">
            <Input value={webhook.config.url} readOnly />
            <Button
              variant="outline"
              onClick={() => copyToClipboard(webhook.config.url)}
            >
              <Copy className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div className="space-y-2">
          <Label>HTTP Method</Label>
          <Input value={webhook.config.method} readOnly />
        </div>
      </Card>

      {/* Secret Management */}
      <Card className="p-4 space-y-4">
        <h3 className="text-lg font-medium">Secret Management</h3>

        <div className="space-y-2">
          <Label>Secret Key</Label>
          <div className="flex gap-2">
            <Input
              type={showSecret ? "text" : "password"}
              value={webhook.secret.key}
              readOnly
            />
            <Button
              variant="outline"
              onClick={() => setShowSecret(!showSecret)}
            >
              {showSecret ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </Button>
            <Button
              variant="outline"
              onClick={() => copyToClipboard(webhook.secret.key)}
            >
              <Copy className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div className="space-y-2">
          <Label>Signature Header Name</Label>
          <Input value={webhook.secret.header_name} readOnly />
        </div>
      </Card>

      {/* Headers Configuration */}
      <Card className="p-4 space-y-4">
        <h3 className="text-lg font-medium">Headers</h3>
        <DynamicKeyValueInput
          values={webhook.config.headers}
          onChange={() => {}}
          readOnly
        />
      </Card>

      {/* Retry Configuration */}
      <Card className="p-4 space-y-4">
        <h3 className="text-lg font-medium">Retry Strategy</h3>

        <div className="space-y-2">
          <Label>Max Retries</Label>
          <Input value={webhook.config.retry_strategy.max_retries} readOnly />
        </div>

        <div className="space-y-2">
          <Label>Initial Interval (seconds)</Label>
          <Input
            value={webhook.config.retry_strategy.initial_interval}
            readOnly
          />
        </div>
      </Card>
      <TestWebhookDialog
        isOpen={showTestDialog}
        onClose={() => setShowTestDialog(false)}
        webhookUrl={webhook.config.url}
        headers={webhook.config.headers}
        authentication={webhook.config.authentication}
      />
    </div>
  );
}
