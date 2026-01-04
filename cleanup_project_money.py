"""
Скрипт для удаления проектных денег из базы
Оставляем только личные доходы и расходы
"""
from services.database import db
from utils.config import Config

def cleanup_project_transactions():
    """Удаляем проектные транзакции"""

    print("🧹 Начинаем очистку проектных транзакций...")

    # Получаем все транзакции
    all_transactions = db.get_transactions(
        user_id=Config.USER_TELEGRAM_ID,
        limit=10000
    )

    print(f"📊 Всего транзакций: {len(all_transactions)}")

    deleted_count = 0

    for t in all_transactions:
        should_delete = False

        # 1. Удаляем 1800$ проектных
        if (t.get('amount') == 1800.0 and
            t.get('currency') == 'USD' and
            'университета' in t.get('description', '').lower()):
            should_delete = True
            print(f"❌ Удаляем: 1800$ проектных - {t.get('description')}")

        # 2. Удаляем ВСЕ переводы партнерам (это распределение проектных денег)
        if t.get('category') == 'Партнерам':
            should_delete = True
            print(f"❌ Удаляем: Перевод партнерам - {t.get('amount')} {t.get('currency')} - {t.get('description')}")

        if should_delete:
            db.delete_transaction(t['id'])
            deleted_count += 1

    print(f"\n✅ Удалено транзакций: {deleted_count}")
    print(f"📊 Осталось транзакций: {len(all_transactions) - deleted_count}")

    # Проверяем новый баланс
    print("\n💰 Новый баланс:")
    balances = db.get_balance(Config.USER_TELEGRAM_ID)

    for currency, data in balances.items():
        print(f"\n{currency}:")
        print(f"  Доход: {data['income']:.2f}")
        print(f"  Расход: {data['expense']:.2f}")
        print(f"  Баланс: {data['balance']:.2f}")
        if 'card_balance' in data:
            print(f"  На карте: {data['card_balance']:.2f}")
            print(f"  Наличкой: {data['cash_balance']:.2f}")

if __name__ == '__main__':
    Config.validate()
    cleanup_project_transactions()
