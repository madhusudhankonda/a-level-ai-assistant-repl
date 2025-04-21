"""
Utility script to ensure all sample question images exist.
This script copies q1 and q2 images to create q3-q12 images if they don't exist.
"""

import os
import shutil
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ensure_question_sample_images():
    """
    Ensure that all numbered question sample images exist (q1-q12)
    This function creates any missing sample images by copying from existing ones
    """
    questions_dir = "./data/questions/paper_1"
    
    # Make sure the directory exists
    if not os.path.exists(questions_dir):
        os.makedirs(questions_dir, exist_ok=True)
        logging.info(f"Created directory: {questions_dir}")
    
    # Check for the base q1 image
    base_image_path = os.path.join(questions_dir, "question_q1_703866-q1.png")
    if not os.path.exists(base_image_path):
        logging.warning(f"Base image {base_image_path} not found. Sample images cannot be created.")
        return False
        
    # Check and create each question image q1-q12
    for q_num in range(1, 13):
        image_path = os.path.join(questions_dir, f"question_q{q_num}_703866-q{q_num}.png")
        if not os.path.exists(image_path):
            # Copy from q1 for any missing question image
            shutil.copy(base_image_path, image_path)
            logging.info(f"Created missing sample image: {image_path}")
    
    logging.info("All sample question images are available")
    return True

if __name__ == "__main__":
    # Run the function to ensure all sample images exist
    ensure_question_sample_images()