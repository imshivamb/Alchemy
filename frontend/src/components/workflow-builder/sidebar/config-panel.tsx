import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useWorkflowState } from "@/stores/workflow.store";
import { WorkflowNode } from "@/types/workflow.types";
import { AlertCircle } from "lucide-react";
import React from "react";
import { ConditionConfig } from "../config-panels/condition-config-panel";
import ActionConfig from "../config-panels/action-config-panel";
import TriggerConfig from "../config-panels/trigger-config-panel";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";

type ConfigPanelProps = {
  selectedNode: WorkflowNode | null;
};

const ConfigPanel = ({ selectedNode }: ConfigPanelProps) => {
  const { updateNode } = useWorkflowState();

  if (!selectedNode) {
    return (
      <Card className="h-full">
        <CardContent className="p-4">
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <AlertCircle className="size-8 mb-2" />
            <p>Select a Node to configure</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const handleNodeUpdate = (data: any) => {
    updateNode(selectedNode.id, data);
  };
  return (
    <Card className="h-full overflow-auto">
      <CardHeader className="sticky top-0 bg-background z-10 pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Configure Node</CardTitle>
          <Badge
            variant={selectedNode.data.isValid ? "default" : "destructive"}
          >
            {selectedNode.type}
          </Badge>
        </div>
        {!selectedNode.data.isValid && (
          <Alert variant="destructive" className="mt-2">
            <AlertDescription>
              {selectedNode.data.errorMessage || "Invalid configuration"}
            </AlertDescription>
          </Alert>
        )}
      </CardHeader>
      <CardContent className="p-4">
        {selectedNode.type === "trigger" && (
          <TriggerConfig data={selectedNode.data} onChange={handleNodeUpdate} />
        )}
        {selectedNode.type === "action" && (
          <ActionConfig data={selectedNode.data} onChange={handleNodeUpdate} />
        )}
        {selectedNode.type === "condition" && (
          <ConditionConfig
            data={selectedNode.data}
            onChange={handleNodeUpdate}
          />
        )}
      </CardContent>
    </Card>
  );
};

export default ConfigPanel;
