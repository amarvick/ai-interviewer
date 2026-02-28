import { useParams } from "react-router-dom";
import ProblemWorkspace from "../../components/ProblemWorkspace/ProblemWorkspace";
import ProblemPageEditor from "../../components/ProblemPageEditor/ProblemPageEditor";

export default function ProblemPage() {
  const { id } = useParams();

  return (
    <ProblemWorkspace
      problemId={id ?? ""}
      secondaryComponent={(problem) => <ProblemPageEditor problem={problem} />}
    />
  );
}
