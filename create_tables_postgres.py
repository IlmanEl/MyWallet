#!/usr/bin/env python3
"""
Create tables using direct PostgreSQL connection
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Supabase connection string format:
# postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
SUPABASE_URL = os.getenv('SUPABASE_URL')  # https://rltpsiiwugfsbpzhklgw.supabase.co
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Extract project ID from URL
project_id = SUPABASE_URL.split('//')[1].split('.')[0]  # rltpsiiwugfsbpzhklgw

# We need the database password - it's usually in project settings
# For now, let's construct the connection string
# User needs to provide DB password from Supabase dashboard

print("\n" + "="*70)
print("🚀 MyWallet Database Setup via PostgreSQL")
print("="*70 + "\n")

print("To connect to Supabase PostgreSQL, we need the database password.\n")
print("Please follow these steps:\n")
print("1. Open: https://supabase.com/dashboard/project/rltpsiiwugfsbpzhklgw/settings/database")
print("2. Find 'Database password' section")
print("3. Copy the password\n")

db_password = input("Enter your Supabase database password: ").strip()

if not db_password:
    print("\n❌ Password required!\n")
    exit(1)

# Connection string
conn_string = f"postgresql://postgres.rltpsiiwugfsbpzhklgw:{db_password}@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"

print("\n🔌 Connecting to Supabase PostgreSQL...")

try:
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    print("✅ Connected successfully!\n")
    print("📊 Creating tables...\n")

    # Read SQL from file
    with open('database/setup.sql', 'r', encoding='utf-8') as f:
        sql = f.read()

    # Execute SQL
    cursor.execute(sql)
    conn.commit()

    print("✅ All tables, indexes, and policies created!")
    print("✅ Default categories inserted!")

    cursor.close()
    conn.close()

    print("\n" + "="*70)
    print("✅ Database setup complete!")
    print("="*70)
    print("\n📝 Next steps:")
    print("1. Create storage bucket 'receipts' in Supabase Dashboard")
    print("2. Run bot: python3 -m bot.main")
    print("\n")

except psycopg2.OperationalError as e:
    print(f"\n❌ Connection error: {e}\n")
    print("Please check:")
    print("- Database password is correct")
    print("- Connection string format")
    print("\n")
except Exception as e:
    print(f"\n❌ Error: {e}\n")
    if conn:
        conn.rollback()
