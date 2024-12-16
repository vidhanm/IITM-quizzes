import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import MathBackground from "../components/MathBackground";

const LandingPage = () => {
  const navigate = useNavigate();

  const buttonVariants = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    hover: { scale: 1.05, transition: { duration: 0.2 } }
  };

  const containerVariants = {
    initial: { opacity: 0 },
    animate: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2
      }
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="min-h-screen flex items-center justify-center"
    >
      <MathBackground />
      
      <motion.div
        variants={containerVariants}
        initial="initial"
        animate="animate"
        className="space-y-6"
      >
        <motion.h1 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl font-extrabold text-center mb-12 text-black drop-shadow-lg bg-white bg-opacity-75 p-4 rounded-lg"
        >
          Select Your Exam
        </motion.h1>

        <motion.div className="flex flex-col space-y-4">
          {["End Term"].map((quiz, index) => (
            <motion.button
              key={quiz}
              variants={buttonVariants}
              whileHover="hover"
              onClick={() => navigate(`/subjects/${quiz.toLowerCase().replace(" ", "-")}`)}
              className="glass-card px-12 py-4 text-lg font-medium hover:shadow-2xl transition-all duration-300"
            >
              {quiz}
            </motion.button>
          ))}
        </motion.div>
      </motion.div>
    </motion.div>
  );
};

export default LandingPage;