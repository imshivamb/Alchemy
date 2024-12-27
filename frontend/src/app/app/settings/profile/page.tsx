import { Separator } from "@/components/ui/separator";
import { PageHeader } from "../../_components/page-header";
import { ProfileAvatar } from "../../_components/profile/profile-avatar";
import { ProfileForm } from "../../_components/profile/profile-form";

export default function ProfileSettingsPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        heading="Profile"
        text="Manage your personal information and preferences."
      />
      <Separator />
      {/* Profile settings content */}

      <ProfileAvatar />
      <ProfileForm />
    </div>
  );
}
