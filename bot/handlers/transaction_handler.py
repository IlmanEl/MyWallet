from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from bot.keyboards.inline_keyboards import Keyboards
from services.database import db
from services.categorization_service import categorization_service
from services.ai_service import ai_service
from models.transaction import Transaction
from utils.config import Config
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Conversation states
AMOUNT, CURRENCY, CATEGORY, DESCRIPTION, PAYMENT_METHOD = range(5)


async def add_expense_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding expense"""
    query = update.callback_query
    await query.answer()

    context.user_data['transaction_type'] = 'expense'

    await query.edit_message_text(
        "💸 Добавление расхода\n\nВведите сумму (например: 500 или 1200.50):"
    )

    return AMOUNT


async def add_income_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding income"""
    query = update.callback_query
    await query.answer()

    context.user_data['transaction_type'] = 'income'

    await query.edit_message_text(
        "💰 Добавление дохода\n\nВведите сумму (например: 5000 или 10000.00):"
    )

    return AMOUNT


async def receive_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive amount from user"""
    try:
        amount = float(update.message.text.replace(',', '.').replace(' ', ''))
        context.user_data['amount'] = amount

        await update.message.reply_text(
            f"Сумма: {amount}\n\nВыберите валюту:",
            reply_markup=Keyboards.currency_selection()
        )

        return CURRENCY

    except ValueError:
        await update.message.reply_text(
            "Некорректная сумма. Попробуйте еще раз (например: 500 или 1200.50):"
        )
        return AMOUNT


async def receive_currency_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive currency selection and ask for description"""
    query = update.callback_query
    await query.answer()

    currency_map = {
        'currency_uah': 'UAH',
        'currency_usd': 'USD',
        'currency_eur': 'EUR'
    }

    currency = currency_map.get(query.data, 'UAH')
    context.user_data['currency'] = currency

    currency_symbol = "₴" if currency == 'UAH' else "$" if currency == 'USD' else "€"
    amount = context.user_data.get('amount', 0)

    await query.edit_message_text(
        f"Сумма: {amount} {currency_symbol}\n\n"
        f"📝 Введите описание транзакции (например: такси, продукты, зарплата):\n\n"
        f"<i>AI автоматически определит категорию</i>",
        parse_mode='HTML'
    )

    return DESCRIPTION


async def receive_category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive category selection"""
    query = update.callback_query
    await query.answer()

    category_id = query.data.replace('cat_', '')

    # Get category details from database
    categories = db.get_categories()
    category = next((c for c in categories if c['id'] == category_id), None)

    if category:
        context.user_data['category'] = category['name']

        await query.edit_message_text(
            f"Категория: {category['name']}\n\nТеперь введите описание транзакции (или отправьте /skip чтобы пропустить):"
        )

        return DESCRIPTION


async def receive_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive description and auto-categorize with AI (if category not already set)"""
    description = update.message.text.strip()

    # Check if category already selected manually
    if 'category' in context.user_data:
        # Category already set - just save description and proceed
        if description and description != '/skip':
            context.user_data['description'] = description

        await update.message.reply_text(
            "Выберите способ оплаты:",
            reply_markup=Keyboards.payment_method()
        )
        return PAYMENT_METHOD

    # No category yet - use AI to categorize based on description
    if not description or description == '/skip':
        # No description - show category selection
        transaction_type = context.user_data.get('transaction_type', 'expense')
        categories = db.get_categories(category_type=transaction_type)

        await update.message.reply_text(
            "Выберите категорию:",
            reply_markup=Keyboards.category_selection(categories)
        )
        return CATEGORY

    context.user_data['description'] = description

    # Use AI to categorize
    try:
        await update.message.reply_text("🤖 AI анализирует...")

        transaction_type = context.user_data.get('transaction_type', 'expense')
        expense_categories = categorization_service.get_available_categories('expense')
        income_categories = categorization_service.get_available_categories('income')
        all_categories = expense_categories + income_categories

        # Get AI suggestion
        parsed = ai_service.parse_natural_language_transaction(description, all_categories)

        if parsed and parsed.get('category'):
            suggested_category = parsed['category']
            context.user_data['category'] = suggested_category
            context.user_data['ai_categorized'] = True

            # Also update description if AI extracted better one
            if parsed.get('description'):
                context.user_data['description'] = parsed['description']

            await update.message.reply_text(
                f"✅ AI предложил категорию: <b>{suggested_category}</b>\n\n"
                f"Выберите способ оплаты:",
                reply_markup=Keyboards.payment_method(),
                parse_mode='HTML'
            )

            return PAYMENT_METHOD

        else:
            # AI failed, show manual selection
            categories = db.get_categories(category_type=transaction_type)
            await update.message.reply_text(
                "❌ AI не смог определить категорию.\n\nВыберите вручную:",
                reply_markup=Keyboards.category_selection(categories)
            )
            return CATEGORY

    except Exception as e:
        logger.error(f"AI categorization error: {e}")
        # Fallback to manual
        transaction_type = context.user_data.get('transaction_type', 'expense')
        categories = db.get_categories(category_type=transaction_type)
        await update.message.reply_text(
            "❌ Ошибка AI. Выберите категорию вручную:",
            reply_markup=Keyboards.category_selection(categories)
        )
        return CATEGORY


async def receive_payment_method_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive payment method and save transaction"""
    query = update.callback_query
    await query.answer()

    payment_method_map = {
        'payment_cash': 'cash',
        'payment_card': 'card',
        'payment_transfer': 'transfer'
    }

    payment_method = payment_method_map.get(query.data, 'cash')
    context.user_data['payment_method'] = payment_method

    # Create transaction
    transaction = Transaction(
        amount=context.user_data['amount'],
        type=context.user_data['transaction_type'],
        category=context.user_data['category'],
        description=context.user_data.get('description'),
        payment_method=payment_method,
        date=datetime.now(),
        user_telegram_id=Config.USER_TELEGRAM_ID,
        ai_categorized=context.user_data.get('ai_categorized', False),
        currency=context.user_data.get('currency', 'UAH')
    )

    # Save to database
    db.add_transaction(transaction.to_dict())

    # Create summary message
    type_emoji = "💸" if transaction.type == "expense" else "💰"
    type_text = "Расход" if transaction.type == "expense" else "Доход"

    currency_symbols = {
        'UAH': '₴',
        'USD': '$',
        'EUR': '€'
    }
    currency_symbol = currency_symbols.get(transaction.currency, transaction.currency)

    summary = f"""✅ Транзакция добавлена!

{type_emoji} {type_text}: {transaction.amount} {currency_symbol}
📁 Категория: {transaction.category}
💳 Способ: {payment_method}"""

    if transaction.description:
        summary += f"\n📝 Описание: {transaction.description}"

    await query.edit_message_text(
        summary,
        reply_markup=Keyboards.back_to_main()
    )

    # Clear user data
    context.user_data.clear()

    return ConversationHandler.END


async def process_text_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process natural language transaction input"""
    user_id = update.effective_user.id

    if user_id != Config.USER_TELEGRAM_ID:
        return

    text = update.message.text

    # Get available categories
    expense_categories = categorization_service.get_available_categories('expense')
    income_categories = categorization_service.get_available_categories('income')
    all_categories = expense_categories + income_categories

    # Parse with AI
    parsed = ai_service.parse_natural_language_transaction(text, all_categories)

    if not parsed or 'amount' not in parsed:
        await update.message.reply_text(
            "Не удалось распознать транзакцию. Попробуйте использовать кнопки в меню."
        )
        return

    # Create transaction
    transaction = Transaction(
        amount=parsed.get('amount', 0),
        type=parsed.get('type', 'expense'),
        category=parsed.get('category', 'Другое'),
        description=parsed.get('description', text),
        payment_method=parsed.get('payment_method'),
        date=datetime.now(),
        user_telegram_id=Config.USER_TELEGRAM_ID,
        ai_categorized=True
    )

    # Confirmation message
    type_emoji = "💸" if transaction.type == "expense" else "💰"
    type_text = "Расход" if transaction.type == "expense" else "Доход"

    confirmation = f"""🤖 Распознано:

{type_emoji} {type_text}: {transaction.amount} грн
📁 Категория: {transaction.category}
📝 Описание: {transaction.description}

Сохранить?"""

    context.user_data['pending_transaction'] = transaction.to_dict()

    await update.message.reply_text(
        confirmation,
        reply_markup=Keyboards.confirmation("save_transaction", "cancel_transaction")
    )


async def save_transaction_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save confirmed transaction"""
    query = update.callback_query
    await query.answer()

    transaction_data = context.user_data.get('pending_transaction')

    if transaction_data:
        db.add_transaction(transaction_data)

        await query.edit_message_text(
            "✅ Транзакция сохранена!",
            reply_markup=Keyboards.back_to_main()
        )

        context.user_data.clear()


async def cancel_transaction_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel transaction"""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "❌ Транзакция отменена.",
        reply_markup=Keyboards.back_to_main()
    )

    context.user_data.clear()


async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    await update.message.reply_text(
        "Операция отменена.",
        reply_markup=Keyboards.back_to_main()
    )

    context.user_data.clear()
    return ConversationHandler.END


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current balance - simple and clear"""
    user_id = Config.USER_TELEGRAM_ID
    balances = db.get_balance(user_id)

    if not balances:
        message = "📭 У вас пока нет транзакций"
    else:
        message = "💼 <b>Ваш баланс:</b>\n\n"

        currency_symbols = {
            'UAH': '₴',
            'USD': '$',
            'EUR': '€'
        }

        for currency, data in balances.items():
            symbol = currency_symbols.get(currency, currency)

            message += f"<b>{currency} ({symbol})</b>\n"
            message += f"━━━━━━━━━━━━━━━\n"
            message += f"  💰 Доход: {data['income']:.2f} {symbol}\n"
            message += f"  💸 Расход: {data['expense']:.2f} {symbol}\n"
            message += f"  <b>📊 Баланс: {data['balance']:.2f} {symbol}</b>\n\n"

    # Handle both message and callback query
    if update.message:
        await update.message.reply_text(message, reply_markup=Keyboards.back_to_main(), parse_mode='HTML')
    elif update.callback_query:
        await update.callback_query.message.edit_text(message, reply_markup=Keyboards.back_to_main(), parse_mode='HTML')
