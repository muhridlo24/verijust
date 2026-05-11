"use client";

import { ReactNode, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getToken } from "@/lib/token";

/**
 * Higher-order component to protect routes from unauthorized access
 * Checks for token and redirects to /login if not authenticated
 */
export function ProtectRoute({ children }: { children: ReactNode }) {
  const router = useRouter();

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.replace("/login");
    }
  }, [router]);

  return <>{children}</>;
}
