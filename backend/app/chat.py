from flask import Blueprint, request, jsonify
import os
import json
import requests
from dotenv import load_dotenv
import logging
import base64
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
logger.debug(f"API Key configured: {'Yes' if os.getenv('OPENROUTER_API_KEY') else 'No'}")

chat_bp = Blueprint('chat', __name__)

def create_messages(context, user_query):
    """Create messages array with proper multimodal format for Optimus"""
    paper = context.get('paper', {})
    questions = context.get('questions', [])
    
    logger.debug(f"Processing user query: '{user_query}'")
    
    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": f"You are a helpful Quiz Assistant for the quiz titled \"{paper.get('title', 'Untitled Quiz')}\" with total score {paper.get('total_score', 0)}."
                }
            ]
        }
    ]
    
    # If the user hasn't asked about a specific question,
    # provide a general introduction without sending any questions
    if not any(q.lower() in user_query.lower() for q in ['question', 'q']) and not re.search(r'\b\d+\b', user_query):
        logger.debug("General query detected, sending welcome message without questions")
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": user_query
                }
            ]
        })
        return messages
    
    # Try to extract question number from user query
    question_numbers = re.findall(r'question\s*(\d+)', user_query.lower())
    # Also try to find standalone numbers
    if not question_numbers:
        standalone_numbers = re.findall(r'\b(\d+)\b', user_query.lower())
        if standalone_numbers:
            logger.debug(f"Found standalone numbers: {standalone_numbers}")
            question_numbers = standalone_numbers
            
    logger.debug(f"Extracted question numbers from user query '{user_query}': {question_numbers}")
    relevant_questions = []
    
    if question_numbers:
        # User mentioned specific question number(s)
        for q_num in question_numbers:
            q_num = int(q_num)
            logger.debug(f"Processing question number: {q_num}")
            if 1 <= q_num <= len(questions):
                question = questions[q_num - 1]
                logger.debug(f"Question {q_num} data: {question.keys() if question else 'None'}")
                relevant_questions.append(question)
                logger.debug(f"Added question {q_num} to relevant questions")
            else:
                logger.debug(f"Question number {q_num} is out of range (1-{len(questions)})")
    
    # If we couldn't identify specific questions, ask the user to be more specific
    if not relevant_questions:
        logger.debug("No relevant questions found, asking user to be more specific")
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": user_query
                }
            ]
        })
        return messages
    
    logger.debug(f"Adding {len(relevant_questions)} relevant questions to the context")
    
    # Process and combine all relevant questions
    user_content = [
        {
            "type": "text",
            "text": user_query
        }
    ]
    
    # Add relevant questions to content
    for i, q in enumerate(relevant_questions, 1):
        # Log the full question structure for debugging
        logger.debug(f"Question structure: {q}")
        
        question_text = q.get('text', '')
        question_type = q.get('type', '')
        marks = q.get('marks', 0)
        image = q.get('image')
        
        # Ensure question_text is a string to avoid NoneType errors
        if question_text is None:
            question_text = "No question text available"
            logger.warning(f"Question {i} has no text")
        
        logger.debug(f"Processing question: {question_text[:50] if question_text else 'No text'}...")
        
        # Add question text to user content
        user_content.append({
            "type": "text",
            "text": f"\nQuestion {i} ({marks} marks):\n{question_text}"
        })
        
        # Add image if present
        if image and image.startswith('data:image'):
            logger.debug("Adding question image")
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": image
                }
            })
        elif image:
            logger.debug(f"Image present but format not recognized: {image[:30]}...")
        else:
            logger.debug("No image found for this question")
        
        # Handle options
        options = q.get('options', [])
        if options and isinstance(options, list):
            logger.debug(f"Processing {len(options)} options")
            options_text = "\nOptions:"
            option_images = []
            
            for j, opt in enumerate(options, 1):
                if isinstance(opt, dict):
                    opt_text = opt.get('text', 'No option text')
                    if opt_text is None:
                        opt_text = "No option text available"
                    
                    options_text += f"\n- Option {j}: {opt_text}"
                    
                    # Collect option image if present
                    opt_image = opt.get('image')
                    if opt_image and opt_image.startswith('data:image'):
                        logger.debug(f"Adding image for option {j}")
                        option_images.append({
                            "type": "image_url",
                            "image_url": {
                                "url": opt_image
                            }
                        })
            
            # Add options text
            user_content.append({
                "type": "text",
                "text": options_text
            })
            
            # Add all option images
            user_content.extend(option_images)
        elif options:
            logger.debug(f"Options not in expected format: {type(options)}")
        else:
            logger.debug("No options found for this question")
    
    # Add all content in a single user message
    messages.append({
        "role": "user",
        "content": user_content
    })
    
    logger.debug(f"Final message count: {len(messages)}")
    return messages

@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    try:
        logger.debug("Received chat request")
        data = request.get_json()
        history = data.get('history', [])
        context = data.get('context', {})
        
        # Check if context has large image data
        if 'questions' in context:
            question_count = len(context.get('questions', []))
            logger.debug(f"Received {question_count} questions in context")
        
        # Get the last user message
        last_user_message = next((msg for msg in reversed(history) if msg['role'] == 'user'), None)
        user_query = last_user_message.get('content', '') if last_user_message else ''
        
        logger.debug(f"Processing user query: '{user_query}'")
        
        # Get API key from environment
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            logger.error("API key not found in environment variables")
            return jsonify({'error': 'API key not configured'}), 500

        # Create messages with proper multimodal format - STATELESS approach
        messages = create_messages(context, user_query)
        
        # Prepare the request to OpenRouter
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': request.headers.get('Referer', 'http://localhost:5173'),
            'X-Title': 'IITM Quizzes'
        }
        
        # Use Llama 4 Maverick model
        payload = {
            'model': 'meta-llama/llama-4-maverick:free',
            'messages': messages,
            'temperature': 0.7,
            # 'max_tokens': 2000
        }
        
        logger.debug(f"Request headers prepared: {json.dumps({k: v for k, v in headers.items() if k != 'Authorization'}, indent=2)}")
        logger.debug(f"Request payload structure: {len(messages)} messages")
        
        # For debugging, print the first message content types
        if messages and len(messages) > 0 and 'content' in messages[0]:
            content_types = [item.get('type', 'unknown') for item in messages[0]['content']]
            logger.debug(f"First message content types: {content_types}")
        
        # Make request to OpenRouter
        logger.debug("Making request to OpenRouter...")
        
        # Convert payload to JSON string
        payload_json = json.dumps(payload)
        logger.debug(f"Request payload JSON length: {len(payload_json)} characters")
        
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers=headers,
            data=payload_json
        )
        
        logger.debug(f"OpenRouter response status: {response.status_code}")

        # Handle non-200 responses
        if response.status_code != 200:
            error_content = response.text
            logger.error(f"OpenRouter API error: {error_content}")
            return jsonify({'error': f'Failed to get response from AI: {error_content}'}), response.status_code

        # Parse the response
        try:
            data = response.json()
            logger.debug(f"OpenRouter response parsed successfully")
            
            # Extract the text content from the response
            response_content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            logger.debug(f"Response content type: {type(response_content)}")
            
            if isinstance(response_content, list):
                # If the response is a list of content parts, extract text parts
                reply = ' '.join(part.get('text', '') for part in response_content if part.get('type') == 'text')
                logger.debug(f"Parsed list response with {len(response_content)} parts")
            else:
                # If the response is a simple string
                reply = response_content
                logger.debug(f"Received string response")
            
            if not reply:
                logger.warning("Received empty reply from API")
                reply = "I'm sorry, I couldn't generate a response for this question. Please try again or ask about a different question."
            
            logger.debug(f"Final reply length: {len(reply)}")
            
            return jsonify({'reply': reply})
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response JSON: {e}")
            logger.error(f"Raw response: {response.text[:200]}...")
            return jsonify({'error': 'Received invalid JSON response from API'}), 500

    except Exception as e:
        logger.exception("Error in chat endpoint")
        return jsonify({'error': str(e)}), 500 