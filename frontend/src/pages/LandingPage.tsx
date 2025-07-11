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
          className="text-4xl font-extrabold text-center mb-12 text-black  bg-white/50 backdrop-blur-md p-4 rounded-lg"
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
              className="bg-white rounded-2xl px-12 py-4 text-lg
                font-['SF_Pro_Display',-apple-system,BlinkMacSystemFont,'Segoe_UI',Roboto,Oxygen-Sans,Ubuntu,Cantarell,'Helvetica_Neue',sans-serif] 
                font-normal tracking-[-0.01em] text-[20px]
                shadow-[4px_4px_20px_rgba(0,0,0,0.15)] 
                relative before:absolute before:inset-0 before:rounded-2xl 
                before:bg-gradient-to-r before:from-gray-50 before:to-white 
                before:-z-10 before:transform before:translate-x-2 before:translate-y-2"
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