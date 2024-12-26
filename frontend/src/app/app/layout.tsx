import { AppSidebar } from "./_components/app-sidebar";
import { SidebarInset } from "@/components/ui/sidebar";
import { Header } from "./_components/header";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <AppSidebar />
      <SidebarInset>
        <Header />
        <main className="flex flex-1 flex-col gap-4 p-4 pt-0">{children}</main>
      </SidebarInset>
    </>
  );
}
