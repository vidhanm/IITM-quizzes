import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import LandingPage from "./pages/LandingPage";
import SubjectsPage from "./pages/SubjectsPage";
import QuestionPapersPage from "./pages/QuestionPapersPage";
import QuestionPaperView from "./pages/QuestionPaperView";

const App = () => {
  return (
    <BrowserRouter>
      <AnimatePresence mode="wait">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/subjects/:quizType" element={<SubjectsPage />} />
          <Route path="/papers/:subject" element={<QuestionPapersPage />} />
          <Route path="/paper/:paperId" element={<QuestionPaperView />} />
        </Routes>
      </AnimatePresence>
    </BrowserRouter>
  );
};

export default App;