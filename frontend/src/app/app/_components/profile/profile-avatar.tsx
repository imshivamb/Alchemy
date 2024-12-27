"use client";

import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { useUserStore } from "@/stores/user-store";
import { AuthStore } from "@/stores/auth.store";

export function ProfileAvatar() {
  const { toast } = useToast();
  const { refreshUserProfile, user } = AuthStore();
  const { updateProfilePicture, isUpdating } = useUserStore();

  // Add console.log to debug
  console.log("User data:", user);
  console.log("Profile picture URL:", user?.profile_picture);

  const fullProfilePictureUrl = user?.profile_picture
    ? `http://localhost:8000${user.profile_picture}`
    : null;

  console.log("Full Profile picture URL:", fullProfilePictureUrl);
  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];
      if (!file || !user?.id) return;

      try {
        const result = await updateProfilePicture(user.id, file);
        console.log("Upload result:", result);
        toast({
          title: "Success",
          description: "Profile picture updated successfully.",
        });
        refreshUserProfile();
      } catch (error) {
        console.error("Upload error:", error);
        toast({
          title: "Error",
          description: "Failed to update profile picture. Please try again.",
          variant: "destructive",
        });
      }
    },
    [updateProfilePicture, user?.id, toast, refreshUserProfile]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/*": [".jpeg", ".jpg", ".png", ".gif"],
    },
    maxFiles: 1,
    multiple: false,
  });

  return (
    <div>
      <div className="p-6">
        <div className="flex items-center gap-6">
          <Avatar className="h-20 w-20">
            <AvatarImage
              src={fullProfilePictureUrl || ""}
              alt="Profile picture"
            />
            <AvatarFallback>
              {user?.first_name?.charAt(0) || user?.email?.charAt(0)}
            </AvatarFallback>
          </Avatar>
          <div className="space-y-4">
            <div>
              <h3 className="text-base font-medium">Profile Picture</h3>
              <p className="text-xs text-muted-foreground">
                Choose a profile picture to personalize your account.
              </p>
            </div>
            <div {...getRootProps()} className="space-y-2">
              <input {...getInputProps()} />
              <Button disabled={isUpdating} variant="outline">
                {isUpdating ? "Uploading..." : "Change picture"}
              </Button>
              <p className="text-xs text-muted-foreground">
                {isDragActive
                  ? "Drop the image here"
                  : "JPG, PNG or GIF. Max file size 5MB."}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
