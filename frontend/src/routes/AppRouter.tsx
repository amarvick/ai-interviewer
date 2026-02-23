// routes/AppRouter.tsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "../components/Layout";
import HomePage from "../pages/HomePage/HomePage";
import LoginPage from "../pages/LoginPage/LoginPage";
import SignupPage from "../pages/SignupPage/SignupPage";
import ProblemListPage from "../pages/ProblemListPage/ProblemListPage";
import ProblemPage from "../pages/ProblemPage/ProblemPage";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/list/:id" element={<ProblemListPage />} />
          <Route path="/problem/:id" element={<ProblemPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
