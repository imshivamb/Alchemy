"use client";

import { LoginFormValues, loginSchema } from "@/schemas/auth-schema";
import { AuthStore } from "@/stores/auth.store";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
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
import Link from "next/link";
import SocialLogin from "./social-login";

const LoginForm = () => {
  const [serverError, setServerError] = useState<string | null>(null);
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login, isLoading } = AuthStore();

  // useEffect(() => {
  //   if (searchParams?.get("registered") === "true") {
  //     toast("Registration successful", {
  //       description: "Please login with your credentials",
  //     });
  //   }
  // }, [searchParams]);

  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
    mode: "onBlur",
  });

  async function onSubmit(data: LoginFormValues) {
    if (form.formState.isSubmitting) return;
    try {
      setServerError(null);
      await login(data);

      // After successful login, redirect properly
      const callbackUrl = searchParams?.get("callbackUrl");
      if (callbackUrl) {
        // Ensure it's a relative URL for security
        const path = callbackUrl.startsWith("/") ? callbackUrl : "/dashboard";
        router.replace(path);
      } else {
        router.replace("/dashboard");
      }
    } catch {
      setServerError("Invalid email or password");
    }
  }

  return (
    <div className="space-y-6">
      {serverError && (
        <Alert variant={"destructive"}>
          <AlertDescription>{serverError}</AlertDescription>
        </Alert>
      )}

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Email</FormLabel>
                <FormControl>
                  <Input placeholder="Enter your Email" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Password</FormLabel>
                <FormControl>
                  <Input
                    type="password"
                    placeholder="Enter your password"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <div className="flex items-center justify-end">
            <Button variant="link" asChild className="px-0">
              <Link href="/forgot-password">Forgot password?</Link>
            </Button>
          </div>

          <div className="flex justify-center items-center">
            <Button type="submit" disabled={isLoading} className="w-full">
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                "Sign in"
              )}
            </Button>
          </div>
        </form>
      </Form>
      <SocialLogin />
    </div>
  );
};

export default LoginForm;
