// app/auth/[provider]/callback/page.tsx
"use client";

import { useSearchParams, useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { AuthStore } from "@/stores/auth.store";
import { AuthService } from "@/services/auth-service";

export default function AuthCallback() {
  const params = useParams();
  const searchParams = useSearchParams();
  const code = searchParams.get("code");
  const provider = params.provider as string;
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (code && provider) {
      AuthService.socialAuth(code)
        .then((response) => {
          AuthStore.setState({
            user: response.user,
            isAuthenticated: true,
          });
          setTimeout(() => (window.location.href = "/dashboard"), 5000);
        })
        .catch((err) => {
          setError(err.message);
          setTimeout(
            () => (window.location.href = "/login?error=social-auth-failed"),
            5000
          );
        });
    }
  }, [code, provider]);

  if (error) {
    return (
      <div className="flex flex-col gap-4 justify-center items-center min-h-screen">
        <div className="text-red-500">Error: {error}</div>
        <div>Redirecting to login...</div>
      </div>
    );
  }

  return (
    <div className="flex justify-center items-center min-h-screen">
      <div className="animate-pulse">Authenticating...</div>
    </div>
  );
}
