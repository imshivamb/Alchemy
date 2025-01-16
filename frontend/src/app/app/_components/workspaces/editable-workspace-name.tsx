"use client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState } from "react";

export const EditableWorkspaceName = ({
  initialName,
  onSave,
}: {
  initialName: string;
  onSave: (name: string) => Promise<void>;
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [workspaceName, setWorkspaceName] = useState(initialName);

  const handleSave = async () => {
    if (!workspaceName.trim()) return;
    await onSave(workspaceName);
    setIsEditing(false);
  };

  if (isEditing) {
    return (
      <div className="flex gap-2">
        <Input
          value={workspaceName}
          onChange={(e) => setWorkspaceName(e.target.value)}
          className="max-w-sm"
          placeholder="Enter workspace name"
        />
        <Button onClick={handleSave}>Save</Button>
        <Button
          variant="outline"
          onClick={() => {
            setIsEditing(false);
            setWorkspaceName(initialName);
          }}
        >
          Cancel
        </Button>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <span>{initialName}</span>
      <Button variant="ghost" size="sm" onClick={() => setIsEditing(true)}>
        Edit
      </Button>
    </div>
  );
};
