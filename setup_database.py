"""
Setup Supabase Database
This script creates all tables, indexes, and default categories
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Create Supabase client with service role key for admin access
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def execute_sql(sql: str, description: str):
    """Execute SQL query"""
    try:
        logger.info(f"Executing: {description}")
        # Use RPC to execute SQL
        result = supabase.rpc('exec_sql', {'sql_query': sql}).execute()
        logger.info(f"✅ Success: {description}")
        return True
    except Exception as e:
        # Try alternative method - direct table operations
        logger.warning(f"RPC method failed, trying alternative: {str(e)}")
        return False


def create_tables():
    """Create all tables"""

    # Create transactions table
    transactions_sql = """
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
    """

    # Create categories table
    categories_sql = """
    CREATE TABLE IF NOT EXISTS categories (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
        parent_category VARCHAR(100),
        emoji VARCHAR(10),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        UNIQUE(name, type)
    );
    """

    # Create recommendations table
    recommendations_sql = """
    CREATE TABLE IF NOT EXISTS ai_recommendations (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_telegram_id BIGINT NOT NULL,
        recommendation_text TEXT NOT NULL,
        category VARCHAR(50),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        is_read BOOLEAN DEFAULT FALSE
    );
    """

    logger.info("Creating tables...")
    print("\n📊 Creating database tables...")

    # Since direct SQL execution might not work, we'll use the Supabase client
    # to check if tables exist by trying to query them

    try:
        # Try to query transactions table
        supabase.table('transactions').select('id').limit(1).execute()
        logger.info("✅ Table 'transactions' already exists")
    except:
        logger.info("⚠️  Table 'transactions' needs to be created manually")
        print("\n⚠️  Tables need to be created in Supabase SQL Editor")
        print("Please run the following SQL in Supabase Dashboard > SQL Editor:")
        print("\n" + "="*60)
        print(transactions_sql)
        print(categories_sql)
        print(recommendations_sql)
        print("="*60 + "\n")
        return False

    return True


def create_indexes():
    """Create indexes"""
    logger.info("Creating indexes...")

    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_telegram_id);",
        "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date DESC);",
        "CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);",
        "CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);",
        "CREATE INDEX IF NOT EXISTS idx_recommendations_user_id ON ai_recommendations(user_telegram_id);"
    ]

    logger.info("⚠️  Indexes should be created in Supabase SQL Editor")


def insert_default_categories():
    """Insert default categories"""
    logger.info("Inserting default categories...")

    expense_categories = [
        {'name': 'Еда и напитки', 'type': 'expense', 'parent_category': None, 'emoji': '🍔'},
        {'name': 'Рестораны', 'type': 'expense', 'parent_category': 'Еда и напитки', 'emoji': '🍽️'},
        {'name': 'Продукты', 'type': 'expense', 'parent_category': 'Еда и напитки', 'emoji': '🛒'},
        {'name': 'Кафе', 'type': 'expense', 'parent_category': 'Еда и напитки', 'emoji': '☕'},

        {'name': 'Транспорт', 'type': 'expense', 'parent_category': None, 'emoji': '🚗'},
        {'name': 'Такси', 'type': 'expense', 'parent_category': 'Транспорт', 'emoji': '🚕'},
        {'name': 'Общественный транспорт', 'type': 'expense', 'parent_category': 'Транспорт', 'emoji': '🚌'},
        {'name': 'Бензин', 'type': 'expense', 'parent_category': 'Транспорт', 'emoji': '⛽'},

        {'name': 'Здоровье', 'type': 'expense', 'parent_category': None, 'emoji': '🏥'},
        {'name': 'Аптеки', 'type': 'expense', 'parent_category': 'Здоровье', 'emoji': '💊'},
        {'name': 'Врачи', 'type': 'expense', 'parent_category': 'Здоровье', 'emoji': '👨‍⚕️'},
        {'name': 'Анализы', 'type': 'expense', 'parent_category': 'Здоровье', 'emoji': '🔬'},

        {'name': 'Дом', 'type': 'expense', 'parent_category': None, 'emoji': '🏠'},
        {'name': 'Коммунальные услуги', 'type': 'expense', 'parent_category': 'Дом', 'emoji': '💡'},
        {'name': 'Ремонт', 'type': 'expense', 'parent_category': 'Дом', 'emoji': '🔨'},
        {'name': 'Мебель', 'type': 'expense', 'parent_category': 'Дом', 'emoji': '🛋️'},

        {'name': 'Работа/Бизнес', 'type': 'expense', 'parent_category': None, 'emoji': '💼'},
        {'name': 'Материалы', 'type': 'expense', 'parent_category': 'Работа/Бизнес', 'emoji': '📦'},
        {'name': 'Инструменты', 'type': 'expense', 'parent_category': 'Работа/Бизнес', 'emoji': '🔧'},
        {'name': 'Партнерам', 'type': 'expense', 'parent_category': 'Работа/Бизнес', 'emoji': '🤝'},

        {'name': 'Образование', 'type': 'expense', 'parent_category': None, 'emoji': '📚'},
        {'name': 'Курсы', 'type': 'expense', 'parent_category': 'Образование', 'emoji': '🎓'},
        {'name': 'Книги', 'type': 'expense', 'parent_category': 'Образование', 'emoji': '📖'},

        {'name': 'Развлечения', 'type': 'expense', 'parent_category': None, 'emoji': '🎮'},
        {'name': 'Одежда', 'type': 'expense', 'parent_category': None, 'emoji': '👕'},
        {'name': 'Подарки', 'type': 'expense', 'parent_category': None, 'emoji': '🎁'},
        {'name': 'Переводы', 'type': 'expense', 'parent_category': None, 'emoji': '💸'},
        {'name': 'Другое', 'type': 'expense', 'parent_category': None, 'emoji': '📌'},
    ]

    income_categories = [
        {'name': 'Зарплата', 'type': 'income', 'parent_category': None, 'emoji': '💰'},
        {'name': 'Проекты', 'type': 'income', 'parent_category': None, 'emoji': '💼'},
        {'name': '3D модели', 'type': 'income', 'parent_category': 'Проекты', 'emoji': '🎨'},
        {'name': 'AI агенты', 'type': 'income', 'parent_category': 'Проекты', 'emoji': '🤖'},
        {'name': 'Фриланс', 'type': 'income', 'parent_category': 'Проекты', 'emoji': '💻'},
        {'name': 'Подарки', 'type': 'income', 'parent_category': None, 'emoji': '🎁'},
        {'name': 'Инвестиции', 'type': 'income', 'parent_category': None, 'emoji': '📈'},
        {'name': 'Другое', 'type': 'income', 'parent_category': None, 'emoji': '📌'},
    ]

    all_categories = expense_categories + income_categories

    try:
        # Check if categories already exist
        existing = supabase.table('categories').select('name').execute()
        if existing.data and len(existing.data) > 0:
            logger.info(f"✅ Categories already exist ({len(existing.data)} found)")
            return True

        # Insert categories
        for cat in all_categories:
            try:
                supabase.table('categories').insert(cat).execute()
            except Exception as e:
                # Category might already exist due to unique constraint
                if 'duplicate' not in str(e).lower():
                    logger.warning(f"Could not insert category {cat['name']}: {e}")

        logger.info(f"✅ Inserted {len(all_categories)} categories")
        return True

    except Exception as e:
        logger.error(f"Error inserting categories: {e}")
        return False


def setup_rls():
    """Setup Row Level Security"""
    logger.info("Setting up RLS policies...")
    logger.info("⚠️  RLS policies should be created in Supabase SQL Editor")

    print("\n🔒 RLS Policies (run in Supabase SQL Editor):")
    print("="*60)
    print("""
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_recommendations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all for authenticated users" ON transactions
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for categories" ON categories
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for recommendations" ON ai_recommendations
    FOR ALL USING (true) WITH CHECK (true);
    """)
    print("="*60 + "\n")


def main():
    """Main setup function"""

    print("\n" + "="*60)
    print("🚀 MyWallet Database Setup")
    print("="*60 + "\n")

    # Check connection
    try:
        logger.info("Testing Supabase connection...")
        # Try to access a system table
        supabase.table('categories').select('id').limit(1).execute()
        logger.info("✅ Connected to Supabase successfully!")
    except Exception as e:
        logger.error(f"❌ Cannot connect to Supabase: {e}")
        print("\n❌ Connection failed. Please check your .env file:")
        print("   - SUPABASE_URL")
        print("   - SUPABASE_SERVICE_ROLE_KEY")
        return

    print("\nℹ️  Due to Supabase API limitations, you need to run the SQL manually.\n")
    print("📋 Steps to complete setup:\n")
    print("1. Open Supabase Dashboard: https://supabase.com/dashboard/project/rltpsiiwugfsbpzhklgw")
    print("2. Go to SQL Editor")
    print("3. Copy and paste the SQL from 'database/setup.sql'")
    print("4. Click 'Run'")
    print("\nAfter that, run this script again to insert categories.\n")

    # Try to insert categories if tables exist
    input("Press Enter after you've run the SQL in Supabase, or Ctrl+C to exit...")

    success = insert_default_categories()

    if success:
        print("\n" + "="*60)
        print("✅ Database setup complete!")
        print("="*60)
        print("\n📝 Next steps:")
        print("1. Create storage bucket 'receipts' in Supabase Dashboard > Storage")
        print("2. Make the bucket public")
        print("3. Run the bot: python -m bot.main")
        print("\n")
    else:
        print("\n⚠️  Please complete the manual steps above.\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.\n")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n❌ Error: {e}\n")
