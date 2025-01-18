import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ActionNode } from "@/types/workflow.types";
import { apps } from "@/config/apps.config";
import React from "react";
import AIConfig from "./action/ai-config";
import { Web3Config } from "./action/web3-config";
import { HTTPConfig } from "./action/http-config";
import { TransformConfig } from "./action/transform-config";
import { Settings } from "lucide-react";
import { Button } from "@/components/ui/button";

type ActionConfigProps = {
  data: ActionNode["data"];
  onChange: (data: Partial<ActionNode["data"]>) => void;
};

const ActionConfigPanel = ({ data, onChange }: ActionConfigProps) => {
  const app = apps.find((a) => a.id === data.appId);
  const action = app?.actions?.find((a) => a.id === data.actionId);

  const handleValidationChange = (isValid: boolean) => {
    onChange({
      ...data,
      isValid,
    });
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {app?.icon && <app.icon className="h-5 w-5" />}
            <div>
              <h2 className="font-semibold">{action?.name || data.label}</h2>
              <p className="text-sm text-gray-500">{app?.name}</p>
            </div>
          </div>
          <Button variant="ghost" size="icon">
            <Settings className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Config Content */}
      <div className="flex-1 p-4 overflow-auto space-y-4">
        {/* Basic Information */}
        <div className="space-y-2">
          <div>
            <Label>Name</Label>
            <Input
              value={data.label}
              onChange={(e) => onChange({ ...data, label: e.target.value })}
              placeholder="Enter action name"
            />
          </div>
          <div>
            <Label>Description</Label>
            <Input
              value={data.description}
              onChange={(e) =>
                onChange({ ...data, description: e.target.value })
              }
              placeholder="Enter description"
            />
          </div>
        </div>

        {/* App-specific configurations */}
        {data.appId === "ai" && data.config.ai && (
          <AIConfig
            config={data.config.ai}
            onChange={(aiConfig) =>
              onChange({
                ...data,
                config: { ...data.config, ai: aiConfig },
              })
            }
          />
        )}
        {data.appId === "web3" && data.config.web3 && (
          <Web3Config
            config={data.config.web3}
            onChange={(web3Config) =>
              onChange({
                ...data,
                config: { ...data.config, web3: web3Config },
              })
            }
          />
        )}
        {data.appId === "webhook" && data.config.http && (
          <HTTPConfig
            config={data.config.http}
            onChange={(httpConfig) =>
              onChange({
                ...data,
                config: { ...data.config, http: httpConfig },
              })
            }
          />
        )}
        {data.appId === "transform" && data.config.transform && (
          <TransformConfig
            onValidationChange={handleValidationChange}
            config={data.config.transform}
            onChange={(transformConfig) =>
              onChange({
                ...data,
                config: { ...data.config, transform: transformConfig },
              })
            }
          />
        )}

        {/* Add new app-specific configurations here */}
        {data.appId === "gmail" && (
          // Gmail specific config
          <>Gmail</>
        )}
        {data.appId === "sheets" && (
          // Google Sheets specific config
          <>Google Sheets</>
        )}
        {/* Add other app configs */}
      </div>
    </div>
  );
};

export default ActionConfigPanel;
