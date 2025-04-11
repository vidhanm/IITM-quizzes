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

def create_messages(context, history):
    """Create messages array with proper multimodal format for Gemini"""
    paper = context.get('paper', {})
    questions = context.get('questions', [])
    
    # Get the last user message to determine which question they're asking about
    last_user_message = next((msg for msg in reversed(history) if msg['role'] == 'user'), None)
    user_query = last_user_message.get('content', '') if last_user_message else ''
    
    messages = [
        {
            "role": "system",
            "content": f"You are a helpful Quiz Assistant for the quiz titled \"{paper.get('title', 'Untitled Quiz')}\" with total score {paper.get('total_score', 0)}."
        }
    ]
    
    # If this is the first message or user hasn't asked about a specific question yet,
    # provide a general introduction without sending any questions
    if not history or not any(q.lower() in user_query.lower() for q in ['question', 'q']):
        messages.append({
            "role": "assistant",
            "content": "I can help you with any questions from this quiz. Please specify which question you'd like help with by mentioning its number or content."
        })
        # Add conversation history for context if it exists
        for msg in history:
            if isinstance(msg.get('content'), str):
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
        return messages
    
    # Try to extract question number from user query
    question_numbers = re.findall(r'question\s*(\d+)', user_query.lower())
    relevant_questions = []
    
    if question_numbers:
        # User mentioned specific question number(s)
        for q_num in question_numbers:
            q_num = int(q_num)
            if 1 <= q_num <= len(questions):
                relevant_questions.append(questions[q_num - 1])
    else:
        # If no question number mentioned, try to find relevant questions based on content
        for q in questions:
            if q.get('text', '').lower() in user_query.lower():
                relevant_questions.append(q)
    
    # If we couldn't identify specific questions, ask the user to be more specific
    if not relevant_questions:
        messages.append({
            "role": "assistant",
            "content": "I couldn't identify which question you're asking about. Please mention the question number (e.g., 'question 1') or provide more details about the question content."
        })
        # Add conversation history for context
        for msg in history:
            if isinstance(msg.get('content'), str):
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
        return messages
    
    # Add relevant questions to context
    for i, q in enumerate(relevant_questions, 1):
        question_text = q.get('text', '')
        question_type = q.get('type', '')
        marks = q.get('marks', 0)
        image = q.get('image')
        
        # Start with text content
        content = [
            {
                "type": "text",
                "text": f"Question {i} ({marks} marks):\n{question_text}"
            }
        ]
        
        # Add image if present
        if image and image.startswith('data:image'):
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": image
                }
            })
        
        # Handle options
        options = q.get('options', [])
        if options and isinstance(options, list):
            options_text = "\nOptions:"
            for j, opt in enumerate(options, 1):
                if isinstance(opt, dict):
                    opt_text = opt.get('text', 'No option text')
                    opt_image = opt.get('image')
                    options_text += f"\n- Option {j}: {opt_text}"
                    
                    # Add option image if present
                    if opt_image and opt_image.startswith('data:image'):
                        content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": opt_image
                            }
                        })
            
            content[0]["text"] += options_text
        
        messages.append({
            "role": "user",
            "content": content
        })
    
    # Add conversation history
    for msg in history:
        # Convert any image references in history to proper format
        if isinstance(msg.get('content'), str):
            messages.append({
                "role": msg['role'],
                "content": msg['content']
            })
    
    return messages

@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    try:
        logger.debug("Received chat request")
        data = request.get_json()
        history = data.get('history', [])
        context = data.get('context', {})
        logger.debug(f"Chat history received: {json.dumps(history, indent=2)}")
        logger.debug(f"Quiz context received: {json.dumps(context, indent=2)}")
        
        # Get API key from environment
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            logger.error("API key not found in environment variables")
            return jsonify({'error': 'API key not configured'}), 500

        # Create messages with proper multimodal format
        messages = create_messages(context, history)
        
        # Prepare the request to OpenRouter
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': request.headers.get('Referer', 'http://localhost:5173'),
            'X-Title': 'IITM Quizzes'
        }
        logger.debug(f"Request headers prepared: {json.dumps({k: v for k, v in headers.items() if k != 'Authorization'}, indent=2)}")

        # Use Gemini Pro model which supports image understanding
        payload = {
            'model': 'google/gemini-2.5-pro-exp-03-25:free',
            'messages': messages
        }
        logger.debug(f"Request payload prepared: {json.dumps(payload, indent=2)}")

        # Make request to OpenRouter
        logger.debug("Making request to OpenRouter...")
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers=headers,
            json=payload
        )
        logger.debug(f"OpenRouter response status: {response.status_code}")

        if response.status_code != 200:
            error_content = response.text
            logger.error(f"OpenRouter API error: {error_content}")
            return jsonify({'error': f'Failed to get response from AI: {error_content}'}), response.status_code

        data = response.json()
        logger.debug(f"OpenRouter response data: {json.dumps(data, indent=2)}")
        
        reply = data.get('choices', [{}])[0].get('message', {}).get('content', '')
        logger.debug(f"Final reply: {reply}")
        
        return jsonify({'reply': reply})

    except Exception as e:
        logger.exception("Error in chat endpoint")
        return jsonify({'error': str(e)}), 500 