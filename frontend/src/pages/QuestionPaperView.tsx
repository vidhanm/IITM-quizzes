import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import MathBackground from "../components/MathBackground";
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import Chatbot from "../components/Chatbot";

interface Option {
  id: number;
  text: string;
  is_correct: boolean;
}

interface Question {
  id: number;
  question_text: string;
  question_type: string;
  options: Option[] | { value_start: number; value_end: number };
  total_mark: number;
}

interface QuestionPaper {
  id: number;
  title: string;
  description: string;
  year: number;
  total_score: number;
}

interface QuestionResult {
  question_id: number;
  correct: boolean;
  score: number;
  explanation: string;
}

interface SubmissionResult {
  total_score: number;
  results: QuestionResult[];
}

const QuestionPaperView = () => {
  const { paperId } = useParams();
  const navigate = useNavigate();
  const [paper, setPaper] = useState<QuestionPaper | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, number | string>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [results, setResults] = useState<SubmissionResult | null>(null);

  useEffect(() => {
    const fetchPaper = async () => {  
      try {
        const response = await fetch(`/api/papers/${paperId}`);
        const data = await response.json();
        console.log("Paper data:", data);
        setPaper(data.paper);
        setQuestions(data.questions);
      } catch (err) {
        console.error("Error fetching paper:", err);
        setError(err instanceof Error ? err.message : 'Failed to load paper');
      } finally {
        setLoading(false);
      }
    };

    fetchPaper();
  }, [paperId]);

  const handleAnswerSelect = (questionId: number, answer: number | string) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const renderAnswerInput = (question: Question) => {
    const questionType = question.question_type || 'MCQ';
    
    if (questionType === 'MCQ' && (!Array.isArray(question.options) || question.options.length === 0)) {
      return (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600">This question is missing its options. Please contact support.</p>
        </div>
      );
    }

    if (questionType === 'SA' && (!question.options || !('value_start' in question.options))) {
      return (
        <div className="space-y-2">
          <input
            type="number"
            step="0.01"
            value={selectedAnswers[question.id] || ''}
            onChange={(e) => handleAnswerSelect(question.id, e.target.value)}
            className="w-full max-w-xs p-2 border rounded"
            placeholder="Enter your numerical answer"
          />
          <p className="text-yellow-600 text-sm">
            Note: This question's answer range is not specified. Any numerical answer will be accepted.
          </p>
        </div>
      );
    }

    if (questionType === 'SA') {
      return (
        <input
          type="number"
          step="0.01"
          value={selectedAnswers[question.id] || ''}
          onChange={(e) => handleAnswerSelect(question.id, e.target.value)}
          className="w-full max-w-xs p-2 border rounded"
          placeholder="Enter your numerical answer"
        />
      );
    }

    return (
      <div className="space-y-2">
        {Array.isArray(question.options) && question.options.map((option) => (
          <div
            key={option.id}
            onClick={() => handleAnswerSelect(question.id, option.id)}
            className={`p-4 rounded-lg cursor-pointer transition-colors ${
              selectedAnswers[question.id] === option.id
                ? 'bg-primary/20'
                : 'hover:bg-gray-100/50'
            }`}
          >
            <div className="flex items-center gap-4">
              <div className={`w-4 h-4 rounded-full border-2 ${
                selectedAnswers[question.id] === option.id
                  ? 'border-primary bg-primary'
                  : 'border-gray-400'
              }`} />
              <span className="option-text-container">
                <img 
                  src={`/api/images/options/${option.id}`}
                  alt=""
                  data-option-id={option.id}
                  className="max-w-full h-auto"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    target.style.display = 'none';
                    const container = target.closest('.option-text-container');
                    if (container && !option.text) {
                      container.textContent = 'Untitled Option';
                    }
                  }}
                />
                {option.text && <span>{option.text}</span>}
              </span>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const handleSubmit = async () => {
    try {
      const response = await fetch(`/api/papers/${paperId}/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(selectedAnswers),
      });

      const data = await response.json();
      setResults(data);
      setSubmitted(true);
    } catch (err) {
      console.error('Error submitting paper:', err);
      setError(err instanceof Error ? err.message : 'Failed to submit paper');
    }
  };

  const getQuestionResult = (questionId: number) => {
    return results?.results.find(result => result.question_id === questionId);
  };

  const renderExplanation = (explanation: string) => {
    return (
      <div className="mt-3 p-4 bg-gray-50 rounded-lg">
        <h4 className="font-semibold mb-2">Explanation:</h4>
        <div className="latex-content">
          <ReactMarkdown
            remarkPlugins={[remarkMath]}
            rehypePlugins={[rehypeKatex]}
          >
            {explanation}
          </ReactMarkdown>
        </div>
      </div>
    );
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!paper) return <div>No paper found</div>;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="min-h-screen p-8"
    >
      <MathBackground />
      {paper && <Chatbot paper={paper} currentQuestions={questions} />}

      <motion.button
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        onClick={() => navigate(-1)}
        className="fixed top-4 left-4 glass-card px-4 py-2 hover:scale-105 transition-transform duration-200"
      >
        ← Back
      </motion.button>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-4xl font-extrabold text-center mb-12 text-black drop-shadow-lg bg-white bg-opacity-75 p-4 rounded-lg max-w-3xl mx-auto"
      >
        <h1 className="text-4xl font-bold">
          {paper.title || "Untitled Paper"}
        </h1>
        <p className="text-xl mt-2">Total Score: {paper.total_score}</p>
      </motion.div>

      <div className="max-w-3xl mx-auto space-y-8">
        {questions.map((question, index) => (
          <motion.div
            key={question.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="glass-card p-6"
          >
            <div className="flex justify-between mb-4">
              <h3 className="text-xl font-semibold">Question {index + 1}</h3>
              <span className="text-sm text-gray-600">Marks: {question.total_mark}</span>
            </div>

            <div className="question-content-container">
              <img
                src={`/api/images/questions/${question.id}`}
                alt=""
                data-question-id={question.id}
                className="max-w-full h-auto mb-4"
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.style.display = 'none';
                }}
              />
              <div className="question-text">{question.question_text}</div>
            </div>

            {renderAnswerInput(question)}

            {submitted && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="mt-4 pt-4 border-t"
              >
                {getQuestionResult(question.id) && (
                  <>
                    <div className={`p-3 rounded-lg ${
                      getQuestionResult(question.id)?.correct 
                        ? 'bg-green-50 text-green-700' 
                        : 'bg-red-50 text-red-700'
                    }`}>
                      <p className="font-semibold">
                        {getQuestionResult(question.id)?.correct 
                          ? '✓ Correct' 
                          : '✗ Incorrect'}
                      </p>
                      <p>Score: {getQuestionResult(question.id)?.score}</p>
                    </div>
                    {renderExplanation(getQuestionResult(question.id)?.explanation || '')}
                  </>
                )}
              </motion.div>
            )}
          </motion.div>
        ))}

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="sticky bottom-8 flex justify-center"
        >
          {!submitted ? (
            <button
              onClick={handleSubmit}
              className="glass-card px-8 py-3 bg-primary text-white rounded-lg hover:scale-105 transition-transform duration-200"
            >
              Submit Paper
            </button>
          ) : (
            <div className="glass-card px-8 py-3 bg-gray-100">
              <p className="font-semibold">Total Score: {results?.total_score || 0}</p>
            </div>
          )}
        </motion.div>
      </div>
    </motion.div>
  );
};

export default QuestionPaperView;