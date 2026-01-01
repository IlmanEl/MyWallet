from telegram import Update
from telegram.ext import ContextTypes
from bot.keyboards.inline_keyboards import Keyboards
from services.database import db
from services.ai_service import ai_service
from utils.config import Config
from utils.helpers import get_date_range, format_currency, format_date
import logging

logger = logging.getLogger(__name__)


async def stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show statistics menu"""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "📊 Статистика\n\nВыберите период:",
        reply_markup=Keyboards.stats_period()
    )


async def stats_period_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show statistics for selected period"""
    query = update.callback_query
    await query.answer()

    period_map = {
        'period_day': 'day',
        'period_week': 'week',
        'period_month': 'month',
        'period_year': 'year',
        'period_all': 'all'
    }

    period = period_map.get(query.data, 'month')
    start_date, end_date = get_date_range(period)

    user_id = Config.USER_TELEGRAM_ID

    # Get transactions for period
    transactions = db.get_transactions(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        limit=10000
    )

    if not transactions:
        await query.edit_message_text(
            f"За выбранный период ({period}) транзакций нет.",
            reply_markup=Keyboards.back_to_main()
        )
        return

    # Calculate totals by currency
    # UAH
    income_uah = sum(t['amount'] for t in transactions
                    if t['type'] == 'income' and t.get('currency', 'UAH') == 'UAH')

    # Exclude project expenses (Партнерам) and self-transfers (наличные на карту)
    expense_uah = sum(t['amount'] for t in transactions
                     if t['type'] == 'expense'
                     and t.get('currency', 'UAH') == 'UAH'
                     and t.get('category') != 'Партнерам'
                     and not ('на карту' in t.get('description', '').lower() and 'налич' in t.get('description', '').lower()))

    balance_uah = income_uah - expense_uah

    # USD
    income_usd = sum(t['amount'] for t in transactions
                    if t['type'] == 'income' and t.get('currency') == 'USD')
    expense_usd = sum(t['amount'] for t in transactions
                     if t['type'] == 'expense' and t.get('currency') == 'USD')
    balance_usd = income_usd - expense_usd

    # Get category stats
    expense_stats = db.get_category_stats(user_id, start_date, end_date, 'expense')
    income_stats = db.get_category_stats(user_id, start_date, end_date, 'income')

    # Build message
    period_names = {
        'day': 'за день',
        'week': 'за неделю',
        'month': 'за месяц',
        'year': 'за год',
        'all': 'за все время'
    }

    if period == 'all':
        message = f"""📊 Статистика {period_names.get(period, '')}

💰 Доходы (UAH): {format_currency(income_uah)}
💸 Расходы (UAH): {format_currency(expense_uah)}
📊 Баланс (UAH): {format_currency(balance_uah)}

💰 Доходы (USD): {income_usd:,.2f} $
💸 Расходы (USD): {expense_usd:,.2f} $
📊 Баланс (USD): {balance_usd:,.2f} $

"""
    else:
        message = f"""📊 Статистика {period_names.get(period, '')}
📅 {format_date(start_date)} - {format_date(end_date)}

💰 Доходы (UAH): {format_currency(income_uah)}
💸 Расходы (UAH): {format_currency(expense_uah)}
📊 Баланс (UAH): {format_currency(balance_uah)}

💰 Доходы (USD): {income_usd:,.2f} $
💸 Расходы (USD): {expense_usd:,.2f} $
📊 Баланс (USD): {balance_usd:,.2f} $

"""

    # Top expense categories (exclude Партнерам)
    if expense_stats:
        message += "📉 Топ расходов:\n"
        filtered_stats = [s for s in expense_stats if s['category'] != 'Партнерам']
        for i, stat in enumerate(filtered_stats[:5], 1):
            percentage = (stat['total'] / expense_uah * 100) if expense_uah > 0 else 0
            message += f"{i}. {stat['category']}: {format_currency(stat['total'])} ({percentage:.1f}%)\n"

    # Top income categories
    if income_stats:
        message += "\n📈 Топ доходов:\n"
        for i, stat in enumerate(income_stats[:5], 1):
            percentage = (stat['total'] / income_uah * 100) if income_uah > 0 else 0
            message += f"{i}. {stat['category']}: {format_currency(stat['total'])} ({percentage:.1f}%)\n"

    await query.edit_message_text(
        message,
        reply_markup=Keyboards.back_to_main()
    )


async def recommendations_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate and show AI recommendations"""
    query = update.callback_query
    await query.answer()

    processing_msg = await query.edit_message_text("🤖 Генерирую рекомендации...")

    user_id = Config.USER_TELEGRAM_ID

    # Get recent transactions (last 30 days)
    import datetime
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=30)

    transactions = db.get_transactions(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        limit=10000
    )

    if not transactions:
        await processing_msg.edit_text(
            "Недостаточно данных для генерации рекомендаций.",
            reply_markup=Keyboards.back_to_main()
        )
        return

    # Generate recommendations
    recommendations = ai_service.generate_financial_recommendations(transactions)

    # Save to database
    db.add_recommendation({
        'user_telegram_id': user_id,
        'recommendation_text': recommendations,
        'category': 'monthly_analysis'
    })

    message = f"🤖 AI Рекомендации:\n\n{recommendations}"

    await processing_msg.edit_text(
        message,
        reply_markup=Keyboards.back_to_main()
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command"""
    await update.message.reply_text(
        "📊 Статистика\n\nВыберите период:",
        reply_markup=Keyboards.stats_period()
    )
