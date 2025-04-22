"""
Update image paths in the database to fix the mismatch between database records and filesystem.
This script specifically addresses paper 57 which has missing files.
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the database URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL')

def update_paper_57_image_paths():
    """
    Update the image paths for paper 57 questions to point to the actual sample images
    """
    # Create a direct database connection without Flask
    engine = create_engine(DATABASE_URL)
    
    # Create a session factory
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    session = Session()
    
    try:
        # Directly update the database using SQL for efficiency
        sample_image_base = os.path.abspath('./attached_assets')
        logger.info(f"Sample image base path: {sample_image_base}")
        
        # Build update statements for each question in paper 57
        for q_num in range(1, 13):
            sample_file = f"703866-q{q_num}.png"
            sample_path = os.path.join(sample_image_base, sample_file)
            
            # Check if the file exists
            if os.path.isfile(sample_path):
                logger.info(f"Found sample image for q{q_num}: {sample_path}")
                
                # Update the database record directly with SQL
                update_query = text(f"""
                UPDATE question 
                SET image_path = '{sample_path}', 
                    image_url = '/question-image/' || id 
                WHERE paper_id = 57 AND question_number = 'q{q_num}'
                """)
                
                result = session.execute(update_query)
                logger.info(f"Updated question q{q_num}, rows affected: {result.rowcount}")
            else:
                logger.warning(f"Sample image not found: {sample_path}")
        
        # Commit the changes
        session.commit()
        logger.info("Successfully committed changes to the database")
        return True
    
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating database: {str(e)}")
        return False
    
    finally:
        session.close()

if __name__ == '__main__':
    logger.info("Starting database update for paper 57 image paths")
    success = update_paper_57_image_paths()
    
    if success:
        logger.info("Database update completed successfully")
        sys.exit(0)
    else:
        logger.error("Database update failed")
        sys.exit(1)