import { AlertDialogFooter } from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { WebhookService } from "@/services/webhook-service";
import { WebhookAuthentication } from "@/types/webhook.types";
import { useState } from "react";
import { toast } from "sonner";

interface TestWebhookDialogProps {
  isOpen: boolean;
  onClose: () => void;
  webhookUrl: string;
  headers?: Record<string, string>;
  authentication?: WebhookAuthentication;
}

export const TestWebhookDialog = ({
  webhookUrl,
  headers = {},
  authentication,
}: TestWebhookDialogProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [testPayload, setTestPayload] = useState('{\n  "key": "value"\n}');
  const [testUrl, setTestUrl] = useState("");

  const buildHeaders = (): Record<string, string> => {
    const testHeaders: Record<string, string> = {
      "Content-Type": "application/json",
      ...headers,
    };

    if (authentication?.type) {
      switch (authentication.type) {
        case "basic":
          if (authentication.username && authentication.password) {
            testHeaders["Authorization"] = `Basic ${btoa(
              `${authentication.username}:${authentication.password}`
            )}`;
          }
          break;
        case "bearer":
          if (authentication.token) {
            testHeaders["Authorization"] = `Bearer ${authentication.token}`;
          }
          break;
        case "api-key":
          if (authentication.apiKey) {
            testHeaders["X-API-Key"] = authentication.apiKey;
          }
          break;
      }
    }

    return testHeaders;
  };

  const handleTest = async () => {
    if (!testUrl) {
      toast.error("Please enter a test URL");
      return;
    }

    try {
      // Validate JSON
      let parsedPayload;
      try {
        parsedPayload = JSON.parse(testPayload);
      } catch {
        toast.error("Invalid JSON payload");
        return;
      }

      // Use WebhookService for proxy call
      const result = await WebhookService.testWebhookProxy({
        target_url: testUrl,
        method: "POST",
        headers: buildHeaders(),
        payload: parsedPayload,
      });

      if (result.status >= 200 && result.status < 300) {
        toast.success("Webhook test successful");
        console.log("Webhook response:", result.body);
      } else {
        throw new Error(`Received status ${result.status} from target`);
      }
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error occurred";
      toast.error(`Webhook test failed: ${errorMessage}`);
      console.error("Full error details:", error);
    }
  };

  return (
    <>
      <Button
        variant="outline"
        onClick={() => setIsOpen(true)}
        disabled={!webhookUrl}
      >
        Test Webhook
      </Button>
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Test Webhook</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Test URL (where to send the request)</Label>
              <Input
                value={testUrl}
                onChange={(e) => setTestUrl(e.target.value)}
                placeholder="Enter URL to test (e.g., webhook.site URL)"
              />
            </div>

            <div>
              <Label>Your Webhook URL (for reference)</Label>
              <div className="flex gap-2">
                <Input value={webhookUrl} readOnly />
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    navigator.clipboard.writeText(webhookUrl);
                    toast.success("URL copied to clipboard");
                  }}
                >
                  Copy
                </Button>
              </div>
            </div>

            <div>
              <Label>Test Payload (JSON)</Label>
              <Textarea
                value={testPayload}
                onChange={(e) => setTestPayload(e.target.value)}
                className="font-mono"
                rows={6}
              />
            </div>
            <AlertDialogFooter>
              <div className="flex gap-2 w-full justify-between">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => window.open("https://webhook.site", "_blank")}
                >
                  Open webhook.site for testing
                </Button>
                <div className="flex gap-2">
                  <Button variant="outline" onClick={() => setIsOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleTest}>Send Test Request</Button>
                </div>
              </div>
            </AlertDialogFooter>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};
