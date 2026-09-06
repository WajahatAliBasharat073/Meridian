import Link from "next/link";
import { Logo } from "@/components/brand/Logo";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4 text-center">
      <Logo className="mb-8" />
      <p className="text-xs font-medium uppercase tracking-wide text-text-faint mb-2">404</p>
      <h1 className="text-2xl font-semibold text-text mb-2">Page not found</h1>
      <p className="text-sm text-text-muted mb-6 max-w-sm">
        That page doesn&apos;t exist. Head back to your dashboard.
      </p>
      <Link href="/today">
        <Button variant="primary" size="lg">
          Go to Today
        </Button>
      </Link>
    </main>
  );
}
