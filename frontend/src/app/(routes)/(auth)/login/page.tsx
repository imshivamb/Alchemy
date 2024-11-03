import LoginForm from "@/components/auth/login-form";
import React from "react";

const LoginPage = () => {
  return (
    <div className=" bg-gray-50 py-12 px-4 w-full sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight text-gray-900">
            Welcome Back!{" "}
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Please sign in to your account
          </p>
        </div>
        <LoginForm />
      </div>
    </div>
  );
};

export default LoginPage;
