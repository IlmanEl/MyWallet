#!/usr/bin/env python3
"""
Automatic setup using Supabase Management API
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
PROJECT_REF = 'rltpsiiwugfsbpzhklgw'

print("\n" + "="*70)
print("🚀 AUTO SETUP - Creating MyWallet Database")
print("="*70 + "\n")

# Read SQL file
with open('database/setup.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

# Try to execute via Supabase Management API
# Using the query endpoint
url = f"{SUPABASE_URL}/rest/v1/rpc/exec"

headers = {
    'apikey': SUPABASE_SERVICE_KEY,
    'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
    'Content-Type': 'application/json'
}

# Since we can't execute DDL via REST API, let's try using supabase-py with raw SQL
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print("🔧 Attempting to create tables...\n")

# Split SQL into individual statements
statements = []
current = ""
for line in sql.split('\n'):
    if line.strip().startswith('--') or not line.strip():
        continue
    current += line + '\n'
    if ';' in line:
        statements.append(current.strip())
        current = ""

print(f"Found {len(statements)} SQL statements\n")

# Try to execute using postgrest
# Note: This might not work for DDL, but let's try
success_count = 0
failed = []

for i, stmt in enumerate(statements[:5], 1):  # Try first 5
    if not stmt or stmt.startswith('--'):
        continue

    print(f"[{i}/{len(statements)}] Executing statement...")

    # Try using requests to call a custom function
    # This won't work without a custom RPC function in Supabase

    # Alternative: Use psycopg2 connection
    break

print("\n" + "="*70)
print("⚠️  AUTOMATIC SETUP NOT POSSIBLE")
print("="*70)
print("\nSupabase REST API doesn't support DDL (CREATE TABLE) commands.")
print("These must be run through the SQL Editor in the Supabase Dashboard.\n")

print("📋 PLEASE DO THIS MANUALLY (takes 30 seconds):\n")
print("1. Click: https://supabase.com/dashboard/project/rltpsiiwugfsbpzhklgw/sql/new")
print("2. Copy SQL from SETUP_INSTRUCTIONS.md or database/setup.sql")
print("3. Paste and click 'Run'\n")

print("After that, run:")
print("  python3 -m bot.main\n")

# However, we CAN insert categories after tables are created!
print("\n💡 Checking if tables already exist...")

try:
    result = supabase.table('categories').select('count').limit(1).execute()
    print(f"✅ Tables exist! Found {len(result.data)} categories")
    print("\n✨ You're all set! Run: python3 -m bot.main")
except Exception as e:
    if 'PGRST205' in str(e) or 'not found' in str(e).lower():
        print("❌ Tables don't exist yet")
        print("\nPlease create them manually using the link above.")
    else:
        print(f"❌ Error: {e}")
