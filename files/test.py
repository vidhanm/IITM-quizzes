import sqlite3
import os

def update_question_explanations():
    """Update explanations for questions from the cleaned database"""
    source_db_path = ('files/quiz_database_cleaned.sqlite3')
    target_db_path = ('files/quiz_database1.sqlite3')
    
    # First verify both databases exist
    if not os.path.exists(source_db_path):
        print(f"Error: Source database not found at {source_db_path}")
        return
    if not os.path.exists(target_db_path):
        print(f"Error: Target database not found at {target_db_path}")
        return

    # Connect to both databases
    source_conn = sqlite3.connect(source_db_path)
    target_conn = sqlite3.connect(target_db_path)
    
    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()
    
    try:
        # Verify tables exist in both databases
        source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='questions'")
        if not source_cursor.fetchone():
            print("Error: 'questions' table not found in source database")
            return

        target_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='questions'")
        if not target_cursor.fetchone():
            print("Error: 'questions' table not found in target database")
            return

        # Rest of your code...
        target_cursor.execute('''
        SELECT id 
        FROM questions
        ''')
        target_question_ids = target_cursor.fetchall()
        
        print(f"Found {len(target_question_ids)} questions in target database")
        updated_count = 0
        
        #For each target question ID, find and update its explanation
        for (question_id,) in target_question_ids:
            source_cursor.execute('''
            SELECT explanation 
            FROM questions 
            WHERE id = ? AND explanation IS NOT NULL
            ''', (question_id,))
            
            result = source_cursor.fetchone()
            
            if result:
                explanation = result[0]
                target_cursor.execute('''
                UPDATE questions 
                SET explanation = ? 
                WHERE id = ?
                ''', (explanation, question_id))
                updated_count += 1
                
                if updated_count % 100 == 0:
                    print(f"Updated {updated_count} questions so far...")
        
        target_conn.commit()
        print(f"Successfully updated {updated_count} questions with explanations")
        
    except Exception as e:
        print(f"Error updating explanations: {str(e)}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Source DB path: {os.path.abspath(source_db_path)}")
        print(f"Target DB path: {os.path.abspath(target_db_path)}")
        target_conn.rollback()
    finally:
        source_conn.close()
        target_conn.close()

def main():
    update_question_explanations()

if __name__ == "__main__":
    main()
