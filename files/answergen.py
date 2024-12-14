from huggingface_hub import InferenceClient
import json
import base64
import requests
from img_down import download_image
from loadimg import load_img
import os
import glob 


def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


def get_image_explanation(image_url):
    try:
        
        my_b64_img = load_img(image_url ,output_type="base64" ) 

        client = InferenceClient(base_url="https://api.together.xyz",api_key="fe13a6fbe19263c3e44c7a7f6661f0eb4a825dec7a405b329b911f291f62e8cf")
        
        messages = [
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text", 
                        "text": "Provide a detailed explanation of this image in the context of an AI or state space problem."
                    },
                    {
                        "type": "image_url",
				"image_url": {
					"url": my_b64_img
                    }
                    }
                ]
            }
        ]
        
        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo", 
            messages=messages, 
            max_tokens=500
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error generating explanation: {str(e)}"

def process_question_paper(input_file):
    # Read the input JSON file
    with open(input_file, 'r') as file:
        data = json.load(file)
    
    # Create a new list to store processed questions
    processed_questions = []
    
    # Process each question
    for question in data['props']['question_paper']['questions']:
        processed_question = {
            'id': question['id'],
            'question_text': question.get('question_text_1', '') or question.get('question_text_2', ''),
            'question_type': question['question_type'],
            "question_image_url" : question['question_image_url'], 
            'total_mark' : question['total_mark'],
            'uuid' : question['uuid'],
            'course_id' : question['course_id'],
            'options': [],
            'answer_explanation': ''
        }
        
        # Add options
        for option in question.get('options', []):
            processed_option = {
                'id': option['id'],
                'question_id' : option['question_id'],
                'text': option['option_text'],
                'is_correct': bool(option['is_correct']),
                'option_image' : option['option_image'],
                'score' : option['score'],
                'option_image_url' : option['option_image_url']

            }
            processed_question['options'].append(processed_option)
        
        # Check for images and generate explanations
        if question.get('question_image_1'):
            image_url = question['question_image_url'][0]  # Assuming first image URL
            image_url = "https://quizpractice.space/read-image?file="+image_url
            print(image_url)
            processed_question['answer_explanation'] = get_image_explanation(image_url)
        
        processed_questions.append(processed_question)
    
    # Write processed questions to a new JSON file
    # Write processed questions to a new JSON file
    output_file = os.path.splitext(input_file)[0] + '_processed.json'
    with open(output_file, 'w') as file:
        json.dump(processed_questions, file, indent=2)
    
    print(f"Processed questions saved to {output_file}")

def process_all_question_papers(directory):
    for file_path in glob.glob(os.path.join(directory, '*.json')):
        process_question_paper(file_path)
# Usage

directory = 'QA/ET/ET_BDM'
process_all_question_papers(directory)