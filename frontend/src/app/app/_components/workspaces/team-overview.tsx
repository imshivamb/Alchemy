'use client';

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useWorkspaceStore } from "@/stores/workspace.store";
import { useEffect, useState } from "react";
import Link from "next/link";
import { LoadingSpinner } from "@/components/ui/loading-spinner";

export const TeamsOverview = () => {
  const { currentWorkspace, isLoading, error } = useWorkspaceStore();
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    const fetchStats = async () => {
      if (currentWorkspace?.id) {
        try {
          const stats = await useWorkspaceStore
            .getState()
            .getWorkspaceStats(currentWorkspace.id);
          setStats(stats);
        } catch (error) {
          console.error("Failed to fetch stats:", error);
        }
      }
    };

    fetchStats();
  }, [currentWorkspace?.id]);

  if (!currentWorkspace) return null;
  if (!stats && isLoading) {
    return (
      <Card>
        <CardContent className="flex justify-center items-center min-h-[200px]">
          <LoadingSpinner />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent>
          <Alert variant="destructive">
            <AlertDescription>
              Failed to load teams information. Please try again.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!stats) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Teams</CardTitle>
        <CardDescription>
          Quick overview of your workspace teams
        </CardDescription>
      </CardHeader>
      <CardContent>
        {stats.teams.total === 0 ? (
          <Alert>
            <AlertDescription>
              No teams created yet. Start collaborating by creating your first
              team.
            </AlertDescription>
          </Alert>
        ) : (
          <div className="space-y-4">
            {/* Will be implemented when teams API is ready */}
            <Alert>
              <AlertDescription>
                You have {stats.teams.total} team(s). View all teams for
                details.
              </AlertDescription>
            </Alert>
          </div>
        )}

        <div className="mt-4 flex gap-2">
          <Link href="/teams" className="flex-1">
            <Button variant="outline" className="w-full">
              View All Teams
            </Button>
          </Link>
          {stats.teams.total < stats.teams.limit && (
            <Link href="/teams/new">
              <Button>Create Team</Button>
            </Link>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
