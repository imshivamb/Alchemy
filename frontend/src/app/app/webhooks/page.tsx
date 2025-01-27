"use client";

import { useEffect, useState } from "react";
import { FastAPIWebhook } from "@/types/webhook.types";
import { useWebhookStore } from "@/stores/webhook.store";
import { WebhookHeader } from "./_components/webhook-header";
import { WebhookTable } from "./_components/webhook-table";
import { WebhookDetailsPanel } from "./_components/webhook-details-panel";
import { CreateWebhookModal } from "./_components/modals/create-webhook";

export default function WebhooksPage() {
  const [selectedWebhook, setSelectedWebhook] = useState<FastAPIWebhook | null>(
    null
  );
  const [searchQuery, setSearchQuery] = useState("");
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const { webhooks, fetchWebhooks } = useWebhookStore();

  useEffect(()=> {
    fetchWebhooks();
  }, [])

  return (
    <div className="flex h-full">
      <div className="flex-1 flex flex-col">
        <WebhookHeader
          onSearch={setSearchQuery}
          onCreateNew={() => setIsCreateModalOpen(true)}
          onRefresh={fetchWebhooks}
        />
        <div className="flex-1 p-6">
          <WebhookTable
            webhooks={webhooks}
            searchQuery={searchQuery}
            onSelect={setSelectedWebhook}
          />
        </div>
      </div>

      {selectedWebhook && (
        <WebhookDetailsPanel
          webhook={selectedWebhook}
          onClose={() => setSelectedWebhook(null)}
        />
      )}

      <CreateWebhookModal
        open={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
      />
    </div>
  );
}
