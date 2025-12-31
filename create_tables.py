"""
Simple script to create tables in Supabase using REST API
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def create_tables_via_rest():
    """Create tables using Supabase REST API"""

    print("\n🔧 Creating tables in Supabase...\n")

    # We'll use PostgREST to execute raw SQL
    # Note: This requires the service role key with full access

    url = f"{SUPABASE_URL}/rest/v1/rpc/exec"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json"
    }

    sql_commands = [
        # Create transactions table
        """
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
        """,

        # Create categories table
        """
        CREATE TABLE IF NOT EXISTS categories (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
            parent_category VARCHAR(100),
            emoji VARCHAR(10),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(name, type)
        );
        """,

        # Create recommendations table
        """
        CREATE TABLE IF NOT EXISTS ai_recommendations (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            user_telegram_id BIGINT NOT NULL,
            recommendation_text TEXT NOT NULL,
            category VARCHAR(50),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            is_read BOOLEAN DEFAULT FALSE
        );
        """,

        # Create indexes
        "CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_telegram_id);",
        "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date DESC);",
        "CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);",
        "CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);",
        "CREATE INDEX IF NOT EXISTS idx_recommendations_user_id ON ai_recommendations(user_telegram_id);",

        # Enable RLS
        "ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE categories ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE ai_recommendations ENABLE ROW LEVEL SECURITY;",

        # Create policies
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT FROM pg_policies WHERE tablename = 'transactions' AND policyname = 'Allow all for authenticated users'
            ) THEN
                CREATE POLICY "Allow all for authenticated users" ON transactions
                    FOR ALL USING (true) WITH CHECK (true);
            END IF;
        END $$;
        """,

        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT FROM pg_policies WHERE tablename = 'categories' AND policyname = 'Allow all for categories'
            ) THEN
                CREATE POLICY "Allow all for categories" ON categories
                    FOR ALL USING (true) WITH CHECK (true);
            END IF;
        END $$;
        """,

        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT FROM pg_policies WHERE tablename = 'ai_recommendations' AND policyname = 'Allow all for recommendations'
            ) THEN
                CREATE POLICY "Allow all for recommendations" ON ai_recommendations
                    FOR ALL USING (true) WITH CHECK (true);
            END IF;
        END $$;
        """
    ]

    print("ℹ️  Due to Supabase API restrictions, you need to manually execute SQL.\n")
    print("Please follow these steps:\n")
    print("1. Open: https://supabase.com/dashboard/project/rltpsiiwugfsbpzhklgw/sql/new")
    print("2. Copy the SQL from 'database/setup.sql'")
    print("3. Paste it and click 'Run'\n")
    print("The SQL file is located at: database/setup.sql\n")

    print("="*70)
    with open('database/setup.sql', 'r') as f:
        print(f.read())
    print("="*70)

    print("\n✅ After running the SQL, press Enter to continue with category insertion...")
    input()

    return True

if __name__ == '__main__':
    create_tables_via_rest()

    print("\n✅ SQL should now be executed in Supabase!")
    print("Running category insertion...\n")

    # Now run the category insertion
    import setup_database
    setup_database.insert_default_categories()

    print("\n" + "="*70)
    print("✅ Database setup complete!")
    print("="*70)
    print("\nNext steps:")
    print("1. Create storage bucket 'receipts' in Supabase Dashboard")
    print("2. Run: python -m bot.main")
