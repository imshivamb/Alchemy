import { Button } from "@/components/ui/button";
import { ChevronRight, Users } from "lucide-react";

export const TeamCard = ({
  name,
  memberCount,
}: {
  name: string;
  memberCount: number;
}) => (
  <div className="flex items-center justify-between p-2 rounded-lg border">
    <div className="flex items-center gap-3">
      <Users className="h-5 w-5 text-muted-foreground" />
      <div>
        <h4 className="text-sm font-medium">{name}</h4>
        <p className="text-sm text-muted-foreground">
          {memberCount} {memberCount === 1 ? "member" : "members"}
        </p>
      </div>
    </div>
    <Button variant="ghost" size="sm">
      <ChevronRight className="h-4 w-4" />
    </Button>
  </div>
);
