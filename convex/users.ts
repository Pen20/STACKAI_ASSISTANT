import { mutation } from "./_generated/server";
import { v } from "convex/values";

export const store = mutation({
  args: {
    clerkId: v.string(),
    email: v.string(),
  },
  handler: async (ctx, args) => {
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerkId", (q) => q.eq("clerkId", args.clerkId))
      .unique();

    if (user) {
      return user._id;
    }

    return await ctx.db.insert("users", {
      clerkId: args.clerkId,
      email: args.email,
    });
  },
});

export const updateUserActivity = mutation({
  args: {
    resource: v.string(),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      console.log("updateUserActivity called without auth - skipping");
      return null;
    }
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerkId", (q) => q.eq("clerkId", identity.subject))
      .unique();

    if (!user) {
      console.error("User not found for activity update");
      return;
    }

    await ctx.db.patch(user._id, {
      lastVisitedResource: args.resource,
    });
  },
});

export const createUser = mutation({
  args: {
    clerkId: v.string(),
    email: v.string(),
    firstName: v.optional(v.string()),
    lastName: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const existingUser = await ctx.db
      .query("users")
      .withIndex("by_clerkId", (q) => q.eq("clerkId", args.clerkId))
      .unique();

    if (existingUser) return existingUser._id;

    return await ctx.db.insert("users", {
      clerkId: args.clerkId,
      email: args.email,
    });
  },
});

export const recordLogin = mutation({
  args: {
    clerkId: v.string(),
    email: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerkId", (q) => q.eq("clerkId", args.clerkId))
      .unique();

    if (user) {
      await ctx.db.patch(user._id, {
        lastLoginAt: Date.now(),
      });
    } else if (args.email) {
      // Fallback: Create user if they don't exist yet (should be covered by user.created, but safe to have)
      await ctx.db.insert("users", {
        clerkId: args.clerkId,
        email: args.email,
        lastLoginAt: Date.now(),
      });
    }
  },
});

export const syncUser = mutation({
  args: {
    clerkId: v.string(),
    email: v.string(),
  },
  handler: async (ctx, args) => {
    // Look for existing user
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerkId", (q) => q.eq("clerkId", args.clerkId))
      .unique();

    if (user) {
      // Update last login timestamp
      await ctx.db.patch(user._id, { lastLoginAt: Date.now() });
      return user._id;
    }

    // New user: Insert into Convex
    return await ctx.db.insert("users", {
      clerkId: args.clerkId,
      email: args.email,
      lastLoginAt: Date.now(),
      // lastVisitedResource is optional in your schema, so it starts undefined
    });
  },
});
