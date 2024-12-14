import requests
import json
import os
import time
# Load the course array
with open('course_array.json', 'r') as file:
    course_array = json.load(file)

def Q1(course_id,course_name):
    '''
    course_id: id of the course
    course_name: name of the course

    This function helps to get the questions paper IDs of Quiz 1 courses
    '''
    url = "https://quizpractice.space/api/get-questions-paper-by-exam"

    payload = {
        "course_id": course_id,
        "year": "all",
        "exam_id": "eyJpdiI6IlBUbXpWa0Q2MWtFNVozaUZ6ejlvNVE9PSIsInZhbHVlIjoiamxUODMyWjROTHNhYUVsb1paZjBoUT09IiwibWFjIjoiZDQ2OWZhMDI0YWNlNDZkZWVhNjI5OWZmNDc2MzBhMDYwOGQyNGI3MjY4ZGRlMjdkYzhiMDQ4Nzk4YjAyYjFiZiIsInRhZyI6IiJ9"
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://quizpractice.space",
        "Referer": "https://quizpractice.space/exam/9251bc3a-e33e-45e0-bcf0-b16a0ea5b5fa"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            folder_name = 'Q1'
            os.makedirs(folder_name, exist_ok=True)
            
            safe_course_name = course_name.replace(' ', '_')
            file_path = os.path.join(folder_name, f'Q1_{safe_course_name}.json')
            with open(file_path, 'w') as file:
                json.dump(response.json(), file, indent=2)
            print(f"Response saved to {file_path}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

# Now you can iterate over the courses
for course_id, course_name in course_array:
    Q1(course_id,course_name)
    time.sleep(1)