"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { LiffProvider } from "@liff/use-liff";
import { useState } from "react";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  const liffId = process.env.NEXT_PUBLIC_LIFF_ID!;

  return (
    <LiffProvider liffId={liffId} withLoginOnExternalBrowser>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </LiffProvider>
  );
}
