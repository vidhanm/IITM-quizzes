import json

# Read the JSON file
with open('cleaned_courses.json', 'r') as file:
    courses = json.load(file)

# Create array of [id, course_name] pairs
course_array = [[course['id'], course['course_name']] for course in courses]

# Print the array in a readable format
print("Course Array:")
print("[ ID  |  Course Name ]")
print("-" * 50)
for course in course_array:
    print(f"[ {course[0]:<3} | {course[1]} ]")

# Optionally, save the array to a new file
with open('course_array.json', 'w') as file:
    json.dump(course_array, file, indent=2)
print("\nArray saved to course_array.json") 