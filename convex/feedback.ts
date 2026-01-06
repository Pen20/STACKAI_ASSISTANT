import { mutation, internalAction } from "./_generated/server";
import { v } from "convex/values";
import { internal } from "./_generated/api";
import { Resend } from "resend";

export const submitFeedback = mutation({
  args: {
    name: v.optional(v.string()),
    email: v.optional(v.string()),
    message: v.string(),
    type: v.string(),
  },
  handler: async (ctx, args) => {
    // 1. Store in Database
    await ctx.db.insert("feedback", {
      name: args.name,
      email: args.email,
      message: args.message,
      type: args.type,
      createdAt: Date.now(),
    });

    // 2. Schedule Email Notification
    await ctx.scheduler.runAfter(0, internal.feedback.sendFeedbackEmail, {
        name: args.name || "Anonymous",
        email: args.email || "No email provided",
        message: args.message,
        type: args.type,
    });
  },
});

export const sendFeedbackEmail = internalAction({
    args: {
        name: v.string(),
        email: v.string(),
        message: v.string(),
        type: v.string(),
    },
    handler: async (ctx, args) => {
        const resend = new Resend(process.env.RESEND_API_KEY);
        
        // Change 'to' to your verified email or a configured admin email
        // For Resend testing, you can only send to the email you signed up with (unless domain is verified)
        await resend.emails.send({
            from: "STACKAI Feedback <onboarding@resend.dev>",
            to: process.env.ADMIN_EMAIL || "your-email@example.com", // Fallback, User needs to set this
            subject: `New ${args.type} from ${args.name}`,
            html: `
                <h1>New Feedback Received</h1>
                <p><strong>Type:</strong> ${args.type}</p>
                <p><strong>From:</strong> ${args.name} (${args.email})</p>
                <hr />
                <p>${args.message}</p>
            `
        });
    }
});
