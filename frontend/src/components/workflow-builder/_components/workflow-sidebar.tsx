import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { FileText, Activity, Info, History, Home } from "lucide-react";
import Link from "next/link";

interface WorkflowSidebarProps {
  selectedPanel: string | null;
  onPanelChange: (panel: string | null) => void;
}

export const WorkflowSidebar = ({
  selectedPanel,
  onPanelChange,
}: WorkflowSidebarProps) => {
  return (
    <div className="w-[55px] border-l bg-background flex flex-col items-center py-4 px-2">
      <TooltipProvider>
        <div className="space-y-6">
          <Tooltip>
            <TooltipTrigger asChild>
              <Link href="/app/home">
                <Button variant="ghost" size="icon">
                  <Home className="!size-5" />
                </Button>
              </Link>
            </TooltipTrigger>
            <TooltipContent side="left">
              <p>Home</p>
            </TooltipContent>
          </Tooltip>

          {[
            { id: "notes", icon: FileText, label: "Notes" },
            { id: "status", icon: Activity, label: "Status" },
            { id: "history", icon: History, label: "Run History" },
            { id: "details", icon: Info, label: "Details" },
          ].map(({ id, icon: Icon, label }) => (
            <Tooltip key={id}>
              <TooltipTrigger asChild>
                <Button
                  variant={selectedPanel === id ? "secondary" : "ghost"}
                  size="icon"
                  onClick={() =>
                    onPanelChange(selectedPanel === id ? null : id)
                  }
                >
                  <Icon className="!size-5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="left">
                <p>{label}</p>
              </TooltipContent>
            </Tooltip>
          ))}
        </div>
      </TooltipProvider>
    </div>
  );
};
