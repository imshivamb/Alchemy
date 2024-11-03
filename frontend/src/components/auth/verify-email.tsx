"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { AuthStore } from "@/stores/auth.store";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { toast } from "sonner";
import { Loader2, CheckCircle2, XCircle } from "lucide-react";

interface VerifyEmailProps {
  token: string;
}

export default function VerifyEmail({ token }: VerifyEmailProps) {
  const [verificationStatus, setVerificationStatus] = useState<
    "loading" | "success" | "error"
  >("loading");
  const router = useRouter();
  const { verifyEmail } = AuthStore();

  useEffect(() => {
    const verifyToken = async () => {
      try {
        await verifyEmail(token);
        setVerificationStatus("success");
        toast.success("Email verified successfully");
      } catch {
        setVerificationStatus("error");
        toast.error("Failed to verify email");
      }
    };

    verifyToken();
  }, [token, verifyEmail]);

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-2xl text-center">
          Email Verification
        </CardTitle>
      </CardHeader>

      <CardContent className="flex flex-col items-center justify-center space-y-4">
        {verificationStatus === "loading" ? (
          <div className="flex flex-col items-center space-y-4">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="text-sm text-muted-foreground">
              Verifying your email...
            </p>
          </div>
        ) : verificationStatus === "success" ? (
          <div className="flex flex-col items-center space-y-4">
            <CheckCircle2 className="h-8 w-8 text-green-500" />
            <p className="text-center">
              Your email has been verified successfully!
            </p>
          </div>
        ) : (
          <div className="flex flex-col items-center space-y-4">
            <XCircle className="h-8 w-8 text-destructive" />
            <p className="text-center">
              Failed to verify your email. The link may be expired or invalid.
            </p>
          </div>
        )}
      </CardContent>

      <CardFooter className="flex justify-center">
        <Button
          variant="link"
          onClick={() => router.push("/login")}
          className="text-sm"
        >
          {verificationStatus === "success"
            ? "Proceed to login"
            : "Back to login"}
        </Button>
      </CardFooter>
    </Card>
  );
}
