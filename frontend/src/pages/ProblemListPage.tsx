import { useParams } from "react-router-dom";
import { useProblemsQuery } from "../hooks/useProblemsQuery";
import ProblemGrid from "../components/ProblemGrid";
import "./ProblemListPage.css";

export default function ProblemListPage() {
  const { id } = useParams();
  const { data, isLoading, isError, error } = useProblemsQuery(id ?? "");

  const testProblems = [
    {
      id: 1,
      title: "Two Sum",
      difficulty: "Easy",
      category: "string",
      description:
        "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
    },
    {
      id: 2,
      title: "Longest Substring Without Repeating Characters",
      difficulty: "Medium",
      category: "string",
      description:
        "Given a string s, find the length of the longest substring without repeating characters.",
    },
    {
      id: 3,
      title: "Median of Two Sorted Arrays",
      difficulty: "Hard",
      category: "arrays",
      description:
        "Given two sorted arrays nums1 and nums2 of size m and n respectively, return the median of the two sorted arrays.",
    },
  ];
  /* TODO -- create loading spinner */
  return (
    <section className="simple-page">
      <h1>{data?.name ?? "Problem List"}</h1>
      {isLoading && <p className="status-line">Loading problem lists...</p>}
      {isError && (
        <p className="status-line error">
          {(error as Error).message || "Request failed."}
        </p>
      )}
      {!isLoading && !isError && data && testProblems.length > 0 && (
        <ProblemGrid problems={testProblems} />
      )}
      {!isLoading && !isError && data?.problems.length === 0 && (
        <p className="status-line">No problem lists found yet.</p>
      )}
    </section>
  );
}
