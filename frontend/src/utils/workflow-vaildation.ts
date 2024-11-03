import { Node, Edge } from "@xyflow/react";
import { WorkflowNode,  ConditionNode, ActionNode, TriggerNode, ConditionRule, ConditionGroup } from "@/types/workflow.types";

// Interfaces and Types
// interface WorkflowValidateError extends ValidationError {
//     type: "workflow" | "node" | "edge";
// }

interface ValidationResult {
    isValid: boolean;
    errors: string[]
}

// Type Guards
function isTriggerNode(node: WorkflowNode): node is TriggerNode {
    return node.type === 'trigger';
}

function isActionNode(node: WorkflowNode): node is ActionNode {
    return node.type === 'action';
}

function isConditionNode(node: WorkflowNode): node is ConditionNode {
    return node.type === 'condition';
}

// Main Workflow Validation
export const validationWorkflow = (nodes: Node[], edges: Edge[]): ValidationResult => {
    const errors: string[] = [];

    // If workflow has no nodes
    if (nodes.length === 0) {
        errors.push("Workflow must have at least one node");
        return { isValid: false, errors };
    }

    // Check for trigger node
    const triggerNodes = nodes.filter(node => node.type === "trigger");
    if (triggerNodes.length === 0) {
        errors.push("Workflow must have a trigger node");
    } else if (triggerNodes.length > 1) {
        errors.push("Workflow can only have one trigger node");
    }

    // Check for disconnected nodes (except trigger node)
    const connectNodes = new Set<string>();
    edges.forEach((edge) => {
        connectNodes.add(edge.source);
        connectNodes.add(edge.target);
    });

    nodes.forEach((node) => {
        if (node.type !== "trigger" && !connectNodes.has(node.id)) {
            errors.push(`Node ${node.data.label} is not connected`);
        }
    });

    // Check for valid node connections
    edges.forEach((edge) => {
        const sourceNode = nodes.find(node => node.id === edge.source);
        const targetNode = nodes.find(node => node.id === edge.target);

        if (!sourceNode || !targetNode) {
            errors.push('Invalid connection detected: missing node');
            return;
        }

        // Validate specific node type connections
        if (sourceNode.type === 'trigger' && targetNode.type === 'trigger') {
            errors.push('Trigger node cannot connect to another trigger node');
        }
    });

    // Validate Individual Nodes
    nodes.forEach((node) => {
        errors.push(...validateNode(node as WorkflowNode));
    });

    return {
        isValid: errors.length === 0,
        errors
    };
};

// Validate Node based on type
export const validateNode = (node: WorkflowNode): string[] => {
    const errors: string[] = [];

    // Common validations
    if (!node.data.label) {
        errors.push(`Node ${node.id} must have a label`);
    }

    // Type-specific validations
    if (isTriggerNode(node)) {
        errors.push(...validateTriggerNode(node));
    } else if (isActionNode(node)) {
        errors.push(...validateActionNode(node));
    } else if (isConditionNode(node)) {
        errors.push(...validateConditionNode(node));
    }

    return errors;
};

// Trigger Node Validation
const validateTriggerNode = (node: TriggerNode): string[] => {
    const errors: string[] = [];
    const { triggerType, config } = node.data;

    switch (triggerType) {
        case 'webhook':
            if (!config.webhook?.webhookUrl) {
                errors.push(`Webhook URL is required for node "${node.data.label}"`);
            }
            break;
        case 'schedule':
            if (!config.schedule?.cronExpression && !config.schedule?.interval) {
                errors.push(`Schedule configuration is required for node "${node.data.label}"`);
            }
            break;
        case 'email':
            if (!config.email?.filters?.length) {
                errors.push(`At least one email filter is required for node "${node.data.label}"`);
            }
            break;
    }

    return errors;
};

// Action Node Validation
const validateActionNode = (node: ActionNode): string[] => {
    const errors: string[] = [];
    const { actionType, config } = node.data;

    switch (actionType) {
        case 'ai':
            if (!config.ai?.model || !config.ai?.prompt) {
                errors.push(`AI configuration is incomplete for node "${node.data.label}"`);
            }
            break;
        case 'web3':
            if (!config.web3?.network || !config.web3?.actionType) {
                errors.push(`Web3 configuration is incomplete for node "${node.data.label}"`);
            }
            break;
        case 'http':
            if (!config.http?.url || !config.http?.method) {
                errors.push(`HTTP configuration is incomplete for node "${node.data.label}"`);
            }
            break;
    }

    return errors;
};

// Condition Node Validation
const validateConditionNode = (node: ConditionNode): string[] => {
    const errors: string[] = [];
    const { config } = node.data;

    if (!config.condition?.rules?.length) {
        errors.push(`At least one condition rule is required for node "${node.data.label}"`);
        return errors;
    }

    const validateRule = (rule: ConditionRule | ConditionGroup, index: number) => {
        if ('rules' in rule) {
            // This is a ConditionGroup
            if (!rule.operator) {
                errors.push(`Group ${index + 1} operator is missing in node "${node.data.label}"`);
            }
            rule.rules.forEach((subRule, subIndex) => {
                validateRule(subRule, subIndex);
            });
        } else {
            // This is a ConditionRule
            if (!rule.field || !rule.operator) {
                errors.push(`Condition rule ${index + 1} is incomplete in node "${node.data.label}"`);
            }
        }
    };

    config.condition.rules.forEach((rule, index) => {
        validateRule(rule, index);
    });

    if (!config.defaultPath) {
        errors.push(`Default path is required for node "${node.data.label}"`);
    }

    return errors;
};