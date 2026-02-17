export type Difficulty = "easy" | "medium" | "hard" | string;

export interface Problem {
  id: number;
  title: string;
  description: string;
  difficulty: Difficulty;
  category: string;
}

export interface ProblemList {
  id: number;
  name: string;
  icon_url: string;
}
