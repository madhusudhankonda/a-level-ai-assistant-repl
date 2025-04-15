from app import app, db
from models import PaperCategory, ExamBoard

with app.app_context():
    # Find OCR Mathematics board
    ocr_maths_board = ExamBoard.query.filter_by(name='OCR', subject_id=1).first()
    
    if ocr_maths_board:
        print(f"Found OCR Mathematics board with ID: {ocr_maths_board.id}")
        
        # Check if categories already exist for this board
        existing_categories = PaperCategory.query.filter_by(board_id=ocr_maths_board.id).all()
        
        if existing_categories:
            print("Existing categories for OCR Mathematics:")
            for cat in existing_categories:
                print(f"  - {cat.id}: {cat.name}")
        else:
            print("No existing categories found for OCR Mathematics. Adding categories...")
            
            # Add missing categories for OCR Mathematics
            categories_to_add = [
                PaperCategory(name='Pure Mathematics', board_id=ocr_maths_board.id, description='Core pure mathematics topics'),
                PaperCategory(name='Pure and Statistics', board_id=ocr_maths_board.id, description='Combined pure and statistics papers'),
                PaperCategory(name='Pure and Mechanics', board_id=ocr_maths_board.id, description='Combined pure and mechanics papers')
            ]
            
            db.session.add_all(categories_to_add)
            db.session.commit()
            
            print("Added new categories for OCR Mathematics")
    else:
        print("Could not find OCR Mathematics board")

    # Print all categories after changes
    print("\nAll Paper Categories after update:")
    all_categories = PaperCategory.query.all()
    for cat in all_categories:
        board = ExamBoard.query.get(cat.board_id)
        print(f"ID: {cat.id}, Name: {cat.name}, Board: {board.name}")