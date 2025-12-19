"""
Manual database table creation script
Creates all tables defined in models.py
"""

from app import app, db

print("Creating database tables...")
print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

with app.app_context():
    # Drop all tables (clean slate)
    print("\nDropping existing tables (if any)...")
    db.drop_all()
    
    # Create all tables
    print("Creating all tables from models...")
    db.create_all()
    
    # Verify tables created
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    print(f"\n✅ Tables created successfully!")
    print(f"Total tables: {len(tables)}")
    print("\nTables in database:")
    for table in sorted(tables):
        print(f"  ✓ {table}")

print("\n✅ Database initialization complete!")
