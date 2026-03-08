"""
Database Migration - Add created_at to Task
============================================
Adds created_at timestamp to track when tasks were created.

USAGE:
    python add_created_at_migration.py

Safe to run multiple times.
"""

import sqlite3
import os
from datetime import datetime


def migrate_sqlite(db_path):
    """Migrate SQLite database."""
    print(f"📦 Migrating SQLite database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check Task table columns
        cursor.execute("PRAGMA table_info(task)")
        task_columns = {row[1] for row in cursor.fetchall()}
        
        print("\n🔄 Migrating Task table...")
        
        if 'created_at' not in task_columns:
            print("  ✅ Adding created_at column")
            # Add column with default value of current time
            cursor.execute("ALTER TABLE task ADD COLUMN created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP")
            
            # For existing tasks, set created_at to a reasonable past date
            # (e.g., 30 days ago) so they appear in history correctly
            print("  📅 Setting created_at for existing tasks...")
            cursor.execute("""
                UPDATE task 
                SET created_at = datetime('now', '-30 days')
                WHERE created_at = CURRENT_TIMESTAMP
            """)
            
            cursor.execute("SELECT COUNT(*) FROM task")
            task_count = cursor.fetchone()[0]
            print(f"  ✅ Updated {task_count} existing tasks")
        else:
            print("  ⏭️  created_at already exists")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        print("\n📸 Tasks now track creation date!")
        print("   New tasks will only appear from creation date forward.")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        conn.close()


def migrate_postgresql(database_url):
    """Migrate PostgreSQL database."""
    print(f"📦 Migrating PostgreSQL database")
    
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        result = urlparse(database_url)
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        cursor = conn.cursor()
        
        # Check Task table
        print("\n🔄 Migrating task table...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'task'
        """)
        task_columns = {row[0] for row in cursor.fetchall()}
        
        if 'created_at' not in task_columns:
            print("  ✅ Adding created_at column")
            cursor.execute("ALTER TABLE task ADD COLUMN created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP")
            
            # Set existing tasks to 30 days ago
            print("  📅 Setting created_at for existing tasks...")
            cursor.execute("""
                UPDATE task 
                SET created_at = CURRENT_TIMESTAMP - INTERVAL '30 days'
                WHERE created_at = CURRENT_TIMESTAMP
            """)
            
            cursor.execute("SELECT COUNT(*) FROM task")
            task_count = cursor.fetchone()[0]
            print(f"  ✅ Updated {task_count} existing tasks")
        else:
            print("  ⏭️  created_at already exists")
        
        conn.commit()
        print("\n✅ PostgreSQL migration completed!")
        
    except ImportError:
        print("❌ psycopg2 not installed")
        raise
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()


def main():
    """Run migration."""
    print("="*60)
    print("  ADD created_at TO TASK TABLE")
    print("  Enables proper historical task tracking")
    print("="*60)
    
    database_url = os.environ.get("DATABASE_URL")
    
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        migrate_postgresql(database_url)
    else:
        db_path = "tasker.db"
        if not os.path.exists(db_path):
            print(f"\n⚠️  Database '{db_path}' not found!")
        migrate_sqlite(db_path)
    
    print("\n" + "="*60)
    print("  MIGRATION COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    main()