"""
Currency exchange handler
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from services.database import db
from utils.config import Config
from datetime import datetime

logger = logging.getLogger(__name__)

# Conversation states
FROM_CURRENCY, FROM_AMOUNT, TO_CURRENCY, TO_AMOUNT = range(4)


async def exchange_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start currency exchange"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton("₴ UAH", callback_data="exchange_from_uah"),
            InlineKeyboardButton("$ USD", callback_data="exchange_from_usd")
        ],
        [
            InlineKeyboardButton("€ EUR", callback_data="exchange_from_eur")
        ],
        [
            InlineKeyboardButton("◀️ Назад", callback_data="back_main")
        ]
    ]

    await query.edit_message_text(
        "💱 <b>Обмен валюты</b>\n\nИз какой валюты обмениваете?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

    return FROM_CURRENCY


async def receive_from_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive source currency"""
    query = update.callback_query
    await query.answer()

    from_currency = query.data.replace('exchange_from_', '').upper()
    context.user_data['exchange_from_currency'] = from_currency

    currency_names = {
        'UAH': 'гривен (₴)',
        'USD': 'долларов ($)',
        'EUR': 'евро (€)'
    }

    await query.edit_message_text(
        f"💱 Обмен из <b>{currency_names[from_currency]}</b>\n\n"
        f"Введите сумму, которую обмениваете:",
        parse_mode='HTML'
    )

    return FROM_AMOUNT


async def receive_from_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive source amount"""
    try:
        amount = float(update.message.text.replace(',', '.').replace(' ', ''))
        context.user_data['exchange_from_amount'] = amount

        from_currency = context.user_data['exchange_from_currency']

        # Build keyboard with other currencies
        keyboard = []
        currencies = {'UAH': '₴ UAH', 'USD': '$ USD', 'EUR': '€ EUR'}

        for curr_code, curr_name in currencies.items():
            if curr_code != from_currency:
                keyboard.append([InlineKeyboardButton(curr_name, callback_data=f"exchange_to_{curr_code.lower()}")])

        keyboard.append([InlineKeyboardButton("◀️ Отмена", callback_data="back_main")])

        currency_symbols = {'UAH': '₴', 'USD': '$', 'EUR': '€'}
        symbol = currency_symbols[from_currency]

        await update.message.reply_text(
            f"💱 Обмениваете: <b>{amount} {symbol}</b>\n\nВ какую валюту?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

        return TO_CURRENCY

    except ValueError:
        await update.message.reply_text(
            "❌ Некорректная сумма. Введите число (например: 100 или 62.5):"
        )
        return FROM_AMOUNT


async def receive_to_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive target currency"""
    query = update.callback_query
    await query.answer()

    to_currency = query.data.replace('exchange_to_', '').upper()
    context.user_data['exchange_to_currency'] = to_currency

    from_currency = context.user_data['exchange_from_currency']
    from_amount = context.user_data['exchange_from_amount']

    currency_symbols = {'UAH': '₴', 'USD': '$', 'EUR': '€'}
    from_symbol = currency_symbols[from_currency]
    to_symbol = currency_symbols[to_currency]

    await query.edit_message_text(
        f"💱 <b>Обмен валюты</b>\n\n"
        f"Из: {from_amount} {from_symbol}\n"
        f"В: {to_symbol}\n\n"
        f"Введите сколько получили в {to_symbol}:",
        parse_mode='HTML'
    )

    return TO_AMOUNT


async def receive_to_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive target amount and create exchange"""
    try:
        to_amount = float(update.message.text.replace(',', '.').replace(' ', ''))

        from_currency = context.user_data['exchange_from_currency']
        from_amount = context.user_data['exchange_from_amount']
        to_currency = context.user_data['exchange_to_currency']

        currency_symbols = {'UAH': '₴', 'USD': '$', 'EUR': '€'}
        from_symbol = currency_symbols[from_currency]
        to_symbol = currency_symbols[to_currency]

        # Calculate exchange rate
        rate = to_amount / from_amount if from_amount > 0 else 0

        # ПРАВИЛЬНАЯ ЛОГИКА ОБМЕНА:
        # Обмен - это НЕ доход и НЕ расход, это просто перемещение между валютами
        #
        # Решение: обновляем баланс напрямую через специальную категорию
        # которая не считается как доход/расход

        # Уменьшаем исходную валюту (расход)
        from_transaction = {
            'amount': from_amount,
            'type': 'expense',
            'category': 'Обмен валюты',
            'description': f'→ {to_amount} {to_symbol}',
            'user_telegram_id': Config.USER_TELEGRAM_ID,
            'currency': from_currency,
            'date': datetime.now().isoformat(),
            'ai_categorized': False,
            'is_team_finance': False
        }

        # Увеличиваем целевую валюту (доход)
        to_transaction = {
            'amount': to_amount,
            'type': 'income',
            'category': 'Обмен валюты',
            'description': f'← {from_amount} {from_symbol}',
            'user_telegram_id': Config.USER_TELEGRAM_ID,
            'currency': to_currency,
            'date': datetime.now().isoformat(),
            'ai_categorized': False,
            'is_team_finance': False,
            'original_amount': from_amount,
            'original_currency': from_currency
        }

        # Save both transactions
        db.add_transaction(from_transaction)
        db.add_transaction(to_transaction)

        keyboard = [
            [InlineKeyboardButton("💱 Еще обмен", callback_data="exchange")],
            [InlineKeyboardButton("💼 Баланс", callback_data="balance")],
            [InlineKeyboardButton("◀️ Главное меню", callback_data="back_main")]
        ]

        await update.message.reply_text(
            f"✅ <b>Обмен валюты выполнен!</b>\n\n"
            f"📤 Отдали: {from_amount} {from_symbol}\n"
            f"📥 Получили: {to_amount} {to_symbol}\n"
            f"💹 Курс: 1 {from_symbol} = {rate:.4f} {to_symbol}\n\n"
            f"Баланс обновлен по обеим валютам.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

        # Clear context
        context.user_data.clear()
        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text(
            "❌ Некорректная сумма. Введите число (например: 2500 или 2675.50):"
        )
        return TO_AMOUNT


async def cancel_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel exchange"""
    await update.message.reply_text(
        "❌ Обмен валюты отменен.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Главное меню", callback_data="back_main")]])
    )
    context.user_data.clear()
    return ConversationHandler.END
