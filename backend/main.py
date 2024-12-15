from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
from database import get_db
import os
app = Flask(__name__, 
    static_folder='dist',
    static_url_path=''
)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'



@app.route('/assets/<path:path>')
def serve_assets(path):
    return send_from_directory(f"{app.static_folder}/assets", path)

@app.route('/', defaults={'path': ''})

@app.route('/<path:path>')
def serve_react_app(path):
    try:
        return send_from_directory(app.static_folder, path)
    except:
        return send_from_directory(app.static_folder, 'index.html')
    
@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({"error": "API endpoint not found"}), 404
    
    return serve_react_app('')
    
@app.after_request
def after_request(response):
    # Ensure CORS headers are set for all responses
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.route("/api/courses")
def get_courses():
    try:
        ("Attempting to connect to database...")  # Debug log
        with get_db() as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM courses")
            courses = cursor.fetchall()
            return jsonify([dict(course) for course in courses])
    except Exception as e:
        print("Database error:", str(e))  # Debug log
        return jsonify({"error": str(e)}), 500

@app.route("/api/courses/<int:course_id>/papers")
def get_course_papers(course_id):
    try:
        with get_db() as db:
            cursor = db.cursor()
            cursor.execute("""
                SELECT qp.id, qp.file_path, qp.total_score
                FROM question_papers qp
                WHERE qp.course_id = ?
            """, [course_id])
            papers = cursor.fetchall()
            
            # Process file paths before sending to frontend
            def get_file_name(file_path):
                # Split by both forward and backward slashes to handle different path formats
                parts = file_path.replace('\\', '/').split('/')
                # Get the last meaningful part
                for part in reversed(parts):
                    #print(part)
                    if part.strip():  # Find first non-empty part from the end
                        return part
                return file_path
            
            return jsonify([{
                'id': paper['id'],
                'file_path': get_file_name(paper['file_path']),  # Send only the filename
                'total_score': paper['total_score']
            } for paper in papers])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/papers/<int:paper_id>")
def get_paper_questions(paper_id):
    with get_db() as db:
        cursor = db.cursor()
        
        # Get paper details
        cursor.execute("SELECT * FROM question_papers WHERE id = ?", (paper_id,))
        paper = cursor.fetchone()
        #print("Paper:", paper)
        
        if not paper:
            return jsonify({"error": "Paper not found"}), 404
        
        # Process the file path to get clean filename
        def get_file_name(file_path):
            # Split by both forward and backward slashes to handle different path formats
            parts = file_path.replace('\\', '/').split('/')
            # Get the last meaningful part
            for part in reversed(parts):
                if part.strip():  # Find first non-empty part from the end
                    return part
            return file_path
        
        # Update paper title with clean filename
        paper_dict = dict(paper)
        paper_dict['title'] = get_file_name(paper_dict['file_path'])
        
        # Get questions with simple query
        cursor.execute("""
            SELECT * FROM questions 
            WHERE question_paper_id = ?
        """, (paper_id,))
        
        questions = cursor.fetchall()
        #print("Questions:", questions)
        
        # For each question, get its options or answer range
        questions_with_options = []
        for q in questions:
            question_data = dict(q)
            
            if q['question_type'] == 'SA':
                # Get answer range for SA questions
                cursor.execute("""
                    SELECT value_start, value_end 
                    FROM answers 
                    WHERE question_id = ?
                """, (q['id'],))
                answer = cursor.fetchone()
                question_data['options'] = dict(answer) if answer else None
            else:
                # Get options for MCQ questions
                cursor.execute("""
                    SELECT id, option_text as text, is_correct 
                    FROM options 
                    WHERE question_id = ?
                """, (q['id'],))
                options = cursor.fetchall()
                question_data['options'] = [dict(opt) for opt in options]
            
            questions_with_options.append(question_data)
        
        return jsonify({
            "paper": paper_dict,  # Use the modified paper dictionary
            "questions": questions_with_options
        })

@app.route("/api/papers/<int:paper_id>/submit", methods=['POST'])
def submit_paper(paper_id):
    answers = request.json
    try:
        with get_db() as db:
            cursor = db.cursor()
            
            results = []
            total_score = 0
            
            # Get all questions for this paper
            cursor.execute("""
                SELECT id, question_type, total_mark, explanation
                FROM questions 
                WHERE question_paper_id = ?
            """, [paper_id])
            questions = cursor.fetchall()
            
            for question in questions:
                question_id = question['id']
                user_answer = answers.get(str(question_id))
                
                if user_answer is None:
                    # Skip questions that weren't answered
                    results.append({
                        "question_id": question_id,
                        "correct": False,
                        "score": 0,
                        "explanation": "No answer provided."
                    })
                    continue
                
                if question['question_type'] == 'SA':
                    # Handle Short Answer questions
                    cursor.execute("""
                        SELECT value_start, value_end
                        FROM answers
                        WHERE question_id = ?
                    """, [question_id])
                    answer_range = cursor.fetchone()
                    
                    try:
                        numeric_answer = float(user_answer)
                        is_correct = (
                            answer_range['value_start'] <= numeric_answer <= answer_range['value_end']
                        ) if answer_range else False
                        score = question['total_mark'] if is_correct else 0
                    except (ValueError, TypeError):
                        is_correct = False
                        score = 0
                        
                else:
                    # Handle MCQ questions
                    cursor.execute("""
                        SELECT is_correct, score
                        FROM options
                        WHERE id = ? AND question_id = ?
                    """, [user_answer, question_id])
                    option = cursor.fetchone()
                    
                    is_correct = option['is_correct'] if option else False
                    score = option['score'] if option else 0
                
                results.append({
                    "question_id": question_id,
                    "correct": is_correct,
                    "score": score,
                    "explanation": question['explanation'] or "No explanation available."
                })
                
                total_score += score
            
            return jsonify({
                "total_score": total_score,
                "results": results
            })
            
    except Exception as e:
        print("Submission error:", str(e))  # For debugging
        return jsonify({"error": str(e)}), 500

@app.route("/api/debug/database")
def debug_database():
    try:
        with get_db() as db:
            cursor = db.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            result = {"tables": {}}
            
            for table in tables:
                table_name = table['name']
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
                result["tables"][table_name] = [dict(row) for row in cursor.fetchall()]
            
            return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/images/<string:type>/<int:id>")
def serve_image(type, id):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(BASE_DIR, 'downloaded_images', type)
    
    # Adjust filename format based on type
    if type == 'questions':
        filename = f"question_{id}.png"  # For question images
    elif type == 'options':
        filename = f"option_{id}.png"    # For option images
    else:
        filename = f"{id}.png"           # For any other type
    
    full_path = os.path.join(image_path, filename)
    #print(f"Looking for image at: {full_path}")  # Debug log
    
    if os.path.exists(full_path):
        return send_from_directory(image_path, filename)
    
    return "Image not found", 404

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)