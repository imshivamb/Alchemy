// components/workflow-builder/sidebar/NodePalette.tsx

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useWorkflowState } from "@/stores/workflow.store";
import {
  ActionNode,
  AIModelType,
  HTTPConfig,
  NodeType,
  TriggerNode,
  Web3ActionType,
  Web3Network,
  WorkflowNode,
} from "@/types/workflow.types";
import {
  Brain, // Added for AI
  Clock,
  Coins,
  FileJson2,
  GitBranch,
  Globe2,
  Mail,
  Webhook,
} from "lucide-react";
import React from "react";

type TriggerType = "webhook" | "schedule" | "email";
type ActionType = "ai" | "web3" | "http" | "transform";

interface NodeTypeButton {
  type: TriggerType | ActionType | string;
  label: string;
  description: string;
  icon: React.ReactNode;
  category: NodeType;
  defaultConfig: any;
}

const nodeTypes: NodeTypeButton[] = [
  {
    type: "webhook" as TriggerType,
    category: "trigger",
    label: "Webhook",
    description: "Start workflow with HTTP webhook",
    icon: <Webhook className="size-4" />,
    defaultConfig: { webhookUrl: "", method: "POST", headers: {} },
  },
  {
    type: "schedule" as TriggerType,
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
    type: "email" as TriggerType,
    category: "trigger",
    label: "Email",
    description: "Trigger on Email Events",
    icon: <Mail className="size-4" />,
    defaultConfig: { filters: [], folders: [], includeAttachments: false },
  },
  {
    type: "ai" as ActionType,
    category: "action",
    label: "AI Process",
    description: "Process with AI models",
    icon: <Brain className="size-4" />,
    defaultConfig: { model: "gpt-4", maxTokens: 150, temperature: 0.7 },
  },
  {
    type: "web3" as ActionType,
    category: "action",
    label: "Web3",
    description: "Blockchain Interactions",
    icon: <Coins className="size-4" />,
    defaultConfig: { network: "solana-mainnet", actionType: "transfer" },
  },
  {
    type: "http" as ActionType,
    category: "action",
    label: "HTTP Request",
    description: "Make HTTP Requests",
    icon: <Globe2 className="size-4" />,
    defaultConfig: { url: "", method: "GET", headers: {} },
  },
  {
    type: "transform" as ActionType,
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
    icon: <GitBranch className="size-4" />,
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
    let newNode: Partial<WorkflowNode>;

    switch (nodeType.category) {
      case "trigger": {
        const triggerConfig = {
          webhook:
            nodeType.type === "webhook"
              ? {
                  webhookUrl: "",
                  method: "POST" as const,
                  headers: {},
                  authentication: {
                    type: "none" as const,
                  },
                  retryConfig: {
                    maxRetries: 3,
                    retryInterval: 1000,
                  },
                }
              : undefined,
          schedule:
            nodeType.type === "schedule"
              ? {
                  scheduleType: "cron" as const,
                  cronExpression: "",
                  timezone: "UTC",
                  interval: {
                    value: 5,
                    unit: "minutes" as const,
                  },
                }
              : undefined,
          email:
            nodeType.type === "email"
              ? {
                  filters: [],
                  folders: [],
                  includeAttachments: false,
                  markAsRead: true,
                }
              : undefined,
        };

        newNode = {
          id: `${nodeType.category}-${Date.now()}`,
          type: "trigger",
          position: { x: 100, y: 100 },
          data: {
            triggerType: nodeType.type as TriggerNode["data"]["triggerType"],
            label: nodeType.label,
            description: nodeType.description,
            isValid: true,
            config: triggerConfig,
            outputSchema: {
              type: "object",
              properties: {},
            },
          },
        };
        break;
      }

      case "action": {
        const actionConfig: ActionNode["data"]["config"] = {
          ai: {
            model: "gpt-4" as AIModelType,
            temperature: 0.7,
            maxTokens: 150,
            prompt: "",
            systemMessage: "",
            outputFormat: "text" as const,
            preprocessors: [],
            fallbackBehavior: {
              retryCount: 3,
              fallbackModel: "gpt-3.5-turbo" as AIModelType,
            },
          },
          web3: {
            network: "solana-mainnet" as Web3Network,
            actionType: "transfer" as Web3ActionType,
            amount: "",
            recipient: "",
            token: {
              mint: "",
              decimals: 9,
            },
            gasConfig: {
              priorityFee: 0,
              maxFee: 0,
            },
          },
          http: {
            url: "",
            method: "GET" as HTTPConfig["method"],
            headers: {},
            body: "",
            authentication: {
              type: "none" as const,
              credentials: {},
            },
            retryConfig: {
              maxRetries: 3,
              retryInterval: 1000,
            },
            timeout: 30000,
          },
          transform: {
            operations: [],
            inputMapping: {},
            outputMapping: {},
            errorBehavior: "skip" as const,
          },
        };

        newNode = {
          id: `${nodeType.category}-${Date.now()}`,
          type: "action",
          position: { x: 100, y: 100 },
          data: {
            actionType: nodeType.type as ActionNode["data"]["actionType"],
            label: nodeType.label,
            description: nodeType.description,
            isValid: true,
            config: {
              ...actionConfig,
              [nodeType.type]: {
                ...actionConfig[nodeType.type as keyof typeof actionConfig],
                ...nodeType.defaultConfig,
              },
            },
            inputSchema: {
              type: "object",
              properties: {},
              required: [],
            },
            outputSchema: {
              type: "object",
              properties: {},
            },
          },
        };
        break;
      }

      case "condition": {
        newNode = {
          id: `${nodeType.category}-${Date.now()}`,
          type: "condition",
          position: { x: 100, y: 100 },
          data: {
            label: nodeType.label,
            description: nodeType.description,
            isValid: true,
            config: {
              condition: {
                operator: "and",
                rules: [],
              },
              defaultPath: "true",
              customLogic: "",
              timeout: 30000,
            },
            inputSchema: {
              type: "object",
              properties: {},
              required: [],
            },
          },
        };
        break;
      }
    }

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
