import React from "react";
import { Button } from "../ui/button";
import { GitHubLogoIcon } from "@radix-ui/react-icons";
import { Mail } from "lucide-react";

const SocialLogin = () => {
  const handleAuth = (provider: "google" | "github") => {
    const urls = {
      google: `https://accounts.google.com/o/oauth2/v2/auth?client_id=${process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID}&redirect_uri=${process.env.NEXT_PUBLIC_GOOGLE_CALLBACK_URL}&response_type=code&scope=email profile`,
      github: `https://github.com/login/oauth/authorize?client_id=${process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID}&redirect_uri=${process.env.NEXT_PUBLIC_GITHUB_CALLBACK_URL}&scope=user:email`,
    };

    window.location.href = urls[provider];
  };
  return (
    <div className="flex gap-2 flex-col w-full">
      <Button className="w-full" onClick={() => handleAuth("google")}>
        <Mail className="size-4 mr-2" />
        Sign in With Google
      </Button>
      <Button
        className="w-full"
        variant={"outline"}
        onClick={() => handleAuth("github")}
      >
        <GitHubLogoIcon className="size-4 mr-2" />
        Sign in With Github
      </Button>
    </div>
  );
};

export default SocialLogin;
