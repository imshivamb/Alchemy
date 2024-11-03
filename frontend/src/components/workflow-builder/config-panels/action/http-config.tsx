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
import { HTTPConfig as HTTPConfigType } from "@/types/workflow.types";

interface HTTPConfigProps {
  config: HTTPConfigType;
  onChange: (config: HTTPConfigType) => void;
}

export const HTTPConfig: React.FC<HTTPConfigProps> = ({ config, onChange }) => {
  return (
    <div className="space-y-4">
      <Input
        placeholder="URL"
        value={config?.url ?? ""}
        onChange={(e) => onChange({ ...config, url: e.target.value })}
      />

      <Select
        value={config?.method ?? "GET"}
        onValueChange={(value) =>
          onChange({ ...config, method: value as HTTPConfigType["method"] })
        }
      >
        <SelectTrigger>
          <SelectValue placeholder="Select method" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="GET">GET</SelectItem>
          <SelectItem value="POST">POST</SelectItem>
          <SelectItem value="PUT">PUT</SelectItem>
          <SelectItem value="DELETE">DELETE</SelectItem>
          <SelectItem value="PATCH">PATCH</SelectItem>
        </SelectContent>
      </Select>

      {/* Headers */}
      <div className="space-y-2">
        <Label>Headers</Label>
        <DynamicKeyValueInput
          values={config?.headers ?? {}}
          onChange={(headers) => onChange({ ...config, headers })}
        />
      </div>

      {/* Authentication */}
      <div className="space-y-2">
        <Label>Authentication</Label>
        <Select
          value={config?.authentication?.type ?? "none"}
          onValueChange={(value) =>
            onChange({
              ...config,
              authentication: {
                ...config.authentication,
                type: value as HTTPConfigType["authentication"]["type"],
              },
            })
          }
        >
          <SelectTrigger>
            <SelectValue placeholder="Select auth type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">None</SelectItem>
            <SelectItem value="basic">Basic Auth</SelectItem>
            <SelectItem value="bearer">Bearer Token</SelectItem>
            <SelectItem value="api-key">API Key</SelectItem>
          </SelectContent>
        </Select>

        {/* Render different auth inputs based on type */}
        {config?.authentication?.type === "basic" && (
          <>
            <Input
              placeholder="Username"
              value={config?.authentication?.credentials?.username ?? ""}
              onChange={(e) =>
                onChange({
                  ...config,
                  authentication: {
                    ...config.authentication,
                    credentials: {
                      ...config.authentication.credentials,
                      username: e.target.value,
                    },
                  },
                })
              }
            />
            <Input
              type="password"
              placeholder="Password"
              value={config?.authentication?.credentials?.password ?? ""}
              onChange={(e) =>
                onChange({
                  ...config,
                  authentication: {
                    ...config.authentication,
                    credentials: {
                      ...config.authentication.credentials,
                      password: e.target.value,
                    },
                  },
                })
              }
            />
          </>
        )}

        {config?.authentication?.type === "bearer" && (
          <Input
            placeholder="Bearer token"
            value={config?.authentication?.credentials?.token ?? ""}
            onChange={(e) =>
              onChange({
                ...config,
                authentication: {
                  ...config.authentication,
                  credentials: {
                    token: e.target.value,
                  },
                },
              })
            }
          />
        )}
      </div>

      {/* Retry Configuration */}
      <div className="space-y-2">
        <Label>Retry Configuration</Label>
        <Input
          type="number"
          placeholder="Max retries"
          value={config?.retryConfig?.maxRetries ?? ""}
          onChange={(e) =>
            onChange({
              ...config,
              retryConfig: {
                ...config.retryConfig,
                maxRetries: parseInt(e.target.value),
              },
            })
          }
        />
        <Input
          type="number"
          placeholder="Retry interval (ms)"
          value={config?.retryConfig?.retryInterval ?? ""}
          onChange={(e) =>
            onChange({
              ...config,
              retryConfig: {
                ...config.retryConfig,
                retryInterval: parseInt(e.target.value),
              },
            })
          }
        />
      </div>

      <Input
        type="number"
        placeholder="Timeout (ms)"
        value={config?.timeout ?? ""}
        onChange={(e) =>
          onChange({ ...config, timeout: parseInt(e.target.value) })
        }
      />
    </div>
  );
};
