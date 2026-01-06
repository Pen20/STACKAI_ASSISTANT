"use client";
import React from "react";
import { useMutation } from "convex/react";
import { api } from "../../../convex/_generated/api";
import Papa from "papaparse";
import { Button } from "@/components/ui/button";
import { FileUp, Loader2 } from "lucide-react";

export function CSVUploader() {
  const insertError = useMutation(api.studentErrors.seedStudentErrors);
  const [isUploading, setIsUploading] = React.useState(false);

  const handleUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: async (results) => {
        const formatted = results.data.map((row: any) => ({
          studentId: String(row.student_id),
          question: row.question,
          seedId: String(row.seed_id || ""),
          response: row.response,
          rightAnswer: row.right_answer,
          grade: parseFloat(row.grade) || 0,
          errorCategory: row.error_category ? row.error_category.split(", ") : [],
          errorSummary: row.error_summary || "",
          llmResponse: row.llm_response || "",
          // "createdBy" will be handled by the mutation using the user's ID
          firstName: row.first_name || row.firstname || "",
          surname: row.surname || row.last_name || row.lastname || "",
          email: row.email || "",
        }));

        try {
            // Send to Convex in chunks
            await insertError({ errors: formatted });
            alert("Dataset uploaded and saved to cloud!");
        } catch (error) {
            console.error(error);
            alert("Upload failed. See console.");
        } finally {
            setIsUploading(false);
        }
      }
    });
  };

  return (
    <div className="relative">
      <input 
        type="file" 
        accept=".csv" 
        onChange={handleUpload} 
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        disabled={isUploading}
      />
      <Button variant="outline" className="gap-2" disabled={isUploading}>
        {isUploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileUp className="h-4 w-4" />} 
        {isUploading ? "Uploading..." : "Upload Dataset"}
      </Button>
    </div>
  );
}
