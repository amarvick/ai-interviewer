import { useParams } from "react-router-dom";

export default function ProblemPage() {
  const { id } = useParams();

  return (
    <section className="simple-page">
      <h1>Problem</h1>
      <p>Problem ID: {id}</p>
    </section>
  );
}
