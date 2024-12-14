import os
import json
from answergen2 import process_question_paper

def process_et_json_file(file_path):
    """Process a single JSON file from the ET folder using answergen2"""
    try:
        # Use the process_question_paper function from answergen2.py
        process_question_paper(file_path)
        return True
        
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
        return False

def process_et_folder(et_folder_path):
    """Process all JSON files in the ET folder and its subdirectories"""
    processed_files = 0
    failed_files = 0
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(et_folder_path):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                print(f"\nProcessing: {file_path}")
                
                if process_et_json_file(file_path):
                    processed_files += 1
                    print(f"Successfully processed: {file_path}")
                else:
                    failed_files += 1
                    print(f"Failed to process: {file_path}")
    
    return processed_files, failed_files

def main():
    # Specify the path to your ET folder
    et_folder_path = "QA/ET"
    
    print(f"Starting to process all JSON files in {et_folder_path} and its subdirectories...")
    
    # Process all JSON files
    processed, failed = process_et_folder(et_folder_path)
    
    # Print results
    print(f"\nProcessing complete!")
    print(f"Successfully processed files: {processed}")
    print(f"Failed files: {failed}")

if __name__ == "__main__":
    main()