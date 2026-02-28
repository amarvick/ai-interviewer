import { useParams } from "react-router-dom";
import InterviewPageEditor from "../../components/InterviewPageEditor/InterviewPageEditor";
import ProblemWorkspace from "../../components/ProblemWorkspace/ProblemWorkspace";

export default function InterviewPage() {
  const { id } = useParams();

  return (
    <ProblemWorkspace
      problemId={id ?? ""}
      secondaryComponent={(problem) => (
        <InterviewPageEditor problem={problem} />
      )}
    />
  );
}
