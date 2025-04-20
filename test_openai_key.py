import os
import sys
from utils.openai_helper import test_openai_connection
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test if the OpenAI API key is working properly"""
    logger.info("Testing OpenAI API key...")
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable is not set!")
        return False
        
    logger.info(f"API key found with length: {len(api_key)}")
    
    # Test the connection
    success, message = test_openai_connection()
    
    if success:
        logger.info(f"OpenAI connection test successful: {message}")
        return True
    else:
        logger.error(f"OpenAI connection test failed: {message}")
        return False

if __name__ == "__main__":
    if main():
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure