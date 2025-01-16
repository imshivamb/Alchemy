"use client";
import { useWorkspaceStore } from "@/stores/workspace.store";
import { EditableWorkspaceName } from "./editable-workspace-name";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export const WorkspacePreferences = () => {
  const { currentWorkspace, updateWorkspace } = useWorkspaceStore();

  if (!currentWorkspace) return null;

  const handleNameUpdate = async (newName: string) => {
    try {
      await updateWorkspace(currentWorkspace.id, { name: newName });
    } catch (error) {
      console.error("Failed to update workspace name:", error);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Workspace Preferences</CardTitle>
        <CardDescription>Manage your workspace settings</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <h4 className="text-sm font-medium mb-2">Workspace Name</h4>
            <EditableWorkspaceName
              initialName={currentWorkspace.name}
              onSave={handleNameUpdate}
            />
          </div>

          <div>
            <h4 className="text-sm font-medium mb-2">Default Timezone</h4>
            <div className="text-sm text-muted-foreground">
              {currentWorkspace.settings?.default_timezone || "UTC"}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
