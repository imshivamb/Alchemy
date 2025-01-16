'use client';

import { formatDate } from "@/lib/format-date";
import { UsageStats } from "./usage-stats";
import { PlanDisplay } from "./plan-display";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useWorkspaceStore } from "@/stores/workspace.store";
import React from "react";

export const WorkspaceOverview = () => {
  const { currentWorkspace } = useWorkspaceStore();
  const [stats, setStats] = React.useState<any>(null);

  React.useEffect(() => {
    // Fetch workspace stats
    const fetchStats = async () => {
      if (currentWorkspace?.id) {
        try {
          const stats = await useWorkspaceStore
            .getState()
            .getWorkspaceStats(currentWorkspace.id);
          setStats(stats);
        } catch (error) {
          console.error("Failed to fetch workspace stats:", error);
        }
      }
    };

    fetchStats();
  }, [currentWorkspace?.id]);

  if (!stats || !currentWorkspace) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Account Overview</CardTitle>
        <CardDescription>View your workspace status and usage</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex justify-between items-center">
          <PlanDisplay plan={stats.plan} />
          <div className="text-sm text-muted-foreground">
            Member since {formatDate(currentWorkspace.created_at)}
          </div>
        </div>

        <UsageStats
          title="Members"
          current={stats.members.total}
          limit={stats.members.limit}
        />

        <UsageStats
          title="Teams"
          current={stats.teams.total}
          limit={stats.teams.limit}
        />
      </CardContent>
    </Card>
  );
};
