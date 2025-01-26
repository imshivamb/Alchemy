import React from "react";
import { DynamicKeyValueInput } from "@/components/ui/dynamic-key-value-input";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { WebhookConfig as WebhookConfigType } from "@/types/workflow.types";
import { TestWebhookDialog } from "../../_components/test-webhook-dialog";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

interface WebhookConfigProps {
  config?: WebhookConfigType;
  onChange: (config: WebhookConfigType) => void;
}

// Default values for WebhookConfigType
const defaultConfig: WebhookConfigType = {
  method: "POST",
  headers: {},
  authentication: {
    type: "none",
  },
  retryConfig: {
    maxRetries: 0,
    retryInterval: 0,
  },
};

export const WebhookConfig = ({
  config = defaultConfig,
  onChange,
}: WebhookConfigProps) => {
  // Helper function to handle authentication type changes
  const handleAuthTypeChange = (
    value: "none" | "basic" | "bearer" | "api-key"
  ) => {
    const newAuth = {
      type: value, // This is now required
      // Reset other auth fields when changing type
      ...(value === "basic"
        ? {
            username: config.authentication?.username,
            password: config.authentication?.password,
          }
        : value === "bearer"
        ? { token: config.authentication?.token }
        : value === "api-key"
        ? { apiKey: config.authentication?.apiKey }
        : {}),
    };

    onChange({
      ...config,
      authentication: newAuth,
    });
  };

  // Helper function to handle authentication field changes
  const handleAuthFieldChange = (field: string, value: string) => {
    const newAuth = {
      type: config.authentication?.type || "none",
      ...config.authentication,
      [field]: value,
    };

    onChange({
      ...config,
      authentication: newAuth,
    });
  };

  return (
    <div className="space-y-4">
      <div className=" ">
        <Label>Webhook URL</Label>
        <div className="flex flex-col space-y-3 gap-2">
          <Input
            placeholder="Generated webhook URL will appear here..."
            value={config.webhookUrl ?? ""}
            readOnly
          />
          <Button
            variant="outline"
            onClick={() => {
              if (config.webhookUrl) {
                navigator.clipboard.writeText(config.webhookUrl);
                toast.success("URL copied");
              }
            }}
          >
            Copy
          </Button>
          <TestWebhookDialog
            webhookUrl={config.webhookUrl ?? ""}
            headers={config.headers}
            authentication={config.authentication}
          />
        </div>
      </div>

      <div>
        <Label>Method</Label>
        <Select
          value={config.method}
          onValueChange={(value) =>
            onChange({
              ...config,
              method: value as WebhookConfigType["method"],
            })
          }
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="GET">GET</SelectItem>
            <SelectItem value="POST">POST</SelectItem>
            <SelectItem value="PUT">PUT</SelectItem>
            <SelectItem value="PATCH">PATCH</SelectItem>
            <SelectItem value="DELETE">DELETE</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div>
        <Label>Headers</Label>
        <DynamicKeyValueInput
          values={config.headers ?? {}}
          onChange={(headers) => onChange({ ...config, headers })}
        />
      </div>

      <div>
        <Label>Authentication</Label>
        <Select
          value={config.authentication?.type ?? "none"}
          onValueChange={handleAuthTypeChange}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">None</SelectItem>
            <SelectItem value="basic">Basic Auth</SelectItem>
            <SelectItem value="bearer">Bearer Token</SelectItem>
            <SelectItem value="api-key">API Key</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Conditional authentication fields based on type */}
      {config.authentication?.type === "basic" && (
        <>
          <div>
            <Label>Username</Label>
            <Input
              value={config.authentication?.username ?? ""}
              onChange={(e) =>
                handleAuthFieldChange("username", e.target.value)
              }
            />
          </div>
          <div>
            <Label>Password</Label>
            <Input
              type="password"
              value={config.authentication?.password ?? ""}
              onChange={(e) =>
                handleAuthFieldChange("password", e.target.value)
              }
            />
          </div>
        </>
      )}

      {config.authentication?.type === "bearer" && (
        <div>
          <Label>Bearer Token</Label>
          <Input
            value={config.authentication?.token ?? ""}
            onChange={(e) => handleAuthFieldChange("token", e.target.value)}
          />
        </div>
      )}

      {config.authentication?.type === "api-key" && (
        <div>
          <Label>API Key</Label>
          <Input
            value={config.authentication?.apiKey ?? ""}
            onChange={(e) => handleAuthFieldChange("apiKey", e.target.value)}
          />
        </div>
      )}

      <div>
        <Label>Max Retries</Label>
        <Input
          type="number"
          min="0"
          value={config.retryConfig?.maxRetries ?? 0}
          onChange={(e) =>
            onChange({
              ...config,
              retryConfig: {
                ...config.retryConfig,
                maxRetries: parseInt(e.target.value) || 0,
              },
            })
          }
        />
      </div>

      <div>
        <Label>Retry Interval (seconds)</Label>
        <Input
          type="number"
          min="0"
          value={config.retryConfig?.retryInterval ?? 0}
          onChange={(e) =>
            onChange({
              ...config,
              retryConfig: {
                ...config.retryConfig,
                retryInterval: parseInt(e.target.value) || 0,
              },
            })
          }
        />
      </div>
    </div>
  );
};

export default WebhookConfig;
