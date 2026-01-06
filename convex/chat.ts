"use node";

import { action } from "./_generated/server";
import { v } from "convex/values";
import OpenAI from "openai";
import { api } from "./_generated/api";

/**
 * System prompt
 */
const SYSTEM_PROMPT = `
You are an expert educational diagnostic assistant using Newman’s Error Analysis.

Rules:
- Use ONLY the provided student data.
- If no record is found, say so clearly.
- Do NOT ask the user for data that already exists.
- Always begin by restating the student's answer and the correct answer using backticks.
- Be concise, diagnostic, and pedagogically helpful.
`;

/**
 * Shape of a studentErrors row (important for TS)
 */
type StudentErrorRow = {
  studentId: string;
  question: string;
  response: string;
  rightAnswer: string;
  grade: number;
  errorCategory: string[];
  errorSummary: string;
};

/**
 * Main AI action
 */
export const askAi = action({
  args: {
    prompt: v.string(),
    history: v.array(
      v.object({
        role: v.union(v.literal("user"), v.literal("assistant")),
        content: v.string(),
      })
    ),
  },

  /**
   * IMPORTANT: Explicit return type
   */
  handler: async (
    ctx,
    args
  ): Promise<string> => {
    // 1️⃣ Parse student ID and question number
    const studentMatch = args.prompt.match(/student\s*(\d+)/i);
    const questionMatch = args.prompt.match(/question\s*(\d+)/i);

    if (!studentMatch || !questionMatch) {
      return "Please specify both a student number and a question number (e.g., 'Student 1 question 4').";
    }

    const studentId = studentMatch[1];
    const question = questionMatch[1];

    // 2️⃣ Fetch student data from Convex
    const rows = await ctx.runQuery(
      api.studentErrors.getByStudentAndQuestion,
      { studentId, question }
    ) as StudentErrorRow[];

    if (rows.length === 0) {
      return `No record found for Student ${studentId} on Question ${question}.`;
    }

    // 3️⃣ Build context string (typed map)
    const context: string = rows
      .map((r: StudentErrorRow) => `
Student ID: ${r.studentId}
Question: ${r.question}
Student Answer: ${r.response}
Correct Answer: ${r.rightAnswer}
Grade: ${r.grade}
Error Category: ${r.errorCategory.join(", ")}
Error Summary: ${r.errorSummary}
`)
      .join("\n");

    // 4️⃣ OpenAI call
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) {
      throw new Error("OPENAI_API_KEY is not set");
    }

    const openai = new OpenAI({ apiKey });

    const completion = await openai.chat.completions.create({
      model: "gpt-4o",
      temperature: 0.2,
      messages: [
        { role: "system", content: SYSTEM_PROMPT },
        { role: "system", content: `Student data:\n${context}` },
        ...args.history.slice(-6),
        { role: "user", content: args.prompt },
      ],
    });

    return completion.choices[0]?.message?.content ?? "";
  },
});
