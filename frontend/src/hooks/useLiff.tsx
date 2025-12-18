"use client";

import { createContext, useContext, useEffect, useState } from "react";
import type { Liff } from "@line/liff";

interface LiffContextValue {
  liff: Liff | null;
  isLoggedIn: boolean;
  isReady: boolean;
  error: Error | null;
  profile: any | null;
}

const LiffContext = createContext<LiffContextValue>({
  liff: null,
  isLoggedIn: false,
  isReady: false,
  error: null,
  profile: null,
});

interface LiffProviderProps {
  children: React.ReactNode;
  liffId: string;
  withLoginOnExternalBrowser?: boolean;
}

export function LiffProvider({
  children,
  liffId,
  withLoginOnExternalBrowser = false,
}: LiffProviderProps) {
  const [liff, setLiff] = useState<Liff | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isReady, setIsReady] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [profile, setProfile] = useState<any | null>(null);

  useEffect(() => {
    let isMounted = true;

    const initializeLiff = async () => {
      try {
        const liffModule = (await import("@line/liff")).default;

        await liffModule.init({
          liffId,
          withLoginOnExternalBrowser,
        });

        if (!isMounted) return;

        setLiff(liffModule);
        const loggedIn = liffModule.isLoggedIn();
        setIsLoggedIn(loggedIn);

        // Get user profile if logged in
        if (loggedIn) {
          try {
            const userProfile = await liffModule.getProfile();
            if (isMounted) {
              setProfile(userProfile);
            }
          } catch (err) {
            console.error("Failed to get profile:", err);
          }
        }

        setIsReady(true);
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err : new Error("LIFF initialization failed"));
          setIsReady(true);
        }
      }
    };

    initializeLiff();

    return () => {
      isMounted = false;
    };
  }, [liffId, withLoginOnExternalBrowser]);

  return (
    <LiffContext.Provider value={{ liff, isLoggedIn, isReady, error, profile }}>
      {children}
    </LiffContext.Provider>
  );
}

export function useLiff() {
  const context = useContext(LiffContext);
  if (context === undefined) {
    throw new Error("useLiff must be used within a LiffProvider");
  }
  return context;
}
