import sqlite3
from huggingface_hub import InferenceClient
import os
from PIL import Image

def get_db_connection():
    """Create a database connection"""
    return sqlite3.connect('files/quiz_database1.sqlite3')

def get_local_image_path(question_id, image_type='question'):
    """
    Get path to locally downloaded image
    image_type can be 'question' or 'option'
    """
    base_path = 'downloaded_images/questions'
    if image_type == 'question':
        image_path = os.path.join(base_path, f'{question_id}.jpg')
    else:
        image_path = os.path.join(base_path, f'{question_id}_{image_type}.jpg')
    
    return image_path if os.path.exists(image_path) else None

def verify_image(image_path):
    """Verify if image exists and is valid"""
    try:
        if image_path and os.path.exists(image_path):
            with Image.open(image_path) as img:
                return True
        return False
    except Exception:
        return False

def get_question_details(conn, question_id):
    """Get all details about a question including its options, answers, and images"""
    cursor = conn.cursor()
    
    # Get question details
    question = cursor.execute('''
        SELECT id, question_text, question_type 
        FROM questions 
        WHERE id = ?
    ''', (question_id,)).fetchone()
    
    if not question:
        return None
    
    # Check for question image - using question_image field from database
    question_image = cursor.execute('''
        SELECT question_image 
        FROM questions 
        WHERE id = ?
    ''', (question_id,)).fetchone()[0]
    
    question_with_image = list(question) + [question_image if question_image else None]
        
    # Get options if they exist
    options = cursor.execute('''
        SELECT id, option_text, is_correct, score, option_image
        FROM options
        WHERE question_id = ?
    ''', (question_id,)).fetchall()
    
    # Get answers if they exist - modified to match your schema
    answers = cursor.execute('''
        SELECT value_start, value_end, answer_type, response_type, explanation
        FROM answers
        WHERE question_id = ?
    ''', (question_id,)).fetchall()
    
    # Get parent question if it's a comprehensive question
    parent_question = None
    if question[2] == 'COMPREHENSIVE':
        parent_result = cursor.execute('''
            SELECT q.id, q.question_text, q.question_image
            FROM questions q
            WHERE q.id = (
                SELECT parent_question_id
                FROM questions
                WHERE id = ?
            )
        ''', (question_id,)).fetchone()
        
        if parent_result:
            parent_question = list(parent_result)
    
    return {
        'question': question_with_image,
        'options': options,
        'answers': answers,
        'parent_question': parent_question
    }

def generate_explanation(client, question_details):
    """Generate comprehensive explanation based on question type and available information"""
    try:
        # Debug logging
        print("\nDEBUG - Question Details:")
        print(f"Question: {question_details['question']}")
        print(f"Options: {question_details['options']}")
        print(f"Answers: {question_details['answers']}")
        print(f"Parent Question: {question_details['parent_question']}")
        
        question_id, question_text, question_type, question_image = question_details['question']
        options = question_details['options']
        answers = question_details['answers']
        parent_question = question_details['parent_question']
        
        # Build context including images
        context_parts = []
        
        # Debug logging for API response
        print("\nDEBUG - Sending to API:")
        print(f"Question Type: {question_type}")
        
        if parent_question:
            parent_text = f"This is a sub-question of: {parent_question[1]}"
            if parent_question[2]:  # parent question image
                parent_text += f"\n[Image Reference: {parent_question[2]}]"
            context_parts.append(parent_text)
        
        # Add question image reference if exists
        question_context = question_text if question_text else ""  # Ensure question_text is not None
        if question_image:
            question_context += f"\n[Image Reference: {question_image}]"
        
        # Prepare prompt based on question type
        if question_type in ['MCQ', 'MSQ'] and options:
            correct_options = [opt for opt in options if opt[2]]
            if not correct_options:
                return "Question appears to be misconfigured - no correct options marked."
            
            options_text = "\n".join([
                f"- {opt[1]}" + (" (CORRECT)" if opt[2] else "") +
                (f" [Image: {opt[4]}]" if opt[4] else "")
                for opt in options
            ])
            
            prompt = f"""Question ID: {question_id}
Type: {question_type}
Question: {question_context}
Options:
{options_text}

Please provide a clear explanation for why the marked options are correct and others are incorrect."""

        elif question_type in ['SA', 'COMPREHENSIVE'] and answers:
            print("Processing SA/COMPREHENSIVE type question")
            print(f"Number of answer entries: {len(answers)}")
            
            answer_details = []
            for ans in answers:
                value_start, value_end, answer_type, response_type, explanation = ans
                if value_start and value_end:
                    answer_details.append(f"Acceptable range: {value_start} to {value_end}")
                    print(f"Answer has range: {value_start} to {value_end}")
                if answer_type:
                    answer_details.append(f"Answer type: {answer_type}")
                if response_type:
                    answer_details.append(f"Response type: {response_type}")
                if explanation:
                    answer_details.append(f"Given explanation: {explanation}")
            
            answer_text = "\n".join(answer_details) if answer_details else "No answer details available"
            
            prompt = f"""Question ID: {question_id}
Type: {question_type}
Question: {question_context}
Answer Information:
{answer_text}

Please provide a clear explanation for this answer, including why the given range or response is appropriate."""

        else:
            return "Unable to generate explanation - insufficient question data"

        print(f"\nSending prompt for question {question_id}...")
        
        # Generate explanation using AI
        messages = [{
            "role": "user",
            "content": prompt
        }]
        
        # Debug API response
        print("\nDEBUG - API Response:")
        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
            messages=messages,
            max_tokens=1000
        )
        print(f"Raw completion: {completion}")
        print(f"Completion type: {type(completion)}")
        
        # Modified response handling
        if hasattr(completion, 'choices') and completion.choices:
            if hasattr(completion.choices[0], 'message'):
                message = completion.choices[0].message
                if hasattr(message, 'content'):
                    explanation = message.content
                else:
                    explanation = str(message)
            else:
                explanation = str(completion.choices[0])
        else:
            explanation = "I don't have"
            
        # Add debug printing for the explanation
        print("\nDEBUG - Generated Explanation:")
        print("-" * 50)
        print(explanation)
        print("-" * 50)
        
        return explanation

    except Exception as e:
        print(f"\nDEBUG - Error Details:")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return f"Error generating explanation: {str(e)}"

def update_explanations():
    """Update explanations for all questions in the database"""
    try:
        print("Initializing explanation update process...")
        
        # Debug API client
        client = InferenceClient(
            base_url="https://api.together.xyz",
            api_key="fe13a6fbe19263c3e44c7a7f6661f0eb4a825dec7a405b329b911f291f62e8cf"
        )
        print("\nDEBUG - API Client initialized")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get questions with various error messages or NULL explanation
        questions = cursor.execute('''
            SELECT id, question_type,
                   (SELECT COUNT(*) FROM options o WHERE o.question_id = q.id) as option_count,
                   (SELECT COUNT(*) FROM answers a WHERE a.question_id = q.id) as answer_count
            FROM questions q
            WHERE explanation IS NULL
               OR explanation LIKE '%Error generating explanation%'
               OR explanation LIKE '%Unable to generate explanation%'
               OR explanation LIKE '%dict%'
               OR explanation LIKE '%unsupported operand%'
               OR explanation = 'No correct option found in the question.'
        ''').fetchall()
        
        print(f"\nProcessing {len(questions)} questions...")
        
        for (question_id, q_type, opt_count, ans_count) in questions:
            print(f"\n{'='*30}")
            print(f"Processing question {question_id}")
            
            question_details = get_question_details(conn, question_id)
            if not question_details:
                print(f"Warning: Could not fetch details for question {question_id}")
                continue
            
            explanation = generate_explanation(client, question_details)
            print(f"Explanation length: {len(explanation)} characters")
            
            cursor.execute('''
                UPDATE questions 
                SET explanation = ?
                WHERE id = ?
            ''', (explanation, question_id))
            
            conn.commit()
            print(f"Updated explanation for question {question_id}")
        
        conn.close()
        print("\nFinished updating explanations successfully!")
        
    except Exception as e:
        print(f"Error in update_explanations: {str(e)}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    update_explanations()  # Process all questions without limit
 