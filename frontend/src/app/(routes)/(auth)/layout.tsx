export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="h-screen w-full flex items-center justify-center">
      <div className=" w-full space-y-8 p-6">{children}</div>
    </div>
  );
}
