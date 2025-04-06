import os
import cv2
import numpy as np
from PIL import Image
import logging
import uuid
from datetime import datetime

def get_data_folder():
    """Get or create the data folder for storing papers and questions"""
    # Create a data folder in the current working directory
    data_folder = os.path.join(os.getcwd(), 'data')
    os.makedirs(data_folder, exist_ok=True)
    return data_folder

def ensure_output_dirs(paper_id):
    """Ensure output directories exist for a paper"""
    data_folder = get_data_folder()
    
    # Create the questions folder for this paper
    questions_folder = os.path.join(data_folder, 'questions', f'paper_{paper_id}')
    os.makedirs(questions_folder, exist_ok=True)
    
    return questions_folder

def process_question_paper(paper_path, paper_id):
    """
    Process a question paper image to extract individual questions
    
    Args:
        paper_path: Path to the question paper image
        paper_id: ID of the paper in the database
        
    Returns:
        Dictionary containing the processed questions and their paths
    """
    logging.info(f"Processing paper: {paper_path}")
    
    # Ensure output directories exist
    questions_folder = ensure_output_dirs(paper_id)
    
    # Detect and extract questions from paper
    questions = extract_questions(paper_path, questions_folder, paper_id)
    
    return {
        'paper_id': paper_id,
        'questions': questions
    }

def extract_questions(paper_path, output_folder, paper_id):
    """
    Extract questions from a paper image
    
    The function attempts to detect questions by finding sections separated by whitespace
    or number markers. For simplicity, we'll simulate this with a basic detection approach.
    
    Args:
        paper_path: Path to the paper image
        output_folder: Where to save extracted question images
        paper_id: ID of the paper for reference
        
    Returns:
        Dictionary mapping question numbers to their image paths
    """
    # For a real implementation, this would use more sophisticated image processing
    # to identify and segment individual questions
    
    # Load the paper image
    paper_img = cv2.imread(paper_path)
    if paper_img is None:
        raise ValueError(f"Could not load image at {paper_path}")
    
    # Get image dimensions
    height, width = paper_img.shape[:2]
    
    # For simplicity, we'll simulate question detection
    # In a real implementation, this would analyze the image to find question boundaries
    
    # Convert image to grayscale for processing
    gray = cv2.cvtColor(paper_img, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding to get binary image
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    
    # Find horizontal lines (potential question separators)
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (width//10, 1))
    horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel)
    
    # Dilate lines to make them more prominent
    horizontal_lines = cv2.dilate(horizontal_lines, np.ones((3,3), np.uint8), iterations=1)
    
    # Find contours
    contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Sort contours by y-coordinate to get them in order from top to bottom
    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])
    
    # Initialize list of y-coordinates for potential question boundaries
    boundaries = [0]  # Start at the top of the image
    
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        # If line is long enough, consider it a question boundary
        if w > width * 0.5:
            boundaries.append(y)
    
    boundaries.append(height)  # End at the bottom of the image
    
    # Create a dictionary to store question information
    questions = {}
    
    # Extract each question based on the boundaries
    for i in range(len(boundaries) - 1):
        # Skip sections that are too small
        if boundaries[i+1] - boundaries[i] < 50:  # Minimum height threshold
            continue
            
        # Extract the question section
        question_img = paper_img[boundaries[i]:boundaries[i+1], 0:width]
        
        # Generate a question number (normally would be extracted from the content)
        question_number = f"q{i+1}"
        
        # Save the question image
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        img_filename = f"paper_{paper_id}_{question_number}_{timestamp}.png"
        img_path = os.path.join(output_folder, img_filename)
        
        cv2.imwrite(img_path, question_img)
        
        # Add to questions dictionary
        questions[question_number] = img_path
    
    logging.info(f"Extracted {len(questions)} questions from paper {paper_id}")
    
    return questions
