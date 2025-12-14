"""Migration script to add user_id to donated_accounts table"""
from app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        try:
            # Add user_id column to donated_accounts
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE donated_accounts ADD COLUMN user_id INTEGER REFERENCES users(id)'))
                conn.commit()
            print("✓ Successfully added user_id column to donated_accounts table")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("✓ Column user_id already exists")
            else:
                print(f"✗ Error: {e}")

if __name__ == '__main__':
    migrate()
