import json
from pathlib import Path

def extract_mcqs(filepath):
    with open(filepath, 'r') as file:
        data = json.load(file)
        
    mcqs = []
    questions = data['props']['question_paper']['questions']
    
    for question in questions:
        if question['question_type'] == 'MCQ':
            # Initialize with default values
            mcq = {
                'question_text': question.get('question_text_1', ''),
                'question_images': question.get('question_image_url', []),
                'options': []
            }
            
            # Handle options with null checking
            for option in question.get('options', []):
                if option:  # Check if option is not None
                    opt = {
                        'text': option.get('option_text', ''),
                        'is_correct': option.get('is_correct', False)
                    }
                    mcq['options'].append(opt)
            
            # Only append MCQ if it has valid content
            if mcq['question_text'] or mcq['question_images'] or mcq['options']:
                mcqs.append(mcq)
    
    return mcqs

def save_mcqs(mcqs, input_file):
    # Create output directory if it doesn't exist
    output_dir = Path('extracted_mcqs')
    output_dir.mkdir(exist_ok=True)
    
    # Generate output filename based on input filename
    output_filename = f"MCQ_{input_file.stem}.json"
    output_path = output_dir / output_filename
    
    # Prepare data structure
    output_data = {
        'source_file': str(input_file),
        'mcq_count': len(mcqs),
        'mcqs': [
            {k: v for k, v in mcq.items() if v is not None and v != []} 
            for mcq in mcqs
        ]
    }
    
    # Save to JSON file with proper encoding
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    return output_path

def main():
    # Input filepath
    input_file = Path('QA/Q1/Q1_AI/Q1_AI_2022_2022_Oct__IIT_M_QUIZ_1_DEGREE_QPF1.json')
    
    # Extract MCQs
    mcqs = extract_mcqs(input_file)
    
    # Save MCQs to file
    output_path = save_mcqs(mcqs, input_file)
    print(f"MCQs extracted and saved to: {output_path}")
    
    # Print for verification
    for i, mcq in enumerate(mcqs, 1):
        print(f"\nMCQ {i}:")
        print(f"Question: {mcq['question_text']}")
        if mcq['question_images']:
            print(f"Images: {mcq['question_images']}")
        print("Options:")
        for opt in mcq['options']:
            correct = "✓" if opt['is_correct'] else " "
            print(f"[{correct}] {opt['text']}")

if __name__ == "__main__":
    main() 