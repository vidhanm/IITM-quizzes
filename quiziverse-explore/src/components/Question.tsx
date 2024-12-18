// quiziverse-explorer/src/components/Question.tsx
import { useState } from 'react';
import { Input } from './ui/input';

interface SAOption {
  value_start: number;
  value_end: number;
}

interface MCQOption {
  id: number;
  text: string;
  is_correct: boolean;
}

interface QuestionProps {
  question: {
    id: number;
    question_text: string;
    question_type: string;
    options: MCQOption[] | SAOption;
    image_urls?: string[];
  };
  onAnswer: (questionId: number, answer: number | string) => void;
  selectedAnswer?: number | string;
  showResult?: boolean;
  result?: {
    correct: boolean;
    explanation?: string;
  };
}

export function Question({ question, onAnswer, selectedAnswer, showResult, result }: QuestionProps) {
  const [inputValue, setInputValue] = useState(selectedAnswer?.toString() || '');

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setInputValue(value);
    
    if (question.question_type === 'SA') {
      const options = question.options as SAOption;
      const numericAnswer = parseFloat(value);
      
      // Check if answer is within the acceptable range
      const isCorrect = numericAnswer >= options.value_start && 
                       numericAnswer <= options.value_end;
      
      onAnswer(question.id, value);
    } else {
      onAnswer(question.id, value);
    }
  };

  return (
    <div className="space-y-4">
      <div className="text-lg font-medium">{question.question_text}</div>
      
      {/* Question images */}
      <img 
        src={`/images/questions/${question.id}`} 
        alt={`Question ${question.id}`} 
        className="max-w-full h-auto" 
      />

      {question.question_type === 'SA' ? (
        <div className="space-y-2">
          <Input
            type="number"
            step="0.01"
            value={inputValue}
            onChange={handleInputChange}
            placeholder="Enter your numerical answer"
            className="max-w-xs"
          />
          {showResult && result && (
            <div className={`mt-2 text-sm ${result.correct ? 'text-green-600' : 'text-red-600'}`}>
              {result.correct ? 'Correct!' : `Incorrect. The answer should be between ${(question.options as SAOption).value_start} and ${(question.options as SAOption).value_end}`}
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-2">
          {(question.options as MCQOption[]).map((option) => (
            <div
              key={option.id}
              onClick={() => onAnswer(question.id, option.id)}
              className={`p-4 rounded-lg cursor-pointer transition-colors ${
                selectedAnswer === option.id
                  ? 'bg-primary/20 border-primary'
                  : 'hover:bg-gray-100/50'
              } ${
                showResult && option.is_correct
                  ? 'bg-green-100 border-green-500'
                  : showResult && selectedAnswer === option.id && !option.is_correct
                  ? 'bg-red-100 border-red-500'
                  : ''
              }`}
            >
              <div className="flex items-center gap-4">
                <div className={`w-4 h-4 rounded-full border-2 ${
                  selectedAnswer === option.id
                    ? 'border-primary bg-primary'
                    : 'border-gray-400'
                }`} />
                <span>{option.text}</span>
              </div>
              {/* Option images */}
              <img 
                src={`/images/options/${option.id}`} 
                alt={`Option ${option.id}`}
                className="mt-2 max-w-full h-auto" 
              />
            </div>
          ))}
        </div>
      )}

      {showResult && result?.explanation && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-600">{result.explanation}</p>
        </div>
      )}
    </div>
  );
}