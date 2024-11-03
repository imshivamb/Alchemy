"use client";

import { AuthStore } from "@/stores/auth.store";
import React, { useEffect } from "react";
import { LoadingSpinner } from "../ui/loading-spinner";

type Props = {
  children: React.ReactNode;
};

const InitAuthCheck = ({ children }: Props) => {
  const { initAuth, isInitialized } = AuthStore();

  useEffect(() => {
    initAuth();
  }, [initAuth]);

  if (!isInitialized) {
    return (
      <div className="h-screen w-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return <>{children}</>;
};

export default InitAuthCheck;
