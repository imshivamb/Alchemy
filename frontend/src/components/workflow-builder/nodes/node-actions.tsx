import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { MoreVertical, Edit, Copy, MessageSquare } from "lucide-react";

interface NodeActionsProps {
  onRename: () => void;
  onCopy: () => void;
  onAddNote: () => void;
}

export const NodeActions = ({
  onRename,
  onCopy,
  onAddNote,
}: NodeActionsProps) => {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="h-8 w-8">
          <MoreVertical className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={onRename}>
          <Edit className="h-4 w-4 mr-2" />
          Rename
        </DropdownMenuItem>
        <DropdownMenuItem onClick={onCopy}>
          <Copy className="h-4 w-4 mr-2" />
          Duplicate
        </DropdownMenuItem>
        <DropdownMenuItem onClick={onAddNote}>
          <MessageSquare className="h-4 w-4 mr-2" />
          Add note
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
