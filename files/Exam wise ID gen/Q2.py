import requests
import json
import os
import time

# Load the course array
with open('course_array.json', 'r') as file:
    course_array = json.load(file)

def Q2(course_id, course_name):
    '''
    course_id: id of the course
    course_name: name of the course

    This function helps to get the questions paper IDs of Quiz 2 courses
    
    '''
    url = "https://quizpractice.space/api/get-questions-paper-by-exam"

    payload = {
        "course_id": course_id,
        "year": "all",
        "exam_id": "eyJpdiI6IjJHMEhMWi9idDdRMW5MOEo2VC9hOHc9PSIsInZhbHVlIjoiU1hRYzB5WUVCeHUvNElPazhLNUlwUT09IiwibWFjIjoiNGNkMTY2NjQ4OTA1MzFkMjdiYTRkNzVmZDc3MjFiZTM3OGQ1NTFjOTI5YjMyZTYwMjczOGIzYWFiODdmZDYyMSIsInRhZyI6IiJ9"
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://quizpractice.space",
        "Referer": "https://quizpractice.space/exam/1948ee72-5c62-4816-97c8-7d662330a220"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        #print(f"Response: {response.text}")
        
        if response.status_code == 200:
            folder_name = 'Q2'  # Changed to Q2
            os.makedirs(folder_name, exist_ok=True)
            
            safe_course_name = course_name.replace(' ', '_')
            file_path = os.path.join(folder_name, f'Q2_{safe_course_name}.json')  # Changed to Q2
            with open(file_path, 'w') as file:
                json.dump(response.json(), file, indent=2)
            print(f"Response saved to {file_path}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

# Now you can iterate over the courses
for course_id, course_name in course_array:
    Q2(course_id, course_name)
    time.sleep(1)  # 1 second delay between requests