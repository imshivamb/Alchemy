import { redirect } from "next/navigation";
import ResetPasswordForm from "@/components/auth/reset-password-form";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface ResetPasswordPageProps {
  searchParams: { [key: string]: string | string[] | undefined };
}

export default async function ResetPasswordPage({
  searchParams,
}: ResetPasswordPageProps) {
  // Safely access search params and ensure they're strings
  const uid =
    typeof searchParams.uid === "string" ? searchParams.uid : undefined;
  const token =
    typeof searchParams.token === "string" ? searchParams.token : undefined;

  // Redirect if params are missing
  if (!uid || !token) {
    redirect("/auth/login");
  }

  return (
    <div className="container flex h-[100vh] w-full items-center justify-center">
      <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl text-center">
              Reset Password
            </CardTitle>
            <CardDescription className="text-center">
              Enter your new password below
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResetPasswordForm uid={uid} token={token} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
