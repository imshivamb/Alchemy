"use client";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import {
  changePasswordSchema,
  type ChangePasswordValues,
} from "@/schemas/security-schema";
import { AuthStore } from "@/stores/auth.store";
import { useSecurityStore } from "@/stores/security.store";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

export function PasswordSection() {
  const { user } = AuthStore();
  const { changePassword, isLoading } = useSecurityStore();

  const form = useForm<ChangePasswordValues>({
    resolver: zodResolver(changePasswordSchema),
    defaultValues: {
      current_password: "",
      new_password: "",
      confirm_new_password: "",
    },
  });

  async function onSubmit(data: ChangePasswordValues) {
    if (!user?.id) return;

    try {
      await changePassword(user.id, data.current_password, data.new_password);
      toast.success("Password updated successfully", {
        description: "Your password has been changed.",
      });
      form.reset();
    } catch (error) {
      console.error("Change password error:", error);
      toast.error("Failed to update password", {
        description:
          error instanceof Error ? error.message : "Please try again later.",
      });
    }
  }

  return (
    <div>
      <div>
        <div className="mb-4 text-base font-semibold">Change Password</div>
      </div>
      <div>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="current_password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Current Password</FormLabel>
                  <FormControl>
                    <Input
                      type="password"
                      placeholder="Enter your current password"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="new_password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>New Password</FormLabel>
                  <FormControl>
                    <Input
                      type="password"
                      placeholder="Enter your new password"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    Password must be at least 8 characters and contain
                    uppercase, lowercase, and numbers.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="confirm_new_password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Confirm New Password</FormLabel>
                  <FormControl>
                    <Input
                      type="password"
                      placeholder="Confirm your new password"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Button type="submit" disabled={isLoading}>
              {isLoading ? "Updating..." : "Update Password"}
            </Button>
          </form>
        </Form>
      </div>
    </div>
  );
}
