import fs from "fs";
import csv from "csv-parser";
import { ConvexHttpClient } from "convex/browser";
import { api } from "../convex/_generated/api.js";
import * as dotenv from "dotenv";

dotenv.config({ path: ".env.local" });

const client = new ConvexHttpClient(process.env.NEXT_PUBLIC_CONVEX_URL!);

const results: any[] = [];

fs.createReadStream("data/predicting_students_errors.csv")
  .pipe(csv())
  .on("data", (data) => results.push(data))
  .on("end", async () => {
    console.log(`Parsed ${results.length} rows.`);

    const formattedErrors = results.map((row: any) => ({
      studentId: row.student_id ? row.student_id.toString() : "",
      question: row.question || "",
      seedId: row.seed_id ? row.seed_id.toString() : "",
      response: row.response || "",
      rightAnswer: row.right_answer || "",
      grade: parseFloat(row.grade) || 0,
      errorCategory: row.error_category
        ? row.error_category.split(",").map((c: string) => c.trim())
        : [],
      errorSummary: row.error_summary || "",
      llmResponse: row.llm_response || "",
      createdBy: "system",
      firstName: row.first_name || row.firstname || "", 
      surname: row.surname || row.last_name || row.lastname || "",
      email: row.email || "",
    }));

    // Batch upload to avoid hitting limits if necessary, but for now try all
    // Convex might complain if too large. Better to chunk.
    const CHUNK_SIZE = 100;
    for (let i = 0; i < formattedErrors.length; i += CHUNK_SIZE) {
        const chunk = formattedErrors.slice(i, i + CHUNK_SIZE);
        console.log(`Seeding chunk ${i / CHUNK_SIZE + 1}...`);
        try {
            await client.mutation(api.studentErrors.seedStudentErrors, { errors: chunk });
        } catch (error) {
            console.error("Error seeding chunk:", error);
        }
    }
    console.log("Seeding complete.");
  });
