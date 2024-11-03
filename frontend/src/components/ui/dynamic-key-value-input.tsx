import React from "react";
import { PlusCircle, Trash2 } from "lucide-react";
import { Input } from "./input";
import { Button } from "./button";

interface DynamicKeyValueInputProps {
  values: Record<string, string>;
  onChange: (values: Record<string, string>) => void;
  keyPlaceholder?: string;
  valuePlaceholder?: string;
  readOnly?: boolean;
}

export const DynamicKeyValueInput = ({
  values,
  onChange,
  keyPlaceholder = "Key",
  valuePlaceholder = "Value",
  readOnly = false,
}: DynamicKeyValueInputProps) => {
  const addKeyValue = () => {
    const newKey = `key-${Object.keys(values).length + 1}`;
    onChange({ ...values, [newKey]: "" });
  };

  const removeKeyValue = (key: string) => {
    const newValues = { ...values };
    delete newValues[key];
    onChange(newValues);
  };

  const updateKey = (oldKey: string, newKey: string) => {
    const newValues = { ...values };
    const value = newValues[oldKey];
    delete newValues[oldKey];
    newValues[newKey] = value;
    onChange(newValues);
  };

  const updateValue = (key: string, value: string) => {
    onChange({ ...values, [key]: value });
  };

  return (
    <div className="sapce-y-2">
      {Object.entries(values).map(([key, value], index) => (
        <div className="flex gap-2" key={index}>
          <Input
            className="flex-1"
            value={key}
            onChange={(e) => updateKey(key, e.target.value)}
            placeholder={keyPlaceholder}
            readOnly={readOnly}
          />
          <Input
            className="flex-1"
            value={value}
            onChange={(e) => updateValue(key, e.target.value)}
            placeholder={valuePlaceholder}
            readOnly={readOnly}
          />
          {!readOnly && (
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={() => removeKeyValue(key)}
              className="size-9"
            >
              <Trash2 className="size-4" />
            </Button>
          )}
        </div>
      ))}
      {!readOnly && (
        <Button
          type="button"
          variant="outline"
          className="w-full"
          onClick={addKeyValue}
        >
          <PlusCircle className="mr-2 size-4" />
          Add {keyPlaceholder}
        </Button>
      )}
    </div>
  );
};
