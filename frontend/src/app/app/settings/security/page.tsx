import { Separator } from "@/components/ui/separator";
import { PageHeader } from "../../_components/page-header";
import { PasswordSection } from "../../_components/security/password-section";
import { ApiKeysSection } from "../../_components/security/api-keys-section";

export default function SecuritySettingsPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        heading="Security"
        text="Manage your account security settings and preferences."
      />
      <Separator />
      {/* Security settings content */}

      <PasswordSection />
      <Separator />
      <ApiKeysSection />
    </div>
  );
}
