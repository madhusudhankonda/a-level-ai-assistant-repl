"""
Script to update the UserProfile table to add the required columns
"""
from app import app, db
from sqlalchemy import text
from datetime import datetime

def add_missing_columns():
    """
    Add missing columns to UserProfile table
    """
    print("Checking UserProfile table for missing columns...")
    try:
        with app.app_context():
            # Check if 'terms_accepted' column exists
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('user_profile')
            column_names = [column['name'] for column in columns]
            
            # List of required columns with their definitions
            required_columns = [
                ("terms_accepted", "BOOLEAN NOT NULL DEFAULT FALSE"),
                ("privacy_accepted", "BOOLEAN NOT NULL DEFAULT FALSE"),
                ("marketing_consent", "BOOLEAN NOT NULL DEFAULT FALSE"),
                ("age_confirmed", "BOOLEAN NOT NULL DEFAULT FALSE"),
                ("terms_accepted_date", "TIMESTAMP WITHOUT TIME ZONE"),
                ("privacy_accepted_date", "TIMESTAMP WITHOUT TIME ZONE"),
                ("ai_usage_consent_required", "BOOLEAN NOT NULL DEFAULT TRUE"),
                ("last_ai_consent_date", "TIMESTAMP WITHOUT TIME ZONE")
            ]
            
            # Add missing columns
            for column_name, column_def in required_columns:
                if column_name not in column_names:
                    print(f"Adding missing column: {column_name}")
                    sql = text(f"ALTER TABLE user_profile ADD COLUMN {column_name} {column_def}")
                    with db.engine.connect() as conn:
                        conn.execute(sql)
                        conn.commit()
                    
            print("UserProfile table update complete!")
            
    except Exception as e:
        print(f"Error updating UserProfile table: {e}")

if __name__ == "__main__":
    add_missing_columns()