# 🚀 MyWallet - Финальная настройка (2 минуты)

## Все готово! Осталось только создать таблицы в Supabase

### Шаг 1: Открыть SQL Editor в Supabase

**Кликните эту ссылку:**
https://supabase.com/dashboard/project/rltpsiiwugfsbpzhklgw/sql/new

### Шаг 2: Скопировать и вставить SQL

Скопируйте **весь** SQL код ниже и вставьте в SQL Editor:

```sql
-- MyWallet Database Setup
-- ========================================

-- 1. CREATE TABLES
-- ========================================

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

CREATE TABLE IF NOT EXISTS categories (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
    parent_category VARCHAR(100),
    emoji VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(name, type)
);

CREATE TABLE IF NOT EXISTS ai_recommendations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_telegram_id BIGINT NOT NULL,
    recommendation_text TEXT NOT NULL,
    category VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_read BOOLEAN DEFAULT FALSE
);

-- 2. CREATE INDEXES
-- ========================================

CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_telegram_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);
CREATE INDEX IF NOT EXISTS idx_recommendations_user_id ON ai_recommendations(user_telegram_id);

-- 3. INSERT DEFAULT CATEGORIES
-- ========================================

INSERT INTO categories (name, type, parent_category, emoji) VALUES
    -- Расходы
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
    ('Другое', 'expense', NULL, '📌'),

    -- Доходы
    ('Зарплата', 'income', NULL, '💰'),
    ('Проекты', 'income', NULL, '💼'),
    ('3D модели', 'income', 'Проекты', '🎨'),
    ('AI агенты', 'income', 'Проекты', '🤖'),
    ('Фриланс', 'income', 'Проекты', '💻'),
    ('Подарки', 'income', NULL, '🎁'),
    ('Инвестиции', 'income', NULL, '📈'),
    ('Другое', 'income', NULL, '📌')
ON CONFLICT (name, type) DO NOTHING;

-- 4. ENABLE ROW LEVEL SECURITY
-- ========================================

ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_recommendations ENABLE ROW LEVEL SECURITY;

-- 5. CREATE RLS POLICIES
-- ========================================

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
```

### Шаг 3: Нажать "Run" (или Ctrl+Enter)

Вы увидите сообщение "Success. No rows returned" - это нормально!

### Шаг 4: Создать Storage Bucket (опционально, для чеков)

1. Открыть: https://supabase.com/dashboard/project/rltpsiiwugfsbpzhklgw/storage/buckets
2. Нажать "New bucket"
3. Имя: `receipts`
4. Выбрать "Public bucket"
5. Создать

### Шаг 5: Запустить бота!

```bash
python3 -m bot.main
```

## Готово!

Откройте Telegram, найдите вашего бота и отправьте `/start`

---

**Токен бота:** `8432998445:AAFdrBKFc9Q6xSEhSNWr4ZEuD60tWde4pnY`
**Ваш Telegram ID:** `393832759`

Попробуйте написать: "Потратил 500 на такси" 🚀
