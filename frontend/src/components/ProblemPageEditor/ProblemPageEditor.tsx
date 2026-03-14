import { useNavigate } from "react-router-dom";
import type { Problem } from "../../types/problem";
import "./ProblemPageEditor.css";
import ProblemPageTerminal from "../ProblemPageTerminal/ProblemPageTerminal";
import ProblemPageCodeEditor from "../ProblemPageCodeEditor/ProblemPageCodeEditor";
import ProblemPageEditorToolbar from "../ProblemPageEditorToolbar/ProblemPageEditorToolbar";
import Modal from "../Modal/Modal";
import { useProblemEditor } from "../../hooks/useProblemEditor";

interface ProblemPageEditorProps {
  problem: Problem;
}

export default function ProblemPageEditor({ problem }: ProblemPageEditorProps) {
  const navigate = useNavigate();
  const {
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
  } = useProblemEditor(problem);

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
        onClose={closeSolvedModal}
        actions={[
          {
            label: "Keep Practicing",
            variant: "secondary",
            onClick: closeSolvedModal,
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
