"use client";

import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { PlusCircle, Trash2 } from "lucide-react";

import {
  ConditionNode,
  ConditionRule,
  ConditionGroup,
  ConditionOperator,
} from "@/types/workflow.types";

interface ConditionConfigProps {
  data: ConditionNode["data"];
  onChange: (data: Partial<ConditionNode["data"]>) => void;
}

export const ConditionConfig: React.FC<ConditionConfigProps> = ({
  data,
  onChange,
}) => {
  const getConditionGroupRules = (
    group: ConditionGroup | ConditionRule
  ): ConditionRule[] => {
    if ("rules" in group) {
      return (group as ConditionGroup).rules.filter(
        (rule): rule is ConditionRule => !("rules" in rule)
      );
    }
    return [];
  };

  const addRule = (groupIndex: number) => {
    const newCondition = { ...data.config.condition };
    const newRule: ConditionRule = {
      field: "",
      operator: "equals",
      value: "",
      valueType: "string",
    };

    if ("rules" in newCondition.rules[groupIndex]) {
      (newCondition.rules[groupIndex] as ConditionGroup).rules.push(newRule);
      onChange({
        ...data,
        config: { ...data.config, condition: newCondition },
      });
    }
  };

  const removeRule = (groupIndex: number, ruleIndex: number) => {
    const newCondition = { ...data.config.condition };
    if ("rules" in newCondition.rules[groupIndex]) {
      (newCondition.rules[groupIndex] as ConditionGroup).rules.splice(
        ruleIndex,
        1
      );
      onChange({
        ...data,
        config: { ...data.config, condition: newCondition },
      });
    }
  };

  const mainGroup = data.config.condition.rules[0] as ConditionGroup;
  const rules = getConditionGroupRules(mainGroup);

  return (
    <div className="space-y-4 p-4">
      {/* Basic Information */}
      <div className="space-y-2">
        <Input
          placeholder="Condition Name"
          value={data.label}
          onChange={(e) => onChange({ ...data, label: e.target.value })}
        />

        <Select
          value={data.config.condition.operator}
          onValueChange={(value: "and" | "or") =>
            onChange({
              ...data,
              config: {
                ...data.config,
                condition: {
                  ...data.config.condition,
                  operator: value,
                },
              },
            })
          }
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="and">AND</SelectItem>
            <SelectItem value="or">OR</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Rules */}
      <div className="space-y-2">
        {rules.map((rule, ruleIndex) => (
          <Card key={ruleIndex}>
            <CardContent className="space-y-2 p-4">
              <div className="flex items-center gap-2">
                <Input
                  placeholder="Field"
                  value={rule.field}
                  onChange={(e) => {
                    const newRules = [...rules];
                    newRules[ruleIndex] = { ...rule, field: e.target.value };
                    onChange({
                      ...data,
                      config: {
                        ...data.config,
                        condition: {
                          ...data.config.condition,
                          rules: [
                            {
                              operator: data.config.condition.operator,
                              rules: newRules,
                            },
                          ],
                        },
                      },
                    });
                  }}
                />

                <Select
                  value={rule.operator}
                  onValueChange={(value: ConditionOperator) => {
                    const newRules = [...rules];
                    newRules[ruleIndex] = { ...rule, operator: value };
                    onChange({
                      ...data,
                      config: {
                        ...data.config,
                        condition: {
                          ...data.config.condition,
                          rules: [
                            {
                              operator: data.config.condition.operator,
                              rules: newRules,
                            },
                          ],
                        },
                      },
                    });
                  }}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="equals">Equals</SelectItem>
                    <SelectItem value="not_equals">Not Equals</SelectItem>
                    <SelectItem value="greater_than">Greater Than</SelectItem>
                    <SelectItem value="less_than">Less Than</SelectItem>
                    <SelectItem value="contains">Contains</SelectItem>
                    <SelectItem value="not_contains">Not Contains</SelectItem>
                  </SelectContent>
                </Select>

                <Input
                  placeholder="Value"
                  value={rule.value}
                  onChange={(e) => {
                    const newRules = [...rules];
                    newRules[ruleIndex] = { ...rule, value: e.target.value };
                    onChange({
                      ...data,
                      config: {
                        ...data.config,
                        condition: {
                          ...data.config.condition,
                          rules: [
                            {
                              operator: data.config.condition.operator,
                              rules: newRules,
                            },
                          ],
                        },
                      },
                    });
                  }}
                />

                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => removeRule(0, ruleIndex)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}

        <Button variant="outline" onClick={() => addRule(0)} className="w-full">
          <PlusCircle className="mr-2 h-4 w-4" />
          Add Rule
        </Button>
      </div>

      {/* Default Path */}
      <div>
        <Select
          value={data.config.defaultPath}
          onValueChange={(value: "true" | "false") =>
            onChange({
              ...data,
              config: {
                ...data.config,
                defaultPath: value,
              },
            })
          }
        >
          <SelectTrigger>
            <SelectValue placeholder="Select default path" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="true">True Path</SelectItem>
            <SelectItem value="false">False Path</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
};
