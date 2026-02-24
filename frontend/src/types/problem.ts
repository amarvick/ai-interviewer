import type { TestCase } from "./testcase";

export type Difficulty = "easy" | "medium" | "hard" | string;

export interface Problem {
  id: string;
  title: string;
  description: string;
  difficulty: Difficulty;
  category: string;
  starter_code: Record<string, string>;
  test_cases: TestCase[];
}

export interface ProblemList {
  id: string;
  name: string;
  icon_url: string;
}

export interface ProblemListProblemsResponse {
  name: string;
  problems: Problem[];
}
