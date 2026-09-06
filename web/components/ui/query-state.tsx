import Link from "next/link";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { ApiError } from "@/lib/api";

export function QueryError({
  error,
  onRetry,
  fallback = "Something went wrong.",
}: {
  error: unknown;
  onRetry?: () => void;
  fallback?: string;
}) {
  const isAuthError = error instanceof ApiError && error.status === 401;
  const isNetwork = error instanceof ApiError && error.status === 0;
  const message = isAuthError
    ? "Your session expired."
    : isNetwork
      ? "Couldn’t reach the server — check your connection."
      : fallback;

  return (
    <div className="space-y-3">
      <Alert variant="error">{message}</Alert>
      {isAuthError ? (
        <Link href="/login">
          <Button variant="primary" size="md">
            Sign in again
          </Button>
        </Link>
      ) : onRetry ? (
        <Button variant="secondary" size="md" onClick={onRetry}>
          Retry
        </Button>
      ) : null}
    </div>
  );
}
