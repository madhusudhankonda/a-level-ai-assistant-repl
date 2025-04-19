from app import app, db
from models import Question
import os
import shutil
import uuid

def get_data_folder():
    """Get the data folder for storing papers and questions"""
    data_folder = os.path.join(os.getcwd(), 'data')
    os.makedirs(data_folder, exist_ok=True)
    return data_folder

# Sample images we'll use to populate the missing question images
SAMPLE_IMAGES = [
    "./data/questions/paper_1/question_q1_703866-q1.png",
    "./data/papers/sample_math_paper.png"
]

with app.app_context():
    # Find a sample image we can use
    sample_image_path = None
    for path in SAMPLE_IMAGES:
        if os.path.exists(path):
            sample_image_path = path
            print(f"Using sample image: {sample_image_path}")
            break
    
    if not sample_image_path:
        print("No sample images found to use as fallbacks!")
        exit(1)
    
    # Get all questions for paper_id=55
    questions = Question.query.filter_by(paper_id=55).all()
    print(f"Found {len(questions)} questions for paper_id=55")
    
    # Create the paper_55 directory if it doesn't exist
    paper_dir = os.path.join(get_data_folder(), "paper_55")
    os.makedirs(paper_dir, exist_ok=True)
    print(f"Ensured directory exists: {paper_dir}")
    
    # For each question, create a new image file in the correct location
    for question in questions:
        print(f"Processing question {question.id}: {question.question_number}")
        
        # Get the expected filename from the path
        filename = os.path.basename(question.image_path)
        
        # Create the new file path
        new_path = os.path.join(paper_dir, filename)
        
        # Copy the sample image to this location
        try:
            shutil.copy(sample_image_path, new_path)
            print(f"  ✓ Created image file at: {new_path}")
            
            # Verify the file exists
            if os.path.exists(new_path):
                print(f"  ✓ Verified file exists")
            else:
                print(f"  ✗ File not created successfully")
                
        except Exception as e:
            print(f"  ✗ Error copying file: {str(e)}")
    
    print("\nDone! All question images should now be available.")
