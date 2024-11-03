"use client";

import { useEffect } from "react";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { XCircle } from "lucide-react";
import { useRouter } from "next/navigation";

export default function ResetPasswordError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const router = useRouter();

  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="container flex h-[100vh] w-full items-center justify-center">
      <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
        <Card>
          <CardHeader>
            <CardTitle className="flex flex-col items-center gap-2">
              <XCircle className="h-8 w-8 text-destructive" />
              <span>Error</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="text-center">
            <p className="text-sm text-muted-foreground">
              {error.message ||
                "Something went wrong while resetting your password."}
            </p>
          </CardContent>
          <CardFooter className="flex justify-center gap-2">
            <Button
              variant="outline"
              onClick={() => router.push("/auth/login")}
            >
              Back to login
            </Button>
            <Button onClick={() => reset()}>Try again</Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}
