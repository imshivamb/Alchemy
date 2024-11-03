export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="max-w-xl w-full space-y-8 p-6">{children}</div>
    </div>
  );
}
