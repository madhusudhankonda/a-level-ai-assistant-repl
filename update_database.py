from app import app, db
from models import (
    User, CreditTransaction, Subject, ExamBoard, PaperCategory, 
    QuestionPaper, Question, Explanation, UserProfile, Topic, 
    QuestionTopic, UserQuery, StudentAnswer
)

def update_database():
    print("Starting database update...")
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database schema updated successfully")
        
        # Get current tables
        tables = db.metadata.tables.keys()
        print("\nCurrent Database Tables:")
        for table in sorted(tables):
            print(f"- {table}")
            
        # Check if we have basic user data
        user_count = User.query.count()
        print(f"\nExisting Users: {user_count}")
        
        # Check if we have topic data
        topic_count = db.session.query(Topic).count() if 'topic' in tables else 0
        print(f"Existing Topics: {topic_count}")
        
        print("\nDatabase update completed.")

if __name__ == "__main__":
    update_database()