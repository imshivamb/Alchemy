import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

interface NodeConnectionProps {
  onClick: () => void;
}

const NodeConnection = ({ onClick }: NodeConnectionProps) => {
  return (
    <div
      className="absolute -bottom-12 left-1/2 transform -translate-x-1/2 flex flex-col items-center"
      onClick={(e) => e.stopPropagation()}
    >
      <div className="w-px h-4 bg-gray-200" />
      <Button
        size="sm"
        variant="outline"
        className="rounded-full h-8 w-8 p-0 bg-white hover:bg-blue-50 hover:border-blue-500"
        onClick={onClick}
      >
        <Plus className="h-4 w-4" />
      </Button>
      <div className="w-px h-4 bg-gray-200" />
    </div>
  );
};

export default NodeConnection;
