import { useEffect, useMemo, useState } from "react";
import type { Problem } from "../types/problem";
import "./ProblemPageEditor.css";
import ProblemPageTerminal from "./ProblemPageTerminal";
import ProblemPageCodeEditor from "./ProblemPageCodeEditor";
import ProblemPageEditorToolbar from "./ProblemPageEditorToolbar";
import type { SubmissionResponse } from "../types/submission";
import { getSubmissions, runSubmission } from "../services/api";

interface ProblemPageEditorProps {
  problem: Problem;
}

type TestCaseStatus = "pending" | "pass" | "fail";

export default function ProblemPageEditor({ problem }: ProblemPageEditorProps) {
  const starterCode = problem?.starter_code;
  const languageOptions = useMemo(() => {
    const keys = Object.keys(starterCode);
    return keys.length > 0 ? keys : ["javascript"];
  }, [starterCode]);

  const [selectedLanguage, setSelectedLanguage] = useState(
    languageOptions[0] ?? "javascript"
  );
  const [code, setCode] = useState(starterCode[selectedLanguage] ?? "");
  const [submissions, setSubmissions] = useState<SubmissionResponse[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [hasSubmittedInSession, setHasSubmittedInSession] = useState(false);
  const [sessionErrors, setSessionErrors] = useState<string[]>([]);
  const [testCaseStatuses, setTestCaseStatuses] = useState<
    Record<number, TestCaseStatus>
  >({});

  useEffect(() => {
    const nextStatuses = problem.test_cases.reduce<
      Record<number, TestCaseStatus>
    >((acc, testCase) => {
      acc[testCase.id] = "pending";
      return acc;
    }, {});
    setTestCaseStatuses(nextStatuses);
    setHasSubmittedInSession(false);
    setSessionErrors([]);
  }, [problem.test_cases]);

  useEffect(() => {
    const loadSubmissions = async () => {
      try {
        const records = await getSubmissions(problem.id);
        setSubmissions(records);
      } catch (error) {
        setSessionErrors([
          error instanceof Error
            ? error.message
            : "Failed to load submissions.",
        ]);
      }
    };

    void loadSubmissions();
  }, [problem.id]);

  const handleLanguageChange = (nextLanguage: string) => {
    setSelectedLanguage(nextLanguage);
    setCode(starterCode[nextLanguage] ?? "");
  };

  const updateCode = (value: string | undefined) => {
    setCode(value ?? "");
  };

  const handleRun = () => {
    // Reserved for future local/sample run support.
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setHasSubmittedInSession(true);
    setSessionErrors([]);

    try {
      const response = await runSubmission({
        problem_id: problem.id,
        code_submitted: code,
        language: selectedLanguage,
      });

      setSubmissions((prev) => [response, ...prev]);
      setTestCaseStatuses(
        (prev) =>
          Object.fromEntries(
            Object.keys(prev).map((id) => [
              Number(id),
              response.result === "pass" ? "pass" : "fail",
            ])
          ) as Record<number, TestCaseStatus>
      );
      if (response.result === "fail") {
        setSessionErrors([
          response.error ?? "Your latest submission failed one or more tests.",
        ]);
      }
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Submission failed.";
      setSessionErrors([message]);
      setTestCaseStatuses(
        (prev) =>
          Object.fromEntries(
            Object.keys(prev).map((id) => [Number(id), "fail"])
          ) as Record<number, TestCaseStatus>
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="editor-stack">
      <section className="editor-panel" aria-label="Code editor">
        <ProblemPageEditorToolbar
          selectedLanguage={selectedLanguage}
          handleLanguageChange={handleLanguageChange}
          languageOptions={languageOptions}
          onRun={handleRun}
          onSubmit={handleSubmit}
          isSubmitting={isSubmitting}
        />

        <ProblemPageCodeEditor
          selectedLanguage={selectedLanguage}
          updateCode={updateCode}
          code={code}
        />
      </section>

      <ProblemPageTerminal
        testCases={problem.test_cases}
        testCaseStatuses={testCaseStatuses}
        submissions={submissions}
        hasSubmittedInSession={hasSubmittedInSession}
        sessionErrors={sessionErrors}
      />
    </div>
  );
}
