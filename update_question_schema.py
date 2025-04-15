#!/usr/bin/env python
"""
Script to update the Question table schema to include missing columns:
- difficulty_level (Integer, nullable=True)
- marks (Integer, nullable=True)
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, MetaData, Table

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)

def add_missing_columns():
    """Add missing columns to the question table"""
    with app.app_context():
        # Use SQLAlchemy Core to get direct access to the database schema
        metadata = MetaData()
        question_table = Table('question', metadata, autoload_with=db.engine)
        
        # Check if columns already exist
        existing_columns = [c.name for c in question_table.columns]
        columns_to_add = []
        
        # Check for difficulty_level column
        if 'difficulty_level' not in existing_columns:
            print("Adding difficulty_level column to question table...")
            columns_to_add.append(Column('difficulty_level', Integer, nullable=True))
        else:
            print("difficulty_level column already exists")
        
        # Check for marks column
        if 'marks' not in existing_columns:
            print("Adding marks column to question table...")
            columns_to_add.append(Column('marks', Integer, nullable=True))
        else:
            print("marks column already exists")
        
        # Add missing columns
        if columns_to_add:
            for column in columns_to_add:
                db.session.execute(db.text(
                    f"ALTER TABLE question ADD COLUMN {column.name} INTEGER"
                ))
            db.session.commit()
            print("Schema update completed")
        else:
            print("No schema updates needed")

if __name__ == "__main__":
    add_missing_columns()