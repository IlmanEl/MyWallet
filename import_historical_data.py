

import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
USER_TELEGRAM_ID = os.getenv('TELEGRAM_USER_ID', '123456789')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def add_transaction(amount, type_trans, category, description, project=None, payment_method=None):
    """Добавить транзакцию в базу данных"""
    try:
        transaction = {
            'user_telegram_id': int(USER_TELEGRAM_ID),
            'amount': abs(float(amount)),
            'type': type_trans,
            'category': category,
            'description': description,
            'date': '2025-01-01T00:00:00Z',  # 2025 год в формате timestamp
            'project': project,
            'payment_method': payment_method,
            'ai_categorized': False
        }

        result = supabase.table('transactions').insert(transaction).execute()
        logger.info(f"✅ {type_trans}: {amount} грн - {description[:40]}")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка: {e} | {description[:40]}")
        return False


def import_all_data():
    """Импорт всех исторических данных"""
    print("\n" + "="*60)
    print("🚀 Импорт исторических данных за 2025 год")
    print("="*60 + "\n")

    total_count = 0

    # ========== ПРОЕКТ 3D МОДЕЛИ ==========
    logger.info("📦 Проект 3D моделей...")

    add_transaction(42000, 'income', '3D модели', 'Оплата за 3D модели - первая часть (42,000)', project='3D Модели')
    add_transaction(2000, 'expense', 'Партнерам', 'Предоплата Халису на материалы', payment_method='Перевод')
    add_transaction(15000, 'expense', 'Партнерам', 'Доля Халиса из первых 20,000', project='3D Модели', payment_method='Перевод')
    add_transaction(1000, 'expense', 'Переводы', 'Рахиму', payment_method='Наличные')
    add_transaction(4000, 'expense', 'Материалы', 'AliExpress', payment_method='Карта')
    add_transaction(4000, 'expense', 'Партнерам', 'Доля Халиса из вторых 20,000', project='3D Модели', payment_method='Перевод')
    add_transaction(1200, 'expense', 'Кафе', 'Кафе с французами', payment_method='Наличные')
    add_transaction(4800, 'expense', 'Курсы', 'Оплата обучения + ежемесячные платы', payment_method='Карта')
    add_transaction(1000, 'expense', 'Материалы', 'Доставка Аль Акса + чайный набор AliExpress', payment_method='Карта')
    add_transaction(47671, 'income', '3D модели', 'Финальная оплата за 3D модели (47,671)', project='3D Модели')
    add_transaction(671, 'expense', 'Переводы', 'Себе на карту', payment_method='Перевод')
    add_transaction(446, 'expense', 'Партнерам', 'Халису', payment_method='Перевод')
    add_transaction(262, 'expense', 'Такси', 'Такси', payment_method='Наличные')
    add_transaction(20000, 'expense', 'Партнерам', 'Доля Халиса (20,000)', project='3D Модели', payment_method='Перевод')
    add_transaction(17000, 'expense', 'Партнерам', 'Доля Халиса из моих 27,000', project='3D Модели', payment_method='Перевод')
    total_count += 15

    # ========== ОБЩИЕ РАСХОДЫ ==========
    logger.info("💸 Общие расходы...")

    add_transaction(1400, 'expense', 'Рестораны', 'Плов узбекский', payment_method='Наличные')
    add_transaction(300, 'expense', 'Рестораны', 'KFC', payment_method='Наличные')
    add_transaction(1000, 'expense', 'Переводы', 'Рахиму', payment_method='Наличные')
    add_transaction(2000, 'expense', 'Переводы', 'Вернуть Адаму лишние 50 долларов', payment_method='Наличные')
    add_transaction(1000, 'expense', 'Одежда', 'Чистка пальто', payment_method='Наличные')
    add_transaction(300, 'expense', 'Другое', 'Общие расходы, транспорт', payment_method='Наличные')
    add_transaction(850, 'expense', 'Ремонт', 'Наконечник рычага ходового Соната', payment_method='Наличные')
    add_transaction(409, 'expense', 'Врачи', 'Врач ЛОР', payment_method='Наличные')
    add_transaction(591, 'expense', 'Переводы', 'Остаток от 1000 грн на карту', payment_method='Перевод')
    add_transaction(1200, 'expense', 'Переводы', 'Наличные на карту', payment_method='Перевод')
    add_transaction(1700, 'expense', 'Анализы', 'Анализы крови', payment_method='Карта')
    add_transaction(300, 'income', 'Подарки', 'Ваня дал на врача', payment_method='Наличные')
    add_transaction(2000, 'expense', 'Переводы', 'Наличные на карту', payment_method='Перевод')
    add_transaction(1344, 'expense', 'Другое', 'Чай, такси, плов', payment_method='Карта')
    add_transaction(1000, 'expense', 'Аптеки', 'Лекарства', payment_method='Наличные')
    add_transaction(1000, 'expense', 'Развлечения', 'Отдых', payment_method='Наличные')
    add_transaction(300, 'expense', 'Кафе', 'Чай', payment_method='Наличные')
    add_transaction(2000, 'expense', 'Переводы', 'Рахиму', payment_method='Наличные')
    total_count += 18

    # ========== ГЕНЕТИКА (первая оплата) ==========
    logger.info("🧬 Генетика...")

    add_transaction(4587, 'income', 'Фриланс', 'Работа генетика', project='Генетика')
    add_transaction(4700, 'expense', 'Переводы', 'На карту (курсы 3900 + купол скалы 700)', payment_method='Перевод')
    add_transaction(300, 'expense', 'Одежда', 'Забрать пальто', payment_method='Наличные')
    add_transaction(200, 'expense', 'Рестораны', 'Плов узбекский', payment_method='Наличные')
    add_transaction(1000, 'expense', 'Другое', 'Траты по мелочам', payment_method='Наличные')
    add_transaction(1808, 'expense', 'Другое', 'Аптеки, проезды, такси, подписки, плов', payment_method='Карта')
    add_transaction(300, 'expense', 'Другое', 'Пополнение счета телефона', payment_method='Наличные')
    add_transaction(124, 'expense', 'Кафе', 'Чай Комфорт Таун', payment_method='Карта')
    add_transaction(500, 'expense', 'Продукты', 'Сухофрукты', payment_method='Наличные')
    total_count += 9

    # ========== AI AGENT ПРОЕКТ ==========
    logger.info("🤖 AI Agent проект...")

    add_transaction(41800, 'income', 'AI агенты', 'Оплата за AI agent референдум', project='AI Agent')
    add_transaction(11000, 'expense', 'Переводы', 'Закрытие долга по Жеке', payment_method='Перевод')
    add_transaction(3000, 'expense', 'Переводы', 'Даше', payment_method='Перевод')
    add_transaction(1000, 'expense', 'Переводы', 'Отцу', payment_method='Перевод')
    add_transaction(300, 'expense', 'Транспорт', 'Машина (бензин/мойка)', payment_method='Наличные')
    add_transaction(300, 'expense', 'Другое', 'Пополнение счета телефона', payment_method='Наличные')
    total_count += 6

    # ========== РАСХОДЫ МАЙ ==========
    logger.info("💸 Расходы май...")

    add_transaction(2000, 'expense', 'Переводы', 'Наличные на карту', payment_method='Перевод')
    add_transaction(200, 'expense', 'Переводы', 'Отцу с карты', payment_method='Карта')
    add_transaction(254, 'expense', 'Аптеки', 'Мазь', payment_method='Карта')
    add_transaction(300, 'expense', 'Кафе', 'Чай', payment_method='Наличные')
    add_transaction(1200, 'expense', 'Транспорт', 'Менять колеса Соната', payment_method='Наличные')
    add_transaction(200, 'expense', 'Транспорт', 'Резинки дворники Соната', payment_method='Наличные')
    add_transaction(400, 'expense', 'Транспорт', 'Развал-схождение этап 1', payment_method='Наличные')
    add_transaction(40, 'expense', 'Общественный транспорт', 'Автобусы 4 раза', payment_method='Наличные')
    add_transaction(87, 'expense', 'Продукты', 'Бабушке хлеб молоко', payment_method='Наличные')
    add_transaction(74.99, 'expense', 'Кафе', 'Сито кафейня', payment_method='Карта')
    add_transaction(115, 'expense', 'Другое', 'Подписка Google', payment_method='Карта')
    add_transaction(8, 'expense', 'Другое', 'Комиссия Temu', payment_method='Карта')
    add_transaction(99.96, 'expense', 'Продукты', 'БРСМ сырки', payment_method='Карта')
    add_transaction(380, 'expense', 'Рестораны', 'Рестик с Абдиком', payment_method='Наличные')
    add_transaction(100, 'expense', 'Переводы', 'Наличные на карту', payment_method='Перевод')
    total_count += 15

    # ========== ГЕНЕТИКА (вторая оплата) ==========
    logger.info("🧬 Генетика 2...")

    add_transaction(4646, 'income', 'Фриланс', 'Работа генетика', project='Генетика')
    add_transaction(3471, 'expense', 'Материалы', 'AliExpress', payment_method='Карта')
    add_transaction(195, 'expense', 'Такси', 'Такси', payment_method='Карта')
    add_transaction(47.50, 'expense', 'Продукты', 'Вода', payment_method='Наличные')
    add_transaction(20, 'expense', 'Другое', 'Мелкие расходы', payment_method='Наличные')
    add_transaction(1900, 'expense', 'Переводы', 'Малику на карту', payment_method='Перевод')
    add_transaction(2000, 'income', 'Другое', 'Малик дал наличкой', payment_method='Наличные')
    add_transaction(20, 'expense', 'Переводы', 'Малику доп', payment_method='Наличные')
    add_transaction(70, 'income', 'Подарки', 'Мама скинула', payment_method='Перевод')
    add_transaction(84, 'expense', 'Другое', 'Подписка Google', payment_method='Карта')
    total_count += 10

    # ========== МЕЧЕТЬ ПРОРОКА ==========
    logger.info("🕌 Мечеть Пророка...")

    add_transaction(10000, 'income', '3D модели', 'Адам дал Халису (моя доля не учтена)', project='Мечеть Пророка')
    add_transaction(10000, 'income', '3D модели', 'Моя доля первая часть', project='Мечеть Пророка')
    add_transaction(2000, 'expense', 'Материалы', 'Доп материал Халису', payment_method='Перевод')
    add_transaction(1000, 'expense', 'Переводы', 'Рахиму', payment_method='Наличные')
    add_transaction(20000, 'income', '3D модели', 'Адам финальная оплата', project='Мечеть Пророка')
    add_transaction(4000, 'income', '3D модели', 'Адам скинул на карту доп', project='Мечеть Пророка', payment_method='Перевод')
    add_transaction(5000, 'expense', 'Переводы', 'Себе на карту', payment_method='Перевод')
    add_transaction(15000, 'expense', 'Партнерам', 'Халису финальная доля', project='Мечеть Пророка', payment_method='Перевод')
    total_count += 8

    # ========== РАСХОДЫ ИЮЛЬ-АВГУСТ ==========
    logger.info("💸 Расходы июль-август...")

    add_transaction(1800, 'expense', 'Ремонт', 'Сантехнику', payment_method='Наличные')
    add_transaction(300, 'expense', 'Рестораны', 'Шурпа', payment_method='Наличные')
    add_transaction(247, 'expense', 'Другое', 'Подписка Apple, проезд', payment_method='Карта')
    add_transaction(293, 'expense', 'Другое', 'Новая почта доставка', payment_method='Карта')
    add_transaction(5000, 'income', 'Другое', 'Обменял 100$ + 1000 грн налички', payment_method='Перевод')
    add_transaction(3900, 'expense', 'Курсы', 'Оплата курсов', payment_method='Карта')
    add_transaction(150, 'expense', 'Рестораны', 'Плов Ташкент', payment_method='Наличные')
    add_transaction(500, 'expense', 'Продукты', 'Курица', payment_method='Наличные')
    add_transaction(245, 'expense', 'Такси', 'Такси', payment_method='Карта')
    add_transaction(263, 'expense', 'Такси', 'Такси', payment_method='Карта')
    add_transaction(170, 'expense', 'Развлечения', 'Баня', payment_method='Карта')
    add_transaction(115, 'expense', 'Развлечения', 'Баня', payment_method='Карта')
    add_transaction(1784, 'income', 'Другое', 'Возврат с AliExpress', payment_method='Карта')
    add_transaction(1913, 'expense', 'Материалы', 'AliExpress', payment_method='Карта')
    total_count += 14

    # ========== РАСХОДЫ СЕНТЯБРЬ-ОКТЯБРЬ ==========
    logger.info("💸 Расходы сентябрь-октябрь...")

    add_transaction(350, 'expense', 'Переводы', 'На карту', payment_method='Перевод')
    add_transaction(1000, 'expense', 'Переводы', 'На карту', payment_method='Перевод')
    add_transaction(205, 'expense', 'Продукты', 'Novus продукты', payment_method='Карта')
    add_transaction(46, 'expense', 'Рестораны', 'Novus Адель', payment_method='Карта')
    add_transaction(358, 'expense', 'Коммунальные услуги', 'Провайдер', payment_method='Карта')
    add_transaction(150, 'expense', 'Рестораны', 'Нур поесть', payment_method='Наличные')
    add_transaction(16, 'expense', 'Общественный транспорт', 'Автобусы', payment_method='Наличные')
    add_transaction(185, 'expense', 'Такси', 'Такси Миком Палас', payment_method='Карта')
    add_transaction(500, 'expense', 'Рестораны', 'Малику и Анжеле пятница', payment_method='Наличные')
    add_transaction(50, 'income', 'Другое', 'Абдик скинул', payment_method='Перевод')
    add_transaction(400, 'expense', 'Продукты', 'Фора, к Бабуру', payment_method='Наличные')
    total_count += 11

    # ========== УНИВЕРСИТЕТ (ДЕКАБРЬ) ==========
    logger.info("🏛️ Университет...")

    add_transaction(1800, 'income', '3D модели', 'Предоплата университет 1800$', project='Университет', payment_method='USD')
    add_transaction(8500, 'expense', 'Материалы', 'Халису материал (из 1800$)', payment_method='Перевод')
    add_transaction(5000, 'expense', 'Материалы', 'Халису материал (из 1800$)', payment_method='Перевод')
    add_transaction(2000, 'expense', 'Переводы', 'Рахиму', payment_method='Наличные')
    add_transaction(2500, 'expense', 'Переводы', 'Рахиму', payment_method='Наличные')
    total_count += 5

    print("\n" + "="*60)
    print(f"✅ Импортировано транзакций: {total_count}")
    print("="*60 + "\n")

    # Расчет итогов
    logger.info("📊 Подсчет итогов...")

    try:
        all_transactions = supabase.table('transactions').select('*').eq('user_telegram_id', int(USER_TELEGRAM_ID)).execute()

        total_income = sum(t['amount'] for t in all_transactions.data if t['type'] == 'income')
        total_expense = sum(t['amount'] for t in all_transactions.data if t['type'] == 'expense')
        balance = total_income - total_expense

        print("\n📈 ИТОГОВАЯ СТАТИСТИКА:")
        print("="*60)
        print(f"💰 Доходы:  {total_income:,.2f} грн")
        print(f"💸 Расходы: {total_expense:,.2f} грн")
        print(f"💵 Баланс:  {balance:,.2f} грн")
        print("="*60 + "\n")

    except Exception as e:
        logger.error(f"Ошибка подсчета: {e}")


if __name__ == '__main__':
    try:
        import_all_data()
    except KeyboardInterrupt:
        print("\n\n❌ Отменено\n")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        print(f"\n❌ Ошибка: {e}\n")
