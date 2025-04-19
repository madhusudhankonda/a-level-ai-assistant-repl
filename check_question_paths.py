from app import app, db
from models import Question
import os

with app.app_context():
    questions = Question.query.filter_by(paper_id=55).all()
    print(f"Found {len(questions)} questions for paper_id=55")
    
    for q in questions:
        print(f"Question {q.id}: {q.question_number}, Image path: {q.image_path}")
        # Check if the file exists at the given path
        if os.path.exists(q.image_path):
            print(f"  ✓ File exists at this path")
        else:
            print(f"  ✗ File NOT found at this path")
            
            # Try some alternative paths
            alt_paths = [
                q.image_path.replace('/home/runner/workspace/', './'),
                os.path.join('./data', os.path.basename(os.path.dirname(q.image_path)), os.path.basename(q.image_path))
            ]
            
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    print(f"  ✓ File exists at alternative path: {alt_path}")
                else:
                    print(f"  ✗ File NOT found at alternative path: {alt_path}")
