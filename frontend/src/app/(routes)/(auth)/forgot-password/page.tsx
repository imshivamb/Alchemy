import ForgetPasswordForm from "@/components/auth/forget-password-form";
import React from "react";

const ForgetPasswordPage = () => {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-full max-w-md space-y-8 p-6">
        <div className="text-center">
          <h2 className="text-3xl font-bold">Forgot Password</h2>
          <p className="mt-2 text-gray-600">
            Enter your email and we&apos;ll send you a reset link
          </p>
        </div>
        <ForgetPasswordForm />
      </div>
    </div>
  );
};

export default ForgetPasswordPage;
