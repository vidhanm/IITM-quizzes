import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import MathBackground from "../components/MathBackground";

interface QuestionPaper {
  id: number;
  file_path: string;
  total_score: number;
}

const QuestionPapersPage = () => {
  const { subject } = useParams();
  const navigate = useNavigate();
  const [papers, setPapers] = useState<QuestionPaper[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPapers = async () => {
      try {
        const response = await fetch(`/api/courses/${subject}/papers`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          }
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch papers');
        }
        
        const data = await response.json();
        setPapers(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load papers');
      } finally {
        setLoading(false);
      }
    };

    fetchPapers();
  }, [subject]);

  const containerVariants = {
    initial: { opacity: 0 },
    animate: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    initial: { opacity: 0, x: -20 },
    animate: { opacity: 1, x: 0 },
    hover: { scale: 1.02, transition: { duration: 0.2 } }
  };

  // Updated getFileName function to clean up the display
  const getFileName = (filePath: string) => {
    // Split by backslash and take everything after the second one
    const parts = filePath.split('\\');
    let filename = parts.length > 2 ? parts.slice(2).join('\\') : filePath;
    
    // Remove .json extension and comprehensive_processed suffix
    filename = filename
      .replace('.json', '')
      .replace('_comprehensive_processed', '');
    
    // Replace underscores with spaces
    filename = filename.replace(/_/g, ' ');
    
    // Remove duplicate year pattern (YYYY YYYY)
    filename = filename.replace(/(\d{4}) \d{4}/, '$1');
    

    return filename;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading papers...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-red-500">Error: {error}</div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="min-h-screen p-8"
    >
      <MathBackground />

      <motion.button
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        onClick={() => navigate(-1)}
        className="fixed top-4 left-4 glass-card px-4 py-2 hover:scale-105 transition-transform duration-200"
      >
        ← Back
      </motion.button>

      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-4xl font-extrabold text-center mb-12 text-black drop-shadow-lg bg-white bg-opacity-75 p-4 rounded-lg max-w-3xl mx-auto"
      >
        <h1 className="text-4xl font-bold mb-2">Question Papers</h1>
        <p className="text-lg text-gray-600">Select a question paper</p>
      </motion.div>

      <motion.div
        variants={containerVariants}
        initial="initial"
        animate="animate"
        className="max-w-2xl mx-auto space-y-4"
      >
        {papers.map((paper) => (
          <motion.div
            key={paper.id}
            variants={itemVariants}
            whileHover="hover"
            onClick={() => navigate(`/paper/${paper.id}`)}
            className="glass-card p-6 cursor-pointer"
          >
            <h2 className="text-xl font-semibold">{getFileName(paper.file_path)}</h2>
            <p className="text-sm text-gray-600">Total Score: {paper.total_score}</p>
          </motion.div>
        ))}
      </motion.div>
    </motion.div>
  );
};

export default QuestionPapersPage;