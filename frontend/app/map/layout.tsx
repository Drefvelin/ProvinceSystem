export default function MapLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div
      className="w-full overflow-auto"
      style={{ minHeight: "calc(100dvh - var(--tfmc-header-h))" }}
    >
      {children}
    </div>
  );
}
