"use client";

import { useEffect } from "react";
import { useLiff } from "@/hooks/useLiff";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";

export default function Home() {
  const { liff, isLoggedIn, isReady, error } = useLiff();
  const router = useRouter();

  useEffect(() => {
    if (!isReady) return;

    if (!isLoggedIn) {
      liff?.login();
      return;
    }

    // Redirect to files page after login
    router.push("/files");
  }, [isReady, isLoggedIn, liff, router]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-2">Error</h1>
          <p className="text-gray-600">{error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-primary" />
        <p className="text-gray-600">กำลังโหลด...</p>
      </div>
    </div>
  );
}
