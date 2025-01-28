import { Workflow } from "@/types/workflow-api.types";
import { SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDistanceToNow } from "date-fns";

interface WorkflowDetailsPanelProps {
  workflow: Workflow;
  onClose: () => void;
}

export function WorkflowDetailsPanel({ workflow }: WorkflowDetailsPanelProps) {
  return (
    <div className="space-y-6">
      <SheetHeader>
        <SheetTitle>{workflow.name}</SheetTitle>
      </SheetHeader>

      {/* Quick Stats */}
      <div className="grid grid-cols-3 gap-4">
        <Card className="p-4 text-center">
          <h4 className="text-sm font-medium text-muted-foreground">Status</h4>
          <Badge
            variant={workflow.is_active ? "default" : "secondary"}
            className="mt-2"
          >
            {workflow.is_active ? "Active" : "Inactive"}
          </Badge>
        </Card>
        <Card className="p-4 text-center">
          <h4 className="text-sm font-medium text-muted-foreground">Tasks</h4>
          <p className="text-2xl font-bold mt-2">{workflow.task_count}</p>
        </Card>
        <Card className="p-4 text-center">
          <h4 className="text-sm font-medium text-muted-foreground">
            Webhooks
          </h4>
          <p className="text-2xl font-bold mt-2">{workflow.webhook_count}</p>
        </Card>
      </div>

      <Tabs defaultValue="details">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="details">Details</TabsTrigger>
          <TabsTrigger value="tasks">Tasks</TabsTrigger>
          <TabsTrigger value="webhooks">Webhooks</TabsTrigger>
        </TabsList>

        <TabsContent value="details" className="space-y-4">
          <Card className="p-4">
            <h3 className="font-medium mb-2">Description</h3>
            <p className="text-sm text-muted-foreground">
              {workflow.description || "No description provided"}
            </p>
          </Card>

          <Card className="p-4">
            <h3 className="font-medium mb-2">Timeline</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Created</span>
                <span>
                  {formatDistanceToNow(new Date(workflow.created_at), {
                    addSuffix: true,
                  })}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Last Updated</span>
                <span>
                  {formatDistanceToNow(new Date(workflow.updated_at), {
                    addSuffix: true,
                  })}
                </span>
              </div>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="tasks" className="space-y-4">
          {workflow.tasks.length > 0 ? (
            workflow.tasks.map((task) => (
              <Card key={task.id} className="p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-medium">{task.name}</h4>
                    <p className="text-sm text-muted-foreground">
                      Type: {task.task_type}
                    </p>
                  </div>
                  <Badge>{task.is_active ? "Active" : "Inactive"}</Badge>
                </div>
              </Card>
            ))
          ) : (
            <p className="text-center text-muted-foreground py-4">
              No tasks configured
            </p>
          )}
        </TabsContent>

        <TabsContent value="webhooks" className="space-y-4">
          {workflow.webhooks.length > 0 ? (
            workflow.webhooks.map((webhook) => (
              <Card key={webhook.id} className="p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-medium">{webhook.name}</h4>
                    <p className="text-sm text-muted-foreground">
                      Type: {webhook.webhook_type}
                    </p>
                  </div>
                  <Badge>{webhook.is_active ? "Active" : "Inactive"}</Badge>
                </div>
                {webhook.trigger_url && (
                  <p className="text-sm text-muted-foreground mt-2 truncate">
                    URL: {webhook.trigger_url}
                  </p>
                )}
              </Card>
            ))
          ) : (
            <p className="text-center text-muted-foreground py-4">
              No webhooks configured
            </p>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
