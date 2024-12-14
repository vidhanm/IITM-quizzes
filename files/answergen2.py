import json
import os
import glob
from img_down import download_image
from loadimg import load_img
import base64
from huggingface_hub import InferenceClient

def prepare_image(image_url):
    """
    Prepare image for AI analysis by converting to base64
    Returns base64 encoded image or None if no image
    """
    if not image_url:
        return None
    try:
        full_image_url = "https://quizpractice.space/read-image?file=" + image_url
        return load_img(full_image_url, output_type="base64")
    except Exception as e:
        print(f"Error loading image {image_url}: {e}")
        return None

def generate_explanation(client, question_details):
    """
    Generate comprehensive explanation based on question type and available information
    """
    try:
        # Prepare images
        images = []
        question_image = prepare_image(question_details['question_image_url'][0] 
                                       if question_details.get('question_image_url') 
                                       else None)
        
        if question_image:
            images.append({
                "type": "image_url",
                "image_url": {"url": question_image}
            })
        
        # Identify the correct option
        correct_option = next((option for option in question_details['options'] if option['is_correct']), None)
        
        if not correct_option:
            return "No correct option found in the question."
        
        # Prepare options text with emphasis on the correct option
        options_text = "\nOptions:\n" + "\n".join([
            f"{option['text']} {'(CORRECT OPTION)' if option['is_correct'] else ''}" 
            for option in question_details['options']
        ])
        
        # Construct messages for AI
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""Question: {question_details.get('question_text', 'No text provided')}
{options_text}

Focus on explaining the CORRECT OPTION: {correct_option['text']}

Please provide a comprehensive explanation that:
1. Clearly explains why the option '{correct_option['text']}' is the correct answer
2. Break down the reasoning step-by-step
3. Explain why other options are incorrect
4. Provide educational insights that help understand the underlying concepts

Your explanation should be thorough and illuminate the reasoning behind the correct answer."""
                    }
                ] + (images if images else [])
            }
        ]
        
        # Generate explanation
        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
            messages=messages,
            max_tokens=1000
        )
        
        return completion.choices[0].message.content
    
    except Exception as e:
        return f"Error generating explanation: {str(e)}"

def process_question_paper(input_file):
    # Initialize client
    client = InferenceClient(
        base_url="https://api.together.xyz", 
        api_key="fe13a6fbe19263c3e44c7a7f6661f0eb4a825dec7a405b329b911f291f62e8cf"
    )
    
    # Read the input JSON file
    with open(input_file, 'r') as file:
        data = json.load(file)
   
    # Create a new list to store processed questions
    processed_questions = []
   
    # Process each question
    for question in data['props']['question_paper']['questions']:
        print("in question")
        processed_question = {
            'id': question['id'],
            'question_text': question.get('question_text_1', '') or question.get('question_text_2', '') or question.get('question_text', ''),
            'question_type': question['question_type'],
            'question_image_url': question['question_image_url'],
            'total_mark': question['total_mark'],
            'uuid': question['uuid'],
            'course_id': question['course_id'],
            'options': [],
            'comprehensive_explanation': ''
        }
       
        # Process options
        for option in question.get('options', []):
            print("in option")
            processed_option = {
                'id': option['id'],
                'question_id': option['question_id'],
                'text': option['option_text'],
                'is_correct': bool(option['is_correct']),
                'option_image': option['option_image'],
                'option_image_url': option['option_image_url'],
                'score': option['score']
            }
            processed_question['options'].append(processed_option)
        
        # Generate comprehensive explanation
        processed_question['comprehensive_explanation'] = generate_explanation(
            client, 
            processed_question
        )
       
        processed_questions.append(processed_question)
   
    # Write processed questions to a new JSON file
    output_file = os.path.splitext(input_file)[0] + '_comprehensive_processed.json'
    with open(output_file, 'w') as file:
        json.dump(processed_questions, file, indent=2)
   
    print(f"Processed questions with comprehensive explanations saved to {output_file}")

def process_all_question_papers(directories):
    """
    Process all JSON files in multiple directories
    """
    for directory in directories:
        print(f"Processing files in directory: {directory}")
        for file_path in glob.glob(os.path.join(directory, '*.json')):
            print(f"Processing file: {file_path}")
            process_question_paper(file_path)

# Alternative usage - process all subdirectories
base_directory = 'QA/ET'
directories = [os.path.join(base_directory, d) for d in os.listdir(base_directory) 
              if os.path.isdir(os.path.join(base_directory, d))]
process_all_question_papers(directories)