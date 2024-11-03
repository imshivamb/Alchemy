"use client";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
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
import { Textarea } from "@/components/ui/textarea";
import {
  DataTransformConfig,
  ValidationResult,
  ValidationError,
} from "@/types/workflow.types";
import { useState } from "react";

interface TransformConfigProps {
  config: DataTransformConfig;
  onChange: (config: DataTransformConfig) => void;
  onValidationChange: (isValid: boolean) => void;
}

export const TransformConfig: React.FC<TransformConfigProps> = ({
  config,
  onChange,
  onValidationChange,
}) => {
  const [errors, setErrors] = useState<ValidationError[]>([]);

  const validateConfig = (newConfig: DataTransformConfig): ValidationResult => {
    const validationErrors: ValidationError[] = [];

    if (!newConfig.operations?.length) {
      validationErrors.push({
        nodeId: "transform",
        field: "operations",
        message: "At least one operation is required",
      });
    } else {
      newConfig.operations.forEach((op, index) => {
        if (!op.type) {
          validationErrors.push({
            nodeId: "transform",
            field: `operation_${index}_type`,
            message: "Operation type is required",
          });
        }
        if (!op.expression?.trim()) {
          validationErrors.push({
            nodeId: "transform",
            field: `operation_${index}_expression`,
            message: "Expression is required",
          });
        }
      });
    }

    if (Object.keys(newConfig.inputMapping || {}).length === 0) {
      validationErrors.push({
        nodeId: "transform",
        field: "inputMapping",
        message: "At least one input mapping is required",
      });
    }

    if (Object.keys(newConfig.outputMapping || {}).length === 0) {
      validationErrors.push({
        nodeId: "transform",
        field: "outputMapping",
        message: "At least one output mapping is required",
      });
    }

    return {
      isValid: validationErrors.length === 0,
      errors: validationErrors,
    };
  };

  const handleChange = (newConfig: DataTransformConfig) => {
    const validationResult = validateConfig(newConfig);
    setErrors(validationResult.errors);
    onValidationChange(validationResult.isValid);
    onChange(newConfig);
  };

  const getErrorMessage = (field: string): string | undefined => {
    const error = errors.find((err) => err.field === field);
    return error?.message;
  };

  return (
    <div className="space-y-4">
      {/* Operations */}
      <div className="space-y-2">
        <Label>Operations</Label>
        <div className="max-h-60 overflow-y-auto space-y-2">
          {config.operations.map((op, index) => (
            <Card key={index} className="p-2">
              <div className="space-y-2">
                <Select
                  value={op.type}
                  onValueChange={(value) => {
                    const newOps = [...config.operations];
                    newOps[index] = { ...op, type: value as any };
                    handleChange({ ...config, operations: newOps });
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select operation type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="map">Map</SelectItem>
                    <SelectItem value="filter">Filter</SelectItem>
                    <SelectItem value="reduce">Reduce</SelectItem>
                    <SelectItem value="sort">Sort</SelectItem>
                    <SelectItem value="transform">Transform</SelectItem>
                  </SelectContent>
                </Select>
                {getErrorMessage(`operation_${index}_type`) && (
                  <span className="text-xs text-red-500">
                    {getErrorMessage(`operation_${index}_type`)}
                  </span>
                )}

                <Input
                  placeholder="Field (optional)"
                  value={op.field || ""}
                  onChange={(e) => {
                    const newOps = [...config.operations];
                    newOps[index] = { ...op, field: e.target.value };
                    handleChange({ ...config, operations: newOps });
                  }}
                />

                <Textarea
                  placeholder="Expression"
                  value={op.expression || ""}
                  onChange={(e) => {
                    const newOps = [...config.operations];
                    newOps[index] = { ...op, expression: e.target.value };
                    handleChange({ ...config, operations: newOps });
                  }}
                />
                {getErrorMessage(`operation_${index}_expression`) && (
                  <span className="text-xs text-red-500">
                    {getErrorMessage(`operation_${index}_expression`)}
                  </span>
                )}

                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => {
                    const newOps = config.operations.filter(
                      (_, i) => i !== index
                    );
                    handleChange({ ...config, operations: newOps });
                  }}
                >
                  Remove
                </Button>
              </div>
            </Card>
          ))}
        </div>
        <Button
          onClick={() => {
            handleChange({
              ...config,
              operations: [
                ...config.operations,
                { type: "map", expression: "" },
              ],
            });
          }}
        >
          Add Operation
        </Button>
      </div>

      {/* Input/Output Mapping */}
      <div className="space-y-4">
        <div>
          <Label>Input Mapping</Label>
          <DynamicKeyValueInput
            values={config.inputMapping}
            onChange={(mapping) => {
              handleChange({ ...config, inputMapping: mapping });
            }}
          />
          {getErrorMessage("inputMapping") && (
            <span className="text-xs text-red-500">
              {getErrorMessage("inputMapping")}
            </span>
          )}
        </div>

        <div>
          <Label>Output Mapping</Label>
          <DynamicKeyValueInput
            values={config.outputMapping}
            onChange={(mapping) => {
              handleChange({ ...config, outputMapping: mapping });
            }}
          />
          {getErrorMessage("outputMapping") && (
            <span className="text-xs text-red-500">
              {getErrorMessage("outputMapping")}
            </span>
          )}
        </div>
      </div>

      {/* Error Behavior */}
      <div>
        <Label>Error Behavior</Label>
        <Select
          value={config.errorBehavior}
          onValueChange={(value: "skip" | "fail" | "default") => {
            handleChange({ ...config, errorBehavior: value });
          }}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select error behavior" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="skip">Skip</SelectItem>
            <SelectItem value="fail">Fail</SelectItem>
            <SelectItem value="default">Use Default</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
};
