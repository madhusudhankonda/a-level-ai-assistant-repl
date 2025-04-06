import os
import json
import base64
import logging
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
MODEL = "gpt-4o"

# Initialize OpenAI client with API key from environment
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def generate_answer(question_image_path, subject):
    """
    Generate an answer for a question using OpenAI's GPT-4o
    
    Args:
        question_image_path: Path to the question image
        subject: Subject of the question (e.g., "Mathematics", "Physics")
    
    Returns:
        Generated answer text
    """
    logging.info(f"Generating answer for question: {question_image_path}")
    
    try:
        # Read the image and encode it to base64
        with open(question_image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Prepare the prompt for GPT-4o
        prompt = f"""
        You are an A-Level {subject} expert tutor. 
        
        Analyze the following {subject} question and provide a detailed, step-by-step solution
        that would earn full marks according to A-Level marking schemes.
        
        Make sure to:
        1. Show all your working clearly
        2. Explain the key concepts involved
        3. Use appropriate mathematical notation or scientific terminology
        4. State any assumptions you make
        5. Present the final answer in the format requested in the question
        
        Your answer should be thorough enough to receive full marks on an A-Level exam.
        """
        
        # Make the API request
        response = openai_client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            max_tokens=2000
        )
        
        # Extract the answer text from the response
        answer_text = response.choices[0].message.content
        
        return answer_text
    
    except Exception as e:
        logging.error(f"Error generating answer: {str(e)}")
        raise Exception(f"Failed to generate answer: {str(e)}")

def generate_explanation(base64_image, answer_text, subject):
    """
    Generate an explanation for a question's answer using OpenAI's GPT-4o
    
    Args:
        base64_image: Base64-encoded image of the question
        answer_text: The pre-generated answer text
        subject: Subject of the question
    
    Returns:
        Explanation text
    """
    logging.info("Generating explanation for answer")
    
    try:
        # Prepare the prompt for GPT-4o
        prompt = f"""
        You are an A-Level {subject} tutor explaining concepts to a student.
        
        I'll show you a question and its answer. Your task is to provide a clear, educational
        explanation of the answer that helps the student understand the underlying concepts.
        
        Focus on:
        1. Breaking down complex steps into simpler terms
        2. Explaining why certain approaches are used
        3. Highlighting key A-Level concepts and principles
        4. Making connections to the broader curriculum
        5. Providing insights that would help the student tackle similar problems
        
        Here is the answer that has been provided:
        
        {answer_text}
        
        Now, explain this answer in a way that genuinely helps the student learn.
        """
        
        # Make the API request
        response = openai_client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            max_tokens=2000
        )
        
        # Extract the explanation from the response
        explanation = response.choices[0].message.content
        
        return explanation
    
    except Exception as e:
        logging.error(f"Error generating explanation: {str(e)}")
        raise Exception(f"Failed to generate explanation: {str(e)}")
