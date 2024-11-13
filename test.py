import json

def clean_courses(json_file):
    try:
        # Load the JSON data
        with open(json_file, 'r') as file:
            courses = json.load(file)
        
        # Clean each course object
        cleaned_courses = []
        for course in courses:
            cleaned_course = {
                'id': course['id'],
                'course_name': course['course_name'],
                'course_code': course['course_code'],
                'uuid': course['uuid'],
                'label': course['label']
            }
            cleaned_courses.append(cleaned_course)
        
        # Save the cleaned courses array to a new JSON file
        with open('cleaned_courses.json', 'w') as file:
            json.dump(cleaned_courses, file, indent=2)
            
        print("Cleaned courses saved to cleaned_courses.json")
        
    except Exception as e:
        print(f"Error processing JSON: {e}")

# Use the function
clean_courses('courses.json')
