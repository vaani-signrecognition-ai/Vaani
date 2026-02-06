"""
Database setup and migration script for VAANI
Run this to create all necessary tables
"""
import psycopg2
import os
from pathlib import Path

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/vaani_db")

def run_schema():
    """Execute the schema.sql file"""
    try:
        # Read schema file
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Connect and execute
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("🔧 Creating database schema...")
        cur.execute(schema_sql)
        conn.commit()
        
        print("✅ Database schema created successfully!")
        
        # Verify tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cur.fetchall()
        print(f"\n📊 Created {len(tables)} tables:")
        for table in tables:
            print(f"   ✓ {table[0]}")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        return False

def check_existing_data():
    """Check if there's existing data in key tables"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        tables_to_check = [
            'users',
            'admins', 
            'ngo_requests',
            'ngo_accounts',
            'sign_dictionary',
            'events'
        ]
        
        print("\n📈 Checking existing data:")
        for table in tables_to_check:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                print(f"   {table}: {count} rows")
            except:
                print(f"   {table}: table not found")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"⚠️ Could not check data: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("VAANI DATABASE SETUP")
    print("=" * 60)
    
    if not DATABASE_URL or "postgresql://" not in DATABASE_URL:
        print("❌ DATABASE_URL not configured!")
        print("   Set it in your .env file or environment variables")
        exit(1)
    
    print(f"📍 Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'localhost'}")
    
    response = input("\n⚠️  This will create/update database tables. Continue? (y/n): ")
    
    if response.lower() == 'y':
        if run_schema():
            check_existing_data()
            print("\n✅ Database setup complete!")
            print("\n💡 Next steps:")
            print("   1. Start Flask server: python backend/app.py")
            print("   2. Access admin panel: http://127.0.0.1:5000")
            print("   3. Default admin login: admin@vaani.com / admin123")
        else:
            print("\n❌ Database setup failed!")
    else:
        print("❌ Setup cancelled")
