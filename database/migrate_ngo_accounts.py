"""
Quick database migration to add missing columns
"""
import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("🔧 Adding missing columns to ngo_accounts...")
    
    # Add is_active column
    try:
        cur.execute("""
            ALTER TABLE ngo_accounts 
            ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE
        """)
        print("✓ Added is_active column")
    except Exception as e:
        print(f"  is_active: {e}")
    
    # Add last_login column
    try:
        cur.execute("""
            ALTER TABLE ngo_accounts 
            ADD COLUMN IF NOT EXISTS last_login TIMESTAMP
        """)
        print("✓ Added last_login column")
    except Exception as e:
        print(f"  last_login: {e}")
    
    conn.commit()
    
    # Update existing records
    cur.execute("UPDATE ngo_accounts SET is_active = TRUE WHERE is_active IS NULL")
    conn.commit()
    print("✓ Updated existing records")
    
    # Verify
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'ngo_accounts'
        ORDER BY ordinal_position
    """)
    
    columns = cur.fetchall()
    print("\n📊 ngo_accounts table structure:")
    for col in columns:
        print(f"   {col[0]} ({col[1]})")
    
    cur.close()
    conn.close()
    
    print("\n✅ Migration complete!")
    
except Exception as e:
    print(f"❌ Migration failed: {e}")
