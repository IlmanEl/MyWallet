"""
Скрипт для автоматического исправления критичных багов
"""
import re

def fix_photo_handler():
    """Исправить валюту в photo_handler.py"""
    file_path = '/Users/ilman/Desktop/MyWallet/bot/handlers/photo_handler.py'

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Добавить импорт если его нет
    if 'from utils.helpers import get_currency_symbol' not in content:
        content = content.replace(
            'from utils.config import Config',
            'from utils.config import Config\nfrom utils.helpers import get_currency_symbol'
        )

    # Заменить захардкоженную валюту
    content = re.sub(
        r'💸 Сумма: \{transaction\.amount\} грн',
        r'💸 Сумма: {transaction.amount} {get_currency_symbol(transaction.currency)}',
        content
    )

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ photo_handler.py исправлен")

def fix_transaction_handler():
    """Исправить валюту в transaction_handler.py"""
    file_path = '/Users/ilman/Desktop/MyWallet/bot/handlers/transaction_handler.py'

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Добавить импорт если его нет
    if 'from utils.helpers import get_currency_symbol' not in content:
        content = content.replace(
            'from utils.helpers import get_date_range, format_currency, format_date',
            'from utils.helpers import get_date_range, format_currency, format_date, get_currency_symbol'
        )

    # Заменить захардкоженную валюту
    content = re.sub(
        r'\{type_emoji\} \{type_text\}: \{transaction\.amount\} грн',
        r'{type_emoji} {type_text}: {transaction.amount} {get_currency_symbol(parsed.get("currency", "UAH"))}',
        content
    )

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ transaction_handler.py исправлен")

def add_amount_validation():
    """Добавить валидацию суммы в transaction_handler.py"""
    file_path = '/Users/ilman/Desktop/MyWallet/bot/handlers/transaction_handler.py'

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Найти функцию receive_amount и добавить валидацию
    new_lines = []
    for i, line in enumerate(lines):
        new_lines.append(line)

        if 'amount = float(update.message.text.replace' in line:
            # Добавить валидацию после этой строки
            indent = '        '
            validation = f'''
{indent}# Валидация
{indent}if amount <= 0:
{indent}    await update.message.reply_text(
{indent}        "❌ Сумма должна быть больше нуля. Попробуйте еще раз:"
{indent}    )
{indent}    return AMOUNT

{indent}if amount > 1_000_000_000:
{indent}    await update.message.reply_text(
{indent}        "❌ Сумма слишком большая. Попробуйте еще раз:"
{indent}    )
{indent}    return AMOUNT

'''
            new_lines.append(validation)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print("✅ Добавлена валидация сумм")

if __name__ == '__main__':
    print("🔧 Начинаю исправление багов...")

    fix_photo_handler()
    fix_transaction_handler()
    add_amount_validation()

    print("\n✅ Все критичные баги исправлены!")
