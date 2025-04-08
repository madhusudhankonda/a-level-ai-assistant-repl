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

def generate_explanation(base64_image, subject):
    """
    Generate an explanation for a question using OpenAI's GPT-4o
    
    Args:
        base64_image: Base64-encoded image of the question
        subject: Subject of the question (e.g., "Mathematics", "Physics")
    
    Returns:
        Generated explanation text
    """
    logging.info(f"Generating explanation for {subject} question")
    
    try:
        # Prepare the prompt for GPT-4o based on the subject
        if subject.lower() in ["mathematics", "maths", "math"]:
            prompt = """
            You are an A-Level Mathematics tutor expert. Analyze this mathematics question and provide a comprehensive solution that would receive full marks on an A-Level exam.
            
            Your response should:
            1. First identify the exact type of question and the mathematical concepts being tested
            2. Break down the problem into clear, manageable steps 
            3. Show all calculations and working in detail
            4. Explain the mathematical reasoning behind each step
            5. Provide the final answer in the format requested in the question
            6. Include a brief explanation of any key concepts that students often struggle with
            
            Use proper mathematical notation. Your solution should be accessible to A-Level students while demonstrating the rigor expected at this level.
            """
        elif subject.lower() in ["physics"]:
            prompt = """
            You are an A-Level Physics tutor expert. Analyze this physics question and provide a comprehensive solution that would receive full marks on an A-Level exam.
            
            Your response should:
            1. First identify the physical principles and concepts being tested
            2. Break down the problem into clear steps, identifying any key equations needed
            3. Show all calculations with correct units and precision
            4. Explain the physical significance of each step
            5. Provide the final answer with appropriate units and significant figures
            6. Include any key theoretical insights that would earn extra marks
            
            Use proper scientific notation and ensure units are correctly applied throughout. Your solution should demonstrate understanding of both the mathematical and conceptual aspects of physics.
            """
        elif subject.lower() in ["chemistry"]:
            prompt = """
            You are an A-Level Chemistry tutor expert. Analyze this chemistry question and provide a comprehensive solution that would receive full marks on an A-Level exam.
            
            Your response should:
            1. First identify the chemical concepts and principles being tested
            2. For reaction questions, include balanced equations and mechanisms where relevant
            3. For calculation questions, show all working clearly with appropriate units
            4. Explain key chemical principles and theory underlying the solution
            5. Include relevant structural diagrams or representations where helpful
            6. Provide complete, accurate answers addressing all parts of the question
            
            Pay particular attention to chemical accuracy, proper terminology, and appropriate use of chemical symbols and conventions. Your answer should demonstrate depth of chemical understanding.
            """
        elif subject.lower() in ["biology"]:
            prompt = """
            You are an A-Level Biology tutor expert. Analyze this biology question and provide a comprehensive solution that would receive full marks on an A-Level exam.
            
            Your response should:
            1. First identify the biological concepts and principles being tested
            2. Provide detailed explanations using correct biological terminology
            3. For processes, explain each step and its significance clearly
            4. Include any relevant diagrams or representations that would be helpful
            5. Make connections between different biological systems or concepts where relevant
            6. Address all components of the question comprehensively
            
            Your answer should demonstrate both breadth and depth of biological knowledge, including molecular, cellular, and systemic understanding where appropriate.
            """
        else:
            prompt = f"""
            You are an A-Level {subject} expert tutor. Analyze this question and provide a comprehensive solution that would receive full marks on an A-Level exam.
            
            Your response should:
            1. First identify the key concepts being tested in this question
            2. Break down the problem into clear, manageable steps
            3. Show all necessary working and calculations
            4. Explain your reasoning and approach throughout
            5. Provide a complete answer addressing all parts of the question
            6. Include any important insights that demonstrate A-Level understanding
            
            Use appropriate technical language and conventions for {subject}. Your solution should be thorough and demonstrate expert subject knowledge.
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
            max_tokens=2500
        )
        
        # Extract the explanation text from the response
        explanation_text = response.choices[0].message.content
        
        return explanation_text
    
    except Exception as e:
        logging.error(f"Error generating explanation: {str(e)}")
        raise Exception(f"Failed to generate explanation: {str(e)}")
