import requests
import json
import os
import time
from pathlib import Path

def safe_filename(text):
    """Convert text to a safe filename"""
    return "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in text)

def process_course_file(filepath, folder_prefix):
    with open(filepath, 'r') as file:
        course_data = json.load(file)
        course_id = course_data['course_id']
        course_name = course_data['course_name']
        
        # Create folder structure with prefix (Q1, Q2, etc)
        qa_folder = Path(f'QA/{folder_prefix}/{folder_prefix}_{course_name}')
        qa_folder.mkdir(parents=True, exist_ok=True)
        
        for paper in course_data['papers']:
            try:
                uuid = paper['uuid']
                description = paper['description']
                year = paper['year']
                
                # Generate safe filename with folder prefix
                filename = safe_filename(f"{folder_prefix}_{course_name}_{year}_{description}")
                
                # Make API request
                url = f"https://quizpractice.space/question-paper/practise/{course_id}/{uuid}"
                headers = {
                    "X-Inertia": "true",
                    "X-Inertia-Version": "4c701bf80a81eb2f8b458185f6f466cc"
                }
                
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                
                # Save response
                output_path = qa_folder / f"{filename}.json"
                with open(output_path, 'w') as outfile:
                    json.dump(response.json(), outfile, indent=2)
                
                print(f"Processed: {folder_prefix}_{course_name} - {description}")
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"Error processing {folder_prefix}_{course_name} - {uuid}: {str(e)}")

def main():
    # Process both Q1 and Q2 results
    for folder_prefix in ['Q1', 'Q2','ET']:
        results_folder = Path(f'results/{folder_prefix}')
        if results_folder.exists():
            for file in results_folder.glob('*.json'):
                print(f"\nProcessing {file.name}")
                process_course_file(file, folder_prefix)

if __name__ == "__main__":
    main()