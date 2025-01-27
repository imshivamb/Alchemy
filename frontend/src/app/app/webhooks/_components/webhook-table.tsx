import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { Edit, Trash2, Play } from "lucide-react";
import { FastAPIWebhook, WebhookStatus } from "@/types/webhook.types";
import { formatDistanceToNow } from "date-fns";
import { WebhookFilters as WebhookFilterComponent } from "./webhook-filters";
import { useState } from "react";
import { WebhookPagination } from "./webhook-pagination";
import { TestWebhookDialog } from "@/components/workflow-builder/_components/test-webhook-dialog";
import { useWebhookStore } from "@/stores/webhook.store";
import { toast } from "sonner";
import { DeleteWebhookModal } from "./modals/delete-webhook";

interface WebhookTableProps {
  webhooks: FastAPIWebhook[];
  searchQuery: string;
  onSelect: (webhook: FastAPIWebhook) => void;
}

interface FilterState {
  status?: WebhookStatus;
  search?: string;
  type?: "incoming" | "outgoing";
}

export function WebhookTable({
  webhooks,
  searchQuery,
  onSelect,
}: WebhookTableProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [filters, setFilters] = useState<FilterState>({});
  const [showTestDialog, setShowTestDialog] = useState(false);
  const [selectedWebhookForTest, setSelectedWebhookForTest] =
    useState<FastAPIWebhook | null>(null);
  const { deleteWebhook } = useWebhookStore();
  const [webhookToDelete, setWebhookToDelete] = useState<FastAPIWebhook | null>(
    null
  );

  const getStatusColor = (status: WebhookStatus): string => {
    switch (status) {
      case WebhookStatus.ACTIVE:
        return "text-green-500";
      case WebhookStatus.INACTIVE:
        return "text-yellow-500";
      case WebhookStatus.FAILED:
        return "text-red-500";
      default:
        return "text-gray-500";
    }
  };

  const getSuccessRate = (webhook: FastAPIWebhook): number => {
    if (webhook.total_deliveries === 0) return 0;
    return (webhook.successful_deliveries / webhook.total_deliveries) * 100;
  };

  const filteredWebhooks = webhooks.filter((webhook) => {
    if (
      searchQuery &&
      !webhook.name.toLowerCase().includes(searchQuery.toLowerCase())
    ) {
      return false;
    }
    if (filters.status && webhook.status !== filters.status) {
      return false;
    }
    return true;
  });

  const handleDelete = async () => {
    if (!webhookToDelete) return;

    try {
      await deleteWebhook(webhookToDelete.id);
      toast.success("Webhook deleted successfully");
    } catch (error) {
      console.log("Error deleting webhook:", error);
      toast.error("Failed to delete webhook");
    } finally {
      setWebhookToDelete(null);
    }
  };

  return (
    <div>
      <WebhookFilterComponent onFilterChange={setFilters} />

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>URL</TableHead>
            <TableHead>Last Triggered</TableHead>
            <TableHead>Success Rate</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {filteredWebhooks.map((webhook: FastAPIWebhook) => (
            <TableRow
              key={webhook.id}
              className="cursor-pointer"
              onClick={() => onSelect(webhook)}
            >
              <TableCell className="font-medium">{webhook.name}</TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  <Switch
                    checked={webhook.status === WebhookStatus.ACTIVE}
                    className={getStatusColor(webhook.status)}
                  />
                  <span>{webhook.status}</span>
                </div>
              </TableCell>
              <TableCell
                className="max-w-[200px] truncate"
                title={webhook.config.url}
              >
                {webhook.config.url}
              </TableCell>
              <TableCell>
                {webhook.last_triggered
                  ? formatDistanceToNow(new Date(webhook.last_triggered), {
                      addSuffix: true,
                    })
                  : "Never"}
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div
                      className="bg-blue-600 h-2.5 rounded-full"
                      style={{ width: `${getSuccessRate(webhook)}%` }}
                    />
                  </div>
                  <span>{getSuccessRate(webhook).toFixed(0)}%</span>
                </div>
              </TableCell>
              <TableCell className="text-right">
                <div
                  className="flex items-center justify-end gap-2"
                  onClick={(e) => e.stopPropagation()}
                >
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => onSelect(webhook)}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setWebhookToDelete(webhook)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => {
                      setSelectedWebhookForTest(webhook);
                      setShowTestDialog(true);
                    }}
                  >
                    <Play className="h-4 w-4" />
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <div className="mt-4 flex justify-center">
        <WebhookPagination
          currentPage={currentPage}
          totalPages={Math.ceil(webhooks.length / 10)}
          onPageChange={setCurrentPage}
        />
      </div>

      <DeleteWebhookModal
        open={!!webhookToDelete}
        onClose={() => setWebhookToDelete(null)}
        onConfirm={handleDelete}
        webhookName={webhookToDelete?.name || ""}
        webhook={webhookToDelete!}
      />

      {selectedWebhookForTest && (
        <TestWebhookDialog
          isOpen={showTestDialog}
          onClose={() => {
            setShowTestDialog(false);
            setSelectedWebhookForTest(null);
          }}
          webhookUrl={selectedWebhookForTest.config.url}
          headers={selectedWebhookForTest.config.headers}
          authentication={selectedWebhookForTest.config.authentication}
        />
      )}
    </div>
  );
}
