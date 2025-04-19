import os
import sys
import base64
import logging
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get your API key from the environment variable
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Configure OpenAI client with additional timeout parameters
openai = OpenAI(
    api_key=OPENAI_API_KEY,
    timeout=60.0,  # Longer timeout
    max_retries=3  # More retries
)

def load_and_encode_image(image_path):
    """Load an image from file and encode it as base64 with data URI prefix"""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            data_uri = f"data:image/jpeg;base64,{encoded_string}"
            return data_uri
    except Exception as e:
        logger.error(f"Error loading image: {e}")
        return None

def test_image_processing(image_path):
    """Test processing an image with OpenAI's API"""
    try:
        logger.info(f"Testing OpenAI image processing with {image_path}")
        
        # Encode the image
        data_uri = load_and_encode_image(image_path)
        if not data_uri:
            return False, "Failed to load or encode image"
        
        # System prompt for image analysis
        system_prompt = """
        You are an expert tutor. Analyze the image of a math question and provide a short description of what the question is asking.
        Keep your response very brief - just 1-2 sentences.
        """
        
        # Make the API call
        logger.info("Calling OpenAI API with image")
        response = openai.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": "Please describe this math question:"},
                    {"type": "image_url", "image_url": {"url": data_uri}}
                ]}
            ],
            max_tokens=100
        )
        
        # Get the text response
        result = response.choices[0].message.content
        logger.info(f"OpenAI image test successful. Response: {result}")
        
        return True, result
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"OpenAI image test failed: {error_message}")
        return False, f"OpenAI image processing failed: {error_message}"

if __name__ == "__main__":
    # Check if image path was provided
    if len(sys.argv) < 2:
        print("Usage: python test_image_openai.py <path_to_image>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    success, message = test_image_processing(image_path)
    
    print(f"Success: {success}")
    print(f"Response: {message}")