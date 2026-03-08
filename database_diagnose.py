"""
Database Diagnostic Script
===========================
Checks if your database has been migrated correctly.

Run this: python check_database.py
"""

import sqlite3
import os

def check_database():
    db_path = "instance/tasker.db"
    
    if not os.path.exists(db_path):
        print("❌ Database file 'tasker.db' not found!")
        print("   Are you in the right directory?")
        return
    
    print("✅ Database file found")
    print("="*60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check Task table
    print("\n📋 TASK TABLE:")
    cursor.execute("PRAGMA table_info(task)")
    task_columns = {row[1]: row[2] for row in cursor.fetchall()}
    
    if 'deleted_at' in task_columns:
        print("  ✅ deleted_at column EXISTS")
    else:
        print("  ❌ deleted_at column MISSING - Migration not run!")
    
    # Check DailyTask table
    print("\n📋 DAILY_TASK TABLE:")
    cursor.execute("PRAGMA table_info(daily_task)")
    daily_columns = {row[1]: row[2] for row in cursor.fetchall()}
    
    required_fields = ['task_title', 'task_duration', 'category_name']
    missing_fields = []
    
    for field in required_fields:
        if field in daily_columns:
            print(f"  ✅ {field} column EXISTS")
        else:
            print(f"  ❌ {field} column MISSING!")
            missing_fields.append(field)
    
    # Check if snapshot fields are populated
    if not missing_fields:
        cursor.execute("SELECT COUNT(*) FROM daily_task WHERE task_title IS NULL")
        null_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM daily_task")
        total_count = cursor.fetchone()[0]
        
        print(f"\n📊 DATA STATUS:")
        print(f"  Total DailyTask records: {total_count}")
        print(f"  Records with NULL task_title: {null_count}")
        
        if null_count > 0:
            print(f"  ⚠️  {null_count} records have NULL snapshot data!")
            print("     This means migration didn't populate existing records.")
    
    # Check for deleted tasks
    if 'deleted_at' in task_columns:
        cursor.execute("SELECT COUNT(*) FROM task WHERE deleted_at IS NOT NULL")
        deleted_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM task")
        total_tasks = cursor.fetchone()[0]
        
        print(f"\n🗑️  DELETED TASKS:")
        print(f"  Total tasks: {total_tasks}")
        print(f"  Deleted tasks: {deleted_count}")
    
    print("\n" + "="*60)
    
    # SUMMARY
    print("\n📝 SUMMARY:")
    
    if missing_fields:
        print("❌ MIGRATION NOT COMPLETED!")
        print(f"   Missing fields: {', '.join(missing_fields)}")
        print("\n   ACTION REQUIRED:")
        print("   Run: python migrate_database.py")
    elif 'deleted_at' not in task_columns:
        print("❌ MIGRATION NOT RUN!")
        print("\n   ACTION REQUIRED:")
        print("   Run: python migrate_database.py")
    else:
        print("✅ Database structure is correct!")
        
        if null_count > 0:
            print(f"\n⚠️  WARNING: {null_count} DailyTask records have NULL snapshot data")
            print("   ACTION REQUIRED:")
            print("   Run: python migrate_database.py again to populate them")
        else:
            print("✅ All snapshot fields are populated!")
            print("\n🎯 Your deletion issue is likely:")
            print("   1. Browser cache (hard refresh: Ctrl+Shift+R)")
            print("   2. JavaScript not loaded (check browser console F12)")
    
    conn.close()

if __name__ == "__main__":
    check_database()