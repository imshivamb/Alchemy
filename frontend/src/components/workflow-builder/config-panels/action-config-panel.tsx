import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ActionNode } from "@/types/workflow.types";
import React from "react";

type ActionConfigProps = {
  data: ActionNode["data"];
  onChange: (data: Partial<ActionNode["data"]>) => void;
};

const ActionConfig = ({ data, onChange }: ActionConfigProps) => {
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
          <AIConfig></AIConfig>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ActionConfig;
