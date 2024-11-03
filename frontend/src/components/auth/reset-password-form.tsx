"use client";

import { AuthStore } from "@/stores/auth.store";
import {
  ResetPasswordValues,
  resetPasswordSchema,
} from "@/schemas/auth-schema";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Alert, AlertDescription } from "../ui/alert";
import {
  Form,
  FormField,
  FormLabel,
  FormItem,
  FormControl,
  FormMessage,
} from "../ui/form";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

interface ResetPasswordFormProps {
  uid: string;
  token: string;
}

const ResetPasswordForm = ({ uid, token }: ResetPasswordFormProps) => {
  const [serverError, setServerError] = useState<string | null>(null);
  const { isLoading, resetPasswordConfirm } = AuthStore();
  const router = useRouter();

  const form = useForm<ResetPasswordValues>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: {
      password: "",
      confirm_password: "",
    },
    mode: "onBlur",
  });

  const onSubmit = async (data: ResetPasswordValues) => {
    if (form.formState.isSubmitting) return;

    try {
      setServerError(null);
      // Combine uid and token as required by the backend
      const resetToken = `${uid}-${token}`;

      await resetPasswordConfirm({
        token: resetToken,
        password: data.password,
        confirm_password: data.confirm_password,
      });

      toast.success("Password reset successful", {
        description: "You can now log in with your new password.",
      });

      // Redirect to login page with success message
      router.push("/login?reset=success");
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Password reset failed. Please try again or request a new reset link.";

      setServerError(errorMessage);

      toast.error("Password reset failed", {
        description: errorMessage,
      });
    }
  };

  return (
    <div className="space-y-6">
      {serverError && (
        <Alert variant="destructive">
          <AlertDescription>{serverError}</AlertDescription>
        </Alert>
      )}

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem>
                <FormLabel>New Password</FormLabel>
                <FormControl>
                  <Input
                    type="password"
                    placeholder="Enter your new password"
                    disabled={isLoading}
                    autoComplete="new-password"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="confirm_password"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Confirm New Password</FormLabel>
                <FormControl>
                  <Input
                    type="password"
                    placeholder="Confirm your new password"
                    disabled={isLoading}
                    autoComplete="new-password"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <Button
            type="submit"
            className="w-full"
            disabled={isLoading || !form.formState.isValid}
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Resetting Password...
              </>
            ) : (
              "Reset Password"
            )}
          </Button>
        </form>
      </Form>
    </div>
  );
};

export default ResetPasswordForm;
