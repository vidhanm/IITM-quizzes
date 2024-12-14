import sqlite3
import json
import glob
import os

def create_database():
    """Create the database schema"""
    # Get absolute path for database
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, 'quiz_database1.sqlite3')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create question_papers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS question_papers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        file_path TEXT UNIQUE NOT NULL,
        total_score REAL,
        course_id INTEGER,
        uuid TEXT UNIQUE
    )
    ''')

    # Create questions table with explanation field
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY,
        exam_id INTEGER,
        question_paper_id INTEGER,
        question_number INTEGER,
        question_text TEXT,
        question_image TEXT,
        question_type TEXT,
        explanation TEXT,  -- Added explanation field
        total_mark REAL,
        parent_question_id INTEGER NULL,
        uuid TEXT,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (question_paper_id) REFERENCES question_papers(id),
        FOREIGN KEY (parent_question_id) REFERENCES questions(id)
    )
    ''')

    # Create options table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS options (
        id INTEGER PRIMARY KEY,
        question_id INTEGER,
        option_text TEXT,
        option_image TEXT,
        score REAL,
        is_correct INTEGER,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (question_id) REFERENCES questions(id)
    )
    ''')

    # Add answers table for non-MCQ questions
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER,
        parent_question_id INTEGER NULL,  -- Added for parent-child relationship
        value_start TEXT,
        value_end TEXT,
        answer_type TEXT,
        response_type TEXT,
        explanation TEXT,  -- Added explanation field
        FOREIGN KEY (question_id) REFERENCES questions(id),
        FOREIGN KEY (parent_question_id) REFERENCES questions(id)  -- Links to parent question
    )
    ''')

    conn.commit()
    conn.close()

# def insert_question_paper(cursor, paper_data):
#     """Insert a question paper into the database"""
#     cursor.execute('''
#     INSERT OR REPLACE INTO question_papers 
#     (id, exam_id, total_score, duration, question_paper_name, 
#      question_paper_description, uuid, year, created_at, updated_at)
#     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#     ''', (
#         paper_data['id'],
#         paper_data['exam_id'],
#         paper_data['total_score'],
#         paper_data['duration'],
#         paper_data['question_paper_name'],
#         paper_data['question_paper_description'],
#         paper_data['uuid'],
#         paper_data['year'],
#         paper_data['created_at'],
#         paper_data['updated_at']
#     ))

def insert_question_paper(cursor, file_path: str):
    """Insert question paper into database"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            questions = data['props']['question_paper']['questions']
            
        # Calculate total score
        total_score = sum(float(q['total_mark']) for q in questions)
        
        # Get course_id from first question
        course_id = next((q['course_id'] for q in questions if q.get('course_id')), None)
        
        # Extract title from file path
        title = os.path.basename(file_path).split('_')[1:3]
        title = ' '.join(title)
        
        # Get UUID from first question
        uuid = questions[0].get('uuid') if questions else None

        cursor.execute("""
            INSERT OR IGNORE INTO question_papers 
            (title, file_path, total_score, course_id, uuid)
            VALUES (?, ?, ?, ?, ?)
        """, (title, file_path, total_score, course_id, uuid))
        
        return cursor.lastrowid
        
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return None

def insert_question(cursor, question_data):
    """Insert a question and its answer (if applicable) into the database"""
    cursor.execute('''
    INSERT OR REPLACE INTO questions 
    (id, exam_id, question_paper_id, question_number, question_text,
     question_image, question_type, total_mark, parent_question_id,
     uuid, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        question_data['id'],
        question_data['exam_id'],
        question_data['question_paper_id'],
        question_data['question_number'],
        question_data['question_text_1'],
        question_data['question_image_1'],
        question_data['question_type'],
        question_data['total_mark'],
        question_data['parent_question_id'],
        question_data['uuid'],
        question_data['created_at'],
        question_data['updated_at']
    ))

    # For SA (Short Answer) type questions, insert into answers table
    if question_data['question_type'] == 'SA':
        cursor.execute('''
        INSERT OR REPLACE INTO answers
        (question_id, parent_question_id, value_start, value_end, answer_type, response_type)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            question_data['id'],
            question_data.get('parent_question_id'),
            question_data['value_start'],
            question_data['value_end'],
            question_data['answer_type'],
            question_data['response_type']
        ))

def insert_option(cursor, option_data, question_id):
    """Insert an option into the database"""
    cursor.execute('''
    INSERT OR REPLACE INTO options 
    (id, question_id, option_text, option_image, score,
     is_correct, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        option_data['id'],
        question_id,
        option_data['option_text'],
        option_data['option_image'],
        option_data['score'],
        1 if option_data['is_correct'] else 0,  # Convert boolean to integer
        option_data['created_at'],
        option_data['updated_at']
    ))

def process_json_files(directory_path):
    """Process JSON files in the given directory"""
    # Get absolute paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, 'quiz_database1.sqlite3')
    abs_directory_path = os.path.join(BASE_DIR, directory_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Use recursive glob to find JSON files in all subdirectories
    json_files = glob.glob(os.path.join(abs_directory_path, "**/*.json"), recursive=True)
    
    print(f"Looking for JSON files in: {abs_directory_path}")
    print(f"Found {len(json_files)} total JSON files")
    
    # Filter files to process
    files_to_process = []
    for file_path in json_files:
        # Only process files that match our expected pattern and structure
        if (not '_comprehensive_processed.json' in file_path and 
            not 'course_array.json' in file_path and
            not 'cleaned_courses.json' in file_path):
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Check if file has the expected structure
                    if ('props' in data and 
                        'question_paper' in data['props'] and 
                        'questions' in data['props']['question_paper']):
                        files_to_process.append(file_path)
                        print(f"Will process file: {file_path}")
            except Exception as e:
                print(f"Error checking file {file_path}: {str(e)}")
    
    print(f"\nFound {len(files_to_process)} files to process")
    
    # Process each file
    for file_path in files_to_process:
        try:
            # Insert question paper first and get its ID
            paper_id = insert_question_paper(cursor, file_path)
            
            if paper_id:  # Only proceed if paper was inserted successfully
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                question_paper = data['props']['question_paper']
                
                # Insert questions and their options/answers
                for question in question_paper['questions']:
                    # Update question's paper ID to match our newly inserted paper
                    question['question_paper_id'] = paper_id
                    insert_question(cursor, question)
                    
                    if question['question_type'] == 'MCQ' and 'options' in question:
                        for option in question['options']:
                            insert_option(cursor, option, question['id'])
                
                conn.commit()
                print(f"Successfully processed: {file_path}")
                
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            conn.rollback()
    
    conn.close()

def main():
    """Main function to create database and process files"""
    print("Creating database and tables...")
    create_database()
    
    print("\nProcessing JSON files...")
    # Process JSON files using relative path
    json_directory = "QA/ET"  # This will be made absolute in process_json_files
    process_json_files(json_directory)

if __name__ == "__main__":
    main()