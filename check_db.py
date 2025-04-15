from app import app, db

with app.app_context():
    # Get all table names
    table_names = [table.name for table in db.metadata.tables.values()]
    print("Current Database Tables:")
    for name in sorted(table_names):
        print(f"- {name}")