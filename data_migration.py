"""
Data Migration Script for MyWallet
Imports financial transactions from unstructured notes
"""

import json
import logging
from datetime import datetime
from openai import OpenAI
from services.database import db
from services.categorization_service import categorization_service
from utils.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=Config.OPENAI_API_KEY)


def parse_notes_with_ai(notes_text: str) -> list:
    """Parse unstructured notes using GPT-4"""

    expense_categories = categorization_service.get_available_categories('expense')
    income_categories = categorization_service.get_available_categories('income')
    all_categories = expense_categories + income_categories
    categories_str = ", ".join(all_categories)

    prompt = f"""Ты парсишь финансовые заметки на русском/украинском языке.

Заметки:
{notes_text}

Доступные категории: {categories_str}

Извлеки все финансовые транзакции и верни их в виде JSON массива.

Для каждой транзакции определи:
- amount: сумма в числовом формате
- type: "income" или "expense"
- category: наиболее подходящая категория из списка
- description: краткое описание (кому/за что)
- date: null (так как дат нет в записях)
- project: название проекта, если упоминается (например "3D модели", "Мечеть Пророка", "Университет")
- payment_method: "cash" если наличка, "card" если карта, "transfer" если перевод

Особенности:
- "минус" или знак "-" означает расход (expense)
- "плюс" или "+" означает доход (income)
- Суммы типа "15 000" = 15000
- Если сумма передается кому-то (например "15 000 халису") - это расход, категория "Переводы"
- Если получили (например "получили 42000") - это доход
- "налички" или "наличкой" = payment_method: "cash"
- "с карты" или "на карту" = payment_method: "card"
- Переводы между счетами (налички на карту) - пропускай
- Проекты: "3д модели", "Мечеть Пророка", "модель университета", "AI agent", "генетики"

Верни JSON массив в формате:
[
  {{
    "amount": 15000,
    "type": "expense",
    "category": "Переводы",
    "description": "Халису",
    "date": "2024-12-15",
    "project": "3D модели"
  }},
  ...
]

Важно: Верни ТОЛЬКО валидный JSON массив, без дополнительного текста."""

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content

        # Try to extract JSON array
        json_start = content.find('[')
        json_end = content.rfind(']') + 1

        if json_start >= 0 and json_end > json_start:
            json_str = content[json_start:json_end]
            transactions = json.loads(json_str)
            logger.info(f"Parsed {len(transactions)} transactions")
            return transactions
        else:
            # Try to parse entire content as JSON object with transactions key
            data = json.loads(content)
            if 'transactions' in data:
                return data['transactions']
            elif isinstance(data, list):
                return data
            else:
                logger.error("No transactions array found in response")
                return []

    except Exception as e:
        logger.error(f"Error parsing notes: {e}")
        return []


def import_transactions(transactions: list, user_telegram_id: int) -> int:
    """Import parsed transactions to database"""

    imported_count = 0

    for t in transactions:
        try:
            transaction_data = {
                'amount': float(t.get('amount', 0)),
                'type': t.get('type', 'expense'),
                'category': t.get('category', 'Другое'),
                'description': t.get('description', ''),
                'user_telegram_id': user_telegram_id,
                'ai_categorized': True,
            }

            # Add project if specified
            if t.get('project'):
                transaction_data['project'] = t['project']

            # Parse date
            if t.get('date'):
                try:
                    transaction_data['date'] = datetime.strptime(t['date'], '%Y-%m-%d').isoformat()
                except:
                    transaction_data['date'] = datetime.now().isoformat()
            else:
                transaction_data['date'] = datetime.now().isoformat()

            # Import to database
            db.add_transaction(transaction_data)
            imported_count += 1

            logger.info(f"Imported: {t.get('type')} {t.get('amount')} грн - {t.get('description')}")

        except Exception as e:
            logger.error(f"Error importing transaction {t}: {e}")
            continue

    return imported_count


def main():
    """Main migration function"""

    print("\n=== MyWallet Data Migration ===\n")

    # Read notes file
    notes_file = input("Введите путь к файлу с заметками (или 'my_notes.txt'): ").strip()
    if not notes_file:
        notes_file = 'my_notes.txt'

    try:
        with open(notes_file, 'r', encoding='utf-8') as f:
            notes_text = f.read()
    except FileNotFoundError:
        print(f"\nОшибка: Файл {notes_file} не найден.")
        print("Создайте файл с вашими заметками и запустите скрипт снова.")
        return

    print(f"\nЧитаем заметки из {notes_file}...")
    print(f"Найдено {len(notes_text)} символов текста.\n")

    # Confirm
    print("ВНИМАНИЕ: Это действие добавит транзакции в базу данных.")
    confirm = input("Продолжить? (yes/no): ").strip().lower()

    if confirm != 'yes':
        print("Миграция отменена.")
        return

    print("\nПарсинг заметок с помощью AI...")
    transactions = parse_notes_with_ai(notes_text)

    if not transactions:
        print("\nНе удалось извлечь транзакции из заметок.")
        return

    print(f"\nНайдено {len(transactions)} транзакций.\n")

    # Show preview
    print("Предпросмотр первых 5 транзакций:")
    for i, t in enumerate(transactions[:5], 1):
        type_text = "Доход" if t['type'] == 'income' else "Расход"
        print(f"{i}. {type_text}: {t['amount']} грн - {t.get('description')} ({t.get('category')})")

    if len(transactions) > 5:
        print(f"... и еще {len(transactions) - 5} транзакций\n")

    # Final confirmation
    confirm = input("\nИмпортировать эти транзакции? (yes/no): ").strip().lower()

    if confirm != 'yes':
        print("Миграция отменена.")
        return

    # Import
    print("\nИмпортирую транзакции...")
    imported = import_transactions(transactions, Config.USER_TELEGRAM_ID)

    print(f"\n✅ Успешно импортировано {imported} из {len(transactions)} транзакций!")
    print("\nОткройте бот в Telegram и проверьте результат командой /balance или /stats")


if __name__ == '__main__':
    try:
        Config.validate()
        main()
    except ValueError as e:
        print(f"\nОшибка конфигурации: {e}")
        print("Проверьте файл .env")
    except KeyboardInterrupt:
        print("\n\nМиграция прервана пользователем.")
