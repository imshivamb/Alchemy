import type { Metadata } from "next";
import localFont from "next/font/local";
import { Sora } from "next/font/google";
import "./globals.css";
import { Toaster } from "sonner";
import { cn } from "@/lib/utils";
import InitAuthCheck from "@/components/auth/initial-auth-check";
import { TooltipProvider } from "@/components/ui/tooltip";
import { SidebarProvider } from "@/components/ui/sidebar";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});

const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

const sora = Sora({
  variable: "--font-sora",
  weight: ["300", "400", "500", "600", "700"],
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Alchemy",
  description: "AI Automation Platform",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={cn(
          "min-h-screen bg-background antialiased",
          sora.className,
          geistSans.variable,
          geistMono.variable
        )}
        suppressHydrationWarning
      >
        <InitAuthCheck>
          <TooltipProvider>
            <SidebarProvider>{children}</SidebarProvider>
          </TooltipProvider>
        </InitAuthCheck>
        <Toaster position="top-center" expand={true} richColors closeButton />
      </body>
    </html>
  );
}
