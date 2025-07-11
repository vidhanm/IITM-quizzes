import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
// We'll use a simple CSS solution instead of external packages that might not be installed

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

  // Custom styles for better formatting
  const customStyles = `
    .markdown-content {
      font-family: system-ui, -apple-system, sans-serif;
    }
    
    .markdown-content table {
      border-collapse: collapse;
      width: 100%;
      margin: 12px 0;
      font-size: 0.9em;
    }
    
    .markdown-content th, 
    .markdown-content td {
      border: 1px solid #ddd;
      padding: 8px;
      text-align: left;
    }
    
    .markdown-content th {
      background-color: #f2f2f2;
      font-weight: bold;
    }
    
    .markdown-content tr:nth-child(even) {
      background-color: #f9f9f9;
    }
    
    .markdown-content strong, 
    .markdown-content b {
      font-weight: bold;
    }
    
    .markdown-content em, 
    .markdown-content i {
      font-style: italic;
    }
    
    .markdown-content ul, 
    .markdown-content ol {
      padding-left: 20px;
      margin: 10px 0;
    }
    
    .markdown-content p {
      margin: 10px 0;
    }

    .markdown-content pre {
      background-color: #1e1e1e;
      color: #d4d4d4;
      padding: 1rem;
      border-radius: 0.5rem;
      overflow-x: auto;
      margin: 1rem 0;
      font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    }

    .markdown-content code {
      font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
      padding: 0.2rem 0.4rem;
      border-radius: 0.25rem;
      font-size: 0.9em;
      background-color: #1e1e1e;
      color: #d4d4d4;
    }

    .markdown-content .keyword { color: #569cd6; }
    .markdown-content .string { color: #ce9178; }
    .markdown-content .comment { color: #6a9955; }
    .markdown-content .number { color: #b5cea8; }
    .markdown-content .operator { color: #d4d4d4; }
    .markdown-content .function { color: #dcdcaa; }
  `;

  // Function to format markdown content properly
  const formatMarkdownContent = (content: string): string => {
    // First, escape any HTML that might be in the content
    let formatted = content
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
    
    // Process code blocks with language specification
    formatted = formatted.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
      // Clean the code by removing line number spans and other HTML-like elements
      code = code
        .replace(/<span.*?>(.*?)<\/span>/g, '$1') // Remove span elements but keep their content
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>')
        .replace(/&amp;/g, '&')
        .trim();

      // Basic syntax highlighting for Python
      if (lang === 'python') {
        code = code
          .replace(/(def|class|if|else|for|in|return|True|False|import|from|as)\b/g, '<span class="keyword">$1</span>')
          .replace(/(["'])(.*?)\1/g, '<span class="string">$1$2$1</span>')
          .replace(/#.*/g, '<span class="comment">$&</span>')
          .replace(/\b(\d+)\b/g, '<span class="number">$1</span>')
          .replace(/(\(|\)|\[|\]|=|\+|-|\*|\/|:)/g, '<span class="operator">$1</span>')
          .replace(/([a-zA-Z_][a-zA-Z0-9_]*(?=\())/g, '<span class="function">$1</span>');
      }
      return `<pre><code class="language-${lang || 'text'}">${code}</code></pre>`;
    });

    // Process inline code
    formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Special handling for LLM-style formatting with asterisks
    // Double asterisks for bold - with special handling for the **Statement X:** pattern
    formatted = formatted.replace(/\*\*(Statement \d+:?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Special cases for Conclusion, Summary Table, etc.
    formatted = formatted.replace(/\*\*(Conclusion:?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/\*\*(Summary Table:?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/\*\*(Incorrect:?)\*\*/g, '<strong class="text-red-500">$1</strong>');
    formatted = formatted.replace(/\*\*(Correct:?)\*\*/g, '<strong class="text-green-500">$1</strong>');
    
    // Handle underscores for bold too (common in some LLM outputs)
    formatted = formatted.replace(/__(.*?)__/g, '<strong>$1</strong>');
    
    // Process italic text with single asterisks or underscores
    formatted = formatted.replace(/(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)/g, '<em>$1</em>');
    formatted = formatted.replace(/(?<!_)_(?!_)(.*?)(?<!_)_(?!_)/g, '<em>$1</em>');
    
    // Process lists
    formatted = formatted.replace(/^\s*-\s+(.*?)$/gm, '<li>$1</li>');
    formatted = formatted.replace(/((?:<li>.*?<\/li>\n?)+)/gs, '<ul>$1</ul>');
    
    // Handle numbered lists
    formatted = formatted.replace(/^\s*(\d+)\.\s+(.*?)$/gm, '<li>$2</li>');
    
    // Clean up any duplicate or nested list tags
    formatted = formatted.replace(/<\/ul>\s*<ul>/g, '');
    formatted = formatted.replace(/<ul>(\s*<ul>)/g, '<ul>');
    formatted = formatted.replace(/(<\/ul>\s*)<\/ul>/g, '$1');
    
    // Process tables
    const tablePattern = /(?:^|\n)([^\n]*\|[^\n]*(?:\n[^\n]*\|[^\n]*)+)(?:\n|$)/g;
    formatted = formatted.replace(tablePattern, (match) => {
      const rows = match.trim().split('\n');
      if (rows.length < 2) return match;
      
      let tableHTML = '<table>';
      let isHeader = true;
      
      for (let i = 0; i < rows.length; i++) {
        const row = rows[i].trim();
        if (row.match(/^\|?\s*[-:]+[-|\s:]*$/)) continue;
        
        const cells = row.split('|')
          .map(cell => cell.trim())
          .filter(cell => cell !== '');
        
        if (cells.length === 0) continue;
        
        const cellTag = (i === 0 && rows.length > 1) ? 'th' : 'td';
        
        tableHTML += '<tr>';
        cells.forEach(cell => {
          tableHTML += `<${cellTag}>${cell}</${cellTag}>`;
        });
        tableHTML += '</tr>';
        
        isHeader = false;
      }
      
      tableHTML += '</table>';
      return tableHTML;
    });
    
    // Handle line breaks
    formatted = formatted.replace(/\n/g, '<br />');
    
    return formatted;
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <style>{customStyles}</style>
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
          className="glass-card flex flex-col max-w-[95vw] sm:max-w-[450px]"
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
                      className={`max-w-[85%] p-3 rounded-lg break-words ${
                        message.role === 'user'
                          ? 'bg-primary text-white'
                          : 'bg-gray-100 shadow-sm'
                      }`}
                    >
                      <div
                        className={`prose ${message.role === 'user' ? 'prose-invert' : ''} max-w-none prose-sm sm:prose-base markdown-content`}
                        dangerouslySetInnerHTML={{
                          __html: formatMarkdownContent(message.content)
                        }}
                      />
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
                    className="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-white/50 text-sm sm:text-base"
                    disabled={isLoading}
                  />
                  {isLoading ? (
                    <button
                      type="button"
                      onClick={handleStop}
                      className="px-3 sm:px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors text-sm sm:text-base"
                    >
                      Stop
                    </button>
                  ) : (
                    <button
                      type="submit"
                      disabled={!input.trim() || isLoading}
                      className="px-3 sm:px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 disabled:opacity-50 transition-colors text-sm sm:text-base"
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