// routes/AppRouter.tsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "../components/Layout";
import HomePage from "../pages/HomePage";
import LoginPage from "../pages/LoginPage";
import SignupPage from "../pages/SignupPage";
import ProblemListPage from "../pages/ProblemListPage";
import ProblemPage from "../pages/ProblemPage";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/lists/:id" element={<ProblemListPage />} />
          <Route path="/problems/:id" element={<ProblemPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
