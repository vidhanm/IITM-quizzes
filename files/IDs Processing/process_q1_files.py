import json
import os

def load_course_array():
    with open('course_array.json', 'r') as file:
        return json.load(file)

def get_safe_filename(course_name):
    return f"Q1_{course_name.replace(' ', '_')}.json"

def process_q1_files():
    # Load course array
    course_array = load_course_array()
    
    # Create results directory if it doesn't exist
    os.makedirs('results', exist_ok=True)
    
    # Process each course
    for course_id, course_name in course_array:
        filename = get_safe_filename(course_name)
        filepath = os.path.join('Q1', filename)
        
        if os.path.exists(filepath):
            with open(filepath, 'r') as file:
                data = json.load(file)
                
                # Extract required information
                course_info = {
                    'course_id': course_id,
                    'course_name': course_name,
                    'papers': [{
                        'uuid': paper['uuid'],
                        'year': paper['year'],
                        'description': paper['question_paper_description']
                    } for paper in data]
                }
                
                # Save to results folder
                result_filename = f"Q1_{course_name.replace(' ', '_')}_info.json"
                with open(os.path.join('results', result_filename), 'w') as outfile:
                    json.dump(course_info, outfile, indent=2)
                print(f"Processed {course_name}")

if __name__ == "__main__":
    process_q1_files() 