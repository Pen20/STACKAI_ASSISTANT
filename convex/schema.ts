import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  users: defineTable({
    clerkId: v.string(),
    email: v.string(),
    lastVisitedResource: v.optional(v.string()), // e.g., "dashboard" or "chatbot"
    lastLoginAt: v.optional(v.number()),
  }).index("by_clerkId", ["clerkId"]),

  studentErrors: defineTable({
    studentId: v.string(),
    question: v.string(),
    seedId: v.string(),      // Added: To track the specific randomized variant
    response: v.string(),
    rightAnswer: v.string(),
    grade: v.float64(),
    errorCategory: v.array(v.string()), // Migrated from CSV error_category 
    errorSummary: v.string(),
    llmResponse: v.string(), // Added: The AI's original analysis from the CSV
    createdBy: v.string(), // "system" for default data, or the User's Clerk ID
    // Generalization fields for non-anonymized data
    firstName: v.optional(v.string()),
    surname: v.optional(v.string()),
    email: v.optional(v.string()),
  }),

  messages: defineTable({
    userId: v.string(), // Clerk ID
    role: v.union(v.literal("user"), v.literal("assistant")),
    content: v.string(),
    timestamp: v.number(),
  }).index("by_userId", ["userId"]),

  feedback: defineTable({
    name: v.optional(v.string()),
    email: v.optional(v.string()),
    message: v.string(),
    type: v.string(), // "contact" or "feedback"
    createdAt: v.number(),
  }),
});
