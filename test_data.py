from app import app, db
from models import Subject, ExamBoard, PaperCategory

with app.app_context():
    subjects = Subject.query.all()
    boards = ExamBoard.query.all()
    categories = PaperCategory.query.all()
    
    print('Subjects:', [{'id': s.id, 'name': s.name} for s in subjects])
    print('Boards:', [{'id': b.id, 'name': b.name, 'subject_id': b.subject_id} for b in boards])
    print('Categories:', [{'id': c.id, 'name': c.name, 'board_id': c.board_id} for c in categories])