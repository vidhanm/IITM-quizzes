import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

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

interface ChatbotProps {
  paper: {
    id: number;
    title: string;
    total_score: number;
  };
  currentQuestions: Question[];
}

const Chatbot = ({ paper, currentQuestions }: ChatbotProps) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Function to convert an image to base64
  const imageToBase64 = async (imgElement: HTMLImageElement): Promise<string | null> => {
    try {
      // Create a canvas element
      const canvas = document.createElement('canvas');
      canvas.width = imgElement.naturalWidth;
      canvas.height = imgElement.naturalHeight;
      
      // Draw the image onto the canvas
      const ctx = canvas.getContext('2d');
      if (!ctx) return null;
      
      ctx.drawImage(imgElement, 0, 0);
      
      // Convert the canvas to base64
      return canvas.toDataURL('image/jpeg');
    } catch (error) {
      console.error('Error converting image to base64:', error);
      return null;
    }
  };

  // Function to get image data for a question or option
  const getImageData = async (element: HTMLImageElement | null): Promise<string | null> => {
    if (!element) return null;
    
    // Wait for the image to load
    if (!element.complete) {
      await new Promise(resolve => {
        element.onload = resolve;
        element.onerror = resolve;
      });
    }

    // If the image failed to load or is hidden, return null
    if (element.style.display === 'none' || !element.complete || !element.naturalWidth) {
      return null;
    }

    return imageToBase64(element);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    console.log('Sending message:', userMessage);
    
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    // Create new AbortController for this request
    abortControllerRef.current = new AbortController();

    try {
      // Create quiz context with proper type handling and property names
      const quizContext = {
        paper: {
          id: paper.id,
          title: paper.title,
          total_score: paper.total_score
        },
        questions: await Promise.all(currentQuestions.map(async q => {
          // Try to get question image
          const questionImg = document.querySelector<HTMLImageElement>(`img[data-question-id="${q.id}"]`);
          const questionImageData = await getImageData(questionImg);
          
          // Handle options
          const processedOptions = Array.isArray(q.options) 
            ? await Promise.all(q.options.map(async opt => {
                const optionImg = document.querySelector<HTMLImageElement>(`img[data-option-id="${opt.id}"]`);
                const optionImageData = await getImageData(optionImg);
                
                return {
                  id: opt.id,
                  text: opt.text,
                  is_correct: opt.is_correct,
                  image: optionImageData
                };
              }))
            : null;

          return {
            id: q.id,
            text: q.question_text,
            type: q.question_type,
            marks: q.total_mark,
            image: questionImageData,
            options: processedOptions,
            answer_range: !Array.isArray(q.options) ? q.options : null
          };
        }))
      };

      console.log('Making API request with context:', quizContext);
      
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          history: [...messages, { role: 'user', content: userMessage }],
          context: quizContext
        }),
        signal: abortControllerRef.current.signal,
      });

      console.log('API Response status:', response.status);
      
      if (!response.ok) {
        const errorData = await response.json();
        console.error('API Error:', errorData);
        throw new Error(errorData.error || 'Failed to get response from chatbot');
      }

      const data = await response.json();
      console.log('API Response data:', data);
      
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);
    } catch (error) {
      console.error('Chat error:', error);
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('Request was aborted');
      } else {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: 'Sorry, I encountered an error. Please try again.' 
        }]);
      }
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {!isOpen && (
        <motion.button
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => {
            setIsOpen(true);
            setIsMinimized(false);
          }}
          className="glass-card p-4 rounded-full shadow-lg"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
            />
          </svg>
        </motion.button>
      )}

      {isOpen && (
        <motion.div
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ 
            opacity: 1, 
            scale: 1,
            height: isMinimized ? '64px' : '600px',
            width: isMinimized ? '300px' : '450px'
          }}
          transition={{ duration: 0.2 }}
          exit={{ opacity: 0, scale: 0.5 }}
          className="glass-card flex flex-col"
        >
          <div className="flex justify-between items-center p-4 border-b bg-primary/10">
            <h3 className="text-lg font-semibold">Quiz Assistant</h3>
            <div className="flex gap-2">
              <button
                onClick={() => setIsMinimized(!isMinimized)}
                className="text-gray-500 hover:text-gray-700 transition-colors"
                title={isMinimized ? "Expand" : "Minimize"}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  {isMinimized ? (
                    <path
                      fillRule="evenodd"
                      d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"
                      clipRule="evenodd"
                    />
                  ) : (
                    <path
                      fillRule="evenodd"
                      d="M3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"
                      clipRule="evenodd"
                    />
                  )}
                </svg>
              </button>
              <button
                onClick={() => {
                  setIsOpen(false);
                  setIsMinimized(false);
                }}
                className="text-gray-500 hover:text-gray-700 transition-colors"
                title="Close"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
            </div>
          </div>

          {!isMinimized && (
            <>
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((message, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex ${
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    <div
                      className={`max-w-[85%] p-3 rounded-lg ${
                        message.role === 'user'
                          ? 'bg-primary text-white'
                          : 'bg-gray-100 shadow-sm'
                      }`}
                    >
                      <ReactMarkdown 
                        className={`prose ${message.role === 'user' ? 'prose-invert' : ''} max-w-none`}
                      >
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  </motion.div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 p-3 rounded-lg shadow-sm">
                      <div className="flex space-x-2">
                        <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce" />
                        <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                        <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              <form onSubmit={handleSubmit} className="p-4 border-t">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type your question..."
                    className="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-white/50"
                    disabled={isLoading}
                  />
                  {isLoading ? (
                    <button
                      type="button"
                      onClick={handleStop}
                      className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                    >
                      Stop
                    </button>
                  ) : (
                    <button
                      type="submit"
                      disabled={!input.trim() || isLoading}
                      className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 disabled:opacity-50 transition-colors"
                    >
                      Send
                    </button>
                  )}
                </div>
              </form>
            </>
          )}
        </motion.div>
      )}
    </div>
  );
};

export default Chatbot; 