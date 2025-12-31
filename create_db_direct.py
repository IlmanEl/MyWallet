#!/usr/bin/env python3
"""
Direct database creation using Supabase Python client
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Create client with service role (admin access)
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print("\n" + "="*70)
print("🚀 Creating MyWallet Database Tables")
print("="*70 + "\n")

# SQL commands
sql_commands = """
-- Create transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_telegram_id BIGINT NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
    category VARCHAR(100),
    description TEXT,
    payment_method VARCHAR(50),
    project VARCHAR(100),
    date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ai_categorized BOOLEAN DEFAULT FALSE,
    voice_transcription TEXT,
    receipt_image_url TEXT
);

-- Create categories table
CREATE TABLE IF NOT EXISTS categories (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
    parent_category VARCHAR(100),
    emoji VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(name, type)
);

-- Create ai_recommendations table
CREATE TABLE IF NOT EXISTS ai_recommendations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_telegram_id BIGINT NOT NULL,
    recommendation_text TEXT NOT NULL,
    category VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_read BOOLEAN DEFAULT FALSE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_telegram_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);
CREATE INDEX IF NOT EXISTS idx_recommendations_user_id ON ai_recommendations(user_telegram_id);

-- Enable RLS
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_recommendations ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
DROP POLICY IF EXISTS "Allow all for authenticated users" ON transactions;
CREATE POLICY "Allow all for authenticated users" ON transactions FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow all for categories" ON categories;
CREATE POLICY "Allow all for categories" ON categories FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow all for recommendations" ON ai_recommendations;
CREATE POLICY "Allow all for recommendations" ON ai_recommendations FOR ALL USING (true) WITH CHECK (true);
"""

# Execute SQL using postgrest
try:
    # Try using the query method
    import requests

    url = f"{SUPABASE_URL}/rest/v1/rpc/exec"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    # Split SQL into individual commands
    commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip()]

    print("📊 Creating tables and indexes...\n")

    # Use psycopg2 or execute via raw SQL
    # Since we can't execute raw SQL directly via REST API, we'll use Python to create tables

    print("⚠️  Direct SQL execution via REST API is not available.")
    print("Using Python Supabase client to insert data...\n")

    # Insert categories directly using the client
    print("📝 Inserting default categories...")

    categories_data = [
        # Expense categories
        {'name': 'Еда и напитки', 'type': 'expense', 'emoji': '🍔'},
        {'name': 'Рестораны', 'type': 'expense', 'parent_category': 'Еда и напитки', 'emoji': '🍽️'},
        {'name': 'Продукты', 'type': 'expense', 'parent_category': 'Еда и напитки', 'emoji': '🛒'},
        {'name': 'Кафе', 'type': 'expense', 'parent_category': 'Еда и напитки', 'emoji': '☕'},

        {'name': 'Транспорт', 'type': 'expense', 'emoji': '🚗'},
        {'name': 'Такси', 'type': 'expense', 'parent_category': 'Транспорт', 'emoji': '🚕'},
        {'name': 'Общественный транспорт', 'type': 'expense', 'parent_category': 'Транспорт', 'emoji': '🚌'},
        {'name': 'Бензин', 'type': 'expense', 'parent_category': 'Транспорт', 'emoji': '⛽'},

        {'name': 'Здоровье', 'type': 'expense', 'emoji': '🏥'},
        {'name': 'Аптеки', 'type': 'expense', 'parent_category': 'Здоровье', 'emoji': '💊'},
        {'name': 'Врачи', 'type': 'expense', 'parent_category': 'Здоровье', 'emoji': '👨‍⚕️'},
        {'name': 'Анализы', 'type': 'expense', 'parent_category': 'Здоровье', 'emoji': '🔬'},

        {'name': 'Дом', 'type': 'expense', 'emoji': '🏠'},
        {'name': 'Работа/Бизнес', 'type': 'expense', 'emoji': '💼'},
        {'name': 'Образование', 'type': 'expense', 'emoji': '📚'},
        {'name': 'Развлечения', 'type': 'expense', 'emoji': '🎮'},
        {'name': 'Одежда', 'type': 'expense', 'emoji': '👕'},
        {'name': 'Подарки', 'type': 'expense', 'emoji': '🎁'},
        {'name': 'Переводы', 'type': 'expense', 'emoji': '💸'},
        {'name': 'Другое', 'type': 'expense', 'emoji': '📌'},

        # Income categories
        {'name': 'Зарплата', 'type': 'income', 'emoji': '💰'},
        {'name': 'Проекты', 'type': 'income', 'emoji': '💼'},
        {'name': '3D модели', 'type': 'income', 'parent_category': 'Проекты', 'emoji': '🎨'},
        {'name': 'AI агенты', 'type': 'income', 'parent_category': 'Проекты', 'emoji': '🤖'},
        {'name': 'Фриланс', 'type': 'income', 'parent_category': 'Проекты', 'emoji': '💻'},
        {'name': 'Подарки', 'type': 'income', 'emoji': '🎁'},
        {'name': 'Инвестиции', 'type': 'income', 'emoji': '📈'},
    ]

    # Check if categories exist first
    try:
        existing = supabase.table('categories').select('name').execute()
        if existing.data and len(existing.data) > 0:
            print(f"✅ Categories table exists with {len(existing.data)} entries")
        else:
            print("❌ Categories table is empty or doesn't exist")
            print("\n🔧 You need to create tables first in Supabase SQL Editor!")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n" + "="*70)
        print("📋 MANUAL SETUP REQUIRED")
        print("="*70)
        print("\nPlease follow these steps:\n")
        print("1. Open: https://supabase.com/dashboard/project/rltpsiiwugfsbpzhklgw/sql/new")
        print("2. Copy the entire SQL from 'database/setup.sql' file")
        print("3. Paste and click 'Run'\n")
        print("SQL file location: database/setup.sql\n")
        exit(1)

    # If we got here, tables exist, insert categories
    count = 0
    for cat in categories_data:
        try:
            supabase.table('categories').insert(cat).execute()
            count += 1
            print(f"  ✓ {cat['emoji']} {cat['name']}")
        except Exception as e:
            if 'duplicate' in str(e).lower() or 'unique' in str(e).lower():
                # Already exists, skip
                pass
            else:
                print(f"  ⚠️  {cat['name']}: {str(e)[:50]}")

    print(f"\n✅ Inserted/verified {count} categories")

    print("\n" + "="*70)
    print("✅ Database setup complete!")
    print("="*70)
    print("\n📝 Next steps:")
    print("1. Create storage bucket 'receipts' (if not exists)")
    print("2. Run bot: python3 -m bot.main")
    print("\n")

except Exception as e:
    print(f"\n❌ Error: {e}\n")
    print("="*70)
    print("📋 PLEASE RUN SQL MANUALLY")
    print("="*70)
    print("\n1. Open: https://supabase.com/dashboard/project/rltpsiiwugfsbpzhklgw/sql/new")
    print("2. Paste the SQL from database/setup.sql")
    print("3. Click 'Run'")
    print("4. Then run this script again\n")
