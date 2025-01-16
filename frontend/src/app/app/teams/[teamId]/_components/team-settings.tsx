"use client";

import { useState } from "react";
import { TeamDetail } from "@/types/teams.types";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useRouter } from "next/navigation";
import { useTeamStore } from "@/stores/team.store";
import { useToast } from "@/hooks/use-toast";

interface TeamSettingsProps {
  team: TeamDetail;
}

export function TeamSettings({ team }: TeamSettingsProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState(team.name);
  const [description, setDescription] = useState(team.description);

  const { updateTeam, deleteTeam, isLoading } = useTeamStore();
  const { toast } = useToast();
  const router = useRouter();

  const handleUpdate = async () => {
    try {
      await updateTeam(team.id, { name, description });
      toast({
        title: "Success",
        description: "Team settings updated successfully",
      });
      setIsEditing(false);
    } catch (error) {
      console.log("Error updating team settings:", error);
      toast({
        title: "Error",
        description: "Failed to update team settings",
        variant: "destructive",
      });
    }
  };

  const handleDelete = async () => {
    if (
      confirm(
        "Are you sure you want to delete this team? This action cannot be undone."
      )
    ) {
      try {
        await deleteTeam(team.id);
        toast({
          title: "Success",
          description: "Team deleted successfully",
        });
        router.push("/teams");
      } catch (error) {
        console.log("Error deleting team:", error);
        toast({
          title: "Error",
          description: "Failed to delete team",
          variant: "destructive",
        });
      }
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Team Settings</CardTitle>
          <CardDescription>
            Manage your team settings and preferences
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Team Name</label>
              {isEditing ? (
                <Input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Enter team name"
                />
              ) : (
                <div className="flex items-center justify-between">
                  <p className="text-sm">{team.name}</p>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setIsEditing(true)}
                  >
                    Edit
                  </Button>
                </div>
              )}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Description</label>
              {isEditing ? (
                <Textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Enter team description"
                />
              ) : (
                <p className="text-sm text-muted-foreground">
                  {team.description}
                </p>
              )}
            </div>

            {isEditing && (
              <div className="flex items-center space-x-2">
                <Button onClick={handleUpdate} disabled={isLoading}>
                  {isLoading ? "Saving..." : "Save Changes"}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setIsEditing(false);
                    setName(team.name);
                    setDescription(team.description);
                  }}
                >
                  Cancel
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-destructive">Danger Zone</CardTitle>
          <CardDescription>
            Irreversible and destructive actions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertDescription>
              Deleting the team will remove all members and data associated with
              it. This action cannot be undone.
            </AlertDescription>
          </Alert>
          <Button
            variant="destructive"
            className="mt-4"
            onClick={handleDelete}
            disabled={isLoading}
          >
            {isLoading ? "Deleting..." : "Delete Team"}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
