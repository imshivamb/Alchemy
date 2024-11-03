import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useWorkflowState } from "@/stores/workflow.store";
import { NodeType, WorkflowNode } from "@/types/workflow.types";
import {
  Clock,
  Coins,
  FileJson2,
  GitBranch,
  Globe2,
  Mail,
  Webhook,
} from "lucide-react";
import React from "react";

interface NodeTypeButton {
  type: string;
  label: string;
  description: string;
  icon: React.ReactNode;
  category: NodeType;
  defaultConfig: any;
}

const nodeTypes: NodeTypeButton[] = [
  {
    type: "webhook",
    category: "trigger",
    label: "Webhook",
    description: "Start workflow with HTTP webhook",
    icon: <Webhook className="size-4" />,
    defaultConfig: { webhookUrl: "", method: "POST", headers: {} },
  },
  {
    type: "schedule",
    category: "trigger",
    label: "Schedule",
    description: "Time Based Trigger",
    icon: <Clock className="size-4" />,
    defaultConfig: {
      scheduleType: "cron",
      cronExpression: "",
      timezone: "UTC",
    },
  },
  {
    type: "email",
    category: "trigger",
    label: "Email",
    description: "Trigger on Email Events",
    icon: <Mail className="size-4" />,
    defaultConfig: { filters: [], folders: [], includeAttachments: false },
  },
  {
    type: "web3",
    category: "action",
    label: "Web3",
    description: "Blockchain Interactions",
    icon: <Coins className="size-4" />,
    defaultConfig: { network: "solana-mainnet", actionType: "transfer" },
  },
  {
    type: "http",
    category: "action",
    label: "HTTP Request",
    description: "Make HTTP Requests",
    icon: <Globe2 className="size-4" />,
    defaultConfig: { url: "", method: "GET", headers: {} },
  },
  {
    type: "transform",
    category: "action",
    label: "Transform",
    description: "Transform Data",
    icon: <FileJson2 className="size-4" />,
    defaultConfig: { operations: [], inputMapping: {}, outputMapping: {} },
  },
  {
    type: "condition",
    category: "condition",
    label: "Condition",
    icon: <GitBranch className="h-4 w-4" />,
    description: "Add conditional logic",
    defaultConfig: {
      condition: { operator: "and", rules: [] },
      defaultPath: "true",
    },
  },
];

const NodePalette = () => {
  const { addNode } = useWorkflowState();

  const handleAddNode = (nodeType: NodeTypeButton) => {
    const newNode: Partial<WorkflowNode> = {
      id: `${nodeType.category}-${Date.now()}`,
      type: nodeType.category,
      position: { x: 100, y: 100 },
      data: {
        nodeType: nodeType.type,
        label: nodeType.label,
        description: nodeType.description,
        config: nodeType.defaultConfig,
        isValid: true,
      },
    };
    addNode(newNode as WorkflowNode);
  };

  return (
    <Card className="h-full overflow-hidden">
      <CardHeader className="px-4 py-3">
        <CardTitle className="text-lg">Add Nodes</CardTitle>
      </CardHeader>
      <CardContent className="p-4">
        <div className="space-y-6">
          {/* Triggers */}
          <div>
            <h3 className="mb-2 font-semibold text-sm">Triggers</h3>
            <div className="space-y-2">
              {nodeTypes
                .filter((node) => node.category === "trigger")
                .map((node) => (
                  <Button
                    key={node.type}
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => handleAddNode(node)}
                  >
                    {node.icon}
                    <span className="ml-2">{node.label}</span>
                  </Button>
                ))}
            </div>
          </div>

          {/* Actions */}
          <div>
            <h3 className="mb-2 font-semibold text-sm">Actions</h3>
            <div className="space-y-2">
              {nodeTypes
                .filter((node) => node.category === "action")
                .map((node) => (
                  <Button
                    key={node.type}
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => handleAddNode(node)}
                  >
                    {node.icon}
                    <span className="ml-2">{node.label}</span>
                  </Button>
                ))}
            </div>
          </div>

          {/* Conditions */}
          <div>
            <h3 className="mb-2 font-semibold text-sm">Logic</h3>
            <div className="space-y-2">
              {nodeTypes
                .filter((node) => node.category === "condition")
                .map((node) => (
                  <Button
                    key={node.type}
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => handleAddNode(node)}
                  >
                    {node.icon}
                    <span className="ml-2">{node.label}</span>
                  </Button>
                ))}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default NodePalette;
