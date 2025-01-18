import LoginForm from "@/components/auth/login-form";
import { GalleryVerticalEnd } from "lucide-react";
import Image from "next/image";

export default function LoginPage() {
  return (
    <div className="grid min-h-svh h-screen lg:grid-cols-2">
      <div className="flex flex-col gap-4 p-6 md:p-10">
        <div className="flex justify-center gap-2 md:justify-start">
          <a href="#" className="flex items-center gap-2 font-bold">
            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-primary text-primary-foreground">
              <GalleryVerticalEnd className="size-4" />
            </div>
            Alchemy
          </a>
        </div>
        <div className="flex flex-1 items-center justify-center">
          <div className="w-full max-w-xs">
            <LoginForm />
          </div>
        </div>
      </div>
      <div className="relative hidden bg-black flex-col items-center justify-center md:flex">
        <h3 className="text-4xl font-bold text-white">
          Automate your workflow
        </h3>
        <Image
          src="/illustration.png"
          alt="Login"
          width={600}
          height={600}
          className="object-cover"
        />
      </div>
    </div>
  );
}
