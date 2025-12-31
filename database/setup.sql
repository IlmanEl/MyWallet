-- MyWallet Database Setup Script
-- Run this in your Supabase SQL Editor

-- ==========================================
-- 1. CREATE TABLES
-- ==========================================

-- Transactions table
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

-- Categories table
CREATE TABLE IF NOT EXISTS categories (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
    parent_category VARCHAR(100),
    emoji VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(name, type)
);

-- AI Recommendations table
CREATE TABLE IF NOT EXISTS ai_recommendations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_telegram_id BIGINT NOT NULL,
    recommendation_text TEXT NOT NULL,
    category VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_read BOOLEAN DEFAULT FALSE
);

-- ==========================================
-- 2. CREATE INDEXES
-- ==========================================

CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_telegram_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);
CREATE INDEX IF NOT EXISTS idx_recommendations_user_id ON ai_recommendations(user_telegram_id);

-- ==========================================
-- 3. CREATE STORAGE BUCKET FOR RECEIPTS
-- ==========================================

-- Run this in the Supabase dashboard under Storage
-- Or use the Supabase UI to create a bucket named 'receipts' with public access

-- Insert this if you want to do it via SQL (may require admin privileges):
-- INSERT INTO storage.buckets (id, name, public) VALUES ('receipts', 'receipts', true);

-- ==========================================
-- 4. INSERT DEFAULT CATEGORIES
-- ==========================================

-- Expense categories
INSERT INTO categories (name, type, parent_category, emoji) VALUES
    ('Еда и напитки', 'expense', NULL, '🍔'),
    ('Рестораны', 'expense', 'Еда и напитки', '🍽️'),
    ('Продукты', 'expense', 'Еда и напитки', '🛒'),
    ('Кафе', 'expense', 'Еда и напитки', '☕'),

    ('Транспорт', 'expense', NULL, '🚗'),
    ('Такси', 'expense', 'Транспорт', '🚕'),
    ('Общественный транспорт', 'expense', 'Транспорт', '🚌'),
    ('Бензин', 'expense', 'Транспорт', '⛽'),

    ('Здоровье', 'expense', NULL, '🏥'),
    ('Аптеки', 'expense', 'Здоровье', '💊'),
    ('Врачи', 'expense', 'Здоровье', '👨‍⚕️'),
    ('Анализы', 'expense', 'Здоровье', '🔬'),

    ('Дом', 'expense', NULL, '🏠'),
    ('Коммунальные услуги', 'expense', 'Дом', '💡'),
    ('Ремонт', 'expense', 'Дом', '🔨'),
    ('Мебель', 'expense', 'Дом', '🛋️'),

    ('Работа/Бизнес', 'expense', NULL, '💼'),
    ('Материалы', 'expense', 'Работа/Бизнес', '📦'),
    ('Инструменты', 'expense', 'Работа/Бизнес', '🔧'),
    ('Партнерам', 'expense', 'Работа/Бизнес', '🤝'),

    ('Образование', 'expense', NULL, '📚'),
    ('Курсы', 'expense', 'Образование', '🎓'),
    ('Книги', 'expense', 'Образование', '📖'),

    ('Развлечения', 'expense', NULL, '🎮'),
    ('Одежда', 'expense', NULL, '👕'),
    ('Подарки', 'expense', NULL, '🎁'),
    ('Переводы', 'expense', NULL, '💸'),
    ('Другое', 'expense', NULL, '📌')
ON CONFLICT (name, type) DO NOTHING;

-- Income categories
INSERT INTO categories (name, type, parent_category, emoji) VALUES
    ('Зарплата', 'income', NULL, '💰'),
    ('Проекты', 'income', NULL, '💼'),
    ('3D модели', 'income', 'Проекты', '🎨'),
    ('AI агенты', 'income', 'Проекты', '🤖'),
    ('Фриланс', 'income', 'Проекты', '💻'),
    ('Подарки', 'income', NULL, '🎁'),
    ('Инвестиции', 'income', NULL, '📈'),
    ('Другое', 'income', NULL, '📌')
ON CONFLICT (name, type) DO NOTHING;

-- ==========================================
-- 5. ROW LEVEL SECURITY (RLS) POLICIES
-- ==========================================

-- Enable RLS
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_recommendations ENABLE ROW LEVEL SECURITY;

-- For single-user mode, you can use simple policies
-- Or disable RLS and rely on application-level security

-- Policy: Allow all operations for authenticated users (adjust as needed)
CREATE POLICY "Allow all for authenticated users" ON transactions
    FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Allow all for categories" ON categories
    FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Allow all for recommendations" ON ai_recommendations
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- ==========================================
-- 6. COMPLETION MESSAGE
-- ==========================================

-- Database setup complete!
-- Next steps:
-- 1. Create storage bucket 'receipts' in Supabase Dashboard (Storage section)
-- 2. Make the bucket public for receipt image access
-- 3. Update your .env file with SUPABASE_URL and SUPABASE_KEY
