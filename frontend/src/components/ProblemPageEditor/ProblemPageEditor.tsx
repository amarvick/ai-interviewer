import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { Problem } from "../../types/problem";
import "./ProblemPageEditor.css";
import ProblemPageTerminal from "../ProblemPageTerminal/ProblemPageTerminal";
import ProblemPageCodeEditor from "../ProblemPageCodeEditor/ProblemPageCodeEditor";
import ProblemPageEditorToolbar from "../ProblemPageEditorToolbar/ProblemPageEditorToolbar";
import Modal from "../Modal/Modal";
import type { SubmissionResponse } from "../../types/submission";
import { getSubmissions, runSubmission } from "../../services/api";

interface ProblemPageEditorProps {
  problem: Problem;
}

type TestCaseStatus = "pending" | "pass" | "fail";

export default function ProblemPageEditor({ problem }: ProblemPageEditorProps) {
  const navigate = useNavigate();
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
    Record<string, TestCaseStatus>
  >({});
  const [isSolvedModalOpen, setIsSolvedModalOpen] = useState(false);

  useEffect(() => {
    const nextStatuses = problem.test_cases.reduce<
      Record<string, TestCaseStatus>
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
      setTestCaseStatuses((prev) => {
        if (response.result === "pass") {
          return Object.fromEntries(
            Object.keys(prev).map((id) => [id, "pass"])
          ) as Record<string, TestCaseStatus>;
        }

        const next = Object.fromEntries(
          Object.keys(prev).map((id) => [id, "pending"])
        ) as Record<string, TestCaseStatus>;

        const failedCaseIndex = parseFailedCaseIndex(response.error);
        if (failedCaseIndex === null) {
          return next;
        }

        const orderedIds = problem.test_cases.map((testCase) => testCase.id);
        for (let i = 0; i < orderedIds.length; i += 1) {
          const id = orderedIds[i];
          if (i + 1 < failedCaseIndex) {
            next[id] = "pass";
          } else if (i + 1 === failedCaseIndex) {
            next[id] = "fail";
          }
        }
        return next;
      });
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

  return (
    <div className="editor-stack">
      <section className="editor-panel" aria-label="Code editor">
        <ProblemPageEditorToolbar
          selectedLanguage={selectedLanguage}
          handleLanguageChange={handleLanguageChange}
          languageOptions={languageOptions}
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

      <Modal
        isOpen={isSolvedModalOpen}
        title="Nice work. You solved it."
        description={`You passed all test cases for ${problem.title}.`}
        onClose={() => setIsSolvedModalOpen(false)}
        actions={[
          {
            label: "Keep Practicing",
            variant: "secondary",
            onClick: () => setIsSolvedModalOpen(false),
          },
          {
            label: "Back to Home",
            variant: "primary",
            onClick: () => navigate("/"),
          },
        ]}
      >
        <p>
          Your latest submission has been saved. You can review submissions in
          the Submissions tab or move on to the next problem.
        </p>
      </Modal>
    </div>
  );
}

function parseFailedCaseIndex(errorText?: string | null): number | null {
  if (!errorText) {
    return null;
  }
  const match = errorText.match(/test case #(\d+)/i);
  if (!match) {
    return null;
  }
  const parsed = Number(match[1]);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : null;
}
