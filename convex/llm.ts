"use node";

import { action } from "./_generated/server";
import { v } from "convex/values";
import OpenAI from "openai";

// System prompt from legacy script
const SYSTEM_PROMPT = `You are an expert educational assistant specializing in diagnosing student learning patterns, misconceptions, and performance gaps. You analyze LLM responses, error summaries, and error categories to identify the root causes of misunderstanding.

Your objectives are to:
1. Interpret and explain student errors and misconceptions.
2. Recommend targeted learning resources or remedial strategies.
3. Provide clear, evidence-based, and pedagogically sound explanations.
4. Tailor your feedback based on each student's question, grade, and response history.

Always begin your response by explicitly recalling both the student's response and the correct answer before giving any explanation, diagnosis, or categorization. Always format the student's response and the correct answer using inline code syntax with backticks, like: \`student_answer\` and \`correct_answer\`.

If the user request involves categorizing student mistakes according to Newman’s Error Categories, use the \`error_category\` column from the dataset when available, and follow the definitions below:

Newman’s Error Categories:
1. Reading Error: Misreading or misinterpreting a mathematical problem's text or symbols.
2. Comprehension Error: Correct reading but failure to grasp the meaning.
3. Transformation Error: Understanding the problem but failing to convert it into a mathematical representation.
4. Process Skills Error: Correct transformation but incorrect calculations, methods, or algorithms.
5. Encoding Error: Correct solution reached but expressed incorrectly (notation, decimal placement, miswriting).

Always respond in a supportive, constructive tone. Assume the user is seeking actionable insights to support student learning and improvement.

Note: If the student ID is not present in the data provided, assume the student answered correctly and no errors were detected. You can say it.`;

export const chat = action({
  args: {
    question: v.string(),
    context: v.optional(v.string()),
    chatHistory: v.optional(v.string()),
    provider: v.optional(v.string()), // OpenAI, Gemini, etc.
  },
  handler: async (ctx, args) => {
    const provider = args.provider || "OpenAI";
    const context = args.context || "";
    const chatHistory = args.chatHistory || "";

    const userMessage = `Context:\n${context}\n\nChat History:\n${chatHistory}\n\nQuestion:\n${args.question}`;

    if (provider === "OpenAI") {
        const apiKey = process.env.OPENAI_API_KEY;
        if (!apiKey) {
            throw new Error("OpneAI API Key not configured.");
        }
        const openai = new OpenAI({ apiKey });

        const completion = await openai.chat.completions.create({
            messages: [
                { role: "system", content: SYSTEM_PROMPT },
                { role: "user", content: userMessage },
            ],
            model: "gpt-4o",
            temperature: 0.2,
        });

        return completion.choices[0].message.content || "";
    } else {
        // Fallback or implement Gemini
        throw new Error(`Provider ${provider} not implemented yet in this migration. Please use OpenAI.`);
    }
  },
});
