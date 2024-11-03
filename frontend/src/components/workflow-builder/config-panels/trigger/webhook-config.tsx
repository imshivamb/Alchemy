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
      ...config.authentication,
      type: value,
      // Reset other auth fields when changing type
      username: value === "basic" ? config.authentication?.username : undefined,
      password: value === "basic" ? config.authentication?.password : undefined,
      token: value === "bearer" ? config.authentication?.token : undefined,
      apiKey: value === "api-key" ? config.authentication?.apiKey : undefined,
    };

    onChange({
      ...config,
      authentication: newAuth,
    });
  };

  // Helper function to handle authentication field changes
  const handleAuthFieldChange = (field: string, value: string) => {
    onChange({
      ...config,
      authentication: {
        ...config.authentication,
        [field]: value,
      },
    });
  };

  return (
    <div className="space-y-4">
      <div>
        <Label>Webhook URL</Label>
        <Input
          placeholder="https://..."
          value={config.webhookUrl ?? ""}
          onChange={(e) => onChange({ ...config, webhookUrl: e.target.value })}
        />
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
