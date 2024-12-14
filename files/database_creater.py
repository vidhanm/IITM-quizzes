# import_data.py
import json
import os
import sqlite3
import re
from pathlib import Path
from typing import Dict, List

# this creates a DB file from comprehensive processed json files in QA/ET 


class DatabaseImporter:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.setup_database()
    
    def setup_database(self):
        """Create necessary tables if they don't exist"""
        self.cursor.executescript("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                code TEXT,  -- Made optional since we may not have it
                uuid TEXT UNIQUE
            );

            CREATE TABLE IF NOT EXISTS question_papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                file_path TEXT UNIQUE NOT NULL,
                total_score REAL,
                course_id INTEGER,
                uuid TEXT UNIQUE,
                FOREIGN KEY (course_id) REFERENCES courses(id)
            );

            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY,
                paper_id INTEGER,
                course_id INTEGER,
                question_text TEXT,
                question_type TEXT NOT NULL,
                total_mark REAL,
                image_urls TEXT,  -- JSON array of URLs
                explanation TEXT,
                uuid TEXT UNIQUE NOT NULL,
                FOREIGN KEY (paper_id) REFERENCES question_papers(id),
                FOREIGN KEY (course_id) REFERENCES courses(id)
            );

            CREATE TABLE IF NOT EXISTS options (
                id INTEGER PRIMARY KEY,
                question_id INTEGER,
                option_text TEXT,
                is_correct BOOLEAN NOT NULL,
                score REAL,
                image_url TEXT,
                FOREIGN KEY (question_id) REFERENCES questions(id)
            );
        """)
        self.conn.commit()

    def extract_course_name(self, file_path: str) -> str:
        """Extract course name from file path
        Example path: files/QA/ET/ET_Advanced Algorithms/ET_Advanced_Algorithms_2023_2023_Sep03__IIT_M_DEGREE_ET1_EXAM_QPE1_comprehensive_processed.json
        """
        if not file_path:
            return "Unknown Course"
            
        # Get the file name without extension
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # Split by underscore and get relevant parts
        parts = file_name.split('_')
        
        # Look for the course name part (typically after "ET_")
        if len(parts) >= 3 and parts[0] == "ET":
            # Take parts until we hit a year or other metadata
            course_parts = []
            for part in parts[1:]:
                if part.isdigit() or part in ["IIT", "DEGREE", "EXAM"]:
                    break
                course_parts.append(part)
            
            course_name = " ".join(course_parts)
            return course_name.strip() or "Unknown Course"
            
        return "Unknown Course"

    def extract_paper_info(self, file_path: str) -> Dict:
        """Extract paper info from file path"""
        # Example path: files/QA/ET/ET_Advanced Algorithms/ET_Advanced_Algorithms_2023_2023_Sep03__IIT_M_DEGREE_ET1_EXAM_QPE1_comprehensive_processed.json
        file_name = os.path.basename(file_path)
        parts = file_name.split('_')
        
        # Load the JSON file to get the UUID
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                questions = json.load(f)
                # Get UUID from first question if available
                uuid = questions[0].get('uuid') if questions else None
        except (json.JSONDecodeError, IndexError, KeyError):
            uuid = None
        
        return {
            'title': self.extract_course_name(file_path),  # "Advanced Algorithms"
            'file_path': file_path,
            'uuid': uuid
        }

    def import_course(self, course_id: int, file_path: str) -> int:
        """Import course and return its ID"""
        course_name = self.extract_course_name(file_path)
        
        # Load the JSON file to get the UUID
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                questions = json.load(f)
                # Get UUID from first question if available
                uuid = questions[0].get('uuid') if questions else None
        except (json.JSONDecodeError, IndexError, KeyError):
            uuid = None
        
        self.cursor.execute("""
            INSERT OR IGNORE INTO courses (id, name, uuid)
            VALUES (?, ?, ?)
        """, (course_id, course_name, uuid))
        
        self.conn.commit()
        return course_id

    def import_question_paper(self, file_path: str, course_id: int, total_score: float = 0) -> int:
        """Import question paper and return its ID"""
        paper_info = self.extract_paper_info(file_path)
        
        self.cursor.execute("""
            INSERT OR IGNORE INTO question_papers 
            (title, file_path, total_score, course_id, uuid)
            VALUES (?, ?, ?, ?, ?)
            RETURNING id
        """, (
            paper_info['title'],
            paper_info['file_path'],
            total_score,
            course_id,
            paper_info['uuid']
        ))
        
        paper_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return paper_id

    def import_question(self, question_data: Dict, paper_id: int):
        """Import question and its options"""
        # Convert image URLs list to JSON string if present
        image_urls = json.dumps(question_data.get('question_image_url')) if question_data.get('question_image_url') else None
        
        self.cursor.execute("""
            INSERT OR IGNORE INTO questions 
            (id, paper_id, course_id, question_text, question_type, total_mark, image_urls, explanation, uuid)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            question_data['id'],
            paper_id,
            question_data.get('course_id'),
            question_data['question_text'],
            question_data['question_type'],
            float(question_data['total_mark']),
            image_urls,
            question_data.get('comprehensive_explanation'),
            question_data['uuid']
        ))

        # Import options
        for option in question_data.get('options', []):
            self.cursor.execute("""
                INSERT OR IGNORE INTO options 
                (id, question_id, option_text, is_correct, score, image_url)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                option['id'],
                question_data['id'],
                option['text'],
                option['is_correct'],
                float(option['score']),
                option.get('option_image_url')
            ))
        
        self.conn.commit()

    def process_json_file(self, file_path: str):
        """Process a single JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            questions = json.load(f)

        if not isinstance(questions, list):
            print(f"Warning: Unexpected JSON format in {file_path}")
            return

        # Calculate total score for paper
        total_score = sum(float(q['total_mark']) for q in questions)

        # Get course_id from first question that has it
        course_id = next((q['course_id'] for q in questions if q.get('course_id')), None)
        if course_id:
            # Import course using the file path
            self.import_course(course_id, file_path)
            
            # Import question paper
            paper_id = self.import_question_paper(file_path, course_id, total_score)
            
            # Import all questions
            for question in questions:
                try:
                    self.import_question(question, paper_id)
                except Exception as e:
                    print(f"Error importing question {question.get('id')}: {str(e)}")

def import_all_files(base_dir: str, db_path: str):
    """Import all JSON files from the directory structure"""
    importer = DatabaseImporter(db_path)
    
    # Walk through all directories
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('processed.json'):
                file_path = os.path.join(root, file)
                print(f"Processing: {file_path}")
                try:
                    importer.process_json_file(file_path)
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")

if __name__ == "__main__":
    # Usage example
    BASE_DIR = "files/QA/ET"  # Your JSON files base directory
    DB_PATH = "quiz_database_cleaned.sqlite3"
    
    import_all_files(BASE_DIR, DB_PATH)