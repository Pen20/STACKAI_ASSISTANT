import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// API Definition for Messages

export const listMessages = query({
  handler: async (ctx) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) return [];

    return await ctx.db
      .query("messages")
      .withIndex("by_userId", (q) => q.eq("userId", identity.subject))
      .order("asc")
      .collect();
  },
});

export const saveMessage = mutation({
  args: { role: v.string(), content: v.string() },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");

    await ctx.db.insert("messages", {
      userId: identity.subject,
      role: args.role as "user" | "assistant",
      content: args.content,
      timestamp: Date.now(),
    });
  },
});

export const clearHistory = mutation({
  handler: async (ctx) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");

    const messages = await ctx.db
      .query("messages")
      .withIndex("by_userId", (q) => q.eq("userId", identity.subject))
      .collect();

    for (const msg of messages) {
      await ctx.db.delete(msg._id);
    }
  },
});
