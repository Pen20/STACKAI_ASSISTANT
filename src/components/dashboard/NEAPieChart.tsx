"use client";

import { useState } from "react";
import { PieChart, Pie, Sector, ResponsiveContainer, Cell, Legend } from "recharts";

// Modern, distinct color palette for diagnostics
const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

interface NEAPieChartProps {
  data: any[];
  question: string;
}

const renderActiveShape = (props: any) => {
  const { cx, cy, midAngle, innerRadius, outerRadius, startAngle, endAngle, fill, payload, percent, value } = props;
  
  // Split long names for better fit
  const words = payload.name.split(" ");
  const firstLine = words.slice(0, Math.ceil(words.length / 2)).join(" ");
  const secondLine = words.slice(Math.ceil(words.length / 2)).join(" ");

  return (
    <g>
      <text x={cx} y={cy} textAnchor="middle" fill="#334155" className="font-bold text-xs">
        <tspan x={cx} dy={secondLine ? "-0.4em" : "0.3em"}>{firstLine}</tspan>
        {secondLine && <tspan x={cx} dy="1.2em">{secondLine}</tspan>}
      </text>
      <Sector
        cx={cx}
        cy={cy}
        innerRadius={innerRadius}
        outerRadius={outerRadius}
        startAngle={startAngle}
        endAngle={endAngle}
        fill={fill}
      />
      <Sector
        cx={cx}
        cy={cy}
        startAngle={startAngle}
        endAngle={endAngle}
        innerRadius={outerRadius + 4} // Reduced spread to prevent card overflow
        outerRadius={outerRadius + 8}
        fill={fill}
      />
    </g>
  );
};

const RADIAN = Math.PI / 180;

export default function NEAPieChart({ data, question }: NEAPieChartProps) {
  const [activeIndex, setActiveIndex] = useState(0);

  // 1. Filter data
  const questionData = data.filter(d => d.question === question);
  
  // 2. Count Categories (Strict Filtering)
  const counts: Record<string, number> = {};
  let totalEntries = 0;

  // Standard NEA Categories normalization map
  const ALLOWED_CATEGORIES: Record<string, string> = {
    "reading": "Reading Error",
    "comprehension": "Comprehension Error",
    "transformation": "Transformation Error",
    "process": "Process Skill Error",
    "encoding": "Encoding Error",
  };

  questionData.forEach(item => {
    const categories = Array.isArray(item.errorCategory) 
      ? item.errorCategory 
      : (typeof item.errorCategory === 'string' ? item.errorCategory.split(", ") : []);

    categories.forEach((cat: string) => {
      const lowerCat = cat.trim().toLowerCase();
      
      // Strict matching logic
      let match = null;
      for (const key in ALLOWED_CATEGORIES) {
        if (lowerCat.includes(key)) {
            match = ALLOWED_CATEGORIES[key];
            break;
        }
      }

      if (match) {
        counts[match] = (counts[match] || 0) + 1;
        totalEntries++;
      }
    });
  });

  // 3. Transform for Chart
  const chartData = Object.keys(counts)
    .map(name => ({
      name,
      value: counts[name],
      percentage: ((counts[name] / totalEntries) * 100).toFixed(1)
    }))
    .sort((a, b) => b.value - a.value);

  /* 
     Removed "Top 4 + Others" logic to strictly show only the requested NEA categories 
     as per user requirement.
  */

  const onPieEnter = (_: any, index: number) => {
    setActiveIndex(index);
  };

  if (totalEntries === 0) {
    return (
      <div className="h-[350px] w-full flex items-center justify-center text-slate-400">
        <p>No error attributes found for this selection.</p>
      </div>
    );
  }

  return (
    <div className="h-[350px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            activeIndex={activeIndex}
            activeShape={renderActiveShape}
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={55} // Slightly smaller
            outerRadius={75} // Slightly smaller to prevent clipping
            fill="#8884d8"
            dataKey="value"
            onMouseEnter={onPieEnter}
            paddingAngle={2}
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} stroke="none" />
            ))}
          </Pie>
          <Legend 
            verticalAlign="bottom" 
            height={36} 
            formatter={(value, entry: any) => (
              <span className="text-slate-600 text-sm font-medium ml-1">
                 {value} ({chartData.find(d => d.name === value)?.percentage}%)
              </span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}