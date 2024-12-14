from dataclasses import dataclass
from typing import List, Optional, Dict

@dataclass
class Option:
    id: int
    text: str
    is_correct: bool
    image_url: Optional[str] = None

@dataclass
class Question:
    id: int
    question_text: str
    question_type: str
    image_urls: Optional[List[str]]
    options: List[Option]
    explanation: Optional[str]
    total_mark: float

@dataclass
class QuestionPaper:
    id: int
    title: str
    description: str
    year: int
    total_score: float

@dataclass
class SubmitAnswer:
    answers: Dict[str, int]