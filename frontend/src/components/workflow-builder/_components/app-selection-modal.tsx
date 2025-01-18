import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { apps } from "@/config/apps.config";
import { LucideIcon, Search } from "lucide-react";
import { useState } from "react";

type AppSelectionModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onSelectApp: (appId: string, triggerId: string) => void;
};

export const AppSelectionModal = ({
  isOpen,
  onClose,
  onSelectApp,
}: AppSelectionModalProps) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");

  const filteredApps = apps.filter(
    (app) =>
      app.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
      (selectedCategory === "all" || app.category === selectedCategory)
  );

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[800px] max-h-[80vh] overflow-auto">
        <DialogHeader>
          <DialogTitle>Choose an app</DialogTitle>
        </DialogHeader>

        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search apps..."
            className="pl-8"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* Category Tabs */}
        <Tabs defaultValue="all" onValueChange={setSelectedCategory}>
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="google">Google</TabsTrigger>
            <TabsTrigger value="communication">Communication</TabsTrigger>
            <TabsTrigger value="blockchain">Blockchain</TabsTrigger>
            <TabsTrigger value="ai">AI</TabsTrigger>
            <TabsTrigger value="automation">Automation</TabsTrigger>
          </TabsList>

          <TabsContent value={selectedCategory} className="mt-4">
            <div className="grid grid-cols-4 gap-4">
              {filteredApps.map((app) => (
                <AppCard
                  key={app.id}
                  {...app}
                  onClick={() => {
                    // This will open the trigger selection view
                    onSelectApp(app.id, "trigger");
                  }}
                />
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};

interface AppCardProps {
  icon: LucideIcon;
  name: string;
  description: string;
  onClick: () => void;
}

const AppCard = ({ icon: Icon, name, description, onClick }: AppCardProps) => {
  return (
    <button
      onClick={onClick}
      className="flex flex-col items-center p-4 border rounded-lg hover:border-blue-500 hover:shadow-sm transition-all bg-white"
    >
      <div className="w-12 h-12 rounded-lg bg-blue-50 flex items-center justify-center mb-3">
        <Icon className="h-6 w-6 text-blue-600" />
      </div>
      <h3 className="font-medium text-sm">{name}</h3>
      <p className="text-xs text-gray-500 text-center mt-1 line-clamp-2">
        {description}
      </p>
    </button>
  );
};
