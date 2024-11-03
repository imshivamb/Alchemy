"use client";

import {
  forgetPasswordSchema,
  ForgetPasswordValues,
} from "@/schemas/auth-schema";
import { AuthStore } from "@/stores/auth.store";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import {
  Form,
  FormField,
  FormLabel,
  FormItem,
  FormControl,
  FormMessage,
} from "../ui/form";

import { toast } from "sonner";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Loader2 } from "lucide-react";
import { useState } from "react";

const ForgetPasswordForm = () => {
  const { isLoading, requestPasswordReset } = AuthStore();
  const [submitted, setSubmitted] = useState(false);

  const form = useForm<ForgetPasswordValues>({
    resolver: zodResolver(forgetPasswordSchema),
    defaultValues: {
      email: "",
    },
  });

  const onSubmit = async (data: ForgetPasswordValues) => {
    if (submitted) return;
    try {
      setSubmitted(true);
      await requestPasswordReset(data.email);
      toast("Check your email", {
        description:
          "If an account exists with this email, you will receive a password reset link.",
      });
      form.reset();
    } catch {
      toast("Check your email", {
        description:
          "If an account exists with this email, you will receive a password reset link.",
      });
    } finally {
      setSubmitted(false);
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem className="mb-3">
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input
                  type="email"
                  placeholder="Enter your email"
                  {...field}
                  disabled={isLoading || submitted}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" disabled={isLoading} className="w-full">
          {isLoading || submitted ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Sending Reset Link...
            </>
          ) : (
            "Send Reset Link"
          )}
        </Button>
        <div className="text-center">
          <Button
            variant="link"
            className="text-sm"
            onClick={() => window.history.back()}
            disabled={isLoading || submitted}
          >
            Back to login
          </Button>
        </div>
      </form>
    </Form>
  );
};

export default ForgetPasswordForm;
