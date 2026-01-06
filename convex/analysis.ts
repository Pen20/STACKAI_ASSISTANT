import { query } from "./_generated/server";
import { v } from "convex/values";

export const getAtRiskStudents = query({
  handler: async (ctx) => {
    const errors = await ctx.db.query("studentErrors").collect();

    // Group errors by studentId
    const studentPerformance = new Map<string, { totalGrade: number; count: number; errors: any[] }>();

    for (const error of errors) {
      if (!studentPerformance.has(error.studentId)) {
        studentPerformance.set(error.studentId, { totalGrade: 0, count: 0, errors: [] });
      }
      const data = studentPerformance.get(error.studentId)!;
      data.totalGrade += error.grade;
      data.count += 1;
      data.errors.push(error);
    }

    // Identify at-risk students (e.g., average grade below 0.5)
    // Using Student ID as requested (e.g., "Student #204")
    const atRiskStudents = [];
    for (const [studentId, data] of studentPerformance.entries()) {
      const average = data.totalGrade / data.count;
      if (average < 0.5) {
        atRiskStudents.push({
          identifier: `Student #${studentId}`, // Anonymized ID
          averageGrade: average.toFixed(2),
          errorCount: data.count,
          topics: [...new Set(data.errors.flatMap(e => e.errorCategory))],
        });
      }
    }

    return atRiskStudents.sort((a, b) => parseFloat(a.averageGrade) - parseFloat(b.averageGrade));
  },
});

export const getQuestionIndices = query({
  handler: async (ctx) => {
    const records = await ctx.db.query("studentErrors").collect();
    if (records.length === 0) return [];

    // 1. Group by student to get total performance
    const studentPerformance: Record<string, { total: number; count: number }> = {};
    records.forEach((r) => {
      if (!studentPerformance[r.studentId]) studentPerformance[r.studentId] = { total: 0, count: 0 };
      studentPerformance[r.studentId].total += r.grade;
      studentPerformance[r.studentId].count += 1;
    });

    // 2. Rank students and get Top/Bottom 27% (Anonymized IDs)
    const sortedStudents = Object.entries(studentPerformance)
      .map(([id, stats]) => ({ id, avg: stats.total / stats.count }))
      .sort((a, b) => b.avg - a.avg);

    const n = sortedStudents.length;
    const boundary = Math.max(1, Math.floor(n * 0.27));
    const topGroupIds = new Set(sortedStudents.slice(0, boundary).map((s) => s.id));
    const bottomGroupIds = new Set(sortedStudents.slice(-boundary).map((s) => s.id));

    // 3. Calculate indices per question
    const questions = Array.from(new Set(records.map((r) => r.question)));
    
    return questions.map((q) => {
      const qRecords = records.filter((r) => r.question === q);
      
      // Difficulty Index (DI): Mean of all grades for this question
      const di = qRecords.reduce((acc, r) => acc + r.grade, 0) / qRecords.length;

      // Discrimination Index (DiscI): Mean(Top) - Mean(Bottom)
      const topGrades = qRecords.filter((r) => topGroupIds.has(r.studentId));
      const bottomGrades = qRecords.filter((r) => bottomGroupIds.has(r.studentId));
      
      const meanTop = topGrades.length > 0 
        ? topGrades.reduce((acc, r) => acc + r.grade, 0) / topGrades.length 
        : 0;
      const meanBottom = bottomGrades.length > 0 
        ? bottomGrades.reduce((acc, r) => acc + r.grade, 0) / bottomGrades.length 
        : 0;

      return {
        question: q,
        difficulty: parseFloat(di.toFixed(2)),
        discrimination: parseFloat((meanTop - meanBottom).toFixed(2)),
      };
    });
  },
});
