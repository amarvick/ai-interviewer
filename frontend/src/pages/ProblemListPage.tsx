import { useParams } from "react-router-dom";

export default function ProblemListPage() {
  const { id } = useParams();

  return (
    <section className="simple-page">
      <h1>Problem List</h1>
      <p>List ID: {id}</p>
    </section>
  );
}
