import { useEffect, useMemo, useState } from "react";
import type { Problem } from "../types/problem";
import type { SubmissionResponse } from "../types/submission";
import { getSubmissions, runSubmission } from "../services/api";
import type { TestCaseStatus } from "../utils/problemEditor";
import { buildInitialStatuses, mapStatusesForResult } from "../utils/problemEditor";

export interface UseProblemEditorResult {
  languageOptions: string[];
  selectedLanguage: string;
  code: string;
  submissions: SubmissionResponse[];
  isSubmitting: boolean;
  hasSubmittedInSession: boolean;
  sessionErrors: string[];
  testCaseStatuses: Record<string, TestCaseStatus>;
  isSolvedModalOpen: boolean;
  handleLanguageChange: (language: string) => void;
  updateCode: (value: string | undefined) => void;
  handleSubmit: () => Promise<void>;
  closeSolvedModal: () => void;
  openSolvedModal: () => void;
}

export function useProblemEditor(problem: Problem): UseProblemEditorResult {
  const starterCode = problem?.starter_code ?? {};
  const languageOptions = useMemo(() => {
    const keys = Object.keys(starterCode);
    return keys.length > 0 ? keys : ["javascript"];
  }, [starterCode]);

  const [selectedLanguage, setSelectedLanguage] = useState<string>(
    languageOptions[0] ?? "javascript"
  );
  const [code, setCode] = useState<string>(starterCode[selectedLanguage] ?? "");
  const [submissions, setSubmissions] = useState<SubmissionResponse[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [hasSubmittedInSession, setHasSubmittedInSession] = useState(false);
  const [sessionErrors, setSessionErrors] = useState<string[]>([]);
  const [testCaseStatuses, setTestCaseStatuses] = useState<
    Record<string, TestCaseStatus>
  >(() => buildInitialStatuses(problem));
  const [isSolvedModalOpen, setIsSolvedModalOpen] = useState(false);

  useEffect(() => {
    setTestCaseStatuses(buildInitialStatuses(problem));
    setHasSubmittedInSession(false);
    setSessionErrors([]);
  }, [problem]);

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

  useEffect(() => {
    setSelectedLanguage(languageOptions[0] ?? "javascript");
  }, [languageOptions]);

  useEffect(() => {
    setCode(starterCode[selectedLanguage] ?? "");
  }, [starterCode, selectedLanguage]);

  const handleLanguageChange = (nextLanguage: string) => {
    setSelectedLanguage(nextLanguage);
    setCode(starterCode[nextLanguage] ?? "");
  };

  const updateCode = (value: string | undefined) => {
    setCode(value ?? "");
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
      setTestCaseStatuses((prev) =>
        mapStatusesForResult(prev, problem, response)
      );
      if (response.result === "fail") {
        setSessionErrors([
          response.error ?? "Your latest submission failed one or more tests.",
        ]);
      } else {
        setIsSolvedModalOpen(true);
      }
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Submission failed.";
      setSessionErrors([message]);
      setTestCaseStatuses(
        (prev) =>
          Object.fromEntries(
            Object.keys(prev).map((id) => [id, "fail"])
          ) as Record<string, TestCaseStatus>
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const closeSolvedModal = () => setIsSolvedModalOpen(false);
  const openSolvedModal = () => setIsSolvedModalOpen(true);

  return {
    languageOptions,
    selectedLanguage,
    code,
    submissions,
    isSubmitting,
    hasSubmittedInSession,
    sessionErrors,
    testCaseStatuses,
    isSolvedModalOpen,
    handleLanguageChange,
    updateCode,
    handleSubmit,
    closeSolvedModal,
    openSolvedModal,
  };
}
