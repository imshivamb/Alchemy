import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ActionNode } from "@/types/workflow.types";
import React from "react";
import AIConfig from "./action/ai-config";
import { Web3Config } from "./action/web3-config";
import { HTTPConfig } from "./action/http-config";
import { TransformConfig } from "./action/transform-config";

type ActionConfigProps = {
  data: ActionNode["data"];
  onChange: (data: Partial<ActionNode["data"]>) => void;
};

const ActionConfig = ({ data, onChange }: ActionConfigProps) => {
  const handleValidationChange = (isValid: boolean) => {
    onChange({
      ...data,
      isValid,
    });
  };
  return (
    <div className="space-y-4 p-4">
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
            onChange={(e) => onChange({ ...data, description: e.target.value })}
            placeholder="Enter description"
          />
        </div>
      </div>
      {/* Action Type Specific Config */}
      <Tabs
        defaultValue={data.actionType}
        onValueChange={(value: any) => onChange({ ...data, actionType: value })}
      >
        <TabsList className="w-full">
          <TabsTrigger value="ai">AI Process</TabsTrigger>
          <TabsTrigger value="web3">Web3</TabsTrigger>
          <TabsTrigger value="http">HTTP</TabsTrigger>
          <TabsTrigger value="transform">Transform</TabsTrigger>
        </TabsList>

        <TabsContent value="ai">
          <AIConfig
            config={data.config.ai}
            onChange={(aiConfig) =>
              onChange({
                ...data,
                config: { ...data.config, ai: aiConfig },
              })
            }
          />
        </TabsContent>
        <TabsContent value="web3">
          <Web3Config
            config={data.config.web3}
            onChange={(web3Config) =>
              onChange({
                ...data,
                config: { ...data.config, web3: web3Config },
              })
            }
          />
        </TabsContent>

        <TabsContent value="http">
          <HTTPConfig
            config={data.config.http}
            onChange={(httpConfig) =>
              onChange({
                ...data,
                config: { ...data.config, http: httpConfig },
              })
            }
          />
        </TabsContent>

        <TabsContent value="transform">
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
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ActionConfig;
