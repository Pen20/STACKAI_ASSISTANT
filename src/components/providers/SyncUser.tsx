"use client";

import { useUser } from "@clerk/nextjs";
import { useMutation } from "convex/react";
import { api } from "../../../convex/_generated/api";
import { useEffect } from "react";

export default function SyncUser() {
  const { isLoaded, isSignedIn, user } = useUser();
  const sync = useMutation(api.users.syncUser);

  useEffect(() => {
    if (isLoaded && isSignedIn && user) {
      sync({
        clerkId: user.id,
        email: user.emailAddresses[0].emailAddress,
      })
      .then(() => console.log("✅ User synced to Convex"))
      .catch((err) => console.error("❌ Sync failed:", err));
    }
  }, [isLoaded, isSignedIn, user, sync]);

  return null; // This component doesn't render anything UI-wise
}
